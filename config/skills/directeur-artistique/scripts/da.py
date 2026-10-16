"""Directeur artistique : écrit ta DA dans marque.json, montre l'échantillon, fabrique la bible en PDF.

Usage :
  python3 da.py planche [couleurs/polices] --out planche-da.png   échantillon visuel (palette, polices, mini-maquettes) SANS rien écrire
  python3 da.py ecrire  [couleurs/polices]                        écrit ~/Documents/Brain/00-Moi/marque.json (copie .bak avant)
  python3 da.py bible corps.html --out bible-da.pdf               bible A4 en PDF à tes couleurs (corps = des <section class="page">)

Options (toutes facultatives, ce qui manque est calculé ou repris de marque.json) :
  --principale #HEX  --foncee #HEX  --texte #HEX  --doux #HEX  --ligne #HEX  --teinte #HEX  --clair #HEX  --accent #HEX
  --police-titre "Nom Google Fonts"  --police-texte "Nom Google Fonts"
  --nom "Ton nom ou ta marque"  --pseudo "@toncompte" (vide = jamais affiché)  --logo /chemin/logo.png

Contrôles automatiques : contraste (texte lisible sur fond clair, texte blanc lisible sur la couleur principale)
et existence des polices dans Google Fonts. Une ALERTE = à corriger avant d'écrire.
"""
import argparse, html, json, os, pathlib, re, shutil, subprocess, sys, tempfile, urllib.error, urllib.parse, urllib.request

sys.path.insert(0, str(pathlib.Path.home() / 'Documents' / 'Brain' / '_outils'))
import marque  # noqa: E402

ICI = pathlib.Path(__file__).resolve().parent
GAB = ICI.parent / 'gabarit'
HEX = re.compile(r'^#[0-9A-Fa-f]{6}$')


# ---------- couleurs ----------
def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def hexa(c):
    return '#%02X%02X%02X' % tuple(max(0, min(255, round(x))) for x in c)


def mix(a, b, t):
    """t = part de b (0 à 1)."""
    ra, rb = rgb(a), rgb(b)
    return hexa([ra[i] * (1 - t) + rb[i] * t for i in range(3)])


