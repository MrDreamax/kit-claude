---
name: apple-design
description: Le Designer Apple. Fait des interfaces web qui se sentent « vivantes » comme chez Apple - animations à ressort, glisser / balayer / tiroirs fluides, élan au lâcher, matières translucides et profondeur, typo (interlettrage, interligne), mouvement réduit, les 8 principes de design Apple, et les 19 principes UX et animation (aussi pour le motion design vidéo). Sert à construire ou relire une page web, une app, un artifact, un formulaire, un deck HTML, une page de vente. Use when "design Apple", "façon Apple", "style Apple", "apple design", "plus fluide", "plus premium", "animation", "ça fait cheap", "rends ça plus pro", "glisser", "swipe", "tiroir", "bottom sheet", "ressort", "spring", "flou / verre", "glassmorphism", "typo", "relis le design de cette page", "motion design", "animation de site", "rends l'animation smooth".
---

## Règle n°1 : maquette d'abord
Avant de coder, monter, générer en volume ou exécuter quoi que ce soit : montre d'abord une MAQUETTE (une image, un écran, 1 slide, 10 s, 3 lignes) et attends que l'utilisateur la valide. Toujours PLUSIEURS versions (3 en général, ta recommandée en premier, chacune nommée en 3 mots) qui CHALLENGENT la direction artistique : 3 directions vraiment différentes (couleurs, typo, mise en page, ambiance), jamais 3 variantes du même style. Vote : un seul bouton « Garder celle-ci » (il en garde une, les autres sont jetées) + une note facultative. DEUX rounds avant validation : round 1 = aspect global, styles vraiment différents ; round 2 = plein de détails de la maquette gardée (plusieurs parties dans le même round, une option gardée par partie). Pas de validation = pas d'exécution. Vaut pour tout : site, tunnel de vente, PDF, slides, pubs.

## Qualité avant de montrer
Rien n'est montré sous 9/10 : fais relire ton travail par un juge séparé (un sous-agent qui ne l'a pas fait) avant chaque envoi, 3 tours max. Si ça n'atteint pas 9, donne la vraie note et ce qui bloque.

# Le Designer Apple

Adapté du skill apple-design d'Emil Kowalski (github.com/emilkowalski/skills), licence MIT, © Emil Kowalski. Source : talks WWDC d'Apple, surtout *Designing Fluid Interfaces* (2018), traduits pour le web (CSS, Pointer Events, `requestAnimationFrame`, librairie Motion / Framer Motion). Texte de la licence : fichier `LICENSE` de ce dossier.

