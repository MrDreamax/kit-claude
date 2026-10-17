#!/usr/bin/env python3
"""Refait index.md et contrôle la santé du Brain.

Usage : python3 ~/Documents/Brain/_outils/brain.py
- Réécrit index.md (1 ligne par fichier : description, statut, taille, date).
- Imprime un contrôle : liens morts, fichiers sans description, statuts inconnus,
  chemins cités par les agents/skills/routines qui n'existent plus, âge de hot.md.
Ne déplace, ne renomme et ne supprime jamais rien. Ne touche qu'à index.md.
"""
import os
import re
import sys
import datetime as dt
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLAUDE_DIR = os.path.expanduser("~/.claude")
STATUTS = ["actif", "en-pause", "remplacé", "rejeté", "historique"]
PERIMES = {"en-pause", "remplacé", "rejeté", "historique"}
SUJETS = ["closing", "pub-meta", "contenu", "montage", "audio", "da", "youtube",
          "offre", "ia", "clients", "business", "perso", "argent", "sante", "etudes",
          "famille", "admin", "apprendre"]
ENTREES = ["hot.md", "index.md", "log.md", "README.md"]
GROS_KO = 20
# fichiers que les routines créent elles-mêmes la première fois (pas une panne s'ils manquent)
A_LA_DEMANDE = {"07-Clients/calls-hors-clients.md", "00-Moi/import-chatgpt.md",
                "07-Clients/00-resultats.md", "07-Clients/00-calls-groupe.md", "01-Projets/charges.md",
                "06-Contenu/declinaisons.md", "06-Contenu/presse-emissions.md", "06-Contenu/manychat.md"}


# ---------- lecture ----------

def parse_frontmatter(text):
    """Frontmatter YAML simple (clé: valeur, listes [a, b]). Renvoie (dict, corps)."""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end == -1:
        return {}, text
    fm = {}
    for line in text[4:end].split("\n"):
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1].replace('\\"', '"')
        elif val.startswith("[") and val.endswith("]") and not val.startswith("[["):
            val = [v.strip().strip("\"'") for v in val[1:-1].split(",") if v.strip()]
        fm[key] = val
    body = text[end + 4:]
    return fm, body.lstrip("\n")


def h1_of(body):
    m = re.search(r"^# (.+)$", body, re.M)
    return m.group(1).strip() if m else ""


def load():
    notes = {}
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = sorted(d for d in dns if not d.startswith((".", "_")))  # _outils, _archives-chatgpt
        for fn in sorted(fns):
            if not fn.endswith(".md"):
                continue
            full = os.path.join(dp, fn)
            rel = os.path.relpath(full, ROOT)
            with open(full, encoding="utf-8", errors="replace") as f:
                text = f.read()
            fm, body = parse_frontmatter(text)
            st = os.stat(full)
            notes[rel[:-3]] = {
                "rel": rel, "fm": fm, "body": body, "h1": h1_of(body),
                "ko": max(1, round(st.st_size / 1024)),
                "date": dt.date.fromtimestamp(st.st_mtime),
                "text": text,
            }
    return notes


# ---------- description automatique pour les fichiers rangés par convention ----------

def jjmm(y, m, d):
    return "%s/%s" % (d, m)


