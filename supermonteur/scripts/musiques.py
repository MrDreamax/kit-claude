"""Musiques du dossier music_reels (réglages), avec leur dernière utilisation 

    python3 musiques.py -> jamais utilisées d'abord, puis la plus ancienne ; « INTERDITE » = 3 derniers reels ou 7 derniers jours ; [ambiance] = fiche d'écoute

Choisir ensuite d'après l'AMBIANCE du sujet (pas la 1re de la liste), puis attaque.py pour le temps fort de départ.
"""
import csv, datetime, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reglages

CFG = reglages.config()
dossier = CFG.get("music_reels")
J = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "musiques_utilisees.csv")
rows = list(csv.DictReader(open(J))) if os.path.exists(J) else []
rows = [r for r in rows if r.get("musique") and r.get("reel") and r.get("date")]   # une ligne tronquée du carnet (musique vide) plantait tout le choix de musique
reels = []
for r in rows:   # ordre du carnet = ordre des montages
    if r["reel"] not in reels: reels.append(r["reel"])
limite = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()   # « arrête d'utiliser tout le temps Survivor » : aussi 7 jours
recents = {os.path.basename(r["musique"]) for r in rows if r["reel"] in reels[-3:] or r["date"] >= limite}   # même morceau rangé dans 2 dossiers = même musique
A = os.path.expanduser("~/Documents/Brain/00-Moi/reglages/musiques-ambiance.json")   # fiche de chaque morceau
AMB = json.load(open(A)) if os.path.exists(A) else {}
der = {}
for r in rows: der[os.path.basename(r["musique"])] = (r["date"], os.path.basename(r["reel"]))
if not dossier or not os.path.isdir(dossier): sys.exit("pas de dossier music_reels dans les réglages (ou SSD absent)")
# ce dossier est rangé en sous-dossiers par ambiance
# (« Dark  -  Intense »...) -> on descend dedans ; chaque morceau s'affiche « sous-dossier/fichier », la mémoire reste au nom du fichier.
L = []
for r, ds, fs in os.walk(dossier):
    ds[:] = [d for d in ds if not d.startswith(".")]
    L += [os.path.relpath(os.path.join(r, f), dossier) for f in fs if not f.startswith(".") and f.lower().endswith((".mp3", ".wav", ".m4a"))]
B = os.path.basename
L.sort(key=lambda f: (B(f) in der, der.get(B(f), ("",))[0]))
for f in L:
    p = os.path.join(dossier, f)
    etat = "INTERDITE (3 derniers reels ou 7 jours)" if B(f) in recents else (f"utilisée le {der[B(f)][0]} ({der[B(f)][1]})" if B(f) in der else "jamais utilisée")
    a = AMB.get(B(f), {})
    print(f"{etat:38s} " + (f"[{a.get('ambiance')} · énergie {a.get('energie')}/5{' · chant' if a.get('chant') else ''}] " if a else "") + f)
