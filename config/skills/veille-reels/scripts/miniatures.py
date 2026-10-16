"""Page de miniatures d'une veille : lit le tableau de la copie Brain (.md), récupère la couverture
de chaque reel à partir de son code (balise og:image, 0 crédit) et écrit 1 page HTML autonome,
aux couleurs, polices et nom de ~/Documents/Brain/00-Moi/marque.json (via marque.py).
Usage : python3 -I miniatures.py <veille.md> <sortie.html>
Stdlib seulement (python3 -I ne voit pas Pillow). Pas de Chrome nécessaire."""
import base64, html, pathlib, re, sys, time, unicodedata, urllib.request
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, str(pathlib.Path.home() / "Documents" / "Brain" / "_outils"))
import marque  # couleurs, polices, nom de l'utilisateur

UA = "facebookexternalhit/1.1"  # Instagram ne sert og:image qu'aux robots de partage
DA = {"--bleu": "principale", "--marine": "foncee", "--gris": "doux", "--fond": "clair", "--ligne": "ligne", "--teinte": "teinte"}


def norm(s):
    return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower().strip()


def lire_tableau(md):
    lignes = [l for l in md.splitlines()]
    for i, l in enumerate(lignes):
        if l.startswith("|") and "lien" in norm(l) and "createur" in norm(l):
            tete = [norm(c) for c in l.strip().strip("|").split("|")]
            rows = []
            for r in lignes[i + 2:]:
                if not r.startswith("|"):
                    break
                cells = [c.strip() for c in r.strip().strip("|").split("|")]
                rows.append(dict(zip(tete, cells)))
            return rows
    sys.exit("Aucun tableau avec les colonnes Créateur + Lien dans le .md")


def col(row, *noms):
    for k, v in row.items():
        if any(k.startswith(n) for n in noms):
            return v
    return ""


def court(nb):
    n = int(re.sub(r"\D", "", nb) or 0)
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f} M".replace(".", ",").replace(",0 M", " M")
    if n >= 1_000:
        return f"{round(n / 1_000)} k"
    return str(n) if n else ""


def get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def miniature(code):
    for essai in range(2):
        for kind in ("reel", "p"):
            try:
                page = get(f"https://www.instagram.com/{kind}/{code}/").decode("utf-8", "ignore")
                m = re.search(r'property="og:image" content="([^"]+)"', page)
                if not m:
                    continue
                img = get(html.unescape(m.group(1)))
                if img[:3] == b"\xff\xd8\xff":
                    return "data:image/jpeg;base64," + base64.b64encode(img).decode()
            except Exception:
                pass
        time.sleep(2)
    return None


def carte(r, img):
    code = r["code"]
    lien = f"https://www.instagram.com/reel/{code}/"
    visuel = (f'<img src="{img}" alt="" loading="lazy">' if img
              else '<div class="vide">aperçu<br>indisponible</div>')
    cible = col(r, "cible")
    stats = " · ".join(x for x in (f"♥ {court(col(r, 'likes'))}" if col(r, "likes") else "",
                                    f"▶ {court(col(r, 'vues'))}" if col(r, "vues") else "") if x)
    return f"""<article>
  <a class="vignette" href="{lien}" target="_blank" rel="noopener">{visuel}
    <span class="num">{html.escape(col(r, '#') or '')}</span>
    <span class="marche">{html.escape(col(r, 'marche'))}</span>
    <span class="stats">{stats}</span>
  </a>
  <div class="infos">
    <a class="createur" href="{lien}" target="_blank" rel="noopener">{html.escape(col(r, 'createur'))}</a>
    <div class="tags"><span class="format">{html.escape(col(r, 'format'))}</span><span>{html.escape(cible)}</span></div>
    <p>{html.escape(col(r, 'hook'))}</p>
  </div>
</article>"""


