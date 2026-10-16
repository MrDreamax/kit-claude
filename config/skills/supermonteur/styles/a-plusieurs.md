# À PLUSIEURS : podcast, visio Zoom, split screen, débat (VALIDÉ, ne plus y toucher)

Lu après `SKILL.md`.
**Zones mortes** : déjà conforme ; seul réglage, les mots forts en plein écran (y 1 340) remontent à 1 337 px pour que les jambages (g, p, j) restent au-dessus de 1 480 px.

Source : 2 personnes côte à côte en 16:9 (visio : tuile gauche L, tuile droite R). Mise en page **MIX** : split haut/bas par défaut (on voit la question ET la réaction), **plein écran sur celui qui parle pendant la phrase qui porte un mot fort** (2-3,5 s), jamais moins de 1,5 s de split entre deux pleins écrans. Sous-titres centrés sur la ligne de jonction en split, au niveau du col en plein écran. Pas de zoom (le changement de plan fait le rythme). Musique sous les voix accordée au sujet (émotionnelle), SFX : aucun sur un sujet grave. Pas d'image générée.

1. **Choisir le passage** : transcrire le podcast (`transcribe.py`, ~1 min pour 10 min), lire, proposer 3 passages de 30-50 s (hook dans la 1re phrase, une idée complète, un échange question → réponse) en QCM. Extraire le passage choisi en 16:9 (`ffmpeg -ss A -to B -i podcast.mp4 -c:v libx264 -crf 14 -c:a aac src169.mp4`).
2. **Transcrire + dérusher en 16:9** comme une face cam (étapes 2-3 sur `src169.mp4` → `cut169.mp4` + `cut169.segments.json`), puis retranscrire `cut169.mp4`.
3. **Qui parle** (bouche qui bouge dans chaque tuile, MediaPipe jawOpen, vote par phrase) :
```bash
python3 $S/podcast.py speakers cut169.mp4 words.json     # ajoute "who": "L"/"R" à chaque mot, imprime une ligne par phrase ; ?? = doute -> vérifier à l'œil
```
4. **plan.json** comme d'habitude (fixes, keywords, title, cta, music…) + le bloc podcast :
`"podcast": {"src": "cut169.mp4", "top": "L", "delogo": [24, 34, 266, 152], "segments": "cut169.segments.json"}` (`top` = tuile en haut, défaut l'hôte ; `delogo` = ancien logo incrusté à effacer, en pixels de la source ; avec un titre-question, pas de mots forts → `"full": [[a, b]]` à la main).
Les `keywords` décident les pleins écrans : 2-4 mots forts sur 40 s (1 plein écran par mot fort, 1re occurrence seulement).
5. **Mise en page** puis le moteur normal (étape 6 sans `matte.py` : pas de chiffre derrière la tête en split) :
```bash
python3 $S/podcast.py layout plan.json        # clip.mp4 9:16 + plan.cam / subY / subYAt / zoom:false écrits tout seuls
node $S/build.mjs --plan plan.json --out index.html && npx --yes hyperframes@0.6.81 render . -q high
python3 $S/mix.py plan.json renders/<x>.mp4 clip.mp4 final.mp4
```
Hook automatique : si aucun mot fort avant 3 s, ouverture en plein écran sur celui qui pose la question (2-3 s, coupé sur une fin de mot), puis split pour voir l'autre réagir (le premier changement passe de ~8 s à ~2,6 s).
Détection testée : 12 phrases sur 12 justes sur 2 extraits (dont une reformulation de l'hôte pendant que l'invité sourit). Score = MOUVEMENT de la mâchoire, pas bouche ouverte (un sourire n'est pas de la parole).
Limites : visio 1080p en plein écran = un peu doux (tuile zoomée x1,8) ; webcam = noirs un peu gris (P1 ~14) ; débit visio rapide (sous-titres jusqu'à 23 car/s) ; pas encore de podcast filmé à 2 caméras séparées ni de 3 personnes et plus.
Droits : monte seulement des enregistrements dont tu es l'une des personnes, ou avec l'accord écrit de l'autre.
