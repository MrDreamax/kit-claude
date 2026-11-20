# Cut Notes : retours image par image

Outil de Super Studio, créé. L'utilisateur regarde le rendu dans une page, tape un commentaire, la note s'accroche à l'image exacte. Claude lit les notes et corrige.
Fichiers : `cut-notes.html` (page, relue ligne par ligne : aucun envoi hors Google Fonts), `review_copy.sh` (copie de revue).

## Quand
**AUTOMATIQUE, dès que le montage est fini (v1 et chaque retouche), sans rien demander** : `python3 ouvre.py <dossier du reel>` fait les étapes 1 et 3 (page + copie de revue + numéro de tour), puis Claude fait 2, 4 et `Artifact open`. Aussi quand l'utilisateur dit « review ». Page en français, il écrit « suivant » (plus « done »).

## Round 1
1. Copier `cut-notes.html` dans le dossier du reel (l'outil Artifact ne publie que depuis le dossier de travail).
2. Publier ce fichier en artifact, `capabilities: {"db": {}, "user": {}, "assets": {}}`, icône `video`. Écrire l'URL dans `cut-notes.url` du dossier du reel. **Un seul artifact par vidéo**, réutilisé à chaque round.
3. Copie de revue : `bash ~/.claude/skills/supermonteur/outils/cut-notes/review_copy.sh final.mp4 review.mp4` (sort chemin, taille, fps). Code 2 (> 15 Mo) : pas d'upload, donner à l'utilisateur le chemin de `final.mp4` pour qu'il le glisse dans la page.
4. Uploader `review.mp4` dans les assets de l'artifact (Artifact, `asset: true`), puis écrire le doc `review/current` (ArtifactData `set`) : `{"src": "<url de l'asset>", "name": "<nom>", "fps": <fps>, "round": 1}`.
5. Vérifier : ArtifactData `get` de `review/current` + `list` de `notes`. Puis envoyer le lien à l'utilisateur en une ligne.

## Quand l'utilisateur dit « suivant » (1 : chemin court)
`ArtifactData list notes` avec `out_dir`, puis `python3 ouvre.py <dossier> --notes <out_dir>` : notes ouvertes du tour -> `/api/retour` + `/api/suivant` de SuperMonteur (le correcteur retouche seulement les moments notés), attente de la nouvelle version, nouvelle copie de revue, tour + 1. Puis upload + `review/current` + `Artifact open`, et chaque note en `fixed` avec la réponse lue dans `retours.json`. Pour l’utilisateur lui-même, la règle « plan avant modif » est remplacée par ce chemin (il note, on corrige).

## Ancien chemin, à la main (« done »)
1. Lire la collection `notes` (ArtifactData `list`), garder le round courant. Chaque note : `tc` (HH:MM:SS:FF), `t` (secondes), `text`, `status`.
2. **Pour l'utilisateur** (règle : plan avant chaque modif) : montrer 1 ligne par note ouverte = ce que je vais changer, attendre son OK. **Pour un client** (process étape 3) : appliquer direct.
3. Appliquer chaque note `open` par retouche ciblée (plan.json, remix audio, re-rendu). Ne toucher à RIEN d'autre.
4. Mettre à jour chaque note (ArtifactData `update`) : `{"status": "fixed", "reply": "<ce que j'ai changé, 1 ligne>"}`, ou laisser `open` avec `reply` = pourquoi je n'ai pas pu.
5. Re-rendre, refaire les étapes 7 et 8 du skill, puis round suivant : nouvelle copie de revue, upload, `review/current` avec `round` + 1 (même artifact, URL dans `cut-notes.url`).
6. Chaque note = une règle générale dans `feedback.md` (boucle 9).

## Rappels
- Les notes décrivent un ressenti (« j'ai décroché ici ») : c'est à moi de trouver la correction.
- Notes et vidéos de revue restent dans le compte Claude de l'utilisateur (artifact privé).
- Sans artifact : ouvrir `cut-notes.html` dans un navigateur, glisser la vidéo, bouton « Copy for Claude », coller dans le chat.


## Bouton « J'ai fini mes notes »
Il envoie les notes ouvertes à Claude (comments.sendToClaude) : la session qui regarde l'artifact les reçoit et corrige tout de suite, puis répond dans le fil. Publier avec capabilities {"db": {}, "user": {}, "assets": {}, "comments": {}}. Envoi impossible (chat fermé, refus) = message orange clair, notes gardées, « Corriger » dans le chat.
