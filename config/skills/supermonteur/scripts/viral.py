#!/usr/bin/env python3
"""FAMILLE « MONTAGE VIRAL » : le tableau vit AU-DESSUS DE LA TÊTE, la face cam reste visible dessous.
Formats (même zone, même fondu) : comparaison en T (« t », validé version A), mauvais / bien / excellent (« mbe »), tier list (« tier »).

  python3 $S/viral.py layout plan.json   # AVANT build.mjs : place au-dessus de la tête (fondu si la tête est trop haute)
                                          #   -> clip_viral.mp4 + plan.cam / subY / viral.zone écrits tout seuls
  python3 $S/viral.py inject plan.json   # APRÈS build.mjs : pose le tableau de plan.viral (t | mbe | tier) dans index.html

plan.viral.t = {"title": {"sans", "serif", "at"}, "bar_at", "left": {"head", "icon": "cross", "at", "items": [[texte, t], ...]},
                "right": {"head", "icon": "check", "at", "items": [...]}, "win": {"at"}}   (texte sur 2 lignes : "a<br>b")
plan.viral.mbe = {"title": {...}, "cards": [{"label": "MAUVAIS", "at", "text"?, "color"?: bad|ok|top, "icon"?: cross|tilde|star|check}, x3],
                  "win": {"at", "card"?}}   cartes de gauche à droite (ordre où il les montre), chacune sur SON mot
plan.viral.tier = {"title": {...}, "rows"?: ["S","A","B","C","D"], "items": [{"text": "Podcast", "at": <mot du format>, "to": "S",
                   "land": <mot de la lettre>}, ...]}   le format grossit au centre quand il est nommé, file dans sa rangée sur la lettre
Règles :
- Place : haut de la tête visé à 720 px (5e centile = quand elle est la plus haute). Trop haute -> la cam descend, le mur
  du haut est prolongé (bande au-dessus de la tête, étirée + floutée) et la cam fond dedans sur 260 px. Validé « fondu ».
- Garde-fou sous-titres : sous le menton (menton + 0,41 x visage) et haut des sous-titres <= 1400 px (zone cachée par
  l'appli à 1479). Plan serré -> la cam descend MOINS et le T passe en COMPACT (zone < 690 px : 1 élément par colonne).
- T : voile sombre en haut, titre MAJUSCULES espacées + question en serif italique, trait horizontal qui s'ouvre du centre
  puis trait vertical qui descend, en-têtes croix rouge / coche bleue tracées, éléments en serif italique calés sur le mot
  (flou -> net, power3, jamais de rebond). Final (« oui ») : colonne perdante grisée + barrée, gagnante +7 % avec halo bleu.
"""
import json, os, shutil, subprocess, sys
import numpy as np

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET, FADE, SMAX, SUBMAX = 720, 260, 480, 1400
MARK = 'id="tttl"'


def measure(src):
    import mediapipe as mp
    from mediapipe.tasks.python import vision, BaseOptions
    W, H = 540, 960
    raw = subprocess.check_output(["ffmpeg", "-nostdin", "-v", "error", "-i", src, "-vf", f"fps=4,scale={W}:{H}",
                                   "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
    fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    det = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=os.path.join(SKILL, "models", "face_landmarker.task")),
        running_mode=vision.RunningMode.IMAGE))
    tops, chins, faces = [], [], []
    for f in fr:
        r = det.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(f)))
        if r.face_landmarks:
            L = r.face_landmarks[0]
            face = (L[152].y - L[10].y) * 1920
            tops.append(L[10].y * 1920 - 0.45 * face); chins.append(L[152].y * 1920); faces.append(face)
    if not tops:
        sys.exit("pas de visage : le montage viral demande une face cam")
    return int(np.percentile(tops, 5)), float(np.median(chins) + 0.41 * np.median(faces))


