---
description: "Motion design des reels : easing GSAP, durées, Ben Marriott, NN/g."
type: formation
statut: actif
sujets: [montage]
---
# Experts : motion design (reels 9:16 face cam)

Date : 2026-10-13. Pour : le motion design de reels.
Niveaux : [P] primaire (guide officiel, ou l'expert lui-même) · [S] secondaire (un tiers décrit) · [H] hypothèse (ma proposition, aucune source) · [C] calcul fait par moi à partir d'une source (voir "Courbes officielles en syntaxe GSAP").

## L'idée en 5 lignes
1. Entrée : "ease out" (démarrage vif, arrivée douce). Sortie : "ease in" (plus courte que l'entrée). Jamais linéaire, sauf une dérive très lente.
2. Les 4 sources officielles (GSAP, Google Material, IBM Carbon, Nielsen Norman) donnent des durées qui tiennent dans 100 à 500 ms, jusqu'à 700 ms pour les grands mouvements. Un montage bien réglé est déjà dans cette zone presque partout.
3. Deux défauts fréquents : (a) aucune sortie douce (tout disparaît à la coupe) ; (b) un rebond `back.out(2)` sur les pastilles, alors qu'un style posé dit "jamais de rebond".
4. Ben Marriott : un petit mouvement inverse avant le grand (anticipation) dirige l'œil. On le garde pour les moments héros seulement, très petit.
5. Un seul mouvement important à la fois : on guide le regard, on ne le disperse pas.

## Les experts retenus
- **GSAP (doc officielle)** : la bibliothèque d'animation. Lu : 2 pages (extraction).
- **Google, Material Design 3** (via le dépôt officiel material-components-android) : durées en ms, courbes en cubic-bezier. Lu : page "Motion" (extraction).
- **IBM Carbon** (guide officiel) : durées, courbes "productive" et "expressive". Lu : page "Motion overview".
- **Nielsen Norman Group** (cabinet de recherche en UX, article "Executing UX Animations: Duration and Motion Characteristics") : durées 100-500 ms, entrée contre sortie. Lu : page entière (extraction).
- **Ben Marriott** : motion designer et formateur (Sydney), cours "Master Motion Design" ; environ 10 ans de métier selon des pages tierces, liste de clients NON trouvée [S]. Lu : 3 vidéos (anticipation, match cut, transition).
- **Jake Bartlett** : formateur After Effects depuis plus de 10 ans, 30+ cours Skillshare, "Lead Educator" chez Battle Axe depuis 2022 (profil Adobe, School of Motion) [S]. Lu : 2 vidéos (graph editor, courbes).
- **School of Motion** : école de motion design ; vidéo d'intro sur les 12 principes (paraphrase de "The Illusion of Life", livre non lu) [S].
- **Issara Willenskomer** ("UX in Motion") : plus de 20 ans, projets de motion pour de grandes marques (biographie UX Magazine) [S]. Lu : l'article "UX in Motion Manifesto" : AUCUN chiffre en ms.

## Courbes officielles en syntaxe GSAP (mon calcul [C])
Méthode : j'ai pris chaque `cubic-bezier` officiel, calculé sa courbe, et cherché l'ease GSAP intégré le plus proche (erreur moyenne sur 400 points ; plus c'est petit, mieux c'est ; sous 0,05 = très proche).
| Courbe officielle | Ease GSAP le plus proche | Erreur |
|---|---|---|
| Material standard-decelerate (0, 0, 0, 1) = "entrée" | `circ.out` ou `power3.out` | 0,019 / 0,049 |
| Material emphasized-decelerate (0,05 ; 0,7 ; 0,1 ; 1) = entrée "forte" | `expo.out` | 0,050 |
| Material emphasized-accelerate (0,3 ; 0 ; 0,8 ; 0,15) = sortie "forte" | `power2.in` | 0,025 |
| Material standard-accelerate (0,3 ; 0 ; 1 ; 1) = sortie | `sine.in` | 0,053 |
| Material standard (0,2 ; 0 ; 0 ; 1) = reste à l'écran | `power2.out` | 0,039 |
| Carbon productive "entrance" (0, 0, 0,38, 0,9) | `power1.out` | 0,016 |
| Carbon expressive "entrance" (0, 0, 0,3, 1) | `power2.out` | 0,048 |
| Carbon "exit" (0,2 ; 0 ; 1 ; 0,9) | `sine.in` | 0,062 |
| CSS ease-out (0, 0, 0,58, 1) | `sine.out` | 0,014 |
| CSS ease-in-out (0,42 ; 0 ; 0,58 ; 1) | `power1.inOut` ou `sine.inOut` | 0,006 / 0,012 |
Lecture simple : entrée douce = `power1.out` / `sine.out` ; entrée normale = `power2.out` / `power3.out` ; entrée forte = `expo.out` ; sortie = `power2.in`. La doc GSAP n'explique pas la force des `power1` à `power4` : cette table est donc la preuve chiffrée.

## Les règles (groupées, chacune avec sa source)

### A. Courbes
- **A1. GSAP : l'ease par défaut est `power1.out`. "Ease out" démarre vite, ralentit à l'arrivée : "le meilleur pour les transitions d'interface, car rapide au départ, donc réactif".** [P] https://gsap.com/resources/getting-started/Easing et https://gsap.com/docs/v3/Eases/ (familles : none, power1 à 4, back, bounce, circ, elastic, expo, sine, steps ; variantes in, out, inOut).
- **A2. Entrée = ease-out. Sortie = ease-in. Le linéaire paraît peu naturel. L'entrée dure un peu plus que la sortie : 300 ms pour apparaître, 200 à 250 ms pour disparaître.** [P] Nielsen Norman Group https://www.nngroup.com/articles/animation-duration/ (page entière).
- **A3. Material 3 : "decelerate" pour ce qui ENTRE à l'écran, "accelerate" pour ce qui SORT, "standard" pour ce qui reste à l'écran. "Emphasized" = les mêmes, plus marqués.** [P] https://raw.githubusercontent.com/material-components/material-components-android/master/docs/theming/Motion.md
- **A4. Carbon : "expressive" (visible) réservé aux "moments rares et importants" ; "productive" (discret) pour le reste.** [P] https://carbondesignsystem.com/elements/motion/overview/
- **A5. "Quand utiliser l'easing ? Toujours." Le linéaire paraît "inachevé, brusque, distrayant".** [P] Issara Willenskomer https://uxmag.com/articles/creating-usability-with-motion-the-ux-in-motion-manifesto (principe 1, "Easing").
- **A6. "Offset et delay" : des objets décalés dans le temps montrent qu'ils sont distincts (aucune valeur chiffrée).** [P] même article (principe 2).
- **A7. Niveau 1 : "easy ease" (F9). Niveau 2 : augmenter l'influence des poignées dans l'éditeur de courbes = beaucoup plus lisse et plus fort. L'easing, c'est la répartition des images : plus serrées au début et à la fin, plus espacées au milieu.** [P] Jake Bartlett https://www.youtube.com/watch?v=6zrEKEuJGKs [01:09]-[02:44] ; https://www.youtube.com/watch?v=7pOCtlrrE3Y [03:28]-[04:15].
- **A8. Sauf pour un effet très sec, les courbes doivent s'enchaîner sans angle vif.** [P] Ben Marriott https://www.youtube.com/watch?v=LcWJKYbYvi8 [09:04]-[09:19].

### B. Durées
- **B1. La plupart des animations : 100 à 500 ms. 100 ms = bas du perceptible (retour simple, case à cocher). 200 à 300 ms = changement d'écran important. 400 ms = "très lent", pour les grands mouvements. À 500 ms, "ça traîne".** [P] NN/g https://www.nngroup.com/articles/animation-duration/. Elles sont plus souvent trop longues que trop courtes.
- **B2. Material, jetons de durée : court 50, 100, 150, 200 ms ; moyen 250, 300, 350, 400 ; long 450, 500, 550, 600 ; très long 700, 800, 900, 1000. "La durée augmente avec l'aire et le trajet de l'animation."** [P] material-components-android docs/theming/Motion.md.
- **B3. Carbon, jetons : 70 ms (bouton), 110 (fondu), 150 (petits déplacements), 240 (toast, expansion), 400 (grande expansion), 700 (fond qui s'assombrit). Plus la distance ou l'échelle est grande, plus c'est long.** [P] https://carbondesignsystem.com/elements/motion/overview/
- **B4. Trois images suffisent à faire comprendre un mouvement ; l'anticipation peut durer presque 3 fois le mouvement principal quand on veut l'exagérer.** [P] Ben Marriott https://www.youtube.com/watch?v=LcWJKYbYvi8 [04:15]-[05:36] et [09:34]-[09:50].

### C. Anticipation et regard
- **C1. Anticipation = un petit mouvement qui précède le grand (ex. reculer avant de lancer). Elle dit au spectateur "regarde ici, quelque chose arrive". Ce n'est pas un rebond.** [P] Ben Marriott https://www.youtube.com/watch?v=LcWJKYbYvi8 [01:54]-[02:41] et [05:51]-[07:10] ("eye tracing" : tu contrôles où l'œil va).
- **C2. Pour faire disparaître un élément pendant une transition, le faire au moment du mouvement le plus rapide.** [P] Ben Marriott https://www.youtube.com/watch?v=UVDpgP7sRbw [06:29]-[06:44].
- **C3. Les 12 principes d'animation (Disney) : slow in / slow out, anticipation, follow through, arcs, timing, mise en scène... Source du livre "The Illusion of Life" (non lu).** [S] School of Motion https://www.youtube.com/watch?v=mT2Fv5bF6Ik [00:53]-[03:18].

## Comment l'appliquer

Réglages de référence (GSAP) pour un montage de reels posé :
| Usage | Ease GSAP | Durée | Remarque |
|---|---|---|---|
| Apparition de texte, insert, carton (opacité, montée, flou) | `power3.out` | 0,45 s (flou 10 px vers 0) | réglage de référence |
| Titre de liste | `power3.out` | 0,30 s | réglage de référence |
| Éléments de liste | `power2.out` | 0,22 s, décalage 0,05 s | réglage de référence |
| Mot géant, lettre par lettre depuis le centre | `expo.out` | 0,60 s, décalage 0,05 s | réglage de référence |
| Chiffre géant (flou 24 px vers 0, échelle 1,18 vers 1) | `power3.out` | 0,32 s | réglage de référence |
| Compteur qui défile | `power2.out` | 0,55 s | réglage de référence |
| Plein écran preuve (flou 16 px vers 0) | `expo.out` | 0,32 s | réglage de référence |
| Tracés SVG | `power2.inOut` | 0,45 s | réglage de référence |
| Zoom caméra | `sine.inOut` | 1,4 s | réglage de référence |
| Pastilles 1-2-3 | `power3.out` | 0,25 s | éviter `back.out(2)` (rebond) |
| Sortie douce des gros éléments | `power2.in` | 0,25 s (listes, preuves : 0,30 s) | souvent oubliée : sans elle, coupe sèche |

1. **Garde l'entrée par défaut `power3.out`, 0,45 s** (opacité 0 vers 1, montée de 24 px, flou 10 px vers 0). Équivalent officiel : Material standard-decelerate [C]. 0,45 s est plus long que les 200-300 ms de NN/g : on est dans une vidéo, pas dans une interface qu'on touche [H]. Source : A1, A2, B1, B2 [P] ; 0,45 s [H].
2. **Ajoute une sortie douce aux gros éléments** (titres, listes, preuves, inserts) : opacité 1 vers 0, `power2.in`, 0,25 s (listes et preuves 0,30 s), qui COMMENCE à `b - durée` (où `b` est la fin de l'élément). Sans cela, l'élément coupe d'un coup à `b`. Garde-fou anti-flash : la sortie douce n'a lieu que s'il reste au moins 1,5 s de face cam derrière ; sinon coupe franche enchaînée au plein écran suivant. Pas de sortie douce sur les sous-titres (coupe). Source : A2 NN/g (sortie plus courte que l'entrée, ease-in) [P] ; C2 Ben [P] ; Material emphasized-accelerate ≈ `power2.in` [C].
3. **Pastilles : remplace `back.out(2)` par `power3.out`, 0,25 s, échelle 0,85 vers 1.** Le rebond contredit un style posé (« sans rebond »). Source : A1 GSAP [P]. Aucun expert lu ne défend le rebond pour du texte.
4. **Deux familles seulement : "douce" et "forte".** Douce : `sine.inOut` (déplacements entre deux positions visibles, zoom) ou `power1.out` / `sine.out` (fondus). Forte : `power3.out` (entrées) ou `expo.out` (mots géants, preuves, "moments rares"). Sortie : `power2.in`. Rien d'autre. Définis-les comme constantes en tête de ton projet (`EASE.in`, `EASE.hero`, `EASE.out`, `EASE.soft`). Source : A1, A3, A4, A7 [P] ; table [C].
5. **Bornes de durée : jamais sous 0,13 s (4 images à 30 i/s) sauf coupe sèche ; mouvement d'objet jamais au-dessus de 0,70 s ; titres et mots géants jusqu'à 1,2 s ; texte à lire au moins 1,5 s à l'écran.** Source : B1, B2, B3 [P] ; bornes de vidéo [H].
6. **La durée suit la taille de l'objet.** Petit (≤ 300 px de large) : 0,25 à 0,35 s. Moyen (300 à 700 px) : 0,35 à 0,50 s. Plein écran : 0,45 à 0,60 s. Tout ce qui est "moment rare" (hook, punchline) peut monter à 0,8 s en `expo.out`. Source : B2, B3 (la durée croît avec l'aire) [P] ; seuils de pixels [H].
7. **Anticipation seulement sur les moments héros** (mot géant, objet accroché au doigt, chiffre) : micro-recul de 6 % de la course (par exemple 8 px vers le bas avant une montée de 24 px), 0,12 s en `power2.out`, puis l'entrée normale du point 1. Jamais de dépassement (pas de `back`, pas d'`elastic`). Source : C1 Ben Marriott [P] ; 6 % et 0,12 s [H].
8. **Un seul mouvement héros à la fois.** Pas deux entrées d'éléments différents à moins de 0,25 s l'une de l'autre, sauf les éléments d'une même liste. Source : C1 (eye tracing) [P] ; A6 offset et delay [P] ; 0,25 s [H].
9. **Décalage (stagger) : 0,05 s entre lettres ou éléments, total au plus 0,5 s ; sur les listes de 14 à 18 éléments, `step = min(0,05 ; 0,45 x durée de page / nombre d'éléments)`.** Source : A6 [P, sans chiffre] ; 0,05 s [H].
10. **Zoom caméra : `sine.inOut`, 1,4 s, amplitude au plus 7 %, jamais sous 1,2 s ; une seule fois par changement d'idée, au moins 5 s entre deux.** Vitesse de pointe : 0,0861 x π / (2 x 1,4) = 9,7 % par seconde [C]. Source : A5, A7 [P] ; C3 Disney (slow in, slow out) [S] ; seuils [H].
11. **Linéaire (`none`) autorisé SEULEMENT pour : la dérive de caméra (1,5 % sur au moins 3,6 s, soit 0,4 % par seconde, invisible), les trajets par échantillons d'un suivi de visage et les compteurs d'horloge ou de REC. Jamais ailleurs.** Source : A2, A5 [P] ; seuils [H].
12. **Match cut (optionnel, à tester AVANT de l'adopter) : zoom de 100 à 103 % juste avant la coupe (`power2.in`, 0,4 s), puis de 103 à 100 % sur le plan suivant (`power2.out`, 0,4 s).** Ben Marriott dit 100 à 105 % et "sois subtil, 5 % est peut-être déjà trop" ; 103 % est mon choix. Source : Ben Marriott https://www.youtube.com/watch?v=ythBGTLjot8 [01:17]-[02:06] [P] ; 3 % [H]. Voir la contradiction ci-dessous.

## Points à arbitrer
- **Ben Marriott et les 12 principes Disney recommandent anticipation, dépassement (follow through), squash et stretch.** Pour un style posé premium, jamais de rebond : garde l'anticipation (point 7, 6 % seulement) et écarte le reste. Les pastilles avec `back.out(2)` sont l'exception à corriger (point 3).
- **Match cut avec zoom (Ben Marriott) contre "pas de punch-in, pas de saccade".** Optionnel, 3 % au lieu de 5, à tester sur 1 reel (point 12).
- **NN/g : sortie en ease-in, plus courte que l'entrée** contre **une règle anti-flash (jamais de tête visible une fraction de seconde entre deux pleins écrans)**. La règle anti-flash gagne : sortie douce seulement s'il reste 1,5 s de face cam (point 2).
- **Durées de Material, Carbon, NN/g = interfaces qu'on touche, pas vidéo.** Je les prends comme plafonds, pas comme cibles. 0,45 s est déjà un peu plus lent ; je ne le change pas.
- **TikTok conseille beaucoup d'animations et de transitions pour "garder l'attention"** (page officielle creative-best-practices) : non suivi, contraire à "peu de coupes, élégant".

## Ce que je n'ai pas trouvé
- **Issara Willenskomer : aucune durée en ms.** Son article UX Magazine donne les 12 principes sans chiffre ; l'article Medium d'origine est bloqué (403) ; son livre "UX in Motion" non lu.
- **"The Illusion of Life" (Thomas et Johnston) : extrait non obtenu.** Les 12 principes viennent de la paraphrase de School of Motion [S] (livre non lu, Google Books sans quota).
- **GSAP** : la doc ne dit pas la force de `power1` à `power4` ni les paramètres de `back` et `elastic` (pages lues). La table ci-dessus est mon calcul.
- **Aucune source donne des durées pour du texte animé en vidéo verticale.** Les chiffres des points 1, 5, 6, 7, 9 de « Comment l'appliquer » sont des adaptations [H] des durées d'interface.
- Vidéos non lues : Ben Marriott "Master Motion Design" (EyHO1liVCpo), Jake Bartlett "Top Easing Tools" (IIBqi3K32c4), Issara "Live Q&A" (v7UG64yhYHc, 1 h).
- Pas de test A/B sur des reels réels : tout reste à valider.

## Tableau des sources
| # | Source + URL | Niveau | Sujet | % lu |
|---|---|---|---|---|
| 1 | GSAP, "Easing" https://gsap.com/resources/getting-started/Easing | P | in/out/inOut, `power1.out` pour l'UI | page entière, extraction automatique |
| 2 | GSAP, "Eases" https://gsap.com/docs/v3/Eases/ | P | familles, ease par défaut | page entière, extraction automatique |
| 3 | Google Material 3 (material-components-android, Motion.md) https://raw.githubusercontent.com/material-components/material-components-android/master/docs/theming/Motion.md | P | jetons de durée, courbes | fichier entier, extraction automatique |
| 4 | IBM Carbon, Motion https://carbondesignsystem.com/elements/motion/overview/ | P | jetons, productive / expressive | page entière, extraction automatique |
| 5 | Nielsen Norman Group, "Executing UX Animations" https://www.nngroup.com/articles/animation-duration/ | P | 100-500 ms, entrée / sortie | page entière, extraction automatique |
| 6 | Issara Willenskomer, "UX in Motion Manifesto" https://uxmag.com/articles/creating-usability-with-motion-the-ux-in-motion-manifesto | P | easing "toujours", offset et delay | article entier ; aucun chiffre |
| 7 | Ben Marriott, "The #1 Skill All Animators Need" https://www.youtube.com/watch?v=LcWJKYbYvi8 | P | anticipation, regard, courbes | environ 98 % |
| 8 | Ben Marriott, "This Animation Technique Works Every Time" https://www.youtube.com/watch?v=ythBGTLjot8 | P | match cut 100 à 105 % | environ 95 % |
| 9 | Ben Marriott, "After Effects Smooth Transitions pt.1" https://www.youtube.com/watch?v=UVDpgP7sRbw | P | retirer un élément au pic de vitesse | environ 63 % (jusqu'à 7:01 sur 11:09) |
| 10 | Jake Bartlett, "Beautiful easing curves in After Effects" https://www.youtube.com/watch?v=6zrEKEuJGKs | P | niveaux d'easing | environ 75 % (jusqu'à 7:20 sur 9:48) |
| 11 | Jake Bartlett, "The LAST graph editor tutorial you'll ever need" https://www.youtube.com/watch?v=7pOCtlrrE3Y | P | easing = répartition des images | environ 50 % (jusqu'à 12:49 sur 25:10, dont 2 min de sponsor) |
| 12 | School of Motion, "The Power of Animation Principles" https://www.youtube.com/watch?v=mT2Fv5bF6Ik | S | 12 principes (paraphrase) | environ 15 % (les 3 premières minutes utiles ; le reste = tutoriel After Effects) |
| 13 | Calcul d'équivalence cubic-bezier vers GSAP (script de calcul) | C | table des courbes | 14 courbes |
| 14 | Disney, "The Illusion of Life" | - | 12 principes | 0 % |
