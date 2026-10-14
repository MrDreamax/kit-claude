---
name: team
description: Met le board d'agents (Head of Common Sense x2, Devil Advocate, Money Maker, CTO, CMO, Copy Chief A/B, Compliance, Stratège, Skipper, Media Buyer, Closer) sur un output important pour qu'ils débattent et rendent un verdict go / no-go. Use when the user writes "team", "mets la team", "board", or asks for the board's opinion on a funnel, offer, sales page, ad, or big decision.
---

# Team — réunion du board

## 1. Cadrer (10 secondes)
Résume en 2 lignes ce qui est soumis au board. S'il manque une info critique, pose UNE question cliquable (AskUserQuestion) avant de lancer.

## 2. Tour 1 : avis indépendants (en parallèle)
Lance en UN SEUL message, en parallèle, les agents pertinents parmi :
`head-of-common-sense`, `head-of-common-sense-2`, `devil-advocate`, `money-maker`, `cto`, `cmo`, `copy-chief-a`, `copy-chief-b`, `compliance-officer`, `strategist`, `skipper`, `media-buyer`, `closer`.

Choix :
- Copy / page / pub : les 2 Common Sense, Devil, Money Maker, CMO, Copy A, Copy B, Compliance, Media Buyer, Closer.
- Vente / VSL / setting / prix / script de call : les 2 Common Sense, Devil, Money Maker, Closer, Copy A, Skipper.
- Budget pub / campagnes Meta : Common Sense, Devil, Money Maker, Media Buyer, Compliance.
- Décision business / stratégie : les 2 Common Sense, Devil, Money Maker, Stratège, Skipper, Closer.
- Technique / outil : Common Sense, Devil, CTO, Money Maker.
- Décision perso (achat, déménagement, études, carrière) : les 2 Common Sense, Devil, Money Maker, Stratège, Skipper.
- Si l'utilisateur dit "toute la team" : tout le monde.

Donne à chaque agent le contenu complet à juger (il ne voit pas la conversation).

## 3. Tour 2 : le débat
Envoie à `devil-advocate` et `head-of-common-sense` la synthèse des avis du tour 1. Ils pointent les contradictions et tranchent.

## 4. Verdict pour l'utilisateur (ultra court)
```
VERDICT : GO / NO-GO / GO SI ...
Pourquoi : 1 ligne
Le board est d'accord sur : 2-3 bullets
Le board se dispute sur : 1-2 bullets
À faire maintenant : 1-3 actions
```
Ne raconte pas le débat. L'utilisateur veut l'output.
Si une version améliorée (copy, page) est demandée, livre-la directement.
Enregistre la décision dans `~/Documents/Brain/05-Decisions/AAAA-MM-JJ-sujet.md`.

## 5. Carnets du board
- Chaque membre lit son carnet (~/Documents/Brain/00-Moi/regles-agents/<nom-agent>.md) avant de répondre : rappelle-le dans le message que tu lui envoies.
- Les membres ne peuvent pas écrire. Si l'utilisateur conteste un avis ou le verdict, c'est TOI qui ajoutes la règle dans le carnet du membre concerné : `JJ/MM/AAAA · correction · ce qui n'allait pas → règle`. Dis-le en une ligne.
