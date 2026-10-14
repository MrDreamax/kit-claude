# Nate Herk : Build & Sell Claude Code Operating Systems (cours 2h35)
- URL : https://www.youtube.com/watch?v=bCljOfCH8Ms
- Thèmes : IA appliquée (second cerveau, skills, cadence), équipe IA
- Fiabilité : praticien qui utilise son système tous les jours (montré). Intérêt : vend sa communauté School et son outil de dictée Glido (partenaire déclaré, reco sortie de la fiche).
- Attention : malgré "& Sell" dans le titre, la vidéo n'explique PAS comment vendre un AIOS. Un seul passage (72:35) cite la monétisation de skills, "ne pas parier dessus". Aucun prix, aucun script de vente, aucun client montré.

## Éléments retenus
| Élément | Preuve | Utile ? | Effort |
|---|---|---|---|
| **4 C : Contexte, Connexions, Capacités, Cadence**, dans cet ordre. Test : une nouvelle session répond-elle comme un assistant ou comme un inconnu ? (12:00) | montré (schéma) | Oui : cadre simple pour présenter un système IA à quelqu'un | S |
| **Onboarding par interview en 7 questions** qui écrit des fichiers about-business / about-me / priorités + 2 posts écrits verbatim pour capter la voix (29:00-32:00) | montré | Oui : onboarding du jour 1 d'un système IA | M |
| **Skill /audit** : note le système sur 100 par C et liste 3 lacunes (47:00) + **/level-up** : 5 questions (tâche faite 3 fois, "stagiaire intelligent", ce qui casserait avec 500 clients, levier de croissance) (50:00) | montré | Oui : audit réutilisable, et boucle d'amélioration continue | M |
| **Découper un métier en fonctions** puis automatiser un morceau à la fois, morceaux réutilisables (5:00) | affirmé + schéma | Oui : méthode de diagnostic d'un métier | S |
| **Dip de productivité de 20 % les premiers jours** avant le gain (9:00) | affirmé (dessiné) | Oui : à annoncer d'avance à ceux à qui tu installes un système, pour éviter la déception | S |
| **Un compte et une clé API dédiés à l'IA, droits limités (lecture seule)**, clés dans un .env, jamais collées dans le chat (38:00-42:00) | montré | Oui : sécurité | S |
| Préférer **API + fichier de référence markdown** au MCP (moins de tokens) ; enregistrer dans le skill les endpoints utilisés (39:00, 46:00) | affirmé | Partiel : à tester avant de l'ériger en règle | M |
| **Skill = recette** : front matter (nom, description) + étapes + références + règles ; chargement progressif en 3 niveaux ; SKILL.md sous 500 lignes ; boucle feedback : regarder 3-5 premières exécutions puis corriger le skill (73:00-83:00) | montré | Oui : checklist qualité pour écrire un skill | S |
| **Skill-builder en 6 étapes** : nom/déclencheur, objectif, étapes, références, règles, auto-amélioration ; fixer le logo en overlay au lieu de le demander à l'IA (85:00-91:00) | montré | Oui : fabriquer des skills par interview | M |
| **Routines cloud** : tâche lancée sans ordinateur allumé, repo GitHub requis, clés dans les variables d'environnement, minimum 1 h, quota 5/15/25 par jour selon plan (Pro/Max/Team) (98:00-116:00) | montré, quotas affirmés (à vérifier) | Partiel : utile pour que des agents tournent la nuit | M |
| **/loop** : rappel ou vérification toutes N minutes, 3 jours max, meurt avec la session (117:00) | montré | Partiel : suivi d'un email urgent, ponctuel | S |
| **Wiki Karpathy** (voir fiche dédiée) + hot.md (cache de 500 mots du dernier contexte) pour l'assistant (125:00-143:00) | montré | Oui | M |
| **Artefacts live** (dashboards qui rappellent QuickBooks/ClickUp à l'ouverture) ; règle POC : prouver en 5 min avant de bâtir sur mesure (143:00-147:00) | montré | Oui : dashboard (pubs, CRM, paiements) sans développement | M |
| **Critères de succès** : l'équipe interroge l'IA au lieu de toi ; tu ouvres moins d'onglets ; la connaissance sort de ta tête (150:00) | affirmé | Oui : grille de résultat | S |
| **GWS CLI** (CLI Google Workspace open source en bêta, non supporté officiellement) pour Drive/Docs/Sheets/Gmail en une commande (51:00-65:00) | montré, finicky de son aveu | Partiel : le connecteur Drive/Gmail existe déjà | L |

## Comment l'appliquer
1. Pour présenter un système IA : "On installe tes 4 C" (contexte, connexions, capacités, cadence). Écris la page en 1 schéma.
2. Copie la trame d'interview en 7 questions pour l'onboarding (ajoute : offre, client idéal, voix, objections de vente).
3. Fais un /audit (score /100) de ton propre système avant de l'utiliser pour d'autres.
4. Règle de sécurité : compte IA dédié + droits lecture seule.

## À vérifier
- Quotas de routines (5/15/25), 3 jours de /loop, "minimum 1 h" : chiffres dits à l'oral, changent vite.
- "-95 % de tokens" cité sur X (via Karpathy), non vérifié.
- Les 54,5/100 de l'audit sont un exemple de démo.

## Ce que la vidéo ne dit pas
Coût mensuel réel, temps passé à maintenir, échecs avec des clients non techniques, comment vendre/packager/facturer un AIOS, résultats business chiffrés. Nate vend une communauté : son usage vient de sa chaîne YouTube, pas d'un coach high ticket.

## À ignorer
Installation VS Code, GWS CLI pas à pas, promos Glido et School, philosophie "mentor pas distributeur".