def layout(plan_path):
    plan = json.load(open(plan_path))
    src = plan["cam"]
    if src == "clip_viral.mp4":
        src = plan.get("viral", {}).get("src", src)
    head, suby0 = measure(src)
    S = int(max(0, min(SMAX, TARGET - head, SUBMAX - suby0)))
    zone = head + S - 30
    suby = int(round(min(max(suby0 + S, 1100), SUBMAX)))
    print(f"haut de tête {head}px · sous-titres {int(suby0)}px -> cam descendue de {S}px, zone tableau 270-{zone}px"
          f"{' (T COMPACT, plan serré)' if zone < 690 else ''}, sous-titres à {suby}px")
    if zone < 420:
        print("ATTENTION : zone < 420 px, le tableau ne tiendra pas. Retourner le rush avec de la place au-dessus de la tête.")
    out = "clip_viral.mp4"
    if S == 0:
        shutil.copyfile(src, out)
    else:
        from PIL import Image
        ramp = np.ones((1920, 1080), np.float32)
        x = np.linspace(0, 1, FADE)
        ramp[:FADE] = (x * x * (3 - 2 * x))[:, None]
        Image.fromarray((ramp * 255).astype(np.uint8)).save("_viral_mask.png")
        band = max(120, min(head - 60, 360))  # mur au-dessus de la tête, sans la tête
        fc = (f"[0:v]split[a][b];"
              f"[a]crop=1080:{band}:0:0,scale=1080:{S + FADE},boxblur=28:2,eq=brightness=-0.05,pad=1080:1920:0:0:black[bg];"
              f"[b]format=rgba[c];[1:v]format=gray,scale=1080:1920[m];[c][m]alphamerge[fg];"
              f"[bg][fg]overlay=0:{S}:shortest=1,format=yuv420p[v]")
        # masque à la cadence du rush + durée exacte (masque à 25 i/s par défaut sur un rush à 30 i/s
        # = alphamerge qui s'arrête 1,6 s avant la fin, image noire à la fin du reel)
        fps, dur = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                            "stream=r_frame_rate:format=duration", "-of", "default=nw=1:nk=1", src]).decode().split()[:2]
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", src, "-loop", "1", "-framerate", fps, "-i", "_viral_mask.png",
                        "-filter_complex", fc, "-map", "[v]", "-map", "0:a?", "-t", dur, "-c:v", "libx264", "-crf", "14", "-preset", "fast",
                        "-pix_fmt", "yuv420p", "-c:a", "copy", out], check=True)
        got = float(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                             "stream=duration", "-of", "csv=p=0", out]))
        if abs(got - float(dur)) > 0.1:
            sys.exit(f"clip_viral.mp4 fait {got:.2f} s au lieu de {float(dur):.2f} s : ne pas monter dessus")
        os.remove("_viral_mask.png")
    v = plan.setdefault("viral", {})
    v.update({"src": src, "shift": S, "zone": zone})
    plan["cam"], plan["subY"] = out, suby
    if suby > 1340 and plan.get("keywords"):
        print("mots forts retirés : à cette hauteur, le serif 132 px passerait sous les boutons de l'appli")
        plan["keywords"] = []
    for k in ("title", "bigwords", "numbers"):
        if plan.get(k):
            print(f"attention : « {k} » occupe la zone du tableau, à retirer en montage viral")
    json.dump(plan, open(plan_path, "w"), ensure_ascii=False, indent=1)
    print(f"-> {out} · plan.json mis à jour (cam, subY, viral.zone)")


JS_HELPERS = [
    'function TIN(s,t,d){tl.fromTo(s,{opacity:0,y:18,filter:"blur(8px)"},{opacity:1,y:0,filter:"blur(0px)",duration:d||.45,ease:"power3.out",immediateRender:false},t);}',
    'function DRAW(s,t,d){tl.fromTo(s,{strokeDashoffset:1},{strokeDashoffset:0,duration:d||.35,ease:"power2.inOut",autoRound:false,immediateRender:false},t);}',
]
# Zones mortes Instagram (TOUS les montages, choix « zone organique ») : rien de texte ni d'animé au-dessus de
# 270 px (14 %, Meta Ads Guide Reels) ni à moins de 65 px des bords (6 %). Le voile (décor) peut déborder.
TOP, X0, X1 = 270, 65, 1015
SHADOW = "text-shadow:0 3px 18px rgba(0,0,0,.65),0 0 2px rgba(0,0,0,.5)"
COL = {"bad": "#FF453A", "ok": "#F2B33D", "top": "#5AA9FF"}
ICON = {"cross": '<path pathLength="1" d="M9 9L31 31"/><path pathLength="1" d="M31 9L9 31"/>',
        "check": '<path pathLength="1" d="M6 21L16 31L34 9"/>',
        "tilde": '<path pathLength="1" d="M6 22C11 13 16 13 20 20S29 27 34 18"/>',
        "star": '<path pathLength="1" d="M20 4L24.7 14.5L36 15.6L27.4 23.1L30 34.3L20 28.4L10 34.3L12.6 23.1L4 15.6L15.3 14.5Z"/>'}


