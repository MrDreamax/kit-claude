#!/usr/bin/env python3
"""Une page HTML -> PDF et/ou PNG, aux couleurs et polices de ta marque (00-Moi/marque.json).

Usage : python3 ~/Documents/Brain/_outils/page_pdf.py <page.html> [options]
  --pdf / --png   ce qu'on sort (sans option : les deux). Fichiers à côté de la page.
  --largeur N --hauteur N   taille de l'image en pixels (défaut A4 : 794 x 1123 ; mobile : 390 x 2400)
  --pages N       nombre de pages PDF attendu au maximum (défaut 1) : au-delà, ALERTE (la page déborde)
  --suffixe NOM   ajoute -NOM au nom de l'image (ex. index-mobile.png), pour garder plusieurs tailles
  --garder        écrit le bloc marque (polices + couleurs) dans la page elle-même (pour une page à héberger)

Dans ton HTML, utilise seulement ces variables (le script les remplit depuis marque.json via marque.py) :
  var(--principale) var(--foncee) var(--texte) var(--doux) var(--ligne) var(--teinte) var(--clair)
  var(--police-titre) var(--police-texte)     ex. font-family: var(--police-titre), sans-serif;
Le logo de marque.json (s'il existe) est copié à côté de la page sous le nom logo.png.
Chrome est lancé par marque.chrome_run (il le relance s'il se bloque). Rien ne quitte l'ordinateur
sauf le chargement des polices Google Fonts (Internet requis).
"""
import argparse, pathlib, re, shutil, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import marque  # noqa: E402

DEBUT, FIN = '<!--marque-->', '<!--/marque-->'
COULEURS = {f'--{n}': n for n in ('principale', 'foncee', 'texte', 'doux', 'ligne', 'teinte', 'clair')}


def bloc(pdf):
    b = DEBUT + marque.lien_polices() + marque.css_vars(COULEURS)
    if pdf:
        b += '<style>@page{size:A4;margin:0}</style>'
    return b + FIN


def injecter(html, b):
    html = re.sub(re.escape(DEBUT) + '.*?' + re.escape(FIN), '', html, flags=re.S)
    i = html.lower().find('</head>')
    return html[:i] + b + html[i:] if i >= 0 else b + html


def nb_pages(pdf):
    try:
        import fitz
        return len(fitz.open(pdf))
    except Exception:
        return len(re.findall(rb'/Type\s*/Page(?![a-zA-Z])', pdf.read_bytes()))


def main():
    a = argparse.ArgumentParser()
    a.add_argument('page')
    a.add_argument('--pdf', action='store_true')
    a.add_argument('--png', action='store_true')
    a.add_argument('--largeur', type=int, default=794)
    a.add_argument('--hauteur', type=int, default=1123)
    a.add_argument('--pages', type=int, default=1)
    a.add_argument('--suffixe', default='')
    a.add_argument('--garder', action='store_true')
    o = a.parse_args()
    veut_pdf = o.pdf or not o.png
    veut_png = o.png or not o.pdf

    src = pathlib.Path(o.page).expanduser().resolve()
    if not src.is_file():
        raise SystemExit(f'Page introuvable : {src}')
    html = injecter(src.read_text(encoding='utf-8'), bloc(veut_pdf))
    logo = marque.logo()
    if logo:
        shutil.copy(logo, src.parent / 'logo.png')
    if o.garder:
        src.write_text(html, encoding='utf-8')
        rendu = src
    else:
        rendu = src.with_name(src.stem + '.rendu.html')
        rendu.write_text(html, encoding='utf-8')
    alertes = []
    try:
        if veut_pdf:
            pdf = src.with_suffix('.pdf')
            marque.chrome_run(['--no-pdf-header-footer', f'--print-to-pdf={pdf}', rendu.as_uri()])
            n = nb_pages(pdf) if pdf.is_file() else 0
            print(f'PDF : {pdf} ({n} page(s))')
            if n == 0:
                alertes.append('le PDF n\'a pas été créé')
            elif n > o.pages:
                alertes.append(f'le PDF fait {n} pages (attendu : {o.pages} max) : la page déborde, réduis le texte')
        if veut_png:
            png = src.with_name(src.stem + (f'-{o.suffixe}' if o.suffixe else '') + '.png')
            marque.chrome_run([f'--screenshot={png}', f'--window-size={o.largeur},{o.hauteur}', '--hide-scrollbars', rendu.as_uri()])
            print(f'PNG : {png}' + ('' if png.is_file() else ' (non créé)'))
            if not png.is_file():
                alertes.append('l\'image n\'a pas été créée')
    finally:
        if rendu != src:
            rendu.unlink(missing_ok=True)
    print('Logo : ' + (str(src.parent / 'logo.png') if logo else 'aucun (marque.json : logo vide)'))
    for t in alertes:
        print('ALERTE : ' + t)
    print('Regarde l\'image avant de livrer : rien de coupé, rien qui se chevauche.')
    return 1 if alertes else 0


if __name__ == '__main__':
    sys.exit(main())
