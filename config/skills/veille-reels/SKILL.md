---
name: veille-reels
description: Veille algorithmique de reels Instagram sur 3 marchés, dans cet ordre de priorité - anglophone, puis espagnol, puis français. 2 réglages mémorisés (ta cible, tes marchés) + à chaque lancement 1 filtre de recherche en 1 clic (sujet, format, marchés, période). 10 outliers à 10 000 likes minimum vérifiés, faits par de vrais créateurs face caméra qui parlent à ta cible exacte, avec le format à reproduire, livrés en tableau dans le chat + 1 page de miniatures cliquables (aperçu de chaque vidéo). Marche avec vidIQ + Apify (comptes payants) ou sans, avec Claude in Chrome ou des liens que tu colles. Use when "veille", "veille concurrentielle", "veille algorithmique", "trouve des reels viraux", "vidéos à reproduire dans ma niche", "marché américain", "marché anglophone", "marché espagnol", "marché français", "ce qui marche aux US / en Espagne", "autres marchés", "outliers", "change mes réglages de veille".
---

# Veille reels : 10 vidéos que tu peux refaire demain

## Carnet
Lis d'abord ~/Documents/Brain/00-Moi/regles-agents/veille-reels.md. S'il n'existe pas, crée-le avec l'en-tête `# Carnet de La Veille (veille-reels)`, une section `## Réglages` et une section `## Règles apprises`. Ses règles passent AVANT ce fichier. Si l'utilisateur corrige, note ou refuse ta veille (même en passant) : ajoute UNE ligne dans `## Règles apprises`, `JJ/MM/AAAA · correction · ce qui n'allait pas → règle`, et dis-le en une ligne.

## Démarrage : réglages + filtre de recherche
2 **réglages** mémorisés (**cible**, **marchés**) + 1 **filtre** posé à chaque lancement.
**Ordre des marchés, toujours : 1. anglophone (US, UK, Canada, Australie...) · 2. espagnol · 3. français.**
1. **Lis les réglages.**
   - **Cible** : ~/Documents/Brain/00-Moi/strategie-contenu.md, section « Ma cible » (qui, problème n°1 dans ses mots).
   - **Marchés** : ligne `Marchés` de la section `## Réglages` du carnet.
   - **Comptes de référence** (créateurs de sa niche, autres pays compris) : même fichier, section « Comptes de référence (pour la veille) ». Ils servent de point de départ et de repère de niveau.
2. **Réglage absent ou encore « À REMPLIR »** : demande-le UNE fois (boutons cliquables, tes propositions en « (Recommandé) », réponse libre possible). Cible : 1 proposition tirée de strategie-contenu.md et de voix-contenu.md si elles sont remplies, + 1 variante plus large. Marchés : les 3 en Recommandé. Écris ensuite la réponse à 2 endroits : dans le carnet (`## Réglages` : `Cible : ...`, `Marchés : ...`, `Mis à jour : JJ/MM/AAAA`) et dans strategie-contenu.md (remplace seulement les « À REMPLIR », n'écrase jamais ce que l'utilisateur a écrit ; les marchés vont en une ligne `Marchés de veille : ...` sous « Comptes de référence »). Cible encore vague après ça : propose le skill `ma-marque` (5 minutes).
3. **Filtre : 1 seul AskUserQuestion à chaque lancement**, 4 questions, tes réglages en option « (Recommandé) » pour que 1 clic suffise. Une question à laquelle le message répond déjà (« veille sur les objections ») : ne la pose pas.
   - **Sujet** : 3 sujets tirés de la cible, son problème n°1 en premier (Recommandé). Il peut écrire le sien.
   - **Format** (multiSelect) : Tous formats faciles (Recommandé) · Face caméra parlé (face caméra, questions-réponses, liste) · Mise en scène (vlog, POV, fiction, sketch) · Montage viral (tier list, comparaison en T, mauvais/bien/excellent).
   - **Marchés** (multiSelect) : anglophone · espagnol · français, dans cet ordre, ceux des réglages marqués « (Recommandé) ».
   - **Période** : 45 derniers jours (Recommandé) · 15 derniers jours (tendances fraîches) · 90 derniers jours (plus de choix, niche étroite).
   Si la cible vient d'être demandée (étape 2), la question Cible a déjà pris la place : fixe la période à 45 jours.
4. Dis le filtre retenu en 1 ligne (« Filtre : sujet …, format …, marchés EN > ES > FR, 45 j ») et lance.
- Le filtre vaut pour CETTE veille. Les réglages ne changent que sur « change mes réglages de veille » : repose Cible + Marchés, mets à jour le carnet et strategie-contenu.md.
- Jamais dans le filtre : le nombre de reels (10) et le seuil (10 000 likes). Ils sont fixes.

