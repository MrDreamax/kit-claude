#!/usr/bin/env bash
# Récupère les transcripts YouTube (vidéo / playlist / chaîne) puis les nettoie.
#
# Usage :
#   bash fetch.sh "URL1" "URL2" ...        # une ou plusieurs URLs
#   bash fetch.sh -f urls.txt              # une URL par ligne (# = commentaire)
#
# Sortie : ./veille-youtube/transcripts/*.vtt (brut) + *.txt (nettoyé)
#          (surcharge : YT_OUT=/autre/dossier)
#
# Réglages (variables d'environnement) :
#   YT_SUBS    langues des sous-titres   (défaut : fr-orig,en-orig)
#   YT_SLEEP   secondes entre requêtes   (défaut : 2, ne pas descendre en dessous)
#   YT_CLIENT  client YouTube de yt-dlp  (défaut : android_vr)
#
# ─────────────────────────────────────────────────────────────────────────────
# À SAVOIR SUR LES BLOCAGES
#
# 1) Le client par défaut est `android_vr` : c'est celui qui a donné les lots les
#    plus réguliers à l'usage. `tv` renvoie souvent « DRM protected », `web_safari`,
#    `mweb` et `ios` sont bloqués plus vite.
#
# 2) Mais le client n'est pas la variable principale : le quota d'IP l'est. Une fois
#    ce quota épuisé, tous les clients renvoient le même « HTTP 429 ». Changer de
#    client ne débloque rien par soi-même ; c'est le temps écoulé qui débloque.
#
# 3) Ce qui marche vraiment, dans cet ordre :
#    a. étaler : --sleep-requests ≥ 2 ;
#    b. fractionner : ~100-150 vidéos par session ;
#    c. rendre repartable : les vidéos déjà sur le disque sont écartées avant tout
#       appel réseau, et --no-overwrites protège l'existant ;
#    d. attendre quand ça bloque, puis relancer la même commande ;
#    e. trier la liste par priorité avant de lancer.
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TDIR="${YT_OUT:-$PWD/veille-youtube/transcripts}"
mkdir -p "$TDIR"

command -v python3 >/dev/null || { echo "python3 introuvable (voir « Prérequis » dans SKILL.md)."; exit 1; }

# Trouver yt-dlp, y compris hors du PATH : l'exécutable autonome est rangé dans
# ~/.local/bin, et `pip install --user` range la commande dans un dossier que le
# PATH ne contient pas toujours (~/Library/Python/3.x/bin sur macOS). Dans ce
# dernier cas, `python3 -m yt_dlp` fonctionne quand même.
if [[ -n "${YT_DLP:-}" ]]; then YTDLP=("$YT_DLP")
elif command -v yt-dlp >/dev/null; then YTDLP=(yt-dlp)
elif [[ -x "$HOME/.local/bin/yt-dlp" ]]; then YTDLP=("$HOME/.local/bin/yt-dlp")
elif python3 -c "import yt_dlp" 2>/dev/null; then YTDLP=(python3 -m yt_dlp)
else echo "yt-dlp introuvable (voir « Prérequis » dans SKILL.md)."; exit 1
fi

YT_CLIENT="${YT_CLIENT:-android_vr}"
SLEEP_REQ="${YT_SLEEP:-2}"

# Une seule piste par vidéo : la piste auto-générée dans la langue parlée (-orig).
# Les autres pistes auto sont des traductions machine : elles coûtent du quota
# pour aucune information en plus.
# ⚠️ `-orig` ne désigne QUE la piste auto-générée. Les sous-titres DÉPOSÉS par la
# chaîne portent des codes de locale (fr-FR, en-US…) et ne correspondent à aucun
# `-orig`. Un lot qui renvoie « no subtitles » en masse est presque toujours ce cas :
# vérifier avec `yt-dlp --list-subs URL`, puis relancer avec YT_SUBS="fr-FR".
SUB_LANGS="${YT_SUBS:-fr-orig,en-orig}"

