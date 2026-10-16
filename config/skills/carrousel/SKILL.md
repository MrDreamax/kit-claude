---
name: carrousel
description: Le Carrousel. Fabrique un carrousel Instagram de 8 slides (1080x1440) à tes couleurs et à tes polices (marque.json) - une grande idée, copy écrit d'après la fiche experts du Brain et ta voix (fil d'une slide à l'autre, titre + 1 phrase), tes vraies photos aux teintes naturelles en alternance avec des illustrations 2D façon motion design dessinées en SVG (jamais d'image IA), couverture avec mot géant derrière la tête, dernière slide « Commente MOT ». Livre les PNG + planche + légende dans ~/Documents/Contenu/carrousels, ne publie jamais. Use when "carrousel", "carousel", "fais-moi un carrousel", "carrousel de la semaine", "transforme ce reel en carrousel", "carrousel sur X", "carousel maker".
---

# Le Carrousel : une grande idée, 8 slides, ta DA

Un carrousel apporte de la confiance et des enregistrements. Un seul sujet, un fil d'une slide à l'autre, ta tête sur la couverture. Le modèle ci-dessous est figé : applique-le, ne le redécide pas à chaque fois.
Référence technique : `exemples/exemple-v4.json` (EXEMPLE FICTIF : remplace les photos par les tiennes).

