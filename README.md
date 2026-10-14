# Kit Claude : un Claude qui te connaît, qui bosse, et qui s'appuie sur des experts

Tu installes ce kit en 1 phrase. Ensuite, Claude :
- **te parle simple et court**, te pose des questions à boutons au lieu de pavés ;
- **se souvient de toi** d'un chat à l'autre (ton profil, tes projets, tes décisions) ;
- **s'appuie sur ~100 fiches d'experts et de livres** (vente, marketing, contenu, pub, IA) au lieu de sa mémoire ;
- **a une équipe** : 13 conseillers qui débattent de tes grosses décisions et rendent un verdict GO / NO-GO ;
- **ne fait jamais rien d'irréversible sans toi** : pas de message envoyé, pas de fichier supprimé, pas de paiement.

Tu viens de ChatGPT ? Il rapatrie ce que ChatGPT sait de toi.

---

## Installer (5 minutes)

1. **Installe l'app Claude** : [claude.com/download](https://claude.com/download) (Mac ou Windows). Il faut un forfait **Pro** minimum.
2. Ouvre l'app, clique sur l'onglet **Code**, choisis ton dossier **Documents** comme dossier de travail.
3. Colle cette phrase et envoie :

```
Installe le kit Claude qui est ici : https://github.com/MrDreamax/kit-claude
```

Claude fait tout le reste. Il te demandera ton accord avant de lancer l'installation (clique « Autoriser »), puis te pose 5 questions pour s'adapter à toi.

---

## Ce qui est installé

| Quoi | Où | À quoi ça sert |
|---|---|---|
| Le master prompt | `~/.claude/CLAUDE.md` | La façon dont Claude te parle et travaille, dans chaque chat |
| Le second cerveau | `Documents/Brain/` | Ton profil, tes projets, et la bibliothèque d'experts. Claude le lit et l'écrit pour toi |
| 14 agents | `~/.claude/agents/` | Le board (13 conseillers) + Le Limier qui trouve les bons experts sur Internet |
| 8 skills | `~/.claude/skills/` | team, livre, veille-youtube, audit-croyances, drift, bienvenue, import-chatgpt, logiciels |
| Logiciels gratuits (au choix) | ton ordinateur | Obsidian (voir ton cerveau), Wispr Flow (dicter au lieu de taper), Chrome + Claude in Chrome, yt-dlp ; bonus Fathom et Canva |

Phrases à essayer :
- « Mets la team sur mon idée : ... »
- « Trouve-moi les meilleurs experts sur ... »
- « Écris-moi un livre sur ... » (un sujet appris en 2 soirées)
- « Fais-moi une fiche de cette vidéo YouTube : ... »
- « Challenge-moi » (ce que tu dis vouloir vs ce que tu fais)

Mettre à jour plus tard : dis à Claude « mets à jour mon kit ». Ton profil et tes fichiers perso ne sont jamais touchés.

---

## Pour Claude : procédure d'installation

Tu installes ce kit pour la personne qui t'a collé ce lien. Fais tout toi-même, explique en 1 ligne à chaque étape, en français, sans jargon.

1. **Télécharge et lance l'installateur** (Mac, Linux, ou Windows avec Git Bash) :
   ```bash
   KIT_URL="https://github.com/MrDreamax/kit-claude"
   rm -rf "$HOME/.claude/kit-tmp" && mkdir -p "$HOME/.claude/kit-tmp" && cd "$HOME/.claude/kit-tmp" \
     && curl -fsSL "$KIT_URL/archive/refs/heads/main.tar.gz" | tar xz \
     && KIT_URL="$KIT_URL" bash */install.sh
   ```
   Lis `install.sh` avant de le lancer si tu veux vérifier ce qu'il fait : il copie le master prompt, les agents et les skills dans `~/.claude/`, et le Brain dans `~/Documents/Brain/`. Il sauvegarde tout fichier existant avant de le remplacer et ne touche jamais aux fichiers perso.
   **Windows sans bash** (PowerShell seul) : télécharge `$KIT_URL/archive/refs/heads/main.zip`, dézippe-le, puis reproduis à la main ce que fait `install.sh` (mêmes règles : sauvegarde avant de remplacer, ne jamais écraser les fichiers perso du Brain, garder le bloc PROFIL du CLAUDE.md existant). Le Brain va dans `%USERPROFILE%\Documents\Brain`.
2. **Vérifie** : `~/.claude/CLAUDE.md` existe, `~/.claude/agents/` contient 14 fichiers, `~/.claude/skills/` contient bienvenue, team, livre, veille-youtube, audit-croyances, drift, import-chatgpt, logiciels, et `~/Documents/Brain/index.md` existe. Si un point manque : trouve la cause, corrige, revérifie.
3. **Nettoie** : supprime `~/.claude/kit-tmp`.
4. **Accueil** : lis `~/.claude/skills/bienvenue/SKILL.md` et suis-le maintenant, dans ce même chat (questionnaire, profil, import ChatGPT, logiciels gratuits, routine du dimanche, mode d'emploi).
5. À la fin, dis à la personne d'ouvrir un **nouveau chat** : le master prompt, les agents et les skills y seront tous actifs.

---

## Crédits
- Les 7 cerveaux de conseillers (`Brain/08-Conseillers`) viennent du projet [Roast Room](https://github.com/nateherkai/roast-room) (licence MIT, voir `brain/08-Conseillers/LICENSE-roast-room.txt`). Ce sont des simulations compilées depuis le travail public de chaque expert, pas les vraies personnes.
- Les fiches experts et les fiches livres sont des synthèses sourcées (vidéos, livres, docs officielles), avec la source de chaque idée. Les textes intégraux inclus sont du domaine public (Claude Hopkins).