def common(Z, title, s, e, ttop=None):
    """voile sombre en haut (décor, peut déborder) + titre posé à TOP (MAJUSCULES espacées + serif italique)"""
    ttop = TOP if ttop is None else ttop
    tt = s * 1.25 + (e * 1.05 if title.get("serif") else 0)
    css = f"""
  .tveil{{position:absolute;left:0;right:0;top:0;height:{Z + 250}px;z-index:5;opacity:0;background:linear-gradient(180deg,rgba(5,8,20,.86) 0%,rgba(5,8,20,.74) 60%,rgba(5,8,20,0) 100%)}}
  .tT{{position:absolute;inset:0;z-index:12;pointer-events:none;color:#fff;{SHADOW}}}
  .tT .ttl{{position:absolute;left:{X0}px;right:{1080 - X1}px;top:{ttop:.0f}px;text-align:center;opacity:0}}
  .tT .ttl .s{{display:block;font-family:"Mont";font-weight:800;font-size:{s}px;line-height:1.25;letter-spacing:.2em;text-transform:uppercase}}
  .tT .ttl .e{{display:block;font-family:"Serif";font-style:italic;font-size:{e}px;line-height:1.05}}"""
    body = ['<div class="tveil" id="tveil"></div><div class="tT">',
            f'<div class="ttl" id="tttl"><span class="s">{title["sans"]}</span>'
            + (f'<span class="e">{title["serif"]}</span>' if title.get("serif") else "") + '</div>']
    js = JS_HELPERS + [f'tl.fromTo("#tveil",{{opacity:0}},{{opacity:1,duration:.35,ease:"power2.out",immediateRender:false}},{max(title["at"] - 0.15, 0):.2f});',
                       f'TIN("#tttl",{title["at"]:.2f},.5);']
    return css, body, js, tt