def derive(key, n, notes):
    """Complète description/type/statut/sujets à partir du frontmatter ou des conventions."""
    fm = n["fm"]
    desc = fm.get("description", "")
    typ = fm.get("type", "")
    statut = fm.get("statut", "")
    sujets = fm.get("sujets", [])
    if isinstance(sujets, str):
        sujets = [s.strip() for s in sujets.split(",") if s.strip()]
    auto = False
    folder = key.split("/")[0]

    m_brief = re.match(r"04-Audits/brief-(\d{4})-(\d\d)-(\d\d)$", key)
    m_rel = re.match(r"04-Audits/relances-(\d{4})-(\d\d)-(\d\d)$", key)
    m_veille = re.match(r"02-Formations/veille-(\d{4})-(\d\d)-(\d\d)-", key)
    m_scripts = re.match(r"06-Contenu/(\d{4})-S(\d+)-scripts-test$", key)

    if not desc:
        auto = True
        if m_brief:
            desc, typ, sujets = "Brief du matin du %s." % jjmm(*m_brief.groups()), "brief", ["business"]
        elif m_rel:
            desc, typ, sujets = "Relances du %s : contacts qui dorment et messages prêts (rien envoyé)." % jjmm(*m_rel.groups()), "relances", ["closing"]
        elif m_veille:
            desc, typ, sujets = "Fiche veille du %s : %s" % (jjmm(*m_veille.groups()), n["h1"]), "veille", ["ia"]
        elif m_scripts:
            desc, typ, sujets = "Scripts test semaine %s." % m_scripts.group(2), "contenu", ["contenu"]
        elif key == "07-Clients/calls-hors-clients":
            desc, typ, sujets = "Calls hors clients (partenaires, prospects, ads) : 1 ligne datée par call.", "index", ["business"]
        elif folder == "07-Clients" and typ == "client":
            bits = [n["h1"] or key.split("/")[-1]]
            if fm.get("niche"):
                bits.append(str(fm["niche"]))
            if fm.get("dernier_call"):
                bits.append("dernier call %s" % fm["dernier_call"])
            desc = " · ".join(bits)
            sujets = ["clients"]
        elif key.startswith("00-Moi/regles-agents/"):
            desc, typ, sujets = n["h1"].replace("Carnet de ", "Carnet : ").replace("Carnet du ", "Carnet : "), "carnet", ["ia"]
        elif folder == "08-Conseillers" and key.count("/") == 2:
            desc, typ = n["h1"], "conseiller"
        else:
            desc = n["h1"] or key.split("/")[-1]
            auto = "manque"  # pas de description et pas de convention
    if not statut or (folder == "07-Clients" and typ == "client"):
        doc_statut = "actif"
    else:
        doc_statut = statut
    # anciens briefs / relances : historique (seul le plus récent reste actif)
    if (m_brief or m_rel) and "statut" not in fm:
        prefix = "04-Audits/brief-" if m_brief else "04-Audits/relances-"
        latest = max(k for k in notes if k.startswith(prefix))
        doc_statut = "actif" if key == latest else "historique"
    return {
        "desc": desc, "type": typ, "statut": doc_statut, "sujets": sujets,
        "remplace_par": fm.get("remplace_par", ""), "auto": auto,
        "client_statut": statut if typ == "client" else "",
    }


# ---------- contrôle ----------

LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")


def resolve(target, notes, by_base):
    t = target.strip()
    if t.endswith(".md"):
        t = t[:-3]
    if t in notes or t in by_base:
        return True
    # liens vers des fichiers non-md (images, pdf, canvas) dans le vault
    return os.path.exists(os.path.join(ROOT, target.strip()))


def agent_paths():
    """Chemins du Brain cités par les skills, agents et routines de Claude."""
    found = defaultdict(set)
    pat = re.compile(r"((?:0[0-9]-[A-Za-zÀ-ÿ]+)/[\w./À-ÿ-]+?\.md|Brain/(?:hot|index|log|README)\.md)")
    roots = [os.path.join(CLAUDE_DIR, d) for d in ("skills", "agents", "scheduled-tasks")]
    files = [os.path.join(CLAUDE_DIR, "CLAUDE.md")]
    for r in roots:
        for dp, dns, fns in os.walk(r):
            dns[:] = [d for d in dns if d not in ("node_modules", ".git")]
            files += [os.path.join(dp, f) for f in fns if f.endswith((".md", ".json", ".py", ".sh"))]
    for f in files:
        try:
            with open(f, encoding="utf-8", errors="ignore") as h:
                txt = h.read()
        except OSError:
            continue
        if "Brain" not in txt and "0" not in txt:
            continue
        for p in pat.findall(txt):
            if any(x in p for x in ("<", "AAAA", "XX", "*", "JJ", "nom-prenom", "SXX")):
                continue
            p = p.replace("Brain/", "")
            found[p].add(os.path.relpath(f, CLAUDE_DIR))
    return found


def hot_age():
    path = os.path.join(ROOT, "hot.md")
    try:
        txt = open(path, encoding="utf-8").read()
    except OSError:
        return None
    m = re.search(r"MAJ\s*:\s*(\d{4}-\d\d-\d\d)", txt)
    d = dt.date.fromisoformat(m.group(1)) if m else dt.date.fromtimestamp(os.stat(path).st_mtime)
    return (dt.date.today() - d).days