def main(src, out):
    md = open(src, encoding="utf-8").read()
    titre = next((l[2:].strip() for l in md.splitlines() if l.startswith("# ")), "Veille reels")
    rows = []
    for r in lire_tableau(md):
        m = re.search(r"instagram\.com/(?:reel|p)/([A-Za-z0-9_-]+)", col(r, "lien"))
        if m:
            r["code"] = m.group(1)
            rows.append(r)
    if not rows:
        sys.exit("Aucun lien de reel Instagram dans le tableau (colonne Lien)")
    with ThreadPoolExecutor(4) as ex:
        imgs = list(ex.map(miniature, [r["code"] for r in rows]))
    cartes = "\n".join(carte(r, i) for r, i in zip(rows, imgs))
    nom = marque.charger().get("nom", "")
    entete = f'<div class="marque">{html.escape(nom.upper())}</div>' if nom else ""
    page = f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(titre)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
{marque.lien_polices()}
<style>
:root{{--bleu:#2563EB;--marine:#111827;--gris:#6B7280;--fond:#fff;--ligne:#E5E7EB;--teinte:#EFF4FF}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--fond);color:var(--marine);font:15px/1.4 var(--police-texte),system-ui,sans-serif;padding:28px 16px 48px}}
header{{max-width:1240px;margin:0 auto 22px}}
.marque{{font:800 13px var(--police-titre),sans-serif;letter-spacing:.14em;color:var(--bleu)}}
h1{{font:800 clamp(20px,3vw,28px)/1.15 var(--police-titre),sans-serif;margin:6px 0 4px}}
header p{{margin:0;color:var(--gris);font-size:13px}}
main{{max-width:1240px;margin:0 auto;display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:18px}}
article{{border:1px solid var(--ligne);border-radius:14px;overflow:hidden;background:#fff}}
.vignette{{position:relative;display:block;aspect-ratio:9/16;background:var(--teinte)}}
.vignette img{{width:100%;height:100%;object-fit:cover;display:block}}
.vide{{height:100%;display:grid;place-items:center;text-align:center;color:var(--gris);font-size:13px}}
.vignette:hover img{{opacity:.88}}
.num{{position:absolute;top:8px;left:8px;background:var(--bleu);color:#fff;font:800 14px var(--police-titre),sans-serif;min-width:28px;height:28px;border-radius:14px;display:grid;place-items:center;padding:0 8px}}
.marche{{position:absolute;top:8px;right:8px;background:var(--marine);color:#fff;font:700 11px var(--police-texte),sans-serif;padding:5px 8px;border-radius:8px;letter-spacing:.06em}}
.stats{{position:absolute;left:0;right:0;bottom:0;padding:26px 10px 9px;color:#fff;font:600 13px var(--police-texte),sans-serif;background:linear-gradient(transparent,rgba(10,20,35,.82))}}
.infos{{padding:10px 12px 12px}}
.createur{{font-weight:600;color:var(--bleu);text-decoration:none;word-break:break-all}}
.tags{{display:flex;gap:6px;align-items:center;margin:6px 0;font-size:12px}}
.format{{background:var(--teinte);color:var(--bleu);padding:3px 8px;border-radius:6px;font-weight:600}}
.infos p{{margin:0;font-size:13px;color:var(--marine);display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}}
@media (max-width:480px){{main{{grid-template-columns:1fr 1fr;gap:10px}} .infos p{{font-size:12px}}}}
</style>
{marque.css_vars(DA)}
</head><body>
<header>{entete}<h1>{html.escape(titre)}</h1>
<p>Clique sur une miniature pour ouvrir le reel. Chiffres vérifiés.</p></header>
<main>
{cartes}
</main></body></html>"""
    open(out, "w", encoding="utf-8").write(page)
    ok = sum(1 for i in imgs if i)
    manque = [r["code"] for r, i in zip(rows, imgs) if not i]
    print(f"{ok}/{len(rows)} miniatures OK" + (f" · sans aperçu : {', '.join(manque)}" if manque else "") + f" -> {out}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