def build_t(spec, Z, SERIF, MONT):
    H = Z - TOP
    s, e, hds, imax = (32, 72, 28, 64) if H >= 400 else (26, 56, 24, 54)
    css, body, js, tt = common(Z, spec["title"], s, e)
    hb = TOP + tt + 16
    hd = hb + 22
    it0 = hd + hds * 1.25 + 24
    mid = 540

    def width(txt, size):
        return max(SERIF.getlength(l) for l in txt.split("<br>")) * size / 100

    cols = {"left": spec["left"]["items"][:2], "right": spec["right"]["items"][:2]}
    nl = max(sum(len(t.split("<br>")) for t, _ in its) for its in cols.values())
    avail = Z - 10 - it0
    its = min([imax, int(avail / (nl * 1.1 + 0.25))] + [int((mid - X0 - 30) / 1.07 / (width(t, 100) / 100)) for c in cols.values() for t, _ in c])
    css += f"""
  .tT .hb{{position:absolute;left:{X0}px;width:{X1 - X0}px;top:{hb:.0f}px;height:5px;border-radius:3px;background:#fff;transform:scaleX(0);transform-origin:50% 50%}}
  .tT .vb{{position:absolute;left:{mid - 2}px;width:5px;top:{hb:.0f}px;height:{Z - hb:.0f}px;border-radius:3px;background:#fff;transform:scaleY(0);transform-origin:50% 0}}
  .tT .col{{position:absolute;top:0;height:100%}}
  .tT .hd{{position:absolute;left:0;right:0;top:{hd:.0f}px;display:flex;align-items:center;justify-content:center;gap:12px;opacity:0;font-family:"Mont";font-weight:800;font-size:{hds}px;letter-spacing:.14em}}
  .tT .hd svg{{width:{int(hds * 1.25)}px;height:{int(hds * 1.25)}px;fill:none;stroke-width:5;stroke-linecap:round;stroke-linejoin:round;overflow:visible}}
  .tT .hd svg path{{stroke-dasharray:1;stroke-dashoffset:1}}
  .tT .it{{position:absolute;left:0;right:0;text-align:center;opacity:0;font-family:"Serif";font-style:italic;font-size:{its}px;line-height:1.1;white-space:nowrap}}
  .tT .strike{{position:absolute;height:5px;border-radius:3px;background:#FF453A;transform:scaleX(0);transform-origin:0 50%}}
"""
    body.append('<div class="hb" id="thb"></div><div class="vb" id="tvb"></div>')
    for side, (a, b) in {"left": (X0, mid), "right": (mid, X1)}.items():
        c = spec[side]
        color = COL["bad"] if c["icon"] == "cross" else COL["top"]
        body.append(f'<div class="col" id="t{side}" style="left:{a}px;width:{b - a}px">')
        body.append(f'<div class="hd" id="t{side}hd"><svg viewBox="0 0 40 40" style="stroke:{color}">{ICON[c["icon"]]}</svg><span>{c["head"]}</span></div>')
        top = it0
        for i, (txt, _) in enumerate(cols[side]):
            body.append(f'<div class="it" id="t{side}{i}" style="top:{top:.0f}px">{txt}</div>')
            if side == "left":  # une barre par ligne
                for li, line in enumerate(txt.split("<br>")):
                    w = width(line, its) + 24
                    body.append(f'<div class="strike t{side}{i}s" style="left:{(b - a - w) / 2:.0f}px;width:{w:.0f}px;top:{top + its * 1.1 * li + its * 0.62:.0f}px"></div>')
            top += len(txt.split("<br>")) * its * 1.1 + its * 0.25
        body.append('</div>')
    js += [f'tl.fromTo("#thb",{{scaleX:0}},{{scaleX:1,duration:.55,ease:"power3.inOut",immediateRender:false}},{spec["bar_at"]:.2f});',
           f'tl.fromTo("#tvb",{{scaleY:0}},{{scaleY:1,duration:.5,ease:"power3.inOut",immediateRender:false}},{spec["bar_at"] + 0.35:.2f});']
    for side in ("left", "right"):
        c = spec[side]
        js.append(f'TIN("#t{side}hd",{c["at"]:.2f},.4);DRAW("#t{side}hd path",{c["at"] + 0.12:.2f},.4);')
        for i, (_, at) in enumerate(cols[side]):
            js.append(f'TIN("#t{side}{i}",{at:.2f});')
    if spec.get("win"):
        w = spec["win"]["at"]
        js.append(f'tl.to("#tleft .it, #tlefthd",{{opacity:.42,duration:.5,ease:"power2.out"}},{w:.2f});')
        for i in range(len(cols["left"])):
            js.append(f'tl.fromTo(".tleft{i}s",{{scaleX:0}},{{scaleX:1,duration:.32,ease:"power3.inOut",stagger:.12,immediateRender:false}},{w + 0.1 + i * 0.14:.2f});')
        js.append(f'tl.to("#tright .it",{{scale:1.07,textShadow:"0 0 26px rgba(90,169,255,.75),0 3px 18px rgba(0,0,0,.5)",duration:.55,ease:"power3.out"}},{w:.2f});')
    return css, body, js, f"T, éléments {its}px, zone {TOP}-{Z}px"


