# Règles des experts (12 domaines) : lire avant chaque montage

Synthèse de 71 vidéos d'experts et des guides officiels (Netflix, BBC, W3C, EBU, Meta, TikTok, GSAP).
**Priorité : ton carnet (`~/Documents/Brain/00-Moi/regles-agents/supermonteur.md`) > `lecons.md` > ta DA de montage (`montage.json`) > ce fichier.** Si un expert contredit ce que l'utilisateur a dit, l'utilisateur gagne.
Détail, sources et minutages : Brain `02-Formations/experts-<domaine>.md` (montage-video, montage-court-reseaux, sous-titrage, colorimetrie, direction-artistique-video, cadrage-9-16, motion-design, sound-design, sfx, musique-cinematique, montage-musique, mixage-audio) et `experts-motion-hyperframes-github.md`, `guide-opus-motion-design-cassandre-rollet.md`.
[P] = l'expert le dit lui-même. [M] = mesuré sur des reels pros de référence. [H] = hypothèse, à tester.

## A. Règles de plan (à appliquer en écrivant `plan.json`, elles passent dans le plan montré à l'utilisateur)

### Montage et rythme
1. À chaque coupe, décider dans cet ordre : émotion > histoire > rythme > regard. Un blanc de 0,6-0,9 s avant la phrase clé n'est jamais resserré (c'est LE silence). Murch [P]
2. Structure en 4 temps : hook 0-7 s, contexte jusqu'à ~60 %, réponse ~15 %, CTA ≤ 10 s. Musique, zooms et preuves suivent ces phases. Heras [P]
3. Dans les 2,4 premières secondes : la promesse dite + 1 événement (mot géant, impact, zoom lent). Si la promesse arrive plus tard dans le rush : le dire à l'utilisateur (c'est le script). Heras [P], Meta [P]
4. Face cam posée : 1 changement (zoom lent, b-roll, carton) toutes les 8 à 15 s après le hook. Rafale de b-rolls (4 max, ~1 s) seulement sur une énumération. Reels pros : 9,6-14,5 s [M]
5. Débit cible 165-195 mots/min, alerte au-dessus de 240 : trop rapide pour un public de 35-50 ans. Reels pros en studio : 158-192 [M]
6. Chaque élément du plan (b-roll, insert, carton, mot géant, chiffre, preuve) a un champ `why` : le mot déclencheur + ce qu'il montre. Pas de `why` = pas d'élément. Heras, Block [P]
7. Un plein écran ou un b-roll démarre 0 à 0,15 s APRÈS le début du mot ou du geste, jamais avant. Il finit sur le dernier mot de l'idée. Tim Smith [P]
8. Incrustations à moins d'une largeur de tête du visage (≤ 300 px), du côté où il regarde ou pointe. Tim Smith [P]
9. Chaque chiffre ou affirmation a sa vraie preuve à l'écran dans les 5 s. Heras [P]
10. Une seule montée par reel : la punchline (riser + silence + impact au même endroit). Événements visuels par tranche de 10 s : ≤ 2, ≤ 3, ≤ 4 au pic, ≤ 2 à la fin. Block [P], plafonds [H]

