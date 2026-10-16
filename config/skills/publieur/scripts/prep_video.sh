#!/bin/bash
# Prépare la vidéo pour Metricool : 1080x1920 H.264 + AAC, départ rapide, et contrôle les limites (Reels : 9:16, 3 s à 15 min, 500 Mo max).
# Usage : prep_video.sh final.mp4 sortie.mp4
set -e
IN="$1"; OUT="$2"
[ -f "$IN" ] || { echo "Vidéo introuvable : $IN"; exit 1; }
W=$(ffprobe -v error -select_streams v:0 -show_entries stream=width -of csv=p=0 "$IN")
H=$(ffprobe -v error -select_streams v:0 -show_entries stream=height -of csv=p=0 "$IN")
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
python3 - "$W" "$H" "$D" <<'P'
import sys
w, h, d = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3])
if abs(w / h - 9 / 16) > 0.02: sys.exit(f"BLOQUE : format {w}x{h}, il faut du 9:16")
if not 3 <= d <= 900: sys.exit(f"BLOQUE : durée {d:.1f} s (3 s à 15 min)")
P
ffmpeg -v error -y -i "$IN" -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -vf "scale=1080:1920" -r 30 \
  -c:a aac -b:a 192k -movflags +faststart "$OUT"
S=$(wc -c < "$OUT" | tr -d ' ')
[ "$S" -lt 500000000 ] || { echo "BLOQUE : $S octets (500 Mo max)"; exit 1; }
echo "OK $OUT $(python3 -c "print(round($S/1e6,1))") Mo, $(python3 -c "print(round($D,1))") s"
