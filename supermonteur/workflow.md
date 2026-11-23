# Workflow du Monteur : brief, étapes 1 à 9

Lu quand on monte à la main, qu'on répare ou qu'un fichier de style cite une étape. Musique : `musique.md`. B-rolls : `brolls.md`. Cahier des charges : `cahier-des-charges.md`.

## Ordre rapide, texte complet des 2 premiers points
2. **Dérush** (ordre rapide, section 2) → durée exacte et seconde de la punchline connues. **Derush Lab RETIRÉ** : le dérush part direct au montage. Ne plus lancer cockpit.py --lab avant de monter.

2. **Face caméra = le style Dynamique** : mix à équilibrer de split screen (face cam + animation), face cam seule, cartons plein écran en dégradé propre, animations plein écran, avec ses sous-titres. Aucune question de degré ; ne plus dire « high prod » ni « degré sous-titres ». « Minimaliste » = le nom du style 2 (choisi par l'utilisateur, l'interditest levé). Les variantes se tranchent en maquettes (round 1 = aspect global, round 2 = détails).
3. **DA** : seulement chez un nouveau client (DA existante `da/<prenom>.json` / nouvelle DA). L'utilisateur = sa DA (`~/Documents/Brain/00-Moi/reglages/da-montage.json`), ne pas demander.
6. **Ambiance et musique** : `musique.md`.
- **Format** : 9:16 pour un reel, ne pas poser la question. Vidéo YouTube : 16:9, `styles/youtube-theyo.md` (remplace « 16:9 pas géré »).
- **Images et vidéos générées par IA : JAMAIS**. Ni Higgsfield, ni Kling, ni Seedance, ni Nano Banana, ni GPT Image, dans AUCUN style, même si un fichier de style en parle encore. Ses vrais plans d'abord ; rien qui colle → Pexels (vérifier la personne), ou pas de B-roll.

## Workflow commun (le fichier du style dit quelles étapes il change)
Un dossier par reel, tout se lance depuis ce dossier.

**Ordre rapide** : on MESURE le cadre, on transcrit le RUSH, puis le dérush coupe ET recadre en une seule passe, sur les seules secondes gardées. Rush c31 de 6 min : 15 min 27 → 37 s, même image, même synchro, Gardien ✅. Ne plus encoder tout le rush avant de couper. Pièges réglés dans les scripts (ne pas y revenir) : encodage = puce vidéo du Mac, jamais `-hwaccel videotoolbox` au décodage (image toute verte), plage de couleurs de la source gardée (sinon -5 % de lumière).

**1. Mesurer le cadre** (choix : recadrage automatique ; montage viral : SANS `cadre.py`)
```bash
python3 $S/cadre.py <rush ORIGINALE, 4K>          # ~5 s, n'encode rien -> cadre.json
VF=$(python3 -c "import json;print(json.load(open('cadre.json'))['vf'])")
```
Rush filmé large (yeux sous 40 % ou visage < 28 % de la largeur) → recadrage fixe depuis la 4K : yeux à 35 %, visage à 33 % (cadre serré du rush « vidéos virales », reel validé 7,75/10). Déjà serrée → simple mise au format. Toujours partir du rush ORIGINALE 4K (zoom > 1,10 sur du 1080 = flou ; le script plafonne alors à 1,10). Plan large de scène (conférence, écran géant derrière) : cadrer à la main (voir `feedback.md`).

**2. Transcrire le RUSH** (`scripts/transcribe.py`, moteur commun `scripts/mots.py` pour TOUS les outils : ElevenLabs Scribe d'abord, envoyé en Opus pour que les longs rushs passent, 2 nouveaux essais si ElevenLabs est occupé, Whisper small du Mac en secours ; chaque mot est recalé sur l'énergie de la voix, utile en salle qui résonne). Nouvel outil qui a besoin des mots = `from mots import transcrire`, jamais `WhisperModel` en direct. Le son du rush est le même que celui du clip : pas besoin d'attendre un recadrage.
```bash
python3 $S/transcribe.py <rush ORIGINALE> words.json
```