def lum(h):
    def f(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (f(x) for x in rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contraste(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def assombrir_jusqua(h, fond, mini):
    """Fonce h jusqu'à atteindre le contraste `mini` sur `fond`."""
    for k in range(0, 21):
        c = mix(h, '#000000', k * 0.05)
        if contraste(c, fond) >= mini:
            return c
    return '#000000'


# ---------- calcul de la palette ----------
def construire(a):
    m = marque.charger()
    c = dict(m['couleurs'])
    donne = {k: getattr(a, k) for k in ('principale', 'foncee', 'texte', 'doux', 'ligne', 'teinte', 'clair', 'accent') if getattr(a, k)}
    for k, v in donne.items():
        if not HEX.match(v):
            sys.exit(f'Couleur invalide pour --{k} : {v} (format attendu : #RRGGBB)')
    c.update(donne)
    clair = c['clair']
    if 'principale' in donne:  # la teinte et l'accent suivent la couleur de marque
        if 'teinte' not in donne:
            c['teinte'] = mix(c['principale'], clair, 0.93)
    if 'foncee' in donne:
        if 'texte' not in donne:
            c['texte'] = mix(c['foncee'], clair, 0.12)
        if 'doux' not in donne:
            c['doux'] = assombrir_jusqua(mix(c['foncee'], clair, 0.5), clair, 4.6)
        if 'ligne' not in donne:
            c['ligne'] = mix(c['foncee'], clair, 0.9)
    if 'accent' not in donne:
        # accent = version claire de la couleur de marque, pour les fonds sombres (couvertures, boutons)
        c['accent'] = mix(c['principale'], '#FFFFFF', 0.5)
    p = dict(m['polices'])
    if a.police_titre:
        p['titre'] = a.police_titre
    if a.police_texte:
        p['texte'] = a.police_texte
    return m, c, p


def verifier(c, p):
    al = []
    clair = c['clair']
    t = contraste(c['texte'], clair)
    if t < 4.5:
        al.append(f"ALERTE : le texte ({c['texte']}) est trop pâle sur le fond ({clair}) : contraste {t:.1f}, il faut 4.5 minimum")
    d = contraste(c['doux'], clair)
    if d < 4.5:
        al.append(f"ALERTE : la couleur douce ({c['doux']}) est trop pâle pour du petit texte : contraste {d:.1f}, il faut 4.5")
    pr = contraste(c['principale'], clair)
    if pr < 3:
        al.append(f"ALERTE : la couleur principale ({c['principale']}) est trop pâle pour des titres sur fond clair : contraste {pr:.1f}, il faut 3 minimum")
    bt = contraste(clair, c['principale'])
    if bt < 3:
        al.append(f"ALERTE : du texte clair sur la couleur principale ({c['principale']}) ne se lit pas : contraste {bt:.1f}")
    if contraste(c['foncee'], clair) < 7:
        al.append(f"ALERTE : la couleur foncée ({c['foncee']}) n'est pas assez foncée pour les titres et les fonds sombres")
    for nom in dict.fromkeys([p['titre'], p['texte']]):
        al.append(police_ok(nom))
    return [x for x in al if x]


def police_ok(nom):
    url = 'https://fonts.googleapis.com/css2?family=' + urllib.parse.quote_plus(nom) + '&display=swap'
    try:
        urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=8)
    except urllib.error.HTTPError as e:
        return f"ALERTE : la police « {nom} » n'existe pas dans Google Fonts (erreur {e.code}) : vérifie l'orthographe sur fonts.google.com"
    except Exception:
        return f"À vérifier : pas d'Internet, impossible de confirmer que « {nom} » existe dans Google Fonts"
    return ''


# ---------- Chrome ----------
def chrome_rendu(page_html, sortie, largeur, hauteur, pdf=False, fichiers=None):
    tmp = tempfile.mkdtemp(prefix='da-')
    try:
        for nom, src in (fichiers or {}).items():
            shutil.copy(src, os.path.join(tmp, nom))
        page = os.path.join(tmp, 'page.html')
        pathlib.Path(page).write_text(page_html, encoding='utf-8')
        out = os.path.join(tmp, 'out.pdf' if pdf else 'out.png')
        cmd = [marque.chrome(), '--headless=new', '--disable-gpu', '--hide-scrollbars', '--allow-file-access-from-files',
               '--use-mock-keychain', f'--user-data-dir={tmp}/chrome', '--virtual-time-budget=8000']
        cmd += ['--no-pdf-header-footer', f'--print-to-pdf={out}'] if pdf else [f'--window-size={largeur},{hauteur}', f'--screenshot={out}']
        subprocess.run(cmd + ['file://' + page], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
        os.makedirs(os.path.dirname(os.path.abspath(sortie)), exist_ok=True)
        shutil.copy(out, sortie)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def fonts_link(p):
    fam = '&'.join('family=' + urllib.parse.quote_plus(f) + ':wght@400;500;600;700;800' for f in dict.fromkeys([p['titre'], p['texte']]))
    return f'<link href="https://fonts.googleapis.com/css2?{fam}&display=swap" rel="stylesheet">'


def vars_css(c, p):
    return ('<style>:root{' + ';'.join(f'--{k}:{v}' for k, v in c.items()) +
            f";--police-titre:'{p['titre']}';--police-texte:'{p['texte']}'}}</style>")


# ---------- planche (échantillon) ----------
ROLES = [('principale', 'Principale', 'boutons, mots forts'), ('foncee', 'Foncée', 'titres, fonds sombres'), ('texte', 'Texte', 'phrases'),
         ('doux', 'Douce', 'petits textes'), ('ligne', 'Ligne', 'séparateurs'), ('teinte', 'Teinte', 'encadrés'),
         ('clair', 'Fond', 'fond des pages'), ('accent', 'Accent', 'sur fond sombre')]


def planche(m, c, p, sortie):
    sw = ''
    for k, nom, role in ROLES:
        v = c[k]
        encre = '#FFFFFF' if lum(v) < 0.4 else '#111111'
        sw += (f'<div class="sw"><div class="chip" style="background:{v};color:{encre}">{html.escape(nom)}</div>'
               f'<div class="hex">{v}</div><div class="role">{html.escape(role)}</div></div>')
    logo = marque.logo()
    nom = html.escape(m.get('nom') or 'Ton nom')
    logo_html = '<img class="logo" src="logo' + logo.suffix + '">' if logo else ''
    page = f"""<!doctype html><html><head><meta charset="utf-8">{fonts_link(p)}{vars_css(c, p)}
<style>
*{{box-sizing:border-box}} body{{margin:0;width:1200px;background:var(--clair);font-family:var(--police-texte),sans-serif;color:var(--texte);padding:56px 64px}}
h1{{font-family:var(--police-titre),sans-serif;font-weight:800;font-size:54px;color:var(--foncee);margin:0 0 6px;letter-spacing:-1px}}
.sub{{color:var(--doux);font-size:20px;margin-bottom:34px}}
.row{{display:flex;gap:14px}} .sw{{flex:1}} .chip{{height:96px;border-radius:14px;display:flex;align-items:flex-end;padding:10px 12px;font-weight:700;font-size:16px;border:1px solid var(--ligne)}}
.hex{{font-weight:700;font-size:17px;margin-top:8px;color:var(--foncee)}} .role{{font-size:14px;color:var(--doux)}}
.cols{{display:flex;gap:36px;margin-top:40px}} .col{{flex:1}}
.lab{{font-size:14px;letter-spacing:.18em;text-transform:uppercase;color:var(--principale);font-weight:700;margin-bottom:12px}}
.type h2{{font-family:var(--police-titre),sans-serif;font-weight:800;font-size:44px;line-height:1.05;color:var(--foncee);margin:0 0 10px}}
.type h2 span{{color:var(--principale)}} .type p{{font-size:21px;line-height:1.5;margin:0 0 12px}}
.type .noms{{font-size:15px;color:var(--doux)}}
.card{{width:300px;height:400px;border-radius:18px;background:var(--foncee);color:#fff;padding:30px;display:flex;flex-direction:column;justify-content:flex-end;position:relative;overflow:hidden}}
.card:before{{content:"";position:absolute;right:-60px;top:-60px;width:220px;height:220px;border-radius:50%;background:var(--principale);opacity:.9}}
.card h3{{font-family:var(--police-titre),sans-serif;font-weight:800;font-size:34px;line-height:1.05;margin:0 0 10px;position:relative}}
.card h3 span{{color:var(--accent)}} .card p{{margin:0;font-size:17px;opacity:.9;position:relative}}
.card2{{width:300px;height:400px;border-radius:18px;background:var(--teinte);border:1px solid var(--ligne);padding:30px;display:flex;flex-direction:column;justify-content:center}}
.card2 h3{{font-family:var(--police-titre),sans-serif;font-weight:800;font-size:30px;line-height:1.1;margin:0 0 14px;color:var(--foncee)}}
.btn{{display:inline-block;background:var(--principale);color:var(--clair);font-family:var(--police-titre),sans-serif;font-weight:700;font-size:20px;padding:14px 26px;border-radius:12px;align-self:flex-start}}
.logo{{height:44px;margin-bottom:14px;display:block}}
.foot{{margin-top:34px;padding-top:14px;border-top:2px solid var(--ligne);font-size:15px;color:var(--doux);display:flex;justify-content:space-between}} .foot b{{color:var(--foncee)}}
</style></head><body>
{logo_html}<h1>Ta DA : <span style="color:var(--principale)">{nom}</span></h1>
<div class="sub">Échantillon : palette, polices et deux mini-maquettes. Pas de fichier modifié tant que tu n'as pas dit OK.</div>
<div class="row">{sw}</div>
<div class="cols">
 <div class="col type"><div class="lab">Polices</div>
  <h2>Un titre qui <span>accroche</span></h2>
  <p>Voilà à quoi ressemblent tes phrases courantes : simples, lisibles, sur un téléphone comme sur un écran de salon.</p>
  <div class="noms">Titres : <b>{html.escape(p['titre'])}</b> · Texte : <b>{html.escape(p['texte'])}</b></div></div>
 <div class="col"><div class="lab">Fond sombre</div><div class="card"><h3>Ta grande idée en <span>une phrase</span></h3><p>Une phrase pour la prolonger.</p></div></div>
 <div class="col"><div class="lab">Fond clair</div><div class="card2"><h3>Ton offre, en clair</h3><div class="btn">Commente MOT</div></div></div>
</div>
<div class="foot"><span><b>{nom}</b></span><span>{html.escape(m.get('pseudo') or '')}</span></div>
</body></html>"""
    fich = {'logo' + logo.suffix: str(logo)} if logo else None
    chrome_rendu(page, sortie, 1200, 1000, fichiers=fich)
    print('OK', sortie)


# ---------- bible ----------
def bible(corps, sortie):
    m = marque.charger()
    c, p = m['couleurs'], m['polices']
    c = dict(c)
    c.setdefault('accent', mix(c['principale'], '#FFFFFF', 0.5))
    logo = marque.logo()
    gab = (GAB / 'bible.html').read_text(encoding='utf-8')
    body = pathlib.Path(corps).read_text(encoding='utf-8')
    page = (gab.replace('%%FONTS%%', fonts_link(p)).replace('%%MARQUE%%', vars_css(c, p)).replace('%%PAGES%%', body)
            .replace('%%NOM%%', html.escape(m.get('nom') or 'Ma marque')))
    fich = None
    if logo:
        page = page.replace('%%LOGO%%', f'<img class="toplogo" src="logo{logo.suffix}">')
        fich = {'logo' + logo.suffix: str(logo)}
    else:
        page = page.replace('%%LOGO%%', '')
    chrome_rendu(page, sortie, 0, 0, pdf=True, fichiers=fich)
    try:
        import fitz
        n = len(fitz.open(sortie))
        print(f'OK {sortie} ({n} pages)')
        if n > 9:
            print(f'ALERTE : {n} pages, la bible doit tenir en 9 pages maximum')
    except ImportError:
        print('OK', sortie, '(installe PyMuPDF pour compter les pages : pip3 install pymupdf)')


# ---------- écrire ----------
def ecrire(a):
    m, c, p = construire(a)
    al = verifier(c, p)
    for x in al:
        print(x)
    if any(x.startswith('ALERTE') for x in al) and not a.forcer:
        sys.exit('Rien écrit : corrige les ALERTES (ou relance avec --forcer si tu assumes).')
    brut = {}
    try:
        brut = json.loads(marque.FICHIER.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        pass
    if marque.FICHIER.exists():
        shutil.copy(marque.FICHIER, str(marque.FICHIER) + '.bak')
    sortie = dict(brut)
    sortie['nom'] = a.nom if a.nom is not None else m.get('nom', '')
    sortie['pseudo'] = a.pseudo if a.pseudo is not None else m.get('pseudo', '')
    sortie['logo'] = a.logo if a.logo is not None else m.get('logo', '')
    sortie['couleurs'] = c
    sortie['polices'] = p
    if sortie['logo'] and not pathlib.Path(os.path.expanduser(sortie['logo'])).is_file():
        sys.exit(f"Logo introuvable : {sortie['logo']}")
    marque.FICHIER.parent.mkdir(parents=True, exist_ok=True)
    marque.FICHIER.write_text(json.dumps(sortie, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    json.loads(marque.FICHIER.read_text(encoding='utf-8'))  # relecture : le JSON est valide
    print('OK écrit', marque.FICHIER)
    print(json.dumps({k: sortie[k] for k in ('nom', 'pseudo', 'logo', 'couleurs', 'polices')}, ensure_ascii=False, indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('mode', choices=['planche', 'ecrire', 'bible'])
    ap.add_argument('corps', nargs='?', help='bible : fichier HTML des pages')
    for k in ('principale', 'foncee', 'texte', 'doux', 'ligne', 'teinte', 'clair', 'accent'):
        ap.add_argument('--' + k)
    ap.add_argument('--police-titre')
    ap.add_argument('--police-texte')
    ap.add_argument('--nom')
    ap.add_argument('--pseudo')
    ap.add_argument('--logo')
    ap.add_argument('--out')
    ap.add_argument('--forcer', action='store_true')
    a = ap.parse_args()
    if a.mode == 'ecrire':
        ecrire(a)
    elif a.mode == 'planche':
        m, c, p = construire(a)
        if a.nom is not None:
            m['nom'] = a.nom
        for x in verifier(c, p):
            print(x)
        planche(m, c, p, a.out or 'planche-da.png')
    else:
        if not a.corps or not a.out:
            sys.exit('Usage : da.py bible corps.html --out bible-da.pdf')
        bible(a.corps, a.out)


if __name__ == '__main__':
    main()
