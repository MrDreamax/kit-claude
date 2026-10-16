#!/usr/bin/env python3
"""Cherche dans TES B-rolls (photos et vidéos) les plans qui illustrent le sujet du reel, et sort une planche numérotée pour choisir la cover.
Dossier par défaut : ~/Documents/Contenu/medias/brolls (change-le avec --dossier ; le skill note ton choix dans son carnet).
Sans index : les mots-clés sont cherchés dans les NOMS des fichiers et des dossiers (ex. « podcast », « tournage », « bureau »).
Aucun nom qui parle (IMG_1234.mov) : sans résultat, la planche montre un échantillon réparti de tes B-rolls les plus récents, et c'est TOI (ou Claude
en regardant la planche) qui choisis. Vertical d'abord.
Usage : broll.py --mots "tournage,camera,podcast" --out DOSSIER [--max 12] [--dossier ~/Documents/Contenu/medias/brolls]
Sorties : DOSSIER/planche.jpg (numéros en jaune) + DOSSIER/candidats.json ({numéro: {fichier, image}}).
Pour une vidéo, l'image prise est celle du milieu du plan (ffmpeg). Images : cand_N.jpg (2400 px de haut max).
"""
import argparse, json, os, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps

PHOTOS = (".jpg", ".jpeg", ".png", ".webp")
HEIC = (".heic", ".heif")
VIDEOS = (".mp4", ".mov", ".m4v")

ap = argparse.ArgumentParser()
ap.add_argument("--mots", default="", help="mots-clés séparés par des virgules (cherchés dans le nom du fichier et des dossiers)")
ap.add_argument("--out", required=True)
ap.add_argument("--max", type=int, default=12)
ap.add_argument("--dossier", default="~/Documents/Contenu/medias/brolls")
a = ap.parse_args()

racine = os.path.expanduser(a.dossier)
if not os.path.isdir(racine):
    raise SystemExit(f"Dossier de B-rolls introuvable : {racine}. Dis-moi où sont tes B-rolls (ou mets-les dans ce dossier).")
mots = [m.strip().lower() for m in a.mots.split(",") if m.strip()]

fichiers = []
for dp, dn, fn in os.walk(racine):
    dn[:] = [d for d in dn if not d.startswith((".", "_"))]
    for n in fn:
        if n.startswith(".") or not n.lower().endswith(PHOTOS + HEIC + VIDEOS):
            continue
        p = os.path.join(dp, n)
        fichiers.append((p, os.path.getmtime(p)))
if not fichiers:
    raise SystemExit(f"Aucun B-roll (photo ou vidéo) dans {racine}.")


def score(p):
    t = os.path.relpath(p, racine).lower()
    return sum(m in t for m in mots)


def dims(p):
    """(largeur, hauteur) ou None."""
    try:
        if p.lower().endswith(VIDEOS):
            out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:stream_side_data=rotation",
                                  "-of", "json", p], capture_output=True, text=True).stdout
            s = json.loads(out)["streams"][0]
            w, h = s["width"], s["height"]
            rot = abs(int((s.get("side_data_list") or [{}])[0].get("rotation", 0)))
            return (h, w) if rot in (90, 270) else (w, h)
        if p.lower().endswith(HEIC):
            return None
        return ImageOps.exif_transpose(Image.open(p)).size
    except Exception:
        return None


# 1. présélection : mots-clés d'abord, puis les plus récents (un échantillon réparti si aucun mot ne correspond)
fichiers.sort(key=lambda x: x[1], reverse=True)
avec_mots = [(score(p), m, p) for p, m in fichiers if mots and score(p)]
avec_mots.sort(key=lambda x: (x[0], x[1]), reverse=True)
if avec_mots:
    pre = [p for _, _, p in avec_mots[:60]]
    mode = "mots-clés"
else:
    pas = max(1, len(fichiers) // 60)
    pre = [p for p, _ in fichiers[::pas][:60]]
    mode = "échantillon récent (aucun nom de fichier ne correspond aux mots-clés)" if mots else "échantillon récent"
# 2. vertical d'abord (les covers sont en 9:16)
mesures = [(p, dims(p)) for p in pre]
mesures.sort(key=lambda x: (0 if x[1] and x[1][1] > x[1][0] else 1))
cands = [p for p, _ in mesures][:a.max]

os.makedirs(a.out, exist_ok=True)
font = ImageFont.load_default()
for f in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "C:/Windows/Fonts/arialbd.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
    if os.path.exists(f):
        font = ImageFont.truetype(f, 40)
        break


def extraire(src, dest):
    """Image JPG (2400 px de haut max) d'une photo ou du milieu d'une vidéo. True si réussi."""
    low = src.lower()
    try:
        if low.endswith(VIDEOS):
            d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src],
                                     capture_output=True, text=True).stdout.strip() or 0)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(d / 2), "-i", src, "-frames:v", "1", "-vf",
                            "scale='if(gt(ih,2400),-2,iw)':'min(ih,2400)'", "-q:v", "2", dest], check=True)
            return True
        if low.endswith(HEIC):
            if shutil.which("sips"):  # Mac
                subprocess.run(["sips", "-s", "format", "jpeg", "-Z", "2400", src, "--out", dest], check=True, capture_output=True)
                return True
            return False
        im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
        if im.height > 2400:
            im = im.resize((round(im.width * 2400 / im.height), 2400), Image.LANCZOS)
        im.save(dest, quality=92)
        return True
    except Exception as e:
        print("ignoré :", os.path.relpath(src, racine), "-", str(e)[:80])
        return False


sortie, vignettes = {}, []
for src in cands:
    i = len(vignettes) + 1
    img = os.path.join(a.out, f"cand_{i}.jpg")
    if not extraire(src, img):
        continue
    th = ImageOps.fit(Image.open(img).convert("RGB"), (300, 533))
    ImageDraw.Draw(th).text((12, 8), str(i), fill="#FFD400", font=font, stroke_width=2, stroke_fill="#000")
    vignettes.append(th)
    sortie[i] = {"fichier": src, "image": img}
    print(i, os.path.relpath(src, racine))
if not vignettes:
    raise SystemExit("Aucune image exploitable (HEIC sans conversion ? ffmpeg manquant ?).")
cols = min(6, len(vignettes))
rows = (len(vignettes) + cols - 1) // cols
planche = Image.new("RGB", (cols * 300, rows * 533), "black")
for k, th in enumerate(vignettes):
    planche.paste(th, ((k % cols) * 300, (k // cols) * 533))
planche.save(os.path.join(a.out, "planche.jpg"), quality=88)
json.dump(sortie, open(os.path.join(a.out, "candidats.json"), "w"), ensure_ascii=False, indent=1)
print("OK", os.path.join(a.out, "planche.jpg"), "·", mode)
