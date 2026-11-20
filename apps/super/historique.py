"""20/11/2026 : l'historique du Studio n'était plus à jour.
Cause : le Studio lisait les vieilles boîtes d'avant le 13/11 (rendus/scripts, publication.json, projets SuperCarrousel).
Depuis, chaque robot range son travail ici, chez l'utilisateur ET chez les clients :
  Scripteur  -> Brain/06-Contenu/scripts.md      (1 ligne par script, texte dans Fichier)
  Carrousel  -> Brain/06-Contenu/carrousels.md   (1 ligne par carrousel, images dans Dossier)
  Publieur   -> Brain/06-Contenu/publications.md (tableau ou lignes « - date · ... »)
  Monteur    -> <montages>/*/final.mp4           (dernier rendu de chaque montage)
Le Studio lit donc ces sources, et rien d'autre. Aucune écriture ici.
"""
import glob, json, os, re, time
from datetime import datetime

HOME = os.path.expanduser("~")
BRAIN = os.environ.get("SUPER_BRAIN") or os.path.join(HOME, "Documents", "Brain")
CONTENU = os.path.join(BRAIN, "06-Contenu")
TEST = re.compile(r"(^|-)(test|essai)(-|$)", re.I)
IMG = (".png", ".jpg", ".jpeg", ".webp")
VID = (".mp4", ".mov")
MOIS = {m: i + 1 for i, m in enumerate(["janv", "févr", "mars", "avr", "mai", "juin", "juil", "août", "sept", "oct", "nov", "déc"])}


def _date(s):
    """« 2026-11-20 09:11 », « 20/11/2026 », « 13/11/2026 23h30 », « 15/11 17h20 » -> horodatage (0 si illisible)."""
    s = (s or "").strip()
    m = re.search(r"(\d{4})-(\d\d)-(\d\d)(?:[ T](\d\d)[:h](\d\d))?", s)
    if m:
        y, mo, d, h, mi = m.groups()
    else:
        m = re.search(r"(\d{1,2})/(\d{1,2})(?:/(\d{4}))?(?:\D+(\d{1,2})h(\d\d)?)?", s)
        if not m: return 0
        d, mo, y, h, mi = m.groups()
        y = y or str(datetime.now().year)
    try: return datetime(int(y), int(mo), int(d), int(h or 0), int(mi or 0)).timestamp()
    except ValueError: return 0


def _statut(s):
    return re.sub(r"\s*\([^)]*\)", "", s or "").strip()


