"""Univers du reel = celui de la RUSH (Bruce Block, The Visual Story : 7 composantes ; Roger Deakins : lumière justifiée).
  python3 univers_check.py fiche clip.mp4          -> univers.json + univers.jpg : la fiche univers AVANT tout visuel
  python3 univers_check.py check plan.json         -> test « 5 sur 7 » de chaque ajout (inserts + b-rolls) + univers-check.jpg
Les 7 composantes : espace, ligne, forme, couleur, ton, mouvement, rythme. Un ajout doit en partager au moins 5 avec la rush ;
il peut contraster sur UNE seule, exprès (l'accent). Mesurées ici : couleur, ton, mouvement, rythme.
Espace, ligne, forme : à juger À L'ŒIL sur univers-check.jpg (rush à gauche, ajout à droite), puis compléter le score.
Seuils [H] (experts : principe sourcé, chiffres à tester) : couleur = 80 % des pixels à moins de 30 (Delta E) de la palette de la
rush ou neutres ; ton = pas plus lumineux que la pièce, pas de voile gris ni de blancs brûlés (lancer match_look.py --fix AVANT) ;
mouvement = image (animée doucement par le moteur) ou plan stable (<= 1,2 px/image, pic <= 6) ; rythme = durée entre 0,5 et 2 x
la médiane des ajouts du même type. Titres et textes (nom avec titre / title / texte, ou "layer": "ui") : hors test.
"""
import json, os, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lookstats import frames, stats, face, _lab, IMG

EYE = ["espace", "ligne", "forme"]


