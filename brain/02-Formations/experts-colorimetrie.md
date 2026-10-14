---
description: "Étalonnage des reels face cam (Cullen Kelly, Mostyn, Qazi) et réglages ffmpeg testés."
type: formation
statut: actif
sujets: [montage]
---
# Experts : colorimétrie / étalonnage (reels 9:16 face cam)

Date : 2026-10-13. Pour : étalonner des reels face cam.
Niveaux : [P] primaire (l'expert le dit lui-même, vidéo ou guide officiel) · [S] secondaire (un tiers décrit l'expert) · [H] hypothèse (ma proposition, aucune source) · [M] mesure faite par moi sur les fichiers de réf (reproductible).

## L'idée en 5 lignes
1. Ordre des 3 coloristes : balance du blanc d'abord, expo + contraste ensuite, la peau en dernier. Jamais l'inverse.
2. Si ta rush a déjà le look voulu (par exemple studio sombre, mur bleu, peau chaude), on le protège. On ne le refait pas. Petits gestes seulement (caméra 8 bits : les bandes arrivent vite).
3. Contraste : fort au milieu, doux dans les noirs et les blancs. Pas de noirs relevés (testé : ça fait un voile gris moche sur la réf).
4. Peau = l'ancre. Elle reste chaude et naturelle. Le bleu LED reste dans le décor, jamais sur le visage.
5. Le vrai gain : caler chaque insert (illustration, b-roll) sur les mesures de la rush. C'est ça qui évite l'effet « autre univers ».

## Les experts retenus
- **Cullen Kelly** : coloriste et "image scientist" à Los Angeles. Crédits : court-métrage nommé aux Oscars 2021 (Feeling Through), clients Netflix, HBO, Hulu, Apple ; enseigne pour Blackmagic et Mixing Light [S, bios SMPTE/Post Magazine/FIDM]. Lu : 3 vidéos, en entier.
- **Darren Mostyn** : coloriste senior, fondateur d'Online Creative (UK, depuis 1999), 20 ans de métier, formateur certifié Blackmagic, juré Dehancer [S, bios]. Lu : 2 vidéos (scopes ; footage 8 bits).
- **Waqas Qazi** : coloriste. Il cite lui-même Adidas, Amazon Prime, Universal Studios [P, dans sa vidéo, non vérifié ailleurs]. Lu : 2 vidéos. Style plus "poussé" qu'un look naturel (voir contradictions).
- **Alexis Van Hurkman** (Color Correction Handbook) : référence du métier. Livre NON lu (aucun extrait officiel accessible). Son tableau sur la peau me vient de **Larry Jordan** (formateur vidéo) [S].

## Les règles (groupées, chacune avec sa source)

### A. Ordre de travail
- **A1. L'exposition et le contraste font 80 % du grade. Premier nœud, avant tout.** [P] Cullen Kelly https://www.youtube.com/watch?v=Dnxz5R9HrVA [00:00] et [15:22]-[16:43].
- **A2. L'exposition est un réglage créatif, pas technique : "bon" = tu aimes, ton client aime.** [P] même vidéo [02:10]-[02:42].
- **A3. Au niveau du plan, on ne crée pas et on n'enlève pas de contraste : on garde celui du look.** [P] même vidéo [08:39]-[09:12].
- **A4. Si tu tires le contraste dans le même sens plan après plan, c'est ton look qui est faux, pas les plans.** [P] même vidéo [09:44]-[10:17].
- **A5. Règle la balance des couleurs AVANT de baisser la saturation. Baisser la saturation globale "tue l'ADN" de la caméra.** [P] Waqas Qazi https://www.youtube.com/watch?v=0GZSn6nDlnM [01:38]-[02:25] et [06:43]-[07:14].
- **A6. Toucher à la peau n'est jamais la première étape.** [P] Waqas, même vidéo [04:19]-[04:34].

