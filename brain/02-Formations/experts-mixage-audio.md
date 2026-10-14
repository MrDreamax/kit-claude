---
description: "Mixage des reels : niveaux, ducking, EQ voix, limiteur -2 dBTP, loudness."
type: formation
statut: actif
sujets: [audio, montage]
---
# Experts : mixage audio (niveaux, ducking, EQ voix, limiteur, loudness) pour reels 9:16

Date : 2026-10-13. Pour : le mixage de reels.

Niveaux : **[P]** = l'expert, la norme ou la doc de l'outil. **[S]** = un tiers ou un blog marketing. **[H]** = mon hypothèse, aucune source.
Sources YouTube : https://www.youtube.com/watch?v=ID puis [mm:ss]. Tableau complet en bas.

## L'idée en 5 lignes

1. La voix est le roi. La plainte n°1 des spectateurs : musique et effets qui écrasent la voix (Boykin, Murch).
2. On règle en **LUFS** (sonie) et en **dBTP** (crête vraie), pas "au volume". Je l'ai mesuré sur 2 reels de test : sonie -13,9 / -14,0 LUFS, crête vraie **-1,0 / -1,1 dBTP**.
3. Instagram : aucune norme de sonie publiée trouvée. Les experts disent -16 pour du parlé sur téléphone ; beaucoup de mix visent -14. Écart à tester, pas à imposer.
4. La crête est trop juste pour un ré-encodage AAC : les normes disent **-2 dBTP** avant un encodeur avec perte.
5. Pour garder la voix devant : creuser le médium de la musique (500 Hz-2 kHz, -4 dB) et laisser la voix démarrer avant que la musique baisse.

## Les experts retenus