# Construire la liste d'URLs
URLS=()
if [[ "${1:-}" == "-f" ]]; then
  [[ -f "${2:-}" ]] || { echo "Fichier d'URLs introuvable : ${2:-}"; exit 1; }
  while IFS= read -r line || [[ -n "$line" ]]; do
    [[ -n "$line" && "$line" != \#* ]] && URLS+=("$line")
  done < "$2"
else
  URLS=("$@")
fi

[[ ${#URLS[@]} -eq 0 ]] && { echo "Aucune URL fournie."; exit 1; }

# ── Écarter avant l'appel réseau ce qui est déjà sur le disque ───────────────
# --no-overwrites empêche de RÉÉCRIRE un fichier, mais pas de redemander la vidéo :
# yt-dlp doit lire ses métadonnées pour connaître le nom de sortie, et cette requête
# consomme le quota d'IP comme un téléchargement. Un lot relancé brûlerait donc son
# quota sur des vidéos déjà extraites. On filtre en amont, sur l'ID présent dans le
# nom de fichier. Ne s'applique qu'aux URLs de vidéo unique (une playlist ou une
# chaîne n'a pas d'ID de vidéo).
KEPT=()
SKIPPED=0
for u in "${URLS[@]}"; do
  vid=""
  [[ "$u" =~ [?\&]v=([A-Za-z0-9_-]{11}) ]] && vid="${BASH_REMATCH[1]}"
  [[ -z "$vid" && "$u" =~ youtu\.be/([A-Za-z0-9_-]{11}) ]] && vid="${BASH_REMATCH[1]}"
  [[ -z "$vid" && "$u" =~ /shorts/([A-Za-z0-9_-]{11}) ]] && vid="${BASH_REMATCH[1]}"
  if [[ -n "$vid" ]] && compgen -G "$TDIR/*__$vid.txt" > /dev/null; then
    SKIPPED=$((SKIPPED + 1))
    continue
  fi
  KEPT+=("$u")
done
if [[ $SKIPPED -gt 0 ]]; then
  echo ">> $SKIPPED vidéo(s) déjà extraite(s) : écartée(s) avant l'appel réseau."
fi
[[ ${#KEPT[@]} -eq 0 ]] && { echo ">> Rien à faire, tout le lot est déjà sur le disque."; exit 0; }
URLS=("${KEPT[@]}")

LOG="$TDIR/.fetch-$(date +%Y%m%d-%H%M%S).log"
echo ">> ${#URLS[@]} source(s) à traiter · langues=$SUB_LANGS · client=$YT_CLIENT · pause=${SLEEP_REQ}s"
echo ">> yt-dlp  : ${YTDLP[*]} ($("${YTDLP[@]}" --version))"
echo ">> sortie  : $TDIR"
echo ">> journal : $LOG"

"${YTDLP[@]}" \
  --skip-download \
  --write-auto-subs --write-subs \
  --sub-langs "$SUB_LANGS" \
  --sub-format vtt \
  --convert-subs vtt \
  --extractor-args "youtube:player_client=$YT_CLIENT" \
  --ignore-errors \
  --no-overwrites \
  --sleep-requests "$SLEEP_REQ" \
  --restrict-filenames \
  --no-progress \
  -o "$TDIR/%(uploader)s__%(title).80s__%(id)s.%(ext)s" \
  "${URLS[@]}" 2>&1 | tee "$LOG" || echo ">> (certaines vidéos ont pu échouer, on continue)"

# ── Diagnostic : les deux échecs ne se traitent pas pareil ───────────────────
BOT=$(grep -c "Sign in to confirm" "$LOG" || true)
RATE=$(grep -c "429" "$LOG" || true)
NOSUB=$(grep -c "no subtitles for the requested" "$LOG" || true)
echo
echo ">> Bilan d'extraction"
echo "   bloquées par l'anti-robot : $BOT"
echo "   HTTP 429 (quota IP)       : $RATE"
echo "   sans piste demandée       : $NOSUB"
if [[ "$BOT" -gt 0 || "$RATE" -gt 0 ]]; then
  cat <<'MSG'
   ⚠️  Blocage en cours. C'est récupérable, mais pas en changeant de client :
       le quota est attaché à l'IP et tous les clients le partagent.
       Le seul remède est le temps. Attendre (30 min à quelques heures), puis
       relancer la MÊME commande : seules les vidéos manquantes seront demandées.
       Si ça persiste : augmenter YT_SLEEP (4, puis 8) et fractionner le lot.
MSG
fi
if [[ "$NOSUB" -gt 0 ]]; then
  echo "   ℹ️  « no subtitles » n'est pas un blocage, et pas non plus la preuve qu'il"
  echo "       n'y a pas de sous-titres : seulement qu'il n'y en a pas dans les langues"
  echo "       demandées ($SUB_LANGS)."
  cat <<'MSG'
       Avant de conclure, lancer sur UNE vidéo :
             yt-dlp --list-subs "URL"
       Une chaîne qui dépose ses sous-titres les expose sous des codes de locale
       (fr-FR, en-US…) : relancer alors avec YT_SUBS="fr-FR" (ou la locale affichée).
       Si la vidéo n'a réellement aucune piste, relancer n'y changera rien : seule
       une transcription locale de l'audio (par exemple Whisper) la récupère.
MSG
fi

echo
echo ">> Nettoyage des .vtt en .txt"
shopt -s nullglob
# Une vidéo peut avoir plusieurs pistes sur le disque (YT_SUBS élargi). On prend
# toujours l'originale avant une traduction machine.
PREF_LANGS=(fr-orig en-orig fr en)
# Dédoublonnage sans tableau associatif : `declare -A` exige bash ≥ 4, or macOS
# livre encore bash 3.2. `sort -u` fait le même travail partout.
BASES="$(
  for vtt in "$TDIR"/*.vtt; do
    b="$(basename "$vtt")"; b="${b%.vtt}"
    echo "$b" | sed -E 's/\.[a-z]{2,3}(-[a-zA-Z0-9-]+)?$//'
  done | sort -u
)"
while IFS= read -r base; do
  [[ -z "$base" ]] && continue
  [[ -s "$TDIR/$base.txt" ]] && continue   # idempotent : ne recalcule pas l'existant
  src=""
  for lang in "${PREF_LANGS[@]}"; do
    if [[ -s "$TDIR/$base.$lang.vtt" ]]; then src="$TDIR/$base.$lang.vtt"; break; fi
  done
  # autre langue : on prend la première piste trouvée pour cette vidéo
  [[ -z "$src" ]] && src="$(ls "$TDIR/$base".*.vtt 2>/dev/null | head -1)"
  [[ -z "$src" ]] && continue
  python3 "$DIR/clean_vtt.py" "$src" > "$TDIR/$base.txt"
done <<< "$BASES"

echo ">> Terminé."
found=("$TDIR"/*.txt)
echo "   ${#found[@]} transcript(s) nettoyé(s) dans $TDIR"
