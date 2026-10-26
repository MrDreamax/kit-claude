# Leçons des premiers montages : règles dures (lire AVANT chaque montage)

Ce sont des règles apprises sur de vrais reels, en itérant avec un vrai créateur. Elles passent avant les préférences du skill.
Ton propre carnet (`~/Documents/Brain/00-Moi/regles-agents/supermonteur.md`) passe AVANT ce fichier : **deux règles qui se contredisent, la plus RÉCENTE gagne**.
Chaque retour de l'utilisateur sur un reel = une ligne datée dans son carnet (`JJ/MM/AAAA · reel · note · ce qui n'allait pas → règle`), puis, si la règle change une règle du skill, on corrige le fichier concerné pour qu'il n'y ait jamais deux versions.

## Image
- **L'univers du montage = celui du RUSH** (décor, lumière, couleurs, tenue). La charte de marque sert au tournage et au branding, jamais plaquée sur un rush d'un autre univers : c'est ce qui a fait un 4/10 (« la DA n'est pas en cohérence avec la vidéo, on regarde le montage au lieu de l'idée »).
- **Zéro chrome 3D, zéro néon, zéro glow, zéro icône « glossy »** : ça fait « très cheap ». Matières réelles (bois, cuir, laiton, papier), objets réels = vraie forme et vraie couleur, détourés, éclairés comme la scène. 1 visuel test validé avant de générer le reste.
- **Illustrations DANS la scène, accrochées aux gestes** (tracking `track.py`) : badge au bout du doigt quand la personne pointe, logos à côté de la tête quand elle dit « réseaux », mot derrière la tête. Jamais une scène séparée.
- **Jamais de filtre ou d'étalonnage créatif** sur les B-rolls ni sur le rush (au plus un raccord). Noirs tenus, jamais relevés (voile gris).
- **Pas de REC, pas de bandes noires, pas de gadget par défaut.** Le viseur REC seulement si la vidéo parle de tournage. Bandes noires : testées et rejetées.
- **Jamais saccadé** : zooms lents seulement (1,4 s, sinusoïdal), pas de coup de zoom, pas de changements de plan trop rapides. **Jamais la tête visible une fraction de seconde entre deux pleins écrans** : enchaînés direct ou >= 1,5 s de face cam.
- **Chiffre géant** : aussi gros que possible (il déborde presque), jamais coupé en haut du cadre ; retiré du sous-titre quand il est à l'écran (« DONNE-MOI » seul, pas « DONNE-MOI 30 »).
- **Preuves = vrais objets** (vraie capture de commentaires, vrai profil). Chiffres de preuve = ceux de la personne, jamais inventés. Pas de dashboard 3D ni d'horloge qui s'emballe.
- **Titre-question** : en haut pendant le hook (0 à ~7 s), 1re ligne en police de la DA majuscules + 2e ligne en serif italique ; si la tête touche le haut du cadre, titre EN BAS (`top: 1300`), jamais sur la tête. Avec un titre : ni mot fort ni mot géant. Proposer un titre dans le plan de chaque reel.
- **Cadrage** : recadrage automatique depuis la 4K (`cadre.py`) : yeux à 35 %, visage à 33 % de la largeur ; rush déjà serré = pas touchée. Plan large de salle ou de scène : cadrer à la main (`zoompan`) et vérifier `subzone.py` sur le clip recadré.

## B-rolls
- Un B-roll doit montrer EXACTEMENT ce qui est dit et être beau (net, vertical bien cadré, lumière propre). Les deux ou rien : mieux vaut 2 B-rolls parfaits que 4 moyens.
- **Jamais de B-roll juste pour mettre du B-roll** (« des fois ça sort de la vidéo »). Par défaut aucun. Dans le doute : face cam.
- **Stables** (tremblement mesuré par `broll.py steady`), **bruts**, courts (1 à 2,5 s). Peu de temps hors du plan de la personne (un bon monteur : ~8 s sur 39 s).
- La personne visible dans un B-roll doit être la même que celle de la face cam : l'index dit seulement « personne visible », vérifier à l'œil. Un plan raté ou d'une autre personne va dans `_exclus.txt` de la bibliothèque.

## Dérush et sous-titres
- Jamais de coupe au milieu d'une phrase ; entrée 0,15 s avant le 1er mot, sortie 0,6 s après le dernier (sinon « ça coupe sec » au hook et à la fin). Dérush serré mais pas essoufflé : débit cible 165-195 mots/min, alerte au-dessus de 240.
- Mots forts en serif italique SEULS à l'écran ; sous-titres plafonnés par les zones mortes (voir SKILL.md) ; jamais sur le cou ni le menton.
- Relire TOUTE la transcription et corriger les erreurs de Whisper (`fixes`) : une faute dans un sous-titre = reel raté.

## Son
- **Musique TOUJOURS émotionnelle**, tous formats : une émotion qu'on SENT (mélodie piano ou cordes qui monte), jamais une nappe neutre, d'ambiance ou de suspense sans mélodie. Sujet grave = piano lent ; business / tension = dark cinématique (orchestral hybride sombre, cordes) avec une coupure puis une frappe sur la punchline ; pas la motivation lumineuse par défaut.
- **Niveau** : musique SEULE à -29 LUFS sous la voix à -14 (à -31 elle devenait inaudible sur un morceau contrasté), resserrée (LRA 6, `lra: 11` pour garder une coupure voulue). Toujours mesurer chaque morceau ; **mesurer la musique seule dans le final** (Demucs si installé, sinon la mesure par segment de `mix.py`) : 15 à 17 dB sous la voix. « Il n'y a pas de musique » est arrivé avec un mix pourtant « OK ».
- Ne pas reprendre la musique du reel précédent. Si la musique est refusée une fois : faire choisir à l'oreille (4 versions A-D de SA vidéo, toutes calées sur la punchline, une lettre en réponse), ou l'utilisateur donne un titre ou un lien qu'il aime et on cherche l'équivalent licencié.
- **SFX seulement sur les gros événements** (hook, plein écran, chiffre géant, CTA, silence) : jamais de clics de pastilles, de whoosh de B-roll, de frappe clavier ni de sons collés (21 SFX en 37 s = « parasites qui cassent la concentration »). <= 1 SFX toutes les 4 s, jamais 2 à moins de 1,5 s.
- **UN seul silence par reel, et seulement si une punchline le mérite**, TOUJOURS annoncé par un riser (montée, coupe nette, punchline + impact). Il faut une VRAIE pause dans le rush (>= 0,6 s : à 0,5 s « on ne sent pas l'impact ») : sinon pas de silence, et dire à la personne de marquer un temps avant la phrase choc au prochain tournage.
- **Voix** : l'ORIGINALE par défaut, à -14 LUFS. Correction douce seulement (EQ vers sa voix studio, +-3,5 dB max, `voix_propre.py` sans `--fort`). Jamais Demucs + expandeur + exciteur sur sa voix sans son accord (« bizarre et déformée », « +10 dB c'est trop, +3 ou +4 »).
- **Écran noir au départ** : le rendu HyperFrames démarre à 0,021 s avec une « edit list » vide, donc QuickTime, iPhone et Instagram n'ont aucune image à 0 s. `mix.py` recale à 0 ; contrôle : `ffprobe start_time` = 0.

## Formats spécifiques (détail dans le fichier du style)
- Voix off : aucun contenu généré par IA, B-rolls VIDÉO avec un visage et de l'action (surtout au hook), jamais de photo fixe sans mouvement.
- Green screen : jamais de B-roll de la personne ni de visage derrière son détourage (« deux visages, on ne sait pas où regarder »). UNE phrase = UN seul visuel. Jamais 3 motion design d'affilée. Zoom progressif seulement.
- Montage viral : le format se décide au script, pas au montage.
- B-roll + texte : texte au-dessus de la tête, jamais de ponctuation finale, une intention par reel.

## Méthode
- Avant de monter et avant chaque modification : montrer le plan (moments, visuels, sons, silence) et attendre l'OK. Corriger par retouches ciblées (remix audio seul, plan.json + re-rendu), jamais tout regénérer.
- **Cut Notes** : « done » avec 0 note ne veut PAS dire « validé » : demander en une ligne s'il a laissé des retours.
- Une règle de ces fichiers qui ne convient pas à l'utilisateur : il gagne. Il le dit une fois, c'est écrit dans son carnet, ça ne revient plus.
