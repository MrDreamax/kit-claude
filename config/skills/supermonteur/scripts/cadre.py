"""Recadrage fixe d'une face cam filmée trop large, vers le cadre serré des reels qui marchent :
yeux à 35 % de la hauteur, visage = 33 % de la largeur (mesuré sur des reels pros). Un monteur humain ne recadre pas : la différence vient du tournage.
  python3 cadre.py rush.mp4 --apply [--eyes 35] [--face 33] [--max 1.5]   -> clip.mp4 (étape 1 du SKILL) + cadre.json
AUTOMATIQUE. Rush déjà serré (yeux <= 40 % et visage >= 28 % de la largeur) = simple mise au format.
Mesure les yeux et la largeur du visage sur le rush (médiane de 16 images), calcule UN cadre fixe (pas de mouvement : ton posé),
recadré dans la source puis réduit en 1080x1920 : net tant que la source est assez grande (4K = jusqu'à x 2).
Zoom plafonné à 1,10 si la source fait 1080 de large (au-delà on agrandit des pixels = flou ; experts cadrage : 4K conseillée).
Experts : Kellan (yeux au tiers haut, visage centré), voir Brain 02-Formations/experts-cadrage-9-16.md. À utiliser seulement sur un rush filmé large.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lookstats import face, _size

src = sys.argv[1]
opt = lambda k, d: float(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else d
EYES, FACE, ZMAX = opt("--eyes", 35) / 100, opt("--face", 33) / 100, opt("--max", 1.5)
W0, H0, _ = _size(src)
if abs(W0 / H0 - 9 / 16) > 0.02: sys.exit(f"source {W0}x{H0} pas en 9:16 : recadrage 16:9 -> 9:16 pas encore géré (SKILL : monter en 9:16)")
F = face(src, 16)
if not F.get("yeux_y"): sys.exit("pas de visage détecté : pas de recadrage")
ey, fx, fw = F["yeux_y"] / 100, F["visage_x"] / 100, F["visage_largeur"] / 100
zmax = ZMAX if W0 >= 1080 * ZMAX else max(1.0, min(1.10, W0 / 1080 * 1.10))
z = 1.0 if (ey <= 0.40 and fw >= 0.28) else max(1.0, min(zmax, FACE / fw))   # déjà bien cadrée : on ne touche pas
cw, ch = int(W0 / z) // 2 * 2, int(H0 / z) // 2 * 2
x = int(min(max(fx * W0 - cw / 2, 0), W0 - cw)) // 2 * 2
y = int(min(max(ey * H0 - EYES * ch, 0), H0 - ch)) // 2 * 2
eyes_after = (ey * H0 - y) / ch * 100
c = {"source": src, "zoom": round(z, 3), "crop": [cw, ch, x, y], "yeux_avant": F["yeux_y"], "yeux_apres": round(eyes_after, 1),
     "visage_avant": F["visage_largeur"], "visage_apres": round(fw * z * 100, 1),
     "vf": (f"crop={cw}:{ch}:{x}:{y}," if z > 1 else "") + "scale=1080:1920:flags=lanczos,fps=30"}
json.dump(c, open("cadre.json", "w"), indent=1, ensure_ascii=False)
print(f"zoom x {z:.2f} · yeux {F['yeux_y']} % -> {eyes_after:.1f} % · visage {F['visage_largeur']} % -> {fw * z * 100:.1f} % de la largeur"
      + (f"  (plafonné : source {W0} px de large)" if z >= zmax and FACE / fw > zmax else ""))
if y + ch >= H0 - 2 and eyes_after > EYES * 100 + 2: print("!! le bas de la source est atteint : yeux pas assez hauts, cadrer plus bas au tournage")
if z == 1: print(f"cadre déjà bon (yeux {F['yeux_y']} %, visage {F['visage_largeur']} %) : pas de recadrage, simple mise au format")
cmd = ["ffmpeg", "-y", "-v", "error", "-i", src, "-vf", c["vf"], "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-c:a", "aac", "-b:a", "192k", "clip.mp4"]
if "--apply" in sys.argv:
    import subprocess
    subprocess.check_call(cmd); print("-> clip.mp4")
else: print(" ".join(f'"{a}"' if " " in a else a for a in cmd))
