# Kit Claude : un Claude qui te connaît, qui bosse, et qui s'appuie sur des experts

Tu installes ce kit en 1 phrase. Ensuite, Claude :
- **te parle simple et court**, te pose des questions à boutons au lieu de pavés ;
- **se souvient de toi** d'un chat à l'autre (ton profil, tes projets, tes décisions) ;
- **s'appuie sur ~100 fiches d'experts et de livres** (vente, marketing, contenu, pub, IA) au lieu de sa mémoire ;
- **a une équipe** : 13 conseillers qui débattent de tes grosses décisions et rendent un verdict GO / NO-GO ;
- **ne fait jamais rien d'irréversible sans toi** : pas de message envoyé, pas de fichier supprimé, pas de paiement.

Tu crées du contenu ? Il écrit tes scripts, monte tes reels, fait tes carrousels, tes slides et ta veille, à ta voix et à tes couleurs.

Tu vends du coaching ou de la formation ? Il transforme les gains de tes clients en preuves, tient ta chaîne de production, qualifie tes commentaires, prépare ta page d'offre, ton recrutement et ton point marge.

Tu viens de ChatGPT ? Il rapatrie ce que ChatGPT sait de toi.

---

## Installer (5 minutes)

1. **Installe l'app Claude** : [claude.com/download](https://claude.com/download) (Mac ou Windows). Il faut un forfait **Pro** minimum.
2. Ouvre l'app, clique sur l'onglet **Code**, choisis ton dossier **Documents** comme dossier de travail.
3. Colle cette phrase et envoie :

```
Installe le kit Claude qui est ici : https://github.com/MrDreamax/kit-claude
```

Claude fait tout le reste. Il te demandera ton accord avant de lancer l'installation (clique « Autoriser »), puis t'ouvre une page avec toutes ses questions (15 minutes) : tu cliques, tu copies, tu colles. Tu préfères le chat ? Il te les pose une à une.

---

## Ce qui est installé

| Quoi | Où | À quoi ça sert |
|---|---|---|
| Le master prompt | `~/.claude/CLAUDE.md` | La façon dont Claude te parle et travaille, dans chaque chat |
| Le second cerveau | `Documents/Brain/` | Ton profil, tes projets, et la bibliothèque d'experts. Claude le lit et l'écrit pour toi |
| 15 agents | `~/.claude/agents/` | Le board (13 conseillers) + Le Limier qui trouve les bons experts sur Internet + Les Stagiaires IA (petit modèle pas cher pour le travail mécanique) |
| 9 skills de base | `~/.claude/skills/` | team, livre, veille-youtube, audit-croyances, drift, bienvenue, import-chatgpt, logiciels, ma-marque |
| 12 skills contenu | `~/.claude/skills/` | scripteur, supermonteur (montage), carrousel, slides, publieur, veille-reels, audit-insta, calls-vers-contenu, usine-pubs, directeur-artistique, anti-ia, higgsfield |
| 10 skills business | `~/.claude/skills/` | chasseur-preuves, producteur, decliner, webmaster, setter, preparateur-coaching, attache-presse, recruteur, cfo, drh |
| Ton dossier contenu | `Documents/Contenu/` | Tes rushes, B-rolls, photos, et tout ce que Claude fabrique (PDF, montages, carrousels) |
| Logiciels gratuits (au choix) | ton ordinateur | Obsidian (voir ton cerveau), Wispr Flow (dicter au lieu de taper), Chrome + Claude in Chrome, yt-dlp ; bonus Fathom et Canva |

Ton équipe business (chacun a son carnet : tes corrections deviennent des règles) :
- **Le Chasseur de preuves** : tes clients ont des gains, il en fait des preuves vérifiées (interview, étude de cas).
- **Le Producteur** : compte tes reels écrits, tournés, montés, programmés, prépare la feuille de tournage.
- **Le Déclineur** : une vidéo longue devient des reels, un carrousel et des fiches de publication.
- **Le Webmaster funnel** : page d'offre, candidature, VSL, flows ManyChat (rien n'est mis en ligne sans toi).
- **Le Setter IA** : lit tes commentaires, trie les chauds, prépare les réponses. Tu envoies.
- **Le Préparateur de coaching** : prépare chaque call de groupe, puis le récap et les gains à exploiter.
- **L'Attaché de presse** : podcasts, pitchs, interviews, partenariats, kit média.
- **Le Recruteur** : closer au pourcentage, juriste, assistant : annonce, tri, entretien, seuils.
- **Le CFO** : ta marge réelle et 5 chiffres, quand tu le demandes (Stripe en lecture seule).
- **Le DRH** : le bulletin de tes agents, ce qui sert, ce qui coûte pour rien.
- **Les Stagiaires IA** (agent) : transcrire, compter, ranger, vérifier des listes, toujours contrôlés.

