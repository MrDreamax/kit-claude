"""L'Usine à pubs : pubs.json -> pubs.html + PDF « à tourner », aux couleurs de ~/Documents/Brain/00-Moi/marque.json.

Usage : python3 build.py <pubs.json> <dossier_de_sortie>
Sort : <dossier>/pubs.html, <dossier>/<nom>.pdf, <dossier>/pages/page-N.png (pour la relecture à l'œil)
et imprime les ALERTES (hook qui salue, titre ou description trop longs, script trop long, risque Meta, champ vide, page qui déborde).

pubs.json :
{
  "nom": "Pubs-AAAA-MM-JJ", "titre": "Pubs à tourner", "kicker": "Pubs Meta", "h1": "6 pubs. <span>1 session.</span>",
  "lead": "une ligne : le plan de test",
  "avant": ["case à cocher avant de tourner (accord client, CTA confirmé...)"],
  "marque": "TON NOM",                              # pied de page (défaut : "nom" de marque.json)
  "pubs": [ {"angle": "preuve client", "niveau": "connaît le problème", "sujet": "titre court",
             "screen": "3-5 mots à l'écran", "hook": "mot à mot (3 s)", "voir": "ce qu'on voit à l'écran",
             "points": ["point 1", "point 2", "point 3"], "preuve": "phrase de preuve <span>en couleur</span>",
             "cta": "phrase de CTA mot à mot", "texte": "texte principal Meta", "titre": "titre Meta (40 car. max)",
             "description": "description Meta (30 car. max)", "risque": "aucun|moyen|haut", "risque_note": "phrase en cause + réécriture",
             "client_cite": false, "src": "verbatim (fichier), fiche expert (section)"} ]
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


def plain(html):
    return re.sub(r'<[^>]+>', ' ', html or '')


def words(html):
    return len([w for w in plain(html).split() if re.search(r'\w', w)])


# Pièges de hook (fiche experts-hooks-retention §1 : pas de salutation, pas de préambule).
HOOK_KO = [(r"^\W*(salut|bonjour|hello|coucou|hey)\b", "salutation au début"),
           (r"(aujourd'hui,? (je vais|on va)|dans cette vidéo|je vais (vous|te) parler|et si je te disais|arrête de scroller|pov\b)", "préambule ou formule bannie")]
# Règles Meta (02-Formations/regles-pub-meta.md) : repérage automatique, toujours « à vérifier » par un humain.
ATTRIBUT = re.compile(r"\b(tu es|t'es|vous êtes|tu as|t'as)\s+(\w+\s+){0,2}(fauché|endetté|ruiné|épuisé|déprimé|dépressif|anxieux|seul|obèse|gros|malade|divorcé|chômeur|en burn-?out|en dépression|trop vieux)", re.I)
AGE = re.compile(r"\b(de plus de|à plus de|après)\s+\d{2}\s+ans\b", re.I)
REVENU = re.compile(r"\d[\d\s.,]*\s?k?\s?(€|euros?|\$)\s*(par|/|en)\s*(mois|semaine|jour|an)\b", re.I)
GARANTI = re.compile(r"(?<!non )\b(garanti(e|s)?|assuré(e|s)?|sans risque)\b", re.I)
CHAMPS = ('angle', 'screen', 'hook', 'points', 'preuve', 'cta', 'texte', 'titre', 'description', 'risque', 'src')


def nb(s):
    return (s or '').replace(' ?', '&nbsp;?').replace(' !', '&nbsp;!').replace(' :', '&nbsp;:')


def foot(nom, droite):
    return f'<div class="foot"><span><b>{nom}</b></span><span>{droite}</span></div>'


def controle(p, n):
    q = f'pub {n}'
    for k in CHAMPS:
        if not p.get(k):
            alerts.append(f'{q} : champ « {k} » vide')
    t = plain(p.get('hook')).strip().lower()
    for rx, why in HOOK_KO:
        if re.search(rx, t):
            alerts.append(f'{q} : hook, {why}')
    if words(p.get('screen')) > 5:
        alerts.append(f"{q} : texte écran de {words(p['screen'])} mots (5 max)")
    if len(p.get('points', [])) != 3:
        alerts.append(f"{q} : {len(p.get('points', []))} points (3 attendus)")
    dit = words(p.get('hook')) + sum(words(x) for x in p.get('points', [])) + words(p.get('preuve')) + words(p.get('cta'))
    if dit > 115:
        alerts.append(f'{q} : {dit} mots dits, environ {round(dit / 2.5)} s (45 s max)')
    if len(plain(p.get('titre'))) > 40:
        alerts.append(f"{q} : titre de {len(plain(p['titre']))} caractères (40 max)")
    if len(plain(p.get('description'))) > 30:
        alerts.append(f"{q} : description de {len(plain(p['description']))} caractères (30 max)")
    if p.get('risque') not in ('aucun', 'moyen', 'haut'):
        alerts.append(f'{q} : risque Meta doit être aucun, moyen ou haut')
    elif p['risque'] == 'haut':
        alerts.append(f'{q} : risque Meta haut, réécris avant de livrer')
    tout = plain(' '.join([p.get(k, '') for k in ('screen', 'hook', 'preuve', 'cta', 'texte', 'titre', 'description')] + p.get('points', [])))
    for rx, why in ((ATTRIBUT, 'attribut personnel prêté au spectateur'), (AGE, 'âge visé'), (REVENU, 'montant de revenu'), (GARANTI, 'promesse de résultat')):
        m = rx.search(tout)
        if m:
            alerts.append(f'{q} (à vérifier) : Meta, {why} : « {m.group(0).strip()} »')


def cover(lot, pubs, nom, i0, lignes, premiere):
    rows = ''.join(f"<tr><td class='n'>{i}</td><td>{p.get('angle', '')}<br><span style='color:var(--mute)'>{p.get('niveau', '')}</span></td>"
                   f"<td>{nb(plain(p.get('hook')))}</td><td><span class='risk {p.get('risque', '')}'>{p.get('risque', '')}</span></td></tr>"
                   for i, p in lignes)
    avant = ''.join(f'<li>{a}</li>' for a in lot.get('avant', []))
    entete = (f"{LOGO}<div class='kicker'>{lot.get('kicker', '')}</div><h1>{lot.get('h1', '')}</h1><p class='lead'>{lot.get('lead', '')}</p>"
              if premiere else f"<div class='kicker'>{lot.get('kicker', '')} (suite)</div>")
    return f"""<section class="page">
  {entete}
  <table><tr><th>#</th><th>Angle</th><th>Hook à dire</th><th>Risque Meta</th></tr>{rows}</table>
  {'<div class="kicker">Avant de tourner</div><ul class="check">' + avant + '</ul>' if premiere and avant else ''}
  {foot(nom, lot.get('titre', ''))}
