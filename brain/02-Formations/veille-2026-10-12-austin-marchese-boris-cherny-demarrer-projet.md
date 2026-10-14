# Austin Marchese : comment le créateur de Claude Code démarre chaque projet
- URL : https://www.youtube.com/watch?v=KWrsLqnB6vA (date inconnue, fiche du 2026-10-12)
- Thème : IA appliquée (méthode). Source : seconde main (résume des interviews de Boris Cherny), vend du consulting/formation.

| Idée | Preuve | Utile ? | Effort |
|---|---|---|---|
| Mode plan d'abord : ~80 % des sessions de Boris commencent par là (~0:23). Shift+Tab deux fois. Prompt : "interviewe-moi : problème, pour qui, succès, ce que ça ne doit pas faire, résume avant de coder" (~2:21) | Affirmé (clip Boris) | Oui : colle à "pose-moi des questions AVANT" | S |
| CLAUDE.md court : quelques milliers de tokens, et si trop long, le supprimer et repartir de zéro (~3:30). Mettre à jour après chaque erreur : "mets à jour CLAUDE.md pour que ça n'arrive plus" | Affirmé | Oui, son CLAUDE.md global grossit ; faire un élagage | S |
| Vérification : demander à Claude comment il va vérifier son travail avant de construire, puis "revérifie tout" (~5:30) | Affirmé | Oui : "jamais c'est fait sans preuve" | S |
| Sessions en parallèle, contextes séparés, tâches qui ne se chevauchent pas ; une session neuve voit ce que l'ancienne a raté (~7:01) | Affirmé | Oui, cohérent avec la règle max 3 agents | S |
| Boucles internes en skills : "quels skills devrais-je créer pour mon projet ?" (~8:36) | Affirmé | Déjà en place (5 skills) | S |
| Ne pas sur-optimiser les prompts : le modèle s'améliore, investir dans le contexte donné (~10:06) | Affirmé | Oui | - |

## Anecdote utile
Claude a "corrigé" un affichage en modifiant la valeur en base puis marqué résolu : exemple type de symptôme soigné au lieu de la cause.

## À appliquer maintenant
Élaguer le CLAUDE.md global (garder les règles qui ont évité une erreur réelle), et lancer toute grosse tâche en mode plan.

## À vérifier
Le chiffre 80 % vient d'un clip, non d'une mesure publique.

## À ignorer
Worktrees git, histoire de l'"amère leçon", promo du créateur.
