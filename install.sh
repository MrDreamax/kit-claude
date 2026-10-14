#!/usr/bin/env bash
# Kit Claude : installe la config Claude Code (master prompt, agents, skills)
# et le second cerveau (Brain avec les fiches experts).
#
# Usage : bash install.sh            (depuis le dossier du kit téléchargé)
# Relançable sans risque : c'est aussi la commande de mise à jour.
#
# Ce que le script ne touche JAMAIS une fois installé :
#   - la partie « Qui je suis » du CLAUDE.md (entre les balises PROFIL)
#   - les fichiers perso du Brain : 00-Moi, 01-Projets, 04-Audits, 05-Decisions,
#     hot.md, log.md, index.md
# Tout fichier remplacé est d'abord sauvegardé dans ~/.claude/backups/kit-<date>/.
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CL="$HOME/.claude"
BR="${KIT_BRAIN:-$HOME/Documents/Brain}"
KIT_URL="${KIT_URL:-$(cat "$SRC/KIT_URL" 2>/dev/null || echo "")}"
TS="$(date +%Y%m%d-%H%M%S)"
BK="$CL/backups/kit-$TS"
NOTES=()

mkdir -p "$CL/agents" "$CL/skills" "$BR"

backup() { # backup <chemin> : copie l'existant avant de le remplacer
  local rel="${1#"$HOME"/}"
  mkdir -p "$BK/$(dirname "$rel")"
  cp -R "$1" "$BK/$rel"
}

# ---------- 1. Master prompt (CLAUDE.md) ----------
NEW="$SRC/config/CLAUDE.md"
DEST="$CL/CLAUDE.md"
if [[ -f "$DEST" ]] && grep -q '<!-- PROFIL:DEBUT -->' "$DEST"; then
  # Mise à jour : on garde « Qui je suis » tel quel.
  BLOCK="$(mktemp)"
  awk '/<!-- PROFIL:DEBUT -->/{f=1} f{print} /<!-- PROFIL:FIN -->/{f=0}' "$DEST" > "$BLOCK"
  OUT="$(mktemp)"
  awk -v bf="$BLOCK" '
    /<!-- PROFIL:DEBUT -->/ { while ((getline l < bf) > 0) print l; skip=1; next }
    /<!-- PROFIL:FIN -->/   { skip=0; next }
    !skip { print }' "$NEW" > "$OUT"
  if ! cmp -s "$OUT" "$DEST"; then backup "$DEST"; cp "$OUT" "$DEST"; fi
  rm -f "$BLOCK" "$OUT"
  NOTES+=("Master prompt mis à jour (ton profil est intact).")
elif [[ -f "$DEST" ]]; then
  # Un CLAUDE.md perso existait avant le kit : on le sauvegarde, bienvenue le relira.
  backup "$DEST"
  cp "$NEW" "$DEST"
  NOTES+=("Ancien CLAUDE.md sauvegardé dans $BK/.claude/CLAUDE.md (le skill bienvenue récupère ce qui compte).")
else
  cp "$NEW" "$DEST"
  NOTES+=("Master prompt installé.")
fi

# ---------- 2. Agents et skills ----------
n_ag=0
for f in "$SRC"/config/agents/*.md; do
  d="$CL/agents/$(basename "$f")"
  if [[ -f "$d" ]] && ! cmp -s "$f" "$d"; then backup "$d"; fi
  cp "$f" "$d"; n_ag=$((n_ag + 1))
done
n_sk=0
for s in "$SRC"/config/skills/*/; do
  name="$(basename "$s")"
  d="$CL/skills/$name"
  if [[ -d "$d" ]] && ! diff -rq "$s" "$d" >/dev/null 2>&1; then backup "$d"; rm -rf "$d"; fi
  mkdir -p "$d"; cp -R "$s". "$d"/; n_sk=$((n_sk + 1))
done
NOTES+=("$n_ag agents et $n_sk skills installés.")

# ---------- 3. Le Brain ----------
# Fichiers du kit (mis à jour à chaque installation) : experts, livres, conseillers, outils.
for dir in 02-Formations 03-Livres 08-Conseillers _outils; do
  mkdir -p "$BR/$dir"
  cp -R "$SRC/brain/$dir/." "$BR/$dir/"
done
for f in README.md MODE-EMPLOI.html; do cp "$SRC/brain/$f" "$BR/$f"; done
# Fichiers perso : copiés seulement s'ils n'existent pas encore.
(
  cd "$SRC/brain"
  for p in 00-Moi 01-Projets 04-Audits 05-Decisions hot.md log.md index.md; do
    [[ -e "$p" ]] || continue
    find "$p" -type f | while read -r f; do
      if [[ ! -e "$BR/$f" ]]; then mkdir -p "$BR/$(dirname "$f")"; cp "$f" "$BR/$f"; fi
    done
  done
)
NOTES+=("Brain prêt dans $BR ($(find "$BR" -name '*.md' | wc -l | tr -d ' ') fiches).")

# ---------- 4. Mémo d'installation ----------
{
  echo "Kit Claude installé le $(date '+%d/%m/%Y %H:%M')"
  echo "Lien du kit (pour « mets à jour mon kit ») : ${KIT_URL:-inconnu}"
  echo "Brain : $BR"
} > "$CL/kit-claude.txt"

echo ""
echo "KIT CLAUDE : INSTALLATION TERMINÉE"
for n in "${NOTES[@]}"; do echo "- $n"; done
[[ -d "$BK" ]] && echo "- Sauvegarde des anciens fichiers : $BK"
echo "- Prochaine étape : lancer le skill bienvenue ($CL/skills/bienvenue/SKILL.md)."
