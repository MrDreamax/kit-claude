"""Le Scripteur : lot.json -> scripts.html + PDF à tourner, aux couleurs de ~/Documents/Brain/00-Moi/marque.json.

Usage : python3 build.py <lot.json> <dossier_de_sortie>
Sort : <dossier>/scripts.html, <dossier>/<nom>.pdf, <dossier>/pages/page-N.png (pour la relecture visuelle)
et imprime les alertes (texte trop long, page qui déborde, champ manquant).

lot.json :
{
  "nom": "Scripts-S43", "titre": "Scripts semaine 43",
  "kicker": "Scripts semaine 43", "h1": "7 reels. <span>1 session.</span>", "lead": "...",
  "avant": ["case à cocher avant de tourner", "..."], "astuce": "<b>L'ordre de tournage :</b> ...",
  "marque": "TON NOM",                           # pied de page (défaut : "nom" de marque.json)
  "courts": [ {"kind": "qa|demo|tab|vo", "jour": "Lundi", "pilier": "Preuve", "cta": "GUIDE", "sujet": "...",
               "screen": "3-5 mots", "hook": "mot à mot", "points": ["...", "..."], "end": "phrase de fin <span>en bleu</span>",
               "ctatext": "Commente GUIDE.", "warn": "optionnel", "src": "sources"} ],
  "longs":  [ {"duree": "18-22 min", "titres": ["choisi", "option 2", "option 3"], "miniature": "...",
               "intro": ["phrase 1 mot à mot", "phrase 2"],
               "blocs": [ {"t": "0:30", "nom": "...", "montre": "ce qu'on voit à l'écran", "dit": ["point", "point"],
                           "rehook": "phrase mot à mot (optionnel)", "cta": "phrase mot à mot (optionnel)"} ],
               "fin": "...", "ctafinal": "...", "clips": ["moment à découper en reel"], "warn": "...", "src": "..."} ]
}
"""
import json, pathlib, re, shutil, subprocess, sys

sys.path.insert(0, str(pathlib.Path.home() / 'Documents' / 'Brain' / '_outils'))
import marque  # couleurs, polices, logo, Chrome de l'utilisateur

SKILL = pathlib.Path(__file__).resolve().parent.parent
GAB = SKILL / 'gabarit'

ICON = {'qa': 'questions-reponses.png', 'demo': 'demonstration.png', 'tab': 'tableau-blanc.png', 'vo': 'voix-off.png'}
FMT = {'qa': 'Questions-réponses', 'demo': 'Audit en live', 'tab': 'Tableau blanc', 'vo': 'Voix off sur B-roll'}
JOB = {'qa': ('Croître', ''), 'demo': ('Convertir', 'v'), 'tab': ('Convertir', 'v'), 'vo': ('Fidéliser', 'f')}

alerts = []
LOGO = ''
# variables du gabarit -> couleurs de marque.json
DA = {'--blue': 'principale', '--navy': 'foncee', '--ink': 'texte', '--mute': 'doux', '--line': 'ligne', '--tint': 'teinte'}


def words(html):
    return len([w for w in re.sub(r'<[^>]+>', ' ', html or '').split() if re.search(r'\w', w)])


# Pièges de hook (fiche experts-hooks-retention §1 : Kane [oniy8VQuOVs 283:23] pas de salutation,
# Paddy Galloway [AX3dEGjBg6w 06:23] pas de préambule « et si je te disais ». « Si tu... » = piège mesuré
# sur un seul compte FR : alerte douce seulement.
HOOK_KO = [(r"^\W*(salut|bonjour|hello|coucou|hey)\b", "salutation au début"),
           (r"(aujourd'hui,? (je vais|on va)|dans cette vidéo|je vais (vous|te) parler|et si je te disais)", "préambule avant le sujet")]
HOOK_DOUX = [(r"^\W*si tu\b", "début en « Si tu… » (piège mesuré sur un seul compte : garde-le seulement si la suite frappe fort)")]


def check_hook(txt, qui):
    plain = re.sub(r'<[^>]+>', ' ', txt or '').strip().lower()
    for rx, why in HOOK_KO:
        if re.search(rx, plain):
            alerts.append(f'{qui} : hook, {why}')
    for rx, why in HOOK_DOUX:
        if re.search(rx, plain):
            alerts.append(f'{qui} (à vérifier) : hook, {why}')
    first = re.split(r'[.?!]', plain)[0]
    if len(first.split()) > 12:
        alerts.append(f'{qui} : 1re phrase du hook de {len(first.split())} mots (sujet à dire en 1-2 s, Kallaway [2byPP_9F0-Q 01:39])')


