"""Prépare une VRAIE photo de l'utilisateur pour une slide : recadrage 3:4, étalonnage naturel (teintes d'origine + légère touche
des couleurs de ta marque dans les ombres, dégradé foncé en bas pour lire le texte) et détourage local pour poser le mot géant
DERRIÈRE la tête sur la couverture.
  python3 prep.py <photo> <nom> [--dossier DOSSIER] [--fx 0.5] [--fy 0.45] [--zoom 1.0] [--bright 1.03] [--grad 0.55] [--sans-detourage]
Écrit DOSSIER/<nom>-bg.jpg (fond) et DOSSIER/<nom>-fg.png (sujet seul, même étalonnage) ; DOSSIER par défaut = ./photos-prep.
fx/fy = centre du recadrage (0 à 1), zoom > 1 = plus serré, grad = où commence le dégradé du bas (0 à 1).
Affiche « tête y≈ » : le haut de la tête en pixels, pour placer le mot géant juste au-dessus (couverture).

Détourage : modèle Robust Video Matting (ONNX, tourne sur ton Mac, aucune photo n'est envoyée nulle part), téléchargé une fois
dans ~/.cache/supermonteur/ (le même fichier que le skill monteur). Il faut `pip3 install onnxruntime numpy pillow`.
Modèle ou onnxruntime indisponible : la photo est préparée quand même, sans détourage (le mot géant passera devant la tête).
"""
import argparse
import os
import pathlib
import sys
import urllib.request

W, H = 1080, 1440
MODEL = os.path.expanduser("~/.cache/supermonteur/rvm_mobilenetv3_fp32.onnx")
MODEL_URL = "https://github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_mobilenetv3_fp32.onnx"
TRI = 0.2  # part de la teinte de marque mélangée aux ombres : la photo garde ses vraies couleurs


def _modele():
    """Chemin du modèle de détourage, téléchargé au besoin. None si indisponible."""
    if os.path.isfile(MODEL) and os.path.getsize(MODEL) > 1_000_000:
        return MODEL
    try:
        os.makedirs(os.path.dirname(MODEL), exist_ok=True)
        print("Téléchargement du modèle de détourage (15 Mo, une seule fois)…")
        tmp = MODEL + ".part"
        urllib.request.urlretrieve(MODEL_URL, tmp)
        os.replace(tmp, MODEL)
        return MODEL
    except Exception as e:  # pas d'Internet, GitHub bloqué…
        print("Détourage indisponible (modèle non téléchargé) :", e)
        return None


def _couleurs():
    sys.path.insert(0, str(pathlib.Path.home() / "Documents" / "Brain" / "_outils"))
    import marque
    c = marque.charger()["couleurs"]

    def rgb(h, noir=0.0, blanc=0.0):
        v = [int(h.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
        v = [x * (1 - noir) + 0 * noir for x in v]
        v = [x * (1 - blanc) + 255 * blanc for x in v]
        return [x / 255 for x in v]
    # tri-ton : très foncé -> foncée -> principale éclaircie -> presque blanc teinté
    cols = [rgb(c["foncee"], noir=0.45), rgb(c["foncee"]), rgb(c["principale"], blanc=0.15), rgb(c["teinte"], blanc=0.5)]
    return rgb(c["foncee"], noir=0.35), cols


def preparer(photo, nom, dossier, fx=0.5, fy=0.45, zoom=1.0, bright=1.03, grad=0.55, detourage=True):
    """Écrit <nom>-bg.jpg et (si le détourage marche) <nom>-fg.png dans `dossier`. Renvoie le haut de la tête en px, ou None."""
    import numpy as np
    from PIL import Image, ImageOps
    deep, cols = _couleurs()
    deep = np.array(deep, np.float32)
    cols = np.array(cols, np.float32)
    stops = np.array([0.0, 0.3, 0.62, 1.0], np.float32)

    im = ImageOps.exif_transpose(Image.open(photo)).convert("RGB")
    iw, ih = im.size
    cw = min(iw, ih * 3 / 4) / zoom
    ch = cw * 4 / 3
    cx = min(max(fx * iw, cw / 2), iw - cw / 2)
    cy = min(max(fy * ih, ch / 2), ih - ch / 2)
    im = im.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))).resize((W, H), Image.LANCZOS)
    rgb = np.asarray(im, np.float32) / 255

    alpha = None
    modele = _modele() if detourage else None
    if modele:
        try:
            import onnxruntime as ort
            # détourage : la même image passée 4 fois pour stabiliser l'état récurrent de RVM
            sess = ort.InferenceSession(modele, providers=["CPUExecutionProvider"])
            x = rgb.transpose(2, 0, 1)[None]
            rec = [np.zeros([1, 1, 1, 1], np.float32)] * 4
            for _ in range(4):
                fgr, pha, *rec = sess.run(None, {"src": x, "r1i": rec[0], "r2i": rec[1], "r3i": rec[2], "r4i": rec[3],
                                                  "downsample_ratio": np.array([0.25], np.float32)})
            alpha = pha[0, 0]
        except ImportError:
            print("onnxruntime manque : pip3 install onnxruntime (détourage ignoré)")

    lum = (rgb * np.array([0.299, 0.587, 0.114], np.float32)).sum(axis=2)
    tri = np.stack([np.interp(lum, stops, cols[:, c]) for c in range(3)], axis=2).astype(np.float32)
    g = (tri * TRI + rgb * (1 - TRI)) * bright
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    bottom = np.clip((yy - grad) / (1 - grad), 0, 1) ** 1.3 * 0.88
    top = np.clip((0.16 - yy) / 0.16, 0, 1) * 0.55
    g = g * (1 - bottom) + deep * bottom
    g = np.clip(g * (1 - top) + deep * top, 0, 1)

    os.makedirs(dossier, exist_ok=True)
    Image.fromarray((g * 255).astype(np.uint8)).save(f"{dossier}/{nom}-bg.jpg", quality=90)
    fg = f"{dossier}/{nom}-fg.png"
    if os.path.exists(fg):
        os.remove(fg)
    if alpha is None:
        return None
    Image.fromarray((np.dstack([g, alpha]) * 255).astype(np.uint8)).save(fg)
    ys = np.where(alpha > 0.5)[0]
    return int(ys.min()) if len(ys) else None


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("photo")
    ap.add_argument("nom")
    ap.add_argument("--dossier", default="photos-prep")
    ap.add_argument("--fx", type=float, default=0.5)
    ap.add_argument("--fy", type=float, default=0.45)
    ap.add_argument("--zoom", type=float, default=1.0)
    ap.add_argument("--bright", type=float, default=1.03)
    ap.add_argument("--grad", type=float, default=0.55)
    ap.add_argument("--sans-detourage", action="store_true")
    a = ap.parse_args()
    y = preparer(os.path.expanduser(a.photo), a.nom, os.path.expanduser(a.dossier), a.fx, a.fy, a.zoom, a.bright, a.grad,
                 detourage=not a.sans_detourage)
    print(a.nom, "tête y≈", y)