def build_mbe(spec, Z, SERIF, MONT):
    """mauvais / bien / excellent : 3 cartes côte à côte, de gauche à droite, chacune sur son mot (son doigt).
    Carte = pastille couleur + IMAGE (img) ou icône tracée + petit texte serif dessous."""
    H = Z - TOP
    s, e = (30, 62) if H >= 420 else (24, 50)
    css, body, js, tt = common(Z, spec["title"], s, e)
    ctop = TOP + tt + 16
    gap, n = 20, len(spec["cards"])
    x0c, x1c = X0 + 10, X1 - 10                      # la carte gagnante grossit de 3 % : elle doit rester dans la zone sûre
    cw, ch = (x1c - x0c - gap * (n - 1)) / n, Z - ctop
    psz, tsz = (22 if H >= 420 else 18), (30 if H >= 420 else 24)
    has_txt = any(c.get("text") for c in spec["cards"])
    txt_h = tsz * 1.12 * 2 if has_txt else 0
    ih = max(60, min((cw - 24) / 1.25, ch - (psz + 18) - txt_h - 46))   # image : ce qui reste entre pastille et texte
    isz = int(min(cw * .42, ih))
    css += f"""
  .tT .card{{position:absolute;top:{ctop:.0f}px;width:{cw:.0f}px;height:{ch:.0f}px;border-radius:24px;opacity:0;background:rgba(12,16,32,.66);border:2px solid rgba(255,255,255,.14);
    display:flex;flex-direction:column;align-items:center;justify-content:flex-start;padding:14px 12px 12px;box-sizing:border-box;gap:10px;transform-origin:50% 60%}}
  .tT .pill{{font-family:"Mont";font-weight:800;font-size:{psz}px;letter-spacing:.14em;text-transform:uppercase;padding:7px 14px;border-radius:40px;color:#0b0d14;text-shadow:none}}
  .tT .card svg{{width:{isz}px;height:{isz}px;fill:none;stroke-width:3.4;stroke-linecap:round;stroke-linejoin:round;overflow:visible;margin-top:6px}}
  .tT .card svg path{{stroke-dasharray:1;stroke-dashoffset:1}}
  .tT .cimg{{width:{cw - 24:.0f}px;height:{ih:.0f}px;border-radius:14px;object-fit:cover;object-position:50% 0;opacity:0;box-shadow:0 6px 18px rgba(0,0,0,.35)}}
  .tT .ctx{{font-family:"Serif";font-style:italic;font-size:{tsz}px;line-height:1.12;text-align:center;opacity:0}}
"""
    for i, c in enumerate(spec["cards"]):
        col = COL.get(c.get("color", ["bad", "ok", "top"][i % 3]), c.get("color"))
        icon = c.get("icon", ["cross", "tilde", "star"][i % 3])
        vis = (f'<img class="cimg" id="tc{i}i" src="{c["img"]}"/>' if c.get("img")
               else f'<svg viewBox="0 0 40 40" style="stroke:{col}">{ICON[icon]}</svg>')
        body.append(f'<div class="card" id="tc{i}" style="left:{x0c + i * (cw + gap):.0f}px;border-color:{col}66">'
                    f'<span class="pill" style="background:{col}">{c["label"]}</span>{vis}'
                    + (f'<div class="ctx" id="tc{i}t">{c["text"]}</div>' if c.get("text") else "") + '</div>')
        js.append(f'tl.fromTo("#tc{i}",{{opacity:0,y:24,scale:.94,filter:"blur(8px)"}},{{opacity:1,y:0,scale:1,filter:"blur(0px)",duration:.45,ease:"power3.out",immediateRender:false}},{c["at"]:.2f});')
        if c.get("img"):
            js.append(f'tl.fromTo("#tc{i}i",{{opacity:0,scale:1.06}},{{opacity:1,scale:1,duration:.45,ease:"power3.out",immediateRender:false}},{c["at"] + 0.12:.2f});')
        else:
            js.append(f'DRAW("#tc{i} svg path",{c["at"] + 0.18:.2f},.42);')
        if c.get("text"):
            js.append(f'TIN("#tc{i}t",{c.get("text_at", c["at"] + 0.3):.2f},.4);')
    if spec.get("win"):
        w, k = spec["win"]["at"], spec["win"].get("card", n - 1)
        others = ",".join(f"#tc{i}" for i in range(n) if i != k)
        col = COL.get(spec["cards"][k].get("color", ["bad", "ok", "top"][k % 3]), "#5AA9FF")
        js.append(f'tl.to("{others}",{{opacity:.45,duration:.5,ease:"power2.out"}},{w:.2f});')
        js.append(f'tl.to("#tc{k}",{{scale:1.03,boxShadow:"0 0 40px {col}aa",borderColor:"{col}",duration:.55,ease:"power3.out"}},{w:.2f});')
    return css, body, js, f"{n} cartes {cw:.0f}x{ch:.0f}px, {'images' if any(c.get('img') for c in spec['cards']) else 'icônes'} {ih:.0f}px, zone {TOP}-{Z}px"