- **EBU** (union des radiodiffuseurs européens, auteurs de la norme R128) : R128, R128 s1 (formats courts), R128 s2 (streaming), Tech 3343 (production), Tech 3344 (diffusion). Documents officiels.
- **Thomas Boykin** : mixeur et monteur son, a coupé le son direct d'un tiers de John Wick (il le dit [06:50]). Live de 65 min sur la sonie. Lu : 100 %.
- **Curtis Judd** : éducateur "son pour la vidéo", plus de 15 ans de prod et post-prod (fiche de cours). Attention : sur la musique contre le dialogue il dit lui-même "je ne prétends pas être un expert" [fvUn8l30VLc 00:52]. Lu : 3 vidéos à 100 %, 1 session de 72 min à ~25 %, 1 vidéo loudness à 100 %.
- **Ian Shepherd** (ingénieur de mastering, Production Advice) et **Alexey Lukin** (ingénieur DSP principal chez iZotope, ~20 ans) : crête vraie et pertes de codec. Lu : PLR 100 %, podcast crête vraie ~25 %.
- **Doc ffmpeg** (l'outil de rendu) : `alimiter`, `loudnorm`, `sidechaincompress`. Lu : les 3 pages.
- **Epidemic Sound** : guide de mixage (blog marketing, [S]) et vidéo stems (source primaire sur son catalogue).
- **Meta** (doc développeur Reels) : format audio. Via résumé de recherche.

## Valeurs d'un mix de test contre valeurs d'experts

| Paramètre | Mix de test (ffmpeg) | Expert / norme | Verdict |
|---|---|---|---|
| Sonie finale | voix `loudnorm I=-14` ; mesuré -13,9 et -14,0 LUFS | parlé -16 / -17 (Judd), web -16 (Boykin), mobile -20 à -16 (EBU s2) | plus fort que les experts : à tester |
| Crête vraie | `alimiter limit=0.89` (-1 dBFS, sans sur-échantillonnage) ; mesuré **-1,0 et -1,1 dBTP** | -1 dBTP en production (EBU R128), **-2 dBTP** avant encodeur avec perte (Tech 3344, Boykin) | trop juste |
| Court terme max (3 s) | -12,8 et -13,1 LUFS | programme +5 LU (EBU s1) = -9 LUFS | OK |
| Compression voix | `acompressor` -20 dB, 3:1, 5/80 ms | ≤ 3 dB de réduction, léger (Boykin) | à mesurer |
| Filtre grave voix | `highpass 80 Hz` | compréhension de ~100 Hz à 2 kHz (Boykin) | OK |
| Musique sous la voix | cible ~-31 LUFS (écart 14-17 LU) | guide Epidemic : -30 à -35 sous un dialogue à -18/-9 [S] | cohérent |
| Ducking | sidechain seuil 0,05, ratio 2,5, attaque 20 ms, release 350 ms | release ~400 ms, fondu 500 ms (Judd) ; la voix démarre avant la baisse (Boykin) | proche |
| EQ de la musique | aucun | creux 500 Hz-2 kHz, -4 dB (Judd, Herman Huang) | manque |
| Format | AAC 192 kb/s, 48 kHz, stéréo | AAC-LC ≥ 128 kb/s, 48 kHz, stéréo (Meta) [S] | OK |

## Les règles

### A. Sonie cible
- Radio et TV européennes : **-23 LUFS**. [P] EBU R128 (2023).
- Streaming sur appareil à gain limité ou bruit (smartphone) : valeur "intermédiaire" **-20 à -16 LUFS** quand le diffuseur contrôle la dynamique. [P] EBU R128 s2 (g).
- Fenêtre AES TD1004 : -16 à -20 LUFS, crête -1 dBTP (document remplacé en 2021 par TD1008). [S] Production Expert.
- YouTube et Spotify normalisent à -14 LUFS ; pour du parlé, Judd recommande **-16 ou -17** (à -14 la voix devient "crunchy"). [P] Judd nOzZKEWJ5wk [06:29-09:31] ; session Ba51uaJ9c40 [47:48] ; 5euZXnPVhNo [07:17] (-16 pour mobile).
- Web ≈ -16 ; -14 "ne laisse presque aucune marge pour les crêtes". [P] Boykin uB6niANrvEo [47:52] et [58:42].
- Instagram : aucune cible officielle trouvée. La doc Meta ne donne que le format (AAC-LC, ≥ 128 kb/s, stéréo, 48 kHz). [S] developers.facebook.com/docs/video-api/guides/reels-publishing (résumé de recherche).
- La sonie se mesure sur *tout* le programme, sans privilégier la voix. [P] EBU R128 (l).

### B. Crête
- Production : ne pas dépasser **-1 dBTP**. [P] EBU R128 (m).
- Avant un encodeur avec perte : limiteur final à **-2 dBTP**, plus bas si le débit est faible. [P] EBU Tech 3344 (tableau "encoding level").
- "Pour la crête vraie, fais juste -2." [P] Boykin [59:10].
- La marge sous 0 dBTP sert aussi à absorber les dépassements créés par la conversion avec perte. [P] Lukin, podcast 2C_Ju3VM-PA [24:07].
- `alimiter` d'ffmpeg ne mesure pas la crête vraie : sa doc conseille de sur-échantillonner 2x ou 4x avec `aresample` avant de l'utiliser. `loudnorm` détecte la crête vraie en passant à 192 kHz. [P] ffmpeg.org/ffmpeg-filters.html.

### C. Sonie à court terme
- Format court (< 2 min) : sonie à court terme (3 s) max = **programme +5 LU**. Le LRA n'est pas utile (trop peu de données). [P] EBU R128 s1.
- Les dépassements viennent des sons soutenus (drone, moteur), pas des coups courts. [P] Boykin [44:49].
- Les effets se règlent à l'oreille ET à la sonie : un tintement a une grosse crête et peu de sonie. [P] EBU Tech 3343.

### D. Voix
- Compression légère : 3 dB de réduction, c'est déjà "totalement ok", plus peut gêner. [P] Boykin [40:29-41:47].
- La compréhension vient surtout de ~100 Hz à 2 kHz ; ne pas couper 500 Hz par réflexe ; de-esser et compresseur désactivés au départ, activés si besoin. [P] Boykin [38:22-39:39].
- Pour la "richesse" d'une voix d'homme : **-3 dB à 1 kHz** ; -6 à -9 dB sur un micro dur. [P] Judd WXKtiwsy7us [08:58-10:17].
- Limiteur sur la voix : crête entre -6 et 0 dBFS, pas collée au plafond. [P] Judd [10:17-11:10].
- Dialogue : écart entre le plus fort et le plus faible < 20 dB, idéalement ~12 (pour du film). [P] Boykin [23:32].

### E. Musique sous la voix
- Baisser seulement le fader (environ -4 dB, transcription floue) ne suffit pas. **Creuser le médium de la musique** : -4 dB vers 1-1,5 kHz. [P] Judd fvUn8l30VLc [02:09-03:50]. Bande 500 Hz-2 kHz, Q ≈ 0,45. [P] Ba51uaJ9c40 [24:26-24:52].
- Le ducking automatique d'Adobe "tire juste le fader", ce n'est pas le meilleur ; démos à -18 puis -14 dB, fondu 500 ms. [P] Judd Ba51uaJ9c40 [17:50-19:07].
- Sidechain : attaque très rapide, release **~400 ms**. [P] Judd [33:20].
- On peut aussi creuser une "poche" dans le médium de la musique avec un effet de type de-esser (transcrit "DSR") ou un EQ dynamique, pour laisser la place à la voix. [P] Herman Huang tzfzkTAQsnE [01:41] ; Judd Ba51uaJ9c40 [42:12].
- Laisser la voix démarrer, puis baisser la musique : ça cache le mouvement (le début de phrase est fort) ; ne pas "Mickey-Mouser" le mix. Marche mieux avec de la musique orchestrale ; une musique électronique compressée laisse entendre la baisse. [P] Boykin [43:06-43:57].
- La musique d'un compositeur arrive trop chaude : la baisser avant le mix. [P] Boykin [24:22].
- Stems : mélodie -20 dB, reste -12 dB, rampe 42 images. [P] Epidemic xnrSA35LlR8 [03:22-03:47].
- Guide Epidemic : dialogue -18 à -9 dB, musique -18 à -22 dB, musique sous dialogue **-30 à -35 dB**, effets -10 à -20 dB (échelle non précisée). [S] epidemicsound.com/blog/audio-mixing-for-video.

### F. Écouter pour de vrai
- Tester sur petit haut-parleur ou téléphone, avec du bruit de fond (ventilateur) ; vérifier que le calme reste au-dessus du bruit. [P] Boykin [32:39-33:56].

## Comment l'appliquer

1. **Plafond -2 dBTP** : remplace `alimiter=limit=0.89:level=0` par `aresample=192000,alimiter=limit=0.794:attack=5:release=50:level=0,aresample=48000`, puis vérifie `ebur128=peak=true` : crête vraie ≤ -2,0. Un mix à -1,0 / -1,1 est trop juste. À mettre sur la dernière ligne de filtres. EBU Tech 3344, Boykin, Lukin, doc ffmpeg [P].
2. **Sonie voix** : garde -14 LUFS pour commencer, mais fais-en un paramètre, et prépare un test d'écoute -14 contre -16 sur téléphone, volume 50 %. Judd, Boykin, EBU s2 [P] disent -16 ; effet sur Instagram inconnu [H].
3. **Normalisation voix transparente** : `loudnorm` en 2 passes (`linear=true` avec les valeurs mesurées) au lieu du mode dynamique, car la voix est déjà compressée 3:1 ; le mode dynamique peut pomper. Doc ffmpeg [P], choix [H].
4. **Compression voix** : mesure la réduction de gain moyenne ; vise ≤ 3 dB, crêtes ≤ 6 dB, ajuste `threshold` (-20 dB) selon la rush. Boykin [P] (3 dB) ; 6 dB [H].
5. **EQ voix** : garde `highpass 80 Hz` ; ne jamais couper 500 Hz en bloc ; si la voix est dure : `equalizer=f=1000:width_type=q:width=1:g=-3` ; `deesser` seulement si les S piquent. À placer au début de la chaîne voix. Judd, Boykin [P] ; Q = 1 [H].
6. **Creuser le médium de la musique** : `equalizer=f=1200:width_type=q:width=0.45:g=-4` dans la chaîne de **chaque** segment musique, après `loudnorm`. Judd [P], Herman Huang [P]. Après ajout, remesure : la musique devrait perdre environ 1 LU [H], donc remonte le niveau du segment d'autant.
7. **Sidechain** : garde seuil 0,05 et ratio 2,5 ; attaque 20 → **30 ms**, release 350 → **450 ms**. Boykin, Judd [P] ; 30 et 450 [H].
8. **Musique sous la voix = -31 LUFS ±1,5, par segment.** Une consigne « entre -26 et -30 = OK » est trop forte si la musique couvre la voix. Règle l'alerte « trop bas » à **-34** (sinon l'alerte tombe à 1 LU de la cible). Epidemic [S].
9. **Contrôle final** : affiche sonie intégrée, crête vraie, `S max`, `M max`. Seuils : intégrée dans ±1 LU de la cible, crête vraie ≤ -2,0 dBTP, `S max` ≤ intégrée +3 LU et ≤ -9 LUFS (commande `ebur128=peak=true:framelog=verbose`). EBU R128 + s1 [P] ; +3 LU [H].
10. **Ordre de la chaîne** : voix (HPF, compresseur, loudnorm) ; musique (loudnorm, EQ médium, fondus) ; somme ; sidechain ; effets ; somme finale ; limiteur true peak ; AAC. Le limiteur reste en dernier. EBU Tech 3344 [P].
11. **Écoute de contrôle** : avant livraison, écoute le final sur le haut-parleur d'un téléphone avec bruit de fond. Chaque mot compris, musique sentie, aucune saturation. Boykin [P].
12. **Format de sortie** : AAC-LC, 48 kHz, stéréo, ≥ 128 kb/s (par exemple 192 kb/s). Meta [S].

