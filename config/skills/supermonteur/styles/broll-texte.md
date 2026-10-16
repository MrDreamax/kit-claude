# B-ROLL + TEXTE (VALIDÉ et FIGÉ : ne plus y toucher sauf demande)

Lu après `SKILL.md`. 5-7 s, 1 plan (2 max) où la personne est EN ACTION, du texte AU-DESSUS DE LA TÊTE, musique, zéro voix. Le spectateur lit pendant que la vidéo tourne en boucle (Meta compte les relectures dans le temps de visionnage). Format à vues (Ronny Mitchell : vues 10/10, cash 3/10 ; Modern Millie : 4 à 9 abonnés pour 1 000 vues) : pour qui veut de la portée. **Si le plan de contenu de l'utilisateur (`strategie-contenu.md`) privilégie la vente plutôt que la portée, le dire avant de monter.** Fiches : Brain `02-Formations/experts-broll-texte.md` (montage), `02-Formations/experts-copy-broll-texte.md` (copy) et `02-Formations/ronny-mitchell-25-formats.md`.
Pas de dérush, de sous-titres, de `build.mjs` ni de `mix.py` ici : tout passe par `brolltexte.py` (texte dessiné avec le Chrome de HyperFrames).

## Règles
- **Texte TOUJOURS au-dessus de la tête**, 2 lignes (3 MAX), chacune sur UNE ligne. Police de la DA en majuscules blanches ; le mot fort en serif italique (124 px seul sur sa ligne, 96 px s'il partage la ligne). Une ligne trop longue rétrécit jusqu'à 44 px, au-delà le script refuse (≈ 28 caractères max par ligne) : raccourcir.
- **CTA facultatif** (la 3e ligne n'est pas forcément un CTA) ; s'il y en a un : **EN BAS**, séparé du texte (bas du bloc à 1 420 px).
- **Jamais de ponctuation en fin de texte** (ni point, ni « ? », ni « ! ») : le script la retire de chaque ligne et du CTA, l'emoji final reste.
- **Contraste** : fond clair ou chargé sous le texte (85e centile > 140/255 ou écart > 45) → **voile noir léger en haut** (dégradé 50 % → 0, comme les titres-questions), tout seul. `"veil": true / false` pour forcer.
- **3 intentions qui performent**, une par reel :
  - **Émotion = une CITATION** : une vraie phrase de quelqu'un, l'auteur pas forcément nommé à l'écran, SOURCE VÉRIFIÉE (Brain `08-Conseillers`, fiches experts ; jamais une citation de mémoire ni une attribution douteuse) ; pas de CTA ; la légende raconte l'histoire derrière la phrase (et peut nommer l'auteur), termine par « Enregistre-le pour… ».
  - **Aide en commentaire** : le texte invite à demander de l'aide en commentaire (« Tu bloques sur ta bio / Colle-la en commentaire ») ; en bas la promesse (« Je réponds à chaque bio ») ; la légende dit quoi poster et ce qu'on y répond. La promesse doit être TENUE : c'est la personne qui répond elle-même (l'humain envoie).
  - **Valeur en légende** : le texte promet un contenu concret (« 3 phrases à copier… ») ; en bas « Lis la légende 👇 » ; la légende LIVRE tout (3 points concrets), termine par « Enregistre ce post… ». Pour générer des leads : « Commente MOT » à la place (15 à 25 fois plus de commentaires, mot lié à une ressource qui EXISTE).
- **Style `da` par défaut** (police de ta DA). Style `natif` (bandeau blanc d'Instagram) seulement si l'utilisateur le demande.

## Le Copywriter (étape OBLIGATOIRE avant le montage)
Lire `experts-copy-broll-texte.md` (règles §2 à §5, 18 patrons §6, grille §7) + la voix de la personne (`00-Moi/voix-contenu.md`) + sa cible (`00-Moi/strategie-contenu.md`).
1. Écrire **10 variantes** réparties sur les 3 intentions, chacune sur un patron différent : POUR QUI en 2 s, une émotion ou une question qui reste ouverte, du concret. Faits vrais seulement (preuves de `voix-contenu.md`), jamais de promesse de revenu, pas de « peut-être », rien qui contredit le plan de contenu de la personne.
2. **Noter** avec la grille (Clarté, Émotion/Curiosité, Concret, Pour moi, Lisibilité, Pont vers la légende, Intention tenue, Voix, 0-10) : garder si moyenne >= 7,5 ET Clarté >= 5 ET Émotion/Curiosité >= 5. Tableau dans `copy.md` du dossier.
3. **Légende** (60-110 mots, `anti-ia` en dernière passe) : 1re ligne = un 2e hook (<= 125 caractères visibles avant « plus ») qui NE répète PAS l'écran ; paragraphes de 1 à 3 phrases ; preuve vraie ; UN seul geste à la fin.
4. La **meilleure de chaque intention** = 3 reels : l'utilisateur choisit (ou les publie tous les trois en Trial Reels).

## Montage
- Plan = TES vrais B-rolls, la personne EN ACTION (écrit, travaille, téléphone, marche), léger mouvement ; jamais un plan figé ni un plan où elle parle (bouche sans son). Avec de la place au-dessus de la tête de préférence. Stable (`"from": "auto"` = `broll.py steady`), brut, **jamais de filtre**. Rien qui colle → Pexels (vérifie la licence). Jamais d'IA avec un visage.
- **Placement automatique** : le script mesure le haut de la tête sur tout le plan (5e centile), pose le texte entre 300 px et la tête - 70 px ; pas assez de place → le plan descend (480 px max) et le haut de l'image est prolongé en fondu (« place rajoutée », comme en montage viral). Pas de visage (de dos, mains, lieu) → texte en haut de la zone sûre. `"y"` force le centre du bloc si besoin.
- Musique émotionnelle, durée EXACTE du plan, bouclable : avec Epidemic, `EditRecording` avec `loopable: true` → wav dans `musique/epidemic/` ; sans Epidemic, un morceau libre de droits coupé à la durée (`ffmpeg -t`) avec un fondu de 0,3 s aux deux bouts. Musique seule à -14 LUFS (gain mesuré, limiteur -2 dBTP).
- Republier la même vidéo : changer au moins les 3 premières secondes (plan ou texte), sinon Instagram la marque comme doublon.

## Lancer
1. Copywriter → `copy.md`. Plans : `python3 broll.py search <action>` (écrit, ordinateur, telephone…) + planche d'images.
2. Musique : `SearchRecordings` (émotion, `vocals: false`) → `EditRecording` (`targetDurationMs` = durée du plan, `forceDuration`, `loopable`, `WAV`) → `DownloadRecordingEdit` → `~/Documents/Contenu/medias/musique/epidemic/`. Sans Epidemic : voir la section Musique de `SKILL.md`.
3. **plan.json** (un dossier par variante ; EXEMPLE FICTIF) :
```json
{"brolls": [{"src": "<chemin absolu>", "from": "auto", "dur": 6}],
 "text": {"lines": ["3 phrases à copier", "dans ta bio de coach"], "strong": "bio de coach", "cta": "Lis la légende 👇"},
 "style": "da", "music": {"src": "<wav loopable>"}, "caption": "<légende>"}
```
(`"cta"` facultatif ; `"da": "chemin.json"` facultatif : par défaut ta DA.)
```bash
python3 $S/brolltexte.py plan.json      # place au-dessus de la tête + texte + CTA + musique -> final.mp4 + legende.txt (~30 s)
```
4. Vérifier : planche à 1, 3 et 5 s (texte au-dessus de la tête à chaque instant, CTA hors des mains si possible, rien hors zone), `ebur128` ≈ -14 LUFS, début à 0 s, la fin enchaîne sur le début sans saut.
