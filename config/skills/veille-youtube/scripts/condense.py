#!/usr/bin/env python3
"""Condense un transcript nettoyé en ses seuls passages à signal.

Sur un gros corpus, on ne lit pas tout. On extrait d'abord les passages qui
portent un chiffre, un prix, une décision, une règle affirmée ou un mot-clé du
profil, et on ne lit intégralement que les transcripts qui restent denses après
ce filtre.

Usage :
    condense.py transcripts/*.txt                          # passages retenus, sur stdout
    condense.py --mots-cles mots-cles.txt transcripts/*.txt
    condense.py --max 25 transcripts/x.txt                 # plafonner les passages
    condense.py --index transcripts/*.txt                  # classement par densité seulement

`mots-cles.txt` : un mot-clé ou une expression par ligne, propres au métier de
l'utilisateur (lignes vides et lignes commençant par # ignorées). Chacun vaut 2
points. Une expression régulière est acceptée si la ligne commence par `re:`.

Le score n'est pas une mesure de vérité : un chiffre affirmé à l'oral dans une
vidéo promotionnelle reste une affirmation, pas une preuve.
"""
import argparse
import pathlib
import re
import sys

# Marqueurs de signal génériques. Chacun vaut ses points ; un passage cumule.
MARQUEURS = [
    # ── Français ──
    # chiffres et argent : le signal le plus fiable
    (r"\b\d[\d\s  ]*(?:€|euros?|k€|K€|M€|millions?|milliards?|%)", 3),
    (r"\b\d+\s*(?:fois|x)\b", 2),
    (r"\b(?:budget|marge|rentab|prix|tarif|facture|coût|coute|coûte|chiffre d'affaires)\w*", 2),
    # décisions et bascules : ce qui s'est réellement passé
    (r"\b(?:on a (?:décidé|arrêté|lancé|changé|recruté|testé|divisé|multiplié)|"
     r"j'ai (?:décidé|arrêté|lancé|changé|recruté|testé)|"
     r"la (?:première|plus grosse) erreur|on s'est planté|ça a raté|on a compris)\b", 3),
    (r"\b(?:erreur|piège|échec|raté|regret)\w*", 2),
    # règles et affirmations fortes : ce qui fait méthode
    (r"\b(?:il faut|ne jamais|jamais|toujours|surtout pas|la règle|le seul|la seule|"
     r"la clé|le vrai sujet|en réalité|contrairement à)\b", 1),
    (r"\b(?:notre méthode|notre process|on recommande|notre conseil|étape par étape)\b", 2),

    # ── Anglais ── (mêmes catégories, mêmes poids : les deux jeux cohabitent)
    (r"(?:\$\s?\d|\b\d[\d,.]*\s*(?:dollars?|bucks|k\b|million|billion|%|percent))", 3),
    (r"\b\d+\s*(?:times|x)\b", 2),
    (r"\b(?:budget|margin|profit|pricing|price|rate|fee|invoice|cost|charge|revenue)\w*", 2),
    (r"\b(?:we (?:decided|stopped|launched|changed|hired|tested|doubled|tripled|realized)|"
     r"i (?:decided|stopped|launched|changed|hired|tested|realized)|"
     r"the (?:first|biggest|worst) mistake|we screwed up|it failed|we figured out)\b", 3),
    (r"\b(?:mistake|trap|failure|failed|regret)\w*", 2),
    (r"\b(?:you have to|you need to|never|always|the rule|the only|the key|"
     r"the real (?:issue|question|problem)|in reality|instead of)\b", 1),
    (r"\b(?:our (?:method|process|framework)|we recommend|my advice|"
     r"here's what i do|step by step)\b", 2),
]

# Bruit typique : politesse, transitions, appels à l'abonnement.
# ⚠️ « like » seul est proscrit : en anglais c'est un mot de remplissage omniprésent.
BRUIT = re.compile(
    r"\b(?:abonne[zr]|(?:mets|met|mettez) un like|commentaire|bienvenue|merci beaucoup|"
    r"bonjour à tous|on se retrouve|dans cette vidéo|à très vite|"
    r"subscribe|hit the like|welcome back|in this video|thanks for watching|"
    r"link in the description|comment below|smash that)\b", re.I)


