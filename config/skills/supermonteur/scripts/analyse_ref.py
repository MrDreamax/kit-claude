"""Analyse une vidéo de référence (le modèle à copier) et en sort la recette chiffrée.
  python3 analyse_ref.py video.mp4 outdir [--lang es]

Mesure : coupes (rythme), voix (débit, pauses), musique (changements, coupures nettes,
niveau sous la voix, tempo), SFX (impacts calés sur les coupes).
Sépare voix / musique avec Demucs (htdemucs, local, gratuit).
Sortie : outdir/<nom>.analyse.json + résumé imprimé.
"""
import json, os, subprocess, sys
import numpy as np
import librosa

src, out = sys.argv[1], sys.argv[2]
lang = sys.argv[sys.argv.index("--lang") + 1] if "--lang" in sys.argv else "fr"
name = os.path.splitext(os.path.basename(src))[0]
os.makedirs(out, exist_ok=True)
wav = os.path.join(out, f"{name}.wav")

def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# 1. Coupes (détection de plans)
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src]).decode())
meta = os.path.join(out, f"{name}.cuts.txt")
run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", f"scale=180:-1,select='gt(scene,0.22)',metadata=print:file={meta}", "-an", "-f", "null", "-"])
cuts = [round(float(l.split("pts_time:")[1]), 2) for l in open(meta) if "pts_time:" in l]
shots = np.diff([0.0] + cuts + [dur])

# 2. Séparation voix / musique
run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-ac", "2", "-ar", "44100", wav])
sep = os.path.join(out, "sep")
if not os.path.exists(os.path.join(sep, "htdemucs", name, "no_vocals.wav")):
    run([sys.executable, "-m", "demucs", "--two-stems", "vocals", "-n", "htdemucs", "-o", sep, wav])
voc_p = os.path.join(sep, "htdemucs", name, "vocals.wav")
mus_p = os.path.join(sep, "htdemucs", name, "no_vocals.wav")

sr, hop = 22050, 512
mus, _ = librosa.load(mus_p, sr=sr, mono=True)
voc, _ = librosa.load(voc_p, sr=sr, mono=True)
t_of = lambda n: librosa.frames_to_time(np.arange(n), sr=sr, hop_length=hop)
db = lambda y: 20 * np.log10(librosa.feature.rms(y=y, hop_length=hop)[0] + 1e-9)
mdb, vdb = db(mus), db(voc)
n = min(len(mdb), len(vdb)); mdb, vdb = mdb[:n], vdb[:n]; t = t_of(n)
mref = np.percentile(mdb, 95)

# 3. Voix : mots, débit, pauses
from faster_whisper import WhisperModel
segs, _ = WhisperModel("small", compute_type="int8").transcribe(voc_p, language=lang, word_timestamps=True)
words = [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)} for s in segs for w in s.words]
gaps = [(round(a["e"], 2), round(b["s"] - a["e"], 2)) for a, b in zip(words, words[1:]) if b["s"] - a["e"] >= 0.3]
speech_time = sum(w["e"] - w["s"] for w in words)
in_speech = np.zeros(n, bool)
for w in words:
    in_speech[(t >= w["s"]) & (t <= w["e"])] = True

# 4. Musique : présence, niveau sous la voix, coupures nettes (drops), changements
present = mdb > mref - 30
music_cover = float(present.mean())
under_voice = float(np.median(vdb[in_speech]) - np.median(mdb[in_speech])) if in_speech.any() else None
drops, i = [], 0
while i < n:
    if not present[i] and 0.5 < t[i] < dur - 0.8:
        j = i
        while j < n and not present[j]:
            j += 1
        if t[min(j, n - 1)] - t[i] >= 0.25:
            drops.append({"t": round(float(t[i]), 2), "duree": round(float(t[min(j, n - 1)] - t[i]), 2)})
        i = j
    else:
        i += 1

H = 2048
feat = np.vstack([librosa.feature.chroma_cqt(y=mus, sr=sr, hop_length=H),
                  librosa.feature.mfcc(y=mus, sr=sr, hop_length=H, n_mfcc=13)])
