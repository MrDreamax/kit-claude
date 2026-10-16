# Extraire des B-rolls stables d'un dossier de rushs

Tu as des heures de vidéo brute (voyage, bureau, tournage) et tu veux en sortir les bons plans de coupe : stables, nets, 3 à 10 s.
Tout se fait sur ton ordinateur, 0 crédit, quelques Mo de données. Prérequis : `pip3 install --user opencv-python` (en plus de l'installation de base du monteur).

1. `python3 analyse.py <dossier_rushs> <ana>` : tremblement image par image (même méthode et mêmes seuils que `scripts/broll.py` : moyenne <= 1.2, pic <= 6), luminosité, netteté. Compter ~10 min pour 1 h de 4K.
2. `python3 segments.py <dossier_rushs> <ana> <seg>` : passages stables de 3 à 10 s, visages (models/face_landmarker.task), 2 plans max par scène semblable, planches numérotées dans `seg/sheets/`.
3. Regarde les planches (Claude les regarde pour toi), puis écris `selection.json` : les plans gardés, leur thème, une action en kebab-case, le lieu, si une personne est visible (format dans l'en-tête de `export.py`).
4. `python3 export.py <seg> <dossier_rushs> selection.json [--dry]` : découpe, range dans `~/Documents/Contenu/medias/brolls/<thème>/`, vignettes, et ajoute les lignes à `_INDEX.csv` (copie de sécurité avant).
Piège : un rush horizontal garde son orientation (le nom du fichier le dit : `_H_`). Les rushs d'origine ne sont jamais modifiés.
