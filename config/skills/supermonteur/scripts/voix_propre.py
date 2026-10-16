"""Voix propre : une voix prise dans une salle (conférence, micro de scène capté par la caméra, pièce vide) remise au son de la
voix STUDIO de la personne (une voix de studio de référence de 30 s à 1 min, dans config.json « voice_ref »).
  python3 voix_propre.py clip.mp4 voix/clean.wav [words.json] [--ref voix_studio.wav] [--fort]
PAR DÉFAUT = DOUX (un traitement fort rend la voix « bizarre et déformée ») : la voix ORIGINALE (pas de Demucs, pas d'expandeur, pas d'exciteur), seulement l'EQ vers la voix
studio, à 35 % et bornée à ±3,5 dB. --fort = l'ancienne chaîne complète ci-dessous (à réserver à une salle vraiment mauvaise).
  puis : python3 mix.py plan.json renders/<x>.mp4 voix/clean.wav final.mp4
Étapes :
  1. Demucs isole la voix (public, bruit de salle).
  2. EQ calée sur la voix studio (config "voice_ref" = un enregistrement de TA voix en studio ; sans lui : EQ générique) : on mesure le profil (1/3 d'octave,
     trames de parole) et on corrige l'écart, lissé, -10 / +9 dB max. Mesuré sur la conf : +10-12 dB de basses en trop (sono),
     -10 à -25 dB d'aigus en moins (son étouffé) ; écart moyen 10,1 dB -> 2,8 dB.
  3. Aigus quasi absents (> 6 kHz) : exciteur (harmoniques recréées depuis 5 kHz), seulement s'il manque plus de 10 dB à 8 kHz.
  4. Écho entre les mots baissé (expandeur doux, -13 dB max, jamais coupé net), dé-esseur, compression légère.
WPE (déréverbération classique, nara_wpe) : gain nul sur une salle qui résonne, pas gardé.
"""
import json, os, subprocess, sys, tempfile
import numpy as np

args = [a for a in sys.argv[1:] if not a.startswith("--")]
src, out = args[0], args[1]
words = args[2] if len(args) > 2 else None
SK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reglages
CFG = reglages.charger()
ref = sys.argv[sys.argv.index("--ref") + 1] if "--ref" in sys.argv else os.path.expanduser(CFG.get("voice_ref") or "")
BANDS = [80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500]
TAIL = ("agate=threshold=0.028:ratio=2.5:range=0.22:attack=3:release=140:knee=3,deesser=i=0.4:m=0.5:f=0.5,"
        "acompressor=threshold=-18dB:ratio=2.5:attack=8:release=140,alimiter=limit=0.89:level=0")


def load(f, sr=48000):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", f, "-vn", "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"])
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def profile(f, sr=48000, n=4096):
    """profil moyen de la parole en 1/3 d'octave, 0 dB à 1 kHz (trames les plus fortes = parole)"""
    a = load(f, sr); w = np.hanning(n)
    fr = np.array([a[i:i + n] * w for i in range(0, len(a) - n, n // 2)])
    S = np.abs(np.fft.rfft(fr, axis=1)) ** 2; e = 10 * np.log10(S.sum(1) + 1e-12)
    S = S[e > np.percentile(e, 55)].mean(0); fq = np.fft.rfftfreq(n, 1 / sr)
    p = np.array([10 * np.log10(S[(fq >= c / 2 ** (1 / 6)) & (fq < c * 2 ** (1 / 6))].mean() + 1e-12) for c in BANDS])
    return p - p[BANDS.index(1000)]


def contrast(f):
    """écart (dB) entre la parole et les blancs entre les mots : plus c'est grand, moins on entend la salle"""
    a = load(f, 16000); n = len(a) // 160
    db = 20 * np.log10(np.sqrt((a[:n * 160].reshape(n, 160) ** 2).mean(1)) + 1e-6)
    if not words: return np.percentile(db, 90) - np.percentile(db, 10)
    W = json.load(open(words))["words"]
    sp = np.concatenate([db[int(w["start"] * 100):int(w["end"] * 100)] for w in W])
    g = [db[int(W[i]["end"] * 100) + 3:int(W[i + 1]["start"] * 100)] for i in range(len(W) - 1) if W[i + 1]["start"] - W[i]["end"] > 0.12]
    g = np.concatenate([x for x in g if len(x)]) if g else db
    return np.median(sp) - np.median(g)


FORT = "--fort" in sys.argv
tmp = tempfile.mkdtemp(prefix="voix_")
brut = os.path.join(tmp, "brut.wav")
subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-i", src, "-vn", "-ac", "2", "-ar", "44100", brut])
voc = brut
if FORT:
    subprocess.check_call([sys.executable, "-m", "demucs", "--two-stems=vocals", "-n", "htdemucs", "-o", tmp, brut],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    voc = os.path.join(tmp, "htdemucs", "brut", "vocals.wav")

chain = "highpass=f=70,"
if ref and os.path.exists(ref):
    R = profile(ref); d = profile(voc) - R
    g = np.convolve(np.pad(-d, 1, mode="edge"), [0.25, 0.5, 0.25], mode="valid")      # lissé : pas de pic étroit
    if FORT: g = np.clip(g, -10, 9); g = np.array([min(x, 7) if b >= 6300 else x for b, x in zip(BANDS, g)])   # +7 max en haut (souffle)
    else: g = np.clip(g * 0.35, -3.5, 3.5)                                                                        # doux : ±3,5 dB
    chain += "firequalizer=gain_entry='" + ";".join([f"entry(20,{g[0]:.1f})"] + [f"entry({b},{x:.1f})" for b, x in zip(BANDS, g)]
                                                     + [f"entry(20000,{g[-1]:.1f})"]) + "',"
    if FORT and d[BANDS.index(8000)] < -10: chain += "aexciter=amount=4.5:drive=6:freq=5000:ceil=16000,"
    print("EQ calée sur la voix studio : " + " ".join(f"{b}:{x:+.0f}" for b, x in zip(BANDS, g)))
else:
    chain += "equalizer=f=350:width_type=q:width=1.0:g=-2.5,equalizer=f=3000:width_type=q:width=0.9:g=2,highshelf=f=9000:g=1.5,"
    print("pas de voix studio de référence (config voice_ref) : EQ générique")
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-i", voc, "-af", chain + (TAIL if FORT else "anull"), "-ar", "48000", out])

msg = f"voix propre -> {out} · écart parole / salle {contrast(brut):.0f} -> {contrast(out):.0f} dB"
if ref and os.path.exists(ref):
    msg += f" · écart au timbre studio {np.abs(profile(brut) - R).mean():.1f} -> {np.abs(profile(out) - R).mean():.1f} dB"
print(msg)
