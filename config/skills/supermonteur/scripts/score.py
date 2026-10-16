"""Prépare la note /10 : mesure le reel et un reel de référence côte à côte, sort les planches à regarder.
  python3 score.py final.mp4 [ref.mp4]      -> score/ (metrics.json, compare.jpg, hook.jpg)
ref : un reel de référence que l'utilisateur t'a donné (facultatif). Sans réf, le script mesure le montage seul.
Les chiffres ne notent rien tout seuls : ils servent à juger la grille de SKILL.md sans se mentir.
À lancer depuis le dossier du reel : words.json (débit, vitesse de lecture) et clip.mp4 (image de la cam) y sont lus s'ils existent.
Repères experts : débit 165-195 mots/min (alerte > 240), <= 20 car/s, cam P1 1-8 / P99 <= 235 / néon < 0,5 %,
yeux à 30-40 % de la hauteur (reels pros : 35 %, largeur du visage 33 %).
"""
import json, os, re, subprocess, sys

final = sys.argv[1]
ref = sys.argv[2] if len(sys.argv) > 2 else ""
if not ref or not os.path.exists(ref):   # pas de réf : la grille seule juge
    print("pas de vidéo de référence : mesures du montage seul (colonne ref = le montage lui-même)")
    ref = final
os.makedirs("score", exist_ok=True)


def run(args):
    return subprocess.run(args, capture_output=True, text=True).stderr


def measure(p):
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]))
    cuts = [float(t) for t in re.findall(r"pts_time:([\d.]+)", run(
        ["ffmpeg", "-i", p, "-vf", "scale=270:-1,select='gt(scene,0.3)',showinfo", "-an", "-f", "null", "-"]))]
    loud = run(["ffmpeg", "-i", p, "-af", "ebur128", "-f", "null", "-"])
    lufs = re.findall(r"I:\s+(-?[\d.]+) LUFS", loud)
    lra = re.findall(r"LRA:\s+([\d.]+) LU", loud)
    silences = re.findall(r"silence_duration: ([\d.]+)", run(
        ["ffmpeg", "-i", p, "-af", "silencedetect=n=-35dB:d=0.4", "-f", "null", "-"]))
    gaps = [b - a for a, b in zip([0] + cuts, cuts + [dur])]
    return {
        "duree_s": round(dur, 1),
        "changements_plan": len(cuts),
        "plans_par_10s": round(len(cuts) / dur * 10, 1),
        "plus_long_plan_fixe_s": round(max(gaps), 1),
        "premier_changement_s": round(cuts[0], 2) if cuts else None,
        "changements_3_premieres_s": sum(1 for c in cuts if c < 3),
        "lufs": float(lufs[-1]) if lufs else None,
        "lra": float(lra[-1]) if lra else None,
        "blancs_sup_0.4s": len(silences),
    }


m = {"final": measure(final), "ref": measure(ref)}

# --- experts (regles-experts.md) : cadrage, débit, vitesse de lecture, image de la cam ---
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lookstats import face, measure as look, verdicts
for name, p in (("final", final), ("ref", ref)):
    F = face(p, 16)   # sur ce que voit le spectateur (zoom compris) ; images sans visage (pleins écrans) ignorées
    m[name].update({"yeux_y_%": F.get("yeux_y"), "yeux_30_40_%": F.get("yeux_dans_30_40"), "visage_largeur_%": F.get("visage_largeur")})
    for k in ("mots_par_min", "car_par_s_max", "cam_noirs_P1", "cam_P99", "cam_neon_%"): m[name][k] = None
if os.path.exists("words.json"):   # dossier du reel : words.json = transcription de clip.mp4
    W = json.load(open("words.json")); W = W.get("words", W) if isinstance(W, dict) else W
    if W:
        m["final"]["mots_par_min"] = round(len(W) / max(W[-1]["end"] - W[0]["start"], 1) * 60)
        # vitesse de lecture des sous-titres (Netflix, BBC : <= 20 car/s) : pire fenêtre de 2 s
        m["final"]["car_par_s_max"] = round(max(sum(len(w["text"].strip()) for w in W if t <= w["start"] < t + 2) / 2 for t in [w["start"] for w in W]), 1)
if os.path.exists("clip.mp4"):     # image de la CAM (le final mélange vignettage, cartons et vrais logos)
    L = look("clip.mp4")
    m["final"].update({"cam_noirs_P1": L["p1"], "cam_P99": L["p99"], "cam_neon_%": L["neon"]})
    for v in verdicts(L): print("!! cam : " + v)
json.dump(m, open("score/metrics.json", "w"), indent=2, ensure_ascii=False)

# planche côte à côte : haut = reel, bas = réf, même cadence
for name, p in (("f", final), ("r", ref)):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", p, "-vf", "fps=1,scale=120:-1,tile=15x2", "-frames:v", "1", f"score/_{name}.jpg"])
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-t", "3", "-i", p, "-vf", "fps=4,scale=180:-1,tile=12x1", "-frames:v", "1", f"score/_h{name}.jpg"])
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", "score/_f.jpg", "-i", "score/_r.jpg", "-filter_complex", "vstack", "score/compare.jpg"])
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", "score/_hf.jpg", "-i", "score/_hr.jpg", "-filter_complex", "vstack", "score/hook.jpg"])
for f in ("_f", "_r", "_hf", "_hr"):
    os.remove(f"score/{f}.jpg")

print(f"{'':28}{'REEL':>10}{'RÉF':>10}")
for k in m["final"]:
    print(f"{k:28}{str(m['final'][k]):>10}{str(m['ref'][k]):>10}")
print("\nRegarder : score/compare.jpg (haut = reel, bas = réf) et score/hook.jpg (3 premières s)")
