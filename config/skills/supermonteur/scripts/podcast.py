"""Famille « À plusieurs » (podcast, visio, split screen) : 2 personnes côte à côte en 16:9 -> reel 9:16.
Mise en page MIX validée : split haut/bas par défaut, plein écran sur celui qui parle pendant la phrase qui porte un mot fort
(2-3,5 s), jamais moins de 1,5 s de split entre deux pleins écrans.

  python3 podcast.py speakers src.mp4 words.json        # qui parle, mot par mot (bouche qui bouge dans chaque tuile) -> words.json["who"]
  python3 podcast.py layout plan.json                    # clip.mp4 9:16 + plan.cam / plan.subY / plan.subYAt / plan.zoom=false

plan.json -> "podcast": {"src": "cut169.mp4", "top": "L", "delogo": [x, y, w, h] | null, "segments": "cut169.segments.json"}
  src   = le passage dérushé en 16:9 (tuile gauche = L, tuile droite = R)
  top   = la tuile en haut du split (défaut L = l'hôte, à gauche)
  delogo = logo incrusté à effacer, en pixels de la source (ex. l'ancien logo d'une visio : [24, 34, 266, 152])
  segments = cut.segments.json de derush.py : les pleins écrans démarrent sur une coupe quand elle est à < 0,15 s
Les plein écrans sont décidés par plan.keywords (1re occurrence de chaque mot fort) ; avec un titre-question (pas de mots forts),
par plan.podcast.full = [[start, end], ...] écrit à la main.
"""
import json, os, subprocess, sys, tempfile
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.join(os.path.dirname(HERE), "models", "face_landmarker.task")
MIN_SPLIT, MAX_FULL, SEAM = 1.5, 3.5, 960
FPS = 12


def probe(src):
    o = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                                 "-show_entries", "format=duration", "-of", "json", src])
    j = json.loads(o)
    return j["streams"][0]["width"], j["streams"][0]["height"], float(j["format"]["duration"])


def faces(src):
    """Par tuile (L, R) et par image : ouverture de la mâchoire (blendshape jawOpen) + centre du visage, à 12 i/s."""
    import mediapipe as mp
    from mediapipe.tasks.python import vision, BaseOptions
    W, H, _ = probe(src)
    w, h = 480, int(480 * H / (W / 2)) // 2 * 2       # chaque tuile analysée en 480 px de large
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", src, "-vf", f"fps={FPS},scale={2 * w}:{h}",
                                   "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
    fr = np.frombuffer(raw, np.uint8).reshape(-1, h, 2 * w, 3)
    out = {}
    for side, x0 in (("L", 0), ("R", w)):
        det = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=MOD), output_face_blendshapes=True,
            running_mode=vision.RunningMode.VIDEO))
        jaw, cx, cy = [], [], []
        for k, f in enumerate(fr):
            r = det.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(f[:, x0:x0 + w])),
                                     int(k * 1000 / FPS))
            if r.face_landmarks:
                bs = {b.category_name: b.score for b in r.face_blendshapes[0]}
                lm = r.face_landmarks[0]
                jaw.append(bs.get("jawOpen", 0) + bs.get("mouthFunnel", 0) * .5)
                cx.append(np.mean([p.x for p in lm])); cy.append(np.mean([p.y for p in lm]))
            else:
                jaw.append(np.nan); cx.append(np.nan); cy.append(np.nan)
        out[side] = {"jaw": np.array(jaw), "cx": np.nanmedian(cx), "cy": np.nanmedian(cy)}
    return out


def speakers(src, words_p):
    """Qui parle : la bouche qui BOUGE le plus (variation de jawOpen) pendant la phrase. Vote par phrase (ponctuation / blanc > 0,35 s)."""
    W = json.load(open(words_p))
    ws = W["words"]
    F = faces(src)
    # MOUVEMENT de la mâchoire seulement : la bouche ouverte d'un sourire qui écoute ne compte pas (sourire
    # pris pour de la parole). Visage perdu (main devant) = image ignorée, pas « bouche fermée ».
    motion = {}
    for s in ("L", "R"):
        j = F[s]["jaw"]
        d = np.abs(np.diff(j, prepend=j[0]))
        motion[s] = d
    n = len(motion["L"])
    def score(s, a, b):
        v = motion[s][max(0, int(a * FPS)):max(int(a * FPS) + 1, min(n, int(b * FPS) + 1))]
        v = v[~np.isnan(v)]
        return float(v.mean()) if len(v) else 0.0
    phrases, cur = [], []
    for i, w in enumerate(ws):
        if cur and (w["start"] - ws[cur[-1]]["end"] > .35): phrases.append(cur); cur = []
        cur.append(i)
        if w["text"].rstrip()[-1:] in ".!?": phrases.append(cur); cur = []
    if cur: phrases.append(cur)
    print("qui parle (L = gauche, R = droite) :")
    for p in phrases:
        a, b = ws[p[0]]["start"], ws[p[-1]]["end"]
        sl, sr = score("L", a, b), score("R", a, b)
        who = "L" if sl >= sr else "R"
        conf = abs(sl - sr) / max(sl + sr, 1e-6)
        for i in p: ws[i]["who"] = who
        txt = " ".join(ws[i]["text"] for i in p)
        print(f"  {a:6.2f}-{b:6.2f} {who} {'  ' if conf > .15 else '??'} {txt[:70]}")
    W["faces"] = {s: {"cx": round(float(F[s]["cx"]), 4), "cy": round(float(F[s]["cy"]), 4)} for s in ("L", "R")}
    json.dump(W, open(words_p, "w"), ensure_ascii=False)
    print("?? = doute (les deux bouches bougent pareil) : vérifier à l'œil et corriger \"who\" dans words.json")