### B. Contraste, noirs, blancs
- **B1. Recette "à toute épreuve" : contraste fort au milieu, contraste doux (courbé) dans les noirs et dans les blancs.** [P] Cullen https://www.youtube.com/watch?v=Dnxz5R9HrVA [20:30]-[21:04]. Il veut garder du détail et du relief en bas et en haut [17:14]-[17:45].
- **B2. Le contraste en courbe en S (genou + épaule) évite d'écraser noirs et blancs.** [P] Cullen https://www.youtube.com/watch?v=dWAaO1cpOh4 [11:14]-[12:06].
- **B3. Contraste = distance entre deux éléments quelconques de l'image (tons, couleurs, zones).** [P] même vidéo [00:00]-[00:49]. 95 % de ses réglages de contraste viennent de 4 outils : lift, gain, offset, contrast+pivot [12:22]-[12:54]. Mélanger tous les outils "salit le goût" [13:29]-[14:02].
- **B4. Noirs : pas écrasés, pas coupés. Blancs : pas collés en haut, seul le blanc pur touche le haut. Descendre sous zéro = OK si c'est voulu.** [P] Darren Mostyn https://www.youtube.com/watch?v=6m3AR-hNsSw [01:51]-[02:22] et [05:34]-[05:50].
- **B5. Le contraste se règle autour d'un point pivot (le gris moyen) pour ne pas bouger l'exposition en même temps.** [P] Cullen https://www.youtube.com/watch?v=Dnxz5R9HrVA [06:28]-[07:49] (pivot 336 chez lui, valeur propre à son espace de travail, pas applicable telle quelle).

### C. Peau
- **C1. Il n'y a pas de formule : une bonne peau est "contextuelle".** [P] Cullen https://www.youtube.com/watch?v=CFwKvMZ309U [00:48]-[01:18].
- **C2. La peau est LA couleur mémoire la plus importante (on a tous un idéal en tête).** [P] même vidéo [02:23]-[02:55].
- **C3. Cible : la ligne "peau" du vectorscope. Hue vs Hue : tourner d'environ 10 degrés, puis baisser la saturation (réglage 0,9) pour compenser.** [P] même vidéo [03:25]-[03:56] et [05:02]-[06:20].
- **C4. L'intention créative passe avant : la peau peut s'éloigner de la ligne si le look le demande.** [P] même vidéo [06:35]-[08:25]. Darren : "cette ligne n'est pas la loi", reste juste constant (dessus, dessous ou sur la ligne) [P] https://www.youtube.com/watch?v=6m3AR-hNsSw [07:57]-[08:14].
- **C5. Les fabricants (Arri, Canon, Sony...) construisent leur colorimétrie autour de la peau. Si la peau est moche, c'est souvent une erreur de balance, pas la caméra.** [P] Waqas https://www.youtube.com/watch?v=0GZSn6nDlnM [00:00]-[00:47] et [12:53]-[13:10].
- **C6. Tableau de luma et saturation de la peau selon la carnation (guide, pas loi).** [S] Larry Jordan, d'après Van Hurkman, https://larryjordan.com/articles/the-secret-to-setting-skin-colors-accurately/ (12/2021) : luma de la peau de 15 % (très foncée) à 70 % (très claire), saturation au vectorscope 15 % à 40 %, teinte à ±2 degrés de la ligne. Exemple : peau mate masculine 35-50 % de luma, 30 % de saturation ; peau claire masculine 45-65 %, 35 %. Mesure sur la joue (cou, bras), pas le visage maquillé.

### D. Décor, séparation, bleu
- **D1. Ne pas neutraliser une lumière de décor : Waqas laisse volontairement le bleu d'un écran allumé "pour rester naturel".** [P] https://www.youtube.com/watch?v=0GZSn6nDlnM [10:44]-[11:00].
- **D2. Fond complémentaire de la peau (bleu/teal contre peau orange) = séparation sans effort. Mais ce n'est qu'une mesure : on juge à l'image.** [P] Darren https://www.youtube.com/watch?v=6m3AR-hNsSw [08:30]-[09:20] ; Waqas https://www.youtube.com/watch?v=akPGqs7daYs [12:29]-[12:44].
- **D3. Bâtir le look AUTOUR du sujet (de la peau), pas l'inverse.** [P] Waqas https://www.youtube.com/watch?v=akPGqs7daYs [06:13]-[06:29].

### E. Footage 8 bits (le cas courant : H.264 de caméra)
- **E1. Point faible = le banding (bandes dans les dégradés). Ne rien pousser trop fort. Petits gestes.** [P] Darren https://www.youtube.com/watch?v=BZqe9jXgPLg [04:48]-[05:04] et [09:07]-[09:24].
- **E2. Éviter les masques/qualifiers en 8 bits : ça casse vite. Préférer des courbes larges avec chute douce (ça cache le banding).** [P] même vidéo [09:39]-[11:17].
- **E3. Rec.709 déjà fait (pas de log) : tu peux étalonner directement en Rec.709, sans gestion de couleur.** [P] même vidéo [08:35]-[08:51].

