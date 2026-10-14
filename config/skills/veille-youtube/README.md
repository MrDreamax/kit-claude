# Veille YouTube : skill Claude Code

Transforme des vidéos YouTube (une vidéo, une playlist, une chaîne) en fiches actionnables,
triées selon **votre** profil : qui vous êtes, ce qui vous intéresse, pourquoi vous faites
cette veille, et ce qu'il faut garder des vidéos.

## Installation

1. Copier ce dossier `veille-youtube/` dans `~/.claude/skills/` (pour tous vos projets) ou dans
   `.claude/skills/` d'un projet (pour ce projet seulement).
2. Ouvrir Claude Code dans le dossier où vous voulez ranger votre veille et demander, par
   exemple : « Analyse cette vidéo : https://www.youtube.com/watch?v=... ».

Le skill a besoin de deux outils : `python3` et `yt-dlp`, un outil gratuit et open source qui
lit les sous-titres YouTube. **Vous n'avez pas à vous en occuper d'avance** : Claude vérifie
au premier usage. S'il manque `yt-dlp`, il vous propose de l'installer et attend votre accord
(Homebrew n'est pas nécessaire). S'il manque Python, il vous explique la marche à suivre, car
cette installation-là demande votre mot de passe ou un clic dans une fenêtre système : sur Mac,
c'est la commande `xcode-select --install`, puis « Installer ».

Au premier usage, Claude vous pose quelques questions pour remplir votre profil
(`veille-youtube/PROFIL.md`), puis s'en sert à chaque analyse. Vous pouvez aussi le remplir
vous-même à partir de `modeles/PROFIL.md`.

## Ce que le skill crée dans votre dossier de travail

```
veille-youtube/
├── PROFIL.md        votre profil (à garder à jour)
├── mots-cles.txt    mots-clés de votre métier, pour trier les gros corpus
├── transcripts/     sous-titres bruts (.vtt) et nettoyés (.txt)
├── digest.md        passages à signal, sur un gros corpus
└── fiches/          une fiche par vidéo + une synthèse par lot
```

## Contenu du skill

- `SKILL.md` : la méthode suivie par Claude (profil, extraction, tri, fiches, règles de rigueur).
- `scripts/fetch.sh` : récupère et nettoie les transcripts, reprend après une coupure.
- `scripts/clean_vtt.py` : convertit les sous-titres auto-générés en texte lisible.
- `scripts/condense.py` : classe et condense les transcripts d'un gros corpus.
- `modeles/PROFIL.md` et `modeles/GRILLE.md` : le profil à remplir et la grille des fiches.

## Bon à savoir

- YouTube limite le nombre de requêtes par connexion. En cas de blocage, attendre puis relancer
  la même commande : rien n'est perdu, seules les vidéos manquantes sont redemandées.
- Les chiffres précis lus dans un sous-titre auto-généré peuvent être déformés par la
  reconnaissance vocale : les fiches les signalent « à vérifier ».
- Respectez les conditions d'utilisation de YouTube et les droits des auteurs : les
  transcripts servent à votre analyse, pas à être republiés.