### Direction artistique, couleur, cadrage
11. **Fiche univers AVANT tout visuel**, tirée du RUSH : les 7 composantes de Bruce Block (espace, ligne, forme, couleur, ton, mouvement, rythme) + la source de lumière (côté, couleur, dureté). Elle remplit `plan.colors` et la lumière des prompts Higgsfield. Block, Deakins [P]
12. Test "5 sur 7" sur chaque ajout : il partage au moins 5 composantes avec le rush. Il peut contraster sur UNE seule, exprès (l'accent). Sinon on jette. Block [P], seuil [H]
13. Test "sortir de la vidéo" sur chaque ajout : d'où vient sa lumière ? Est-il dans CETTE pièce ? Sert-il la phrase ? Un seul non = retiré. Deakins [P]
14. Palette : 3 teintes dominantes max (prises sur le rush) + 1 accent. Ombre portée d'un insert du côté opposé à la source de lumière. Deakins [P]
15. Caler les inserts SUR le rush (luminosité, couleur, netteté, grain), jamais le rush sur les inserts. Jamais de LUT sur la cam. Waqas Qazi [P], tolérances [H]
16. Pas d'étalonnage créatif : noirs tenus (jamais relevés : ça fait un voile gris, testé [M]), garder la couleur des lumières de la pièce (LED comprises), zéro néon. Darren Mostyn, Cullen Kelly [P]
17. Cadre : yeux entre 33 et 36 % de la hauteur, visage centré (47-53 % de la largeur). Reels pros : 35,1 % et 49,7 % [M]

### Motion design
18. Deux familles d'easing seulement. Forte : `power3.out` 0,45 s (entrées), `expo.out` (mots géants, preuves). Douce : `sine.inOut` (zoom 1,4 s). Sortie : `power2.in`. Jamais `back` ni `elastic` (rebond). GSAP, NN/g, Ben Marriott [P]
19. Un seul mouvement héros à la fois : jamais 2 entrées à moins de 0,25 s (sauf éléments d'une même liste). Ben Marriott [P]
20. La durée suit la taille : petit objet 0,25-0,35 s, moyen 0,35-0,5 s, plein écran 0,45-0,6 s, moment rare (hook, punchline) jusqu'à 0,8 s. NN/g [P], seuils [H]
20b. (détail Brain `02-Formations/experts-motion-hyperframes-github.md`) Pause de 0,3-0,75 s entre l'action et son résultat (« virgule dramatique »), ex. barres grises puis barre accent. HeyGen `motion-doctrine` [P]
20c. Deux blocs qui s'enchaînent bougent sur le même axe et dans le même sens ; jamais d'aller-retour gauche / droite d'un bloc à l'autre ; 2-3 types de transitions par vidéo, pas plus. HeyGen `motion-doctrine` [P]
20d. Un chiffre qui compte : 1,2-2 s si la place le permet (moins de 0,8 s = flash illisible), il grossit pendant qu'il compte, le suffixe arrive après. Jamais de rebond sur un chiffre (c'est une donnée). HeyGen `counting-dynamic-scale` [P]
20e. Graphiques : 1 seule donnée en accent (la dernière barre, la ligne « réalité »), pas de camembert, le moins de grille et de légende possible. HeyGen `stat-bars-and-fills`, `data-in-motion` [P]

### Sous-titres
Le style est VERROUILLÉ : Montserrat 700 majuscules blanc 52 px (ou la police de ta DA), 1-3 mots, mot fort SEUL à l'écran en serif blanc 132 px, fondu 0,1 s, haut du bloc ~95 px sous le col. Les experts ne changent rien à ça. Ils ajoutent seulement :
21. Durée minimale d'un bloc = max(0,5 s ; 0,3 s par mot), sinon fusionner avec le bloc suivant. ≤ 20 caractères/s : au-delà, c'est le dérush qui est trop rapide. BBC, Netflix [P]
22. Jamais 2 mots forts de suite, 6 à 10 par 40 s. Wampus, Isaac [P]
23. Jamais finir un bloc sur un petit mot (et, mais, que, de, en...). Jamais séparer un nombre de son unité ni un prénom de son nom. Netflix, BBC [P]
24. Ne jamais descendre sous 46 px (lecteurs de 35-50 ans). BBC, Legge [P]
25. Si un reel part en PUB : Meta cache le bas sous y = 1 248. Des sous-titres posés plus bas (ex. 1 310) seraient alors en partie sous l'interface : le dire à l'utilisateur avant. En organique : OK. Meta [P pubs]

### Son
26. Musique : écrire l'émotion en 1 mot (`music[].emotion`) AVANT de chercher. Piano seul fragile ou drone sombre, sans voix, BPM ≤ 75 (→ règle du skill : jamais de drone ni de nappe sans mélodie ; une émotion qu'on sent, dark cinématique avec cordes, voir SKILL.md). Juger avec la voix posée dessus, garder 3 finalistes. Reznor/Ross, Michelmore [P]
27. Le sommet naturel du morceau (`from`, `preferenceRegions`) tombe sur le silence ou la punchline. Après le pic, le dernier segment 2 dB plus bas pour le CTA. Michelmore [P]
28. 2 morceaux max sur 40 s, changement seulement quand le sujet change, recalé sur une fin de phrase (pause ≥ 0,15 s), jamais au milieu d'un mot. Michelmore, Standard Story [P]
29. 3 couches max en même temps : voix + musique + 1 SFX. ≤ 1 SFX toutes les 4 s en moyenne, plafond = durée / 4. Quand ça déborde, on enlève dans l'ordre : whoosh b-roll, chiffre, plein écran. On garde : hook, silence, CTA. Murch, Burtt, Thom [P]
30. Riser : son pic tombe pile sur l'événement, pic 2 à 4 s après le début du riser. S'il jure avec la musique : riser "souffle" (non tonal). Epidemic, Spitfire [P]
31. Silence : 0,6 à 2,5 s (→ moteur : 0,6-0,9 s, la vraie pause gardée au dérush). Un seul kit SFX sombre et cohérent par reel (ne pas mélanger des sons de sources différentes). Murch, Herman Huang [P]
32. Musique à -29 LUFS ±1,5 sous la voix (à -31 elle « n'existait pas » sur un morceau contrasté), mesurée PAR segment (pas seulement en global).

## B. À tester en A/B (proposer à l'utilisateur, ne jamais imposer)
- Musique qui entre à la fin de la 1re phrase (fondu 1,5 s) contre dès 0 s. Reznor/Ross [P]
- Voix à -16 LUFS (Curtis Judd, Boykin, EBU) contre -14 (par défaut).
- Visage plus clair au hook (35 % de luma, MrBeast) contre un look plus sombre.
- Coupe sèche de musique avec une petite queue de 0,3-0,6 s contre coupe nette.
- 3 variantes de hook par vidéo pour les Trial Reels (pratique de plusieurs créateurs [S]).
- Sous-titres sur 3 tailles (support 52-80 px, ancre 76-112 px, mot héros 150-240 px) contre 52 px partout. audrey-560 `hyperframes-cinematic-caption` [P]
- Zéro mouvement « d'attente » (dérive lente des blocs motion) contre « jamais figé ». HeyGen `motion-doctrine` [P]
- Sortie = 75 % de l'entrée (inserts 0,34 s au lieu de 0,25 s, listes 0,14 s au lieu de 0,3 s). HeyGen `motion-doctrine` [P]
- Passer HyperFrames de 0.6.81 à une version plus récente (sous-titres embarqués, blocs du registre) : risque de casser le moteur, à tester sur une copie.

## C. Ce que le moteur applique déjà (testé)
- `derush.py` : micro-fondu 0,03 s à chaque coupe (anti-clic) ; plages calées sur la grille des images (image et son exactement de la même durée, la bouche ne se décale jamais).
- `mix.py` : plafond -2 dBTP suréchantillonné ; chaque morceau mesuré et recalé sur sa cible sous la voix ; creux -4 dB à 1,2 kHz ; musique -5 dB pendant ~1 s sous impact / sub drop / plein écran / CTA ; sidechain 30 / 450 ms (la musique remonte en douceur entre les phrases) ; fondus à puissance constante.
- `build.mjs` : pas de `contrast()` sur la cam ni les B-rolls ; pastilles en `power3.out` (pas de rebond) ; sorties douces `power2.in` (inserts et chiffres 0,25 s ; listes, preuves, CTA 0,3 s) seulement s'il reste >= 1,5 s de face cam derrière ; zoom : 5 s mini entre deux zooms dans le hook (0-7 s), 8 s ensuite ; GSAP `autoRound:false` sur les tracés (sinon le tracé saute de vide à plein) ; chiffres géants qui comptent 1,2-2 s en grossissant de 55 % à 100 % ; cartons liste en cascade `power4.out` 0,2 s ; blocs `ring` et `bars`.
- `config.json` : whoosh de B-roll et d'insert coupés ; musique à -29 LUFS ; voix à -14.
- Outils de mesure : `lookstats.py` (look + cadre), `match_look.py` (cale chaque ajout sur le rush, couleur réelle jamais touchée), `univers_check.py` (fiche univers + test 5 sur 7 + planche), `score.py` (débit, car/s, image cam, yeux).
- Écartés : cotes du viseur REC de montage « surveillance », tout rebond, glitch, flash, néon, sous-titres multicolores.
- Cadrage : un rush filmé large (yeux ~47 %, visage ~25 %) est recadré depuis la 4K par `cadre.py` (x 1,34 : yeux 47 % -> 36 %, visage 25 % -> 33 %) ; un rush déjà serré (yeux ~34 %, visage ~33 %) n'est pas touchée. Un monteur humain ne recadre PAS : la différence vient du tournage.
- Débit à surveiller : au-dessus de 240 mots/min ou 20 car/s de sous-titres, c'est le dérush qui est trop serré.