</section>"""


def page(p, n, total, nom):
    pts = ''.join(f'<li>{x}</li>' for x in p.get('points', []))
    texte = plain(p.get('texte')).strip()
    vu, reste = html.escape(texte[:125]), html.escape(texte[125:])
    warn = []
    if p.get('client_cite'):
        warn.append('<b>Client cité :</b> accord écrit à obtenir avant diffusion, sans son nom sauf accord explicite.')
    if p.get('risque_note'):
        warn.append(f"<b>Meta ({p.get('risque', '')}) :</b> {p['risque_note']}")
    w = ''.join(f"<div class='warn'>{x}</div>" for x in warn)
    tt, dd = len(plain(p.get('titre'))), len(plain(p.get('description')))
    return f"""<section class="page">
  <div class="kicker">Pub {n} / {total}</div>
  <div class="meta"><span class="tag">{p.get('angle', '')}</span><span class="tag">Niveau : {p.get('niveau', '')}</span><span class="tag">≈ {round((words(p.get('hook')) + sum(words(x) for x in p.get('points', [])) + words(p.get('preuve')) + words(p.get('cta'))) / 2.5)} s</span><span class="tag">Risque Meta : {p.get('risque', '')}</span></div>
  <div class="screen"><small>Texte à l'écran</small>{nb(p.get('screen'))}</div>
  <div class="hookline"><small>Hook</small>{nb(p.get('hook'))}</div>
  <p class="voir"><b>On voit :</b> {p.get('voir', '')}</p>
  <ol class="pts">{pts}</ol>
  <div class="preuve">{p.get('preuve', '')}</div>
  <div class="cta"><b>CTA</b>{p.get('cta', '')}</div>
  <div class="meta2"><b class="l">Textes Meta</b>
    <p>Texte principal : {vu}<span class="cut">{reste}</span> <span class="n">({len(texte)} car., la partie claire est visible avant « Voir plus »)</span></p>
    <p>Titre : {html.escape(plain(p.get('titre')))} <span class="n">({tt}/40)</span> · Description : {html.escape(plain(p.get('description')))} <span class="n">({dd}/30)</span></p></div>
  {w}
  <div class="src">Sources : {p.get('src', '')}</div>
  {foot(nom, f'Pub {n} / {total}')}
