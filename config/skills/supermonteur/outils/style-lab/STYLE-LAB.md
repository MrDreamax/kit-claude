# Style Lab : ta DA de montage choisie sur TA rush, en 1 seul tour

Facultatif. À lancer une fois, si tu veux choisir au visuel tes polices, ta couleur, ta musique et ton rythme au lieu des réglages par défaut (Montserrat + Instrument Serif, blanc, accent = couleur de ta marque, rythme posé). Tu votes sur de vrais rendus de TOI ; ça écrit ta DA de montage dans `~/Documents/Brain/00-Moi/montage.json` (bloc `da`), que tous les montages suivants lisent. Une mise à jour du kit ne l'écrase jamais.
Durée : ~25 min dont ~10 min de rendu (jusqu'à 8 variantes).
Coût : 0 si tu sautes la section « ambiance » (4 images de toi, ~1 crédit Higgsfield, compte Higgsfield requis). Musique : tes morceaux Epidemic ou libres de droits (1 à 4), jamais de musique non licenciée.
5 sections, 1 seule variable par carte : **Ton ambiance** (facultatif, 4 images de toi), **Tes polices** (4 couples), **Ta couleur** (2 tirées de ta rush + ta marque + un bleu sobre), **Ta musique** (1 à 4 morceaux), **Ton rythme** (posé / nerveux).
Le reste est réglé par le skill et ne se vote pas : sous-titres au niveau du col, mot fort seul à l'écran, zones mortes Instagram, musique émotionnelle, zéro néon / chrome.

## 1. Matière (dossier `~/Documents/Contenu/montages/style-lab/`)
1. Une rush de toi en face cam. Étapes 1-3 de `SKILL.md` (cadrage, transcription, dérush) → `clip.mp4` + `words.json`.
2. Lire `words.json` : choisir un passage de **8-12 s** qui finit sur une phrase entière, avec **1 mot fort** et **1 punchline** de 2-3 lignes (tes mots, dits dans le passage). Noter les corrections de Whisper (`fixes`).
3. **Ambiance** (facultatif, Higgsfield branché) : 3 images nettes de ton visage tirées de la rush → `media_upload` + `curl PUT` + `media_confirm` → `generate_image_batch`, `gpt_image_2_5`, 9:16, les 3 réfs en `medias`, 4 prompts (Premium sombre, Cinéma chaud, Clair épuré, Énergique coloré). Chaque prompt finit par « Photorealistic, natural skin texture, keep identity exactly. No text, no logos, no floating objects, no neon, no glow. » **Vérifier que c'est bien ton visage sur les 4** (planche), sinon refaire avec d'autres réfs AVANT de te les montrer. Télécharger, réduire en JPG 720 px.
4. **Musique** (facultatif) : 1 morceau par émotion (motivation qui monte, dark cinématique, cordes cinéma, émotion piano), sans voix, coupé à la durée du passage. Avec Epidemic : `SearchRecordings` → `EditRecording` (`forceDuration`, WAV) → `DownloadRecordingEdit` → `~/Documents/Contenu/medias/musique/epidemic/` + 1 ligne dans `_LICENCE.txt`. Sans Epidemic : tes morceaux libres de droits dans `musique/libre/` (voir SKILL.md, section Musique). Aucun morceau = la section musique saute.
5. **Ta marque** : si `marque.json` a une couleur principale choisie par toi (nom rempli), la passer en `--brand`. Sinon demande ta couleur en 1 ligne (code couleur, ou la tirer de ton logo / profil). Aucune → la carte devient « Noir et blanc ».

## 2. Fabriquer le round (~10 min)
```bash
python3 ~/.claude/skills/supermonteur/outils/style-lab/round.py build --clip clip.mp4 --words words.json \
  --start <s> --end <s> --keyword <mot fort> --card "*ligne serif|ligne|*ligne serif" --card-at <s> --card-end <s> \
  --fixes '{"faute": "correction"}' --brand "#RRGGBB" \
  [--music m1.wav m2.wav m3.wav m4.wav --music-labels "Motivation|Dark cinématique|Cordes cinéma|Émotion piano"] \
  [--da-images da1.jpg da2.jpg da3.jpg da4.jpg] --out round
```
Sortie : `round/round.json` (sections + cartes + ce que chaque carte règle) et, par carte, `full.mp4` (avec le son) + `preview.mp4` (muet, léger), plus `round/planche-<section>.jpg`. Regarder les planches avant de publier : sous-titres lisibles, carton qui tient, rien hors zone.

## 3. La page de vote
1. Copier `outils/style-lab/style-lab.html` dans le dossier de travail, la publier en artifact : `capabilities: {"db": {}, "user": {}, "assets": {}}`, icône `palette`. URL dans `style-lab.url`.
2. Uploader dans les assets de l'artifact (`asset: true`, `file_paths` par lots de 25) : `preview.mp4` + `full.mp4` de chaque carte vidéo, l'image de chaque carte ambiance. Garder l'id de chaque fichier.
3. `python3 round.py db --round round/round.json --assets assets.json --handle <ton pseudo Insta, facultatif>` écrit les documents et la liste `writes`. Les passer en UN `ArtifactData` `batch`.
4. Vérifier : `ArtifactData list` de `cards` = le nombre de cartes de `round.json`. Puis t'envoyer le lien en 1 ligne : « Une carte "Garder" par section, puis "Envoyer mon avis", puis écris done ici. »

## 4. Verrouiller (quand tu écris « done »)
1. `ArtifactData list` de `submissions` → la plus récente dans `vote.json` (0 soumission : lire la collection `notes`, et demander en 1 ligne si c'est fini).
2. `python3 round.py lock --round round/round.json --vote vote.json` → met à jour le bloc `da` de `~/Documents/Brain/00-Moi/montage.json`.
   Code 3 = une section a 0 ou plusieurs « Garder » : la trancher en QCM dans le chat (option recommandée = ta carte « Peut-être », sinon la 1re = le défaut), puis relancer avec `--pick section=carte`.
3. Lire tes notes (le script les affiche) : un réglage demandé (« plus gros », « plus foncé ») → l'appliquer dans le bloc `da` (`subSize`, `colors`…) et le dire en 1 ligne.
4. Une ligne dans le carnet `~/Documents/Brain/00-Moi/regles-agents/supermonteur.md` : « Style Lab : polices = …, couleur = …, rythme = … ».

## Plan B (la page ne garde rien : elle affiche « Cette page ne joint pas Claude »)
Montrer `round/planche-<section>.jpg` une par une et poser 1 QCM par section dans le chat (les vidéos avec son : donner le chemin de `full.mp4`), puis `lock` avec un `--pick` par section (sans `--vote`).

Crédit : adapté du modèle gratuit Style Lab de Shaan Johari (@viashaan, https://instagram.com/viashaan).
