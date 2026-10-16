#!/bin/bash
# Archive une vidéo PUBLIÉE : l'historique de toutes tes vidéos terminées au même endroit.
# Dossier par défaut : ~/Documents/Contenu/publications/archive (ou un disque externe de ton choix : 4e argument ou variable PUBLIEUR_ARCHIVE).
# Copie (jamais de déplacement) sous le nom « AAAA-MM-JJ - Titre.mp4 ». Code 2 = disque absent, on réessaie au prochain passage.
# Usage : archive.sh final.mp4 2026-10-19 "Tier list des formats Instagram" [/dossier/d/archive]
set -e
SRC="$1"; DATE="$2"; TITRE="$3"
EXPLICITE="${4:-$PUBLIEUR_ARCHIVE}"
DEST_DIR="${EXPLICITE:-$HOME/Documents/Contenu/publications/archive}"
[ -n "$SRC" ] && [ -n "$DATE" ] && [ -n "$TITRE" ] || { echo "Usage : archive.sh final.mp4 AAAA-MM-JJ \"Titre\" [dossier]"; exit 1; }
# Dossier choisi par l'utilisateur (disque externe) : son dossier parent doit exister, sinon le disque est absent (on ne crée jamais un faux disque).
if [ -n "$EXPLICITE" ] && [ ! -d "$(dirname "$DEST_DIR")" ]; then echo "Disque ou dossier absent ($(dirname "$DEST_DIR")) : archive à refaire au prochain passage"; exit 2; fi
[ -f "$SRC" ] || { echo "Vidéo introuvable : $SRC"; exit 1; }
mkdir -p "$DEST_DIR"
NOM=$(printf '%s' "$TITRE" | tr '/:' '--')
DEST="$DEST_DIR/$DATE - $NOM.${SRC##*.}"
taille() { wc -c < "$1" | tr -d ' '; }
if [ -f "$DEST" ] && [ "$(taille "$DEST")" = "$(taille "$SRC")" ]; then echo "DÉJÀ ARCHIVÉE $DEST"; exit 0; fi
cp -p "$SRC" "$DEST"
[ "$(taille "$DEST")" = "$(taille "$SRC")" ] || { echo "ERREUR : copie incomplète $DEST"; exit 1; }
echo "OK $DEST"
