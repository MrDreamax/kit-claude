#!/usr/bin/env python3
"""Contrôles automatiques d'une fiche de publication (JSON). Sort la liste des contrôles ; code 1 si un contrôle bloque.
Règles : Brain/02-Formations/experts-legendes-instagram.md (mot-clé en 1re ligne, 5 hashtags max, 1 CTA, 1er commentaire, alt text)
+ anti ton IA (pas de tiret cadratin, pas de « ce n'est pas X, c'est Y »).
Usage : controle.py fiche.json
"""
import json, re, sys
from datetime import datetime


def controler(f):
    res = []  # (niveau, texte) niveau = ok | alerte | bloque

    def add(cond, ok_txt, ko_txt, niveau_ko="bloque"):
        res.append(("ok", ok_txt) if cond else (niveau_ko, ko_txt))

    import os
    add(os.path.exists(f.get("video", "")), "Vidéo trouvée", f"Vidéo introuvable : {f.get('video', '?')}")
    ig = f.get("instagram", {})
    leg = ig.get("legende", "")
    mot = f.get("mot_cle", "").strip()
    l1 = leg.strip().split("\n")[0].lower() if leg.strip() else ""
    ou = [x for x, v in (("dit à voix haute", f.get("dit_a_voix")), ("écrit sur la cover", f.get("sur_cover"))) if v]
    add(mot and mot.lower() in l1, f"Mot-clé « {mot} » en 1re ligne" + (", " + ", ".join(ou) if ou else ""),
        f"Mot-clé « {mot} » absent de la 1re ligne de la légende")
    if mot and not f.get("dit_a_voix"):
        res.append(("alerte", f"Mot-clé « {mot} » pas dit à voix haute dans la vidéo"))
    tags = re.findall(r"#\w+", leg)
    add(len(tags) <= 5, f"{len(tags)} hashtags (Instagram en autorise 5 max)", f"{len(tags)} hashtags : 5 max sur Instagram")
    add(len(leg) <= 2200, "Légende sous 2 200 caractères", f"Légende trop longue ({len(leg)} / 2 200)")
    cta = f.get("cta", "").strip()
    n_cta = len(re.findall(r"\b" + re.escape(cta) + r"\b", leg)) if cta else 0
    add(n_cta == 1, f"1 seul appel à l'action : Commente {cta}", f"CTA « {cta} » présent {n_cta} fois (il en faut 1)")
    add(bool(ig.get("premier_commentaire", "").strip()), "1er commentaire prêt (question)", "1er commentaire manquant")
    add(bool(ig.get("alt", "").strip()), "Texte alternatif rempli", "Texte alternatif manquant", "alerte")
    yt = f.get("youtube", {})
    add(0 < len(yt.get("titre", "")) <= 100, "Titre YouTube sous 100 caractères", f"Titre YouTube : {len(yt.get('titre',''))} caractères (1 à 100)")
    tk = f.get("tiktok", {}).get("legende", "")
    add(0 < len(tk) <= 2200, "Légende TikTok prête", "Légende TikTok vide ou trop longue")
    tous = "\n".join([leg, ig.get("premier_commentaire", ""), yt.get("titre", ""), yt.get("description", ""), tk])
    ia = []
    if "—" in tous:
        ia.append("tiret cadratin")
    if re.search(r"(ce n'est pas|ce n’est pas|c'est pas)[^.\n]{1,60}, c'est", tous, re.I):
        ia.append("« ce n'est pas X, c'est Y »")
    add(not ia, "Ton IA retiré, pas de tiret cadratin", "Ton IA à retirer : " + ", ".join(ia))
    c = f.get("cover", {})
    if c:
        mots = len((c.get("titre", "") + " " + c.get("sous_titre", "")).split())
        add(mots <= 6, "Texte de la cover dans la zone visible de la grille", f"Cover : {mots} mots, viser 2 à 4", "alerte")
        if c.get("source") == "broll":
            res.append(("ok", "Cover tirée de tes B-rolls" + (", retouchée Higgsfield à ta DA, visage intact" if c.get("retouche") == "higgsfield" else ", étalonnée à ta DA (sans retouche IA)")))
    try:
        d = datetime.fromisoformat(f["date"])
        add(d > datetime.now(), "Date dans le futur", "Date déjà passée : à décaler")
    except Exception:
        res.append(("bloque", "Date manquante ou illisible (format AAAA-MM-JJTHH:MM:SS)"))
    if f.get("heure_provisoire"):
        res.append(("alerte", f.get("note_heure", "Heure provisoire : pas encore assez de stats Metricool sur ton compte")))
    return res


if __name__ == "__main__":
    f = json.load(open(sys.argv[1]))
    r = controler(f)
    for niv, txt in r:
        print({"ok": "✓", "alerte": "!", "bloque": "✗"}[niv], txt)
    sys.exit(1 if any(n == "bloque" for n, _ in r) else 0)
