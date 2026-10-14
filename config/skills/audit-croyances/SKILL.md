---
name: audit-croyances
description: Audit hebdomadaire de ce que Claude croit sur l'utilisateur. Génère une page web locale listant toutes les croyances (CLAUDE.md, mémoires, Brain) pour que l'utilisateur coche vrai / à changer / faux, puis met tout à jour quand il écrit "go". Use every Sunday, or when the user says "audit", "qu'est-ce que tu crois sur moi", "belief system".
---

# Audit des croyances

## Carnet d'apprentissage
- Avant de commencer : lis ~/Documents/Brain/00-Moi/regles-agents/audit-croyances.md. Ses règles passent AVANT ce fichier.
- Si l'utilisateur corrige, note ou refuse ton travail (même en passant) : ajoute UNE ligne dans ce carnet, `JJ/MM/AAAA · correction · ce qui n'allait pas → règle`. Une règle actionnable par ligne. Si elle contredit une ancienne, remplace l'ancienne. Dis-le en une ligne : « Noté dans mon carnet : ... ».

## 1. Collecter
Lis :
- `~/.claude/CLAUDE.md`
- tous les dossiers `memory/` sous `~/.claude/projects/*/memory/`
- `~/Documents/Brain/00-Moi/` et `~/Documents/Brain/01-Projets/`

Extrais chaque croyance en une phrase courte (ex : "Tu es associé avec X sur le projet Y", "Ton objectif n°1 est Z", "Tu préfères les réponses en bullet points"). Garde la source (fichier) de chacune. Groupe par thème : Moi, Objectifs, Projets, Façon de travailler, Préférences.

## 2. Générer la page
Écris `~/Documents/Brain/04-Audits/AAAA-MM-JJ.html`, un seul fichier autonome, sans dépendance externe. Pour chaque croyance :
- la phrase (style Hormozi, ultra concis)
- 3 boutons : ✅ Vrai · ✏️ À changer · ❌ Faux
- si "À changer" : une zone de texte apparaît pour écrire la correction
En haut : progression (x / total). En bas, un gros bouton **"Copier pour Claude"** qui copie dans le presse-papier un récapitulatif (uniquement les "À changer" et "Faux", avec la source de chaque). Sauvegarde l'état dans localStorage. Pas besoin d'un beau design, ça doit juste être agréable et rapide.

Ouvre la page : `open <chemin>` (Mac) ou `start "" "<chemin>"` (Windows).

## 3. Dire à l'utilisateur (une ligne)
"Coche tout, clique sur Copier, colle ici et écris go."

## 4. Sur "go"
Applique chaque correction dans le fichier source : supprime ce qui est faux, réécris ce qui est à changer. Mets à jour les index (MEMORY.md). Confirme en 1 ligne : "X croyances corrigées, Y supprimées."

## 5. Bonus : drift
Après la page, lance le skill `drift` (dit A, fait B sur 30 jours) et ajoute ses 3 écarts les plus chers en tête du message à l'utilisateur. Puis ménage du Brain : mets à jour ~/Documents/Brain/hot.md (500 mots max, l'état actuel) puis lance `python3 ~/Documents/Brain/_outils/brain.py` (refait index.md tout seul, ne l'édite jamais à la main). Règle ce qu'il liste en bas de index.md : en-tête manquant (modèle dans ~/Documents/Brain/README.md), lien mort, doc devenu faux (statut + remplace_par, voir README). Chemin d'agent cassé : signale-le à l'utilisateur en 1 ligne. Rien supprimé, rien renommé, rien déplacé. Relance le script à la fin pour vérifier que le contrôle est propre.

## 6. Ménage des carnets
Relis ~/Documents/Brain/00-Moi/regles-agents/ (un carnet par agent) : fusionne les doublons, remplace les règles périmées, signale à l'utilisateur en une ligne les règles qui se contredisent entre deux agents. Ne supprime rien sans le dire.