def charger_mots_cles(chemin):
    """Lit le fichier de mots-clés du profil ; chaque entrée vaut 2 points."""
    motifs = []
    for ligne in pathlib.Path(chemin).read_text(encoding="utf-8").splitlines():
        ligne = ligne.strip()
        if not ligne or ligne.startswith("#"):
            continue
        if ligne.startswith("re:"):
            motif = ligne[3:].strip()
        else:
            # Bornes Unicode plutôt que \b, qui ne voit pas la fin d'un mot accentué.
            motif = r"(?<![\w])" + re.escape(ligne) + r"(?![\w])"
        if motif:                      # une ligne vide donnerait un motif qui matche tout
            motifs.append((motif, 2))
    return motifs


def passages(texte, taille=45):
    """Découpe en fenêtres de ~`taille` mots, sur les frontières de phrase.

    Certains transcripts arrivent SANS AUCUNE PONCTUATION : découper sur `[.!?]`
    renverrait un unique bloc de plusieurs milliers de mots. Toute « phrase » plus
    longue que deux fenêtres est donc recoupée au mot.
    """
    texte = re.sub(r"\s+", " ", texte).strip()
    phrases = []
    for ph in re.split(r"(?<=[.!?])\s+", texte):
        mots = ph.split()
        if len(mots) > 2 * taille:
            for i in range(0, len(mots), taille):
                phrases.append(" ".join(mots[i:i + taille]))
        else:
            phrases.append(ph)
    bloc, n = [], 0
    for ph in phrases:
        bloc.append(ph)
        n += len(ph.split())
        if n >= taille:
            yield " ".join(bloc)
            bloc, n = [], 0
    if bloc:
        yield " ".join(bloc)


def score(p, marqueurs):
    if BRUIT.search(p):
        return 0
    return sum(poids for rx, poids in marqueurs if rx.search(p))


def condenser(chemin, maxi, marqueurs):
    texte = pathlib.Path(chemin).read_text(encoding="utf-8", errors="replace")
    notes = [(score(p, marqueurs), i, p) for i, p in enumerate(passages(texte))]
    retenus = sorted((n for n in notes if n[0] >= 4), key=lambda t: -t[0])[:maxi]
    retenus.sort(key=lambda t: t[1])            # remettre dans l'ordre du récit
    total = sum(n[0] for n in notes)
    densite = total / max(len(notes), 1)
    return densite, len(notes), retenus


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fichiers", nargs="+")
    ap.add_argument("--max", type=int, default=20, help="passages retenus par vidéo")
    ap.add_argument("--index", action="store_true", help="classement par densité seulement")
    ap.add_argument("--mots-cles", help="fichier de mots-clés propres au profil (2 points chacun)")
    a = ap.parse_args()

    brut = list(MARQUEURS)
    if a.mots_cles:
        brut += charger_mots_cles(a.mots_cles)
    marqueurs = [(re.compile(p, re.I), poids) for p, poids in brut]

    resultats = []
    for f in a.fichiers:
        try:
            resultats.append((f, *condenser(f, a.max, marqueurs)))
        except Exception as e:                    # un transcript illisible ne casse pas le lot
            print(f"!! {f} : {e}", file=sys.stderr)

    resultats.sort(key=lambda r: -r[1])

    if a.index:
        print(f"{'densité':>8}  {'blocs':>6}  fichier")
        for f, d, n, _ in resultats:
            print(f"{d:8.2f}  {n:6d}  {pathlib.Path(f).name}")
        return

    for f, d, n, retenus in resultats:
        # Retirer le préfixe « chaîne__ », identique sur tout un corpus.
        nom = pathlib.Path(f).name
        nom = nom.split("__", 1)[1] if "__" in nom else nom
        print(f"\n\n{'=' * 78}\n### {nom}\n### densité {d:.2f} · {n} blocs · {len(retenus)} retenus\n{'=' * 78}")
        for s, _, p in retenus:
            print(f"\n[{s}] {p}")


if __name__ == "__main__":
    main()
