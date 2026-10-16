"""Rendu HTML -> PNG avec Chrome headless, dans un dossier temporaire (Chrome ne lit pas toujours ~/Documents à cause des droits macOS).
Polices et couleurs de marque : voir marque_html() (lit ~/Documents/Brain/00-Moi/marque.json)."""
import os, pathlib, shutil, subprocess, sys, tempfile
from PIL import Image

sys.path.insert(0, str(pathlib.Path.home() / "Documents" / "Brain" / "_outils"))
import marque  # noqa: E402


def mix(a, b, t):
    ra = [int(a.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    rb = [int(b.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    return "#%02X%02X%02X" % tuple(round(ra[i] * (1 - t) + rb[i] * t) for i in range(3))


def accent():
    """Couleur d'accent des covers : couleurs.accent de marque.json, sinon la couleur principale éclaircie (lisible sur fond sombre)."""
    c = marque.charger()["couleurs"]
    return c.get("accent") or mix(c["principale"], "#FFFFFF", 0.5)


def marque_html():
    """Balises <link> (Google Fonts) + <style> à mettre dans le <head> : variables --foncee, --principale, --police-titre…"""
    c = dict(marque.charger()["couleurs"])
    c["accent"] = accent()
    p = marque.charger()["polices"]
    v = ";".join(f"--{k}:{x}" for k, x in c.items())
    return f"{marque.lien_polices('400;500;600;700;800;900')}<style>:root{{{v};--police-titre:'{p['titre']}';--police-texte:'{p['texte']}'}}</style>"


def rendre(html, fichiers, sortie, largeur, hauteur, rogner_blanc=False):
    """html : texte de la page. fichiers : {nom_dans_la_page: chemin_source}."""
    tmp = tempfile.mkdtemp(prefix="publieur-")
    try:
        for nom, src in fichiers.items():
            shutil.copy(src, os.path.join(tmp, nom))
        page = os.path.join(tmp, "page.html")
        with open(page, "w", encoding="utf-8") as f:
            f.write(html)
        png = os.path.join(tmp, "out.png")
        subprocess.run([marque.chrome(), "--headless=new", "--use-mock-keychain", "--disable-gpu", "--hide-scrollbars", "--use-mock-keychain",
                        "--allow-file-access-from-files", f"--user-data-dir={tmp}/chrome", "--virtual-time-budget=8000",
                        f"--window-size={largeur},{hauteur}", f"--screenshot={png}", "file://" + page],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
        im = Image.open(png).convert("RGB")
        if rogner_blanc:
            w, h = im.size
            px = im.load()
            y = h - 1
            while y > 0 and all(px[x, y] == (255, 255, 255) for x in range(0, w, 20)):
                y -= 1
            if y >= h - 2:
                raise SystemExit(f"Page coupée : agrandir la hauteur de rendu ({hauteur}px)")
            im = im.crop((0, 0, w, min(h, y + 60)))
        os.makedirs(os.path.dirname(os.path.abspath(sortie)), exist_ok=True)
        im.save(sortie)
        return sortie
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
