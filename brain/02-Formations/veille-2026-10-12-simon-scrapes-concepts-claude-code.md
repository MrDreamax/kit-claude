# Simon Scrapes : 27 concepts de Claude Code pour non-techniques (27 min)
- URL : https://www.youtube.com/watch?v=ZlDnsf_DOzg
- Thème : IA appliquée (glossaire). Source : vend une formation (AI Automation Academy), explications correctes mais de base. Promo à ignorer.

| Élément | Preuve | Utile ? | Effort |
|---|---|---|---|
| **Liste d'autorisation / refus dans settings.json** : pré-approuver lecture, tests, git ; garder sous validation les installations, suppressions, appels réseau ; **deny** pour .env et dossiers secrets (3:00-5:00, 12:00) | affirmé + exemple montré | Oui : moins de clics, et protège les clés | S |
| **Context rot** : contexte trop long = qualité en baisse ; /clear entre tâches, /compact avec consigne ("garde les infos X") ; compaction auto vers 85 % (6:00-11:00) | affirmé | Oui : règle "1 tâche par chat" | S |
| `claude --resume`, /cost, /stats (7:00-8:00) | affirmé | Oui | S |
| Hiérarchie : CLAUDE.md (manuel) / mémoire auto / skills (recettes) / hooks (scripts auto sans tokens) / sous-agents (contexte propre) / équipes d'agents (se parlent) / MCP (outils externes) (8:00-20:00) | affirmé | Oui : cartographie de ce que fait chaque outil | S |
| **Hooks** : règles automatiques sans tokens (ex : journaliser chaque commande, formater à la sauvegarde) (16:00-17:00) | affirmé | Oui : journal d'actions, blocage de commandes dangereuses | M |
| Règle de choix : skill pour mieux faire dans la conversation, sous-agent pour une tâche autonome, équipe quand les agents doivent se coordonner (18:00-20:00) | affirmé | Oui | S |
| **/rewind** (checkpoints avant chaque édition) (21:00) | affirmé | Oui : filet de sécurité pour un débutant | S |
| **Mode -p (headless)** pour lancer une tâche sans conversation ; boucle "Ralph" plugin (22:00-24:00) | affirmé | Partiel | M |
| **Worktrees** (`claude -w`) : plusieurs Claude en parallèle sans se marcher dessus (25:00) | affirmé | Non pour l'instant, utile seulement pour du code | - |
| Modèles : Haiku simple, Sonnet standard, Opus quand ça compte (11:00) | affirmé | Oui : sous-agents en Sonnet pour les tâches d'exécution | - |

## Comment l'appliquer
Demande à Claude : "ajoute les permissions sûres et un deny sur .env et secrets, montre-moi avant de sauvegarder".

## À vérifier
Noms de modèles et prix cités (Opus 4.6, Pro 20 $, Max 100/200 $) : datés.

## Ne dit pas
Aucun cas business, aucune mesure.

## À ignorer
Git/GitHub, worktrees, Ralph loop, promo de la formation.
