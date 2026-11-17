# Style horizontal, pour du vertical (VALIDÉ par l’utilisateur le, publié)

Rush horizontal publié en format court. Référence : reel SooWei Goh https://www.instagram.com/reel/DfHgP9Fsyxn/ (« style soowei » = ce style). Modèle : `horizontal.json` (à copier, titre compris).

## Déclencheur
« style horizontal », « style soowei », « horizontal avec bandes noires ». Style fixé : pas de question de style, pas de maquette, pas de vote. Rush horizontal SANS demande de ce style : `devine-format.md` reste la règle.

## Ce qu'on voit
- 1080x1920 : image zoomée en 4:3 comme SooWei, 1080x810, y 555-1365, côtés coupés à parts égales. Autour : deux bandes noires (fond flou assombri essayé puis écarté par l’utilisateur). Le même zoom du début à la fin, jamais de punch-in, jamais d'étalonnage. Vérifier à la planche que personne n'est coupé sur les B-rolls.
- **Titre accrocheur d'UNE ligne au-dessus de l'image** (l’utilisateur, ;, deux fois), y 424, soit 131 px au-dessus de l'image, SF Pro 76 graisse 700, MAJUSCULES, jaune #FFD60A, de la 1re image à la fin, réduit seul pour tenir sur 840 px. OBLIGATOIRE : champ `titre` de horizontal.json. Pas de virgule, de point ni de deux-points, le « ? » reste. Vrai, tiré de la vidéo. Accrocheur : un résultat concret et chiffré + une contradiction, à la 1re personne. Modèle : « 3 erreurs qui tuent tes reels », pas « Être viral ne fait pas vendre ». **Je lui propose 3 titres notés 9/10 minimum, le meilleur en premier, avant le rendu.** Note par un juge séparé : clair en une seconde, chiffre ou contradiction, curiosité, court, et rien que la vidéo ne dise pas. Sous 9 = je réécris, jamais de note gonflée.
- Sous-titres SUR l'image, en bas, y 1095 (sous le menton même penché vers la caméra), SF Pro 56 graisse 500 (40 fin comme lui essayé puis refusé par l’utilisateur le), blanc avec ombre noire légère (flou 7, 85 %, pas de contour), minuscules sans ponctuation, **4 mots max à l'écran, une idée par sous-titre** (l’utilisateur, : 3 essayé, 4 retenu, ~1 s de lecture à son débit de 4 mots/s), le morceau entier d'un coup. **UN chiffre fort par vidéo en jaune**, champ `jaune` de horizontal.json, pas plus : partout ailleurs il perdrait son effet. `horizontal.py` coupe seul au sens (jamais sur un petit mot, jamais dans une expression : listes `FAIBLES` et `LIES`), tient chaque morceau 0,33 s minimum et imprime toutes les coupes : les relire, une coupe bancale se règle en ajoutant le mot à `LIES` ou en coupant la ligne dans `horizontal.json`.
- **Teaser en ouverture, SEULEMENT s'il y a un vrai moment fort**, sinon pas de champ `teaser` et je le dis à la livraison : le moment le plus fort de la vidéo, celui qui attise la curiosité, voix et image d'origine, puis coupe sèche et la vidéo démarre au début. Pas de durée imposée, une phrase qui se comprend seule et qui crée une question avec l'ouverture (6 000 € reçus, puis « voici mon conseil »).
- B-rolls de vie horizontaux (4 à 6 pour 1 min), **d'abord ceux qui maximisent le statut social** (l’utilisateur, : scène, public, lieux, voyages, belles rencontres), peu importe s'ils sont clairs, plan moyen ~4 s, coupes franches, 0 SFX. `orientation` H dans `_INDEX.csv` : un plan vertical ne passe pas.
- Musique continue de MUSIQUE (dossier `music_reels`), choisie d'après l'ambiance, départ sur un temps fort (`attaque.py`), sa montée calée sur le moment fort du texte. Voix intacte.

## Les étapes (~6 min, dont 5 de carte SD)
1. Ouvrir Super, `POST /api/nouveau`, transcription `words.rush.json`. Garder la dernière bonne prise de chaque phrase : `plages.json`, bords au ras de la voix, jamais de coupe < 0,45 s en pleine phrase.
2. `python3 $S/horizontal.py derush <rush>` en arrière-plan : `cut.mp4`, `cut.segments.json`, `cut.words.json`. Relire le texte imprimé.
3. Écrire `horizontal.json` : `titre`, `jaune`, `teaser` si moment fort (`de` et `a` = mots exacts de la transcription, `lignes` = ses sous-titres), `musique`, `debut`, `ecart` (15), `lignes`, `brolls`. B-roll `de` / `a` = texte d'une ligne ou `{"coupe": n, "decale": 0.3}` : une coupe de dérush se cache en la DÉPASSANT de 0,3 s (un bord posé pile dessus est refusé par le Gardien).
4. S'il y a un teaser : `python3 $S/horizontal.py teaser` une fois. Puis `python3 $S/horizontal.py` (~1 min) puis `cp cut.mp4 clip.mp4 ; cp cut.words.json words.json ; python3 $S/gardien.py .`
5. Planche d'images, note par un sous-agent juge contre la référence.
6. Copier `final.mp4` dans `versions/`, QuickTime, `SendUserFile`, `renommer_rush.py`.

7. Retour tournage : à la livraison, 3 points max sur le décor, la manière de filmer ou le sujet, chacun avec l'action à faire au prochain tournage.

## Pièges déjà payés
- **Fin basse** : la vidéo finit sur une phrase avec un point, voix qui descend. `python3 $S/fin_basse.py cut.mp4 cut.words.json` (ou `--candidats --de --a` sur le rush pour choisir la fin). Une fin qui monte ou reste plate = on change de dernière phrase.
- **Euh et reprises invisibles** : ElevenLabs les gomme. Chercher la voix dans les blancs entre mots avant d écrire plages.json, couper chaque euh / mot doublé / faux départ.
- B-roll exact sinon face cam : le plan « Hook = » et le téléphone qu'on ne voit pas sont sortis. Mieux vaut 4 justes que 6 moyens.
- Pas de plan à diapo lisible d'un ancien positionnement (« Dev Perso »).
- B-roll : prendre un passage stable, regarder le plan entier à 2 images/s avant de choisir `from`.
- Démarrer sur la phrase forte, pas sur « je pense » tête baissée.
- La preuve (écran de téléphone) se tourne en plan fixe de 2 s, net, sinon elle ne se lit pas.
