# Le moteur (build.mjs, HyperFrames) : à lire avant de modifier un script ou quand un rendu casse

## Ce que fait build.mjs
- Sous-titres : 1-3 mots, <= 16 caractères, police de la DA (Montserrat 700 par défaut) en majuscules blanc 52 px, hauteur `subzone.py` (sous le col), mots forts en serif italique blanc 132 px seuls à l'écran ; cachés sous les cartons liste. Coupe de chaque phrase cherchée au meilleur endroit (plus de « UN BON / COUP », « CE N'EST / PAS »). Interdits : texte >= 60 px, mot fort en couleur, pop, mot par mot, mot fort sur la ligne d'un sous-titre normal.
- Caméra : zoom lent (1,4 s, sinusoïdal) seulement quand l'idée change (fin de phrase + >= 5 s dans le hook 0-7 s, >= 8 s ensuite), alternance large (1.0) / serré (1.07) + dérive lente, jamais de saut de cadre ni de coup de zoom. `"zoom": false` = cam fixe.
- Sorties douces : inserts et chiffres s'effacent en 0,25 s, listes / preuves / CTA en 0,3 s (`power2.in`), seulement s'il reste >= 1,5 s de face cam derrière (sinon coupe franche enchaînée, anti-flash). Sous-titres et b-rolls : coupe sèche.
- Anti-flash : entre deux pleins écrans (liste, preuve, CTA, B-roll, carton minimaliste), le moteur enchaîne direct ou garde >= 1,5 s de face cam (il affiche ce qu'il corrige).
- Chiffres : police de la DA graisse 600, 440 px, blanc, en haut, entrée flou → net ; la vidéo détourée passe devant (même zoom que la cam).
- Listes : fond dégradé de ta couleur foncée, titre + 2e ligne serif italique, éléments en 2 colonnes qui apparaissent un par un avec halo.
- B-rolls : plein écran au-dessus de la cam, sous les sous-titres, légère poussée 1.12 → 1.02.
- Minimaliste (`plan.mini`) : cartons (z 20, coupe sèche, mots calés sur la voix), icônes et captures (z 8, entrée 0,3-0,4 s expo, sortie sèche, tracés `strokeDashoffset`).
- Hook / mots géants / preuves / CTA : mouvements expo et ease-in-out, flou → net, jamais de rebond ni de flash. 1 seul accent (`colors.accent` de la DA = la couleur principale de ta marque). Sons écrits dans `cues.json` et mixés tout seuls par `mix.py`, filtrés par `config.json` → `sfx_auto` (priorité : impact, riser, sub drop, liste, chiffre, feuille CTA) et `sfx_gap` 1,5 s. Clics, frappe, pop, tic, whoosh de B-roll et aspiration = coupés (« parasites »). Un SFX dont le fichier est absent de `~/Documents/Contenu/medias/sfx/` est simplement sauté.

## D'où viennent polices et couleurs
`scripts/reglages.py da` assemble : valeurs par défaut du skill → `marque.json` (couleur principale = accent des blocs, couleur foncée = fonds des cartons liste, police de titre si elle est fournie dans `fonts/`) → bloc `da` de `~/Documents/Brain/00-Moi/montage.json` (Style Lab ou à la main). Un plan peut encore écraser : `plan.colors`, `plan.fonts`, `plan.subSize`, `plan.zoomGap`, ou `plan.da` (chemin d'un .json complet). Polices fournies (OFL) : Montserrat, Inter, Oswald, Poppins SemiBold, Bebas Neue ; serif italiques : Instrument Serif, Playfair Display, DM Serif Display, Bodoni Moda (`fonts/scales.json` = facteur de taille par police étroite ou large).

## Zones mortes appliquées par élément
Captures minimalistes posées à >= 278 px ; cartons liste : texte de 43 px réduit tout seul (37 px pour 18 lignes) pour tenir entre 540 et 1 480 px ; CTA : touches, champ et commentaires au-dessus de 1 480 px et à 65 px des bords (3 commentaires visibles au lieu de 4, clavier un peu plus petit), le fond de la feuille et la plaque grise du clavier descendent jusqu'en bas (décor) ; tout sous-titre plafonné à 1 427 px, tout mot fort à 1 337 px. Green screen : boîtes des blocs motion dans `MOBOX` (voir `styles/green-screen.md`). Contrôle : `node $S/zones.mjs .`.

## Règles HyperFrames (sinon le rendu casse)
- Vidéos `muted` et statiques dans le HTML ; le son est collé par `mix.py` (HyperFrames tronque l'audio).
- Jamais animer un élément `.clip` directement : animer un wrapper.
- Visibilité = 4 `fromTo` qui se suivent (fonction `V`), jamais `set()`/`to()` : le rendu parallèle saute dans le temps.
- Déterministe : pas de `Math.random`, `Date.now`, réseau.
- Tracé SVG (`strokeDashoffset` avec `pathLength="1"`) : toujours `autoRound:false` (déjà automatique dans `F()`). Sinon GSAP arrondit au px entier et le tracé saute de vide à plein.
- Compteur : chiffres `tabular-nums` dans une boîte de largeur fixe, durée >= 0,8 s (1,2-2 s idéal), le chiffre grossit de 55 % à 100 % pendant qu'il compte, suffixe APRÈS le compte (recette officielle HyperFrames `counting-dynamic-scale`).
- Avant de modifier `build.mjs` : sauvegarder le fichier hors du skill, puis rejouer 2 `plan.json` de test (un face cam simple, un minimaliste) avec l'ANCIEN et le NOUVEAU moteur : `index.html` et `cues.json` doivent sortir identiques (comparer avant / après, pas avec un `index.html` stocké, qui date d'un moteur plus vieux).
- Rythme : `plan.zoomGap` ou `DA.zoomGap` = [écart mini entre 2 zooms dans le hook, ensuite] ; posé = [5, 8] (défaut), nerveux = [2.5, 4].
