"""B-rolls : créneaux réguliers + recherche dans la bibliothèque.

  python3 broll.py slots plan.json words.json --density low|high
      -> créneaux répartis RÉGULIÈREMENT sur toute la vidéo (jamais groupés), hors hook, chiffres, listes, pastilles.
         low  = 1 plan de ~1.8 s toutes les ~8 s (illustration posée)
         high = 1 plan de ~1 s toutes les ~3.5 s (très dynamique)
         Pour chaque créneau : les mots prononcés à ce moment-là (= ce qu'il faut illustrer).
  python3 broll.py prep plan.json
      -> copie chaque B-roll choisi (plan.brolls[].src absolu + from) dans broll/ : coupé, recadré 1080x1920, 30 i/s.
  python3 broll.py search mot1 mot2 ...
      -> les 12 meilleurs fichiers de ta bibliothèque (index _INDEX.csv de ton dossier brolls, voir outils/indexer-brolls),
         verticaux d'abord. Sans index : cherche les mots dans les noms de fichiers et de dossiers.
  python3 broll.py steady fichier.mp4 2.5
      -> le passage de 2,5 s le plus STABLE du fichier (toujours des plans stables en B-roll).
         Tremblement = déplacement de l'image d'une image à l'autre (px, image de 270 px de large).
         Bon : moyenne <= 1,2 et pic <= 6 (un monteur humain : 0 à 1,4). prep l'utilise tout seul si "from": "auto".
B-rolls BRUTS : jamais de filtre ni d'étalonnage créatif (ça fait « filtre bizarre »).
Plans à ne jamais proposer : une ligne par plan (colonne action de l'index, ou nom de fichier) dans <brolls_root>/_exclus.txt (# = commentaire).
"""
import csv, json, os, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reglages
CFG = reglages.charger()
PASSE = ("souvenir", "passe", "avant", "enfan", "jeune", "ado", "etudi", "debut", "ancien", "galere")

def slots(plan_p, words_p, density):
    plan = json.load(open(plan_p)); W = json.load(open(words_p))["words"]
    import subprocess
    cam = os.path.join(os.path.dirname(os.path.abspath(plan_p)), plan["cam"])
    dur = plan.get("duration") or float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", cam]))
    every, length = {"low": (8.0, 1.8), "high": (3.5, 1.0)}[density]
    busy = [(0, 2.2), (dur - 1.0, dur)]                       # hook + fin
    busy += [(n["start"] - .3, n["end"] + .3) for n in plan.get("numbers", [])]
    busy += [(l["start"] - .3, l["end"] + .3) for l in plan.get("lists", [])]
    if plan.get("bullets"): busy.append((plan["bullets"]["at"][0] - .3, plan["bullets"]["end"] + .3))
    free = lambda a, b: all(b <= x or a >= y for x, y in busy)
    out, t = [], 2.2 + every / 2
    while t < dur - 1.5:
        # on cherche le début de mot libre le plus proche de la cible t (créneaux réguliers, calés sur la voix)
        cands = sorted((abs(w["start"] - t), w["start"]) for w in W if free(w["start"], w["start"] + length))
        if cands and cands[0][0] < every / 2:
            a = round(cands[0][1] - 0.03, 2); b = round(a + length, 2)
            said = " ".join(w["text"] for w in W if a - 0.6 <= w["start"] <= b + 0.3)
            out.append({"start": a, "end": b, "dit": said})
        t += every
    print(json.dumps(out, ensure_ascii=False, indent=1))

def search(terms):
    root = CFG.get("brolls_root") or ""
    p = CFG.get("brolls_index")
    terms = [t.lower() for t in terms]
    ex = os.path.join(root, "_exclus.txt")   # plans où la personne n'est pas toi, plans ratés...
    exclus = {l.split("#")[0].strip() for l in open(ex, encoding="utf-8")} - {""} if os.path.exists(ex) else set()
    if not p or not os.path.exists(p):
        # pas d'index : on cherche dans les noms de fichiers et de dossiers
        if not os.path.isdir(root):
            print(f"Bibliothèque B-roll introuvable ({root}). Dépose tes vidéos dans ce dossier, puis lance outils/indexer-brolls/indexer.py."); return
        hits = []
        for dp, _, fs in os.walk(root):
            for f in fs:
                if f.startswith(".") or not f.lower().endswith((".mp4", ".mov", ".m4v", ".jpg", ".jpeg", ".png")): continue
                if f in exclus or os.path.splitext(f)[0] in exclus: continue
                path = os.path.join(dp, f)
                score = sum(t in path.lower() for t in terms)
                if score: hits.append((score, path))
        for sc, path in sorted(hits, key=lambda x: -x[0])[:12]: print(sc, path)
        if not hits: print("Rien d'adapté (pas d'index : lance outils/indexer-brolls/indexer.py pour chercher par action et par lieu)."
                           + (" -> générer avec Higgsfield." if CFG.get("higgsfield") else " (Higgsfield désactivé : garde la face cam, Pexels, ou tes photos.)"))
        return
    rows, mini = [], CFG.get("brolls_min_date", "")
    passe = any(t.startswith(PASSE) for t in terms)
    for r in csv.DictReader(open(p, encoding="utf-8")):
        if r.get("action") in exclus or r.get("fichier") in exclus: continue
        if mini and r.get("date_tournage", "") < mini: continue   # tourné trop tôt ou non daté
        if r.get("usage") == "souvenir" and not passe: continue   # photo du passé : seulement quand on parle du passé
        hay = " ".join([r.get("theme", ""), r.get("action", ""), r.get("lieu", ""), r.get("tenue", ""), r.get("usage", "")]).lower()
        score = sum(t in hay for t in terms)
        if score and (r.get("qualite", "ok") == "ok" or r.get("usage") == "souvenir"):   # vieille photo = qualité moyenne normale
            rows.append((score, r.get("orientation") == "V", float(r.get("duree_s") or 0), r))
    rows.sort(key=lambda x: (-x[0], not x[1], -x[2]))
    for s, v, d, r in rows[:12]:
        print(f'{s} {r["orientation"]} {d:5.1f}s  {os.path.join(CFG["brolls_root"], r["dossier"], r["fichier"])}  [{r["action"]} · {r["lieu"]} · personne visible={r.get("personne_visible")} · {r.get("date_tournage")}{" · SOUVENIR" if r.get("usage") == "souvenir" else ""}]')
    if not rows: print("Rien d'adapté." + (" -> générer avec Higgsfield." if CFG.get("higgsfield") else " (Higgsfield désactivé : garde la face cam, Pexels, ou tes photos.)"))

