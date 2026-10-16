---
name: publieur
description: Le Publieur. Prend tes reels déjà montés et les programme sur tes réseaux via Metricool (ton Instagram pro en Reel, Facebook Reels, YouTube Shorts, TikTok) - une fiche par reel (légende avec le mot-clé en 1re ligne, CTA unique, 1er commentaire, texte alternatif, titre YouTube, légende TikTok, heure), une cover tirée de tes vrais B-rolls (retouchée avec Higgsfield à ta DA si tu as un compte, visage intact), des contrôles automatiques, puis la semaine sur une page et un seul OK, et l'archive des vidéos publiées. Ne publie jamais sans ce OK, jamais sur un compte qui n'est pas dans ta fiche strategie-contenu.md, ne répond jamais aux commentaires. Use when "publie", "publication", "programme mes reels", "programme la semaine", "poste mes vidéos", "go semaine", "semaine de publication", "cover de reel", "légende", "Metricool", "publieur", "mets en ligne".
---

# Le Publieur : reels montés → programmés sur tes réseaux, un seul OK

Chaîne vidéo : veille-reels → scripteur → tournage → supermonteur → **publieur**. Le bouchon de beaucoup de créateurs, c'est publier régulièrement. Ce skill fait tout, sauf le OK.

**Règle d'or : rien ne part sans le OK explicite de l'utilisateur sur la page de la semaine.** Un OK vaut pour cette semaine-là, pas pour la suivante.

```bash
P=~/.claude/skills/publieur/scripts
```
Durée à annoncer : ~5 min par reel (dont ~1 min de retouche Higgsfield si tu en as), ~30 min pour 7 reels. Coût : ~4 crédits Higgsfield par cover (plafond 8, essais compris), 0 sans Higgsfield.

## Ce qu'il te faut (dis-le en 1 ligne au premier lancement)
- **Metricool** (metricool.com), qui programme réellement les posts. Plan gratuit : 1 marque, 20 posts par mois dans le planificateur, 1 profil par réseau, LinkedIn et X non inclus (source : help.metricool.com, vérifie la page tarifs avant de t'engager). Ce skill crée **3 posts par reel** (Instagram + Facebook, TikTok, YouTube) : en gratuit, commence par 1 ou 2 réseaux, ou prends un plan payant (sans plafond mensuel, prix sur metricool.com/pricing). À faire toi-même : créer le compte, brancher ton Instagram PRO (relié à une Page Facebook), ta chaîne YouTube, ton TikTok, ta Page Facebook (Connexions), puis le connecteur Metricool dans Claude (claude.ai → réglages → connecteurs). Vérifie en appelant `getBrandSettings`, jamais de mémoire. Si Metricool répond une erreur de plan : on prépare les fiches, tu programmes à la main dans le planificateur (légendes prêtes à copier).
- **Une adresse publique pour la vidéo** : Metricool la télécharge depuis un lien. Deux chemins : l'hébergement de **Higgsfield** (testé, 0 crédit, compte Higgsfield) ou un lien **Google Drive / Dropbox** (Metricool l'accepte ; pour Drive, relier Google Drive dans Metricool). Aucun des deux : fiches seulement, tu glisses la vidéo toi-même dans le planificateur.
- **Higgsfield** (payant, facultatif, higgsfield.ai) : retoucher la cover à ta DA. Sans compte : la cover est ta photo B-roll étalonnée aux couleurs de ta marque (`--etalonner`), on te le dit.
- **ffmpeg** (préparer la vidéo : `brew install ffmpeg`), **Google Chrome**, **Python 3 avec Pillow** (`pip3 install pillow`) : skill `logiciels` si besoin.