def controle(notes, meta):
    by_base = defaultdict(list)
    for k in notes:
        by_base[k.split("/")[-1]].append(k)
    issues = []
    morts = []
    for k, n in notes.items():
        if k == "index":
            continue
        sans_code = re.sub(r"```.*?```", "", n["text"], flags=re.S)
        sans_code = re.sub(r"`[^`\n]*`", "", sans_code)  # un exemple en `code` n'est pas un lien
        for t in LINK_RE.findall(sans_code):
            if not resolve(t, notes, by_base):
                morts.append("%s → [[%s]]" % (n["rel"], t.strip()))
    if morts:
        issues.append(("Liens morts", morts))
    sans = [notes[k]["rel"] for k, m in meta.items() if m["auto"] == "manque" and k.split("/")[-1] not in ("hot", "index", "log", "README")]
    if sans:
        issues.append(("Sans description (ajoute un en-tête, voir README)", sans))
    casses = []
    for k, n in notes.items():
        t = n["text"]
        if not t.startswith("---\n"):
            continue
        for ln in t[4:t.find("\n---", 4)].split("\n"):
            m = re.match(r"^[A-Za-z_][\w-]*:\s*(.*)$", ln)
            v = m.group(1).strip() if m else ""
            if not v or v[0] in "\"'|>" or (v.startswith("[") and not v.startswith("[[")):
                continue
            if ": " in v or v.startswith("[[") or v[0] in "@`%{":
                casses.append("%s → %s (mets la valeur entre guillemets)" % (n["rel"], ln[:60]))
    if casses:
        issues.append(("En-tête cassé (Obsidian ne le lit plus)", casses))
    inconnus = ["%s (statut: %s)" % (notes[k]["rel"], m["statut"]) for k, m in meta.items()
                if m["statut"] not in STATUTS]
    if inconnus:
        issues.append(("Statut hors vocabulaire", inconnus))
    sujets_inc = ["%s (%s)" % (notes[k]["rel"], s) for k, m in meta.items() for s in m["sujets"] if s not in SUJETS]
    if sujets_inc:
        issues.append(("Sujet hors vocabulaire", sujets_inc))
    rp = []
    for k, m in meta.items():
        t = m["remplace_par"]
        if t:
            inner = LINK_RE.findall(t)
            if inner and not resolve(inner[0], notes, by_base):
                rp.append("%s → %s" % (notes[k]["rel"], t))
    if rp:
        issues.append(("remplace_par vers un fichier absent", rp))
    standard = {"_hot", "principles", "frameworks", "voice", "sources", "stories", "positions", "books", "README"}
    amb = ["%s : %s" % (b, ", ".join(sorted(v))) for b, v in by_base.items() if len(v) > 1 and b not in standard]
    if amb:
        issues.append(("Noms en double (un lien court peut ouvrir le mauvais fichier)", amb))
    cass = []
    for p, srcs in sorted(agent_paths().items()):
        if p not in A_LA_DEMANDE and not os.path.exists(os.path.join(ROOT, p)):
            cass.append("%s (cité par %s)" % (p, ", ".join(sorted(srcs))))
    if cass:
        issues.append(("Chemins cités par les agents/skills/routines qui n'existent plus", cass))
    age = hot_age()
    if age is not None and age > 7:
        issues.append(("hot.md trop vieux", ["dernière MAJ il y a %d jours : à rafraîchir" % age]))
    return issues, age


# ---------- écriture de l'index ----------

def line(k, n, m, show_statut=False):
    s = "- "
    if m["statut"] in PERIMES:
        s += "⚠ %s · " % m["statut"]
    s += "[[%s]] · %s · %s" % (k, m["desc"], n["date"].strftime("%d/%m"))
    if n["ko"] >= GROS_KO:
        s += " · **%d Ko**" % n["ko"]
    if m["remplace_par"]:
        s += " → lire %s" % m["remplace_par"]
    return s


