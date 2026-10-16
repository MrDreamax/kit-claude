#!/usr/bin/env python3
"""Cover de reel 1080x1920 : une de TES photos B-roll (retouchée avec Higgsfield si tu as un compte, sinon étalonnée ici) + titre + sous-titre.
Polices et couleurs : celles de ~/Documents/Brain/00-Moi/marque.json (titre en police de titres, sous-titre en police de texte,
couleur d'accent = couleurs.accent ou la couleur principale éclaircie).
Sorties dans --out : cover.png (pour Metricool), grille.jpg (aperçu 3:4 du profil), cover_480.jpg (pour la fiche).
Usage : cover.py --photo photo.jpg --titre "TIER LIST" --sous-titre "des formats Instagram" --out DOSSIER [--etalonner] [--haut 1395]
  --etalonner : sans Higgsfield, un léger étalonnage aux couleurs de ta marque (ombres teintées, contraste doux). Le visage ne change pas.
"""
import argparse, html, os, pathlib, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _rendu import rendre, marque_html
from PIL import Image, ImageChops, ImageEnhance, ImageOps

sys.path.insert(0, str(pathlib.Path.home() / "Documents" / "Brain" / "_outils"))
import marque  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--photo", required=True)
ap.add_argument("--titre", required=True)
ap.add_argument("--sous-titre", default="")
ap.add_argument("--out", required=True)
ap.add_argument("--haut", type=int, default=1395, help="haut du bloc texte en px (zone 3:4 visible = 240 à 1680)")
ap.add_argument("--etalonner", action="store_true")
a = ap.parse_args()

mots = len((a.titre + " " + a.sous_titre).split())
if mots > 6:
    print(f"ALERTE : {mots} mots sur la cover, viser 2 à 4 (sinon coupé dans la grille)")

# Photo recadrée en 1080x1920 (rotation EXIF appliquée)
im = ImageOps.fit(ImageOps.exif_transpose(Image.open(os.path.expanduser(a.photo))).convert("RGB"), (1080, 1920), Image.LANCZOS)
if a.etalonner:  # ombres teintées de la couleur foncée de la marque (18 % max), contraste et saturation doux
    foncee = marque.charger()["couleurs"]["foncee"]
    masque = im.convert("L").point(lambda v: int((255 - v) * 0.18))
    im = Image.composite(Image.new("RGB", im.size, foncee), im, masque)
    im = ImageEnhance.Color(ImageEnhance.Contrast(im).enhance(1.05)).enhance(0.97)

os.makedirs(a.out, exist_ok=True)
fond = os.path.join(a.out, ".fond.png")
im.save(fond)

page = f"""<!doctype html><html><head><meta charset="utf-8">{marque_html()}<style>
html,body{{margin:0;width:1080px;height:1920px;overflow:hidden;background:#000}}
.bg{{position:absolute;inset:0;background:url(fond.png) center/cover}}
.fade{{position:absolute;left:0;right:0;top:{a.haut - 215}px;height:{1920 - a.haut + 215}px;background:linear-gradient(to bottom,rgba(0,0,0,0),rgba(0,0,0,.78) 45%,rgba(0,0,0,.85))}}
.t{{position:absolute;left:60px;right:60px;top:{a.haut}px;text-align:center;color:#fff}}
.a{{font-family:var(--police-titre),sans-serif;font-weight:900;font-size:132px;letter-spacing:-2px;line-height:1;text-transform:uppercase;white-space:nowrap}}
.b{{font-family:var(--police-texte),sans-serif;font-weight:700;font-size:96px;line-height:1.08;margin-top:12px;color:var(--accent);white-space:nowrap}}
</style></head><body><div class="bg"></div><div class="fade"></div>
<div class="t"><div class="a">{html.escape(a.titre)}</div><div class="b">{html.escape(a.sous_titre)}</div></div>
<script>
// les polices sont chargées à la main avant de mesurer, puis chaque ligne est réduite jusqu'à tenir dans la largeur (jamais coupée)
const css=getComputedStyle(document.documentElement);
const fams=['--police-titre','--police-texte'].map(v=>css.getPropertyValue(v).replace(/['"]/g,'').trim());
Promise.all(fams.flatMap(f=>['400','700','900'].map(w=>document.fonts.load(w+' 40px "'+f+'"').catch(()=>0)))).then(()=>document.fonts.ready).then(()=>{{
  for(const el of document.querySelectorAll('.a,.b')){{let fs=parseFloat(getComputedStyle(el).fontSize);while(el.scrollWidth>el.clientWidth+1&&fs>50){{fs-=4;el.style.fontSize=fs+'px'}}}}
}});
</script></body></html>"""

cover = os.path.join(a.out, "cover.png")
rendre(page, {"fond.png": fond}, cover, 1080, 1920)
os.remove(fond)
c = Image.open(cover)
g = c.crop((0, 240, 1080, 1680))
g.resize((360, 480), Image.LANCZOS).save(os.path.join(a.out, "grille.jpg"), quality=90)
c.convert("RGB").resize((480, 853), Image.LANCZOS).save(os.path.join(a.out, "cover_480.jpg"), quality=88)
print("OK", cover)