def shakes(path, ss=0, du=None):
    """Déplacement global image à image (corrélation de phase, même mesure que broll.py), en px par image à 30 i/s."""
    W, H = 270, 480
    cmd = ["ffmpeg", "-v", "error", "-ss", str(ss)] + (["-t", str(du)] if du else []) + ["-i", path, "-vf",
           f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps=15", "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    f = np.frombuffer(subprocess.check_output(cmd), np.uint8).reshape(-1, H, W).astype(np.float32)
    win = np.outer(np.hanning(H), np.hanning(W)); F = [np.fft.fft2(x * win) for x in f]; d = []
    for A, B in zip(F, F[1:]):
        R = A * np.conj(B); R /= np.abs(R) + 1e-9; r = np.abs(np.fft.ifft2(R)); y, x = np.unravel_index(r.argmax(), r.shape)
        y, x = (y - H if y > H // 2 else y), (x - W if x > W // 2 else x); d.append((x * x + y * y) ** .5 / 2)
    return np.array(d) if d else np.zeros(1)


def coverage(S, R):
    """% des pixels de l'ajout proches (Delta E <= 30) d'une couleur de la rush, ou neutres (gris, noir, blanc)."""
    pal = np.array([c[2] for c in R["palette"]])
    lab = np.array([c[2] for c in S["palette"]]); share = np.array([c[1] for c in S["palette"]])
    near = (np.sqrt(((lab[:, None] - pal[None]) ** 2).sum(2)).min(1) <= 30) | (np.hypot(lab[:, 1], lab[:, 2]) < 10)
    return round(float(share[near].sum()), 1)


def fiche(cam):
    R = stats(frames(cam)); F = face(cam)
    temp = "chaude" if R["rb_lumiere"] > 1.08 else "froide" if R["rb_lumiere"] < 0.92 else "neutre"
    u = {"rush": cam,
         "couleur": {"palette": [{"hex": h, "part": p} for h, p, _ in R["palette"]], "accent": "1 seul, pris dans la palette (règle DA)"},
         "ton": {"noirs_P1": R["p1"], "mediane_P50": R["p50"], "hautes_lumieres_P99": R["p99"], "nettete": R["nettete"]},
         "lumiere": {"couleur": f"{temp} (R/B {R['rb_lumiere']})", "source": "À REMPLIR en regardant univers.jpg : côté, couleur, dureté"},
         "cadre": F,
         "espace": "À REMPLIR : profondeur (plat / profond), fond (uni, bureau, extérieur)",
         "ligne": "À REMPLIR : lignes dominantes (verticales, horizontales, diagonales)",
         "forme": "À REMPLIR : formes dominantes (rondes, carrées, organiques)",
         "mouvement": "À REMPLIR : caméra fixe / main ; gestes amples ou posés",
         "rythme": "À REMPLIR : débit et énergie (posé, rapide)"}
    json.dump(u, open("univers.json", "w"), indent=1, ensure_ascii=False)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", cam, "-vf", "fps=4/30,scale=270:-1,tile=4x1", "-frames:v", "1", "univers.jpg"])
    print(f"univers.json : palette {' '.join(c['hex'] for c in u['couleur']['palette'])} · lumière {temp} · noirs {R['p1']} · "
          f"médiane {R['p50']} · hautes lumières {R['p99']}")
    print("À compléter à l'œil (univers.jpg) : source de lumière, espace, ligne, forme, mouvement, rythme. "
          "Puis : plan.colors depuis la palette, lumière dans chaque prompt Higgsfield.")


def check(plan_p):
    here = os.path.dirname(os.path.abspath(plan_p)); plan = json.load(open(plan_p))
    P = lambda s: s if os.path.isabs(s) else os.path.join(here, s)
    cam = P(plan["cam"]); R = stats(frames(cam))
    # titres / textes posés PAR-DESSUS la vidéo (calque d'interface) : pas des objets de la pièce, hors test
    ui = lambda x: x.get("layer") == "ui" or any(k in os.path.basename(x["src"]).lower() for k in ("titre", "title", "texte"))
    adds = [("insert", P(x["src"]), x["start"], x["end"], 0) for x in plan.get("inserts", []) if not ui(x)]
    adds += [("b-roll", P(x["src"]), x["start"], x["end"], x.get("from", 0) if x.get("from") != "auto" else 0) for x in plan.get("brolls", [])]
    if not adds: print("aucun ajout (inserts, b-rolls) dans le plan"); return
    med = {k: float(np.median([b - a for kk, _, a, b, _ in adds if kk == k])) for k in {x[0] for x in adds}}
    cnt = {k: sum(1 for x in adds if x[0] == k) for k in med}
    rows, tiles = [], []
    for i, (kind, src, a, b, frm) in enumerate(adds):
        img = src.lower().endswith(IMG)
        S = stats(frames(src, 1 if img else 4, frm, frm + (b - a)))
        obj = S["transparent"] > 2
        cov = coverage(S, R)
        ok = {"couleur": cov >= 80}
        ok["ton"] = (S["p99"] <= R["p99"] + 15) if obj else (S["p99"] <= 235 and S["p1"] <= R["p1"] + 8)
        if img: ok["mouvement"] = True
        else:
            d = shakes(src, frm, b - a); ok["mouvement"] = bool(d.mean() <= 1.2 and d.max() <= 6)
        ok["rythme"] = cnt[kind] < 2 or 0.5 * med[kind] <= b - a <= 2 * med[kind]   # régulier : entre 0,5 et 2 x la durée médiane du même type
        n = sum(ok.values()); need = max(0, 5 - n)
        verdict = "KO (même avec 3/3 à l'œil)" if need > 3 else f"il faut {need}/3 à l'œil (espace, ligne, forme)" if need else "OK dès maintenant"
        if not ok["ton"]: verdict += " · ton : passer d'abord match_look.py --fix"
        rows.append(f"{i + 1}. {kind} {os.path.basename(src)} {a:.1f}-{b:.1f} s : auto {n}/4 "
                    f"[{' '.join(('✓ ' if v else '✗ ') + k for k, v in ok.items())}] · couleur {cov} % proche de la rush · {verdict}")
        tiles.append((cam, (a + b) / 2, src, frm + (b - a) / 2 if not img else None, i))
    print(f"Univers de la rush : palette {' '.join(h for h, _, _ in R['palette'])} · P1 {R['p1']} · P99 {R['p99']}\n" + "\n".join(rows))
    # planche : une ligne par ajout, rush (même instant) à gauche, ajout à droite, sur fond de la couleur dominante de la rush
    os.makedirs("univers-tmp", exist_ok=True); parts = []
    bg = R["palette"][0][0].replace("#", "0x")
    for cam_, t, src, ts, i in tiles:
        ffr = f"univers-tmp/{i}.jpg"
        if ts is not None:   # vidéo : extraire l'image d'abord (sinon l'incrustation arrive après la 1re image de la planche = vide)
            png = f"univers-tmp/{i}.png"
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.2f}", "-i", src, "-frames:v", "1", png]); src = png
        inp = ["-ss", f"{t:.2f}", "-i", cam_, "-i", src]
        subprocess.run(["ffmpeg", "-y", "-v", "error", *inp, "-f", "lavfi", "-i", f"color=c={bg}:s=270x480", "-filter_complex",
                        "[0:v]scale=270:480,setsar=1[a];[1:v]scale=270:480:force_original_aspect_ratio=decrease[o];"
                        "[2:v][o]overlay=(W-w)/2:(H-h)/2:shortest=1[b];[a][b]hstack", "-frames:v", "1", ffr])
        parts.append(ffr)
    subprocess.run(["ffmpeg", "-y", "-v", "error", *sum([["-i", x] for x in parts], []), "-filter_complex",
                    "".join(f"[{k}:v]" for k in range(len(parts))) + f"vstack=inputs={len(parts)}" if len(parts) > 1 else "null",
                    "univers-check.jpg"])
    for x in os.listdir("univers-tmp"): os.remove(os.path.join("univers-tmp", x))
    os.rmdir("univers-tmp")
    print("À l'œil : univers-check.jpg (gauche = rush au même instant, droite = ajout). Pour chaque ajout : espace, ligne, forme "
          "partagés avec la rush ? Puis le test Deakins : d'où vient sa lumière ? est-il dans CETTE pièce ? sert-il la phrase ? Un non = retiré.")


if __name__ == "__main__":
    {"fiche": fiche, "check": check}[sys.argv[1]](sys.argv[2])
