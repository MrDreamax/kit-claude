# Cut Notes : retours image par image

Page de revue : tu regardes ton reel, tu tapes un commentaire, la note s'accroche à l'image exacte. Claude lit les notes et corrige. Outil créé par Cyril MrDreamax (byStratosphere, @mrdreamax.business).
Fichiers : `cut-notes.html` (la page, aucun envoi hors Google Fonts), `review_copy.sh` (copie légère pour la page).
Il faut les artifacts de Claude (claude.ai). Sans artifact : plan B en bas.

## Quand
Après chaque rendu à faire relire (étape 8 du SKILL livrée), ou quand l'utilisateur dit « review » / « je te fais mes retours ».

## Round 1
1. Copier `cut-notes.html` dans le dossier du reel (l'outil Artifact ne publie que depuis le dossier de travail).
2. Publier ce fichier en artifact, `capabilities: {"db": {}, "user": {}, "assets": {}}`, icône `video`. Écrire l'URL dans `cut-notes.url` du dossier du reel. **Un seul artifact par vidéo**, réutilisé à chaque round.
3. Copie de revue : `bash ~/.claude/skills/supermonteur/outils/cut-notes/review_copy.sh final.mp4 review.mp4` (sort chemin, taille, fps). Code 2 (> 15 Mo) : pas d'upload, donner à l'utilisateur le chemin de `final.mp4` pour qu'il le glisse dans la page.
4. Uploader `review.mp4` dans les assets de l'artifact (Artifact, `asset: true`), puis écrire le doc `review/current` (ArtifactData `set`) : `{"src": "<url de l'asset>", "name": "<nom>", "fps": <fps>, "round": 1}`.
5. Vérifier : ArtifactData `get` de `review/current` + `list` de `notes`. Puis envoyer le lien en une ligne.

## Quand l'utilisateur écrit « done »
1. Lire la collection `notes` (ArtifactData `list`), garder le round courant. Chaque note : `tc` (HH:MM:SS:FF), `t` (secondes), `text`, `status`.
2. **« done » avec 0 note ne veut PAS dire validé** : demander en une ligne s'il a laissé des retours (une note tapée sans Entrée peut se perdre ; la page l'enregistre en quittant le champ, mais vérifier).
3. Montrer 1 ligne par note ouverte = ce que tu vas changer, attendre l'OK (plan avant chaque modification).
4. Appliquer chaque note `open` par retouche ciblée (plan.json, remix audio, re-rendu). Ne toucher à RIEN d'autre.
5. Mettre à jour chaque note (ArtifactData `update`) : `{"status": "fixed", "reply": "<ce que j'ai changé, 1 ligne>"}`, ou laisser `open` avec `reply` = pourquoi je n'ai pas pu.
6. Re-rendre, refaire les étapes 7 et 8 du skill, puis round suivant : nouvelle copie de revue, upload, `review/current` avec `round` + 1 (même artifact, URL dans `cut-notes.url`).
7. Chaque note = une règle générale dans le carnet `~/Documents/Brain/00-Moi/regles-agents/supermonteur.md` (boucle de l'étape 9).

## Rappels
- Les notes décrivent un ressenti (« j'ai décroché ici ») : c'est à Claude de trouver la correction.
- Notes et vidéos de revue restent dans ton compte Claude (artifact privé).
- Plan B sans artifact : ouvrir `cut-notes.html` dans un navigateur, glisser la vidéo, bouton « Copy for Claude », coller dans le chat.
