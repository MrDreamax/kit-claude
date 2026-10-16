"""L'Auditeur Insta : audit.json -> audit.html + PDF de 2 pages, aux couleurs de ~/Documents/Brain/00-Moi/marque.json.

Usage : python3 build.py <audit.json> <dossier_de_sortie>
Sort : <dossier>/audit.html, <dossier>/<nom>.pdf, <dossier>/pages/page-N.png (pour la relecture à l'œil)
et imprime les ALERTES (total qui ne tombe pas juste, critère manquant, champ vide, page qui déborde).
La note totale est CALCULÉE (somme des notes des critères) : n'écris pas de total à la main.

audit.json :
{
  "nom": "Audit-COMPTE", "titre": "Audit Instagram", "compte": "@pseudo", "date": "JJ/MM/AAAA",
  "resume": "une ligne : le diagnostic",
  "marque": "TON NOM",                                   # pied de page (défaut : "nom" de marque.json)
  "criteres": [ {"nom": "Bio, 1re ligne", "pts": 14, "note": 6, "pourquoi": "une ligne", "source": "[P 24]"}, ... 12 critères, pts = 100 au total ],
  "mediane": "1 250 vues (30 derniers posts)",
  "top":  [ {"titre": "sujet du post", "multiple": "4,2x", "pourquoi": "ce qui le sépare des autres"}, ... 3 ],
  "flop": [ {"titre": "...", "multiple": "0,3x", "pourquoi": "..."}, ... 3 ],
  "diagnostic": "des vues sans abonnés = problème de profil ; pas de vues = problème de hook (une phrase)",
  "leviers": [ {"titre": "...", "constat": "chiffré", "pourquoi": "ce que ça bloque (avec la source)", "gain": "ce que ça change"}, ... 3 ],
  "sources": "fiches du Brain et données utilisées (Apify, captures fournies...)"
}
"""
import html, json, os, pathlib, re, shutil, signal, subprocess, sys, tempfile

sys.path.insert(0, str(pathlib.Path.home() / 'Documents' / 'Brain' / '_outils'))
import marque  # couleurs, polices, logo, Chrome de l'utilisateur

SKILL = pathlib.Path(__file__).resolve().parent.parent
GAB = SKILL / 'gabarit'
CHROME = marque.chrome()
DA = {'--blue': 'principale', '--navy': 'foncee', '--ink': 'texte', '--mute': 'doux', '--line': 'ligne', '--tint': 'teinte'}
alerts = []
LOGO = ''


def chrome_run(args, essais=4, delai=30):
    """Lance Chrome sans interface. Chrome se bloque parfois au démarrage : on le tue et on réessaie (profil neuf à chaque fois)."""
    for n in range(essais):
        prof = tempfile.mkdtemp(prefix='chrome-')
        p = subprocess.Popen([CHROME, '--headless=new', '--use-mock-keychain', '--disable-gpu', f'--user-data-dir={prof}', '--virtual-time-budget=5000'] + args,
                             stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, start_new_session=True)
        try:
            sortie = p.communicate(timeout=delai)[0]
            shutil.rmtree(prof, ignore_errors=True)
            return sortie
        except subprocess.TimeoutExpired:
            try:
                os.killpg(p.pid, signal.SIGKILL)
            except Exception:  # Windows : pas de groupe de processus
                p.kill()
            p.communicate()
            shutil.rmtree(prof, ignore_errors=True)
    raise SystemExit('Chrome ne répond pas après 4 essais : ferme les fenêtres Chrome inutiles, puis relance.')


def e(s):
    return html.escape(str(s if s is not None else ''))


def foot(nom, droite):
    return f'<div class="foot"><span><b>{e(nom)}</b></span><span>{e(droite)}</span></div>'


def classe(note, pts):
    r = note / pts if pts else 0
    return 'ok' if r >= .75 else 'mid' if r >= .4 else 'ko'


def verifier(a):
    for k in ('compte', 'date', 'resume', 'mediane', 'diagnostic', 'sources'):
        if not a.get(k):
            alerts.append(f'champ « {k} » vide')
    cr = a.get('criteres', [])
    if len(cr) != 12:
        alerts.append(f'{len(cr)} critères (12 attendus)')
    for c in cr:
        for k in ('nom', 'pourquoi', 'source'):
            if not c.get(k):
                alerts.append(f"critère « {c.get('nom', '?')} » : champ « {k} » vide")
        if not isinstance(c.get('pts'), (int, float)) or not isinstance(c.get('note'), (int, float)):
            alerts.append(f"critère « {c.get('nom', '?')} » : pts ou note manquants")
        elif c['note'] > c['pts'] or c['note'] < 0:
            alerts.append(f"critère « {c['nom']} » : note {c['note']} hors de 0 à {c['pts']}")
        if len(c.get('pourquoi', '')) > 110:
            alerts.append(f"critère « {c.get('nom')} » : « pourquoi » de {len(c['pourquoi'])} caractères (110 max, une ligne)")
    total_pts = sum(c.get('pts', 0) for c in cr if isinstance(c.get('pts'), (int, float)))
    if cr and total_pts != 100:
        alerts.append(f'les points des critères font {total_pts}, pas 100')
    for k, n in (('top', 3), ('flop', 3), ('leviers', 3)):
        if len(a.get(k, [])) != n:
            alerts.append(f"{len(a.get(k, []))} éléments dans « {k} » ({n} attendus)")
    for k in ('top', 'flop'):
        for x in a.get(k, []):
            if not (x.get('titre') and x.get('multiple') and x.get('pourquoi')):
                alerts.append(f'« {k} » : un élément a un champ vide')
    for x in a.get('leviers', []):
        if not all(x.get(k) for k in ('titre', 'constat', 'pourquoi', 'gain')):
            alerts.append('« leviers » : un levier a un champ vide')


