---
name: logiciels
description: Installe en un clic les logiciels gratuits du système (Obsidian pour voir le second cerveau, Wispr Flow pour dicter au lieu de taper, Chrome + Claude in Chrome, yt-dlp pour lire YouTube, et en bonus Fathom et Canva), puis les règle. Use from the bienvenue skill, or when "installe les logiciels", "installe Obsidian", "installe Wispr", "dictée vocale", "quels logiciels", "ouvre mon cerveau dans Obsidian".
---

# Logiciels : le système complet, en un clic

Vérifié sur les sites officiels le 14/10/2026. Si un lien ou un nom ne marche plus : va voir le site officiel, ne devine pas.

## 1. Regarder ce qui est déjà là
- Mac : `ls /Applications`, `command -v brew`, `command -v yt-dlp || ls ~/.local/bin/yt-dlp`.
- Windows : `winget list` (PowerShell).
Ne propose pas ce qui est déjà installé.

## 2. Demander (AskUserQuestion, 2 questions, multiSelect)
**« Les essentiels : j'installe lesquels ? »** (tout coché = recommandé)
- **Obsidian (Recommandé)** : ton second cerveau devient visible, comme un wiki (liens, carte). Gratuit, sans compte.
- **Wispr Flow (Recommandé)** : tu parles au lieu de taper, dans toutes les apps. Gratuit jusqu'à 2 000 mots/semaine. Compte à créer.
- **Chrome + Claude in Chrome** : je peux utiliser ton navigateur pour toi (remplir, chercher, cliquer). Gratuit (l'extension demande un forfait Claude payant).
- **Outil YouTube (yt-dlp)** : invisible, il me permet de lire les vidéos YouTube pour les skills. Gratuit, 37 Mo.

**« Des bonus ? »**
- **Fathom** : enregistre, transcrit et résume tes visios (Zoom, Meet, Teams). Gratuit et illimité. Compte à créer (avec une adresse Gmail ou Outlook perso, il faut une visio prévue dans les 7 jours).
- **Canva** : créer visuels, présentations, posts. Gratuit (5 Go, 20 usages d'IA). Compte à créer.
- **Rien d'autre**

Le choix vaut accord pour télécharger ces logiciels depuis leurs sites officiels. Annonce en une ligne le poids total (Wispr ~300 Mo, Chrome ~280 Mo, Canva ~230 Mo) et la durée (2 à 10 minutes selon la connexion).

## 3. Installer
| Logiciel | Mac (Homebrew) | Windows (winget) | Lien officiel |
|---|---|---|---|
| Obsidian | `brew install --cask obsidian` | `Obsidian.Obsidian` | obsidian.md/download |
| Wispr Flow | `brew install --cask wispr-flow` | `WisprFlow.WisprFlow` | wisprflow.ai/downloads |
| Chrome | `brew install --cask google-chrome` | `Google.Chrome` | google.com/chrome |
| yt-dlp | `brew install yt-dlp` | `yt-dlp.yt-dlp` | github.com/yt-dlp/yt-dlp |
| Fathom | `brew install --cask fathom` | `Fathom.Fathom` | fathom.video/download |
| Canva | `brew install --cask canva` | `Canva.Canva` | canva.com/download |

**Mac avec Homebrew** : une seule commande `brew install --cask <les apps choisies>` (+ `brew install yt-dlp`).

**Mac sans Homebrew** (cas le plus courant) : n'installe pas Homebrew (il demande le mot de passe). Pour chaque app :
- `curl -fL -o /tmp/<app>.dmg "<lien>"`, puis `hdiutil attach -nobrowse -quiet /tmp/<app>.dmg`, copie le `.app` du volume monté dans `/Applications` (`cp -R`), `hdiutil detach`, supprime le .dmg.
- Liens directs officiels :
  - Chrome : `https://dl.google.com/chrome/mac/universal/stable/GGRO/googlechrome.dmg`
  - Obsidian : le `.dmg` de la dernière release (`curl -s https://api.github.com/repos/obsidianmd/obsidian-releases/releases/latest`, champ `browser_download_url` qui finit par `.dmg`)
  - Canva : `https://www.canva.com/download/mac/universal/canva-desktop` (redirige vers le .dmg)
  - Wispr Flow et Fathom : pas de lien direct stable (testé le 14/10/2026 : la page renvoie du HTML). Ouvre `https://wisprflow.ai/downloads` ou `https://fathom.video/download/macos` et dis : « Clique sur le bouton de téléchargement Mac, ouvre le fichier et glisse l'app dans Applications. »
- yt-dlp : `mkdir -p ~/.local/bin && curl -fL -o ~/.local/bin/yt-dlp https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_macos && chmod +x ~/.local/bin/yt-dlp`, puis `~/.local/bin/yt-dlp --version`.

**Windows** : `winget install --id <ID> -e`. winget demande d'accepter les conditions des logiciels : montre-le à la personne et demande son accord une fois pour toutes avant d'ajouter `--accept-package-agreements --accept-source-agreements`. Sans winget : ouvre le lien officiel.

Un échec ? Trouve la cause (réseau, place disque, droits), corrige, réessaie une fois. Sinon ouvre la page officielle et donne l'action en une ligne.

## 4. Régler (après chaque installation)
- **Obsidian** : enregistre le Brain comme coffre AVANT le premier lancement, si Obsidian n'est pas ouvert. Fichier : Mac `~/Library/Application Support/obsidian/obsidian.json`, Windows `%APPDATA%\obsidian\obsidian.json`. Format : `{"vaults":{"<16 caractères hexadécimaux au hasard>":{"path":"<chemin absolu du Brain>","ts":<heure en millisecondes>,"open":true}}}`. Si le fichier existe : ajoute l'entrée sans rien effacer, et retire `"open":true` des autres. Puis ouvre Obsidian. Si le Brain ne s'affiche pas : « Au démarrage d'Obsidian, clique Open folder as vault > Open, choisis Documents > Brain, puis Open. »
- **Wispr Flow** : ouvre l'app. Action de la personne en une ligne : « Connecte-toi (Google ou mail), autorise le micro et l'accessibilité. Ensuite, maintiens Fn (Mac) ou Ctrl+Win (Windows) et parle : le texte s'écrit là où est ton curseur. »
- **Chrome + Claude in Chrome** : ouvre `https://chromewebstore.google.com/detail/claude/fcoeoabgfenejglbffodgkkbkcdhcgfn` dans Chrome. Action : « Clique Add to Chrome, connecte-toi avec ton compte Claude, épingle l'extension. Vérifie que l'éditeur est Anthropic. » Puis dans l'app Claude : Settings > Connectors > Claude in Chrome, l'activer.
- **yt-dlp** : rien à faire. Teste `yt-dlp --version` (ou `~/.local/bin/yt-dlp --version`).
- **Fathom** : ouvre `https://fathom.video`. Action : « Crée ton compte et connecte ton agenda : il rejoindra tes visios tout seul. »
- **Canva** : ouvre l'app. Action : « Connecte-toi ou crée ton compte. »

## 5. Vérifier, puis dire
Vérifie chaque app (`ls /Applications/<App>.app` ou `winget list`). Note dans `~/Documents/Brain/00-Moi/profil.md`, section « Mes outils », la liste installée avec la date.
Message final, 1 ligne par app : « ✓ Obsidian : ton cerveau est dedans » · « ✓ Wispr Flow : reste à te connecter (1 min) » · « ✗ Canva : lien à cliquer : ... ». Rien d'autre.
