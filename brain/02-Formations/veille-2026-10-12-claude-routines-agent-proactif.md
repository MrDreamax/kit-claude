# Claude (Anthropic) : construire un workflow d'agent proactif avec Claude Code
- URL : https://www.youtube.com/watch?v=eSP7PLTXNy8 (atelier "Code with Claude", date inconnue, fiche du 2026-10-12)
- Thème : IA appliquée (automatisation). Source officielle, présente son propre produit (routines).
- Routines = session Claude Code lancée dans le cloud d'Anthropic : on définit prompt + dépôts + connecteurs + déclencheur. Ne dépend pas du Mac allumé (~3:30). Se crée avec /schedule (~7:36), la session reste ouvrable et pilotable (web, CLI, desktop).

| Idée | Preuve | Utile ? | Effort |
|---|---|---|---|
| 3 décisions pour toute routine : déclencheur, contexte (connecteurs), pilotage (~8:42) | Affirmé | Oui, grille de conception | S |
| Déclencheurs : horaire, événement GitHub, ou appel webhook avec les données en contexte (~5:48) | Montré | Oui : webhook = nouveau lead du CRM qui déclenche une routine | M |
| Générateur + critique : une routine produit, une 2e relit avant l'humain (~12:16) | Affirmé | Oui : brouillon de relance + relecteur qui le vérifie avant envoi | M |
| Exemple doc hebdo lundi 10 h avec notification Slack (~9:30) | Montré | Exemple de rapport hebdo automatique | - |
| Vérificateur de déploiement et tri hebdo de backlog (~18:17) | Affirmé | Transposable : tri hebdo des leads/objections | M |
| Humain dans la boucle d'abord, autonomie ensuite quand la confiance monte | Affirmé | Oui | - |

## Comment l'appliquer
Passe tes tâches récurrentes (par exemple un rapport hebdo du lundi) en routine cloud si elles doivent tourner Mac éteint. Vérifie d'abord ce que ta tâche planifiée actuelle suppose (fichiers locaux, session ouverte).

## À vérifier
Limites et coût des routines selon le plan, accès aux connecteurs claude.ai (enregistreur d'appels, CRM) depuis une routine. Non précisés.

## Ce que la vidéo ne dit pas
Tarifs, quotas, fiabilité, gestion des secrets. Exemples 100 % développeurs (GitHub).

## À ignorer
Détails GitHub/Datadog/on-call.