def subzone_of(src, x, crop_w, H):
    """Hauteur des sous-titres en plein écran (subzone.py sur 4 s du recadrage de cette personne)."""
    tmp = tempfile.mktemp(suffix=".mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-t", "4", "-i", src, "-vf", f"crop={crop_w}:{H}:{x}:0,scale=1080:1920",
                    "-an", "-c:v", "libx264", "-crf", "23", tmp], check=True)
    y = int(subprocess.check_output(["python3", os.path.join(HERE, "subzone.py"), tmp]).decode().strip().splitlines()[-1])
    os.remove(tmp)
    return y


def layout(plan_p):
    here = os.path.dirname(os.path.abspath(plan_p))
    P = json.load(open(plan_p))
    pc = P["podcast"]
    src = os.path.join(here, pc["src"])
    W_, H, dur = probe(src)
    tw = W_ // 2
    words = json.load(open(os.path.join(here, P["words"])))
    ws, fc = words["words"], words.get("faces", {"L": {"cx": .5, "cy": .45}, "R": {"cx": .5, "cy": .45}})
    if not all("who" in w for w in ws): sys.exit("lancer d'abord : podcast.py speakers <src> <words.json>")
    top = pc.get("top", "L"); bot = "R" if top == "L" else "L"

    # coupes du dérush (les pleins écrans démarrent dessus quand c'est possible : le changement de plan cache le raccord)
    cuts = [0.0]
    if pc.get("segments") and os.path.exists(os.path.join(here, pc["segments"])):
        t = 0.0
        for a, b in json.load(open(os.path.join(here, pc["segments"]))):
            t += b - a; cuts.append(t)

    # --- fenêtres plein écran : la phrase qui porte un mot fort (1re occurrence), 2-3,5 s
    norm = lambda s: s.lower().strip(".,!?…\"'«» ").replace("’", "'")
    kws = [] if P.get("title") else [[norm(x) for x in str(k).split()] for k in P.get("keywords", [])]
    full = [list(x) for x in pc.get("full", [])]
    used = set()
    for i, w in enumerate(ws):
        for k, ph in enumerate(kws):
            if k in used or [norm(ws[i + j]["text"]) if i + j < len(ws) else None for j in range(len(ph))] != ph: continue
            used.add(k)
            j = i                                   # début de phrase : on remonte jusqu'à la ponctuation, même voix
            while j > 0 and ws[j - 1]["who"] == w["who"] and ws[j - 1]["text"].rstrip()[-1:] not in ".,!?" and w["start"] - ws[j - 1]["start"] <= 1.6:
                j -= 1
            s = ws[j]["start"] - .05
            near = min(cuts, key=lambda c: abs(c - s))
            if abs(near - s) < .15: s = near
            e = ws[i + len(ph) - 1]["end"]
            k2 = i + len(ph)                        # on finit la phrase si elle tient dans 3,5 s
            while k2 < len(ws) and ws[k2]["who"] == w["who"] and ws[k2]["end"] - s <= MAX_FULL and ws[k2 - 1]["text"].rstrip()[-1:] not in ".,!?":
                e = ws[k2]["end"]; k2 += 1
            full.append([max(0, s), min(dur, e + .3)])
    # HOOK (score.py : rien ne bougeait avant 8,3 s) : si aucun plein écran avant 3 s, on ouvre en plein écran sur celui
    # qui parle en premier (la question), 2-3 s, coupé sur une fin de mot, puis split pour voir l'autre réagir
    full.sort()
    if not full or full[0][0] > 3.0:
        first = ws[0]["who"]
        ends = [w["end"] for w in ws if w["who"] == first and 2.0 <= w["end"] <= 3.0]
        h_end = ends[-1] + .05 if ends else min(3.0, dur)
        if not full or full[0][0] - h_end >= MIN_SPLIT: full.insert(0, [0.0, h_end])
    merged = []
    for f in full:
        if merged and f[0] - merged[-1][1] < MIN_SPLIT: merged[-1][1] = max(merged[-1][1], f[1])
        else: merged.append(f)
    full = merged
    if full and full[0][0] < MIN_SPLIT and full[0][0] > 0: full[0][0] = 0
    if full and dur - full[-1][1] < MIN_SPLIT: full[-1][1] = dur
    who_at = lambda t: max(("L", "R"), key=lambda s: sum(min(w["end"], t + .6) - max(w["start"], t - .1)
                                                          for w in ws if w["who"] == s and w["end"] > t - .1 and w["start"] < t + .6) + (s == "R") * 1e-6)

    spans, t = [], 0.0
    for a, b in full:
        if a > t: spans.append((t, a, "split", None))
        spans.append((a, b, "full", who_at(a + .05))); t = b
    if t < dur: spans.append((t, dur, "split", None))

    # --- cadrages : split = tuile recadrée en 1080x960 (visage aux 42 %), plein écran = 9:16 centré sur le visage
    sh = min(H, int(tw * 960 / 1080)) // 2 * 2
    sy = {s: int(min(max(fc[s]["cy"] * H - .42 * sh, 0), H - sh)) for s in ("L", "R")}
    fw = int(H * 9 / 16) // 2 * 2
    fx = {s: int(min(max((0 if s == "L" else tw) + fc[s]["cx"] * tw - fw / 2, (0 if s == "L" else tw)), (tw if s == "L" else W_) - fw)) for s in ("L", "R")}
    X0 = {"L": 0, "R": tw}
    pre = "delogo=x={}:y={}:w={}:h={},".format(*pc["delogo"]) if pc.get("delogo") else ""
    LUX = "scale=1080:960:flags=lanczos,unsharp=5:5:0.5"
    fcx = f"[0:v]{pre}split={len(spans)}" + "".join(f"[s{i}]" for i in range(len(spans))) + ";"
    for i, (a, b, kind, who) in enumerate(spans):
        trim = f"trim={a:.3f}:{b:.3f},setpts=PTS-STARTPTS"
        if kind == "split":
            fcx += (f"[s{i}]{trim},split[t{i}][u{i}];[t{i}]crop={tw}:{sh}:{X0[top]}:{sy[top]},{LUX}[a{i}];"
                    f"[u{i}]crop={tw}:{sh}:{X0[bot]}:{sy[bot]},{LUX}[b{i}];[a{i}][b{i}]vstack,"
                    f"drawbox=x=0:y={SEAM - 2}:w=1080:h=4:color=black@0.9:t=fill[p{i}];")
        else:
            fcx += f"[s{i}]{trim},crop={fw}:{H}:{fx[who]}:0,scale=1080:1920:flags=lanczos,unsharp=5:5:0.6[p{i}];"
    fcx += "".join(f"[p{i}]" for i in range(len(spans))) + f"concat=n={len(spans)}:v=1:a=0,fps=30,format=yuv420p[v]"
    out = os.path.join(here, "clip.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", fcx, "-map", "[v]", "-map", "0:a",
                    "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-c:a", "aac", "-b:a", "192k", out], check=True)

    # --- sous-titres : sur la jonction en split (centrés sur la ligne), au niveau du col en plein écran
    ysplit = SEAM - 34
    yfull = {s: subzone_of(src, fx[s], fw, H) for s in {w for _, _, k, w in spans if k == "full"}}
    P["cam"], P["zoom"], P["subY"] = "clip.mp4", False, ysplit
    P["subYAt"] = [{"start": round(a, 3), "end": round(b, 3), "y": ysplit if k == "split" else yfull[w]} for a, b, k, w in spans]
    P["podcast"]["spans"] = [[round(a, 3), round(b, 3), k, w] for a, b, k, w in spans]
    json.dump(P, open(plan_p, "w"), ensure_ascii=False, indent=1)
    print(f"clip.mp4 : {dur:.1f} s · " + " | ".join(f"{k}{'-' + w if w else ''} {a:.2f}-{b:.2f}" for a, b, k, w in spans))
    print(f"sous-titres : split y={ysplit}, plein écran {yfull}")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "speakers": speakers(sys.argv[2], sys.argv[3])
    elif cmd == "layout": layout(sys.argv[2])
    else: sys.exit(__doc__)
