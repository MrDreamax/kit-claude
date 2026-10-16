#!/usr/bin/env python3
"""Fiches de publication à valider par l'utilisateur.
  fiche.py fiche fiche.json --out fiche.png        -> la fiche détaillée d'un reel
  fiche.py semaine f1.json f2.json ... --out semaine.png  -> la semaine sur une page (1 ligne par reel)
Chaque fiche.json est dans le dossier du reel, à côté de cover.png / cover_480.jpg / grille.jpg (sortis par cover.py).
"""
import argparse, html, json, os, re, sys
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _rendu import rendre, marque_html
from controle import controler

JOURS = ["Lun.", "Mar.", "Mer.", "Jeu.", "Ven.", "Sam.", "Dim."]
# Couleurs et polices de la marque (marque.json) : variables --foncee, --principale, --teinte, --ligne, --doux, --police-titre…
CSS = """:root{--navy:var(--foncee);--blue:var(--principale);--tint:var(--teinte);--line:var(--ligne);--mute:var(--doux);--ok:#1D8A5B;--warn:#C98A12;--ko:#C0392B}
*{box-sizing:border-box}
body{margin:0;width:1080px;background:#fff;font-family:var(--police-texte),-apple-system,"Helvetica Neue",Arial,sans-serif;color:#0E1621;font-size:34px;line-height:1.45}
.wrap{padding:64px 60px 70px}
.tag{font-family:var(--police-titre),sans-serif;font-weight:800;font-size:24px;letter-spacing:.22em;color:var(--blue);text-transform:uppercase}
h1{font-family:var(--police-titre),sans-serif;font-weight:900;font-size:62px;line-height:1.05;color:var(--navy);margin:14px 0 10px;letter-spacing:-1px}
.when{display:inline-block;background:var(--navy);color:#fff;border-radius:16px;padding:12px 24px;font-weight:700;font-size:32px;margin-top:8px}
.top{display:flex;gap:36px;margin:44px 0 40px;align-items:flex-start}
.phone{width:420px;border-radius:44px;overflow:hidden;border:10px solid #0E1621;flex:none}
.phone img{display:block;width:100%}
.side{flex:1}
h3{font-family:var(--police-titre),sans-serif;font-weight:800;font-size:30px;color:var(--navy);margin:0 0 12px;letter-spacing:.02em;text-transform:uppercase}
.grid{width:240px;border-radius:10px;display:block;margin-bottom:28px;border:1px solid var(--line)}
.pill{display:inline-block;background:var(--tint);color:var(--navy);border-radius:999px;padding:8px 20px;font-size:28px;font-weight:600;margin:0 8px 10px 0}
.card{border:2px solid var(--line);border-radius:28px;padding:34px 38px;margin-bottom:28px}
.card.ig{border-color:var(--blue)}
.cap{white-space:pre-line;font-size:34px}
.lab{font-size:24px;font-weight:700;color:var(--mute);text-transform:uppercase;letter-spacing:.12em;margin:26px 0 6px}
.small{font-size:30px;color:#2b3442;white-space:pre-line}
.chk{list-style:none;padding:0;margin:0}
.chk li{padding:10px 0 10px 58px;position:relative;border-bottom:1px solid var(--line);font-size:31px}
.chk li:last-child{border:0}
.chk li:before{content:"✓";position:absolute;left:4px;top:8px;width:40px;height:40px;border-radius:50%;background:var(--ok);color:#fff;font-weight:800;font-size:26px;display:flex;align-items:center;justify-content:center}
.chk li.alerte:before{content:"!";background:var(--warn)}
.chk li.bloque:before{content:"✗";background:var(--ko)}
.block{background:var(--navy);color:#fff;border-radius:28px;padding:34px 38px;margin-top:8px}
.block b{color:#8CC8F0}
.row{display:flex;gap:30px;align-items:center;border-bottom:2px solid var(--line);padding:26px 0}
.row img{width:170px;border-radius:18px;flex:none}
.row .d{font-family:var(--police-titre),sans-serif;font-weight:800;color:var(--blue);font-size:26px;letter-spacing:.06em;text-transform:uppercase}
.row .t{font-family:var(--police-titre),sans-serif;font-weight:800;color:var(--navy);font-size:36px;line-height:1.15;margin:6px 0}
.row .l{font-size:27px;color:#2b3442}
.row .s{font-size:25px;font-weight:700;margin-top:6px}"""


def e(t):
    """Échappe et met une espace insécable avant ? ! : (typo française, pas de « ? » orphelin)."""
    t = html.escape(t or "")
    for p in ("?", "!", ":"):
        t = t.replace(" " + p, "&nbsp;" + p)
    # mots d'1 ou 2 lettres collés au mot suivant : pas de « S à » / « D. » seul en fin de ligne
    return re.sub(r"(?<=[ (])(\w{1,2}) (?=\S)", r"\1&nbsp;", t)


def quand(f):
    d = datetime.fromisoformat(f["date"])
    return f"{JOURS[d.weekday()]} {d:%d/%m} · {d:%H}h{d:%M}"


