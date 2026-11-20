#!/usr/bin/env python3
"""Cut Notes AUTOMATIQUE 
Lancé SEUL juste après chaque montage (v1 comme retouche), sans rien demander.

  python3 ouvre.py <dossier du reel> [--video final.mp4] -> juste après un montage fini
  python3 ouvre.py <dossier du reel> --attendre -> lancé en arrière-plan quand le montage tourne dans
                                                                    SuperMonteur : attend statut « retours », puis pareil
  python3 ouvre.py <dossier du reel> --notes <dossier json> -> à « suivant » : les notes Cut Notes (ArtifactData list
        notes, out_dir) deviennent des retours SuperMonteur (/api/retour + /api/suivant : le correcteur ne retouche QUE les
        moments notés), on attend la nouvelle version, puis nouvelle copie de revue + round + 1 (même artifact).

Fait : copie de revue 720p (review.mp4, < 15 Mo), page cut-notes.html dans le dossier (l'outil Artifact ne publie
que sous ~/Documents/Montage), numéro de round (+1 à chaque passage), robot Monteur de la vitrine
« J'attends tes notes ».
Affiche une ligne JSON : {html, review, fps, nom, round, url}. Puis Claude, dans le même tour :
  1. url vide -> Artifact publish html (capabilities {"db": {}, "user": {}, "assets": {}, "comments": {}}, icône video),
                  écrire l'URL dans <dossier>/cut-notes.url
     url remplie -> on garde le MÊME artifact (1 artifact par vidéo)
  2. Artifact publish url + file_path review + asset: true -> id/url de l'asset
  3. ArtifactData set review/current = {"src": <url asset>, "name": nom, "fps": fps, "round": round}
  4. Artifact open url (la page s'ouvre toute seule chez lui)
Quand il écrit « suivant » : CUT-NOTES.md, section « Quand l'utilisateur dit suivant ».
"""
import argparse, glob, json, os, re, shutil, subprocess, sys, time, urllib.request
MONTEUR = "http://127.0.0.1:8801"

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.realpath(os.path.expanduser("~/Documents/Montage"))
ACTIVITE = os.path.join(RACINE, "apps/super/activite.py")


def video_du_reel(d):
    """final.mp4 sinon la dernière version de etat.json (SuperMonteur range versions/vN.mp4)."""
    f = os.path.join(d, "final.mp4")
    try:
        e = json.load(open(os.path.join(d, "etat.json")))
        v = os.path.join(d, e["versions"][-1]["fichier"])
        if os.path.exists(v) and (not os.path.exists(f) or os.path.getmtime(v) >= os.path.getmtime(f)): return v
    except Exception:
        pass
    return f


def nom_du_reel(d):
    try:
        e = json.load(open(os.path.join(d, "etat.json")))
        for k in ("titre", "nom"):
            if e.get(k): return str(e[k])
    except Exception:
        pass
    try:
        t = json.load(open(os.path.join(d, "plan.json"))).get("title") or {}
        n = " ".join(x for x in (t.get("l1"), t.get("l2")) if x)
        if n: return n
    except Exception:
        pass
    return re.sub(r"^\d{4}-\d{2}-\d{2}-", "", os.path.basename(d.rstrip("/"))).replace("-", " ")


def statut(d):
    try: return json.load(open(os.path.join(d, "etat.json"))).get("statut", "")
    except Exception: return ""


def attendre(d, minutes=45, deja=None):
    """Attend la fin du montage (statut « retours ») ; erreur / bloqué = on s'arrête et on le dit."""
    fin = time.time() + minutes * 60
    while time.time() < fin:
        st = statut(d)
        if st in ("erreur", "bloque"): sys.exit(f"Montage en panne (statut {st}) : lire etat.json, ne pas ouvrir Cut Notes.")
        if st == "retours" and (deja is None or version(d) > deja): return
        time.sleep(5)
    sys.exit(f"Montage toujours pas fini après {minutes} min (statut {statut(d)}).")


