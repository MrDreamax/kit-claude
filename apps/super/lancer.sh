#!/bin/bash
# Lance Super et les 4 outils s'ils dorment, puis donne le lien.
cd "$(dirname "$0")" || exit 1
for a in supermonteur supercarrousel; do [ -f "../$a/lancer.sh" ] && bash "../$a/lancer.sh" > /dev/null 2>&1; done  # superda archivé le 12/11/2026
if ! curl -s -m 2 -o /dev/null http://localhost:8800/api/etat; then
  nohup python3 serveur.py 8800 > serveur.log 2>&1 &
  for i in 1 2 3 4 5 6 7 8 9 10; do sleep 0.5; curl -s -m 2 -o /dev/null http://localhost:8800/api/etat && break; done
fi
curl -s -m 2 -o /dev/null http://localhost:8800/api/etat && echo "Super : http://localhost:8800" || { echo "Super ne démarre pas :"; tail -5 serveur.log; exit 1; }