## Critères (tous obligatoires)
1. **Cible d'abord** : le créateur parle à ta cible, pas juste à la niche. Un reel « pour créateurs en général » ne passe que si le problème est celui de ta cible.
2. **≥ 10 000 likes**, vérifiés sur le reel lui-même (jamais l'estimation d'un outil de recherche).
3. **A performé vite** (45 derniers jours ou la période du filtre, outlier : vues très au-dessus de la médiane du créateur). La taille du compte est indifférente.
4. **Vrai créateur face caméra** : pas de clipping, pas de repost, pas de page de citations, pas de pub sponsorisée.
5. **Pas de stars** déjà connues (Dan Martell, Codie Sanchez, Hormozi, Gary Vee, Grant Cardone...).
6. **Format facile à refaire** par un débutant seul avec un téléphone.
7. Instagram uniquement, sauf demande contraire.

## Les outils (2 comptes payants, optionnels)
- **vidIQ** (compte payant sur vidiq.com, connecteur à brancher) : trouve les outliers (`vidiq_instagram_tiktok_outlier_search`, 5 crédits l'appel).
- **Apify** (compte à créer sur apify.com, usage payant, connecteur à brancher) : vérifie les likes de chaque reel (`apify/instagram-scraper`).
- Les clés restent dans les connecteurs : ne les colle jamais dans le chat ni dans un fichier. Un connecteur coupé dans la session : demande à l'utilisateur de le réactiver.
- **Sans ces comptes, tu fais la veille à la main (voie B ci-dessous).** Même tri, mêmes critères, même rendu. Elle est plus lente et ramène moins de candidats : dis-le, n'abaisse pas la barre.

## Méthode
1. **Anti-doublon** : récupère les reels déjà livrés :
   `find ~/Documents/Brain/04-Audits ~/Documents/Contenu/veille -type f \( -name '*veille-reels*.md' -o -name '*veille*.html' \) -exec grep -ohE "instagram.com/(reel|p)/[A-Za-z0-9_-]+" {} + 2>/dev/null | sed 's#.*/##' | sort -u`
   (find et pas un glob : sous zsh, un glob sans résultat fait planter TOUTE la commande et l'anti-doublon rend 0 sans rien dire.)
   Passe les codes dans `excludeContentIds` (voie A). Ajoute les stars et les créateurs déjà livrés dans `excludeCreatorHandles`. Voie B : écarte-les à la main.

### Voie A : vidIQ + Apify branchés
2. **1 recherche vidIQ par marché coché dans le filtre**, en parallèle, avec `vidiq_instagram_tiktok_outlier_search` :
   - `query` : le **sujet du filtre** vu comme le problème de la cible, écrit dans la langue du marché, + le **format du filtre** s'il n'est pas « tous » (« talking head » / « POV skit, vlog » / « tier list, comparison »). EXEMPLE FICTIF (cible : coachs sportifs indépendants) : « personal trainer explains why clients disappear after the first session, talking head ». ES et FR : la même chose traduite.
   - `audienceQuery` : EN `Culture/Region: English-speaking (US, UK, Canada, Australia); Global: true; Demographics: <cible en anglais>;` · ES `Culture/Region: Spanish-speaking (Spain, Mexico, Argentina, Colombia, Latin America); Global: true; Demographics: <cible en espagnol>;` · FR `Culture/Region: French-speaking (France, Belgium, Switzerland, Quebec); Global: true; Demographics: <cible en français>;`
   - `descriptionLanguage` ["en"], ["es"] ou ["fr"], `datePostedAfter` = J-45 (ou la **période du filtre**), `viewsMin` 150000, `followersMax` 600000, `resultsPerPlatform` 25, `collapseByCreator` true.
   - Ignore la partie TikTok de la réponse.
3. **Lecture** : la réponse est trop grosse pour le chat, elle est sauvée dans un fichier (parfois en JSON : le parseur le gère, passe-le tel quel). Résume-la avec `python3 -I ~/.claude/skills/veille-reels/scripts/parse_vidiq.py <fichier_EN> EN <fichier_ES> ES <fichier_FR> FR` (seulement les marchés lancés ; 1 bloc par reel : créateur, vues, x médiane, abonnés, code, concept, hook, style).
4. **Tri sur la cible** (et sur le format du filtre : écarte ce qui n'en est pas), puis vérifie 10 à 15 candidats d'un coup avec Apify `apify/instagram-scraper` (directUrls des reels, resultsType posts, resultsLimit 1), et lis avec `get-dataset-items` fields `shortCode,ownerUsername,likesCount,videoPlayCount,timestamp,paidPartnership,videoDuration,caption`. Coût : ~0,01 $.

### Voie B : sans vidIQ ni Apify
2. **Les candidats** viennent d'une de ces sources :
   - **Des liens de reels** que l'utilisateur colle (ceux qu'il a vus ou sauvegardés).
   - **Claude in Chrome** (skill `logiciels`) : ouvre Instagram dans le navigateur de l'utilisateur, déjà connecté (tu ne tapes jamais de mot de passe). Cherche le sujet du filtre avec des mots-clés dans la langue de chaque marché, puis parcours les comptes de référence de strategie-contenu.md. À vitesse humaine : 15 candidats maximum, pas de défilement massif. Si Instagram demande une vérification, arrête-toi et dis-le : tu ne la valides jamais à sa place.
3. **Vérifie chaque candidat à la main** : ouvre le reel et lis likes, vues, date, légende et compte. Compteur de likes masqué = non vérifiable = écarté. Médiane du créateur : compare aux vues de ses 6 derniers reels visibles sur sa grille (un outlier est très au-dessus).
4. **Tri sur la cible** et sur le format du filtre : écarte ce qui n'en est pas, puis applique les pièges ci-dessous.

### Pièges vus en vrai (les deux voies)
- Un outil de recherche gonfle les vues, parfois jusqu'à 14 fois. Les chiffres livrés sont TOUJOURS ceux relus sur le reel lui-même (Apify ou la page du reel).
- Likes / vues sous 0,5 % = vues boostées ou achetées : exclus (EXEMPLE : 1 054 likes pour 1 million de vues).
- Légende qui crédite un autre compte (« 📸 @... », « Créditos: @... », « Original creator ») sur un petit compte = repost : exclus, va voir l'original.

### Garder 10
5. Garde 10 reels, **répartis selon l'ordre des marchés** : 3 marchés = 5 EN, 3 ES, 2 FR · 2 marchés = 6 / 4 · 1 marché = 10. Un marché à sec : ses places vont au marché n°1, puis au n°2. Côté FR, mêmes règles qu'ailleurs : pas les grands noms déjà connus de la cible. Moins de 10 qui passent ? **1 seule recherche de plus** sur le marché n°1, sous un autre angle : reprends le format qui a le mieux marché dans la 1re (EXEMPLE FICTIF : « le coach filme la fin de séance avec un client » a donné 3 reels de plus), et exclus tous les codes et créateurs déjà vus. Toujours moins de 10 ? Livre ce que tu as et dis combien manquent, n'abaisse pas la barre.

## Rendu : tableau dans le chat + page de miniatures
- 1 tableau dans le chat, 1 ligne par reel, trié par marché (EN, puis ES, puis FR), puis ✅ avant ⚠️, puis likes : # · marché · cible (✅ parle à la cible / ⚠️ limite) · créateur · likes vérifiés · lien cliquable · hook traduit en français · format (noms FR des 25 formats : ~/Documents/Brain/02-Formations/ronny-mitchell-25-formats.md). Le # est le même que sur les miniatures.
- Au-dessus : 1 ligne filtre + « X reels passent, il en manque Y » + les recalés en 1 ligne (boost, repost, sous 10 000 likes). En dessous : 3 à 5 comptes à suivre.
- Pas de bloc « concept », pas de paragraphe, pas de script. PDF seulement si l'utilisateur le demande.
- Copie .md dans ~/Documents/Brain/04-Audits/AAAA-MM-JJ-veille-reels.md (c'est elle qui sert à l'anti-doublon ET aux miniatures) + 1 ligne en bas de ~/Documents/Brain/log.md. Son tableau garde ces colonnes : `| # | Marché | Cible | Créateur | Likes | Vues | Date | Lien | Hook en français | Format |` (modèle : ~/.claude/skills/veille-reels/exemples/echantillon-veille.md).
- **Miniatures (jamais un lien seul)** : `mkdir -p ~/Documents/Contenu/veille && python3 -I ~/.claude/skills/veille-reels/scripts/miniatures.py ~/Documents/Brain/04-Audits/AAAA-MM-JJ-veille-reels.md ~/Documents/Contenu/veille/AAAA-MM-JJ-veille.html`. Le script lit le tableau, récupère la couverture de chaque reel depuis son code (0 crédit, quelques secondes) et écrit 1 page autonome, à tes couleurs, tes polices et ton nom (~/Documents/Brain/00-Moi/marque.json) : 1 carte par reel (miniature 9:16 cliquable, n°, marché, likes, vues, créateur, format, hook). Il doit répondre « 10/10 miniatures OK » ; sinon la carte reste cliquable avec « aperçu indisponible », dis combien en 1 ligne.
- Ouvre la page juste après le tableau (SendUserFile si disponible, sinon `open <fichier>`), et donne son chemin.

En cas d'échec (connecteur coupé, recherche vide, Instagram qui bloque) : une ligne dans ~/Documents/Brain/04-Audits/erreurs-taches.md (date, tâche, erreur) et dis-le en une ligne.
