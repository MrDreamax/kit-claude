# Nate Herk : Karpathy "LLM wiki", second cerveau en 5 minutes
- URL : https://www.youtube.com/watch?v=sboNwYmH3AY
- Thème : IA appliquée, second cerveau. Source : praticien, vend une communauté (neutre sur l'outil, Obsidian gratuit).

| Élément | Preuve | Utile ? | Effort |
|---|---|---|---|
| **Architecture** : dossier `raw/` (sources brutes) + `wiki/` (pages rédigées par l'IA avec liens) + `index.md` + `log.md` (historique) + CLAUDE.md qui explique les règles (3:00-5:00) | montré | Oui : une base de notes structurée, avec en plus index + log | M |
| **Ingestion** : déposer une source dans raw/, dire "ingère", l'IA crée 5-25 pages liées (10 min pour un article, 14 min pour 36 transcripts) (9:00-12:00) | montré | Oui : brancher la veille YouTube dessus | M |
| **Web Clipper Obsidian** pour envoyer une page web directement dans raw/ (8:00) | montré | Partiel | S |
| **hot.md** : cache d'environ 500 mots de ce qui vient d'être traité, lu en premier par l'assistant (14:00) | montré | Oui : économise des tokens | S |
| **Lint** : audit périodique du wiki (incohérences, trous, liens manquants) (15:00) | affirmé | Oui : tâche planifiée hebdo | S |
| Vs RAG : suffisant à l'échelle de centaines de pages, au-delà de millions de documents il faut du RAG classique (16:00-17:00) | affirmé (tableau fait par Claude) | Oui : rassurant pour une petite structure | S |
| Un autre projet pointe vers le wiki via un "wiki path" dans son CLAUDE.md, avec règle "ne lis le wiki que si nécessaire" (13:00) | montré | Oui | S |

## Comment l'appliquer
Ajoute `index.md`, `log.md` et `hot.md` dans ta base de notes, et un lint hebdomadaire (par exemple le dimanche).

## À vérifier
"-95 % de tokens" (utilisateur X, 383 fichiers) : non prouvé. Karpathy : ~100 articles, ~500 000 mots, dit par Nate.

## Ne dit pas
Qualité des réponses mesurée, coût réel en tokens d'une ingestion, erreurs de l'IA qui s'écrivent dans le wiki.

## À ignorer
Démo AI 2027, comparaisons philosophiques.