def mmss(s):
    try:
        m, sec = (s or '').strip().split(':')[:2]
        return int(m) + int(sec) / 60
    except ValueError:
        return None


def check_long(l, j):
    """Règles R de 02-Formations/experts-scripts-youtube-long.md §9 qu'un script peut vérifier seul."""
    q = f'long {j}'
    nums = [int(x) for x in re.findall(r'\d+', l.get('duree', ''))]
    total = mmss(l.get('total')) or (sum(nums) / len(nums) if nums else 20)
    intro = ' '.join(l.get('intro', []))
    plain = re.sub(r'<[^>]+>', ' ', intro).lower()
    if not re.search(r"\b(mais|sauf que)\b", plain):
        alerts.append(f'{q} : R4, pas de boucle en « mais » / « sauf que » dans les 30 premières secondes')
    preuves = sum(bool(re.search(rx, plain)) for rx in (r'120', r'6 ans', r'ingénieur'))
    if preuves > 1:
        alerts.append(f'{q} : R5, {preuves} preuves de crédibilité dans l\'intro (1 seule)')
    if words(intro) > 110:
        alerts.append(f'{q} : intro de {words(intro)} mots, trop pour 30 s')
    blocs = l.get('blocs', [])
    ts = [mmss(b.get('t')) for b in blocs]
    if any(x is None for x in ts) or ts != sorted(ts):
        alerts.append(f'{q} : temps des blocs manquants ou dans le désordre (format m:ss)')
        return
    rh = sum(1 for b in blocs if b.get('rehook'))
    attendu = max(3, round(total / 5))
    if not attendu <= rh <= attendu + 1:
        alerts.append(f'{q} : R9, {rh} re-hooks pour {round(total)} min (attendu {attendu} à {attendu + 1})')
    pos = []
    for i, b in enumerate(blocs):
        if b.get('cta'):
            fin_bloc = ts[i + 1] if i + 1 < len(ts) else total
            pos.append(round(100 * fin_bloc / total))
    if not 1 <= len(pos) <= 2:
        alerts.append(f'{q} : R12, {len(pos)} CTA dans la vidéo (1 à 2)')
    elif not (30 <= pos[0] <= 45 and (len(pos) == 1 or 85 <= pos[-1] <= 95)):
        alerts.append(f'{q} (à vérifier) : R12, CTA vers {pos} % de la vidéo (repères : 35-40 % et ~90 %)')
    fin = re.sub(r'<[^>]+>', ' ', (l.get('fin') or '') + ' ' + (l.get('ctafinal') or '')).lower()
    if re.search(r"abonne|\blike\b|merci d'avoir|pouce bleu", fin):
        alerts.append(f'{q} : R14, « abonne-toi / like / merci » à la fin')


def nb(s):
    return (s or '').replace(' ?', '&nbsp;?').replace(' !', '&nbsp;!').replace(' :', '&nbsp;:')


def foot(marque, right):
    return f'<div class="foot"><span><b>{marque}</b></span><span>{right}</span></div>'


def cover(lot, courts, marque):
    rows = []
    for i, s in enumerate(courts, 1):
        job, jc = JOB.get(s['kind'], ('', ''))
        rows.append(f"<tr><td class='n'>{i}</td><td>{s.get('jour', '')}</td><td class='f'><img src='{ICON.get(s['kind'], ICON['qa'])}'>{FMT.get(s['kind'], s['kind'])}</td>"
                    f"<td><span class='job {jc}'>{job}</span></td><td>{nb(s.get('sujet', ''))}</td><td class='ck'>{s.get('cta', '')}</td></tr>")
    for j, l in enumerate(lot.get('longs', []), 1):
        rows.append(f"<tr><td class='n'>L{j}</td><td>YouTube</td><td class='f'><img src='{ICON['demo']}'>Audit long · {l.get('duree', '')}</td>"
                    f"<td><span class='job v'>Convertir</span></td><td>{nb(l['titres'][0])}</td><td class='ck'>call</td></tr>")
    avant = ''.join(f'<li>{a}</li>' for a in lot.get('avant', []))
    tip = f"<div class='tip'>{lot['astuce']}</div>" if lot.get('astuce') else ''
    return f"""<section class="page">
  {LOGO}
  <div class="kicker">{lot.get('kicker', '')}</div>
  <h1>{lot.get('h1', '')}</h1>
  <p class="lead">{lot.get('lead', '')}</p>
  <table><tr><th>#</th><th>Jour</th><th>Format</th><th>Job</th><th>Sujet</th><th>CTA</th></tr>
    {''.join(rows)}</table>
  {'<div class="kicker">Avant de tourner</div><ul class="check">' + avant + '</ul>' if avant else ''}
  {tip}
  {foot(marque, lot.get('titre', ''))}
</section>"""


