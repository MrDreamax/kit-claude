# GREEN SCREEN : la personne détourée devant ce dont elle parle (VALIDÉ)

Lu après `SKILL.md`. La **démo filmée** (écran de l'ordinateur filmé + zooms 4K) a été retirée du skill (le code de `source.py` reste, il est partagé) : ne pas la proposer.
Principe validé : 1 visuel par phrase, un article généré au hook, des images réalistes en zoom progressif, du motion design (2 d'affilée max), zéro visage dans les sources, musique dynamique.

**Zones mortes (build.mjs + source.py)** : chaque bloc motion est recalé à 280 px (boîtes mesurées dans `MOBOX`), jamais plus bas qu'avant ni sous 890 px (air au-dessus des sous-titres) ; s'il manque de place il est réduit (dm, chart, profile -16 %, bars -17 %, ring -12 %), sinon il descend simplement (compare, webapp, versus, badge) ; `connect` glisse depuis un cache à 65 px ; react = vidéo en 950 px entre les marges, crédit à 274 px ; bulle à 65 px du bord. **Nouveau type de bloc = mesurer sa boîte et l'ajouter à `MOBOX`**, puis `zones.mjs`.

La personne parle face cam pendant toute la vidéo : la source remplit l'écran pendant les phrases qui en parlent, face cam seule le reste. 3 mises en page (`"layout"`) : `greenscreen` (la personne détourée en bas au centre devant la source, ombre douce ; **DÉFAUT**), `split` (source en haut, visage en bas), `bubble` (source plein écran + visage dans une bulle). Sources qui défilent doucement de `y0` à `y1`, ou une vidéo (`"from"`). Sous-titres au-dessus de la tête détourée ; sur fond clair = ombre renforcée automatique (zone `light`), jamais de bande grise.

## Règles de découpe (ce sont elles qui gagnent)
- **UNE phrase** (jusqu'au point / point d'interrogation, pas la virgule) **= UN seul visuel** : image OU motion design OU article.
- Jamais 3 motion design d'affilée (2 max).
- L'**« article » seulement pour le HOOK**, généré (titre-question, aucun média réel ni visage, aucune marque de presse) avec Higgsfield si branché, sinon dessiné en motion design. Pas de vraies pages ni d'articles réels au milieu.
- **ZÉRO VISAGE** dans toutes les sources : jamais de B-roll de la personne ni d'image avec un visage derrière son détourage (« deux visages, on ne sait pas où regarder »), jamais de mannequins ni de photos d'auteur.
- Musique DYNAMIQUE et émotionnelle (trap sombre ou orchestral, ~120 BPM).
- Pas d'abonnement supplémentaire : tes B-rolls + Higgsfield (facultatif) + Pexels suffisent. Sans Higgsfield : images de tes photos / B-rolls (sans visage) ou motion design seul.

## Images d'idée (Higgsfield, facultatif)
- Modèle `gpt_image_2_5` (0,25 crédit), photo RÉALISTE et captivante (« candid realistic photo, 35mm, natural light, film grain, not CGI »), pas une nature morte de studio (les images fades sont refusées). Ambiance = celle de la vidéo (matières, lampe, couleur d'accent si ça colle). Fond clair de préférence pour que le détourage ressorte.
- Objets dans le TIERS HAUT (sinon cachés derrière la personne), AUCUN visage ni main, zéro chrome / néon / texte.
- `"push": 0.10` = zoom PROGRESSIF, `"push": -0.10` = dézoom progressif, `"cy"` = point visé (0 haut, 1 bas) ; JAMAIS de zoom brusque (« punch » ignoré).
- Pages et images sont dessinées par HyperFrames (bloc `img` automatique) et non par ffmpeg : ffmpeg bouge au pixel entier = saccades (à-coups 1,18 px/image contre 0,11 px).

## Motion design HyperFrames (style validé, en mettre plus)
`{"src": "@motion", "type": ..., "start", "end"}` ; fond = univers de la vidéo (la pièce, sa lumière), la personne détourée devant, zéro visage, mouvements expo sans rebond. Types dans `MOTION` (build.mjs) :
- `dm` (boîte de messages, le message avec la coche passe en tête à `highlight`)
- `chart` (courbe « ce que tu espères » qui monte vs « la réalité » plate)
- `badge` (coche qui se dessine + jauge `label` + 5 étoiles)
- `connect` (2 tuiles `left`/`right` qui se relient, données qui circulent, pastille `pill` à `pillAt`)
- `versus` (« Pour qui ? » : la mauvaise raison barrée, la bonne s'allume)
- `profile` (fiche profil sans photo, la coche bleue apparaît à côté du nom)
- `compare` (UNE phrase « pas plus de X, en revanche Y » : barre X à plat, barre Y qui monte à `pivot`)
- `webapp` (astuce prix : appli « + frais des stores » vs PC « prix réduit », `webAt` / `appAt`)
- `ring` (anneau qui se remplit jusqu'à `value` % avec le compteur au centre, `suffix` défaut « % », `label` en serif italique dessous ; pour UN pourcentage dit à voix haute)
- `bars` (`values` = 3-5 barres, `labels` sous chaque barre, `title`, `value` + `prefix`/`suffix` = chiffre qui compte ; les barres grises montent, pause 0,35 s, puis la dernière en accent monte avec son chiffre ; pour une progression « avant → maintenant »)
Ajouter un type quand une idée revient.

## Options (seulement si l'utilisateur le demande)
- **Hook react** : 3-5 s d'une vidéo du web sur le sujet (`yt-dlp --download-sections "*0:00-0:06"`, **demander l'accord avant tout téléchargement** : nom, source, durée ; vérifier que l'extrait peut être cité), `"fit": true` (vidéo entière en haut, fond bleu nuit, muette, `"credit"` = source à l'écran, `"pre": "delogo=..."` pour flouter une bulle webcam) ; pas de titre-question en même temps (doublon).
- Capture d'une vraie page : `node $S/shoot.mjs out.png URL [hauteur max]` (largeur mobile x2 = 1080 px, bandeau cookies REFUSÉ, jamais de contrôle anti-robot contourné) ; bas de page impossible à faire défiler jusqu'en haut → recadrer l'extrait dans une image 1080x1920 ; flouter les mini-photos d'auteur.

## Lancer
1. Dérusher la cam (étapes 1-3 de SKILL.md) → `cam.mp4` + `words.json`.
2. Planche 1 i/s de la cam ; pour chaque phrase qui montre quelque chose, UN visuel (image, motion, article au hook).
3. **plan.json** (title / keywords, fixes, cta, music) + `"source": {"cam": "cam.mp4", "layout": "greenscreen", "items": [{"src": "src/page.png", "start", "end", "y0", "y1"}, {"src": "@motion", "type": "versus", "start", "end"}]}`
```bash
python3 $S/source.py compare plan.json A B   # (si la mise en page n'est pas choisie) les 3 côte à côte sur A-B s -> comparatif_mises_en_page.mp4
python3 $S/source.py layout plan.json        # clip.mp4 + cam / subY / subYAt / zoom:false ; green screen = détourage auto de toute la cam (~10 s par s)
node $S/build.mjs --plan plan.json --out index.html && npx --yes hyperframes@0.6.81 render . -q high
python3 $S/mix.py plan.json renders/<x>.mp4 cam.mp4 final.mp4
```
4. Vérifier la 1re image de chaque passage source (planche à 2 i/s) : rien de caché derrière la personne, zéro visage.
Bug connu et corrigé : jamais de `-ss` sur la vidéo détourée (webm VP9 + transparence) : la 1re image sortait sans alpha (rectangle noir) → décodage depuis le début + `trim`.
Limites : le visage filmé large est détouré en 0,66 de la hauteur ; pas encore de vraie « réaction » à une vidéo avec son d'origine (mixage 2 voix) ; captures = pages publiques seulement (rien derrière un login).