**3. Dérusher + recadrer en une passe**
Lire la transcription. Repérer les répétitions et phrases ratées : on garde la **dernière** prise. Les noter en plages d'indices de mots dans `drop.json` (`[[12,18]]`, ou `[]`).
```bash
python3 $S/derush.py <rush ORIGINALE> words.json cut.mp4 --drop drop.json --vf "$VF"
python3 $S/transcribe.py cut.mp4 words.json && mv cut.mp4 clip.mp4      # on retravaille sur la version coupée
```
**Coupes au ras de la voix** : derush.py laisse ~0,15 s de blanc à CHAQUE coupe, même serré, et `--plages` remet ses marges. Après derush.py (sans --vf), toujours : `python3 ~/.claude/skills/supermonteur/outils/derush/ras.py <rush> <dossier>` → `ras.mp4` + `ras.words.json` (~0,08 s par coupe, son = image, Gardien « mot coupé » vert). Mesurer les blancs avec un seuil FIXE (un clip serré n'a plus de silence pour caler le « calme »).
**Pub à plusieurs hooks** : une seule vidéo par script, écran noir 1 s « HOOK 1 / HOOK 2 / HOOK 3 / BODY » avant chaque partie : `python3 ~/.claude/skills/supermonteur/outils/derush/ecrans_hooks.py ras.mp4 ras.words.json <sortie.mp4> --parts "début hook 1|début hook 2|...|début body"`.
**Rush déjà dérushé** (rien à couper) : `python3 $S/cadre.py <rush ORIGINALE> --apply` → clip.mp4 directement (puce vidéo du Mac), puis `transcribe.py clip.mp4 words.json`.
**Entrée / sortie** : le dérush garde 0,15 s avant le 1er mot et 0,6 s après le dernier (`--lead` / `--tail`). Il écrit aussi `cut.words.json` = la transcription du RUSH recalée sur la version coupée (souvent meilleure qu'une transcription refaite sur le montage coupé) : on peut la prendre au lieu de retranscrire.
Le script ne coupe que dans les blancs entre deux mots : fin de phrase (., ! ? … ; :) = blanc + respiration supprimés ; milieu de phrase = AUCUNE coupe d'image, le souffle est seulement baissé au bruit de la pièce. Chaque coupe : micro-fondu son de 0,03 s (anti-clic) et plages calées sur la grille des images (image et son exactement de la même durée, la bouche ne se décale jamais). Testé.
**La pause avant la punchline** (seulement s'il la demande, les cuts serrésgagnent ; la musique continue dessous) : repérer la punchline AVANT le dérush et ajouter `--pause <indice du mot punchline>` : la vraie pause avant ce mot est gardée (jusqu'à 0,9 s). Pas de pause dans le rush = pas de silence (le dire à l'utilisateur : marquer un temps avant la phrase choc au tournage).

**4. Écrire `plan.json`** en lisant la transcription (c'est là que se joue la qualité). Champs communs (le fichier du style ajoute les siens) :
```json
{
  "cam": "clip.mp4", "words": "words.json",
  "fixes": {"boulettes": "bullet"},
  "keywords": ["dangereux", "illégal", "hook", "succès", "virales"],
  "music": {"src": "<dossier music_reels>/<titre>", "from": 0, "fin": "naturelle"},
}
```
- **fixes** : relire TOUTE la transcription et corriger les erreurs de Whisper (`{"boulettes": "bullet"}`). Obligatoire : une faute dans un sous-titre = reel raté. `fixes` change CHAQUE occurrence du mot (→ « 10 » aurait aussi changé « tu dis oui ») : un mot courant se corrige directement dans `words.json` (son indice).
- **keywords** : 6-10 mots forts, ou groupes de 2-3 mots (`"badge bleu"`) → serif italique blanc 132 px, affichés SEULS à l'écran (les petits mots devant restent dans le bloc d'avant). Jamais en couleur.
- **title** : `{"l1": "Le badge bleu Meta", "l2": "une arnaque ?", "start": 0, "end": 4}` = titre-question pendant le hook (petites MAJUSCULES + serif italique, voile sombre, fondu ; `top` pour le placer, ex. 1300 = en bas quand la tête touche le haut du cadre). **Règle (Style Lab assouplie) : vidéo AVEC titre = pas de mot fort serif (`keywords` ignorés), mais les mots géants derrière la tête restent permis (« dépendance », « AGI » demandés sur RUSH) ; vidéo SANS titre = mots forts + mots géants.** Titre : jamais de virgule, point ni deux-points (build.mjs les retire). Proposer le titre dans le plan de chaque reel.
- **cta** : `{"start", "end", "word": "HOOK", "count": "1 284", "user": "toi", "comments": [["pseudo", "texte", "2 min"], ...]}` = sur « commente MOT » : vraie feuille de commentaires qui monte du bas, le mot se tape lettre par lettre (clavier qui s'allume), puis se publie en haut de la liste. Commentaires par défaut = des gens qui tapent le mot (pas de faux témoignages).
- **music** : `musique.md` (dossier `music_reels`, niveau, début, frappe, changement de musique, cas client). **silences** : NE PLUS UTILISER, voir `musique.md`.

**4 bis. B-rolls** : `brolls.md`.

**5. Ajouts du style** : voir le fichier du style (B-rolls, images, tableau, source…).

**6. Compo + rendu + son** : par défaut **`bash $S/monte.sh .`** = tout ce qui suit d'un coup, avec le Gardien AVANT le rendu ; il affiche le temps de chaque étape et s'arrête au 1er problème. Testé sur Titanic. Les commandes une par une ne servent qu'à réparer :
```bash
node $S/build.mjs --plan plan.json --out index.html              # écrit aussi timeline.json (vraies positions, lues par le Gardien)
npx --yes hyperframes@0.8.149 lint                                # 0 erreur (warning "overlap 0 s" sur #camwrap = sans effet)
node $S/zones.mjs .                                              # zones mortes Insta : « OK : 0 » attendu (~3 s)
npx --yes hyperframes@0.8.149 render . -q high                    # ~2 min 30 pour 40 s
python3 $S/mix.py plan.json renders/<x>.mp4 clip.mp4 final.mp4   # voix (config voice_lufs, -14) + musique recalée par morceau + SFX auto
```
(Face caméra : `matte.py` avant le build, voir `styles/face-cam.md`.)
**Son de salle** (conférence, micro de scène capté par la caméra) : `python3 $S/voix_propre.py clip.mp4 voix/doux.wav words.json` = sa voix ORIGINALE + EQ douce vers sa voix studio (`config.voice_ref`), ±3,5 dB max (la version forte Demucs + expandeur + exciteur rendait sa voix « bizarre et déformée », « +10 dB c'est trop, +3 ou +4 »). `--fort` seulement avec son accord. Puis `mix.py ... voix/doux.wav final.mp4`. Client : sa voix studio en `--ref`.
**Choix de la musique à l'oreille** : `musique.md`.
**Couleur** (seulement si l'utilisateur le demande) : 2 options en avant / après sur 2 images AVANT de rendre (`couleur/avant-apres.jpg`), noirs P1 1-8 vérifiés (`lookstats.py`), puis `ffmpeg -vf "$(cat couleur/<option>.txt)"` sur clip.mp4 → clip_grade.mp4 = `plan.cam`. Validée sur la conf : « Naturel » (peau plus chaude, violet calmé).
**Écran noir au départ** : corrigé dans mix.py (la vidéo commençait à 0,021 s, QuickTime / iPhone / Instagram n'avaient aucune image à 0 s). Contrôle : ffprobe `start_time` = 0.

**7. Vérifier (obligatoire avant de dire "c'est fait")**
```bash
ffprobe -v error -show_entries stream=codec_name,width,height,pix_fmt,start_time -of compact final.mp4   # h264 1080x1920 yuv420p + aac, start_time 0
ffmpeg -y -v error -i final.mp4 -vf "fps=2,scale=150:-1,tile=10x8" -frames:v 1 check.jpg
ffmpeg -i final.mp4 -af ebur128 -f null - 2>&1 | grep " I:" | tail -1     # final ~ -14 LUFS
```
`mix.py` mesure CHAQUE morceau sous la voix et le recale tout seul sur sa cible (`target`, défaut -32) à ±1 LU ; il affiche une ligne par morceau (OK / trop fort / TROP BAS) puis « final : -14 LUFS, crête vraie ≤ -2 dBTP ». Pour un CTA plus calme : `"target": -33` sur le dernier segment. **Mesurer la musique SEULE dans le final (Demucs)** : 15-17 dB sous la voix, sinon on ne l'entend pas.
Regarder `check.jpg` : un seul bloc de sous-titre à la fois, tête devant chaque chiffre, listes lisibles, B-rolls répartis régulièrement, pas de visage coupé. Échec → corriger, refaire.

**7 bis. Le Gardien (obligatoire, BLOQUANT)** : `python3 $S/gardien.py .` vérifie chaque erreur que l'utilisateur a DÉJÀ signalée (micro-coupes, silences entendus, musique coupée ou en retard, trou de son, fin muette, écran noir, plans < 1,2 s, flash de tête, bruitages collés, volume, zones mortes). Un seul ❌ = on corrige et on relance, JAMAIS on livre. Testé : bloque Tesla v1, v2, v3, laisse passer la v4 validée.
**AVANT le rendu : `python3 $S/gardien.py . --avant`** (monte.sh le lance seul, ~10 s) : micro-coupures, plans ≥ 2 s, silences, musique dès 0 s et jusqu'au bout, plus d'1 minute (`"duree_min": 0` dans plan.json pour un client), B-rolls sans HDR, flash de tête, bruitages, zones mortes, et un APERÇU image par image (face cam + B-rolls + cartons en vignettes) pour les flashs. Testé sur Titanic : la v1 est bloquée avant le rendu sur les mêmes erreurs que le Gardien avait trouvées après (micro-coupures 29,3 / 42,97 / 49,5 s, plans de 1,54 et 0,18 s, flash à 35,5 s, 59,1 s), la version validée passe. Seul ce qui dépend du rendu reste après : volume, fin muette, image dès 0 s, et un B-roll qui bouge vite (tête tournée dans le plan de la montre).

**8. Note /10** : `note-10.md` (obligatoire).
**Livraison** : la vraie vidéo seulement. JAMAIS de « copie légère pour le téléphone » ; si l'envoi refuse un fichier > 30 Mo, dire en une ligne qu'il est dans l'app du Mac.

## Rush renommé après le montage
Dès que le titre du reel est fixé (v1 montée), renommer le rush pour le retrouver : `python3 ~/Documents/SuperApps/supermonteur/renommer_rush.py <dossier du montage>` (ou `--rush <chemin>` si le rush n'est cité nulle part) -> `2026-10-28 Titre du reel - RUSH.MP4`, sur place (carte de la caméra ou SSD), sans copie ; les fiches des montages qui citaient l'ancien chemin sont mises à jour. Le moteur le fait seul après la v1. Jamais sur un B-roll, une musique ou un fichier du montage.


**9. Boucle feedback (après chaque reel)**
Source : Christian Peverelli, montage automatisé avec Claude Code (règles accumulées par retours).
1. Retours = **Cut Notes** (s'ouvre seul après chaque version, notes accrochées à l'image). Sinon : ses retours dans le chat.
2. Corriger le reel (retouches ciblées). **Parcours « le mix » (choix de l'utilisateur)** : style choisi UNE fois au début (3 aperçus de 5 s, mémorisé) → 1 seule version complète → correction en 2 passes max : sur le point qui cloche SEULEMENT, 3 cartes à cliquer (3 musiques, 3 accroches…), jamais 3 versions complètes du reel (Titanic : 87 min).
3. Chaque retour ou note (« 6/10, musique trop forte ») = **une ligne datée dans `feedback.md`** (règle générale + historique des notes), et une ligne dans le carnet Brain `00-Moi/regles-agents/supermonteur.md`. Si la règle change une règle de ce skill, corriger le fichier concerné (SKILL.md ou le fichier du style) pour qu'il n'y ait jamais deux versions. Une erreur corrigée ne revient jamais.
4. **Note mesurable = un contrôle de plus dans `gardien.py`** (date + note d'origine), puis le relancer sur la dernière vidéo validée : elle doit rester ✅. C'est ça qui empêche une erreur de revenir, pas le carnet.
5. **Compteur de versions** : chaque reel = une ligne dans l'historique de `feedback.md` avec la version (v1, v2...) et « VALIDÉ » quand il dit oui. Objectif : validé en v1, au pire v2. Le DRH compte le dimanche : nombre moyen de versions par reel.
