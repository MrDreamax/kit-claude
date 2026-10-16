#!/bin/bash
# Copie de revue pour Cut Notes : H.264 720p, < 15 Mo (cible 13 Mo).
# Usage : review_copy.sh final.mp4 [sortie.mp4]
# Affiche : chemin, taille en octets, fps. Code 2 si > 15 Mo (alors donner à l'utilisateur le chemin du rendu complet).
set -e
IN="$1"; OUT="${2:-review.mp4}"
DUR=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$IN")
FPS=$(ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate -of default=nw=1:nk=1 "$IN" | awk -F/ '{ if ($2) printf "%.3f", $1/$2; else print $1 }')
# 13 Mo * 8 / durée, moins 128 kb/s d'audio, plafonné à 4 Mb/s
VB=$(awk -v d="$DUR" 'BEGIN { v = int(13*8*1024/d - 128); if (v > 4000) v = 4000; if (v < 300) v = 300; print v }')
ffmpeg -y -v error -i "$IN" -vf "scale='if(gt(iw,ih),-2,720)':'if(gt(iw,ih),720,-2)'" \
  -c:v libx264 -preset medium -b:v ${VB}k -maxrate $((VB*12/10))k -bufsize $((VB*2))k \
  -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 128k "$OUT"
SIZE=$(stat -f%z "$OUT" 2>/dev/null || stat -c%s "$OUT")
echo "$OUT $SIZE $FPS"
[ "$SIZE" -le 15728640 ] || exit 2