## Points à arbitrer

- **Voix à -14 LUFS** : Judd, Boykin et l'EBU disent -16 pour le parlé sur mobile. À tester, pas à imposer (les plateformes normalisent peut-être autrement).
- **Crêtes saturées = à éviter** : un mix à -1,0 dBTP ne sature pas, mais il est au ras. Après le ré-encodage d'Instagram, une crête peut dépasser 0 dBTP. Le point 1 (-2 dBTP) protège.
- **« La 2e musique est trop forte »** : si ta consigne dit encore « entre -26 et -30 = OK » alors que la cible est ~-31, aligne-la (point 8).
- Judd dit que baisser le fader ou le ducking automatique « n'est pas le meilleur » : un mix qui ne fait que du sidechain, sans EQ, manque le creux de médium (point 6).

## Ce que je n'ai pas trouvé

- **Norme de sonie officielle d'Instagram** : introuvable. Des sites tiers parlent de -14 LUFS sans preuve ; je ne les cite pas comme fait.
- Page Netflix de mixage : illisible (site dynamique). Boykin la cite : dialogue -27 LUFS (gated). AES TD1004 / TD1008 : PDF non lu, seulement un résumé de Production Expert [S]. ITU-R BS.1770 : non lu. EBU R128 s4 (cinéma, LDR ≤ 5 LU) : seulement via Tech 3343.
- Aucune source primaire pour : boost de présence (Hz), fréquence du de-esser, valeur de seuil/ratio/attaque/release d'un sidechain pour un *face cam parlé* (Judd et Boykin parlent de film, de vidéo ou de podcast). Mes valeurs (30 ms, 450 ms, Q = 1) sont [H].
- Mesure de l'effet réel du ré-encodage Instagram sur la crête : non testée (pas de compte de test).
- Mesures de sonie faites sur 2 reels seulement.