## 0. Avant tout
1. Lis le carnet `~/Documents/Brain/00-Moi/regles-agents/publieur.md` (absent = premier lancement). Ses règles passent AVANT ce fichier. Sa section « Réglages » contient les choix demandés une seule fois, une ligne chacun : `archive : <dossier>`, `brolls : <dossier>`, `marque Metricool : <nom>`, `Higgsfield : oui ou non`. Une correction de l'utilisateur (même en passant) = 1 ligne `JJ/MM/AAAA · correction · problème → règle`, et dis-le en 1 ligne.
2. Lis `~/Documents/Brain/00-Moi/voix-contenu.md` et `strategie-contenu.md` (réseaux, comptes, CTA, freebies, volume). « À REMPLIR » dedans : lance d'abord `ma-marque`. La section « Réseaux et volume » doit lister **le compte de chaque réseau** (`Comptes : instagram @…, tiktok @…, youtube <nom de la chaîne>`). Manque : demande-les UNE fois (boutons) et écris-les là.
3. **Garde-fou comptes.** Appelle `getBrandSettings`. Pour chaque réseau branché dans la marque Metricool, le compte doit figurer dans `strategie-contenu.md`. **Jamais de publication sur un compte qui n'y est pas listé** (compte perso, ancien compte, compte d'un tiers) : on ne programme rien sur ce réseau et on le dit en 1 ligne avec l'action Metricool (déconnecter le compte, ou l'ajouter à strategie-contenu.md si c'est bien le tien). Plusieurs marques : bouton pour choisir, noté dans le carnet. Pas d'`instagramData` (compte pro) : fiches seulement.
4. Règles TikTok et YouTube Shorts (durée, légende, mots-clés, republier le même reel) : `~/Documents/Brain/02-Formations/experts-algo-tiktok-shorts.md`.
5. Règles de légende : `~/Documents/Brain/02-Formations/experts-legendes-instagram.md` (ou `regles-legendes.md` de ce skill si le Brain est absent).
6. Bilan des passages précédents (à chaque lancement) : voir § 7.

## 1. Quels reels
- Registre : `~/Documents/Brain/06-Contenu/publications.md` (1 ligne par reel : `AAAA-MM-JJ · titre · statut · lien du planificateur`, à créer s'il n'existe pas). Une vidéo déjà au registre ne repart jamais.
- Candidats : les `final.mp4` des dossiers `~/Documents/Contenu/montages/AAAA-MM-JJ-<sujet>/` absents du registre, du plus ancien au plus récent. Exclus : les dossiers ou fichiers `test`, les comparatifs. Le OK sur la semaine vaut validation du montage.
- Nombre : le volume de `strategie-contenu.md` (reels par semaine). Pas assez de reels montés : dis combien manquent en 1 ligne, c'est là que ta portée dort.
- Matière de chaque reel : la transcription du dossier de montage (`words.json` ou `cut.words.json`) et, s'il existe, le script du Scripteur (`~/Documents/Contenu/scripts/`) pour le mot-clé et le CTA. **Rien d'inventé** : la légende ne promet que ce que la vidéo dit.

## 2. La fiche (`fiche.json`)
Dossier : `~/Documents/Contenu/publications/<AAAA-MM-JJ>-<slug>/` (date de publication prévue). Exemple fictif : `exemples/fiche-exemple.json`.
```json
{"titre": "Titre du reel", "video": "/chemin/final.mp4", "duree": 49,
 "date": "2027-01-04T20:00:00", "heure_provisoire": true, "note_heure": "Heure provisoire : ...",
 "plateformes": ["instagram", "facebook", "youtube", "tiktok"],
 "mot_cle": "agenda vide", "dit_a_voix": true, "sur_cover": true, "cta": "GUIDE",
 "cover": {"source": "broll", "retouche": "higgsfield", "photo": "...", "titre": "AGENDA VIDE", "sous_titre": "3 erreurs"},
 "instagram": {"type": "REEL", "legende": "...", "premier_commentaire": "...", "alt": "..."},
 "youtube": {"titre": "...", "description": "..."},
 "tiktok": {"legende": "..."}}
```
`retouche` = `higgsfield` ou `aucune`. Comment l'écrire :
- **Mot-clé** : 1 principal (ce que ta cible tape : « trouver des clients », « agenda vide »). En 1re ligne de légende, dit à voix haute (vérifie dans la transcription), écrit sur la cover. Règles 6 à 10 de la fiche experts.
- **Légende Instagram + Facebook** : ligne 1 = mot-clé + promesse. 1 à 2 lignes de valeur tirées de la vidéo. Le CTA (une seule fois). 0 à 3 hashtags ciblés (5 max officiel).
- **CTA** : celui du script. Sinon le CTA principal de `strategie-contenu.md`. Un mot-clé freebie seulement s'il existe vraiment dans `strategie-contenu.md` ET que ta réponse automatique aux commentaires (ManyChat ou autre) répond ; dans le doute, le CTA principal, et alerte dans la fiche.
- **1er commentaire** : une question ouverte sur le sujet, postée par l'utilisateur lui-même.
- **Texte alternatif** : ce qu'on voit vraiment dans la vidéo.
- **YouTube Shorts** : titre de 100 caractères max (mot-clé + bénéfice), description d'1 ou 2 lignes + l'appel à commenter le mot-clé.
- **TikTok** : 1 phrase + 1 question + 3 hashtags.
- **Trial reel** : jamais par défaut. Seulement pour reposter un reel GAGNANT de plus d'1 mois, avec 2 éléments changés, 5 par jour max (`02-Formations/experts-volume-frequence.md`).
- Voix de `voix-contenu.md` (tu ou vous, ton, lignes rouges). Dernière passe : skill `anti-ia` (pas de tiret cadratin, pas de « ce n'est pas X, c'est Y », pas de triade forcée).