## Carnet d'apprentissage
- Avant de commencer : lis `~/Documents/Brain/00-Moi/regles-agents/carrousel.md` (absent = rien à lire). Ses règles passent AVANT ce fichier.
- Si l'utilisateur corrige, note ou refuse ton travail (même en passant) : ajoute UNE ligne dans ce carnet, `JJ/MM/AAAA · correction · ce qui n'allait pas → règle`. Si elle contredit une ancienne, remplace l'ancienne. Dis-le en une ligne : « Noté dans mon carnet : ... ».

## Avant le 1er carrousel
- Lis `~/Documents/Brain/00-Moi/voix-contenu.md` et `strategie-contenu.md`. Tant qu'ils contiennent « À REMPLIR » (cible, ton, CTA) : lance d'abord le skill `ma-marque`. Jamais de carrousel sur une voix inventée.
- Tes couleurs et polices : `~/Documents/Brain/00-Moi/marque.json`. Valeurs par défaut neutres (bleu et blanc) tant que tu n'as pas fait ta DA : propose le skill `directeur-artistique` en 1 ligne, sans bloquer.
- Tes photos : dossier `~/Documents/Contenu/medias/photos/`. Il est vide ou n'existe pas ? Demande UNE fois (bouton) où elles sont (ou dis-lui d'y mettre 15 à 30 photos de lui : visage net, tenues et lieux variés) et note-le dans le carnet.
- Le moteur a besoin de Google Chrome et de Python 3 avec `pip3 install pillow numpy onnxruntime` (skill `logiciels` si besoin). Premier lancement : il télécharge une fois un modèle de détourage de 15 Mo (GitHub). Sans lui la couverture marche quand même, le mot passe devant la tête.

## Le modèle (figé)
| Élément | Règle |
|---|---|
| Format | 3:4, 1080x1440, 8 slides par défaut (6 minimum, 10 maximum) |
| Ambiance | tes couleurs (marque.json) : fond clair, couleur foncée, couleur principale. Petites touches d'appoint (jaune, corail, menthe) : 2 à 4 par dessin, jamais plus |
| Polices | celles de marque.json : police de titres (gras) pour les titres, les majuscules de la couverture et le CTA ; police de texte pour les phrases. `"titre_style": "italique"` dans le spec pour des titres en italique |
| Alternance | slide photo / slide illustration (la couverture = photo) |
| Photos | tes VRAIES photos, variées (plusieurs séances), teintes naturelles, légère touche de ta couleur dans les ombres (`prep.py`) |
| Illustrations | 2D motion design dessinées en SVG (`art.py`) : fond clair, grand cercle de ta teinte, aplats, 2 à 4 petits éléments déco |
| Interdit | images générées par IA : trop IA, l'audience le sent. Pas de @, pas de numéro de slide tant que `pseudo` est vide dans marque.json (s'il est rempli, le moteur affiche « @pseudo · n/N » en bas à gauche) |
| Couverture | photo + mot géant DERRIÈRE la tête + 1 ligne en majuscules, 7 mots max au total |
| Slides | 1 idée par slide : titre + 1 phrase courte (ou liste 1-2-3 de 3 lignes courtes). Jamais de pavé |
| Fin | « Commente MOT » + la ressource promise. Flèche de swipe partout sauf sur la dernière |

## Étapes (⏱ ~25 min : annonce-le au début, dis le temps réel à la fin)

### 1. La grande idée (une seule par carrousel)
Dans l'ordre : ce que l'utilisateur demande ; un sujet de la veille carrousels (`~/Documents/Brain/04-Audits/*veille-carrousels*.md` s'il en existe : on copie le sujet et la structure, jamais la posture) ; un script de reel validé (`06-Contenu/`) ; une vraie question de client (`06-Contenu/questions-clients-*.md`).
Le sujet doit toucher un problème de sa cible (`strategie-contenu.md`).
Mot-clé de fin : un freebie de `strategie-contenu.md` qui EXISTE vraiment. Aucun ? Mets « [freebie à créer] » et dis-le, ou termine sur son autre CTA (réserver un appel, lien en bio). N'invente jamais une ressource.

### 2. Le texte
- Lis d'abord `~/Documents/Brain/02-Formations/experts-copywriting-carrousels.md` (méthode Chris Do : AIDA + titre ROT, fil par « … ») et `~/Documents/Brain/00-Moi/voix-contenu.md`.
- Couverture : écris 10 titres (Résultat, Objection ou Temps, chiffre si possible), garde le meilleur. Elle et la slide 2 doivent accrocher seules.
- Chaque slide ouvre la suivante (« … », question, « mais »). Une slide de preuve vers la fin.
- Preuves autorisées seulement : celles de `voix-contenu.md` (« Preuves à mettre en avant ») et les cas clients SANS nom tirés du Brain. Rien d'inventé : une preuve qui manque s'écrit entre [crochets] et tu le dis.
- Voix : celle de `voix-contenu.md` (ton, tu ou vous, lignes rouges). Aucun concurrent nommé.
- Dernière passe : skill `anti-ia`.
- Légende : 4 à 6 lignes qui prolongent (pas un copier-coller des slides), finit par le CTA. 5 hashtags max.

### 3. Les photos (4 slides)
- Planches pour choisir : `python3 ~/.claude/skills/carrousel/scripts/planches.py <dossier_scratchpad> [sous-dossier ...]` (sans sous-dossier : tout `~/Documents/Contenu/medias/photos/`). Puis lis les planches (Read) et `index.json` pour les chemins.
- Jamais : photos où quelqu'un d'autre est au premier plan, photos de la vie intime (lignes rouges de `voix-contenu.md`), portraits retouchés ou générés par IA.
- Chaque photo doit coller à SA slide (ex. preuve = scène devant une salle, posture = sourire en tenue pro). Varie les séances.
- Couverture : la tête doit laisser de la place au-dessus (« tête y≈ » entre 300 et 450 dans la sortie). Photo trop serrée : prends-en une plus large ou baisse `zoom`.

### 4. Les illustrations (4 slides)
- `scripts/art.py` : `apples_grid` (tous pareils / `red_at` = celui qui est différent), `copies` (copier les gros comptes), `stairs` (3 étapes), `chart_up` (résultats, croissance), `chat` (DM, messages), `checklist` (erreurs, étapes). Elles prennent tes couleurs toutes seules.
- Sujet nouveau : écris une nouvelle fonction dans `art.py` (mêmes couleurs, `frame()`, dessin entre y 80 et 820, 2 à 4 éléments `deco`) et ajoute-la à `ARTS`. Ou un fichier `.svg` à côté du spec (`"svg": "mon-dessin.svg"`).

### 5. La description puis le montage
- Copie `exemples/exemple-v4.json` dans le scratchpad, adapte : `photos` (chemin + recadrage `fx`, `fy`, `zoom`), `slides`, `caption`, `hashtags`, `out` = `~/Documents/Contenu/carrousels/AAAA-MM-JJ-<sujet>`.
- `python3 ~/.claude/skills/carrousel/scripts/carrousel.py <spec.json>` (SANS `-I` : les scripts s'importent entre eux). ~1 min. Il prépare les photos, monte les 8 images avec Chrome, écrit `slide-1.png` à `slide-8.png`, `00-planche.png`, `legende.txt` et `spec.json`, et imprime des ALERTES.
- Les photos préparées sont gardées dans `_photos/` : relancer est rapide.

### 6. Vérifier (jamais livrer sans)
0 alerte, ou chaque alerte expliquée. Lis `00-planche.png`, puis en grand chaque slide douteuse. Contrôle :
- texte lisible, pas de mot seul sur une ligne (le moteur le dit ; force avec `<br>` et `&nbsp;`) ;
- mot de couverture lisible : la tête ne cache pas une lettre entière (ajuste `word_top`) ;
- illustration qui ne touche pas le texte ; photo qui colle au sujet de la slide ;
- bon mot-clé à la fin ; 8 PNG en 1080x1440.
Corrige la description et relance.

### 7. Livrer
- Envoie la planche (SendUserFile si disponible, sinon `open` le fichier) + 3 à 5 lignes : sujet, d'où il vient (veille, script…), ce qui reste à faire.
- Brain : 1 ligne en bas de `~/Documents/Brain/log.md`.
- Rappelle de vérifier que la réponse automatique aux commentaires (ManyChat ou autre) répond bien au mot-clé AVANT de publier.
- Ne publie et ne programme JAMAIS sans son feu vert explicite.

## Technique
- Moteur maison : description JSON -> HTML -> PNG avec Google Chrome en ligne de commande (rien d'autre à installer que Python et ses 3 modules). Polices Google Fonts : Internet requis au montage.
- `prep.py` : recadrage 3:4, étalonnage naturel, détourage local (Robust Video Matting, ONNX) : aucune photo ne quitte ton ordinateur. Modèle téléchargé une fois dans `~/.cache/supermonteur/` (partagé avec le skill monteur).
- Porte cash : un carrousel n'amène pas un client sous 7 jours. S'il y passe plus d'une demi-journée, dis-le une fois.