feat = (feat - feat.mean(1, keepdims=True)) / (feat.std(1, keepdims=True) + 1e-9)
feat = librosa.decompose.nn_filter(feat, aggregate=np.median, metric="cosine", width=3)
S = librosa.segment.recurrence_matrix(feat, mode="affinity", metric="cosine", sym=True, width=1).astype(float)
L = int(2.5 * sr / H)
g = np.outer(np.r_[np.ones(L), -np.ones(L)], np.r_[np.ones(L), -np.ones(L)]) * np.outer(np.hanning(2 * L), np.hanning(2 * L))
Sp = np.pad(S, L)
nov = np.array([np.sum(Sp[k:k + 2 * L, k:k + 2 * L] * g) for k in range(S.shape[0])])
nov = np.maximum(nov, 0); nov = nov / (nov.max() + 1e-9)
tf = librosa.frames_to_time(np.arange(len(nov)), sr=sr, hop_length=H)
pk = librosa.util.peak_pick(nov, pre_max=L, post_max=L, pre_avg=L, post_avg=L, delta=0.12, wait=int(3 * sr / H))
changes = [round(float(tf[k]), 2) for k in pk if 1.0 < tf[k] < dur - 1.0 and nov[k] > 0.35]

bounds = [0.0] + changes + [dur]
sections = []
for a, b in zip(bounds, bounds[1:]):
    seg = mus[int(a * sr):int(b * sr)]
    bpm = float(np.atleast_1d(librosa.beat.beat_track(y=seg, sr=sr)[0])[0]) if len(seg) > sr * 2 else 0.0
    sl = (t >= a) & (t < b)
    sections.append({"de": round(a, 2), "a": round(b, 2), "bpm": round(bpm), "niveau_db": round(float(np.median(mdb[sl]) - mref), 1) if sl.any() else None})

# 5. SFX : impact net sur la coupe (transitoire dans la piste sans voix)
env = librosa.onset.onset_strength(y=mus, sr=sr, hop_length=hop)
te = t_of(len(env)); base = np.median(env) + 1e-9
sfx_cuts = [c for c in cuts if env[(te > c - 0.15) & (te < c + 0.15)].max(initial=0) / base > 6]
strong = librosa.util.peak_pick(env, pre_max=5, post_max=5, pre_avg=20, post_avg=20, delta=base * 4, wait=8)
hits = [round(float(te[k]), 2) for k in strong if env[k] / base > 8][:40]

res = {
    "video": os.path.basename(src), "duree": round(dur, 2),
    "coupes": {"nb": len(cuts), "plan_moyen_s": round(float(shots.mean()), 2), "plan_median_s": round(float(np.median(shots)), 2),
               "plan_min_s": round(float(shots.min()), 2), "plan_max_s": round(float(shots.max()), 2), "temps": cuts},
    "voix": {"mots": len(words), "mots_par_min": round(len(words) / dur * 60), "part_parole": round(speech_time / dur, 2),
             "pauses_0_3s_plus": len(gaps), "pauses_longues": sorted(gaps, key=lambda x: -x[1])[:8]},
    "musique": {"couverture": round(music_cover, 2), "voix_au_dessus_musique_db": round(under_voice, 1) if under_voice is not None else None,
                "changements": changes, "sections": sections, "coupures_nettes": drops},
    "sfx": {"coupes_avec_impact": len(sfx_cuts), "ratio_coupes_avec_impact": round(len(sfx_cuts) / max(len(cuts), 1), 2),
            "impacts_forts": hits},
    "texte": " ".join(w["w"] for w in words),
}
json.dump(res, open(os.path.join(out, f"{name}.analyse.json"), "w"), ensure_ascii=False, indent=1)
c, v, m, s = res["coupes"], res["voix"], res["musique"], res["sfx"]
print(f"{name} | {dur:.0f}s | {c['nb']} coupes, plan moyen {c['plan_moyen_s']}s | {v['mots_par_min']} mots/min, {v['pauses_0_3s_plus']} pauses | "
      f"musique {int(m['couverture']*100)}% du temps, voix +{m['voix_au_dessus_musique_db']} dB, {len(m['changements'])} changements {m['changements']}, "
      f"{len(m['coupures_nettes'])} coupures nettes | SFX sur {int(s['ratio_coupes_avec_impact']*100)}% des coupes")