def build_tier(spec, Z, SERIF, MONT):
    """tier list : rangées S..D ; chaque élément grossit au CENTRE quand il est nommé (at), puis file dans sa rangée sur la
    LETTRE (land) (animation GSAP, sans rebond). Élément = icône (img, fond transparent) + nom DANS la tuile (label, police de la DA :
    des logos ou petites images plutôt que du texte seul, le texte dans l'icône) ; emoji possible ; texte seul seulement en secours (pastille)."""
    Z = min(Z, 900)
    rows = spec.get("rows", ["S", "A", "B", "C", "D"])
    RC = spec.get("colors", {"S": "#E5534B", "A": "#F08C3A", "B": "#E8C547", "C": "#6DBE6A", "D": "#4F9BFF", "F": "#8E8E93"})
    H = Z - TOP
    items = spec["items"]
    hide = spec.get("title_hide", True)   # le titre est dit à voix haute -> grand au début, puis place au tableau
    if hide:
        s, e = (34, 76) if H >= 400 else (28, 60)
        tt0 = s * 1.25 + e * 1.05
        css, body, js, tt = common(Z, spec["title"], s, e, TOP + (H - tt0) / 2)
        t_out = max(spec["title"]["at"] + 0.8, min(it["at"] for it in items) - 0.3)
        js.append(f'tl.to("#tttl",{{opacity:0,y:-12,filter:"blur(6px)",duration:.3,ease:"power2.in"}},{t_out - 0.3:.2f});')
        rtop, rgap, r0 = TOP + 4, 6, t_out
    else:
        s, e = (26, 48) if H >= 400 else (22, 40)
        css, body, js, tt = common(Z, spec["title"], s, e)
        rtop, rgap, r0 = TOP + tt + 12, 6, spec["title"]["at"] + 0.35
    rowh = (Z - rtop - rgap * (len(rows) - 1)) / len(rows)
    lx = X0 + rowh + 8
    inner = X1 - lx - 12
    visual = all(it.get("img") or it.get("emoji") for it in items)
    pos = {}
    if visual:   # vignettes carrées, 1 ligne par rangée si possible, sinon 2
        per = {r: [k for k, it in enumerate(items) if it["to"] == r] for r in rows}
        mx = max(len(v) for v in per.values())
        th = rowh - 10
        if mx * (th + 6) > inner:
            th = min((rowh - 14) / 2, inner / ((mx + 1) // 2) - 6)
        cols_per_line = max(1, int((inner + 6) // (th + 6)))
        for r, ks in per.items():
            ry = rtop + rows.index(r) * (rowh + rgap)
            nlines = (len(ks) + cols_per_line - 1) // cols_per_line or 1
            tot = nlines * th + (nlines - 1) * 4
            for j, k in enumerate(ks):
                li, ci = divmod(j, cols_per_line)
                pos[k] = (lx + 6 + ci * (th + 6), ry + (rowh - tot) / 2 + li * (th + 4), th, th)
        big = min(220, H * .5) / th      # taille au centre (220 px : on lit le nom dans la tuile)
        info = f"vignettes {th:.0f}px"
    else:        # secours : pastilles texte, taille commune, 2 lignes max par rangée
        def place(fs):
            chh, padx, g = fs + 16, 13, 7
            out, ok = {}, True
            for r in rows:
                mine = [k for k, it in enumerate(items) if it["to"] == r]
                lines, x = [[]], 0
                for k in mine:
                    w = MONT.getlength(items[k]["text"]) * fs / 100 + 2 * padx
                    if x and x + w > inner:
                        lines.append([]); x = 0
                    lines[-1].append((k, x, w)); x += w + g
                if len(lines) > 2 or 2 * chh + 6 > rowh - 6:
                    ok = False
                ry = rtop + rows.index(r) * (rowh + rgap)
                tot = len(lines) * chh + (len(lines) - 1) * 6
                for li, ln in enumerate(lines):
                    for k, xx, w in ln:
                        out[k] = (lx + 6 + xx, ry + (rowh - tot) / 2 + li * (chh + 6), w, chh)
            return ok, out
        fs = 34
        while fs > 14:
            ok, pos = place(fs)
            if ok:
                break
            fs -= 1
        big, info = 1.7, f"pastilles texte {fs}px"
        css += f"""
  .tT .chip{{font-family:"Mont";font-weight:700;font-size:{fs}px;line-height:{fs + 16}px;padding:0 13px;white-space:nowrap}}"""
    css += f"""
  .tT .tile{{position:absolute;left:{X0}px;width:{rowh:.0f}px;height:{rowh:.0f}px;border-radius:14px;opacity:0;display:flex;align-items:center;justify-content:center;
    font-family:"Mont";font-weight:800;font-size:{int(rowh * .52)}px;color:#0b0d14;text-shadow:none}}
  .tT .band{{position:absolute;left:{lx:.0f}px;width:{X1 - lx:.0f}px;height:{rowh:.0f}px;border-radius:14px;opacity:0;background:rgba(255,255,255,.08);border:1.5px solid rgba(255,255,255,.12);box-sizing:border-box}}
  .tT .tk{{position:absolute;opacity:0;box-sizing:border-box;border-radius:12px;background:linear-gradient(160deg,#2B3A66,#1C2747);border:1.5px solid rgba(255,255,255,.24);
    transform-origin:50% 50%;box-shadow:0 8px 24px rgba(0,0,0,.35);text-shadow:none;overflow:hidden;display:flex;align-items:center;justify-content:center}}
  .tT .tk img{{position:absolute;object-fit:contain}}
  .tT .tk .tl{{position:absolute;left:4%;right:4%;text-align:center;font-family:"Mont";font-weight:700;color:#fff;line-height:1.02;white-space:nowrap}}
"""
    for i, r in enumerate(rows):
        ry = rtop + i * (rowh + rgap)
        body.append(f'<div class="tile" id="tr{i}" style="top:{ry:.0f}px;background:{RC.get(r, "#8E8E93")}">{r}</div>'
                    f'<div class="band" id="tb{i}" style="top:{ry:.0f}px"></div>')
        js.append(f'tl.fromTo("#tr{i},#tb{i}",{{opacity:0,x:24}},{{opacity:1,x:0,duration:.4,ease:"power3.out",immediateRender:false}},{r0 + i * 0.07:.2f});')
    cx, cy = 540, rtop + (Z - rtop) / 2
    for k, it in enumerate(items):
        x, y, w, h = pos[k]
        if it.get("img") and it.get("label"):   # icône + nom DANS la tuile, en Montserrat (cohérence DA)
            words = it["label"].replace("-", "- ").split()
            lines = [it["label"]]
            if len(it["label"]) > 11 and len(words) > 1:   # 2 lignes équilibrées
                cut = min(range(1, len(words)), key=lambda c: abs(len(" ".join(words[:c])) - len(" ".join(words[c:]))))
                lines = [" ".join(words[:cut]), " ".join(words[cut:])]
            lw = max(MONT.getlength(l) for l in lines) / 100
            lfs = min(w * .15, w * .9 / lw, w * .26 / (len(lines) * 1.05))
            inner_html = (f'<img src="{it["img"]}" style="left:{w * .14:.1f}px;top:{h * .03:.1f}px;width:{w * .72:.1f}px;height:{h * (.72 if len(lines) == 1 else .64):.1f}px"/>'
                          f'<span class="tl" style="font-size:{lfs:.2f}px;bottom:{h * .05:.1f}px">{"<br>".join(lines).replace("- ", "-")}</span>')
            extra = ""
        elif it.get("img"):
            inner_html, extra = f'<img src="{it["img"]}" style="left:0;top:0;width:100%;height:100%;object-fit:cover"/>', ""
        elif it.get("emoji"):
            inner_html, extra = it["emoji"], f'font-size:{h * .64:.0f}px;line-height:1;'
        else:
            inner_html, extra = it["text"], ""
        cls = "tk" if visual else "tk chip"
        body.append(f'<div class="{cls}" id="tk{k}" style="left:{x:.0f}px;top:{y:.0f}px;width:{w:.0f}px;height:{h:.0f}px;{extra}">{inner_html}</div>')
        dx, dy = cx - (x + w / 2), cy - (y + h / 2)
        at, fly = it["at"], max(it["land"], it["at"] + 0.35)
        # x/y aussi dans le « to » du 1er tween : sinon GSAP ne les pose pas (bug : l'élément grossissait dans sa case)
        js.append(f'tl.fromTo("#tk{k}",{{opacity:0,x:{dx:.0f},y:{dy:.0f},scale:{big * .75:.2f},filter:"blur(8px)"}},{{opacity:1,x:{dx:.0f},y:{dy:.0f},scale:{big:.2f},filter:"blur(0px)",duration:.3,ease:"power3.out",immediateRender:false}},{at:.2f});')
        js.append(f'tl.fromTo("#tk{k}",{{x:{dx:.0f},y:{dy:.0f},scale:{big:.2f}}},{{x:0,y:0,scale:1,duration:.42,ease:"power3.inOut",immediateRender:false}},{fly:.2f});')
        ri = rows.index(it["to"])
        js.append(f'tl.fromTo("#tr{ri}",{{filter:"brightness(1.45)"}},{{filter:"brightness(1)",duration:.45,ease:"power2.out",immediateRender:false}},{fly + 0.38:.2f});')
    return css, body, js, f"{len(rows)} rangées de {rowh:.0f}px, {len(items)} éléments, {info}, zone {TOP}-{Z}px"


def inject(plan_path):
    from PIL import ImageFont
    plan = json.load(open(plan_path))
    v = plan["viral"]
    Z = v.get("zone", 690)
    if Z - TOP < 300:
        print(f"ATTENTION : seulement {Z - TOP}px entre la zone morte du haut ({TOP}px) et la tête : tableau très serré. "
              "Au tournage : cadrer plus large (visage plus petit, tête plus bas).")
    kinds = [k for k in ("t", "mbe", "tier") if k in v]
    if len(kinds) != 1:
        sys.exit("plan.viral doit contenir UN tableau : t, mbe ou tier")
    html = open("index.html", encoding="utf8").read()
    if MARK in html:
        sys.exit("le tableau est déjà dans index.html : relancer build.mjs d'abord")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import reglages
    DAF = {**reglages.da()["fonts"], **plan.get("fonts", {})}   # mêmes polices que build.mjs (DA de l'utilisateur)
    SERIF = ImageFont.truetype(os.path.join("fonts", DAF["serif"]), 100)
    MONT = ImageFont.truetype(os.path.join("fonts", DAF["sans"]), 100)
    try:
        MONT.set_variation_by_axes([700])
    except Exception:
        pass
    css, body, js, info = {"t": build_t, "mbe": build_mbe, "tier": build_tier}[kinds[0]](v[kinds[0]], Z, SERIF, MONT)
    body.append("</div>")
    html = html.replace("</style>", css + "\n</style>", 1)
    i = html.rindex("  </div>\n  <script>")
    html = html[:i] + "    " + "".join(body) + "\n" + html[i:]
    anchor = "    tl.to({},{duration:DUR},0);"
    if anchor not in html:
        sys.exit("ancre de la timeline introuvable dans index.html (build.mjs a changé ?)")
    html = html.replace(anchor, "    " + "\n    ".join(js) + "\n" + anchor, 1)
    open("index.html", "w", encoding="utf8").write(html)
    print(f"tableau « {kinds[0]} » posé dans index.html ({info})")


if __name__ == "__main__":
    {"layout": layout, "inject": inject}[sys.argv[1]](sys.argv[2])
