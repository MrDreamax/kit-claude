# Style YouTube theyo (16:9), VALIDÉ par l’utilisateur (« Oui, on garde »)

Vidéo longue YouTube, pas un reel. Fiche source : Brain `02-Formations/theyo-9-pratiques-ia-et-montage-auto.md`. Échantillon de référence : `~/Documents/Montage/MONTAGES/echantillon-youtube-theyo/` (index.html à copier, sons.json, final.mp4).

## Autonomie
l’utilisateur donne le rush, je rends une vidéo notée 9/10 minimum, avec 1 seul tour de retours visé. Pas de 3 versions à voter : le style est fixé ici. Je ne pose qu'une question si le sujet ou le rush est ambigu. Avant le rendu complet : 1 échantillon de 30 s du hook, puis je continue si le juge et les mesures sont d'accord.

## La recette, mesurée
- **Format** : 1920 x 1080, 30 i/s, -14 LUFS, pic sous -1 dB.
- **Rythme** : plan médian 2,8 s, 11 changements d'image par minute. Intro très dense. Il se pose aux explications, accélère aux démonstrations.
- **Part à l'écran** : ~35 % face caméra, ~55 % animations plein écran, ~10 % illustrations.
- **Pas de sous-titres**. Des mots en grand, synchronisés à la voix (`mots.json`, moins de 0,2 s d'écart).
- **Coupes franches**, jamais de fondu entre deux plans.

## Dispositions
1. Face caméra plein écran, cadre poitrine d'origine, zoom lent de +5 % sur tout le plan, jamais de zoom brusque.
2. Face caméra + mot du côté libre, sur voile sombre (« le top 1 % », « dix fois »).
3. Mot seul sur fond noir, ou sur un mur de cartes en perspective 3D.
4. Interface recréée : fenêtre arrondie, ombre douce, légère 3D. Jamais une capture brute à plat.
5. Schéma de points et lignes blanches (constellation) pour un concept abstrait.
6. Comparaison : 2 cartes inclinées face à face, un mot au-dessus.
7. **Barre de niveaux** : le fil rouge. Cartes avec cadenas, la case du chapitre s'ouvre. Toujours le même visuel à chaque chapitre. Le plan du début revient à la fin.

## Couleurs et polices
- Fond noir avec léger halo central, une seule couleur d'accent : le bleu de l’utilisateur `#4F9BFF`, pris dans `da-montage.json`. Son violet et ses néons restent à lui.
- Police : SF Pro partout (règle reprise fidèle), graisse 600, interlettrage serré. Pas de serif : échantillon en SF Pro validé par l’utilisateur.

## Quand animer
Une phrase sans enjeu reste en face caméra. Une animation seulement si elle montre EXACTEMENT ce qui est dit. Chiffre dit = chiffre affiché tel quel, jamais inventé.

## Son
Voix du rush sans traitement. Musique 24 dB sous la voix. Un son court à chaque apparition ou mouvement, coupé net au début. `python3 $S/mix_youtube.py rendu.mp4 rush.mp4 final.mp4 --sons sons.json --musique m.mp3 --ecart 24`.

## Illustrations
Ses vrais plans d'abord, Pexels ensuite. Aucune image ni vidéo générée par IA, même si theyo en utilise.

## Les étapes
1. `mots.py` (ElevenLabs) sur le rush, dérush au ras de la voix (`cuts-serres`).
2. Découper en chapitres, écrire le plan : temps | ce qui est dit | disposition | son.
3. Écrire `index.html` (GSAP + HyperFrames), un fichier par chapitre si la vidéo dépasse 3 min. `npx --yes hyperframes@0.8.149 lint` : 0 erreur.
4. Rendu : `HF_SEGMENTED_CAPTURE=true HF_SEGMENT_FRAMES=600 HF_SEGMENT_BROWSER_RECYCLE=1 npx --yes hyperframes@0.8.149 render . -q high` (29 s de vidéo = 1 min sur le Mac 8 Go).
5. `mix_youtube.py`.
6. Le juge : sous-agent Claude séparé, grille `note-10-youtube.md`, puis correction, 3 tours max.
7. Mes contrôles à moi, toujours : planche d'images, lint, pic et volume.

## Pièges déjà payés
- GSAP `xPercent` sur un élément en `transform` CSS écrase le centrage : séparer scène 3D, pivot et contenu.
- Tween de `filter` depuis `none` : l'élément passe au noir. Toujours `fromTo` avec les 2 valeurs.
- Plusieurs `fromTo` sur le même élément : `immediateRender: false` sauf le premier.
- Ne jamais animer `visibility` sur un élément `.clip`.
- Une scène qui attend son mot laisse un écran vide : le titre part dès le début de la scène.
- Rush déjà monté : les anciens textes incrustés restent. Les effacer avec une plaque du décor propre (image du rush sans texte, bords doux, posée par `overlay`), jamais par un recadrage serré : l’utilisateur a vu « trop zoomé » tout de suite.
- Plan vertical : entier dans une carte arrondie à droite, mot à gauche. Couper pour remplir le 16:9 décapite ou fait « trop zoomé ».
- Un seul limiteur laisse passer un pic au-dessus de 0 dB : `mix_youtube.py` en enchaîne 2 (pic -2,7 dB). Toujours mesurer avec `ebur128=peak=true`.
- Mesure des coupes sur fond noir : seuil de scène 0,08, pas 0,25.