def _lignes_tableau(f):
    """Lignes d'un tableau Markdown (sans en-tête ni séparateur), cellules nettoyées."""
    if not os.path.exists(f): return []
    out, entete = [], None
    for l in open(f, encoding="utf-8"):
        l = l.strip()
        if not l.startswith("|"): continue
        c = [x.strip() for x in l.strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", x or "--") for x in c): continue
        if entete is None: entete = [x.lower() for x in c]; continue
        out.append(dict(zip(entete, c + [""] * (len(entete) - len(c)))))
    return out


def _chemin(p):
    """Chemin écrit à la main dans le Brain -> vrai chemin sur le Mac (ou "")."""
    p = (p or "").strip().strip("`").split(" (")[0].strip()
    if not p: return ""
    p = os.path.expanduser(p)
    for base in ("", BRAIN, os.path.join(HOME, "Documents"), CONTENU):
        q = p if os.path.isabs(p) else os.path.join(base, p)
        if base == "" and not os.path.isabs(p): continue
        if os.path.exists(q): return q
    return ""


def scripts():
    out = []
    for r in _lignes_tableau(os.path.join(CONTENU, "scripts.md")):
        f = _chemin(r.get("fichier"))
        texte = ""
        if f and os.path.isfile(f) and f.endswith((".md", ".txt")):
            texte = re.sub(r"^---\n.*?\n---\n", "", open(f, encoding="utf-8").read(), flags=re.S).strip()
        titre = r.get("accroche") or r.get("sujet") or "Script"
        t = _date(r.get("date")) or (os.path.getmtime(f) if f else 0)
        out.append({"titre": titre[:1].upper() + titre[1:], "date": t, "statut": _statut(r.get("statut")),
                    "version": r.get("version", ""), "texte": texte})
    return sorted(out, key=lambda x: x["date"], reverse=True)


def carrousels():
    out = []
    for r in _lignes_tableau(os.path.join(CONTENU, "carrousels.md")):
        d = _chemin(r.get("dossier"))
        media = sorted(x for x in glob.glob(os.path.join(d, "*")) if x.lower().endswith(IMG + VID)) if d and os.path.isdir(d) else []
        couv = next((x for x in media if x.lower().endswith(IMG)), "")
        titre = r.get("sujet") or "Carrousel"
        out.append({"titre": titre[:1].upper() + titre[1:], "date": _date(r.get("date")) or (os.path.getmtime(d) if d else 0),
                    "statut": _statut(r.get("statut")), "version": r.get("version", ""), "couverture": couv, "media": media})
    return sorted(out, key=lambda x: x["date"], reverse=True)


RES = {"ig": "Insta", "insta": "Insta", "instagram": "Insta", "fb": "Facebook", "facebook": "Facebook", "yt": "YouTube",
       "youtube": "YouTube", "tiktok": "TikTok", "linkedin": "LinkedIn", "threads": "Threads"}


def _reseaux(s):
    vus = []
    for m in re.finditer(r"\b(ig|insta(?:gram)?|fb|facebook|yt|youtube|tiktok|linkedin|threads)\b", (s or "").lower()):
        n = RES[m.group(1)]
        if n not in vus: vus.append(n)
    return vus


def _titre_pub(s):
    m = re.search(r"«\s*([^»]+?)\s*»", s)
    t = m.group(1) if m else s
    t = re.sub(r"\b(IMG|CAM)[_ ]?\d+\b", "", t)
    t = re.sub(r"\([^)]*\)", "", t).strip(" ·-:")
    return t[:1].upper() + t[1:] if t else "Une publication"


def publications():
    f = os.path.join(CONTENU, "publications.md")
    if not os.path.exists(f): return []
    out = []
    for r in _lignes_tableau(f):
        cles = list(r.keys())
        if not cles: continue
        tout = " ".join(r.values())
        statut = r.get("statut", "")
        if not re.search(r"publi|programm|blotato", (statut + " " + tout).lower()): continue
        if re.search(r"\b(préparé|annulé|abandonné)\b", statut.lower()) and "publi" not in statut.lower(): continue
        quoi = "carrousel" if "carrousel" in tout.lower() else "reel"
        out.append({"titre": _titre_pub(r.get(cles[1], "")), "date": _date(r.get(cles[0])), "reseaux": _reseaux(tout),
                    "quoi": quoi, "brut": tout})
    for l in open(f, encoding="utf-8"):
        l = l.strip()
        if not l.startswith("- ") or "·" not in l: continue
        p = [x.strip() for x in l[2:].split("·")]
        quoi = "carrousel" if "carrousel" in l.lower() else "reel"
        titre = next((x for x in p[1:] if "«" in x), p[1] if len(p) > 1 else "")
        out.append({"titre": _titre_pub(titre), "date": _date(p[0]), "reseaux": _reseaux(l), "quoi": quoi, "brut": l})
    out = [x for x in out if x["date"]]
    return sorted(out, key=lambda x: x["date"], reverse=True)


def _titre_montage(d, pubs):
    try:
        t = json.load(open(os.path.join(d, "plan.json"), encoding="utf-8")).get("title") or {}
        t = " ".join(x for x in (t.get("l1"), t.get("l2")) if x).strip() if isinstance(t, dict) else str(t)
        if t: return t
    except Exception: pass
    k = os.path.basename(d)
    num = re.search(r"(img|cam)[_-]?(\d{3,})", k, re.I)
    for p in pubs:
        if k in p["brut"] or (num and re.search(rf"\b{num.group(1)}[_ ]?{num.group(2)}\b", p["brut"], re.I)):
            return p["titre"]
    return ""


def montages(dossier):
    pubs = publications()
    out = []
    for f in glob.glob(os.path.join(dossier, "*", "final.mp4")):
        d = os.path.dirname(f); k = os.path.basename(d)
        if TEST.search(k): continue
        vign = next((os.path.join(d, n) for n in ("apercu2.jpg", "apercu.jpg", "vignette.jpg", "planche.jpg") if os.path.exists(os.path.join(d, n))), "")
        valide = False
        try: valide = json.load(open(os.path.join(d, "etat.json"), encoding="utf-8")).get("statut") == "valide"
        except Exception: pass
        out.append({"id": k, "titre": _titre_montage(d, pubs), "date": os.path.getmtime(f), "video": f, "vignette": vign, "valide": valide})
    return sorted(out, key=lambda x: x["date"], reverse=True)


def media_autorise(p, racines):
    """Le Studio ne montre que des images ou vidéos rangées dans le Brain, Contenu ou les montages."""
    p = os.path.realpath(p)
    if not p.lower().endswith(IMG + VID) or not os.path.isfile(p): return False
    return any(p.startswith(os.path.realpath(r) + os.sep) for r in racines)