def version(d):
    try: return int(json.load(open(os.path.join(d, "etat.json"))).get("version", 0))
    except Exception: return 0


def post(chemin, corps):
    r = urllib.request.Request(MONTEUR + chemin, data=json.dumps(corps).encode(), headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(r, timeout=20))


def envoyer_notes(d, rid, dossier_notes, rnd):
    """Notes ouvertes du round en cours -> retours SuperMonteur, puis « suivant »."""
    N = []
    for f in glob.glob(os.path.join(dossier_notes, "**", "*.json"), recursive=True):
        try: n = json.load(open(f))
        except Exception: continue
        n = n.get("data", n)
        if int(n.get("round", 1)) != rnd or n.get("status") in ("fixed", "resolved") or not str(n.get("text", "")).strip(): continue
        N.append(n)
    if not N: sys.exit("Aucune note ouverte dans ce tour : demander en 1 ligne s'il a laissé des retours (rien n'est validé).")
    for n in sorted(N, key=lambda x: float(x.get("t", 0))):
        post(f"/api/retour/{rid}", {"t": float(n.get("t", 0)), "texte": str(n["text"]).strip()})
    post(f"/api/suivant/{rid}", {})
    return len(N)


def main():
    a = argparse.ArgumentParser(); a.add_argument("dossier"); a.add_argument("--video")
    a.add_argument("--attendre", action="store_true"); a.add_argument("--notes")
    o = a.parse_args()
    rid = os.path.basename(os.path.expanduser(o.dossier).rstrip("/"))
    d = os.path.realpath(os.path.expanduser(o.dossier))
    if not d.startswith(RACINE + os.sep):
        sys.exit(f"Dossier hors de {RACINE} : l'outil Artifact ne pourra pas publier. Copie le reel dessous d'abord.")
    f_etat = os.path.join(d, "cut-notes.json")
    try: etat = json.load(open(f_etat))
    except Exception: etat = {}
    envoyees = 0
    if o.notes:
        v0 = version(d)
        envoyees = envoyer_notes(d, rid, o.notes, int(etat.get("round", 1)))
        if os.path.exists(ACTIVITE):
            subprocess.run([sys.executable, ACTIVITE, "monteur", f"Je corrige tes {envoyees} notes"], capture_output=True)
        attendre(d, 30, deja=v0)
    elif o.attendre:
        attendre(d)
    v = os.path.realpath(o.video) if o.video else video_du_reel(d)
    if not os.path.exists(v): sys.exit(f"Pas de vidéo montée : {v}")

    html = os.path.join(d, "cut-notes.html")
    shutil.copy(os.path.join(ICI, "cut-notes.html"), html)          # toujours la dernière page du skill
    rv = os.path.join(d, "review.mp4")
    r = subprocess.run(["bash", os.path.join(ICI, "review_copy.sh"), v, rv], capture_output=True, text=True)
    if r.returncode not in (0, 2): sys.exit("Copie de revue ratée : " + (r.stderr or r.stdout)[-400:])
    _, taille, fps = r.stdout.split()[-3:]
    if r.returncode == 2:
        sys.exit(f"review.mp4 trop lourd ({int(taille) // 1048576} Mo > 15) : plan B = lui donner le chemin {v} à glisser dans la page.")

    url = open(os.path.join(d, "cut-notes.url")).read().strip() if os.path.exists(os.path.join(d, "cut-notes.url")) else ""
    rnd = int(etat.get("round", 0)) + 1 if url else 1
    etat.update({"round": rnd, "video": os.path.relpath(v, d), "le": time.strftime("%Y-%m-%d %H:%M")})
    json.dump(etat, open(f_etat, "w"), ensure_ascii=False, indent=1)

    if os.path.exists(ACTIVITE):
        subprocess.run([sys.executable, ACTIVITE, "monteur", "Vidéo prête : j'attends tes notes dans Cut Notes"], capture_output=True)

    print(json.dumps({"html": html, "review": rv, "fps": float(fps), "nom": nom_du_reel(d), "round": rnd, "url": url, "notes_envoyees": envoyees},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
