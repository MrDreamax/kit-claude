"""Fabrique un deck de slides 1920x1080 à tes couleurs et à tes polices (~/Documents/Brain/00-Moi/marque.json).
  python3 slides.py <plan.json>
Le plan : voir ../exemples/youtube-audit-bio.json et ../exemples/webinaire-test.json. Deux formats :
  youtube   : police de titres en majuscules + police d'accent italique (Instrument Serif par défaut) pour le mot fort
  webinaire : police de titres + police de texte, une couleur d'achat seulement pour le bouton (jaune par défaut)
Types de slide : attente, phrase, section, correction, liste (révélée point par point), methode, capture, cloture.
Sort dans "out" (défaut ~/Documents/Contenu/slides/AAAA-MM-JJ-<titre>) : deck.html (à présenter en plein écran), PNG 1920x1080
numérotés, deck.pdf, planche.png. Besoin de Google Chrome et de Pillow seulement.
Imprime les alertes de la checklist (02-Formations/experts-slides-webinaire-youtube.md) et les textes qui débordent.
Couleurs de marque.json : principale (accent), foncee (titres, fonds de partie), clair (fond), doux (petits textes), ligne.
Réglages facultatifs de marque.json : couleurs.bouton (bouton d'achat, jaune par défaut), polices.accent (police italique du format youtube).
"""
import concurrent.futures
import datetime
import html
import json
import math
import os
import pathlib
import random
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(SKILL, "assets")
FONTS = os.path.join(ASSETS, "fonts")
sys.path.insert(0, str(pathlib.Path.home() / "Documents" / "Brain" / "_outils"))
import marque  # noqa: E402

M = marque.charger()
C, POL = M["couleurs"], M["polices"]
CARD_W, CARD_HMAX = 760, 780

# polices fournies avec le skill (licence libre OFL) : marchent sans Internet. Les autres viennent de Google Fonts.
LOCALES = {
    "Montserrat": ("Montserrat.ttf", "", "font-weight:100 900"),
    "Archivo": ("Archivo-latin.woff2", "woff2", "font-weight:100 900"),
    "Inter": ("Inter-latin.woff2", "woff2", "font-weight:100 900"),
    "Instrument Serif": ("InstrumentSerif-Italic.ttf", "", "font-style:italic"),
}

alerts = []


