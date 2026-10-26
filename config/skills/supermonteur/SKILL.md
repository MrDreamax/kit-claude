---
name: supermonteur
description: Le Monteur. Monte ton rush en reel 9:16 Instagram prêt à poster, au niveau d'un vrai monteur (dérush, sous-titres + mot fort en serif, musique émotionnelle, zones mortes Instagram), avec TES couleurs et TA police. 8 styles, un fichier chacun - face caméra en 3 degrés (sous-titres, minimaliste, high prod), à plusieurs (podcast, visio, split screen), voix off, green screen, montage viral (comparaison en T, mauvais / bien / excellent, tier list), B-roll + texte. Tu peux donner 1 à 3 reels de référence que tu aimes : il en tire la recette (rythme, niveau de musique), jamais le contenu. Use when "monte-moi ce rush", "monte ce reel", "monte cette vidéo", "sous-titre cette vidéo", "sous-titres", "montage", "face cam", "podcast", "visio", "voix off", "green screen", "tier list", "comparaison en T", "à faire / à ne pas faire", "mauvais bien excellent", "B-roll + texte", "texte sur b-roll", "lis la légende", "monteur", "supermonteur".
---

# Le Monteur : un rush → un reel premium prêt à poster

Chaque montage doit tenir la comparaison avec le reel d'un vrai monteur. Tu donnes le rush, Claude fait le reste : dérush, sous-titres, musique, B-rolls, contrôles. Tu valides un plan court avant, tu regardes le résultat après.

```bash
export PATH="$HOME/.local/bin:$HOME/.local/node/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
S=~/.claude/skills/supermonteur/scripts
$S/setup.sh            # 1re fois sur un ordinateur : doit afficher SETUP OK (sinon il dit quoi installer)
```
Annoncer la durée au lancement et à la fin (~5 min pour 40 s de vidéo).

