"""Planches contact numérotées de TES photos, pour choisir les photos d'un carrousel.
  python3 planches.py <dossier_sortie> [sous-dossier ...] [--racine ~/Documents/Contenu/medias/photos]
Sans sous-dossier : toutes les photos de la racine. Écrit planche-01.jpg, planche-02.jpg… (40 photos par planche) + index.json (numéro -> chemin).
Un numéro jaune sur chaque vignette : tu choisis une photo, tu prends son chemin dans index.json pour le spec du carrousel.
"""
import argparse
import json
import os

from PIL import Image, ImageDraw, ImageFont, ImageOps

ap = argparse.ArgumentParser()
ap.add_argument("sortie")
ap.add_argument("dossiers", nargs="*")
ap.add_argument("--racine", default="~/Documents/Contenu/medias/photos")
a = ap.parse_args()

ROOT = os.path.expanduser(a.racine)
OUT, FOLDERS = os.path.expanduser(a.sortie), a.dossiers or [""]
TW, TH, COLS, ROWS = 220, 293, 8, 5
font = ImageFont.load_default()
for f in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "C:/Windows/Fonts/arialbd.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
    if os.path.exists(f):
        font = ImageFont.truetype(f, 22)
        break
os.makedirs(OUT, exist_ok=True)

files = []
for f in FOLDERS:
    for dp, _, fn in os.walk(os.path.join(ROOT, f)):
        files += sorted(os.path.join(dp, n) for n in fn if n.lower().endswith((".jpg", ".jpeg", ".png")) and not n.startswith("._"))
if not files:
    raise SystemExit(f"Aucune photo trouvée dans {ROOT}. Mets tes photos là (jpg ou png) ou donne un autre dossier avec --racine.")

index, per = {}, COLS * ROWS
for s in range(0, len(files), per):
    sheet = Image.new("RGB", (COLS * TW, ROWS * TH), "#333")
    d = ImageDraw.Draw(sheet)
    for i, path in enumerate(files[s:s + per]):
        n = s + i + 1
        index[n] = path
        try:
            im = ImageOps.exif_transpose(Image.open(path))
            im.draft("RGB", (TW * 2, TH * 2))
            im = ImageOps.fit(im.convert("RGB"), (TW - 4, TH - 4))
        except Exception:
            continue
        x, y = (i % COLS) * TW + 2, (i // COLS) * TH + 2
        sheet.paste(im, (x, y))
        d.rectangle([x, y, x + 46, y + 28], fill="#000")
        d.text((x + 4, y + 2), str(n), fill="#FFD400", font=font)
    sheet.save(os.path.join(OUT, f"planche-{s // per + 1:02d}.jpg"), quality=80)
json.dump(index, open(os.path.join(OUT, "index.json"), "w"), ensure_ascii=False, indent=0)
print(len(files), "photos,", (len(files) + per - 1) // per, "planches dans", OUT)
