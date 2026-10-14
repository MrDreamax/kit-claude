---
name: import-chatgpt
description: Rapatrie dans Claude ce que ChatGPT sait de la personne. Deux voies - rapide (2 minutes, un message à coller dans ChatGPT) ou complète (export de toutes les conversations ChatGPT transformé en archives lisibles dans le Brain). Remplit le profil, les projets et la mémoire. Use when "importe ChatGPT", "je viens de ChatGPT", "récupère mon historique ChatGPT", "transfert depuis ChatGPT", or from the bienvenue skill.
---

# Import ChatGPT : on ne repart pas de zéro

## 1. Choisir la voie (AskUserQuestion)
« Comment on rapatrie ChatGPT ? »
- **Rapide, 2 minutes (Recommandé)** : tu colles un message dans ChatGPT, tu me colles sa réponse. Je récupère ce qu'il sait de toi.
- **Complet** : tout ton historique de conversations. Il faut demander l'export à ChatGPT (mail sous 24 h à 7 jours).
- **Les deux** : le rapide maintenant, le complet quand le mail arrive.

## 2. Voie rapide
Donne ce message à copier, dans un bloc de code, avec la consigne « Colle ça dans ChatGPT, puis colle-moi sa réponse ici » :
```
Je change d'assistant IA. Fais-moi un état complet de tout ce que tu sais sur moi : ta mémoire enregistrée, mes instructions personnalisées, et ce que tu as appris dans nos conversations. Classe-le en : 1) qui je suis (métier, situation, famille si je l'ai dit), 2) mes objectifs, 3) mes projets en cours, 4) ma façon de travailler et mes préférences de réponse, 5) les sujets que je te pose le plus souvent, 6) les décisions importantes que j'ai prises. Une ligne par info, avec la date quand tu l'as. N'invente rien, ne résume pas, n'oublie rien. Le tout dans un seul bloc de code.
```
Quand la réponse arrive :
- Trie chaque ligne : qui il est / objectifs / préférences → `~/Documents/Brain/00-Moi/profil.md` ; projets → un fichier par projet dans `~/Documents/Brain/01-Projets/` (en-tête du README du Brain) ; décisions → `05-Decisions/`.
- Mets à jour la partie « Qui je suis » de `~/.claude/CLAUDE.md` (entre les balises PROFIL, 8 lignes max) et ta mémoire.
- Copie la réponse brute dans `~/Documents/Brain/00-Moi/import-chatgpt.md` (avec en-tête `type: moi`).
- Ignore les infos sensibles inutiles (santé, mots de passe, numéros) sauf si la personne veut les garder. Ne garde jamais un mot de passe ou une clé.
- Termine en 3 lignes : « J'ai récupéré X infos. Ce qui change pour toi : ... ».
- Bonus facultatif, en une ligne : la même réponse peut aussi aller dans la mémoire de Claude sur claude.ai (Settings > Memory > Start import), pour les chats hors de cette app.

## 3. Voie complète
a) Dis à la personne, en une ligne : « Dans ChatGPT : ta photo de profil > Settings > Data controls > Export data > Export. Tu reçois un mail (jusqu'à 7 jours, souvent moins), le lien de téléchargement expire 24 h après : clique-le vite. Dis-moi quand le zip est dans Téléchargements. »
b) Quand c'est fait : trouve le zip le plus récent dans `~/Downloads` qui contient un `conversations*.json` (`unzip -l`). Si rien : demande-lui où il est.
c) Lance :
`python3 ~/.claude/skills/import-chatgpt/import_chatgpt.py "<chemin du zip>"`
   Mac : si une fenêtre propose d'installer les « outils de développement », dis à la personne de cliquer Installer (5 minutes), puis relance. Sans python possible : reviens à la voie rapide.
d) Le résultat est dans `~/Documents/Brain/_archives-chatgpt/` (INDEX.md, conversations/, mes-messages.txt, instructions-perso.txt). Ces archives ne sont pas dans l'index du Brain : on les cherche avec grep quand on en a besoin.
e) Analyse (délègue à un sous-agent si `mes-messages.txt` dépasse ~200 Ko) : lis `instructions-perso.txt`, `INDEX.md` (les titres disent les sujets) et `mes-messages.txt` en commençant par les 6 derniers mois. Sors les faits durables comme en voie rapide (profil, projets, décisions, préférences), chacun avec sa date. Ne recopie pas les conversations dans le Brain : seulement les faits.
f) Une ligne en bas de `~/Documents/Brain/log.md`, mise à jour de `hot.md`, puis `python3 ~/Documents/Brain/_outils/brain.py`.
g) Fin : « J'ai lu N conversations (de <date> à <date>). Voilà ce que je sais de toi maintenant : » + 5 lignes. Puis : « Si je me trompe sur un point, dis-le, je corrige. »

## Règles
- Le zip et les archives restent sur l'ordinateur de la personne. Ne les envoie nulle part.
- Ne supprime jamais le zip : la personne le fera si elle veut.