## 3. La cover : une photo de tes B-rolls, pas une image de la vidéo
1. `python3 -E $P/broll.py --mots "4 à 6 mots du sujet" --out <dossier>/broll` (dossier B-roll du carnet, sinon `~/Documents/Contenu/medias/brolls`, option `--dossier`). Les mots sont cherchés dans les noms de fichiers et de dossiers ; sans correspondance, il montre un échantillon récent. Puis **regarde** `planche.jpg` (Read). Choisis la photo qui raconte le sujet (ex. sujet « formats vidéo » : la personne en train de se filmer), visage net, du bas libre pour le texte, tenue et lieu proches de ta DA (`da.md`). Aucun B-roll : dis-le, pas de cover au hasard.
2. **Avec Higgsfield** (outils chargés en retard : refais un ToolSearch avant de dire que c'est bloqué) : `media_upload` → `curl -X PUT -H "Content-Type: image/png" -H "If-None-Match: *" --data-binary @photo` → `media_confirm` → `generate_image` avec `nano_banana_2`, `aspect_ratio 9:16`, `resolution 2k`, `count 2`, la photo en `image_references`, et CE prompt (ne le réécris pas, adapte seulement les crochets) :
   > Edit this exact photo. Keep the same [man / woman], same face and identity, same expression, same pose and hands, same [vêtement de la photo], same framing[, and the same objet du premier plan]. Change only the color grade and the light: [AMBIANCE de da.md en anglais : lumière, contraste, décor], [murs et ombres teintés de la couleur de marine/foncée de marque.json, par son NOM, pas son hex], [source de lumière et chaleur], natural skin tones, slightly richer contrast, crisp eyes, subtle 35mm film grain. Light polish only: even skin that keeps its real texture, calmer background. Natural photograph, true-to-life face, no text.
3. `jobs_wait`, télécharge les 2 versions, compare-les à l'original **visage recadré côte à côte** (Read). Visage changé = jeté. Garde la plus fidèle à ta DA.
4. `python3 -E $P/cover.py --photo retouche.png --titre "AGENDA VIDE" --sous-titre "3 erreurs" --out <dossier>` : titre en 2 à 4 mots avec le mot-clé. **Sans Higgsfield** : même commande avec la photo B-roll brute et `--etalonner`. Puis regarde `grille.jpg` : texte et visage entiers dans le carré 3:4. Si le texte mange le visage : `--haut` (zone visible y 240 à 1680). Polices et couleurs = `marque.json`.

## 4. L'heure
- Volume de `strategie-contenu.md`, 1 reel par jour maximum. `getBestTimeToPostByNetwork` (instagram, la semaine à venir, fuseau de `getBrandSettings`) : l'heure la plus forte de chaque jour.
- Pas assez de données (compte récent) : 20 h (plateau 17 h à 21 h, hypothèse à tester) et `heure_provisoire: true`. Tester 2 ou 3 créneaux, pas 10.

## 5. Validation : la semaine sur une page, un seul OK
1. `python3 -E $P/controle.py <dossier>/fiche.json` pour chaque reel. Un ✗ = tu corriges toi-même avant de montrer.
2. `python3 -E $P/fiche.py fiche <dossier>/fiche.json --out <dossier>/fiche.png` (détail) puis `python3 -E $P/fiche.py semaine <les fiche.json> --out ~/Documents/Contenu/publications/semaine-<AAAA-MM-JJ>.png`.
3. Regarde les images toi-même (Read) avant de les envoyer. Puis envoie la page semaine (SendUserFile si disponible, sinon `open`) et AskUserQuestion : « Je programme la semaine ? » → « Go, programme tout (Recommandé) » / « À corriger ». Les fiches détaillées sont dans chaque dossier.
4. Correction → carnet + on refait seulement la fiche concernée, puis on remontre la page semaine.

## 6. Programmer (après le OK, jamais avant)
1. `$P/prep_video.sh final.mp4 <dossier>/reel.mp4` (1080x1920, contrôle 9:16, 3 s à 15 min, 500 Mo max).
2. **Adresse publique de la vidéo et de la cover** :
   - Higgsfield (testé, 0 crédit) : `media_upload` avec `files` = reel.mp4 (video/mp4) + cover.png (image/png) → `curl -X PUT -H "Content-Type: ..." -H "If-None-Match: *" --data-binary @fichier '<upload_url>'` (HTTP 200) → `media_confirm` (type video / image) → les `url`. Vérifie `curl -sI <url>` = 200 avant Metricool.
   - Sans Higgsfield : un lien Google Drive ou Dropbox partagé que l'utilisateur te donne (Metricool le récupère ; Drive relié dans Metricool). La cover doit être un jpg, jpeg ou png.
3. `createScheduledPost`, `blogId` = id de la marque (`getBrandSettings`), `publicationDate {dateTime, timezone}` (fuseau de la marque), `autoPublish: true`, `draft: false`. **3 posts par reel** (textes différents), seulement pour les réseaux de `plateformes` dont le compte passe le garde-fou :
   - A. Instagram + Facebook : `text` = légende, `firstCommentText`, `media` [url vidéo], `videoThumbnailUrl` url cover, `mediaAltText` [alt], `instagramData {type: "REEL", showReelOnFeed: true}`, `facebookData {type: "REEL", title: titre}`.
   - B. TikTok : `text` = légende TikTok, `tiktokData {privacyOption: "PUBLIC_TO_EVERYONE"}`, `videoThumbnailUrl` (ignoré si compte TikTok perso).
   - C. YouTube : `text` = description, `youtubeData {title, type: "short", privacy: "public", madeForKids: false}`, `videoThumbnailUrl` ; erreur `VIDEO_THUMBNAIL_NOT_APPLICABLE` → refais SANS la cover (chaîne pas vérifiée).
   - La vidéo contient des images ou une voix générées par IA (B-rolls IA, voix clonée) : ajoute `isAiGenerated: true` (instagramData), `isAiGeneratedContent: true` (youtubeData), `isAigc: true` (tiktokData).
4. **Premier passage ever** : programme UN seul reel, `getScheduledPosts` pour vérifier réseau, heure, légende, cover, montre le `plannerUrl` à l'utilisateur, note le résultat dans le carnet, puis le reste.
5. Preuve de fin : `getScheduledPosts` sur la semaine → nombre de posts = 3 × reels (ou moins si moins de réseaux). Registre mis à jour (statut « programmé », date, plannerUrl), 1 ligne dans `~/Documents/Brain/log.md`.
6. Rappel en 1 ligne : répondre soi-même aux commentaires les 7 premiers jours (FAQ Instagram : ça aide la portée) ; ceux qui ont écrit le mot-clé reçoivent la ressource par ta réponse automatique, sinon tu leur réponds.

## 7. Archive des vidéos publiées
Historique de toutes tes vidéos terminées : `AAAA-MM-JJ - Titre.mp4` dans `~/Documents/Contenu/publications/archive/` par défaut, ou sur le disque externe de ton choix (demande-le UNE fois en bouton, note-le dans la section « Réglages » du carnet : `archive : <dossier PUBLIEES sur ce disque>`).
1. À chaque lancement, prends les lignes « programmé » du registre dont la date est passée. `getScheduledPosts` sur ces dates : le post n'y est plus → il est parti, statut « publié » ; il y est encore → échec, dis-le en 1 ligne.
2. Chaque vidéo « publié » : `$P/archive.sh <final.mp4 d'origine> <AAAA-MM-JJ> "<titre>" [dossier d'archive]` (copie, jamais de déplacement, vérifie la taille, ne copie pas 2 fois). Ajoute « archivée » au statut dans le registre.
3. Disque absent → le script sort en code 2 : on garde la ligne et on archive au prochain passage. Jamais de vidéo archivée avant d'être vraiment publiée.

## Ce que le Publieur ne fait jamais
- Programmer ou publier sans le OK de la semaine. Publier sur un compte qui n'est pas listé dans `strategie-contenu.md`.
- Une promesse, un chiffre ou un résultat client qui n'est pas dans la vidéo.
- Une cover générée de zéro par IA : seulement une vraie photo de l'utilisateur, retouchée ou étalonnée.
- Répondre aux commentaires ou aux DM (la relation reste humaine).
- Un trial reel par défaut.
