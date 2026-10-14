---
name: drift
description: Compare ce que l'utilisateur a dit vouloir (objectifs, décisions, règles dans le Brain) avec ce qu'il a réellement fait sur 30 jours (journal du Brain, décisions, projets, audits). Sort les écarts sans filtre. Use when "drift", "est-ce que je fais ce que je dis", "challenge-moi", "/drift", ou en fin d'audit du dimanche.
---

# Drift : dit A, fait B ?

## Carnet d'apprentissage
- Avant de commencer : lis ~/Documents/Brain/00-Moi/regles-agents/drift.md. Ses règles passent AVANT ce fichier.
- Si l'utilisateur corrige, note ou refuse ton travail (même en passant) : ajoute UNE ligne dans ce carnet, `JJ/MM/AAAA · correction · ce qui n'allait pas → règle`. Une règle actionnable par ligne. Si elle contredit une ancienne, remplace l'ancienne. Dis-le en une ligne : « Noté dans mon carnet : ... ».

Source : Greg Isenberg x Vin, Obsidian + Claude Code (commandes /drift et /challenge). Applique la règle d'or n°3 du master prompt : on ne caresse pas dans le sens du poil.

## 1. Ce qu'il a dit
~/Documents/Brain/00-Moi/profil.md (objectifs), la partie « Qui je suis » de ~/.claude/CLAUDE.md, 05-Decisions/ (30 derniers jours), 01-Projets/ (prochaines étapes annoncées), mémoire Claude (~/.claude/projects/*/memory/), hot.md.

## 2. Ce qu'il a fait
log.md (ce qui a vraiment avancé, avec les dates), 04-Audits/, 05-Decisions/ (décisions prises puis abandonnées), 01-Projets/ (étapes restées au même point), et les connecteurs branchés s'il y en a (agenda, mails : titres et dates seulement, sans tout relire).
Si le Brain a moins de 2 semaines de vie : dis-le, et fais l'exercice sur ce qui existe (ou demande-lui 3 objectifs et reviens dans 30 jours).

## 3. Rendu
Max 5 écarts, du plus cher au moins cher (argent, temps, santé, relations) :
"Tu as dit [X] le [date]. Tu as fait [Y]. Coût probable : [Z]. Une action pour recoller : [A]."
Plus 1 croyance à challenger : une chose qu'il tient pour vraie que les faits contredisent.
Écris dans ~/Documents/Brain/04-Audits/drift-AAAA-MM-JJ.md. Chat : les 3 écarts les plus chers, une ligne chacun.
Faits uniquement, chaque écart sourcé (fichier ou date). Pas de morale.
