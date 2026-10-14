# Règles du Brain (pour Claude et les agents)

Ce dossier est ton second cerveau. Tu n'as pas besoin de l'ouvrir : Claude le lit et l'écrit pour toi. Ces règles ont un seul but : que le prochain chat trouve vite le bon fichier et ne s'appuie jamais sur un doc périmé.

## Ce qu'il y a dedans
- `hot.md` : ton état actuel en 1 minute. Lu en premier.
- `index.md` : une ligne par fichier (refait automatiquement).
- `log.md` : une ligne par chose ajoutée, la plus récente en bas.
- `00-Moi/` : ton profil, tes préférences, les carnets des agents (ce qu'ils ont appris de tes corrections).
- `01-Projets/` : un fichier par projet.
- `02-Formations/` : fiches experts sourcées (contenu, vente, pub, montage, IA...).
- `03-Livres/` : résumés de livres de référence (marketing, vente, copywriting).
- `04-Audits/` : audits, bilans, pages de l'audit du dimanche.
- `05-Decisions/` : une note par décision importante.
- `08-Conseillers/` : 7 cerveaux d'experts (Hormozi, Buffett, Bezos, Martell, Wickman, Gary Vee, Paul Graham), en anglais, sourcés.
- `_archives-chatgpt/` (si tu as importé ChatGPT) : tes anciennes conversations, hors index.

## Lire
1. [[hot]] : l'état actuel en 1 minute. Toujours en premier.
2. [[index]] : une ligne par fichier. Taille en gras = gros fichier : grep d'abord.
3. Puis seulement les fichiers utiles. `tail -20 log.md` = ce qui a changé récemment.
- ⚠ dans l'index, ou `statut:` autre que `actif` en tête de fichier : ne t'appuie pas dessus. Lis le fichier indiqué par `remplace_par`.
- 03-Livres/textes/ : textes bruts (domaine public). Grep seulement, jamais en entier.
- 08-Conseillers : `_hot.md` du conseiller d'abord (voir [[08-Conseillers/README]]).
- 00-Moi/regles-agents/ : le carnet d'un agent est lu par cet agent avant sa mission (voir [[00-Moi/regles-agents/README]]).

## Écrire une note
- Nom : minuscules-avec-tirets.md. Date devant si c'est daté : `AAAA-MM-JJ-sujet.md`. Jamais un nom qui existe déjà ailleurs dans le Brain.
- En-tête obligatoire en haut du fichier :
```
---
description: "Ce qu'il y a dedans. À lire quand ..."
type: moi | projet | formation | veille | livre | audit | decision | contenu | strategie | index | systeme
statut: actif
sujets: [business, perso]
---
```
- Puis `# Titre`, puis l'essentiel en 3 à 5 lignes : le lecteur s'arrête souvent là.
- Liens avec le chemin complet : `[[02-Formations/experts-hooks-retention]]`.
- Après : 1 ligne EN BAS de `log.md`, `hot.md` si l'état actuel change, puis `python3 ~/Documents/Brain/_outils/brain.py` (refait l'index et contrôle tout).
- Jamais de mot de passe, clé API, token ou IBAN en clair.

## Quand une note devient fausse
- Ne la supprime pas, ne la renomme pas, ne la déplace pas : des skills et agents lisent ces chemins. `brain.py` signale tout chemin d'agent cassé.
- Change son en-tête : `statut: remplacé` (ou `en-pause`, `rejeté`, `historique`) + `remplace_par: "[[chemin/de/la/nouvelle]]"` + `note: "pourquoi, depuis quand"`.

## Vocabulaire
- **statut** : `actif` · `en-pause` · `remplacé` · `rejeté` · `historique`.
- **sujets** : closing · pub-meta · contenu · montage · audio · da · youtube · offre · ia · clients · business · perso · argent · sante · etudes · famille · admin · apprendre.

## Entretien
- `_outils/brain.py` refait `index.md` et liste en bas ce qu'il faut régler : liens morts, fichiers sans en-tête, noms en double, chemins d'agents cassés, hot.md trop vieux.
- Chaque dimanche, le skill `audit-croyances` fait le ménage.
- Les fichiers 02-Formations, 03-Livres, 08-Conseillers et _outils sont mis à jour par le kit (« mets à jour mon kit »). Tes fichiers perso (00-Moi, 01-Projets, 04-Audits, 05-Decisions, hot, log) ne sont jamais touchés.