def fiche(f, dossier, sortie, statut=""):
    ig, yt, tk = f.get("instagram", {}), f.get("youtube", {}), f.get("tiktok", {})
    plats = f.get("plateformes", ["instagram", "facebook", "youtube", "tiktok"])
    pills = [f"Reel {'trial' if ig.get('type') == 'TRIAL_REEL' else 'normal'}",
             "Trial" if ig.get("type") == "TRIAL_REEL" else "Pas de trial",
             f"{round(f.get('duree', 0))} s",
             "Cover = ton B-roll" if f.get("cover", {}).get("source") == "broll" else "Cover"]
    # Les contrôles qui passent et qui comptent peu sont regroupés en 1 ligne (pas de pavé)
    secondaires = ("Vidéo trouvée", "Légende sous", "1er commentaire prêt", "Texte alternatif rempli", "Titre YouTube sous",
                   "Légende TikTok prête", "Date dans le futur")
    lignes, regroupes = [], 0
    for n, t in controler(f):
        if n == "ok" and t.startswith(secondaires):
            regroupes += 1
        else:
            lignes.append((n, t))
    if regroupes:
        lignes.append(("ok", "Longueurs, 1er commentaire, texte alternatif et date : OK"))
    checks = "".join(f'<li class="{n}">{e(t)}</li>' for n, t in lignes)
    bloc = f.get("bloc", "")
    p = f"""<!doctype html><html><head><meta charset="utf-8">{marque_html()}<style>{CSS}</style></head><body><div class="wrap">
<div class="tag">Publication{(' · ' + e(statut)) if statut else ''}</div>
<h1>{e(f['titre'])}</h1>
<div class="when">{quand(f)} · {len(plats)} plateforme{'s' if len(plats) > 1 else ''}</div>
<div class="top"><div class="phone"><img src="cover_480.jpg"></div><div class="side">
<h3>Sur ta grille</h3><img class="grid" src="grille.jpg"><h3>Réglages</h3>
{''.join(f'<span class="pill">{e(x)}</span>' for x in pills)}</div></div>
<div class="card ig"><h3>Instagram{' · Facebook' if 'facebook' in plats else ''}</h3><div class="cap">{e(ig.get('legende'))}</div>
<div class="lab">1er commentaire (posté par toi)</div><div class="small">{e(ig.get('premier_commentaire'))}</div>
<div class="lab">Texte alternatif</div><div class="small">{e(ig.get('alt'))}</div></div>
{f'''<div class="card"><h3>YouTube Shorts</h3><div class="lab" style="margin-top:0">Titre</div><div class="small">{e(yt.get('titre'))}</div>
<div class="lab">Description</div><div class="small">{e(yt.get('description'))}</div></div>''' if 'youtube' in plats else ''}
{f'''<div class="card"><h3>TikTok</h3><div class="small">{e(tk.get('legende'))}</div></div>''' if 'tiktok' in plats else ''}
<div class="card"><h3>Contrôles automatiques</h3><ul class="chk">{checks}</ul></div>
{f'<div class="block">{bloc}</div>' if bloc else ''}
</div></body></html>"""
    imgs = {n: os.path.join(dossier, n) for n in ("cover_480.jpg", "grille.jpg")}
    return rendre(p, imgs, sortie, 1080, 5200, rogner_blanc=True)


def semaine(fiches, sortie):
    rows, imgs = [], {}
    jours = [x[0]["date"][:10] for x in fiches]
    for i, (f, dossier) in enumerate(sorted(fiches, key=lambda x: x[0]["date"])):
        r = controler(f)
        if jours.count(f["date"][:10]) > 1:
            r.insert(0, ("alerte", "2 reels le même jour : 1 par jour"))
        ko = [t for n, t in r if n == "bloque"]
        al = [t for n, t in r if n == "alerte"]
        etat = (f'<div class="s" style="color:var(--ko)">✗ {e(ko[0])}</div>' if ko else
                f'<div class="s" style="color:var(--warn)">! {e(al[0])}</div>' if al else
                '<div class="s" style="color:var(--ok)">✓ Tous les contrôles passent</div>')
        l1 = f.get("instagram", {}).get("legende", "").strip().split("\n")[0]
        imgs[f"c{i}.jpg"] = os.path.join(dossier, "cover_480.jpg")
        rows.append(f'<div class="row"><img src="c{i}.jpg"><div><div class="d">{quand(f)}</div>'
                    f'<div class="t">{e(f["titre"])}</div><div class="l">{e(l1)}</div>{etat}</div></div>')
    p = f"""<!doctype html><html><head><meta charset="utf-8">{marque_html()}<style>{CSS}</style></head><body><div class="wrap">
<div class="tag">Publication · semaine à valider</div><h1>{len(fiches)} reel{'s' if len(fiches) > 1 else ''} à programmer</h1>
<div class="when">Un seul OK et tout part</div><div style="margin-top:30px">{''.join(rows)}</div></div></body></html>"""
    return rendre(p, imgs, sortie, 1080, 400 + 330 * len(fiches) + 400, rogner_blanc=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["fiche", "semaine"])
    ap.add_argument("json", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--statut", default="")
    a = ap.parse_args()
    if a.mode == "fiche":
        print("OK", fiche(json.load(open(a.json[0])), os.path.dirname(os.path.abspath(a.json[0])), a.out, a.statut))
    else:
        print("OK", semaine([(json.load(open(j)), os.path.dirname(os.path.abspath(j))) for j in a.json], a.out))
