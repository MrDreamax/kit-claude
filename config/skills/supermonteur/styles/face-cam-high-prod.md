# FACE CAM · degré 3 : HIGH PROD (reel phare)

Lu après `SKILL.md`. Tout l'arsenal : chiffres géants, mots géants, listes, preuves, B-rolls, images, CTA. On peut couvrir la tête : B-rolls et/ou motion design plein écran pendant que la personne parle. La tête n'a pas besoin d'être à l'écran tout le temps.
Brief en plus : **Style** Sobre / Dynamique (plans plus courts, plus de B-rolls et zooms).
Étalon : un reel de référence que l'utilisateur t'a donné (voir « Références de style » dans `SKILL.md`), ou la version d'un monteur humain si elle existe pour ce rush ; sinon les règles d'experts. Le but : faire mieux que la référence, jamais la copier.

## 1 bis. Fiche univers (après l'étape 1 de SKILL.md ; Bruce Block, Deakins : l'univers du reel = celui du rush)
```bash
python3 $S/univers_check.py fiche clip.mp4      # univers.json + univers.jpg : palette, couleur de la lumière, noirs / hautes lumières, cadre
```
Compléter `univers.json` à l'œil (source de lumière, espace, ligne, forme), remplir `plan.colors` depuis la palette, mettre la lumière dans chaque prompt Higgsfield. `python3 $S/lookstats.py clip.mp4 --face` = mesure seule (bornes : noirs P1 1-8, P99 <= 235, néon < 0,5 %).

## 4. Champs plan.json du high prod (en plus des champs communs de SKILL.md)
```json
{
  "numbers": [{"text": "30", "start": 0.4, "end": 1.95},
              {"text": "99", "suffix": "%", "count": 99, "start": 16.6, "end": 18.35}],
  "lists": [{"start": 10.72, "end": 13.42, "title": ["50 façons de parler", "d'une seule idée"],
             "pages": [["1-Les problèmes autour du sujet", "..."], ["19-...", "..."]]}],
  "bullets": {"at": [30.1, 30.32, 30.54], "end": 32.2},
  "brolls": []
}
```
(EXEMPLE FICTIF : chiffres, titres et listes viennent TOUJOURS de ce que la personne dit.)
- **numbers** : chaque chiffre fort prononcé (30 secondes, 99 %, 800 vidéos) → chiffre géant derrière la tête, du début du mot à ~1.5 s. `count` = compteur qui défile. Aussi gros que possible, jamais coupé en haut ; le chiffre sort du sous-titre.
- **lists** : quand la personne cite une liste (« 50 sujets », « 16 principes ») → carton plein écran, du mot qui l'annonce jusqu'à la phrase suivante. Pages de 14-18 éléments max. Contenu : celui de la personne (doc, script, Brain) ; ne jamais inventer une liste de son savoir-faire sans le dire.
- **bullets** : « 3 points / 3 étapes » → pastilles, une par élément.
- **inserts suivis (tracking)** : `python3 $S/track.py clip.mp4 0.3 3.0 --point index_tip --out track_badge.json` (points : index_tip, thumb_tip, palm, head_top, head_left, head_right, chin) puis `{"src": "hf/badge.png", "start", "end", "track": "track_badge.json", "offset": [0, -150], "w": 260}` : l'objet suit le geste. Après recadrage (`cadre.py`), vérifier que l'objet suivi reste dans le cadre.
- **hook** : `{}` = ouverture : impact grave seulement. Viseur REC = `"rec": true`, seulement si la vidéo parle de tournage. **Jamais de bandes noires** (testées et rejetées ; `bars: true` les remet, ne pas l'utiliser). Options : `rec`, `impact` (false pour couper), `recEnd`. Hook complet en 7 s : REC (0 s) → mot géant derrière la tête (~0,9 s) → plein écran éclair < 1 s (B-roll ou preuve) avant 3,5 s.
- **bigwords** : `[{"text": "dangereux", "start": 3.6, "end": 4.95}]` = LE mot-clé en serif géant derrière la tête, lettre par lettre depuis le centre, 2 échos en contour qui dérivent, zoom d'impact + aspiration inversée. 1 à 2 par vidéo, surtout dans le hook. Passe par `matte.py` comme les chiffres. Le mot sort du sous-titre tout seul. Ignoré si la vidéo a un `title`.
- **proofs** = « montrer au lieu de dire » : quand la phrase porte une preuve, un chiffre ou une durée, plein écran pendant que la voix continue. **3 à 5 pleins écrans max en tout (listes + preuves + B-rolls plein écran), 1 à 5 s chacun, jamais deux types identiques à la suite.** Sous-titres masqués dessous.
  - `{"type": "curve", "start", "end", "title": ["Copier un hook", "ou le construire"], "from": "Hook copié", "to": "16 principes", "levels": ["Débutant", "Expert"], "steps": [...], "climax": 20.9}` → papier clair : la ligne grise plafonne en bas, la ligne accent monte d'un coup (`climax` = l'instant où elle part, calé sur le mot fort). Pour : « même avec 6 mois », « ce que tout le monde fait vs ». **Seul type de preuve autorisé.**
  - ÉCARTÉS (testés et rejetés, ne pas utiliser ni proposer) : `clock` (horloge qui s'emballe) et `dashboard` (verre sombre 3D). Chiffres de preuve = ceux de la personne (vrais résultats), jamais inventés.

## 5. B-rolls (si utiles : par défaut AUCUN, voir le cahier des charges)
Décider la densité pour TOUTE la vidéo : `none` / `low` / `high`. Bibliothèque : `~/Documents/Contenu/medias/brolls/` (indexée par `outils/indexer-brolls`).
```bash
python3 $S/broll.py slots plan.json words.json --density low     # créneaux réguliers + ce qui est dit à ce moment
python3 $S/broll.py search tournage camera                       # chercher dans la bibliothèque, verticaux d'abord
```
Pour chaque créneau, choisir le fichier qui illustre EXACTEMENT ce qui est dit et qui est beau (net, vertical bien cadré, lumière propre), l'ajouter dans `plan.brolls` (`{"src": "<chemin absolu>", "from": 2.0, "start": .., "end": ..}` ; `"from": "auto"` = passage le plus stable). Une personne visible dans le B-roll = la même que la face cam (vérifier, l'index dit seulement « personne visible » ; plans bannis : `_exclus.txt` de la bibliothèque). Si tu as un `brolls_min_date` dans `montage.json` : aucun plan plus ancien. Pas de bon fichier → on garde la face cam, mais la répartition doit rester régulière (sinon passer à `none`). Mieux vaut 2 B-rolls parfaits que 4 moyens. Bibliothèque vide : Pexels (gratuit, voir le dossier de la bibliothèque), tes propres plans, ou aucun B-roll.
```bash
python3 $S/broll.py prep plan.json                               # coupe + recadre les B-rolls dans broll/
```

