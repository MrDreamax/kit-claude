#!/bin/bash
# Vérifie / installe ce qu'il faut pour monter (une seule fois par ordinateur). Ne casse rien si c'est déjà là.
# Mac : les trois outils de base s'installent avec Homebrew (https://brew.sh) :
#   brew install ffmpeg node        puis        pip3 install --user numpy pillow faster-whisper mediapipe onnxruntime
# Facultatif : pip3 install --user demucs librosa opencv-python   et   brew install yt-dlp
export PATH="$HOME/.local/bin:$HOME/.local/node/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
ok=1
command -v python3 >/dev/null || { echo "MANQUE python3 (Mac : xcode-select --install)"; ok=0; }
command -v node >/dev/null    || { echo "MANQUE node : brew install node (ou https://nodejs.org)"; ok=0; }
command -v ffmpeg >/dev/null  || { echo "MANQUE ffmpeg : brew install ffmpeg"; ok=0; }
command -v ffprobe >/dev/null || { echo "MANQUE ffprobe (livré avec ffmpeg) : brew install ffmpeg"; ok=0; }
MODS="numpy onnxruntime faster_whisper mediapipe PIL"
PIPS="numpy onnxruntime faster-whisper mediapipe pillow"
if command -v python3 >/dev/null; then
  python3 -c "import ${MODS// /, }" 2>/dev/null || python3 -m pip install --user -q $PIPS
  python3 -c "import ${MODS// /, }" 2>/dev/null || { echo "MANQUE modules python : pip3 install --user $PIPS"; ok=0; }
fi
# Chrome de rendu + puppeteer-core d'HyperFrames (rendu, contrôle des zones, texte du B-roll + texte)
if command -v npx >/dev/null; then
  npx --yes hyperframes@0.6.81 browser ensure >/dev/null 2>&1 || { echo "MANQUE Chrome de rendu (npx --yes hyperframes@0.6.81 browser ensure)"; ok=0; }
fi
# Modèle de détourage (RobustVideoMatting, licence GPL-3.0 : téléchargé ici sur TON ordinateur, jamais redistribué par le kit)
M="$HOME/.cache/supermonteur/rvm_mobilenetv3_fp32.onnx"
if [ ! -s "$M" ]; then
  mkdir -p "$(dirname "$M")"
  curl -sL -o "$M" https://github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_mobilenetv3_fp32.onnx
fi
[ -s "$M" ] || echo "ATTENTION : modèle de détourage absent (utile seulement pour high prod et green screen) : $M"
# Dossiers de travail (vides au départ)
mkdir -p "$HOME/Documents/Contenu/medias/"{rushes,brolls,photos,sfx} "$HOME/Documents/Contenu/medias/musique/"{epidemic,libre} "$HOME/Documents/Contenu/montages"
[ $ok = 1 ] && echo "SETUP OK" || exit 1