## Tableau des sources

| # | Source + URL | Niveau | Sujet | % lu |
|---|---|---|---|---|
| 1 | EBU R128 (2023), https://tech.ebu.ch/docs/r/r128.pdf | P | -23 LUFS, -1 dBTP | ~90 % |
| 2 | EBU R128 s1 (2020), https://tech.ebu.ch/docs/r/r128s1.pdf | P | format court, +5 LU | 100 % |
| 3 | EBU R128 s2 (2023), https://tech.ebu.ch/docs/r/r128s2.pdf | P | streaming, -20 à -16 | 100 % |
| 4 | EBU Tech 3343, https://tech.ebu.ch/docs/tech/tech3343.pdf | P | production | ~10 % (recherche + 2 passages) |
| 5 | EBU Tech 3344, https://tech.ebu.ch/docs/tech/tech3344.pdf | P | -2 dBTP avant encodeur | ~5 % (recherche + 1 passage) |
| 6 | Boykin, https://www.youtube.com/watch?v=uB6niANrvEo | P | sonie, voix, musique | 100 % |
| 7 | Judd, "Mix dialogue with music", https://www.youtube.com/watch?v=fvUn8l30VLc | P | EQ médium | 100 % |
| 8 | Judd, "Volume vs Loudness", https://www.youtube.com/watch?v=nOzZKEWJ5wk | P | -16 / -17 | 100 % |
| 9 | Judd, session son pour la vidéo, https://www.youtube.com/watch?v=Ba51uaJ9c40 | P | ducking, sidechain | ~25 % |
| 10 | Judd, workflow dialogue, https://www.youtube.com/watch?v=WXKtiwsy7us | P | EQ voix | 100 % |
| 11 | Judd, normalisation (partie 1), https://www.youtube.com/watch?v=5euZXnPVhNo | P | -16 mobile | 100 % |
| 12 | Shepherd, PLR, https://www.youtube.com/watch?v=iv67sjuq2go | P | plateformes | 100 % |
| 13 | Shepherd et Lukin, crête vraie, https://www.youtube.com/watch?v=2C_Ju3VM-PA | P | marge codec | ~25 % |
| 14 | Epidemic, stems, https://www.youtube.com/watch?v=xnrSA35LlR8 | P (catalogue) | -20 / -12 dB | 100 % |
| 15 | Epidemic, mixage, https://www.epidemicsound.com/blog/audio-mixing-for-video | S | niveaux en dB | texte lu via fetch |
| 16 | Herman Huang, https://www.youtube.com/watch?v=tzfzkTAQsnE | P (sponsorisé) | médium de la musique | 100 % |
| 17 | ffmpeg-filters, https://ffmpeg.org/ffmpeg-filters.html | P (outil) | alimiter, loudnorm, sidechain | 3 pages lues |
| 18 | Meta Reels, https://developers.facebook.com/docs/video-api/guides/reels-publishing | S | AAC 48 kHz | résumé de recherche |
| 19 | AES TD1004, https://www.production-expert.com/production-expert-1/aes-update-loudness-recommendations-for-audio-only-streaming | S | -16 à -20 | résumé de recherche |
| 20 | Mesures ebur128 de deux reels de test | mesure | sonie, crête, court terme | 2 fichiers |
