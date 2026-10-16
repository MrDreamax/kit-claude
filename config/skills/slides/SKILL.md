---
name: slides
description: Le Projectionniste. Fabrique tes slides 16:9 1920x1080 à tes couleurs et à tes polices (marque.json) pour (1) une vidéo YouTube (audit de compte, tableau blanc, prof) en majuscules + mot fort en italique, (2) un webinaire qui vend (slide méthode fil rouge, liste révélée point par point, captures réelles cerclées à la main, slide de clôture avec valeur empilée, compte à rebours et un seul bouton). Une idée par slide, règles de la fiche experts du Brain, alertes automatiques (trop de mots, texte qui déborde, valeur totale sous le prix). Livre deck.html à présenter en plein écran, deck.pdf, les PNG pour le montage et une planche. Jamais d'image IA, ne publie rien. Use when "slides", "fais-moi des slides", "deck", "présentation", "diapo", "PowerPoint", "Keynote", "slides YouTube", "slides pour ma vidéo", "slides de webinaire", "webinaire", "masterclass", "conférence", "slide d'offre", "slide de clôture".
---

# Le Projectionniste : des slides qui se lisent en 2 secondes

Une idée par slide, un mot fort, beaucoup de blanc. Les couleurs et les polices viennent de `~/Documents/Brain/00-Moi/marque.json` : change ta DA (skill `directeur-artistique`), les slides suivent. Tant que tu n'as pas fait ta DA, elles sortent en bleu et blanc neutre : propose-la en 1 ligne, sans bloquer.
Référence technique : `exemples/youtube-audit-bio.json` et `exemples/webinaire-test.json` (EXEMPLES FICTIFS, tous les types de slide). La capture d'exemple `exemples/capture-exemple-fictive.png` est un faux compte dessiné pour la démonstration.

## Carnet d'apprentissage
- Avant de commencer : lis `~/Documents/Brain/00-Moi/regles-agents/slides.md` (absent = rien à lire). Ses règles passent AVANT ce fichier.
- Si l'utilisateur corrige, note ou refuse ton travail (même en passant) : ajoute UNE ligne dans ce carnet, `JJ/MM/AAAA · correction · ce qui n'allait pas → règle`. Si elle contredit une ancienne, remplace l'ancienne. Dis-le en une ligne : « Noté dans mon carnet : ... ».

## Le modèle
| Élément | YouTube | Webinaire |
|---|---|---|
| Format | 16:9, 1920x1080 | 16:9, 1920x1080 |
| Couleurs | fond clair, couleur foncée, couleur principale (1 seul accent) de marque.json. Seule la slide `section` est sur fond foncé | pareil + une couleur pour le bouton d'achat seulement (jaune `#FFD43B` par défaut, réglable avec `couleurs.bouton` dans marque.json) |
| Polices | police de titres en majuscules 800 + mot fort en italique dans la police d'accent (Instrument Serif par défaut, réglable avec `polices.accent`) | police de titres en 900 + police de texte |
| Petit titre | majuscules espacées, couleur principale, petit | police de texte grise, petit |
| Changement de partie | slide `section` fond foncé | pareil |
| Interdit | image IA, photo stock, logo, numéro de slide, @ répété, prix en géant | pareil |

## Ce qu'il te faut
Google Chrome et Python 3 avec Pillow (`pip3 install pillow`) : skill `logiciels` si besoin. Rien d'autre. Polices fournies hors ligne : Montserrat, Archivo, Inter, Instrument Serif (licences libres OFL). Toute autre police de marque.json vient de Google Fonts : Internet requis au montage ET quand tu ouvres `deck.html` (le moteur alerte si une police ne charge pas).

## Étapes (⏱ ~10 min pour une vidéo YouTube, ~45 min pour un webinaire d'1 h : annonce-le au début, dis le temps réel à la fin)

### 1. Cadrer (une seule question si ça manque)
Format (youtube / webinaire), sujet, durée, et la matière : script de la vidéo, plan du webinaire, transcription d'un appel, audit fait par `audit-insta`. Sans matière : demande-la, n'invente pas le contenu.

