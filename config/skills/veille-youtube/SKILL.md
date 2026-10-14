---
name: veille-youtube
description: Extraire l'actionnable de vidéos YouTube (une vidéo, une playlist ou une chaîne entière) en fonction du profil de l'utilisateur. Récupère les transcripts avec yt-dlp, les nettoie, les condense sur un gros corpus, puis produit une fiche par vidéo selon une grille adaptée à qui est l'utilisateur, ce qui l'intéresse et ce qu'il veut en garder. Utiliser dès qu'on demande d'analyser, résumer, ficher ou faire de la veille sur des vidéos YouTube.
---

# Veille YouTube : extraire ce qui compte pour vous

## Carnet d'apprentissage
- Avant de commencer : lis ~/Documents/Brain/00-Moi/regles-agents/veille-youtube.md. Ses règles passent AVANT ce fichier.
- Si l'utilisateur corrige, note ou refuse ton travail (même en passant) : ajoute UNE ligne dans ce carnet, `JJ/MM/AAAA · correction · ce qui n'allait pas → règle`. Une règle actionnable par ligne. Si elle contredit une ancienne, remplace l'ancienne. Dis-le en une ligne : « Noté dans mon carnet : ... ».

Ce skill transforme des vidéos YouTube en **fiches actionnables**, filtrées par le profil de
l'utilisateur. Il ne résume pas : il trie. Une vidéo d'une heure contient en général trois ou
quatre idées utiles pour une personne donnée, et ce ne sont pas les mêmes pour tout le monde.

Tout le skill tourne autour d'un fichier : **le profil** (`veille-youtube/PROFIL.md`, dans le
dossier de travail de l'utilisateur). Sans profil, pas de tri possible.

## Étape 0 : Le profil (obligatoire, une seule fois)

Au premier usage, chercher `veille-youtube/PROFIL.md` dans le dossier courant.

**S'il n'existe pas**, ne rien extraire. Interroger d'abord l'utilisateur, en quelques questions
courtes (pas un formulaire de vingt lignes), pour remplir le modèle `modeles/PROFIL.md` :

1. **Qui êtes-vous ?** Rôle, activité, taille de la structure, secteur, marché.
2. **Pourquoi cette veille ?** La décision ou le projet qu'elle doit nourrir.
3. **Ce qui vous intéresse** : thèmes prioritaires, et ceux qui sont hors sujet.
4. **Ce qu'il faut garder** des vidéos : méthodes, chiffres, outils, erreurs, citations, etc.
5. **Ce qu'il faut jeter** : promotion, généralités, lifestyle, ce que vous savez déjà.
6. **Ce que vous faites déjà**, pour repérer ce qui le contredit ou le complète.
7. **Langue des vidéos** et langue souhaitée pour les fiches.

Écrire le profil avec ses réponses, le lui montrer, et le faire valider avant de continuer.
Proposer aussi une liste de mots-clés propres à son métier pour `veille-youtube/mots-cles.txt`
(un par ligne) : ils servent au tri automatique des gros corpus.

**S'il existe**, le relire à chaque session. Le profil se met à jour quand l'utilisateur change
de priorité ; ne jamais le réécrire sans le lui dire.

## Étape 1 : Récupérer les transcripts

### Prérequis : Claude s'en charge, avec l'accord de l'utilisateur

Avant le premier lot, vérifier les deux outils nécessaires :

```bash
command -v python3 && python3 --version
command -v yt-dlp && yt-dlp --version
```

**Si `yt-dlp` manque**, ne pas renvoyer l'utilisateur vers une documentation : proposer de
l'installer soi-même. Choisir la première solution possible sur le poste :

| Situation | Commande proposée |
|---|---|
| `brew` présent (macOS) | `brew install yt-dlp` |
| `pipx` présent | `pipx install yt-dlp` |
| `python3` en version **3.10 ou plus** | `python3 -m pip install --user yt-dlp` |
| aucun des trois (cas d'un Mac sans Homebrew) | l'exécutable autonome officiel, voir ci-dessous |

⚠️ **Le Python fourni par Apple est en 3.9**, et yt-dlp exige 3.10 ou plus. Sur ce Python,
`pip` installerait une ancienne version, que YouTube bloque. Vérifier la version avec
`python3 --version` avant de choisir la troisième ligne.

**L'exécutable autonome** est publié par le projet yt-dlp lui-même et ne dépend pas de
Python. Nom du fichier : `yt-dlp_macos` sur Mac, `yt-dlp_linux` sur Linux (processeur Intel ou
AMD), `yt-dlp_linux_aarch64` sur Linux ARM. Il pèse une quarantaine de Mo. Installation dans
`~/.local/bin`, où `fetch.sh` le trouve même si ce dossier n'est pas dans le PATH, avec
vérification de l'empreinte publiée par le projet :

```bash
F=yt-dlp_macos   # ou yt-dlp_linux, yt-dlp_linux_aarch64
U=https://github.com/yt-dlp/yt-dlp/releases/latest/download
mkdir -p ~/.local/bin && cd ~/.local/bin
curl -fLO "$U/$F" && curl -fLO "$U/SHA2-256SUMS"
grep " $F\$" SHA2-256SUMS | shasum -a 256 -c - && mv "$F" yt-dlp && chmod +x yt-dlp && rm SHA2-256SUMS
~/.local/bin/yt-dlp --version
```

Si la vérification d'empreinte échoue, supprimer le fichier téléchargé, ne pas l'exécuter, et
le dire à l'utilisateur.

Dans tous les cas, **demander l'autorisation en une phrase claire** (ce qu'on installe, d'où,
et pour le téléchargement, sa taille) et attendre un oui explicite avant de lancer quoi que ce
soit, par exemple :

> Pour lire les sous-titres YouTube, j'ai besoin de l'outil gratuit et open source `yt-dlp`,
> qui n'est pas installé. Je peux l'installer avec `brew install yt-dlp`. Je lance
> l'installation ?

Après l'installation, vérifier la version obtenue, et le dire. Si elle a échoué, montrer le
message d'erreur tel quel au lieu de tenter autre chose en silence.

**Si `python3` manque**, Claude ne peut pas l'installer lui-même : l'installation demande le
mot de passe administrateur ou ouvre une fenêtre système. Il donne à l'utilisateur la marche à
suivre, puis vérifie avec `python3 --version` quand celui-ci dit que c'est fait :

- **Mac** : lancer `xcode-select --install` dans le Terminal, puis cliquer sur « Installer »
  dans la fenêtre qui s'ouvre. Les outils de développement d'Apple incluent Python 3, ce qui
  suffit aux scripts du skill (pas à `pip install yt-dlp`, d'où l'exécutable autonome
  ci-dessus) ;
- **Linux** : `sudo apt install python3` (Debian, Ubuntu) ou l'équivalent de la distribution ;
- **Windows** : l'installeur de https://www.python.org/downloads/, en cochant
  « Add python.exe to PATH ».

Homebrew n'est **pas** nécessaire. Si l'utilisateur veut l'installer quand même, lui donner la
commande officielle de https://brew.sh, à lancer lui-même :
`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`.

Jamais de commande `sudo` lancée par Claude.

**Mise à jour.** YouTube change souvent ses pages, et une version ancienne de `yt-dlp` échoue
alors sur toutes les vidéos (par exemple « Unable to extract… » sur l'ensemble du lot, alors
que les vidéos s'ouvrent normalement dans un navigateur). Dans ce cas, proposer la mise à jour
(`brew upgrade yt-dlp`, `pipx upgrade yt-dlp`, `python3 -m pip install --user -U yt-dlp`, ou
`~/.local/bin/yt-dlp -U` pour l'exécutable autonome, selon la méthode d'installation), avec la même demande d'accord.

```bash
bash <skill>/scripts/fetch.sh "URL1" "URL2"      # vidéos, playlists ou chaînes
bash <skill>/scripts/fetch.sh -f urls.txt         # une URL par ligne
```

`<skill>` est le dossier de ce skill. Les transcripts arrivent dans
`veille-youtube/transcripts/` du dossier courant (surcharge : `YT_OUT=...`) : un `.vtt` brut et
un `.txt` nettoyé par vidéo.

Langue : par défaut `fr-orig,en-orig` (pistes auto-générées dans la langue parlée). Pour une
autre langue, `YT_SUBS="es-orig" bash fetch.sh ...`.

### Ce qu'il faut savoir sur les blocages de YouTube

- **Le vrai frein est un quota attaché à l'adresse IP**, pas le client utilisé. Quand il est
  épuisé, tous les clients renvoient le même refus (`HTTP 429` ou « Sign in to confirm you're
  not a bot »). Ne jamais prétendre qu'un réglage « contourne » la protection.
- **Le seul vrai remède est le temps** : attendre (30 minutes à quelques heures), puis relancer
  **la même commande**. Le script reprend où il s'était arrêté et ne redemande pas ce qui est
  déjà sur le disque.
- **Étaler et fractionner** : 2 secondes minimum entre requêtes (réglage par défaut), lots de
  100 à 150 vidéos par session au plus. Si les refus persistent : `YT_SLEEP=4`, puis 8.
- **Trier la liste par priorité avant de lancer**, pour que ce qui passe en premier soit ce qui
  compte le plus.
- Une session cloud sort par une IP de datacenter, bloquée bien plus tôt qu'une connexion
  domestique : lancer les gros corpus depuis son propre poste. Ne jamais chercher à contourner
  un proxy imposé.
- Lancer le script au premier plan : un `nohup ... &` dans un outil d'exécution se fait tuer
  sans erreur visible. Vérifier qu'aucun ancien `yt-dlp` ne tourne encore (`pgrep -f yt-dlp`),
  il consommerait le quota du lot en cours.

### « No subtitles » n'est presque jamais une absence

Ce message dit seulement qu'il n'y a pas de piste **dans les langues demandées**. Le suffixe
`-orig` ne désigne que la piste auto-générée ; une chaîne qui **dépose** ses sous-titres les
expose sous des codes de locale (`fr-FR`, `en-US`…). Si beaucoup de vidéos d'un lot sont
concernées, vérifier sur **une** vidéo :

```bash
yt-dlp --list-subs "URL"
```

puis relancer avec `YT_SUBS="fr-FR"` (ou la locale affichée). Si et seulement si la vidéo n'a
réellement aucune piste, relancer n'y changera rien : seule une transcription locale de l'audio
(par exemple Whisper) la récupère.

## Étape 2 : Trier (gros corpus seulement)

Au-delà d'une dizaine de vidéos, on ne lit pas tout. On condense d'abord chaque transcript en
ses passages à signal (chiffres, prix, décisions, règles affirmées, mots-clés du profil) :

```bash
python3 <skill>/scripts/condense.py --index --mots-cles veille-youtube/mots-cles.txt veille-youtube/transcripts/*.txt
python3 <skill>/scripts/condense.py --mots-cles veille-youtube/mots-cles.txt veille-youtube/transcripts/*.txt > veille-youtube/digest.md
```

`--index` classe les vidéos par densité ; sans lui, le script sort les passages retenus
(environ un dixième du texte). Lire le digest, puis **lire intégralement** les vidéos les plus
denses et celles dont le titre touche directement les priorités du profil.

Contrôler le haut **et** le bas du classement avant de s'y fier : la densité n'est pas une
mesure de vérité, seulement un filtre de lecture.

## Étape 3 : Une fiche par vidéo

Appliquer `modeles/GRILLE.md`, **lue à travers le profil**. Une fiche par vidéo dans
`veille-youtube/fiches/`, nommée `AAAA-MM-JJ-<chaine>-<sujet-court>.md`.

La question qui tranche pour chaque élément : **est-ce utile à CETTE personne, pour CE qu'elle
a déclaré vouloir faire ?** Un excellent conseil hors de son périmètre va dans « À ignorer »,
pas dans les pépites.

## Étape 4 : Synthèse

Quand un lot couvre plusieurs vidéos ou une chaîne entière, terminer par
`veille-youtube/fiches/00-synthese-<chaine>.md` :

- les **3 à 7 actions** à mener, classées par effet attendu et effort, rattachées aux fiches ;
- ce qui **contredit** ce que l'utilisateur fait déjà (section 6 du profil), et pourquoi ;
- les **affirmations récurrentes non prouvées**, qui méritent une vérification avant d'agir ;
- ce que la source **ne dit pas** (coûts, échecs, chiffres jamais montrés).

## Règles de rigueur (non négociables)

1. **Montré, affirmé, déduit.** Chaque fiche distingue ce qui est montré à l'écran (tableau,
   capture), ce qui est seulement affirmé à l'oral, et ce que vous en déduisez. Une déduction ne
   s'écrit jamais comme un fait.
2. **Les décimales d'un sous-titre auto-généré ne sont pas fiables.** La reconnaissance vocale
   altère les chiffres (« 11,30 » devient « 1130 »). Garder les ordres de grandeur, signaler les
   montants précis comme « à vérifier ». Si la chaîne publie un blog ou un article sur le même
   sujet, il est une meilleure source que le transcript.
3. **Une source intéressée se lit comme telle.** Une chaîne qui vend une formation, un
   programme ou un outil a intérêt à ses chiffres : la méthode peut se garder, les montants et
   les taux se signalent comme non vérifiés.
4. **Une recommandation d'outil sous partenariat ne se retient pas.** Si la source déclare un
   partenariat avec un éditeur (ou vend l'outil), la recommandation d'achat sort de la fiche ;
   on peut la mentionner comme un fait sur la source. La méthode décrite indépendamment de la
   marque, elle, peut rester.
5. **Pas de citation longue.** Reformuler ; une citation, quand elle est indispensable, reste
   courte et entre guillemets avec sa source.