SHAKE_MAX, PEAK_MAX = 1.2, 6.0

def shakes(path, ss=0, du=None):
    """Déplacement global image à image (corrélation de phase), à 15 i/s, en px pour 270x480."""
    import subprocess
    import numpy as np
    W, H = 270, 480
    cmd = ["ffmpeg", "-v", "error", "-ss", str(ss)] + (["-t", str(du)] if du else []) + ["-i", path, "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps=15", "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    f = np.frombuffer(subprocess.check_output(cmd), np.uint8).reshape(-1, H, W).astype(np.float32)
    win = np.outer(np.hanning(H), np.hanning(W)); F = [np.fft.fft2(x * win) for x in f]; d = []
    for A, B in zip(F, F[1:]):
        R = A * np.conj(B); R /= np.abs(R) + 1e-9; r = np.abs(np.fft.ifft2(R)); y, x = np.unravel_index(r.argmax(), r.shape)
        y, x = (y - H if y > H // 2 else y), (x - W if x > W // 2 else x); d.append((x * x + y * y) ** .5 / 2)   # /2 : 15 i/s -> px par image à 30 i/s
    return np.array(d)

def steady(path, du):
    """(from, moyenne, pic) du passage de du secondes le plus stable."""
    import numpy as np
    d = shakes(path); n = max(1, int(du * 15)); best = None
    for i in range(0, max(1, len(d) - n + 1)):
        w = d[i:i + n]; sc = (w.mean(), w.max())
        if best is None or sc[0] + sc[1] / 10 < best[1] + best[2] / 10: best = (i / 15, *sc)
    return best

def prep(plan_p):
    import subprocess
    d = os.path.dirname(os.path.abspath(plan_p)); plan = json.load(open(plan_p))
    os.makedirs(os.path.join(d, "broll"), exist_ok=True)
    vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30"
    for i, b in enumerate(plan.get("brolls", [])):
        if not os.path.isabs(b["src"]): continue
        img = b["src"].lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
        name = f"broll/b{i}.jpg" if img else f"broll/b{i}.mp4"
        if not img:   # plan stable obligatoire : "from": "auto" = meilleur passage ; sinon on mesure et on prévient
            du = b["end"] - b["start"]
            if b.get("from") == "auto": b["from"], m, pk = steady(b["src"], du)
            else: d_ = shakes(b["src"], b.get("from", 0), du); m, pk = d_.mean(), d_.max()
            print(f"  tremblement {m:.2f} px/img, pic {pk:.1f}" + ("  <-- INSTABLE : prendre un autre passage (from auto) ou un autre plan" if m > SHAKE_MAX or pk > PEAK_MAX else "  (stable)"))
        cmd = ["ffmpeg", "-y", "-v", "error"] + ([] if img else ["-ss", str(b.get("from", 0))]) + ["-i", b["src"]]
        cmd += ["-vf", vf.replace(",fps=30", "") if img else vf] + (["-frames:v", "1", "-q:v", "2"] if img else
               ["-t", f"{b['end'] - b['start'] + 0.2:.2f}", "-an", "-c:v", "libx264", "-crf", "18", "-preset", "fast"])
        subprocess.check_call(cmd + [os.path.join(d, name)])
        b["orig"], b["src"], b["from"] = b["src"], name, 0
        print(name, "<-", b["orig"])
    json.dump(plan, open(plan_p, "w"), ensure_ascii=False, indent=1)

if sys.argv[1] == "prep":
    prep(sys.argv[2])
elif sys.argv[1] == "steady":
    f_, m, pk = steady(sys.argv[2], float(sys.argv[3]))
    print(f"from {f_:.2f}s  tremblement {m:.2f} px/img, pic {pk:.1f}" + ("  <-- INSTABLE, changer de plan" if m > SHAKE_MAX or pk > PEAK_MAX else "  (stable)"))
elif sys.argv[1] == "slots":
    slots(sys.argv[2], sys.argv[3], sys.argv[sys.argv.index("--density") + 1] if "--density" in sys.argv else "low")
else:
    search(sys.argv[2:])