Carnet à lire AVANT chaque mission : `~/Documents/Brain/00-Moi/regles-agents/apple-design.md` (absent = rien à lire). Une règle du carnet passe avant ce fichier. Si l'utilisateur corrige ou refuse ton travail, ajoute UNE ligne dans ce carnet : `JJ/MM/AAAA · correction · ce qui n'allait pas → règle`.

## Comment parler à l'utilisateur
- En français, ultra court. Il veut le résultat, pas la théorie.
- Échantillon d'abord : 1 écran ou 1 composant montré (capture), puis on étend.
- Charte de la marque avant tout : couleurs et polices viennent de `~/Documents/Brain/00-Moi/marque.json` et `da.md`. Ce skill règle le MOUVEMENT et la FINITION, il ne change pas les couleurs.
- Le code reste en anglais (c'est du code). Les explications, en français.

## L'idée en une phrase
Une interface semble vivante quand le mouvement part de la position actuelle à l'écran, garde la vitesse du doigt, projette l'élan vers l'avant, et peut être rattrapée et inversée à tout instant. Le ressort (spring) fait tout ça naturellement.

Apple sert 4 besoins : se sentir en sécurité, comprendre, réussir, avoir du plaisir. Chaque règle sert l'un des 4.

## 1. Réponse : zéro délai
- Réagir à l'appui (pointer-down), pas au relâché.
- Chasser chaque attente inutile : debounce, minuteurs, attente de transition, délai de 300 ms au tap.
- Pendant un glisser, un curseur ou un tiroir : l'écran suit 1 pour 1 tout du long, pas seulement à la fin.

```css
.button:active { transform: scale(0.97); transition: transform 100ms ease-out; }
```

## 2. Manipulation directe : collé au doigt
- L'objet suit le doigt en gardant l'endroit où on l'a attrapé (jamais de saut au centre).
- Pointer Events + `setPointerCapture` pour suivre même hors de l'élément.
- Garder l'historique des derniers mouvements (position + temps) pour connaître la vitesse au lâcher.

```js
el.addEventListener('pointerdown', (e) => {
  el.setPointerCapture(e.pointerId);
  const grabOffset = e.clientY - el.getBoundingClientRect().top;
});
```

## 3. Interruptible : LA règle n°1
- Jamais bloquer l'utilisateur pendant une animation. Il doit pouvoir rattraper un objet en vol et le renvoyer.
- Toujours animer depuis la valeur affichée à l'écran, jamais depuis la cible. Sinon : saut visible.
- Pas de transition CSS ni de `@keyframes` pour ce qui se touche au doigt : on ne peut pas les rattraper. Ressort à la place.
- Au demi-tour, garder la vitesse en cours (pas de « mur de briques »).
- Mouvement en 2D : un ressort pour X, un ressort pour Y.

## 4. Des ressorts, pas des durées fixes
Deux réglages :
- **Amortissement (damping)** : 1.0 = aucun rebond, arrêt doux. Moins de 1 = rebondit.
- **Réponse (response)** : vitesse pour atteindre la cible, en secondes. Ce n'est pas une durée.

Par défaut : amortissement 1.0 partout. Un peu de rebond (~0.8) seulement si le geste avait de l'élan (un lancer, un glisser lâché). Un menu qui rebondit tout seul = faux.

| Interaction | Amortissement | Réponse |
| --- | --- | --- |
| Déplacer (ex. vidéo flottante) | 1.0 | 0.4 |
| Rotation | 0.8 | 0.4 |
| Tiroir / feuille du bas | 0.8 | 0.3 |

```js
import { animate } from 'motion';
animate(el, { y: 0 }, { type: 'spring', bounce: 0, duration: 0.4 });      // défaut
animate(el, { y: target }, { type: 'spring', bounce: 0.2, duration: 0.4 }); // après un lancer
```

## 5. Passer la vitesse du doigt à l'animation
Au lâcher, l'animation repart à la vitesse exacte du doigt. Aucune couture visible.
Si la librairie veut une vitesse relative : `vitesseDoigt / (cible − position)`. Motion prend directement les px/s (option `velocity`).

## 6. Projeter l'élan
Ne pas aller au point d'arrêt le plus proche du lâcher. Calculer où l'objet irait avec son élan, puis choisir le point le plus proche de CE point-là.

```js
function project(v /* px/s */, d = 0.998) { return (v / 1000) * d / (1 - d); } // 0.99 = plus sec
const target = nearestSnapPoint(current + project(releaseVelocity));
animateSpringTo(target, { velocity: releaseVelocity });
```

## 7. Cohérence de l'espace
- Ça sort par où c'est entré. Entré par la droite = sort par la droite.
- Un menu, un popover, une feuille naît du bouton qui l'ouvre (`transform-origin` sur le bouton).
- Aller et retour : courbes miroir.

## 8. Annoncer la direction
Les images intermédiaires montrent déjà où ça va (Control Center « pousse vers le doigt »).

## 9. Bords élastiques
Au bout, résister de plus en plus au lieu de s'arrêter net.

```js
function rubberband(over, dim, c = 0.55) { return (over * dim * c) / (dim + c * Math.abs(over)); }
```

## 10. Détails des gestes
- Tap : surbrillance à l'appui, action au relâché. ~10 px de marge, annulable en glissant hors du bouton.
- Glisser : seuil de ~10 px avant de choisir la direction, puis 1 pour 1.
- Écouter tous les gestes possibles dès le 1er mouvement, puis couper les perdants.
- Double-tap seulement où il existe vraiment (il retarde le simple tap).

## 11. Fluidité image par image
- Animer seulement `transform` et `opacity`. `will-change` juste avant un mouvement.
- `requestAnimationFrame` = l'horloge de l'écran.
- Mouvement très rapide : un léger flou ou étirement lit mieux qu'un trait net.

## 12. Matières et profondeur
- Barres, menus, feuilles = couches translucides (`backdrop-filter: blur()` + fond semi-transparent), le contenu défile dessous.
- Matière sombre / lourde = zones de structure. Matière claire = éléments cliquables. Jamais deux couches claires translucides l'une sur l'autre.
- Grande surface = plus de flou + ombre plus profonde.
- Tâche qui bloque = voile sombre derrière. Panneau à côté = translucide sans voile.
- Texte sur verre : plus contrasté, un poil plus gras, un poil plus espacé. La couleur va sur une couche pleine.
- Pas de trait de 1 px sous une barre fixe : un léger fondu / flou là où le contenu passe dessous.
- Apparition d'un verre : animer flou + échelle ensemble, pas juste l'opacité.

```css
.toolbar {
  background: rgba(255,255,255,0.6);
  backdrop-filter: blur(20px) saturate(180%);
  border-top: 1px solid rgba(255,255,255,0.4);
}
```

## 13. Mouvement + son + vibration
1. Cause claire : le retour part de l'action réelle.
2. Même image : visuel, son et vibration au même instant.
3. Utile : seulement aux moments qui comptent (succès, erreur, validation). Trop = ignoré.

## 14. Mouvement réduit et accessibilité
- `prefers-reduced-motion: reduce` : fondus courts à la place des glissés et ressorts, pas de rebond.
- `prefers-reduced-transparency: reduce` : fonds pleins, pas de flou.
- `prefers-contrast: more` : fonds presque pleins + bordure nette.
- Éviter : grands fonds qui bougent, oscillations lentes en boucle, sauts de luminosité.

```css
@media (prefers-reduced-motion: reduce) { .sheet { transition: opacity 200ms ease; transform: none !important; } }
@media (prefers-reduced-transparency: reduce) { .toolbar { background: white; backdrop-filter: none; } }
```

## 15. Typo
- Interlettrage selon la taille : gros titres resserrés (≈ -0.02em), texte courant près de 0, tout petit texte un poil espacé. Jamais une valeur unique.
- Interligne inverse : serré sur les gros titres, aéré sur le texte.
- Hiérarchie = graisse + taille + interligne ensemble. Insister avec la graisse.
- Tailles en `rem` / `em` pour suivre la taille de texte de l'utilisateur.
- Police système d'abord (`system-ui`), sauf raison (ou police de la charte).

```css
:root { font: 100%/1.5 system-ui, sans-serif; }
.display { font-size: clamp(2rem, 5vw, 4rem); line-height: 1.05; letter-spacing: -0.02em; font-optical-sizing: auto; }
```

## 16. Les 8 principes Apple
1. **But** : décider ce qu'on NE fait pas. Chaque élément coûte du temps et de l'attention.
2. **Contrôle** : l'utilisateur choisit. Annuler facile ; confirmation seulement pour l'irréversible.
3. **Responsabilité** : agir dans son intérêt (vie privée, sécurité, surtout avec l'IA).
4. **Familiarité** : partir de ce qu'il connaît. Même aspect = même comportement = même place.
5. **Souplesse** : téléphone, ordi, tous les âges et capacités.
6. **Simplicité, pas minimalisme** : enlever l'inutile, mots simples, moins d'étapes, le plus important est le plus visible.
7. **Finition** : chaque espacement, timing, alignement est un choix qu'on peut défendre.
8. **Plaisir** : le résultat des 7 autres, pas des confettis ajoutés.

Règles pratiques :
- 4 retours : état, terminé, alerte, erreur. Valider dans le champ, pas à l'envoi.
- Chaque écran répond : où suis-je, où aller, qu'y a-t-il, comment sortir.
- Un réglage près de ce qu'il change. Besoin d'une étiquette pour l'expliquer = mal placé.
- Étiquettes précises (« Progrès », « Bibliothèque ») plutôt que « Accueil ».

## 16 bis. Les 19 principes UX et animation (sites ET motion design vidéo)
À appliquer dès qu'on anime quelque chose : page web, app, artifact, deck, ou motion design d'une vidéo.
1. **Exagération** : grossir un peu le retour pour marquer le moment (un clic qui « pop »).
2. **Partir du point d'origine** : ça s'ouvre depuis l'endroit cliqué, pas depuis le centre.
3. **Décalage** : les éléments arrivent l'un après l'autre (30 à 60 ms d'écart), jamais tous ensemble.
4. **Écraser et étirer** : ça s'écrase un peu à l'impact, ça s'étire en mouvement.
5. **Élastique** : tirer au-delà du bord étire, et ça revient en ressort au lâcher (voir 9).
6. **Seuil de Doherty** : réponse en moins de 400 ms, sinon montrer que ça charge.
7. **Anticipation** : un petit recul ou une charge juste avant le mouvement.
8. **Loi de Fitts** : ce qu'on clique souvent = gros et proche.
9. **Lent au début, lent à la fin** : jamais de mouvement linéaire, ça fait robot.
10. **Loi de Hick** : plus de choix = décision plus lente. Couper les options.
11. **Suite du mouvement** : les détails bougent encore un instant après l'arrêt du bloc principal.
12. **Arcs** : bouger en courbe, pas en ligne droite.
13. **Effet Von Restorff** : celui qui est différent se remarque. Une seule chose mise en avant par écran (jamais de faux badge « Le plus populaire », voir anti-vibecode).
14. **Durée** : animations d'interface sous 300 ms.
15. **Interruptible** : on peut changer d'avis en plein mouvement (voir 3).
16. **Action secondaire** : un petit détail qui soutient l'action principale (une coche qui brille après l'envoi).
17. **Volume** : donner de la profondeur aux choses plates (ombre, lumière, réaction au doigt).
18. **Fréquence d'usage** : plus on s'en sert souvent, moins on l'anime.
19. **Règle pic-fin** : on se souvient du meilleur moment et de la fin. Soigner les deux.

En motion design vidéo : 1, 3, 4, 7, 9, 11, 12, 16, 17 et 19 comptent le plus ; 6, 8, 10, 14 et 18 sont pour les interfaces.

## 17. Méthode
- Prototype cliquable plutôt que maquettes figées.
- Mouvement et visuel pensés ensemble, pas l'animation en couche finale.
- Revoir les animations au ralenti, image par image. Vérifier sur téléphone ET ordi.

## Vérification avant de livrer
1. Ouvrir la page dans le navigateur, capture ordi + capture téléphone (375 px).
2. Tester un glisser / un clic : ça répond à l'appui, ça se rattrape en vol.
3. Tester mouvement réduit (émulation) : pas de glissé, que des fondus.
4. Montrer la capture à l'utilisateur. Jamais « c'est fait » sans preuve.

## Mémo
| Besoin | Technique | Valeur |
| --- | --- | --- |
| Ressort par défaut | sans rebond | amort. 1.0, réponse 0.3-0.4 |
| Après un lancer | léger rebond | amort. ~0.8, réponse 0.3-0.4 |
| Point d'arrivée d'un lancer | projection | `pos + (v/1000)·d/(1−d)`, d ≈ 0.998 |
| Interrompre | partir de la valeur affichée | lire le transform à l'écran |
| Revenir ou valider | sens de la vitesse, pas la position | au lâcher |
| Bord | élastique | résistance progressive |
| Barre translucide | `backdrop-filter` | contenu dessous |
| Typo gros titres | resserrer | -0.02em |
| Mouvement réduit | fondu | `prefers-reduced-motion` |