### 2. Lire avant d'écrire
- `~/Documents/Brain/02-Formations/experts-slides-webinaire-youtube.md` : la checklist de 15 règles en bas (obligatoire).
- `~/Documents/Brain/00-Moi/voix-contenu.md` (ton, tu ou vous, lignes rouges).
- Webinaire : le fond vient de `~/Documents/Brain/03-Livres/brunson-expert-secrets.md` (Perfect Webinar). Les prix et valeurs de l'offre viennent de l'utilisateur ou du skill `offre` (s'il est installé), jamais de toi.
- Preuves autorisées seulement : celles de `voix-contenu.md` (« Preuves à mettre en avant »), cas clients chiffrés SANS nom tirés du Brain, captures réelles. Rien d'inventé : une preuve qui manque s'écrit entre [crochets].

### 3. Écrire le plan (un fichier JSON dans le scratchpad)
Copie un exemple de `exemples/`, change `out` en `~/Documents/Contenu/slides/AAAA-MM-JJ-<sujet>` (sans `out`, c'est le dossier par défaut), puis écris les slides :
- Une idée par slide, 12 mots max (si tu as 3 points, fais 3 slides : les slides sont gratuites).
- YouTube : alterne phrase / capture / correction ; une `section` (reset visuel) toutes les 3 à 5 minutes ; titre = une phrase qui conclut (« Ta bio ne dit pas qui tu aides »), jamais un sujet (« Analyse de la bio »). Ce qui est écrit ne répète pas mot pour mot ce que tu dis.
- Webinaire : `attente` au début, thèse en une `phrase`, `methode` qui revient à chaque étape, `liste` révélée, une preuve après chaque point clé, `cloture` à la fin. Vise 150 à 250 slides pour 60 min (le moteur prévient si tu es loin).
- Captures : vraies captures seulement (fournies par l'utilisateur, faites par toi dans Chrome sur un profil public, ou celles de l'audit). Le compte d'un tiers : son accord, ou nom flouté. `cercle` = la zone à entourer en pixels de l'image d'origine [x, y, largeur, hauteur], `encre: "clair"` si la capture est sombre, `recadrage` pour couper l'image, `source` toujours.
- Compte à rebours : seulement si l'offre ferme vraiment (pas de fausse urgence). `demo: true` tant que l'utilisateur n'a pas validé les valeurs. `devise` : « € » par défaut.

### 4. Fabriquer
`python3 ~/.claude/skills/slides/scripts/slides.py <plan.json>` (environ 1,5 s par slide : un deck de 10 slides = 15 s, un webinaire de 200 slides = 3 à 5 min).
Il sort dans `out` : `deck.html`, `deck.pdf`, `png/01.png...`, `planche.png`, `plan.json`, et imprime les ALERTES.

### 5. Vérifier (jamais livrer sans avoir regardé)
- 0 alerte, ou chaque alerte expliquée à l'utilisateur (ex. valeurs de démo).
- `DÉBORDE` ou `TEXTE RÉDUIT` : coupe le texte, relance. Ne baisse jamais la taille à la main.
- Lis `planche.png`, puis ouvre en grand chaque slide avec une capture (le cercle tombe-t-il sur la bonne ligne ? la note cache-t-elle quelque chose ?). Corrige, relance.

### 6. Livrer
- Envoie `planche.png` (SendUserFile si disponible, sinon `open` le fichier), en 2 lignes : où sont les fichiers, ce qui reste à valider.
- Comment s'en servir : `deck.html` dans Chrome, touche F = plein écran, flèches ou clic = slide suivante (partage d'écran en webinaire). `png/` = à poser dans le montage (Premiere, CapCut ou le skill `supermonteur`). `deck.pdf` = à envoyer.
- Une ligne dans `~/Documents/Brain/log.md`. Ne publie jamais rien.

## Les types de slide (champs du plan)
| Type | Sert à | Champs |
|---|---|---|
| `attente` | début de webinaire, les gens arrivent | `kicker`, `a`, `c` |
| `phrase` | une idée, une thèse | `kicker`, `a` (ligne principale, `\n` = retour à la ligne), `b` (mot fort en couleur principale), `c` (petite ligne) |
| `section` | changement de partie, fond foncé | `kicker`, `a`, `b` |
| `correction` | avant barré → après en grand | `kicker`, `avant`, `a`, `b`, `c` |
| `liste` | points qui apparaissent un par un (l'ancien se grise) | `kicker`, `titre`, `items` (6 max, 8 mots max chacun), `revele` (true par défaut : 1 slide par point) |
| `methode` | le fil rouge : fini = petit et coché, en cours = géant, suivant = estompé | `kicker`, `etapes` (3 idéalement), `actuelle` (1, 2, 3) |
| `capture` | vraie capture + cercle à la main ; sans `a`, la capture seule en grand | `kicker`, `a`, `b`, `image`, `recadrage`, `cercle`, `note`, `encre`, `assombrir` (true), `source` |
| `cloture` | l'offre : valeur empilée, total plus gros que le prix, compte à rebours, un seul bouton | `kicker`, `items` [[libellé, valeur]], `total` (sinon la somme), `prix`, `devise`, `compte_a_rebours`, `bouton`, `lien`, `demo` |

## Technique
- Moteur maison : `scripts/slides.py` (plan → HTML + alertes) + `assets/deck.html` (gabarit : ajuste le texte qui déborde et le signale ; couleurs et polices injectées depuis marque.json). Chrome en ligne de commande mesure chaque slide, fait un PNG par slide (en parallèle) et le PDF.
- Polices en local dans `assets/fonts` : le dossier livré marche sans Internet tant que marque.json n'utilise que ces polices.
- Idée de départ : scène fixe 1920x1080 en HTML (projet frontend-slides, licence MIT). Aucun code copié.
