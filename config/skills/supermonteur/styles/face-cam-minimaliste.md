# FACE CAM · degré 2 : MINIMALISTE

Lu après `SKILL.md`. Explication avec des chiffres, des preuves, des captures. Style : cartons typo mot par mot, icônes au trait, captures d'écran avec un cercle tracé à la main (le style des webinaires et VSL épurés).
Beaucoup d'air, zéro transition : ça apparaît net, ça disparaît net, jamais de rebond.

- Socle de `SKILL.md` : étapes 1-3, tes sous-titres verrouillés (jamais changés), musique accordée à la vidéo, étape 7.
- **Couleurs = celles de TA rush**, jamais une palette plaquée. Dégradé des cartons = `plan.colors.grad` : `[haut gauche sombre, haut droite vif, bas gauche, bas droite clair, fond]` ; défaut = tiré de ta couleur d'accent (`marque.json`).
- **Dosage** (mesuré sur des VSL pros : 1 élément toutes les 3 à 6 s) : 1 phrase = 1 visuel max. Cartons sur les punchlines (1 toutes les 10-20 s, 1 à 3 lignes de 1-3 mots, SES mots à lui, condensés). Icônes sur les noms concrets (temps = horloge, argent = billet, visibilité = œil). Captures = vraies preuves (profil, stats, commentaires) avec un cercle sur LA chose dite.
- Pas de chiffre géant, mot géant, B-roll, REC, image générée ni preuve plein écran (c'est le high prod). Zoom lent du moteur gardé. Titre-question / CTA : seulement si la vidéo le demande, demander.
- Sons : 1 whoosh à l'entrée de chaque carton (auto, `list`, si le fichier est dans `medias/sfx/`), rien sur les icônes et captures.
- **Zones mortes** (build.mjs) : captures posées à >= 278 px (elles grossissent de 3 % en dérivant).

## `plan.mini` (build.mjs)
- `{"type": "card", "start", "end", "bg": "grad" | "flat" | "#hex", "lines": [{"text": "en revanche", "font": "serif"}, {"text": "gagner en"}, {"text": "crédibilité", "font": "serif", "size": 190}]}` → carton plein écran, chaque mot apparaît QUAND il est dit (cherché dans la transcription) ; `"at"` + `"whole": true` = toute la ligne d'un coup ; `"swap": true` = la ligne remplace celle d'avant au même endroit (« IMPORTANT » → « ASSET ») ; `font` sans = MAJUSCULES grasses (défaut), serif = italique ; taille auto (tient dans 900 px). Compte comme plein écran : anti-flash, pas de sous-titres dessous. (EXEMPLE FICTIF : remplace par tes mots.)
- `{"type": "icon", "icon": "eye" | ["calendar", "calendar"], "start", "end", "cross": t, "y": 360, "size": 210}` → icône(s) au trait fin blanc au-dessus de la tête (y sous le haut de la tête : `headtop.py`) ; `cross` = croix rouge tracée à cet instant (« non », « pas »). Icônes : eye, calendar, user, users, chart, phone, message, clock, money, badge, shield, heart, star, idea, handshake (en ajouter dans `MINI_ICONS`).
- `{"type": "shot", "src": "ins/x.png", "start", "end", "y": 210, "w": 900, "circle": {"at", "cx", "cy", "rx", "ry"}}` → capture recadrée sur l'utile, carte arrondie au-dessus de la tête, légère dérive ; cercle blanc tracé à la main à `at` (coordonnées en px de l'image ; `color` possible).

## Pas encore fait
Capture tenue dans la main (tracking) puis passée derrière la tête (détourage), mot surligné dans un bloc couleur, pastilles 1-2 au-dessus de la tête, médias en cartes arrondies sur fond uni.
