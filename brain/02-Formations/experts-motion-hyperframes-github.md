---
description: "Meilleures skills motion design HyperFrames trouvées sur GitHub (14/10) : top 8, techniques à reprendre avec fichier + ligne, incompatibilités DA."
type: formation
statut: actif
sujets: [montage]
---
# Skills motion design HyperFrames sur GitHub (recherche du 14/10/2026)

Rien installé, rien rendu, rien testé.

## Version
- HyperFrames est en 0.8.158 (vérifié npm 14/10). Le moteur du skill supermonteur tourne en 0.6.81 (juin 2026).
- Toutes les skills ci-dessous visent la 0.8.x. Les recettes GSAP/CSS se transposent. Les commandes CLI (`hyperframes check`) et les blocs du registre : à vérifier en 0.6.81.

## Top
| # | Repo | Étoiles | Verdict | Apport |
|---|---|---|---|---|
| 1 | heygen-com/hyperframes (skills officielles) | 63 593 | Reprendre | ~50 recettes GSAP (compteurs, barres, courbe tracée, flou de profondeur, cascades), doctrine "smooth beats bouncy", texte derrière le sujet |
| 2 | audrey-560/hyperframes-cinematic-caption | 63 | Reprendre | Hiérarchie sous-titres support/anchor/hero, budget d'occlusion du mot derrière la tête |
| 3 | Tejashmakwana/motionmaxxing | 474 | Piocher | Durées et eases mesurées sur 4 288 mouvements pro (médiane 0,33 s), règles de compteurs |
| 4 | nateherkai/herk-edit-kit | 1 464 | Piocher | Chiffres mesurés sur 27 reels (plans 1,1-1,4 s, accent serif 5-20 % des blocs) |
| 5 | gquthier/autonomous-shortform-facecam-editing | 11 | Piocher | Une carte par phrase, archétypes de cartes, pièges HyperFrames |
| 6 | kurbaitaev/ghost-editor | 70 | Piocher | Écran derrière la tête détourée (famille "Toi + une source") |
| 7 | heygen-com/hyperframes-community-skills | 202 | Piocher peu | Captions en profondeur, trop démonstratif |
| 8 | pycodebr/heditor | 65 | Marginal | Dimensions d'un HUD REC (thriller.md) |

## Techniques à reprendre (chemins relatifs au dossier de téléchargement)
1. Eases : `power3.out` par défaut, ressort amorti sans dépassement (`springEase`). heygen-com__hyperframes/skills/hyperframes-animation/adapters/gsap-easing-and-stagger.md L14-21, L59-136.
2. Flou → net : "flouter l'approche, atterrir net, tenir". hyperframes-animation/references/motion-blur.md L10-21 ; motionmaxxing references/type.md L118-121 (12 px → 0 en 4 images). Flou sur un wrapper, pas sur le mot (embedded-captions/SKILL.md L269).
3. Chiffre derrière la tête : taille ≈ largeur / (caractères x 0,72) (embedded-captions/references/typographic-moves.md L12-48) ; occlusion 10-30 %, jamais le visage (audrey references/style-system.md L128-145).
4. Sous-titres : support 52-80 px, anchor 76-112 px, hero 150-240 px ; zone sûre x 90-990, y 240-1520 (audrey style-system.md L36-72).
5. Compteur qui grossit de 40-60 % à 100 %, tabular-nums, jamais de back.out (hyperframes-animation/rules/counting-dynamic-scale.md).
6. Graphiques sobres : barres, jauge, anneau, étoiles fractionnaires, courbe tracée, ni grille ni légende (rules/stat-bars-and-fills.md, svg-path-draw.md, hyperframes-creative/references/data-in-motion.md).
7. Raccords : même axe, même sens, coupe à mi-mouvement, pause 0,3-0,75 s avant le climax, 2-3 types de transitions par film (.claude/skills/motion-doctrine/SKILL.md L33-65, L122-151).
8. Cascade pour listes et pastilles : power4.out, 60-80 px sur 0,16-0,20 s (rules/waterfall-entry.md L23-70).
9. Rack focus + zoom lent 1 → 1,04 (rules/depth-of-field-blur.md, multi-phase-camera.md).
10. Hook REC : REC à 34 px du haut, coins 74x74 px à 22 px, clignote toutes les 0,5 s (heditor references/styles/thriller.md). ÉCARTÉ le 14/10 : cotes d'un écran de surveillance, notre viseur respecte les zones sûres Instagram.

## À écarter (contraire à la DA)
Rebonds (spring-pop, back.out, word-pop), flash/glitch/strobe, néon, captions multicolores (herk 25-45 % colorés), camera-3d-captions (15 fps, whip-in).

## Non vérifié
Aucun rendu vu. Compatibilité 0.6.81 non testée. Scripts jamais lus. Chiffres des repos = leurs déclarations.

## Appliqué dans le skill supermonteur (testé)
- Bug racine corrigé : GSAP arrondissait les tracés SVG au px entier, les courbes et coches sautaient de vide à plein. `autoRound:false` dans `F()`.
- Compteurs des chiffres géants : 1,2-2 s, le chiffre grossit en comptant, suffixe après.
- Cascade des cartons liste : power4.out, 40 px, 0,2 s.
- Nouveaux blocs motion : `ring` (anneau + compteur) et `bars` (barres + barre accent qui compte).
- Non appliqué (contredit une règle du monteur) : 3 tailles de sous-titres, zéro dérive lente, sorties à 75 %. Listé en partie B de `regles-experts.md`.