def build(notes, meta, issues, age):
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    out = []
    out.append("# Index du Brain")
    out.append("Généré automatiquement le %s par `python3 ~/Documents/Brain/_outils/brain.py`. Ne pas éditer à la main : écrasé à chaque passage." % now)
    out.append("")
    out.append("Lire dans cet ordre : [[hot]] (état actuel) → cet index → seulement les fichiers utiles. Écrire une note : [[README]] (règles).")
    out.append("Ligne = `[[chemin]] · ce qu'il y a dedans · date de modif`. **Taille en gras** = gros fichier (%d Ko et plus) : grep d'abord, puis lire la section. ⚠ = périmé : ne pas s'appuyer dessus, lire le fichier indiqué par →." % GROS_KO)
    out.append("")

    # par sujet
    out.append("## Par sujet (fichiers actifs, hors clients, carnets et conseillers)")
    par = defaultdict(list)
    for k, m in meta.items():
        if m["statut"] in PERIMES or m["type"] in ("client", "carnet", "conseiller", "brief", "relances"):
            continue
        for s in m["sujets"]:
            par[s].append(k)
    bases = defaultdict(int)
    for k in notes:
        bases[k.split("/")[-1]] += 1
    court = lambda k: k.split("/")[-1] if bases[k.split("/")[-1]] == 1 else k
    for s in SUJETS:
        if par.get(s):
            out.append("- **%s** (%d) : %s" % (s, len(par[s]), " · ".join("[[%s]]" % court(k) for k in sorted(par[s], key=court))))
    out.append("")

    folders = sorted({k.split("/")[0] for k in notes if "/" in k})
    for fo in folders:
        keys = sorted(k for k in notes if k.startswith(fo + "/"))
        if fo == "07-Clients":
            out.append("## 07-Clients (%d fiches)" % len([k for k in keys if meta[k]["type"] == "client"]))
            for k in keys:
                m = meta[k]
                if m["type"] != "client":
                    out.append(line(k, notes[k], m))
            for k in keys:
                m = meta[k]
                if m["type"] == "client":
                    out.append("- [[%s]] · %s · client %s" % (k, m["desc"], m["client_statut"] or "?"))
            out.append("")
            continue
        if fo == "08-Conseillers":
            people = sorted({k.split("/")[1] for k in keys if k.count("/") == 2})
            out.append("## 08-Conseillers (%d cerveaux d'experts, en anglais)" % len(people))
            for k in keys:
                if k.count("/") == 1:
                    out.append(line(k, notes[k], meta[k]))
            for p in people:
                hot = "08-Conseillers/%s/_hot" % p
                pil = re.search(r"\*\*(?:Pillar|Seat):\*\*\s*([^*\n]+?)\s*\*\*(?:The )?[Qq]uestion[^*]*\*\*\s*([^\n]+)", notes[hot]["body"]) if hot in notes else None
                autres = [k.split("/")[-1] for k in keys if k.startswith("08-Conseillers/%s/" % p) and not k.endswith("/_hot")]
                out.append("- [[%s]] · %s · puis au plus 2 de : %s" % (hot, ("%s %s" % (pil.group(1).strip(), pil.group(2).strip()) if pil else p), ", ".join(autres)))
            out.append("")
            continue
        main = [k for k in keys if k.count("/") == 1]
        subs = [k for k in keys if k.count("/") > 1]
        out.append("## %s (%d)" % (fo, len(keys)))
        actifs = [k for k in main if meta[k]["statut"] not in PERIMES and meta[k]["type"] != "veille"]
        veille = sorted([k for k in main if meta[k]["type"] == "veille" and meta[k]["statut"] not in PERIMES],
                        key=lambda k: (bool(re.search(r"/veille-\d{4}-", k)), k))
        perimes = [k for k in main if meta[k]["statut"] in PERIMES and meta[k]["statut"] != "historique"]
        histo = [k for k in main if meta[k]["statut"] == "historique"]
        for k in actifs:
            out.append(line(k, notes[k], meta[k]))
        if veille:
            out.append("- Fiches veille (%d) : lire d'abord la synthèse, puis une fiche si besoin" % len(veille))
            for k in veille:
                out.append("  " + line(k, notes[k], meta[k]))
        sub_dirs = sorted({"/".join(k.split("/")[:2]) for k in subs})
        for sd in sub_dirs:
            sk = [k for k in subs if k.startswith(sd + "/")]
            readme = sd + "/README"
            if readme in notes:
                out.append(line(readme, notes[readme], meta[readme]))
            rest = [k for k in sk if k != readme]
            if rest and all(meta[k]["type"] == "carnet" for k in rest):
                out.append("  - %d carnets (lus par chaque agent avant sa mission) : %s" % (
                    len(rest), " · ".join("[[%s|%s]]" % (k, k.split("/")[-1]) for k in rest)))
            else:
                for k in rest:
                    out.append("  " + line(k, notes[k], meta[k]))
        for k in perimes:
            out.append(line(k, notes[k], meta[k]))
        if histo:
            out.append("- Historique (ne lire que si besoin) : %s" % " · ".join("[[%s]]" % k for k in histo))
        out.append("")

    out.append("## Contrôle automatique")
    total = len(notes)
    if not issues:
        out.append("- Tout est propre : %d fichiers, 0 lien mort, 0 fichier sans description, 0 chemin d'agent cassé, hot.md MAJ il y a %s j." % (total, age))
    else:
        out.append("- %d fichiers. Points à régler (au prochain audit du dimanche) :" % total)
        for title, items in issues:
            out.append("  - **%s** (%d) : %s" % (title, len(items), " ; ".join(items[:15]) + (" ; ..." if len(items) > 15 else "")))
    out.append("")
    return "\n".join(out)


def main():
    notes = load()
    meta = {k: derive(k, n, notes) for k, n in notes.items()}
    issues, age = controle(notes, meta)
    txt = build(notes, meta, issues, age)
    tmp = os.path.join(ROOT, ".index.md.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(txt)
    os.replace(tmp, os.path.join(ROOT, "index.md"))
    print("Index refait : %d fichiers." % len(notes))
    if not issues:
        print("Contrôle : tout est propre (hot.md MAJ il y a %s j)." % age)
    for title, items in issues:
        print("- %s : %d" % (title, len(items)))
        for i in items[:10]:
            print("    %s" % i)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # ne jamais faire planter une routine
        print("brain.py : erreur, index non modifié : %s" % e)
        sys.exit(0)