def page_court(s, n, total, marque):
    for k in ('kind', 'screen', 'hook', 'points', 'end', 'ctatext', 'src'):
        if not s.get(k):
            alerts.append(f'court {n} : champ « {k} » vide')
    check_hook(s.get('hook'), f'court {n}')
    corps = re.sub(r'<[^>]+>', ' ', ' '.join(s.get('points', []))).lower()
    if not re.search(r"\b(mais|cependant|sauf que|pourtant)\b", corps):
        alerts.append(f'court {n} (à vérifier) : C6, aucun « mais » dans le corps (tension)')
    if words(s.get('screen')) > 5:
        alerts.append(f"court {n} : texte écran de {words(s['screen'])} mots (5 max)")
    if not 3 <= len(s.get('points', [])) <= 5:
        alerts.append(f"court {n} : {len(s.get('points', []))} points (3 à 5)")
    total_w = words(s.get('hook')) + sum(words(p) for p in s.get('points', [])) + words(s.get('end')) + words(s.get('ctatext'))
    if total_w > 190:
        alerts.append(f'court {n} : {total_w} mots dits, environ {round(total_w / 2.5)} s (trop long pour un reel de 60 s)')
    job, _ = JOB.get(s['kind'], ('', ''))
    pts = ''.join(f'<li>{p}</li>' for p in s.get('points', []))
    warn = f"<div class='warn'>{s['warn']}</div>" if s.get('warn') else ''
    jour = f" · {s['jour']}" if s.get('jour') else ''
    return f"""<section class="page">
  <div class="shead"><div><div class="kicker">Script {n} / {total}{jour}</div>
    <div class="meta"><span class="tag">{FMT.get(s['kind'], s['kind'])}</span><span class="tag">Job : {job.lower()}</span><span class="tag">Pilier {s.get('pilier', '').lower()}</span><span class="tag">CTA {s.get('cta', '')}</span><span class="tag">≈ {round(total_w / 2.5)} s</span></div></div>
    <img src="{ICON.get(s['kind'], ICON['qa'])}" alt=""></div>
  <div class="screen"><small>Texte à l'écran</small>{nb(s.get('screen'))}</div>
  <div class="hookline"><small>Hook</small>{s.get('hook', '')}</div>
  <ol class="pts">{pts}</ol>
  <div class="end">{s.get('end', '')}</div>
  <div class="cta"><b>CTA</b>{s.get('ctatext', '')}</div>
  {warn}
  <div class="src">Sources : {s.get('src', '')}</div>
  {foot(marque, f'Script {n} / {total}')}
</section>"""


