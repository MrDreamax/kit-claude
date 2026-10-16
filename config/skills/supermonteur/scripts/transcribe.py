"""Transcription mot à mot (faster-whisper local, gratuit).
  python3 transcribe.py video.mp4 out.words.json [--model small] [--lang fr] [--no-snap]
Recalage sur le vrai son (rush de conférence) : dans une salle qui résonne, Whisper colle les pauses À L'INTÉRIEUR des mots
(« vous » 4,94-6,10 s pour 0,25 s de parole), donc derush.py ne voyait aucun blanc à couper. On mesure l'énergie de la voix
(10 ms) et chaque plage vraiment silencieuse >= 0,15 s cachée dans un mot est sortie du mot : la plus grande partie parlée garde
le mot, l'autre part au mot voisin (on ne perd jamais de parole). --no-snap = timings Whisper bruts.
"""
import json, subprocess, sys
import numpy as np
from faster_whisper import WhisperModel

src, out = sys.argv[1], sys.argv[2]
model = sys.argv[sys.argv.index("--model") + 1] if "--model" in sys.argv else "small"
lang = sys.argv[sys.argv.index("--lang") + 1] if "--lang" in sys.argv else "fr"
segs, _ = WhisperModel(model, compute_type="int8").transcribe(src, language=lang, word_timestamps=True)
words = [{"text": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)} for s in segs for w in s.words]


def snap(words, run_min=0.15, part_min=0.06, margin=0.05):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", src, "-ac", "1", "-ar", "16000",
                                   "-af", "highpass=f=100", "-f", "s16le", "-"])
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    hop = 160                                                         # 10 ms
    n = len(a) // hop
    db = 20 * np.log10(np.sqrt((a[:n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-6)
    low = db < np.percentile(db, 90) - 22                             # 22 dB sous la parole forte = silence de la salle
    runs, i = [], 0                                                   # plages silencieuses (trous <= 0,1 s fusionnés)
    while i < n:
        if low[i]:
            j = i
            while j < n and low[j]: j += 1
            if runs and i - runs[-1][1] <= 10: runs[-1][1] = j
            else: runs.append([i, j])
            i = j
        else: i += 1
    # marge de 0,05 s rendue à la parole : le « s » d'attaque (souffle aigu, peu d'énergie) reste dans le mot (ex. « soufflez »)
    runs = [(s / 100 + margin, e / 100 - margin) for s, e in runs if (e - s) / 100 >= run_min + 2 * margin]
    moved = 0
    for k, w in enumerate(words):
        inside = [(max(s, w["start"]), min(e, w["end"])) for s, e in runs if s < w["end"] and e > w["start"]]
        inside = [(s, e) for s, e in inside if e - s >= run_min]
        if not inside: continue
        s, e = max(inside, key=lambda r: r[1] - r[0])
        before, after = s - w["start"], w["end"] - e
        if max(before, after) < 0.03: continue                       # mot presque tout en silence : on n'y touche pas
        if after >= before or before < part_min:                    # le mot = la partie APRÈS le silence
            if before >= part_min and k > 0: words[k - 1]["end"] = round(max(words[k - 1]["end"], s), 3)
            w["start"] = round(e, 3)
        else:                                                         # le mot = la partie AVANT le silence
            if after >= part_min and k + 1 < len(words): words[k + 1]["start"] = round(min(words[k + 1]["start"], e), 3)
            w["end"] = round(s, 3)
        moved += 1
    return moved


if "--no-snap" not in sys.argv and words:
    print(f"recalage sur le son : {snap(words)} mot(s) débarrassé(s) d'une pause cachée")
json.dump({"words": words}, open(out, "w"), ensure_ascii=False)
print(f"{len(words)} mots -> {out}")
print(" ".join(w["text"] for w in words))