## Carnet d'apprentissage et réglages
- Avant de commencer : lis `~/Documents/Brain/00-Moi/regles-agents/supermonteur.md` (s'il n'existe pas, crée-le). Ses règles passent AVANT tout le reste de ce skill. Deux règles qui se contredisent : la plus RÉCENTE gagne.
- Si l'utilisateur corrige, note ou refuse un montage (même en passant) : ajoute UNE ligne datée, `JJ/MM/AAAA · reel · note · ce qui n'allait pas → règle`, et dis-le en une ligne : « Noté dans mon carnet : ... ».
- **Ta marque** (couleur principale, couleur foncée, police) : `~/Documents/Brain/00-Moi/marque.json`, lu par `scripts/reglages.py`. **Ta DA en mots** (ambiance, décor, tenue) : `00-Moi/da.md`. **Ta voix et ta cible** (pour les titres, mots forts, CTA, légendes) : `00-Moi/voix-contenu.md` et `00-Moi/strategie-contenu.md`. S'ils contiennent encore « À REMPLIR », le montage tourne quand même avec des réglages neutres ; propose juste le skill `ma-marque` en une ligne.
- **Réglages techniques** : `config.json` (dossiers, niveaux de son, kit SFX : valeurs par défaut) puis `~/Documents/Brain/00-Moi/montage.json` (les tiens : même clés + un bloc `da`, jamais écrasé par une mise à jour du kit). `python3 $S/reglages.py da` affiche la DA de montage utilisée.
- **Dossiers** : rushes `~/Documents/Contenu/medias/rushes/` · B-rolls `.../medias/brolls/` · photos `.../medias/photos/` · musique `.../medias/musique/{epidemic,libre}/` · SFX `.../medias/sfx/` · un dossier par reel dans `~/Documents/Contenu/montages/AAAA-MM-JJ-<sujet>/` (tout se lance depuis ce dossier). Une info absente (ex. ton dossier de B-rolls est ailleurs) : demande-la UNE fois en bouton, et écris-la dans `montage.json` + une ligne dans le carnet.

## Ordre de lecture (dans le dossier du skill)
1. **`lecons.md`** : les règles dures apprises sur de vrais reels. Après ton carnet.
2. **`regles-experts.md`** (12 domaines d'experts sourcés). Partie A = à appliquer dans chaque plan ; parties B et C = seulement si l'utilisateur est d'accord. Si un expert contredit ce que l'utilisateur a dit, l'utilisateur gagne.
3. Après le brief : **UNIQUEMENT le fichier du style choisi** (ne pas lire les autres) :

| Style | Fichier |
|---|---|
| Face caméra · sous-titres | `styles/face-cam-soustitres.md` |
| Face caméra · minimaliste | `styles/face-cam-minimaliste.md` |
| Face caméra · high prod | `styles/face-cam-high-prod.md` |
| À plusieurs (podcast, visio, split screen, débat) | `styles/a-plusieurs.md` |
| Voix off | `styles/voix-off.md` |
| Green screen | `styles/green-screen.md` |
| Montage viral (T, mauvais / bien / excellent, tier list) | `styles/montage-viral.md` |
| B-roll + texte | `styles/broll-texte.md` |

4. Étape 8 : `note-10.md`. Modifier un script ou rendu cassé : `moteur.md`.

## 0. BRIEF AVANT TOUT MONTAGE (obligatoire, en boutons QCM via AskUserQuestion, option recommandée en 1er)
Toujours premium. Ne monter qu'après les réponses.
1. **Style** : proposer les 4 styles qui collent au rush (4 boutons max, le reste via « Autre ») parmi Face caméra / À plusieurs / Voix off / Green screen / Montage viral / B-roll + texte. Le montage viral se décide au script (la vidéo doit être écrite pour).
2. **Degré** (face caméra) : option recommandée = celle qui colle à la vidéo.
   - **Sous-titres** → dérush + sous-titres + musique, rien d'autre. Conseil court, volume (beaucoup de reels par semaine).
   - **Minimaliste** → cartons typo mot par mot, icônes au trait, captures + cercle à la main. Explication avec chiffres, preuves, captures.
   - **High prod** → chiffres géants, B-rolls, preuves, CTA. Reel phare. + question **Style** : Sobre / Dynamique.
3. **Référence** (facultatif, 1 bouton) : « Tu as 1 à 3 reels que tu aimes ? » Voir « Références de style » plus bas.
4. **Musique** (la première fois seulement, la réponse va dans le carnet) : « Tu as un compte Epidemic Sound ? » Oui (recommandé) / Non, musique libre de droits / Non, sans musique (je l'ajoute dans l'appli Instagram). Voir la section Musique.
- **Format** : 9:16 seulement, ne pas poser la question. Un rush en 16:9 (hors podcast / visio) : le dire ; si la personne est au centre, recadrage centré `ffmpeg -i rush.mp4 -vf "crop=ih*9/16:ih,scale=1080:1920:flags=lanczos,fps=30" ...` après avoir regardé une image ; sinon redemander un rush en vertical.
- **Images générées** : Higgsfield (si `"higgsfield": true` dans tes réglages, c'est-à-dire un compte Higgsfield branché à Claude ; au 1er montage, vérifie que ses outils sont bien disponibles, puis écris `{"higgsfield": true}` dans `montage.json`), sans demander, SEULEMENT là où le style en prévoit (high prod, green screen, icônes de tier list). Jamais en sous-titres, minimaliste, à plusieurs, voix off ; B-roll + texte : jamais avec un visage. Sans Higgsfield : tes B-rolls, tes photos, Pexels, ou Gemini sur ta clé (`gemini_image.py`, facultatif) ; jamais d'IA qu'on ne peut pas assumer.

## LE PROCESS
1. **Univers = le RUSH.** Regarder le rush d'abord : décor, lumière, couleurs, tenue. Tout ce qu'on ajoute doit sembler filmé dans CETTE pièce (`plan.colors` pour coller). La charte de marque (`da.md`) sert au TOURNAGE et au branding, jamais plaquée au montage sur un rush d'un autre univers.
2. **Illustrations DANS la scène, accrochées aux gestes** (tracking `track.py`) : badge au bout du doigt quand la personne pointe, logos à côté de la tête sur « réseaux », mot derrière la tête. Objets réels = vraie forme et vraie couleur, détourés, éclairés comme la scène. Jamais une scène séparée.
3. **B-rolls = TES vrais plans, BRUTS, STABLES, courts** (1-2,5 s, `broll.py steady` / `"from": "auto"`), jamais de filtre. Peu de temps hors de son plan (~8 s sur 39 s). Preuves = vrais objets (vraie capture de commentaires, vrai profil).
4. **Sous-titres** (verrouillés) : police de la DA (`fonts.sub`, `subSize`, `subTrack` si fournis ; par défaut Montserrat 700, 52 px, espacement 0,5 px) ; **mot fort = serif italique blanc 132 px, SEUL à l'écran** (la phrase s'efface, il arrive seul quand il est dit, jamais de mot normal à côté), groupe de 1 à 3 mots possible ; entrée fondu + petite montée ; hauteur **au niveau du col, jamais sur le cou ni le menton** (`subzone.py` : menton + 0,41 x visage).
5. **Serré, sans gadget** : dérush serré ; REC, bandes noires, mot serif géant : seulement si la vidéo le justifie.
6. **Comparer à la référence avant d'envoyer** (high prod, si l'utilisateur en a donné une) : planches 1 i/s côte à côte + `analyse_ref.py` sur les deux (coupes, débit, SFX sur les coupes ~60 %). Musique seule 15-17 dB sous la voix.

## Références de style (facultatif : 1 à 3 reels que l'utilisateur aime)
L'utilisateur donne un lien ou un fichier. Lien : `yt-dlp` (demande l'OK avant de télécharger : nom, source, durée ; fichier gardé dans `~/Documents/Contenu/medias/references/`, jamais republié ; si le site exige une connexion, un enregistrement d'écran suffit). Puis pour chaque référence :
```bash
python3 $S/analyse_ref.py ref1.mp4 analyse-ref/        # coupes, débit de parole, pauses, niveau de la musique sous la voix, SFX sur les coupes
```
(besoin de `librosa` et de Demucs, voir Dépendances). Résume la recette en 5 lignes (plan moyen, mots/min, musique x dB sous la voix, % de coupes avec SFX, changements de musique) et applique-la à TON montage : **on prend la mécanique (rythme, niveaux), jamais le contenu, le texte, la musique ni les images** (méthode Picasso). Écris la recette dans le carnet. Sans référence, les règles d'experts suffisent.

## Le cahier des charges (non négociable, tous les styles)
- **Zones mortes Instagram** : aucun texte ni élément animé au-dessus de **270 px** (14 %, chiffre officiel Meta Ads Guide Reels), à moins de **65 px** des bords (6 %), sous **1 480 px** (pseudo + légende), et sous-titres entre 120 et 960 px en largeur (boutons à droite). Les fonds / voiles / décors peuvent déborder. Les 35 % du bas de Meta (1 248 px) ne valent que si un reel part en pub. **Contrôle** : `node $S/zones.mjs .` après build (et après `viral.py inject`) = chaque texte (encre réelle) et élément animé, toutes les 0,25 s ; attendu « OK : 0 ». Détail par élément : `moteur.md`.
- Couper silences et répétitions. **Jamais de coupe au milieu d'une phrase.** Enlever la respiration en début de phrase.
- Rush **déjà dérushée** seulement si l'utilisateur le dit ou si aucun blanc > 0.2 s → sauter l'étape 3. Sinon on resserre.
- **Musique TOUJOURS ÉMOTIONNELLE** (tous styles) : motivation, tristesse, nostalgie, espoir… une émotion qu'on SENT (mélodie piano / cordes qui monte). Jamais une nappe neutre, d'ambiance ou de suspense sans mélodie. Sujet grave = piano lent qui monte ; business / tension = **dark cinématique** (orchestral hybride épique sombre, cordes) avec une COUPURE puis une FRAPPE sur la punchline. Le champ `music` de la DA n'est qu'un indice. Jamais de musique non licenciée (voir Musique). SFX minimalistes.
- Police minimaliste : Montserrat (ou la police de ta DA). 2e police pour les mots importants : **serif italique** (Instrument Serif par défaut).
- **Jamais de B-roll juste pour mettre du B-roll**. Par défaut AUCUN. Un B-roll seulement quand il montre ce que la tête ne peut pas montrer (lieu, résultat, objet, action dite à cet instant). Dans le doute : face cam. S'il y en a : peu mais réparti, jamais groupé dans un seul passage.
- **Visuels générés = Higgsfield**, seulement dans les styles qui en prévoient : VIDÉO générée seulement pour un gros moment SANS visage (hook, preuve : Cinema Studio Video 3.0 / Seedance 2.0 / Kling 3.0, ~6 crédits / 5 s), IMAGES animées par le moteur pour le reste (Nano Banana 2 / GPT Image 2, < 1 crédit). **Jamais de plan de la personne généré** : partir d'un de SES vrais B-rolls. Ses vrais plans d'abord, Higgsfield pour ce qu'ils ne peuvent pas montrer. Zéro chrome, zéro néon, zéro glow ; 1 visuel test validé avant le reste. Annoncer les crédits dépensés.
- **Jamais saccadé** : pas de zoom brusque, pas de changements de plan trop rapides. Le moteur ne zoome que lentement (1,4 s) quand l'idée change. **Jamais la tête visible une fraction de seconde entre deux pleins écrans** : enchaînés direct ou >= 1,5 s de face cam (garde-fou anti-flash dans build.mjs, il affiche ce qu'il corrige).
- **Méthode** : AVANT de monter et AVANT chaque modification, montrer le plan (moments, visuels, sons, silence) et attendre l'OK. Sous-titres : 3 lignes suffisent. Corriger par retouches ciblées (remix audio seul, plan.json + re-rendu) au lieu de tout regénérer. **Échantillon d'abord** : pour un nouveau style ou un lot de plus de 3 reels, monter 1 reel, le montrer, attendre l'OK, puis le lot.

## Musique et SFX : d'où ça vient (jamais de téléchargement non licencié)
- **Epidemic Sound (recommandé)** : compte payant sur epidemicsound.com, connecteur à brancher dans Claude (claude.ai → réglages → connecteurs). Le plan « Creator » couvre les réseaux sociaux en organique ; une pub Meta demande un plan supérieur : vérifie ton plan si le reel part en pub. Process : l'ÉMOTION à faire ressortir d'abord (jamais « neutre », « ambiance », « suspense » seul), puis `SearchRecordings` (terme d'émotion, `vocals: false` ; pour coller à un morceau que tu aimes : `SearchExternalReferences` → recherche par id Spotify), présélection 10-15 titres → `EditRecording` à la durée exacte (`forceDuration`, `preferenceRegions` sur le meilleur passage) → `DownloadRecordingEdit` (WAV) dans `~/Documents/Contenu/medias/musique/epidemic/<ambiance>/` avec une ligne dans `musique/_LICENCE.txt` (titre ; source ; licence) → `"fin": "naturelle"` (le morceau finit tout seul, pas de long fondu). Ne pas reprendre la musique du reel précédent.
- **Sans Epidemic** (gratuit) : un morceau libre de droits que **TU** as téléchargé toi-même (bibliothèque audio de YouTube Studio, Pixabay Music…) et déposé dans `~/Documents/Contenu/medias/musique/libre/`. Claude lit la licence de CHAQUE morceau (certains demandent un crédit dans la légende, certains limitent l'usage), la note dans `_LICENCE.txt`, et refuse en cas de doute. Claude coupe le morceau à la durée (`ffmpeg -ss … -t …`, fondu de sortie 1,2 s).
- **Sans musique du tout** : monter sans, et ajouter un son depuis la bibliothèque de l'appli Instagram au moment de publier (vérifie dans l'appli ce que ton type de compte a le droit d'utiliser). Le reste du montage (niveaux, silences) reste valable.
- **Jamais** : musique extraite d'une vidéo, d'un site de streaming ou d'un morceau commercial. Un titre tendance ne se télécharge pas ; il se choisit dans l'appli Instagram.
- **Niveau** : `target` = niveau de la musique SEULE en LUFS sous la voix à -14 (défaut `config.json` → `music_target_lufs` = -29 : à -31 la musique « n'existait pas » sur un morceau contrasté ; elle est aussi resserrée, LRA 6, pour ne jamais disparaître dans ses creux ; `lra: 11` pour garder une coupure voulue). `mix.py` mesure et recale chaque segment. La musique est creusée de -4 dB vers 1,2 kHz (place pour la voix) et s'efface de 5 dB pendant ~1 s sous chaque gros effet (impact, sub drop, plein écran, CTA).
- **Choisir à l'oreille** : dès que la musique est refusée une fois, monter 4 versions A-D de SA vidéo (une musique chacune, toutes calées sur la punchline, même voix), copies légères envoyées ensemble, l'utilisateur répond une lettre. Ou il donne un titre / lien qu'il aime → `SearchExternalReferences` → équivalent Epidemic.
- **SFX** : `config.json` → `sfx` liste les fichiers attendus dans `~/Documents/Contenu/medias/sfx/` (impact, riser, subdrop, whoosh…). Avec Epidemic : `SearchSoundEffects` + `DownloadSoundEffect` (sons sombres cohérents, un seul kit par reel). Sans fichiers : pas de SFX (le degré sous-titres n'en veut de toute façon aucun). Les SFX sont automatiques, seulement sur les gros événements, jamais 2 à moins de 1,5 s.
- **Changement de musique** : quand le sujet, l'ambiance ou le plan change DANS la vidéo, `music` devient une liste de segments `[{"src", "from", "start", "end", "emotion"}, {..., "transition": "douce" | "sec"}]`. Douce = fondu enchaîné 1,5 s ; sec = coupe nette + impact. Un seul sujet du début à la fin → un seul morceau. 2 morceaux max sur 40 s.

## Workflow commun (le fichier du style dit quelles étapes il change)
Un dossier par reel, tout se lance depuis ce dossier.

**1. Caler en 1080×1920, 30 i/s + recadrer si filmée trop large** (automatique ; montage viral : SANS `cadre.py`)
```bash
python3 $S/cadre.py <rush ORIGINALE, 4K> --apply     # ~45 s -> clip.mp4
```
Rush filmé large (yeux sous 40 % ou visage < 28 % de la largeur) → recadrage fixe depuis la 4K : yeux à 35 %, visage à 33 %. Déjà serrée → simple mise au format. Toujours partir du rush ORIGINALE 4K (zoom > 1,10 sur du 1080 = flou ; le script plafonne alors à 1,10). Plan large de scène (conférence, écran géant derrière) : cadrer à la main (`zoompan`) et vérifier `subzone.py` sur le clip recadré. Rush iPhone HDR (HEVC 10 bits, couleurs délavées) : la convertir d'abord en SDR (sur Mac : `avconvert`).

**2. Transcrire** (Whisper local, gratuit ; chaque mot est recalé sur l'énergie de la voix, utile en salle qui résonne)
```bash
python3 $S/transcribe.py clip.mp4 words.json
```

**3. Dérusher** (sauf rush déjà dérushé)
Lire la transcription. Repérer les répétitions et phrases ratées : on garde la **dernière** prise. Les noter en plages d'indices de mots dans `drop.json` (`[[12,18]]`, ou `[]`).
```bash
python3 $S/derush.py clip.mp4 words.json cut.mp4 --drop drop.json
python3 $S/transcribe.py cut.mp4 words.json && mv cut.mp4 clip.mp4      # on retravaille sur la version coupée
```
**Entrée / sortie** : le dérush garde 0,15 s avant le 1er mot et 0,6 s après le dernier (`--lead` / `--tail`). Il écrit aussi `cut.words.json` = la transcription du RUSH recalée sur la version coupée (souvent meilleure qu'une transcription refaite sur le montage coupé) : on peut la prendre au lieu de retranscrire.
Le script ne coupe que dans les blancs entre deux mots : fin de phrase = blanc + respiration supprimés ; milieu de phrase = blanc resserré à 0.15 s. Chaque coupe : micro-fondu son de 0,03 s (anti-clic) et plages calées sur la grille des images (image et son exactement de la même durée, la bouche ne se décale jamais).
**LE silence** (s'il y en a un) : repérer la punchline AVANT le dérush et ajouter `--pause <indice du mot punchline>` : la vraie pause avant ce mot est gardée (jusqu'à 0,9 s). Pas de pause dans le rush = pas de silence (le dire : marquer un temps avant la phrase choc au tournage).

**4. Écrire `plan.json`** en lisant la transcription (c'est là que se joue la qualité). Champs communs (le fichier du style ajoute les siens) :
```json
{
  "cam": "clip.mp4", "words": "words.json",
  "fixes": {"boulettes": "bullet"},
  "keywords": ["dangereux", "illégal", "hook", "succès", "virales"],
  "music": {"src": "~/Documents/Contenu/medias/musique/epidemic/<ambiance>/<titre>.wav", "from": 0, "fin": "naturelle"},
  "silences": [{"to": 8.30}]
}
```
(EXEMPLE FICTIF : mots, titres et chemins viennent du rush et de tes dossiers.)
- **fixes** : relire TOUTE la transcription et corriger les erreurs de Whisper (`{"boulettes": "bullet"}`). Obligatoire : une faute dans un sous-titre = reel raté.
- **keywords** : 6-10 mots forts, ou groupes de 2-3 mots (`"badge bleu"`) → serif italique blanc 132 px, affichés SEULS à l'écran (les petits mots devant restent dans le bloc d'avant). Jamais en couleur.
- **title** : `{"l1": "Le badge bleu", "l2": "une arnaque ?", "start": 0, "end": 4}` = titre-question pendant le hook (petites MAJUSCULES + serif italique, voile sombre, fondu ; `top` pour le placer, ex. 1300 = en bas quand la tête touche le haut du cadre). **Vidéo AVEC titre = ni mot fort ni mot géant ; vidéo SANS titre = mots forts + mots géants derrière la tête.** Avec un titre, `keywords` et `bigwords` sont ignorés sur toute la vidéo (le moteur le dit). Proposer le titre dans le plan de chaque reel (formulé avec les mots de la personne, `voix-contenu.md`).
- **cta** : `{"start", "end", "word": "GUIDE", "count": "1 284", "user": "toi", "comments": [["pseudo", "texte", "2 min"], ...]}` = sur « commente MOT » : vraie feuille de commentaires qui monte du bas, le mot se tape lettre par lettre (clavier qui s'allume), puis se publie en haut de la liste. Le mot vient de `strategie-contenu.md` (une ressource qui EXISTE). Commentaires par défaut = des gens qui tapent le mot (pas de faux témoignages).
- **music** : voir la section Musique. `target` / `lufs` : `lufs` n'est qu'un point de départ, `mix.py` mesure et recale chaque segment.
- **silences** : `[{"to": 8.30}]` = **UN SEUL par reel, et seulement si une punchline le mérite** (sinon aucun). TOUJOURS un riser avant (si le fichier riser existe). C'est une VRAIE pause : voix ET musique coupées ~0,6-0,9 s (gardée au dérush avec `--pause`), puis impact pile sur le mot. `to` = début du mot punchline ; `mix.py` prend la fin du mot d'avant comme début et ABANDONNE le silence si la pause fait < 0,6 s.

**5. Ajouts du style** : voir le fichier du style (B-rolls, images, tableau, source…).

**6. Compo + rendu + son**
```bash
node $S/build.mjs --plan plan.json --out index.html
npx --yes hyperframes@0.6.81 lint                                # 0 erreur (warning "overlap 0 s" sur #camwrap = sans effet)
node $S/zones.mjs .                                              # zones mortes Insta : « OK : 0 » attendu (~3 s)
npx --yes hyperframes@0.6.81 render . -q high                    # ~2 min 30 pour 40 s
python3 $S/mix.py plan.json renders/<x>.mp4 clip.mp4 final.mp4   # voix (voice_lufs, -14) + musique recalée par morceau + SFX auto
```
(High prod : `matte.py` avant le build, voir son fichier.)
**Son de salle** (conférence, micro de scène capté par la caméra) : `python3 $S/voix_propre.py clip.mp4 voix/doux.wav words.json` = ta voix ORIGINALE + EQ douce vers ta voix studio (`config.voice_ref` : un enregistrement de ta voix en studio, 30 s à 1 min ; sans lui, EQ générique), ±3,5 dB max. La version forte (`--fort`, Demucs + expandeur + exciteur) rend la voix « bizarre et déformée » : seulement avec l'accord de l'utilisateur. Puis `mix.py ... voix/doux.wav final.mp4`.
**Couleur** (seulement si l'utilisateur le demande) : 2 options légères en avant / après sur 2 images AVANT de rendre (`couleur/avant-apres.jpg`), filtres `ffmpeg` doux (`eq`, `colorbalance`), noirs P1 1-8 vérifiés (`lookstats.py`), puis `ffmpeg -vf "…"` sur clip.mp4 → clip_grade.mp4 = `plan.cam`. Jamais de LUT créative.
**Écran noir au départ** : corrigé dans mix.py (la vidéo commençait à 0,021 s, QuickTime / iPhone / Instagram n'avaient aucune image à 0 s). Contrôle : ffprobe `start_time` = 0.

**7. Vérifier (obligatoire avant de dire "c'est fait")**
```bash
ffprobe -v error -show_entries stream=codec_name,width,height,pix_fmt,start_time -of compact final.mp4   # h264 1080x1920 yuv420p + aac, start_time 0
ffmpeg -y -v error -i final.mp4 -vf "fps=2,scale=150:-1,tile=10x8" -frames:v 1 check.jpg
ffmpeg -i final.mp4 -af ebur128 -f null - 2>&1 | grep " I:" | tail -1     # final ~ -14 LUFS
```
`mix.py` mesure CHAQUE morceau sous la voix et le recale tout seul sur sa cible (`target`, défaut -29) à ±1 LU ; il affiche une ligne par morceau (OK / trop fort / TROP BAS) puis « final : -14 LUFS, crête vraie ≤ -2 dBTP ». Pour un CTA plus calme : `"target": -33` sur le dernier segment. **Mesurer la musique SEULE dans le final** (Demucs si installé) : 15-17 dB sous la voix, sinon on ne l'entend pas.
Regarder `check.jpg` : un seul bloc de sous-titre à la fois, tête devant chaque chiffre, listes lisibles, B-rolls répartis régulièrement, pas de visage coupé. Échec → corriger, refaire.

**8. Note /10** : `note-10.md` (obligatoire).

**9. Boucle feedback (après chaque reel)**
1. Retours = **Cut Notes** : envoyer un lien où l'utilisateur tape ses notes accrochées à l'image exacte. Process : `outils/cut-notes/CUT-NOTES.md` (1 artifact par vidéo, URL dans `cut-notes.url` du dossier du reel ; « done » = lire les notes, corriger, répondre sous chaque note, round suivant). « done » avec 0 note ≠ validé : demander en une ligne s'il a laissé des retours. Sans artifact : l'utilisateur dit ses retours dans le chat.
2. Corriger le reel (retouches ciblées).
3. Chaque retour ou note (« 6/10, musique trop forte ») = **une ligne datée dans le carnet** `~/Documents/Brain/00-Moi/regles-agents/supermonteur.md`. Si la règle change une règle de ce skill, corriger le fichier concerné (SKILL.md, `lecons.md` ou le fichier du style) pour qu'il n'y ait jamais deux versions. Une erreur corrigée ne revient jamais.
4. Reel validé : le programmer = skill `publieur` (ce skill ne publie jamais). Une ligne dans `~/Documents/Brain/log.md` si le montage change l'état actuel (nouveau style adopté, règle durable).

## Outils annexes (dans `outils/`)
- **`style-lab/`** : choisir TA DA de montage (polices, couleur, musique, rythme, ambiance) en un tour de votes sur de vrais rendus de toi. Facultatif. `STYLE-LAB.md`.
- **`cut-notes/`** : la page de retours image par image. `CUT-NOTES.md`.
- **`indexer-brolls/`** : indexe ton dossier de B-rolls (durée, format, date automatiques ; Claude regarde les planches et décrit chaque plan) pour que `broll.py search` trouve « le bon plan ». `python3 ~/.claude/skills/supermonteur/outils/indexer-brolls/indexer.py scan`.
- **`extraire-brolls/`** : sortir les passages stables de longues rushes (voyage, bureau) vers ta bibliothèque. `README.md`.

## Dépendances (le setup les vérifie)
Mac : `brew install ffmpeg node` puis `pip3 install --user numpy pillow faster-whisper mediapipe onnxruntime`. HyperFrames et son Chrome de rendu se téléchargent tout seuls via `npx` (Internet requis la 1re fois). Détourage (high prod, green screen) : modèle RobustVideoMatting téléchargé par `setup.sh`. Facultatif : `pip3 install --user demucs librosa opencv-python` (contrôle de la musique seule, analyse de références, extraction de B-rolls) et `brew install yt-dlp` (références par lien).

En cas d'échec (outil absent, rendu cassé) : une ligne dans `~/Documents/Brain/04-Audits/erreurs-taches.md` (date, tâche, erreur) et dis-le en une ligne.
