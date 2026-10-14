---
name: livre
description: Speedrun d'apprentissage. Transforme les meilleurs livres + vidéos YouTube d'un sujet en un seul livre de ~160 pages, lisible en deux soirées, écrit dans le style d'Alex Hormozi. Use when the user wants to learn a topic fast, "écris-moi un livre sur...", "speedrun ce sujet", or wants to condense books/courses.
---

# Livre — apprendre un sujet en deux soirées

## Carnet d'apprentissage
- Avant de commencer : lis ~/Documents/Brain/00-Moi/regles-agents/livre.md. Ses règles passent AVANT ce fichier.
- Si l'utilisateur corrige, note ou refuse ton travail (même en passant) : ajoute UNE ligne dans ce carnet, `JJ/MM/AAAA · correction · ce qui n'allait pas → règle`. Une règle actionnable par ligne. Si elle contredit une ancienne, remplace l'ancienne. Dis-le en une ligne : « Noté dans mon carnet : ... ».

1. **Cadrer** (questions cliquables) : sujet exact, objectif (ce que l'utilisateur veut savoir faire à la fin), contexte perso.
2. **Sélection** : sous-agents Sonnet en parallèle sur Goodreads, Reddit, listes de bestsellers. Sors 7 à 10 livres à plus fort impact + 10 vidéos YouTube de référence. Montre la liste, l'utilisateur valide en un clic.
3. **Corpus** : l'utilisateur dépose les PDF qu'il possède dans `~/Documents/Brain/03-Livres/<sujet>/sources/`. Donne-lui juste ce chemin. Récupère toi-même les transcriptions YouTube.
4. **Lecture intégrale** : un sous-agent par livre lit le texte du début à la fin et en extrait les enseignements, mécanismes, exemples et métaphores. Il vérifie qu'il a tout lu (nombre de mots lus = nombre de mots du fichier).
5. **Écriture** : avec le meilleur modèle disponible. ~160 pages, style Alex Hormozi : mots simples, métaphores, schémas en texte, chaque ligne est une punchline. Objectif : lire ce livre = avoir lu tout le corpus.
6. **Livraison** : `~/Documents/Brain/03-Livres/<sujet>/LIVRE.md` (+ PDF si demandé). Ajoute 20 flashcards question/réponse à la fin.
