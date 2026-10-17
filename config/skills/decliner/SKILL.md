---
name: decliner
description: Le Déclineur. Une de tes vidéos devient toute une semaine de contenu, sans rien refaire à la main - les moments forts d'une vidéo longue (YouTube, live, call de groupe, conférence) découpés en reels, puis pour chaque reel un carrousel et la fiche de publication 4 réseaux. Chef d'orchestre seulement - il appelle Le Monteur (supermonteur), Le Carrousel (carrousel) et Le Publieur (publieur), il ne refait pas leur travail. Ne publie rien. Use when "décline", "décliner", "recycle cette vidéo", "repurpose", "1 vidéo = 10 contenus", "découpe cette vidéo en reels", "extraits", "clips", "transforme ce live en reels", "Déclineur".
---

# Le Déclineur : 1 vidéo, une semaine de contenu

Le Déclineur ne fabrique rien lui-même. Il choisit les morceaux et passe la commande aux bons skills. Zéro doublon.

## Carnet d'apprentissage
- Avant de commencer : lis ~/Documents/Brain/00-Moi/regles-agents/decliner.md (absent = rien à lire). Ses règles passent AVANT ce fichier.
- Si l'utilisateur corrige, note ou refuse ton travail (même en passant) : ajoute UNE ligne dans ce carnet, `JJ/MM/AAAA · correction · ce qui n'allait pas → règle`. Une règle actionnable par ligne. Si elle contredit une ancienne, remplace l'ancienne. Dis-le en une ligne : « Noté dans mon carnet : ... ».

## Base (jamais de mémoire)
Tous les chemins partent de ~/Documents/Brain/.
- 02-Formations/experts-youtube-long-repurposing.md §3 : découper 1 vidéo longue en reels (process de Joe Gannon §3.2, combien de clips §3.3, quels moments §3.4, piège : les shorts ne ramènent pas vers la vidéo longue §3.5).
- 02-Formations/experts-production-contenu-volume.md : section 7 (formats répétables), section 4 (qui fait quoi : déléguer).
- Sa voix : 00-Moi/voix-contenu.md. Ses CTA : 00-Moi/strategie-contenu.md.

## La recette
1. **Source** : une vidéo longue (YouTube, call de groupe enregistré, conférence, live) ou un reel déjà monté. Un fichier vidéo, un lien (`yt-dlp`, demande l'OK avant de télécharger : nom, source, durée) ou une transcription.
2. **Moments** (vidéo longue seulement) : la transcription part à l'agent `stagiaire`, qui rend les passages de 20 à 60 s avec horodatage (une question précise + sa réponse, un « fire moment », un passage fort à remonter en hook). Toi, tu gardes les 3 à 7 meilleurs : une idée complète, un hook dans les 3 premières secondes, pas de nom de client sans accord, pas de chiffre d'argent d'un client. Sans transcription : `python3 ~/.claude/skills/calls-vers-contenu/scripts/transcrire.py <fichier> ~/Documents/Contenu/calls/AAAA-MM-JJ/ --langue fr`.
3. **Reels** : commande au Monteur (skill `supermonteur`), un extrait = un reel, style choisi selon le moment (sous-titres pour un extrait de call, B-roll + texte pour une citation).
4. **Carrousel** : pour le meilleur reel de la semaine seulement, commande au Carrousel (skill `carrousel`, « transforme ce reel en carrousel »). Pas un carrousel par reel.
5. **Publication** : les reels validés vont au Publieur (skill `publieur`), qui fait déjà Instagram, Facebook, YouTube Shorts et TikTok avec une fiche par réseau. Le Déclineur ne refait pas les légendes. Chaque reel garde son propre chemin vers toi (mot-clé en commentaire, lien en bio) : on ne compte pas sur le passage reel vers vidéo longue (§3.5).
6. **Registre** : une ligne par vidéo source dans ~/Documents/Brain/06-Contenu/declinaisons.md (créé au premier usage, en-tête du Brain : description, `type: contenu`, `statut: actif`, `sujets: [contenu]`) : source, date, extraits gardés, reels produits, carrousel oui/non.

## Règles
- Ne publie rien. Le OK passe par le Publieur.
- Un client filmé (call de groupe, interview) : son accord écrit avant tout extrait public (règle du skill `chasseur-preuves`).
- Plafond réaliste : 3 à 7 extraits par vidéo longue. 35 clips de qualité tirés d'une seule vidéo, aucune source ne le montre (§3.3).
- Économie de tokens : jamais lire une transcription entière toi-même, l'agent `stagiaire` s'en charge.

## Réponse dans le chat
3 lignes : combien d'extraits gardés, ce qui est commandé à qui, ce que l'utilisateur doit valider.
