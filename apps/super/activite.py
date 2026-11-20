#!/usr/bin/env python3
# 11/11 : Claude (dans le chat) dit au Studio ce que fait chaque robot. Le Studio n'a plus de chat, il affiche.
#   python3 activite.py monteur "Je monte ta vidéo"     -> le robot travaille, sa bulle affiche le texte
#   python3 activite.py monteur fini                     -> le robot s'arrête
#   python3 activite.py scripteur script "Titre" < texte -> range un script dans rendus/scripts/ (visible dans le Studio)
import json, os, re, sys, time
ICI = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(ICI, "activite.json")
ROBOTS = ("scripteur", "monteur", "carrousel", "publieur")
if len(sys.argv) < 3 or sys.argv[1] not in ROBOTS: sys.exit(__doc__ or "usage : activite.py <robot> <texte|fini|script Titre>")
k, quoi = sys.argv[1], sys.argv[2]
if quoi == "script":
    titre = sys.argv[3] if len(sys.argv) > 3 else "Script"
    texte = sys.stdin.read().strip()
    d = os.path.join(ICI, "rendus", "scripts"); os.makedirs(d, exist_ok=True)
    nom = time.strftime("%Y-%m-%d-%H%M%S-") + (re.sub(r"[^\w]+", "-", titre.lower()).strip("-")[:40] or "script") + ".md"
    open(os.path.join(d, nom), "w", encoding="utf-8").write(f"# {titre}\n\n{texte}\n")
    print("script rangé :", nom); sys.exit()
try: a = json.load(open(F))
except Exception: a = {}
a[k] = {"travail": quoi != "fini", "texte": "" if quoi == "fini" else quoi, "depuis": time.time()}
tmp = F + ".part"; json.dump(a, open(tmp, "w"), ensure_ascii=False); os.replace(tmp, F)
print(k, "->", a[k]["texte"] or "au repos")
