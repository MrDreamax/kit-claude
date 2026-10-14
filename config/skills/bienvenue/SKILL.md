---
name: bienvenue
description: Accueil du kit Claude. Questionnaire de départ (questions cliquables, 3 minutes) qui remplit la partie « Qui je suis » du master prompt et le profil du Brain, propose de rapatrier ce que ChatGPT sait de la personne, puis montre en 5 lignes ce que le kit sait faire. Use right after installing the kit, when « Qui je suis » still says À REMPLIR, or when the user says "bienvenue", "refais mon profil", "présente-toi", "tu sais faire quoi".
---

# Bienvenue : 3 minutes pour que Claude te connaisse

Ton but : qu'à la fin, Claude parle à cette personne comme un assistant qui la connaît depuis des mois. Ton ton : chaleureux, simple, zéro jargon. La personne est peut-être totalement débutante.

## 1. Dire bonjour (2 lignes max)
« Le kit est installé. Je te pose 5 questions rapides pour m'adapter à toi, ensuite tu n'auras plus jamais à te présenter. »

Si `~/.claude/kit-claude.txt` existe et qu'un ancien CLAUDE.md a été sauvegardé (chemin dans `~/.claude/backups/kit-*/.claude/CLAUDE.md`) : lis-le, garde ses préférences utiles pour l'étape 3, et dis-le en une ligne.

## 2. Les questions (AskUserQuestion, option recommandée en premier)
Un seul appel avec ces 4 questions :
1. « Tu vas surtout utiliser Claude pour quoi ? » (multiSelect) : Mon travail / mon business · Mes études · Ma vie perso (admin, santé, famille) · Créer du contenu.
2. « Ton niveau avec l'IA ? » : Débutant total · J'utilise déjà ChatGPT · À l'aise.
3. « Comment je te parle ? » : Ultra court, juste l'essentiel (Recommandé) · Court avec un peu d'explication · Détaillé, j'aime comprendre.
4. « Tu viens de ChatGPT ? » : Oui, rapatrie ce qu'il sait de moi (Recommandé si oui) · Oui, mais plus tard · Non.

Puis en texte libre, une seule question : « Ton prénom, et en une phrase : ce que tu fais et ton objectif n°1 pour les 3 prochains mois ? »
Tutoiement par défaut. Si la personne vouvoie, vouvoie-la et note-le.

## 3. Écrire le profil
a) Dans `~/.claude/CLAUDE.md`, remplace UNIQUEMENT ce qu'il y a entre `<!-- PROFIL:DEBUT -->` et `<!-- PROFIL:FIN -->` (garde les deux balises) par :
```
## Qui je suis
- <Prénom>. <ce qu'il fait, 1 ligne>.
- Objectif n°1 (3 mois) : <objectif>.
- J'utilise Claude pour : <usages>.
- Niveau IA : <niveau>. <si débutant : « Pars du principe que je suis un immense débutant. »>
- Je veux l'output, pas le comment. <adapter selon la réponse 3 : ultra court / court + explication / détaillé>
- <tutoiement ou vouvoiement>
```
6 à 8 lignes max : ce bloc est lu à chaque chat.

b) Remplis `~/Documents/Brain/00-Moi/profil.md` (garde l'en-tête, remplace les « À REMPLIR ») avec la version longue.
c) `~/Documents/Brain/hot.md` : remplace « À REMPLIR » par 3 à 5 lignes (qui, objectif n°1, ce qui est en cours).
d) Une ligne en bas de `~/Documents/Brain/log.md` : `- AAAA-MM-JJ · Profil créé (skill bienvenue).`
e) Enregistre aussi l'essentiel dans ta mémoire.

## 4. ChatGPT
- Réponse « Oui, rapatrie » : lance le skill `import-chatgpt` maintenant (lis `~/.claude/skills/import-chatgpt/SKILL.md` et suis-le).
- « Plus tard » : dis en une ligne « Quand tu veux, écris : importe ChatGPT. »

## 5. Les logiciels gratuits
Lance le skill `logiciels` (lis `~/.claude/skills/logiciels/SKILL.md` et suis-le) : il propose en un clic Obsidian, Wispr Flow, Chrome + Claude in Chrome, et installe les outils invisibles dont les skills ont besoin.

## 6. La routine du dimanche
Si l'outil de tâches planifiées de l'app est disponible (`create_scheduled_task`) : crée la tâche `audit-du-dimanche`, chaque dimanche à 10h (heure locale), avec ce prompt :
« Lance le skill audit-croyances (~/.claude/skills/audit-croyances/SKILL.md) et suis-le : génère la page d'audit du jour dans ~/Documents/Brain/04-Audits/, ouvre-la, puis dis en une ligne : "Ton audit du dimanche est prêt. Coche tout, clique sur Copier, colle-le dans un chat et écris go." »
Dis en une ligne qu'elle tourne seulement si l'app Claude est ouverte. Outil absent : dis-lui juste « Le dimanche, écris audit ».

## 7. Ce que je sais faire (le message final, court)
Ouvre le mode d'emploi illustré : `open ~/Documents/Brain/MODE-EMPLOI.html` (Mac) ou `start "" "%USERPROFILE%\Documents\Brain\MODE-EMPLOI.html"` (Windows). Puis écris :

```
C'est prêt, <Prénom>. 5 phrases à essayer :
- « Mets la team sur mon idée : ... » → 13 experts débattent, verdict GO / NO-GO
- « Trouve-moi les meilleurs experts sur ... » → sources sérieuses, pas des blogs
- « Écris-moi un livre sur ... » → un sujet appris en 2 soirées
- « Fais-moi une fiche de cette vidéo YouTube : <lien> »
- « Challenge-moi » → ce que tu dis vs ce que tu fais

Bonus en 1 clic (facultatif) :
- Tes mails, agenda, Drive : claude.ai > Customize > Connectors > Gmail / Google Calendar / Google Drive

Ouvre un nouveau chat : tout est actif.
```
Adapte les 5 exemples aux usages cochés à l'étape 2 (ex. études : « Écris-moi un livre sur la macroéconomie »). Ne dépasse pas 15 lignes.

## Relancer
Si la personne relance `bienvenue` plus tard : montre-lui son profil actuel en 5 lignes et demande ce qu'elle veut changer (QCM), au lieu de tout reposer.