</section>"""


def main():
    lot = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'))
    out = pathlib.Path(sys.argv[2]).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    global LOGO
    lg = marque.logo()
    if lg:
        shutil.copy(lg, out / ('logo' + lg.suffix))
        LOGO = f'<img class="toplogo" src="logo{lg.suffix}" alt="">'
    nom = lot.get('marque') or marque.charger().get('nom', '').upper()
    pubs = lot.get('pubs', [])
    if not pubs:
        print('ERREUR : aucune pub dans le fichier'); sys.exit(1)
    for i, p in enumerate(pubs, 1):
        controle(p, i)
    num = list(enumerate(pubs, 1))
    pages = []
    for k in range(0, len(num), 7):
        pages.append(cover(lot, pubs, nom, k, num[k:k + 7], k == 0))
    pages += [page(p, i, len(pubs), nom) for i, p in num]
    html = ((GAB / 'page.html').read_text(encoding='utf-8').replace('%%TITLE%%', lot.get('titre', 'Pubs'))
            .replace('%%PAGES%%', '\n\n'.join(pages)).replace('%%FONTS%%', marque.lien_polices()).replace('%%MARQUE%%', marque.css_vars(DA)))
    (out / 'pubs.html').write_text(html, encoding='utf-8')

    pdf = out / f"{lot.get('nom', 'Pubs')}.pdf"
    chrome_run(['--no-pdf-header-footer', f'--print-to-pdf={pdf}', (out / 'pubs.html').as_uri()])
    dom = chrome_run(['--window-size=794,1123', '--dump-dom', (out / 'pubs.html').as_uri()])
    m = re.search(r'data-overflow="([^"]*)"', dom)
    if m is None:
        alerts.append('contrôle de débordement non lu : regarde les PNG')
    elif m.group(1):
        alerts.append(f'texte qui déborde (passe sous les sources) page(s) {m.group(1)} : raccourcis')
    if not pdf.exists():
        print('ERREUR : PDF non produit'); sys.exit(1)

    import fitz  # PyMuPDF : contrôle des pages + PNG pour la relecture à l'œil
    doc = fitz.open(pdf)
    (out / 'pages').mkdir(exist_ok=True)
    for i, pg in enumerate(doc, 1):
        pg.get_pixmap(dpi=70).save(out / 'pages' / f'page-{i}.png')
        if not pg.get_text().strip():
            alerts.append(f'page {i} vide')
    if len(doc) != len(pages):
        alerts.append(f'{len(doc)} pages dans le PDF pour {len(pages)} prévues : un bloc déborde')
    print(f'ok : {pdf} ({len(doc)} pages)')
    for a in alerts:
        print('ALERTE', a)


if __name__ == '__main__':
    main()