## 5 bis. Images sur-mesure (incrustations)
**Avec quoi ?** `config.json` / `montage.json` → `"higgsfield": true` (compte Higgsfield branché à Claude) → Higgsfield. Sinon Gemini sur TA clé (`gemini_image.py`, images fixes seulement, animées par HyperFrames, facultatif), sinon pas d'image générée : tes B-rolls, tes photos.
Quand une idée se montre mieux en image (logo, objet, chiffre en 3D, schéma, produit) et que rien dans la bibliothèque ne colle : la générer sur Higgsfield. Outils Higgsfield = outils différés : les charger via ToolSearch.
- **Charte AVANT tout visuel** (chrome 3D / néon = « très cheap ») : zéro chrome, zéro néon, zéro glow ; 1 visuel test validé avant le reste. Objet réel (badge, logo, interface) = vraie forme et vraie couleur (réf Google Images), détouré, éclairé comme la scène.
- Prompt = l'idée exacte dite à cet instant + la lumière de la fiche univers + `broll.prompt_higgsfield` de la DA (`reglages.py da`). Format 1:1 ou 4:5. Modèle par défaut : `nano_banana_2` (rapide). Texte lisible dans l'image → `gpt_image_2`. Rendu ciné → `soul_cinematic`. VIDÉO générée seulement pour un gros moment sans visage (voir cahier des charges).
- Détourer avec `remove_background` → PNG transparent, télécharger dans le dossier du reel (`ins/`).
- Ajouter dans `plan.inserts` : `{"src": "ins/x.png", "start": .., "end": .., "pos": "top"}` ; `top` = au-dessus de la tête, jamais sur le visage (défaut) ; `center` = grande carte qui cache le visage, <= 2 s.
- Même règle que les B-rolls : régulier, exact, beau. Pas de plafond d'images : autant que nécessaire, mais régulier et utile. Annoncer les crédits dépensés.
- Image plein écran (pas détourée) → la mettre dans `plan.brolls` (le moteur accepte .png/.jpg).
- Sans Higgsfield (Gemini) :
```bash
python3 $S/gemini_image.py "<prompt + broll.prompt_higgsfield de la DA>" ins/x.png --ratio 1:1   # 9:16 pour un B-roll plein écran
```
Pas de clé → le script affiche le lien et la commande du trousseau Mac (la clé est copiée dans le presse-papier, jamais collée dans le chat). Détourage d'un PNG Gemini : `remove_background` Higgsfield ou `rembg` local.

## 5 ter. Caler les ajouts sur le rush, puis test « 5 sur 7 » (avant tout rendu)
```bash
python3 $S/match_look.py clip.mp4 ins/*.png broll/*.mp4 --w 400 --fix   # objet : exposition baissée s'il brille plus que la pièce, couleur JAMAIS touchée ; b-roll : brut, seulement blancs brûlés / voile gris
python3 $S/univers_check.py check plan.json                             # couleur, ton, mouvement, rythme mesurés + univers-check.jpg
```
Remplacer dans `plan.json` chaque fichier calé par son `.cale`. Regarder `univers-check.jpg` (rush à gauche, ajout à droite) et juger espace, ligne, forme : il faut 5 composantes sur 7 en commun, sinon on retire ou on refait. Puis le test Deakins : d'où vient sa lumière ? est-il dans CETTE pièce ? sert-il la phrase ? `--color` seulement pour un visuel GÉNÉRÉ (jamais un vrai logo ni de vrais plans).

## 6. Détourage avant le rendu
```bash
python3 $S/matte.py plan.json                                    # tête devant les chiffres et mots géants (~20 s par chiffre)
```
Puis l'étape 6 de `SKILL.md` (build, lint, zones, rendu, mix).

## Comparer à l'étalon avant d'envoyer
Si l'utilisateur a donné une référence : planches 1 i/s côte à côte (`score.py`) + `analyse_ref.py` sur les deux (coupes, débit, SFX sur les coupes ~60 %). Puis la note /10 (`note-10.md`).