# ---------- couleurs ----------
def _rgb(h):
    return [int(h.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]


def mix(a, b, t):
    ra, rb = _rgb(a), _rgb(b)
    return "#%02X%02X%02X" % tuple(round(ra[i] * (1 - t) + rb[i] * t) for i in range(3))


def lum(h):
    def f(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (f(x) for x in _rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def rgba(h, a):
    r, g, b = _rgb(h)
    return f"rgba({r},{g},{b},{a})"


BLEU, MARINE, CLAIR_FOND = C["principale"], C["foncee"], C["clair"]
BOUTON = C.get("bouton") or "#FFD43B"
ENCRE_CLAIRE = mix(BLEU, "#FFFFFF", 0.35)  # le trait sur une capture sombre
ACCENT = POL.get("accent") or "Instrument Serif"


def vars_css():
    v = {"bleu": BLEU, "marine": MARINE, "clair": CLAIR_FOND, "gris": C["doux"], "gris2": mix(C["doux"], CLAIR_FOND, 0.35),
         "ciel": mix(BLEU, "#FFFFFF", 0.5), "ligne": C["ligne"], "doux-fonce": mix(C["doux"], MARINE, 0.4),
         "bouton": BOUTON, "bouton-ombre": mix(BOUTON, "#000000", 0.2), "bouton-texte": MARINE if lum(BOUTON) > 0.35 else CLAIR_FOND,
         "bord": rgba(MARINE, 0.1), "ombre": rgba(MARINE, 0.25)}
    css = ";".join(f"--{k}:{x}" for k, x in v.items())
    return f":root{{{css};--ftitre:'{POL['titre']}';--ftexte:'{POL['texte']}';--faccent:'{ACCENT}'}}"


def fonts_head(theme, build):
    """@font-face pour les polices fournies, lien Google Fonts pour les autres. Copie les fichiers dans build/fonts."""
    utiles = [POL["titre"], ACCENT] if theme == "youtube" else [POL["titre"], POL["texte"]]
    faces, google = [], []
    for fam in dict.fromkeys(utiles):
        if fam in LOCALES:
            fichier, fmt, extra = LOCALES[fam]
            shutil.copy(os.path.join(FONTS, fichier), os.path.join(build, "fonts", fichier))
            f = f' format("{fmt}")' if fmt else ""
            faces.append(f'@font-face{{font-family:"{fam}";src:url(fonts/{fichier}){f};{extra}}}')
        else:
            google.append(fam)
    link = ""
    if google:
        q = "&".join("family=" + urllib.parse.quote_plus(f) + ":ital,wght@0,400;0,600;0,700;0,800;0,900" for f in google)
        link = f'<link href="https://fonts.googleapis.com/css2?{q}&display=swap" rel="stylesheet">'
    return "\n".join(faces), link, google


# ---------- aides ----------
def warn(n, msg):
    alerts.append(f"slide {n:02d} · {msg}")


def esc(s):
    return html.escape(str(s or ""))


def words(*parts):
    return sum(len(re.findall(r"[\wÀ-ÿ'’]+", p or "")) for p in parts)


def kick(s):
    return f'<div class="kick">{esc(s)}</div>' if s else ""


def lines_ab(d, cls="ab"):
    a = "<br>".join(esc(x) for x in str(d.get("a", "")).split("\n")) if d.get("a") else ""
    out = f'<div class="{cls}">'
    if a:
        out += f'<div class="a">{a}</div>'
    if d.get("b"):
        out += f'<div class="b">{esc(d["b"])}</div>'
    if d.get("c"):
        out += f'<div class="c">{esc(d["c"])}</div>'
    return out + "</div>"


# ---------- types ----------
def s_attente(d, n):
    return "attente", f'{kick(d.get("kicker"))}<div class="inner center">{lines_ab(d)}</div>'


def s_phrase(d, n):
    if words(d.get("a"), d.get("b"), d.get("c")) > 12:
        warn(n, f"phrase de {words(d.get('a'), d.get('b'), d.get('c'))} mots (règle 2 : un mot, une phrase, 12 max)")
    return "phrase", f'{kick(d.get("kicker"))}<div class="inner center">{lines_ab(d)}</div>'


def s_section(d, n):
    if words(d.get("a"), d.get("b")) > 8:
        warn(n, "titre de partie trop long (8 mots max)")
    return "section", f'{kick(d.get("kicker"))}<div class="inner center">{lines_ab(d)}</div>'


def s_correction(d, n):
    if not d.get("avant"):
        warn(n, "correction sans « avant »")
    return "correction", (f'{kick(d.get("kicker"))}<div class="inner center"><div class="avant"><span>{esc(d.get("avant"))}</span></div>'
                          f'<svg class="fleche" width="40" height="100" viewBox="0 0 40 100"><path d="M20 4 V 88 M6 74 L20 92 L34 74"/></svg>'
                          f'{lines_ab(d)}</div>')


def s_liste(d, n, step):
    items = d.get("items", [])
    if len(items) > 6:
        warn(n, f"{len(items)} points : coupe en 2 slides (règle 3 : peu d'éléments)")
    for it in items:
        if words(it) > 8:
            warn(n, f"point trop long : « {it[:40]}… » (8 mots max)")
    li = ""
    for i, it in enumerate(items):
        st = "done" if step is not None and i < step else ("cur" if step is None or i == step else "todo")
        li += f'<li class="{st}"><span class="num">{i + 1}</span><span class="txt">{esc(it)}</span></li>'
    titre = f'<div class="ltitre">{esc(d["titre"])}</div>' if d.get("titre") else ""
    return "liste", f'{kick(d.get("kicker"))}<div class="inner">{titre}<ol>{li}</ol></div>'


def s_methode(d, n):
    et, cur = d.get("etapes", []), int(d.get("actuelle", 1))
    if not 2 <= len(et) <= 4:
        warn(n, "méthode : 3 étapes idéalement (2 à 4)")
    ok = '<span class="ok"><svg width="26" height="26" viewBox="0 0 26 26"><path d="M5 13.5 L10.5 19 L21 7"/></svg></span>'
    parts = []
    for i, e in enumerate(et, 1):
        if i < cur:
            parts.append(f'<div class="step done"><div class="n">{i}</div><div class="t">{ok}{esc(e)}</div></div>')
        elif i == cur:
            parts.append(f'<div class="step cur"><div class="n">{i}</div><div class="t">{esc(e)}</div><div class="bar"></div></div>')
        else:
            parts.append(f'<div class="step next"><div class="n">{i}</div><div class="t">{esc(e)}</div></div>')
    return "methode", f'{kick(d.get("kicker", "La méthode"))}<div class="inner row">{"<div class=line></div>".join(parts)}</div>'


def ellipse_path(cx, cy, rx, ry, seed):
    rnd = random.Random(seed)
    tilt = math.radians(rnd.uniform(-2.5, 1.5))
    a0 = math.radians(195)
    pts = []
    for k in range(96):
        t = a0 - 2 * math.pi * (k / 95) * 1.07  # un tour + 7 % : le trait déborde comme à la main
        r = 1 + 0.035 * math.sin(3 * t + seed) + (0.05 if k > 88 else 0)
        x, y = rx * r * math.cos(t), ry * r * math.sin(t)
        pts.append((cx + x * math.cos(tilt) - y * math.sin(tilt), cy + x * math.sin(tilt) + y * math.cos(tilt)))
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)


def s_capture(d, n, theme, build):
    from PIL import Image
    src = os.path.expanduser(d.get("image", ""))
    if not os.path.isfile(src):
        warn(n, f"image introuvable : {src}")
        return "capture", f'{kick(d.get("kicker"))}<div class="inner center">{lines_ab(d)}</div>'
    if not d.get("source"):
        warn(n, "capture sans source (règle 20 : la source en petit sous l'image)")
    name = f"img/{n:02d}{os.path.splitext(src)[1].lower()}"
    cercle = list(d["cercle"]) if d.get("cercle") else None
    im = Image.open(src)
    if d.get("recadrage"):  # [x, y, l, h] en px de l'image d'origine ; le cercle reste en coordonnées d'origine
        x0, y0, cw, ch = d["recadrage"]
        name = f"img/{n:02d}.png"
        im.crop((x0, y0, x0 + cw, y0 + ch)).save(os.path.join(build, name))
        iw, ih = cw, ch
        if cercle:
            cercle[0] -= x0
            cercle[1] -= y0
    else:
        shutil.copy(src, os.path.join(build, name))
        iw, ih = im.size
    seul = not d.get("a")
    maxw, maxh = (1500, 690) if seul else (CARD_W, CARD_HMAX)
    dw = maxw
    dh = dw * ih / iw
    if dh > maxh:
        dh, dw = maxh, maxh * iw / ih
    s = iw / dw  # px image par px écran
    svg = ""
    if cercle:
        x, y, w, h = cercle
        pad = max(h * 0.42, 14 * s)
        cx, cy, rx, ry = x + w / 2, y + h / 2, min(w / 2 + pad * 0.9, x + w / 2 - 8 * s), h / 2 + pad
        col = ENCRE_CLAIRE if d.get("encre") == "clair" else BLEU
        dim = ""
        if d.get("assombrir", True):
            dim = (f'<mask id="m{n}"><rect width="{iw}" height="{ih}" fill="#fff"/>'
                   f'<rect x="{cx - rx}" y="{cy - ry}" width="{2 * rx}" height="{2 * ry}" rx="{ry}" fill="#000"/></mask>'
                   f'<rect width="{iw}" height="{ih}" fill="rgba(10,10,11,.55)" mask="url(#m{n})"/>')
        note = ""
        if d.get("note"):
            fs = 58 * s
            nw = len(d["note"]) * fs * 0.42
            if iw - (cx + rx) > nw + 20 * s:
                nx, ny = cx + rx + 14 * s, cy + fs * 0.33
            elif cy + ry + fs * 1.2 < ih:
                nx, ny = max(cx - rx, 10 * s), cy + ry + fs * 1.05
            else:
                nx, ny = max(cx - rx, 10 * s), cy - ry - fs * 0.35
            note = f'<text class="note" x="{nx:.0f}" y="{ny:.0f}" font-size="{fs:.0f}" fill="{col}">{esc(d["note"])}</text>'
        svg = (f'<svg class="ink" viewBox="0 0 {iw} {ih}" preserveAspectRatio="none">{dim}'
               f'<path d="{ellipse_path(cx, cy, rx, ry, n)}" fill="none" stroke="{col}" stroke-width="{6.5 * s:.1f}" '
               f'stroke-linecap="round" stroke-linejoin="round"/>{note}</svg>')
    card = (f'<div class="card" style="width:{dw:.0f}px;height:{dh:.0f}px"><img src="{name}">{svg}</div>'
            f'<div class="src">{esc(d.get("source"))}</div>')
    if seul:
        return "capture seul", f'{kick(d.get("kicker"))}<div class="inner center"><div class="cardwrap">{card}</div></div>'
    tw = 1920 - 300 - dw - 90
    return "capture", (f'{kick(d.get("kicker"))}<div class="inner capt"><div class="texte" style="width:{tw:.0f}px">{lines_ab(d)}</div>'
                       f'<div class="cardwrap" style="width:{dw:.0f}px">{card}</div></div>')


def montant(v, devise):
    return f"{int(v):,}".replace(",", " ") + " " + devise if isinstance(v, (int, float)) else esc(v)


def s_cloture(d, n):
    items = d.get("items", [])
    devise = d.get("devise", "€")
    total = d.get("total") or sum(v for _, v in items if isinstance(v, (int, float)))
    prix = d.get("prix")
    if not isinstance(prix, (int, float)) or not total or total <= prix:
        warn(n, "clôture : la valeur totale doit être PLUS GROSSE que le prix (règle 12)")
    if d.get("demo"):
        warn(n, "clôture : valeurs de DÉMO, à faire fixer par toi (ou le skill `offre` s'il est installé) avant diffusion")
    if not d.get("lien"):
        warn(n, "clôture sans lien")
    it = "".join(f'<div class="it">{esc(l)} <b>{montant(v, devise)}</b></div>' for l, v in items)
    cd = ""
    if d.get("compte_a_rebours"):
        cd = (f'<div class="cd"><div class="l">{esc(d.get("compte_label", "L’offre ferme dans"))}</div>'
              f'<div class="t">{esc(d["compte_a_rebours"])}</div><div class="u"><span>min</span><span>sec</span></div></div>')
    else:
        warn(n, "clôture sans compte à rebours (règle 12 : l'info la plus visible)")
    return "cloture", (f'{kick(d.get("kicker"))}<div class="inner clo"><div class="stack">{it}'
                       f'<div class="tot"><span class="l">Valeur totale</span><span class="v">{montant(total, devise)}</span></div>'
                       f'<div class="prix"><span>{esc(d.get("prix_label", "Aujourd’hui"))}</span><span>{montant(prix, devise)}</span></div></div>'
                       f'<div class="right">{cd}<div class="btn">{esc(d.get("bouton", "Je réserve →"))}</div>'
                       f'<div class="link">{esc(d.get("lien"))}</div></div></div>')


def build_slides(plan, build):
    theme = plan.get("format", "youtube")
    out, n = [], 0
    for d in plan["slides"]:
        t = d.get("type")
        if t == "liste" and d.get("revele", True) and len(d.get("items", [])) > 1:
            for step in range(len(d["items"])):
                n += 1
                out.append(s_liste(d, n, step))
            continue
        n += 1
        if t == "liste":
            out.append(s_liste(d, n, None))
        elif t == "capture":
            out.append(s_capture(d, n, theme, build))
        elif t in ("attente", "phrase", "section", "correction", "methode", "cloture"):
            out.append(globals()["s_" + t](d, n))
        else:
            warn(n, f"type inconnu « {t} », slide ignorée")
            n -= 1
    return theme, out


# ---------- Chrome ----------
def chrome(user_dir, extra):
    return [marque.chrome(), "--headless=new", "--use-mock-keychain", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files", "--use-mock-keychain",
            "--force-device-scale-factor=1", f"--user-data-dir={user_dir}", "--virtual-time-budget=10000"] + extra


def rendre(build, nb):
    """Rapport de mesure (--dump-dom), un PNG par slide (en parallèle), puis le PDF. Renvoie les notes du rapport."""
    url = pathlib.Path(build, "deck.html").as_uri()
    os.makedirs(os.path.join(build, "png"), exist_ok=True)
    dom = subprocess.run(chrome(os.path.join(build, "chrome-r"), ["--dump-dom", url + "?report=1"]), capture_output=True, text=True, timeout=300).stdout
    rapport = None
    m = re.search(r'<pre id="rapport">(.*?)</pre>', dom, re.S)
    if m:
        rapport = json.loads(html.unescape(m.group(1)))

    def shoot(i):
        subprocess.run(chrome(os.path.join(build, f"chrome-{i}"), ["--window-size=1920,1080", f"--screenshot={build}/png/{i:02d}.png", f"{url}?shot=1&s={i}"]),
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        list(ex.map(shoot, range(1, nb + 1)))
    subprocess.run(chrome(os.path.join(build, "chrome-pdf"), ["--no-pdf-header-footer", f"--print-to-pdf={build}/deck.pdf", url + "?print=1"]),
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300)
    return rapport


def planche(build, nb):
    from PIL import Image
    cols, tw = (6, 320) if nb > 24 else (4, 480)
    th, g = tw * 9 // 16, 12
    rows = math.ceil(nb / cols)
    sheet = Image.new("RGB", (cols * tw + (cols + 1) * g, rows * th + (rows + 1) * g), "#8a8a8a")
    for i in range(nb):
        im = Image.open(os.path.join(build, "png", f"{i + 1:02d}.png")).convert("RGB").resize((tw, th), Image.LANCZOS)
        sheet.paste(im, (g + (i % cols) * (tw + g), g + (i // cols) * (th + g)))
    sheet.save(os.path.join(build, "planche.png"))


def main():
    plan = json.load(open(sys.argv[1], encoding="utf-8"))
    slug = re.sub(r"[^a-z0-9]+", "-", plan.get("titre", "slides").lower()).strip("-") or "slides"
    out = os.path.expanduser(plan.get("out") or f"~/Documents/Contenu/slides/{datetime.date.today():%Y-%m-%d}-{slug}")
    build = tempfile.mkdtemp(prefix="slides-")
    try:
        os.makedirs(os.path.join(build, "img"))
        os.makedirs(os.path.join(build, "fonts"))
        theme, slides = build_slides(plan, build)
        faces, link, google = fonts_head(theme, build)
        tpl = open(os.path.join(ASSETS, "deck.html"), encoding="utf-8").read()
        body = "\n".join(f'<section class="slide {cls}">{h}</section>' for cls, h in slides)
        deck = (tpl.replace("{{THEME}}", "yt" if theme == "youtube" else "web").replace("{{TITRE}}", esc(plan.get("titre", "Slides")))
                .replace("{{FONTFACES}}", faces).replace("{{FONTLINK}}", link).replace("{{VARS}}", vars_css()).replace("{{SLIDES}}", body))
        open(os.path.join(build, "deck.html"), "w", encoding="utf-8").write(deck)
        nb = len(slides)
        rapport = rendre(build, nb)
        if rapport:
            for r in rapport["slides"]:
                if r["over"]:
                    alerts.append(f"slide {r['n']:02d} · DÉBORDE : le texte sort de la slide même réduit, coupe le texte")
                elif r["k"] < 0.85:
                    alerts.append(f"slide {r['n']:02d} · TEXTE RÉDUIT à {round(r['k'] * 100)} % pour tenir : trop de mots ?")
            for f in rapport.get("polices_manquantes", []):
                alerts.append(f"POLICE « {f} » non chargée (Internet coupé ou nom inconnu de Google Fonts) : les slides utilisent une police de secours")
        else:
            alerts.append("contrôles de débordement impossibles : Chrome n'a pas rendu de rapport")
        from PIL import Image
        for i in range(1, nb + 1):
            sz = Image.open(os.path.join(build, "png", f"{i:02d}.png")).size
            if sz != (1920, 1080):
                alerts.append(f"png/{i:02d}.png : taille {sz[0]}x{sz[1]} au lieu de 1920x1080")
        planche(build, nb)
        os.makedirs(out, exist_ok=True)
        for f in ("deck.html", "deck.pdf", "planche.png"):
            if os.path.exists(os.path.join(build, f)):
                shutil.copy(os.path.join(build, f), out)
        for sub in ("fonts", "img", "png"):
            if os.path.isdir(os.path.join(build, sub)):
                shutil.copytree(os.path.join(build, sub), os.path.join(out, sub), dirs_exist_ok=True)
    finally:
        shutil.rmtree(build, ignore_errors=True)
    json.dump(plan, open(os.path.join(out, "plan.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    if theme == "webinaire" and plan.get("duree_min"):
        cible = plan["duree_min"] * 2.5
        if nb < cible:
            alerts.append(f"deck · {nb} slides pour {plan['duree_min']} min : les praticiens en font 150 à 250 par heure (règle 4, hypothèse)")
    print(f"{nb} slides -> {out}")
    print("\n".join(["ALERTES :"] + alerts) if alerts else "0 alerte")


if __name__ == "__main__":
    main()