def page1(a, nom, total):
    rows = ''.join(
        f"<tr><td class='c'>{e(c['nom'])}<small>{e(c.get('source', ''))}</small></td>"
        f"<td class='b'><div class='bar'><i class='{classe(c['note'], c['pts'])}' style='width:{round(100 * c['note'] / c['pts']) if c['pts'] else 0}%'></i></div></td>"
        f"<td class='p'>{c['note']:g}<span>/{c['pts']:g}</span></td><td>{e(c['pourquoi'])}</td></tr>"
        for c in a.get('criteres', []) if isinstance(c.get('pts'), (int, float)) and isinstance(c.get('note'), (int, float)))
    return f"""<section class="page">
  {LOGO}
  <div class="head"><div><div class="kicker">{e(a.get('titre', 'Audit Instagram'))} · {e(a.get('date', ''))}</div><h1>{e(a.get('compte', ''))}</h1>
    <p class="resume">{e(a.get('resume', ''))}</p></div>
    <div class="score"><b>{total:g}<i>/100</i></b><small>Note du profil</small></div></div>
  <table><tr><th>Critère</th><th>Score</th><th>Note</th><th>Pourquoi</th></tr>{rows}</table>
  {foot(nom, 'Le profil sur 100')}
  <div class="src">Chaque critère cite sa règle (fiches experts du Brain) ; « hypothèse » = pas de règle sourcée.</div>
</section>"""


def cartes(liste, kind):
    return ''.join(f"<div class='card {kind}'><b class='m'>{e(x.get('multiple', ''))}</b><span class='t'>{e(x.get('titre', ''))}</span><span class='w'>{e(x.get('pourquoi', ''))}</span></div>" for x in liste)


def page2(a, nom):
    lev = ''.join(
        f"<div class='lev'><div class='n'>{i}</div><div><div class='t'>{e(x.get('titre', ''))}</div>"
        f"<p><b>Constat</b> {e(x.get('constat', ''))}</p><p><b>Pourquoi ça bloque</b> {e(x.get('pourquoi', ''))}</p><p><b>Si c'est réglé</b> {e(x.get('gain', ''))}</p></div></div>"
        for i, x in enumerate(a.get('leviers', []), 1))
    return f"""<section class="page">
  <div class="kicker">Les 30 derniers posts · médiane : {e(a.get('mediane', ''))}</div>
  <h2>Ce qui marche, <span>ce qui flop</span></h2>
  <div class="cols"><div>{cartes(a.get('top', []), 'top')}</div><div>{cartes(a.get('flop', []), 'flop')}</div></div>
  <div class="note">{e(a.get('diagnostic', ''))}</div>
  <h2>Les 3 leviers <span>par ordre d'impact</span></h2>
  {lev}
  {foot(nom, 'Top, flop et leviers')}
  <div class="src">Sources : {e(a.get('sources', ''))}</div>
</section>"""


def main():
    a = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'))
    out = pathlib.Path(sys.argv[2]).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    global LOGO
    lg = marque.logo()
    if lg:
        shutil.copy(lg, out / ('logo' + lg.suffix))
        LOGO = f'<img class="toplogo" src="logo{lg.suffix}" alt="">'
    nom = a.get('marque') or marque.charger().get('nom', '').upper()
    verifier(a)
    total = sum(c['note'] for c in a.get('criteres', []) if isinstance(c.get('note'), (int, float)))
    pages = [page1(a, nom, total), page2(a, nom)]
    doc = ((GAB / 'page.html').read_text(encoding='utf-8').replace('%%TITLE%%', e(a.get('titre', 'Audit Instagram')))
           .replace('%%PAGES%%', '\n\n'.join(pages)).replace('%%FONTS%%', marque.lien_polices()).replace('%%MARQUE%%', marque.css_vars(DA)))
    (out / 'audit.html').write_text(doc, encoding='utf-8')

    pdf = out / f"{a.get('nom', 'Audit')}.pdf"
    chrome_run(['--no-pdf-header-footer', f'--print-to-pdf={pdf}', (out / 'audit.html').as_uri()])
    dom = chrome_run(['--window-size=794,1123', '--dump-dom', (out / 'audit.html').as_uri()])
    m = re.search(r'data-overflow="([^"]*)"', dom)
    if m is None:
        alerts.append('contrôle de débordement non lu : regarde les PNG')
    elif m.group(1):
        alerts.append(f'contenu qui déborde (passe sous les sources) page(s) {m.group(1)} : raccourcis')
    if not pdf.exists():
        print('ERREUR : PDF non produit'); sys.exit(1)

    import fitz  # PyMuPDF : contrôle des pages + PNG pour la relecture à l'œil
    d = fitz.open(pdf)
    (out / 'pages').mkdir(exist_ok=True)
    for i, pg in enumerate(d, 1):
        pg.get_pixmap(dpi=80).save(out / 'pages' / f'page-{i}.png')
        if not pg.get_text().strip():
            alerts.append(f'page {i} vide')
    if len(d) != 2:
        alerts.append(f'{len(d)} pages dans le PDF (2 attendues) : un bloc déborde')
    print(f'ok : {pdf} ({len(d)} pages), note {total:g}/100')
    for x in alerts:
        print('ALERTE', x)


if __name__ == '__main__':
    main()