Phrases à essayer :
- « Mets la team sur mon idée : ... »
- « Trouve-moi les meilleurs experts sur ... »
- « Écris-moi un livre sur ... » (un sujet appris en 2 soirées)
- « Fais-moi une fiche de cette vidéo YouTube : ... »
- « Challenge-moi » (ce que tu dis vouloir vs ce que tu fais)
- « Écris-moi le lot de la semaine » (tes scripts de reels à tourner)
- « Monte cette vidéo » (reel prêt à poster)
- « Fais-moi un carrousel sur ... »
- « Fais ma veille » (les vidéos qui cartonnent dans ta niche)
- « Qui a un gain à transformer en preuve ? » (tes clients, tes interviews, tes études de cas)
- « Où en est ma production ? » (combien de reels d'avance, le prochain tournage)
- « Qui a commenté, qui est chaud ? » (tes commentaires qualifiés, réponses en brouillon)
- « Fais le point marge » (cash net, pub, marge réelle)

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
   Lis `install.sh` avant de le lancer si tu veux vérifier ce qu'il fait : il copie le master prompt, les agents et les skills dans `~/.claude/`, le Brain dans `~/Documents/Brain/` et crée `~/Documents/Contenu/`. Il sauvegarde tout fichier existant avant de le remplacer et ne touche jamais aux fichiers perso.
   **Windows sans bash** (PowerShell seul) : télécharge `$KIT_URL/archive/refs/heads/main.zip`, dézippe-le, puis reproduis à la main ce que fait `install.sh` (mêmes règles : sauvegarde avant de remplacer, ne jamais écraser les fichiers perso du Brain, garder le bloc PROFIL du CLAUDE.md existant). Le Brain va dans `%USERPROFILE%\Documents\Brain`.
2. **Vérifie** : `~/.claude/CLAUDE.md` existe, `~/.claude/agents/` contient 15 fichiers, `~/.claude/skills/` contient les 31 skills (bienvenue, team, livre, veille-youtube, audit-croyances, drift, import-chatgpt, logiciels, ma-marque, scripteur, supermonteur, carrousel, slides, publieur, veille-reels, audit-insta, calls-vers-contenu, usine-pubs, directeur-artistique, anti-ia, higgsfield, chasseur-preuves, producteur, decliner, webmaster, setter, preparateur-coaching, attache-presse, recruteur, cfo, drh), `~/Documents/Brain/index.md` et `~/Documents/Brain/_outils/marque.py` existent. Si un point manque : trouve la cause, corrige, revérifie.
3. **Nettoie** : supprime `~/.claude/kit-tmp`.
4. **Accueil** : lis `~/.claude/skills/bienvenue/SKILL.md` et suis-le maintenant, dans ce même chat (questionnaire, profil, import ChatGPT, logiciels gratuits, réglage de sa marque s'il crée du contenu, routine du dimanche, mode d'emploi).
5. À la fin, dis à la personne d'ouvrir un **nouveau chat** : le master prompt, les agents et les skills y seront tous actifs.

---

## Crédits
- Le skill `higgsfield` vient du projet [higgsfield-ai-prompt-skill](https://github.com/OSideMedia/higgsfield-ai-prompt-skill) d'O-Side Media (licence MIT, voir `config/skills/higgsfield/LICENSE`).
- Les pages Cut Notes et Style Lab du skill `supermonteur` (retours image par image, choix du style de montage) ont été créées par Cyril MrDreamax (byStratosphere, [@mrdreamax.business](https://instagram.com/mrdreamax.business)).
- Les 7 cerveaux de conseillers (`Brain/08-Conseillers`) viennent du projet [Roast Room](https://github.com/nateherkai/roast-room) (licence MIT, voir `brain/08-Conseillers/LICENSE-roast-room.txt`). Ce sont des simulations compilées depuis le travail public de chaque expert, pas les vraies personnes.
- Les fiches experts et les fiches livres sont des synthèses sourcées (vidéos, livres, docs officielles), avec la source de chaque idée. Les textes intégraux inclus sont du domaine public (Claude Hopkins).
