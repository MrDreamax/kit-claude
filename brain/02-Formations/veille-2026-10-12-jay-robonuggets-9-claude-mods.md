# Jay (RoboNuggets) : 9 mods Claude Code
- URL : https://www.youtube.com/watch?v=lDrAZ1wAyVs (publié début octobre 2026, fiche du 2026-10-12)
- Thème : IA appliquée (outillage). Source qui vend une communauté (RoboNuggets) : méthode gardée, argumentaire écarté.
- Mod = petit module qui écoute les événements de Claude Code et change l'écran ou le comportement. Dispo depuis le 1er oct, version 2.1.287 ou plus, terminal et onglet Code du desktop (~0:40-0:55 et ~10:54). Se crée en le décrivant à Claude (skill intégré "plugin-authoring", ~11:08). Temporaire par défaut : demander "sauvegarde-le en plugin" pour le garder.

| Mod | Effet | Utile ? | Effort |
|---|---|---|---|
| Reflect (~9:05) : quand tu corriges ("non", "pas bon"), propose de sauver la règle dans CLAUDE.md | Montré | Oui : automatise l'amélioration continue | S |
| Cache tax (~7:04) : prévient avant un message qui relit toute la conversation (cache froid après ~1 h) + /keepwarm | Affirmé | Oui, si ton plan a des limites d'usage | S |
| Blast radius (~8:15) : bouton confirmer avant suppression de dossier | Montré | Oui : évite les suppressions accidentelles | S |
| You should know (~4:33) : 2e agent qui souligne coûts et risques cachés dans le pavé de texte | Montré | Partiel, consomme des tokens | S |
| Savvy progress (~2:02) : barre de progression et panneau des sous-agents avec coût | Montré | Partiel, utile si tu as beaucoup d'agents | S |
| File tree, Replay theater, Claude skins, terminal browser | Montré | Non prioritaire | - |

## Comment l'appliquer
Demande à Claude : "crée-moi les mods Reflect, Cache tax et Blast radius et sauvegarde-les en plugin". Vérifie d'abord la version de Claude Code.

## À vérifier
Que les mods tournent bien dans ton app desktop (la vidéo dit terminal + onglet Code, pas VS Code). Le PDF du guide est derrière la communauté (non lu).

## Ce que la vidéo ne dit pas
Failles de sécurité d'un mod qui lit tous les événements, coût en tokens des mods qui appellent un modèle.

## À ignorer
Promo RoboNuggets, mini-jeux, thèmes visuels.