## Essais que j'ai faits (pour que les valeurs tombent juste) [M]
Fichier test : un reel de référence de monteur (720x1280, 8 bits). ffmpeg 6.0 de la machine. Mesures en luma 0-255.
- Réf monteur (notée 7,5/10), médiane de 37 images : P1 = 2, P50 = 26, P95 = 173, P99 = 199. Pixels "néon" (saturation > 0,9 ET luminosité > 0,8) : 0,04 % (max 0,12 %). Zone visage large (cheveux inclus) : luma 68 (27 %). Joue sur 1 image : R186 G120 B98 (luma 52 %).
- `eq=contrast=1.06` (même principe qu'un filtre CSS `contrast(1.05)`) : P10 passe de 5,8 à 0. Cause : ce contraste pivote à 50 % et écrase tout ce qui est sous 0,5 x (1 - 1/1,05) = 2,4 % de 255 = 6/255. Sur une image sombre, ça veut dire environ 10 % des pixels en noir pur.
- `eq=gamma=1.08` : voile gris visible sur les noirs. Rejeté.
- Courbe en S sur la luma seule, `lutyuv=y='16+219*((val-16)/219-0.12*sin(2*PI*(val-16)/219)/(2*PI))'` : P10 5,8 -> 4,7 ; P50 23 -> 18,9 ; P95 167 -> 170 ; joue inchangée (186/120/96). Aucun voile. Visuellement presque identique à l'original, ce qui est le but.
- `curves=all=...` en RVB : booste la saturation de la peau (peau claire 224,172,140 -> 235,186,145). À éviter pour la cam.
- `vibrance=intensity=-0.5` : LED bleue (30,70,255) -> (34,72,246), mais touche aussi la peau (224,172,140 -> 205,170,149). Pas sélectif.
- `colortemperature=temperature=5200` : réchauffe (blanc 255,255,255 -> 255,231,212). Valeur sous 6500 = plus chaud, au-dessus = plus froid.
- `colorbalance=rs=-0.03:bs=0.05` sur noir (11,11,13) -> (6,11,22) : trop bleu (dérive vers le néon). Moitié moins = ok.
- Chaîne complète validée (H.264, 1080x1920, yuv420p) : voir « Comment l'appliquer », point 2. Coût : `colorbalance` double le temps (environ 2 x la durée de la vidéo), le reste est quasi gratuit.

## Comment l'appliquer

1. **Mesurer avant de toucher.** Sur 10 images de la rush, calcule P1, P50, P95, P99 (luma 0-255), luma de la joue, moyenne R,G,B, % de pixels néon. Réf monteur [M] : P1 2, P50 26, P95 173, P99 199, néon 0,04 %. Rien à corriger si ta rush est dans ±10 de ces valeurs. Source : Darren [01:51]-[02:22] (lire les scopes) + mesure. [P+M]
2. **Une seule passe de grade, légère, dans la commande ffmpeg qui cale la vidéo en 1080x1920.** Chaîne testée : `scale=1080:1920:flags=lanczos,fps=30,format=yuv420p10le,lutyuv=y='64+876*((val-64)/876-0.12*sin(2*PI*(val-64)/876)/(2*PI))',colorbalance=rs=-0.015:bs=0.02,eq=saturation=1.03,format=yuv420p`. Paramètres : amplitude du S a = 0,12 (plage 0,08 à 0,18), saturation 1,03 (plage 0,97 à 1,06), ombres : rouge -0,01 à -0,02, bleu +0,01 à +0,03. Source : Cullen B1-B2 [P] ; valeurs [H] testées [M].
3. **Pas de filtre de contraste global qui pivote à 50 %** (`contrast(1.05)` en CSS, `eq=contrast`) : il écrase tout sous 6/255 (essai [M] : P10 5,8 -> 0). Garde une saturation légère ou passe-la dans la chaîne du point 2. Source : Darren B4 [P] + calcul [M].
4. **Noirs et blancs : P1 entre 1 et 8, P99 ≤ 235 (légal 16-235). Jamais de lift ni de gamma au-dessus de 1,03** (voile gris testé avec 1,08). Source : Darren [01:51]-[02:22], [05:34]-[05:50] [P] ; valeurs [H].
5. **Peau = ancre, cible calibrée une fois sur toi.** Mesure la joue sur 5 rushs, garde la médiane (luma, saturation). Fenêtre : ±8 points de luma autour de ta médiane. Table de départ [S] : luma de la peau 15 à 70 % selon la carnation (peau mate masculine 35-50 %, claire 45-65 %), saturation vectorscope 15-40 %. Réf monteur [M] : joue à 52 % de luma. Hors fenêtre au hook (0-3 s) : monter l'expo du visage, pas celle du décor. Source : C2, C6 [P+S].
6. **Balance des blancs avant la saturation, et seulement pour la peau.** Réglage max ±300 K : `colortemperature=temperature=6200` (réchauffe) à `6800` (refroidit), 6500 = neutre. Saturation globale entre 0,97 et 1,06 : ne jamais la baisser pour "réparer". Source : A5 [P] ; plage [H].
7. **Garde le bleu des LED et du mur.** Ne corrige pas la teinte du mur (écart de teinte ≤ 10 degrés avant/après grade). Ombres seulement un peu froides : noir pur ne doit pas dépasser B - R = 8/255 (test : rs -0,03 / bs +0,05 donne B - R = 16, trop). Source : D1-D2 [P] ; seuil [H].
8. **Zéro néon : moins de 0,5 % des pixels avec saturation > 0,9 ET luminosité > 0,8.** Réf monteur [M] : 0,04 %, max 0,12 %. Si dépassé sur un INSERT ou un b-roll : `vibrance=intensity=-0.3` (touche aussi la peau : jamais sur la cam). Seuil mesuré [M+H]. Aucun expert ne chiffre le néon.
9. **Footage 8 bits : petits gestes.** Chaque réglage ≤ 15 % de variation (a ≤ 0,15, saturation ±6 %, ±300 K). Travailler en 10 bits (`format=yuv420p10le` avant les filtres, retour `yuv420p` à la fin). Pas de masque de couleur (pas de key sur la peau). Si des bandes se voient sur le mur bleu : `noise=alls=1:allf=t` (grain fin) ou `deband`. Source : E1-E3 [P] ; valeurs [H].
10. **Cale les inserts SUR la rush, jamais la rush sur les inserts.** Mesure P1, P50, P99 et R/B moyen d'un insert (pixels non transparents) et compare à la rush. Tolérances : écart de P50 ≤ 10/255, de P1 ≤ 4, de P99 ≤ 25, de R/B ≤ 0,15. Hors tolérance : corrige l'insert (`eq=brightness`, `colorbalance`), jamais la cam. Aligne aussi la saturation des b-rolls sur celle de la cam (mêmes valeurs). Dans un prompt de génération vidéo, décris la lumière de la rush. Source : cohérence (voir experts-direction-artistique-video, Deakins) ; chiffres [H].
11. **Un seul look par reel, appliqué à toute la rush.** Écart de luma médiane entre deux plans de cam du même reel ≤ 5/255 ; au-delà, c'est un problème de tournage (lumière), pas de montage. Source : A4 Cullen [P] ; seuil [H].
12. **LUT : jamais sur la cam. Si besoin sur les inserts générés pour les rapprocher : `lut3d` mélangé à 30 % max** (`split` + `blend=all_expr='A*0.7+B*0.3'`). Source : Waqas "ne pas retirer l'ADN" [P, 11:32-12:03] ; 30 % [H].
13. **Checklist « image » (0 / 0,5 / 1) :** P1 dans [1,8], P99 ≤ 235, néon < 0,5 %, joue dans la fenêtre ±8, écart insert/cam ≤ 10 en P50. 4 critères sur 5 = 1 ; 3 = 0,5. Source : B4, C4, points 8 et 10 ; seuils [H].

## Là où les experts se contredisent (ou ne s'appliquent pas)
- **Waqas Qazi pousse la peau** ("Drive, Joker, John Wick... tu veux que les gens s'en souviennent") [P] https://www.youtube.com/watch?v=akPGqs7daYs [01:08]-[01:23]. Pour un look naturel, ne suis PAS ce conseil.
- **Hypothèse du Brain "noirs un peu relevés, look cinéma" (experts-montage-high-prod S33, [H])** : mes essais montrent un voile. Je la corrige : noirs tenus, jamais relevés.
- **Visage clair au hook (MrBeast, déjà au Brain)** contre **une réf monteur sombre (visage 27 % de luma, notée 7,5/10)**. Les deux ne vont pas ensemble. Test A/B à faire : visage médian à 27 % contre 35 %.
- **Les 3 coloristes travaillent en log + gestion de couleur (ACES) ou en caméra cinéma.** Un tournage en H.264 Rec.709 8 bits ne s'y prête pas : ces conseils ne s'appliquent pas tels quels, d'où le point 9 (petits gestes). Darren le dit lui-même pour le 8 bits [08:35].
- **"Teal et orange"** (Darren, [08:30]) : si ta rush l'a déjà (mur bleu, peau chaude), n'en rajoute pas : point 7.

## Ce que je n'ai pas trouvé
- **Livre de Van Hurkman : non lu.** Pearson ne donne qu'un chapitre d'exemple (primaires, pas les couleurs mémoire). Le tableau de la peau vient de Larry Jordan [S].
- **Aucun coloriste ne donne de valeurs ffmpeg.** Toutes les valeurs ffmpeg sont ma traduction [H], testées sur 1 image/clip de la réf monteur. Pas testées sur ta rush du jour : à valider en A/B.
- **Aucune source ne chiffre un "look sombre bleuté sans néon"** ni la saturation maximale d'une LED. Le seuil néon 0,5 % est ma mesure sur la réf.
- Vidéos de Cullen non lues : "Why using temp & tint is terrible" (VuyomLeOqGc), "Pro white balance techniques" (GD_TCaxbIN0). Waqas "3 steps" lu à 43 % seulement.
- Pas de source sur la couleur des sous-titres blancs selon la luma du fond.

## Tableau des sources
| # | Source + URL | Niveau | Sujet | % lu |
|---|---|---|---|---|
| 1 | Cullen Kelly, "This is 80% of what makes your image look great" https://www.youtube.com/watch?v=Dnxz5R9HrVA | P | expo, contraste, S, recette | 100 % |
| 2 | Cullen Kelly, "Davinci Resolve: Skin Tone Secrets" https://www.youtube.com/watch?v=CFwKvMZ309U | P | peau, ligne, intention | 100 % |
| 3 | Cullen Kelly, "Create Better Contrast, Part 1" https://www.youtube.com/watch?v=dWAaO1cpOh4 | P | contraste, courbe S, outils | 100 % |
| 4 | Waqas Qazi, "Your Skin Tones Look Fake..." https://www.youtube.com/watch?v=0GZSn6nDlnM | P | balance avant saturation, bleu d'écran | environ 83 % (jusqu'à 14:29 sur 18:10) |
| 5 | Waqas Qazi, "3 EASY Steps to get PERFECT Skin Tones" https://www.youtube.com/watch?v=akPGqs7daYs | P | look autour de la peau, fond complémentaire | environ 43 % (jusqu'à 15:38 sur 36:06) |
| 6 | Darren Mostyn, "How I ACTUALLY Read My Scopes" https://www.youtube.com/watch?v=6m3AR-hNsSw | P | noirs, blancs, ligne peau, teal/orange | environ 87 % (jusqu'à 12:16 sur 14:08) |
| 7 | Darren Mostyn, "Pro Colorist on 8-bit Phone Footage" https://www.youtube.com/watch?v=BZqe9jXgPLg | P | 8 bits, banding, courbes larges | environ 63 % (jusqu'à 12:21 sur 19:25) |
| 8 | Larry Jordan, "The Secret to Setting Skin Colors Accurately" https://larryjordan.com/articles/the-secret-to-setting-skin-colors-accurately/ | S | tableau peau (d'après Van Hurkman) | page entière, extraction automatique |
| 9 | Bios : Cullen Kelly (postmagazine.com, fidm.edu, atc21.smpte.org), Darren Mostyn (blog.dehancer.com) | S | crédits des experts | titres de résultats de recherche seulement |
| 10 | Mesures sur un reel de référence de monteur + essais ffmpeg 6.0 | M | seuils et valeurs | 37 images mesurées ; 1 clip de test |
| 11 | Van Hurkman, "Color Correction Handbook" | - | peau, couleurs mémoire | 0 % (aucun extrait officiel accessible) |
