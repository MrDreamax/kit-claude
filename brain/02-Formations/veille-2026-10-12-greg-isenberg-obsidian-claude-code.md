# Greg Isenberg x Vin : Obsidian + Claude Code pour piloter sa vie
- URL : https://www.youtube.com/watch?v=6MBq1paspVU
- Thème : second cerveau, IA. Source : opinion/pratique perso de l'invité (Vin), sans chiffres business. Pas de vente d'outil (Obsidian gratuit, dit sans affiliation).

| Élément | Preuve | Utile ? | Effort |
|---|---|---|---|
| **Commandes slash sur le vault** : /context (charge ta vie + projets via les liens), /today (revue du matin : agenda, tâches, notes), /close-day (actions du jour, confiances) (12:00-14:00) | montré | Oui : équivalent de "début de chat : lis ma base de connaissance", en 1 commande | S |
| **Obsidian CLI** donne à Claude les liens entre notes, pas que le texte (10:00) | affirmé + démo | Partiel : Claude peut déjà lire les fichiers directement | M |
| **/challenge** : confronte une croyance à l'historique du vault ; **/drift** : écart entre intentions et actes sur 30-60 jours ; **/emerge** : idées que le vault implique sans les dire ; **/trace** : évolution d'une idée dans le temps (14:00-19:00) | montré | Oui : /drift et /challenge évitent que l'IA te caresse dans le sens du poil | M |
| **/ghost** : réponds comme moi, profil de voix construit depuis le vault, puis évaluation de fidélité (15:00) | montré | Oui : scripts/reels dans ta voix | M |
| **/ideas** : scan 30 jours, idées d'outils, d'articles, de personnes à rencontrer (35:00-46:00) | montré (rapport de 5 min) | Partiel | M |
| **Demander à l'IA quelles commandes créer** d'après le vault, puis "construis-la" (/graduate : promouvoir les idées des notes quotidiennes en notes dédiées) (47:00-50:00) | montré | Oui : méta-prompt | S |
| **Règle de séparation** : l'IA n'écrit pas dans le vault humain, seulement dans un coin à part, pour ne pas confondre tes pensées et les siennes (33:00) | montré/affirmé | Oui : à comparer avec une base où Claude écrit déjà | S |
| Vault d'équipe partagé (34:00 à 43:00, idée) ; délégation depuis une note ("planifie un appel...") (44:00) | affirmé, non testé | Partiel | L |
| Les requêtes sur un gros vault prennent des minutes (36:00) | montré | à savoir | - |

## Comment l'appliquer
Crée 3 commandes dans ~/.claude/skills : /context (lit ton profil + le projet en cours), /drift (compare objectifs déclarés et actions réelles sur 30 jours, croisé avec tes enregistrements d'appels), /challenge.

## À vérifier
"Plus heureux, plus riche" (intro) : promesse, rien de mesuré.

## Ne dit pas
Aucun usage business, aucun coût, aucun chiffre. Beaucoup de contenu est de la réflexion perso.

## À ignorer
Philosophie (mémoire humaine), confidentialité en général (point utile : ne pas donner sa base de notes à un agent autonome sans réfléchir).
