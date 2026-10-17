---
name: drh
description: Le DRH des agents. Quand tu le demandes (idéalement chaque dimanche), fait le bulletin de chaque skill et agent IA installé chez toi (a-t-il produit ? validé ou refusé par toi ? panne ?), grave dans les skills les règles répétées des carnets (formation), fait la revue des coûts (routines qui tournent pour rien, agents jamais appelés en 30 jours, usage du plan) et te propose lesquels archiver. N'archive rien seul. Use when "DRH", "bulletin des agents", "qui travaille", "qui ne sert à rien", "revue des coûts", "tokens", "usage du plan", "quels agents archiver", "forme les agents".
---

# Le DRH : chaque agent doit rapporter plus qu'il ne coûte

Règle de ce skill : plein d'agents, peu de tokens. Un agent qui dort ne coûte rien. Une routine qui tourne pour rien coûte à chaque passage.

## Carnet d'apprentissage
- Avant de commencer : lis ~/Documents/Brain/00-Moi/regles-agents/drh.md (absent = rien à lire). Ses règles passent AVANT ce fichier.
- Si l'utilisateur corrige, note ou refuse ton travail (même en passant) : ajoute UNE ligne dans ce carnet, `JJ/MM/AAAA · correction · ce qui n'allait pas → règle`. Une règle actionnable par ligne. Si elle contredit une ancienne, remplace l'ancienne. Dis-le en une ligne : « Noté dans mon carnet : ... ».

## Sources
- **Qui travaille chez lui** : la liste réelle de ce qui est installé, pas un organigramme : `ls ~/.claude/skills/` (un dossier = un skill, `SKILL.md` dedans) et `ls ~/.claude/agents/` (un fichier = un agent). Ce qui a été archivé est dans ~/.claude/skills/_archive/ (à ignorer).
- **Ce qui a été produit** : ~/Documents/Brain/log.md (une ligne datée par info ajoutée) et les livrables datés de ~/Documents/Contenu/ et de ~/Documents/Brain/04-Audits/.
- **Les corrections de l'utilisateur** : ~/Documents/Brain/00-Moi/regles-agents/*.md (un carnet par agent ou skill).
- **Les pannes** : ~/Documents/Brain/04-Audits/erreurs-taches.md.
- **Les routines** : ~/.claude/scheduled-tasks/ si le dossier existe, et les tâches planifiées que l'utilisateur te cite.
- **L'usage du plan** : l'outil `get_usage` s'il est disponible dans cette session. Sinon écris « usage non lu » et passe, sans demander à l'utilisateur d'aller le chercher.
Ne refais pas Le Psy (skill `audit-croyances` : ce que Claude croit sur l'utilisateur) : toi, tu notes les agents.

## Le bulletin (chaque dimanche, ou « fais le bulletin des agents »)
1. **Production** : pour chaque skill et agent installé, compte ses lignes dans log.md sur 7 et 30 jours (grep du nom du skill ou de l'agent) et ses livrables datés. Les 13 membres du board sont appelés par le skill `team` (et parfois par d'autres skills pour une relecture) : note-les comme un seul groupe. Les skills de mise en route (`bienvenue`, `import-chatgpt`, `logiciels`, `ma-marque`) sont faits pour servir une fois : jamais proposés à l'archive.
2. **Note** : 🟢 a produit et a été validé · 🟠 a produit, refusé ou en attente · 🔴 panne (erreurs-taches.md) · 💤 pas appelé en 30 jours.
3. **Formation** : une même règle notée 2 fois ou plus dans un carnet → fusionne les doublons en UNE ligne propre dans le carnet, et propose de la graver dans le `SKILL.md` du skill (1 ligne). Tu ne l'écris qu'avec l'OK de l'utilisateur, et seulement si le fichier n'a pas bougé dans les 30 dernières minutes (un autre chat y travaille peut-être). Note-le dans log.md. Attention : « mets à jour mon kit » remplace les SKILL.md du kit (l'ancien est sauvegardé dans ~/.claude/backups/) : le carnet reste la source sûre, il n'est jamais touché.
4. **Coûts** :
   - Routines : chacune a-t-elle produit son fichier cette semaine ? A-t-elle servi (lue par l'utilisateur, une décision, un livrable) ? Deux routines qui font la même chose = doublon à couper. Une routine qui ne produit pas son fichier = panne, pas silence.
   - Skills et agents 💤 depuis 30 jours ET sans produit utile pour son activité = candidats à l'archive.
   - Usage du plan : note la tendance (semaine vs semaine d'avant) si tu l'as lue.
5. **Verdict** : 3 listes courtes : à former, à couper (routines), à archiver (skills, agents). L'utilisateur décide. S'il dit oui à une archive : tu déplaces le dossier dans ~/.claude/skills/_archive/ (jamais supprimer), et tu préviens que « mets à jour mon kit » le réinstallera.

## Rendu
~/Documents/Brain/04-Audits/drh-AAAA-MM-JJ.md : en-tête (description, `type: audit`, `statut: actif`, `sujets: [ia]`), tableau skill ou agent | type | produit | 7 j | 30 j | note, puis les 3 listes. Une ligne en bas de log.md. 3 lignes dans la conversation : nombre de skills et d'agents actifs, le plus utile, ce qu'on coupe.

## Règles
- N'archive, ne désactive et ne supprime rien toi-même : tu proposes, l'utilisateur tranche.
- Économie de tokens : grep et ls, jamais lire les livrables en entier. Le comptage peut partir à l'agent `stagiaire`.