def pages_long(l, j, nom_marque):
    for k in ('titres', 'intro', 'blocs', 'ctafinal', 'src'):
        if not l.get(k):
            alerts.append(f'long {j} : champ « {k} » vide')
    check_hook(' '.join(l.get('intro', [])[:1]), f'long {j}')
    check_long(l, j)
    titres = ''.join(f"<li>{t}</li>" for t in l.get('titres', [])[1:])
    intro = ''.join(f'<p>{p}</p>' for p in l.get('intro', []))
    rows = ''.join(f"<tr><td class='t'>{b.get('t', '')}</td><td><b>{b.get('nom', '')}</b><br>{b.get('montre', '')}</td>"
                   f"<td class='rh'>{' · '.join(x for x, k in (('CTA', 'cta'), ('re-hook', 'rehook')) if b.get(k))}</td></tr>" for b in l.get('blocs', []))
    p1 = f"""<section class="page">
  <div class="kicker">Script long {j} · YouTube · {l.get('duree', '')}</div>
  <h2>{l['titres'][0] if l.get('titres') else ''}</h2>
  <p class="alt">Autres titres possibles :</p>
  <ul class="titres">{titres}</ul>
  <p class="thumb"><b>Miniature :</b> {l.get('miniature', '')}</p>
  <div class="intro"><small>Les 30 premières secondes · mot à mot</small>{intro}</div>
  <table class="tl"><tr><th>Temps</th><th>Bloc · ce qu'on voit</th><th>Relance</th></tr>{rows}</table>
  {foot(marque, f'Script long {j} · 1/2')}
</section>"""
    blocs = []
    for b in l.get('blocs', []):
        dit = ''.join(f'<li>{d}</li>' for d in b.get('dit', []))
        rh = f"<div class='rehook'><b>Re-hook</b>{b['rehook']}</div>" if b.get('rehook') else ''
        cta = f"<div class='ctamid'><b>CTA</b>{b['cta']}</div>" if b.get('cta') else ''
        blocs.append(f"<div class='bloc'><div class='bt'><i>{b.get('t', '')}</i>{b.get('nom', '')}</div><ul>{dit}</ul>{cta}{rh}</div>")
    clips = ''.join(f'<li>{c}</li>' for c in l.get('clips', []))
    warn = f"<div class='warn'>{l['warn']}</div>" if l.get('warn') else ''
    par_page = l.get('blocs_par_page', 4)
    lots = [blocs[i:i + par_page] for i in range(0, len(blocs), par_page)] or [[]]
    n_pages = 1 + len(lots)
    out = [p1.replace('1/2', f'1/{n_pages}')]
    for k, lot_b in enumerate(lots, 2):
        last = k == n_pages
        tail = f"""<div class="end">{l.get('fin', '')}</div>
  <div class="cta"><b>CTA final</b>{l.get('ctafinal', '')}</div>
  {'<div class="kicker" style="margin-top:4mm">À découper en reels</div><ul class="clips">' + clips + '</ul>' if clips else ''}
  {warn}
  <div class="src">Sources : {l.get('src', '')}</div>""" if last else ''
        out.append(f"""<section class="page">
  <div class="kicker">Script long {j} · le déroulé ({k - 1}/{len(lots)}) · tu improvises sur les points</div>
  {''.join(lot_b)}
  {tail}
  {foot(marque, f'Script long {j} · {k}/{n_pages}')}
</section>""")
    return out


def main():
    lot = json.loads(pathlib.Path(sys.argv[1]).read_text())
    out = pathlib.Path(sys.argv[2]).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    for f in GAB.glob('*.png'):
        shutil.copy(f, out / f.name)
    global LOGO
    lg = marque.logo()
    if lg:
        shutil.copy(lg, out / ('logo' + lg.suffix))
        LOGO = f'<img class="toplogo" src="logo{lg.suffix}" alt="">'
    m = marque.charger()
    nom_marque = lot.get('marque') or m.get('nom', '').upper()
    courts = lot.get('courts', [])
    pages = [cover(lot, courts, nom_marque)] if (len(courts) + len(lot.get('longs', []))) > 1 else []
    pages += [page_court(s, i, len(courts), nom_marque) for i, s in enumerate(courts, 1)]
    for j, l in enumerate(lot.get('longs', []), 1):
        pages += pages_long(l, j, nom_marque)
    html = (GAB / 'page.html').read_text().replace('%%TITLE%%', lot.get('titre', 'Scripts')).replace('%%PAGES%%', '\n\n'.join(pages)).replace('%%FONTS%%', marque.lien_polices()).replace('%%MARQUE%%', marque.css_vars(DA))
    (out / 'scripts.html').write_text(html)

    pdf = out / f"{lot.get('nom', 'Scripts')}.pdf"
    # Chrome se bloque parfois au démarrage : marque.chrome_run le tue et réessaie (profil neuf)
    marque.chrome_run(['--no-pdf-header-footer', f'--print-to-pdf={pdf}', (out / 'scripts.html').as_uri()])
    dom = marque.chrome_run(['--window-size=794,1123', '--dump-dom', (out / 'scripts.html').as_uri()])
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
    for i, p in enumerate(doc, 1):
        p.get_pixmap(dpi=70).save(out / 'pages' / f'page-{i}.png')
        if not p.get_text().strip():
            alerts.append(f'page {i} vide')
    if len(doc) != len(pages):
        alerts.append(f'{len(doc)} pages dans le PDF pour {len(pages)} prévues : un bloc déborde')
    print(f'ok : {pdf} ({len(doc)} pages)')
    for a in alerts:
        print('ALERTE', a)


if __name__ == '__main__':
    main()
