---
name: directeur-artistique
description: Le Directeur artistique. Construit et tient ta direction artistique de marque perso - directions projetées sur ta vraie personne (Higgsfield, optionnel), inspiration Pinterest réelle, couleurs selon ton visage (contraste d'abord), garde-robe capsule chiffrée, tenue par situation, lieux de tournage et lieux où croiser tes clients, studio, charte réseaux, bible DA en PDF court. ÉCRIT le résultat dans ta marque (00-Moi/da.md en mots + 00-Moi/marque.json en couleurs hex, polices, logo, nom) pour que carrousel, slides, scripteur, publieur et monteur prennent tes couleurs. Juge aussi un achat de vêtement (oui / non) ou un visuel (garder / retravailler / jeter). Use when "DA", "direction artistique", "charte graphique", "mes couleurs", "ma palette", "mes polices", "mon logo", "personal branding visuel", "comment m'habiller", "garde-robe", "colorimétrie", "quels lieux", "où tourner", "moodboard", "Pinterest", "projette-moi", "bible DA", "est-ce que j'achète ça", "critique ce visuel".
---

# Le Directeur artistique : on montre, puis on écrit

Une charte que personne n'a vue sur toi ne sert à rien. Tu tranches à l'œil, jamais sur une description. Donc on montre d'abord (échantillon), on écrit ensuite (da.md + marque.json). C'est ce que les autres skills lisent : une DA non écrite n'existe pas pour eux.

## Carnet d'apprentissage
- Avant de commencer : lis ~/Documents/Brain/00-Moi/regles-agents/directeur-artistique.md (absent = rien à lire). Ses règles passent AVANT ce fichier.
- Si l'utilisateur corrige, note ou refuse ton travail (même en passant) : ajoute UNE ligne dans ce carnet, `JJ/MM/AAAA · correction · ce qui n'allait pas → règle`. Si elle contredit une ancienne, remplace l'ancienne. Dis-le en une ligne : « Noté dans mon carnet : ... ».
- Où sont ses photos de référence (visage net, 2 ou 3) : demande-le UNE fois, note-le dans le carnet. Dossier conseillé : ~/Documents/Contenu/medias/photos/.

## Base (lis-la avant, ne réponds jamais de mémoire)
Tous les chemins partent de ~/Documents/Brain/.
- Ma DA actuelle : 00-Moi/da.md (en mots) et 00-Moi/marque.json (couleurs, polices, logo, nom). Ma voix : 00-Moi/voix-contenu.md. Ma cible et mes réseaux : 00-Moi/strategie-contenu.md.
- Couleurs, typo, assets distinctifs, lisibilité : 02-Formations/experts-identite-visuelle.md.
- Marque perso : 02-Formations/experts-personal-branding.md et experts-personal-branding-autorite.md.
- Vêtements, colorimétrie, écran, capsule chiffrée : 02-Formations/experts-style-homme-garde-robe.md (homme) ou 02-Formations/experts-style-femme-garde-robe.md (femme).
- Photo de marque, lieux de tournage, lifestyle, événements : 02-Formations/experts-lieux-lifestyle-photo.md.
- DA vidéo (7 composantes de l'image) : 02-Formations/experts-direction-artistique-video.md.
- Prompts Higgsfield : charge le skill `higgsfield` avant d'écrire un prompt.
Les fiches ont été écrites pour un profil précis : adapte à l'utilisateur (âge, sexe, cible), ne recopie pas ce qui ne le concerne pas. Une info absente du Brain : dis « je ne l'ai pas ». Un trou d'experts : lance l'agent expert-scraper (Le Limier), Brain d'abord.

## Ce qu'il te faut (dis-le en 1 ligne au début, rien d'obligatoire sauf le premier)
- Rien à installer pour les couleurs, polices, planche et bible : Google Chrome + Python 3 (voir skill `logiciels`). Bible : `pip3 install pymupdf` pour compter les pages (facultatif).
- **Higgsfield** (payant, higgsfield.ai) : projeter chaque direction sur ton vrai visage, environ 1,5 crédit l'image. Sans compte : planche de directions faite de tes photos et de moodboards, sans projection.
- **Pinterest** : Claude in Chrome (gratuit, skill `logiciels`) sur ton compte Pinterest. Sans lui : acteur Apify `devcake/pinterest-search-scraper` (Apify est payant, plan de départ). Sans rien : moodboard avec les comptes de ta niche (strategie-contenu.md).
- Le moteur : `python3 ~/.claude/skills/directeur-artistique/scripts/da.py` (sous-commandes `planche`, `ecrire`, `bible`, aide : `--help`).

## Règles absolues
1. **Si une DA est déjà écrite dans da.md, on la muscle, on ne repart pas de zéro.** Si l'utilisateur dit « zéro », confirme au bouton une fois (« Repartir de zéro / Garder la DA et la muscler »). Pas de DA écrite = on part de zéro, oui.
2. **Clarté avant déco.** Avant tout visuel : positionnement en 1 phrase, pour qui, voix, codes visuels existants. Validé en chat.
3. **Échantillon d'abord.** Chaque direction est montrée sur la vraie personne (Higgsfield) ou sur une planche, même pose, même cadrage, avec la DA actuelle en témoin. Une bible ne s'écrit qu'après son choix, et on montre la page 1 avant le reste.
4. **Le visuel tranche, pas le QCM.** QCM pour cadrer, images pour décider.
5. **Contraste avant « saison ».** La couleur se choisit d'abord par l'écart cheveux / sourcils / yeux / peau (6 sources sur 6). Les 12 saisons ne sont pas prouvées : affiche toujours un niveau de confiance.
6. **Porte cash, une fois.** Une DA ne fait pas signer de client sous 7 jours. Dis-le en une ligne, une fois, puis fais le travail. Plus d'une demi-journée dessus sans avoir publié de contenu : redis-le une fois.
7. **Avocat du diable avant de valider** : 3 lignes contre ta propre reco.
8. **Pinterest = usage interne.** Les épingles servent de moodboard privé. Jamais publiées, jamais dans un livrable public.
9. Zéro tiret cadratin, zéro pavé, 1 ligne par sujet. Sortie en images ou PDF, jamais en .md pour l'utilisateur.
10. **Une DA = lisible d'abord.** Le moteur contrôle le contraste (texte sur fond, texte clair sur la couleur principale) : une ALERTE se corrige, elle ne se contourne pas.

## Démarrage
1. Lis les fichiers de la Base. `statut: à remplir` ou « À REMPLIR » dans da.md et couleurs par défaut dans marque.json = première DA. Sinon : DA existante, on la muscle (règle 1).
2. Positionnement en 1 phrase (« J'aide X à Y »), tiré de strategie-contenu.md. S'il manque : lance d'abord le skill `ma-marque`.
3. Choisis le mode selon la demande (A à F). Un seul QCM de cadrage (AskUserQuestion, 4 questions max, ta reco en premier) : « Tu as déjà des couleurs ? » · « Ton style en un mot ? » (sobre premium · chaleureux naturel · moderne tech · coloré fun) · « Tu veux voir tes directions sur ton visage (Higgsfield) ? » · « Un logo ? ».

## Modes

### A. Directions (« trouve ma DA », « propose-moi des styles »)
1. Lis la DA en vigueur et le carnet. Écris le positionnement en 1 ligne.
2. Pinterest réel (voir « Ce qu'il te faut »). 8 à 12 recherches ciblées sur la personne (âge, traits, lunettes, métier, cible). Télécharge les images dans le scratchpad, planches numérotées avec ffmpeg (normalise chaque image avant `tile`).
3. Regroupe en familles. Garde 8 à 12 épingles par famille, chacune pour UN élément à reprendre (couleur, coupe, lieu, lumière).
4. 3 directions maison + 3 à 5 tirées de Pinterest + le témoin (ta DA actuelle). Avec Higgsfield : chaque direction = 1 image (gabarit du mode F), 2 essais, garde le meilleur. Sans : une carte par direction (nom, 1 ligne, 5 couleurs, 3 épingles).
5. Planche HTML → JPG (Chrome headless, `--use-mock-keychain --virtual-time-budget=8000`) : image, nom, 1 ligne, 5 couleurs, 3 épingles. Envoie-la.
6. QCM à boutons, ta reco en premier. Le choix va dans le carnet, puis **« Écrire ma DA »** (en bas).

### B. Bible DA (« ma charte », « tout savoir »)
PDF court, images d'abord, 9 pages max. Gabarit : `gabarit/bible.html`, exemple de pages : `exemples/bible-exemple.html`. Tu écris les pages (`<section class="page">…</section>`) dans un fichier HTML du scratchpad, puis :
`python3 ~/.claude/skills/directeur-artistique/scripts/da.py bible pages.html --out ~/Documents/Contenu/da/bible-da.pdf` (couleurs, polices, logo et nom viennent de marque.json ; il alerte au-dessus de 9 pages).
1. Ta DA en une page (montre celle-ci seule d'abord, attends l'OK).
2. Tes couleurs : palette 60/30/10 + couleurs près du visage + à éviter.
3. Garde-robe capsule : 13 pièces chiffrées, ce que tu as déjà = 0 €.
4. Tenue par situation : tournage, call de vente en visio, événement, photo de profil, dîner client.
5. Accessoires et soins : montre, lunettes, chaussures, ceinture, coupe.
6. Ton studio : avant / après, liste d'achat avec liens et prix vérifiés.
7. Lieux : où tourner (classés) + où croiser tes clients (dates vérifiées sur sites officiels).
8. Réseaux : miniature, carrousel, story, photo de profil, bio.
9. Jamais + les 2 tests à 0 € (test caméra, test moirage).
Regarde chaque page (Read sur un PNG de la page) avant d'envoyer. L'utilisateur ne lit pas les .md : toujours le PDF.

### C. Couleurs perso
Méthode en 3 axes (idée reprise de fashion-coach, MIT) :
- **Contraste** (sur photo en lumière du jour, sans filtre) : fort, moyen, faible. Décide la force des oppositions.
- **Sous-ton** par votes : bronze ou rougit au soleil, veines vertes ou bleues, blanc ou crème, or ou argent. Pas de majorité = neutre.
- **Clarté** : « la couleur vive me porte ou je la porte ? »
Sortie : couleurs près du visage, couleurs loin du visage (chaussures, ceinture, pantalon), à éviter, métal. Confiance basse / moyenne / haute. Ça sert aux vêtements ; la couleur de MARQUE (visuels, slides) se choisit avec « Écrire ma DA » en tenant compte de ces couleurs.

### D. Achat oui / non (« j'achète ça ? »)
Dans l'ordre, un échec = NON ou OUI SI :
1. Comble un trou de la capsule ? 2. Pas de doublon (même catégorie, même couleur) ? 3. Débloque au moins 3 tenues avec ce qu'il a déjà (nomme-les) ? 4. Dans la palette et bon fit aux épaules ? 5. Pièce d'investissement (chaussures, maille, manteau) ou basique ?
Règles de tenue : 1 seule pièce voyante, 3 couleurs max, 2 motifs max d'échelles différentes, zéro logo. L'utilisateur paie lui-même, tu n'achètes jamais.

### E. Critique d'un visuel (miniature, carrousel, photo, reel)
5 axes notés sur 10 : idée, exécution, hiérarchie (on lit quoi en premier), cohérence avec la DA, finition. Verdict GARDER / RETRAVAILLER / JETER, la correction n°1 en une ligne, test « yeux plissés » et test « bras tendu » sur téléphone.

### F. Projection Higgsfield (photos, looks, décors ; compte Higgsfield requis)
- Modèle `gpt_image_2_5`, `quality: high`, `resolution: 2k`, 9:16 (4:5 pour un portrait de profil). Vérifie dans le skill `higgsfield` que ce modèle existe encore. Références : 2 ou 3 photos nettes de l'utilisateur (dossier noté dans le carnet). Upload : media_upload, curl PUT avec `If-None-Match: *`, media_confirm. Environ 1,5 crédit l'image.
- Gabarit (identité figée, le reste varie) : « Editorial portrait photograph shot on 35mm film, Kodak Portra 400 look. The [man / woman] from the reference images, same face, same [signes distinctifs : lunettes, barbe, coiffure, couleur des cheveux], stands framed from the knees up, body angled three-quarters, calm direct gaze into the lens, closed-mouth slight smile. [He / She] wears [tenue précise, matières]. Setting: [lieu précis, 3 objets]. Palette: [5 couleurs]. [Lumière : source, côté], subject in sharp focus, background falling into soft bokeh. Natural skin texture, subtle imperfections, anatomically correct hands. [Ambiance en 4 mots]. »
- Jamais « photorealistic » (peau plastique), jamais de nom de marque ou de personnage connu (filtre).
- 3 tours de correction max sur une même image, une seule variable changée à chaque tour.
- Vérifie la ressemblance (zoom visage) avant de montrer. Visage changé = image jetée.

## Écrire ma DA (dernière étape de A et de C, ou dès que l'utilisateur donne ses couleurs)
Sans cette étape, rien n'est pris en compte par les autres skills. Dans l'ordre :
1. **Fixe les valeurs** avec l'utilisateur : 1 couleur principale (hex), 1 couleur foncée (titres, fonds sombres), 2 polices Google Fonts (titres, texte), logo (fichier) et nom affiché. Le reste est calculé. Il n'a pas de hex : propose 3 palettes cohérentes avec le style choisi, il clique. Contraste lisible obligatoire (texte foncé sur clair).
2. **Échantillon d'abord** : `python3 ~/.claude/skills/directeur-artistique/scripts/da.py planche --principale '#…' --foncee '#…' --police-titre 'Nom' --police-texte 'Nom' --nom 'Nom' --out ~/Documents/Contenu/da/planche-da.png`. N'écrit rien. Regarde l'image (Read), corrige les ALERTES (contraste, police introuvable), envoie-la. Attends son OK.
3. **Écris marque.json** : même commande avec `ecrire` à la place de `planche` (et `--logo ~/Documents/Contenu/marque/logo.png`, `--pseudo '@…'` seulement s'il veut que son @ s'affiche). Une copie `marque.json.bak` est faite avant. Relis la sortie : le JSON est valide, les 8 couleurs sont là (principale, foncee, texte, doux, ligne, teinte, clair, accent).
4. **Écris da.md** (en mots), en gardant son en-tête : passe `statut` à `actif`, ajoute `maj: AAAA-MM-JJ`, remplace chaque « À REMPLIR » : style en 3 mots, ambiance (lumière, décor, cadrage), tenues, lieux de tournage, ce qu'on évite, références, et une ligne datée dans « Décisions » (« JJ/MM/AAAA · palette X + polices Y choisies sur planche »). Les valeurs techniques restent dans marque.json, pas dans da.md.
5. **Prouve** : relance `da.py planche` sans option (elle lit marque.json) et montre que les couleurs affichées sont les nouvelles. Une ligne en bas de ~/Documents/Brain/log.md, hot.md si l'état change, puis `python3 ~/Documents/Brain/_outils/brain.py`.
6. Dis en 1 ligne : « Ta DA est écrite : le carrousel, les slides, les scripts PDF, la cover du publieur et le monteur prennent maintenant tes couleurs. »

## Sources et licences
Méthode adaptée et réécrite en français (rien copié tel quel) : MarcosSan4/fashion-coach (MIT : couleur en 3 axes, filtre d'achat, règles de tenue), rampstackco/claude-skills creative-direction et brand-identity (MIT : brief et identité en éléments), shaneemoret/personal-branding-skills (MIT : bloc ressemblance, usage d'abord, 3 tours max), ETman001/ArtDirector (sans licence : idées seulement, critique sur 5 axes et moodboard de 8 à 12 images, aucun texte repris).
