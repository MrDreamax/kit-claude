#!/usr/bin/env python3
"""Style Lab : tu choisis TA DA de montage en UN tour, sur TA rush.
5 sections, 1 seule variable par carte : DA visuelle (4 images avec ton visage, facultatif : demande un compte Higgsfield), polices (4),
couleur (4), musique (1 à 4, à l'oreille), rythme (posé / nerveux). Tu votes Garder / Peut-être / Jeter dans la page Style Lab,
puis `lock` écrit ta DA de montage dans ~/Documents/Brain/00-Moi/montage.json (bloc "da").

  python3 round.py build --clip clip.mp4 --words words.json --start 0 --end 10 --keyword rassurant \\
      --card "*en revanche|gagner en|*crédibilité" --card-at 3.07 --card-end 6.15 \\
      [--music m1.wav m2.wav m3.wav m4.wav --music-labels "Motivation|Dark cinématique|Espoir|Émotion piano"] \\
      [--da-images d1.png d2.png d3.png d4.png --da-labels "..."] [--brand "#E4572E"] [--fixes '{"a": "b"}'] --out style-lab
     clip/words = la rush APRÈS les étapes 1-3 de SKILL.md ; passage de 8-12 s qui finit sur une phrase entière ;
     keyword = 1 mot fort dit dans le passage ; card = 1 punchline dite dans le passage (« * » = ligne en serif).
     -> style-lab/round.json + un dossier par carte (full.mp4 avec le son, preview.mp4 muet < 2 Mo, ou image)
  python3 round.py db --round style-lab/round.json --assets assets.json [--handle pseudo]
     assets.json = {"chemin du fichier": "id de l'asset"} (résultat de l'upload) -> style-lab/db/*.json + la liste `writes` à passer à UN ArtifactData batch
  python3 round.py lock --round style-lab/round.json --vote vote.json [--out chemin.json]
     vote.json = la soumission de la page (ArtifactData get submissions/<id>) ou la liste de la collection notes.
     -> ~/Documents/Brain/00-Moi/montage.json (bloc "da" mis à jour, le reste du fichier est gardé). Code 3 = une section a 0 ou plusieurs « Garder » : la trancher en QCM dans le chat, puis
        relancer avec --pick section=carte.
"""
import argparse, colorsys, concurrent.futures as cf, glob, json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(os.path.dirname(HERE))
S = os.path.join(SKILL, "scripts")
ENV = dict(os.environ, PATH=os.path.expanduser("~/.local/bin") + ":" + os.path.expanduser("~/.local/node/bin") + ":/opt/homebrew/bin:/usr/local/bin:" + os.environ.get("PATH", ""))
sys.path.insert(0, S)
import reglages
HF = ["npx", "--yes", "hyperframes@0.6.81"]
SCALES = json.load(open(os.path.join(SKILL, "fonts", "scales.json")))
# police étroite = sous-titres qui paraissent petits à 52 px : on compense la taille (mesuré sur une planche)
SCALES = {**SCALES, "BebasNeue-Regular.ttf": 1.35}

# 4 couples de polices libres (OFL), le 1er = le choix par défaut du skill (Montserrat + Instrument Serif)
FONTS = [("Montserrat.ttf", "InstrumentSerif-Italic.ttf", "Montserrat + Instrument Serif", "Sobre et premium, le choix par défaut."),
         ("Poppins-SemiBold.ttf", "PlayfairDisplay-Italic.ttf", "Poppins + Playfair", "Rond et chaleureux, serif élégante."),
         ("Inter.ttf", "DMSerifDisplay-Italic.ttf", "Inter + DM Serif", "Net et moderne, serif qui claque."),
         ("BebasNeue-Regular.ttf", "BodoniModa-Italic.ttf", "Bebas + Bodoni", "Haut et serré, look magazine.")]
DA_LABELS = ["Premium sombre", "Cinéma chaud", "Clair épuré", "Énergique coloré"]
RYTHME = [("pose", [5, 8], "Posé", "Zoom lent quand l'idée change. Élégant, on écoute."),
          ("nerveux", [2.5, 4], "Nerveux", "Zoom lent à chaque phrase. Plus de mouvement, toujours sans à-coup.")]


def sh(cmd, cwd=None, quiet=True):
    r = subprocess.run(cmd, cwd=cwd, env=ENV, capture_output=quiet, text=True)
    if r.returncode:
        sys.exit(f"!! échec : {' '.join(map(str, cmd))[:200]}\n{(r.stderr or '')[-1500:]}")
    return r.stdout


# ---------- couleurs ----------
def hx(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h % 1, max(0, min(1, s)), max(0, min(1, v)))
    return "#%02X%02X%02X" % (round(r * 255), round(g * 255), round(b * 255))


def hsv_of(c):
    c = c.lstrip("#")
    return colorsys.rgb_to_hsv(*(int(c[i:i + 2], 16) / 255 for i in (0, 2, 4)))


def hue_name(h, s):
    if s < 0.15: return "noir et blanc"
    d = h * 360
    for lim, n in ((15, "rouge"), (40, "orange"), (65, "jaune"), (160, "vert"), (195, "turquoise"), (255, "bleu"), (290, "violet"), (335, "rose"), (361, "rouge")):
        if d < lim: return n


def palette(c):
    """Couleur d'accent -> dégradé des cartons (plan.colors.grad : haut gauche sombre, haut droite vif, bas gauche, bas droite clair, fond)
    + fond des cartons liste. Même recette que build.mjs gradFromAccent."""
    h, s, v = hsv_of(c)
    if s < 0.15:
        return {"accent": "#FFFFFF", "grad": ["#0A0A0A", "#D9D9D9", "#3A3A3A", "#F2F2F2", "#1A1A1A"], "list": ["#2A2A2A", "#161616", "#0B0B0D"]}
    s = max(s, 0.6)
    return {"accent": hx(h, s, 0.95), "grad": [hx(h, s * .9, .11), hx(h, s, .95), hx(h, s * .85, .40), hx(h, s * .35, .94), hx(h, s * .8, .33)],
            "list": [hx(h, s * .6, .18), hx(h, s * .6, .12), "#0B0B0D"]}


def rush_colors(clip, a, b):
    """Les 2 teintes saturées qui dominent la rush (décor, lumière), peau écartée. Univers = la RUSH."""
    from PIL import Image
    tmp = tempfile.mkdtemp()
    sh(["ffmpeg", "-v", "error", "-ss", str(a), "-to", str(b), "-i", clip, "-vf", "fps=0.8,scale=160:-1", os.path.join(tmp, "f%02d.png")])
    bins = {}
    for f in glob.glob(os.path.join(tmp, "*.png")):
        for r, g, bb in Image.open(f).convert("RGB").getdata():
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, bb / 255)
            if s < 0.35 or v < 0.18: continue
            if h < 0.13 and s < 0.7: continue          # peau
            k = int(h * 24)
            w, hs = bins.get(k, (0, 0))
            bins[k] = (w + s * v, hs + h * s * v)
    shutil.rmtree(tmp, ignore_errors=True)
    out = []
    for k, (w, hs) in sorted(bins.items(), key=lambda kv: -kv[1][0]):
        h = hs / w
        if all(min(abs(h - o), 1 - abs(h - o)) > 0.09 for o in out): out.append(h)
        if len(out) == 2: break
    return [hx(h, 0.8, 0.95) for h in out]


# ---------- une carte = un dossier ----------
def base_da(nom, fonts, colors, zoomgap):
    sans, serif = fonts
    return {"nom": nom, "fonts": {"sans": sans, "serif": serif, "sub": sans}, "subSize": round(52 * SCALES.get(sans, 1)),
            "colors": {"text": "#FFFFFF", "halo": "0,0,0", "glow": "0,0,0", **colors}, "zoomGap": zoomgap}


def make(out, name, cfg, da, music):
    d = os.path.join(out, name)
    os.makedirs(d, exist_ok=True)
    for f in ("clip.mp4", "words.json"):
        p = os.path.join(d, f)
        if not os.path.exists(p):
            try: os.link(os.path.join(out, "_base", f), p)
            except OSError: shutil.copy(os.path.join(out, "_base", f), p)
    json.dump(da, open(os.path.join(d, "da.json"), "w"), ensure_ascii=False, indent=1)
    plan = {"cam": "clip.mp4", "words": "words.json", "da": "da.json", "fixes": cfg["fixes"], "keywords": [cfg["keyword"]],
            "mini": [cfg["card"]]}
    if music: plan["music"] = music
    json.dump(plan, open(os.path.join(d, "plan.json"), "w"), ensure_ascii=False, indent=1)
    return d


def render(d):
    """Rendu HyperFrames, réutilisé seulement si plan.json et da.json n'ont pas bougé depuis (clé dans renders/.key)."""
    import hashlib
    key = hashlib.sha1(b"".join(open(os.path.join(d, f), "rb").read() for f in ("plan.json", "da.json"))).hexdigest()
    kf = os.path.join(d, "renders", ".key")
    if glob.glob(os.path.join(d, "renders", "*.mp4")) and os.path.exists(kf) and open(kf).read() == key:
        return d
    shutil.rmtree(os.path.join(d, "renders"), ignore_errors=True)
    sh(["node", os.path.join(S, "build.mjs"), "--plan", "plan.json", "--out", "index.html"], cwd=d)
    sh(HF + ["render", ".", "-q", "high"], cwd=d)
    open(kf, "w").write(key)
    return d


def finish(d, src_dir=None):
    """mix.py (voix -14 + musique + SFX) -> full.mp4, puis preview.mp4 muet léger pour la page."""
    v = sorted(glob.glob(os.path.join(src_dir or d, "renders", "*.mp4")), key=os.path.getmtime)[-1]
    sh(["python3", os.path.join(S, "mix.py"), os.path.join(d, "plan.json"), v, os.path.join(d, "clip.mp4"), os.path.join(d, "full.mp4")])
    sh(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(d, "full.mp4"), "-an", "-vf", "scale=360:640:flags=lanczos,fps=30",
        "-c:v", "libx264", "-crf", "30", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", os.path.join(d, "preview.mp4")])
    return d


def build(a):
    out = os.path.abspath(a.out)
    os.makedirs(os.path.join(out, "_base"), exist_ok=True)
    # passage choisi : vidéo coupée + transcription recalée à 0
    sh(["ffmpeg", "-v", "error", "-y", "-ss", str(a.start), "-to", str(a.end), "-i", a.clip, "-c:v", "libx264", "-crf", "16", "-preset", "medium",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", os.path.join(out, "_base", "clip.mp4")])
    W = json.load(open(a.words))["words"]
    W = [{**w, "start": round(w["start"] - a.start, 3), "end": round(w["end"] - a.start, 3)} for w in W if w["start"] >= a.start - 0.01 and w["end"] <= a.end + 0.01]
    json.dump({"words": W}, open(os.path.join(out, "_base", "words.json"), "w"), ensure_ascii=False)
    lines = []
    for i, t in enumerate(a.card.split("|")):
        serif = t.startswith("*")
        ln = {"text": t.lstrip("*"), "font": "serif" if serif else "sans"}
        if serif and i == len(a.card.split("|")) - 1: ln["size"] = 190
        lines.append(ln)
    cfg = {"fixes": json.loads(a.fixes or "{}"), "keyword": a.keyword,
           "card": {"type": "card", "start": round(a.card_at - a.start, 3), "end": round(a.card_end - a.start, 3), "bg": "grad", "lines": lines}}
    labels = (a.music_labels or "").split("|")
    froms = a.music_from or [0] * len(a.music)
    MUS = [{"src": os.path.abspath(m), "from": float(f)} for m, f in zip(a.music, froms)]
    MUS0 = MUS[0] if MUS else None   # sans musique : les cartes se jugent sans son

    # couleurs : 2 de SA rush + sa marque (ou noir et blanc) + un bleu sobre, sans doublon de teinte
    rc = [(c, f"De ta rush ({hue_name(*hsv_of(c)[:2])})", "Tirée du décor et de la lumière de ta vidéo.") for c in rush_colors(a.clip, a.start, a.end)]
    brand = (a.brand, f"Ta marque ({a.brand})", "La couleur de ta marque.") if a.brand else ("#FFFFFF", "Noir et blanc", "Aucune couleur : blanc sur noir, très sobre.")
    cols = rc[:1] + [brand] + rc[1:] + [("#2F74FF", "Bleu nuit", "Un bleu sobre et premium.")]   # la marque passe avant la 2e teinte de la rush
    seen, COLS = [], []
    for c, lab, desc in cols:
        h, s, _ = hsv_of(c)
        if any(min(abs(h - o), 1 - abs(h - o)) < 0.07 and s >= 0.15 and so >= 0.15 for o, so in seen): continue
        seen.append((h, s)); COLS.append((c, lab, desc))
    for c, lab, desc in [("#C2A36B", "Or champagne", "Chaud et haut de gamme."), ("#FFFFFF", "Noir et blanc", "Aucune couleur : blanc sur noir, très sobre.")]:
        if len(COLS) < 4 and all(lab != x[1] for x in COLS): COLS.append((c, lab, desc))
    COLS = COLS[:4]
    P0, F0, R0 = palette(COLS[0][0]), FONTS[0][:2], RYTHME[0][1]

    cards, jobs = [], set()
    def card(cid, sec, label, desc, d, meta, sound=False, img=None):
        cards.append({"id": cid, "section": sec, "label": label, "desc": desc, "kind": "image" if img else "video",
                      "file_full": img or os.path.join(d, "full.mp4"), "file_preview": img or os.path.join(d, "preview.mp4"), "sound": sound, "meta": meta})

    # 1. DA visuelle (images Higgsfield faites avant, avec son visage)
    for i, im in enumerate(a.da_images or []):
        lab = (a.da_labels.split("|") if a.da_labels else DA_LABELS)[i]
        dst = os.path.join(out, f"da-{i + 1}" + os.path.splitext(im)[1]); shutil.copy(im, dst)
        card(f"da-{'abcd'[i]}", "da", lab, "Toi, dans cette ambiance. Elle guide les visuels générés et le décor des cartons.", None,
             {"ambiance": lab, "image_ref": dst}, img=dst)
    # base = polices par défaut + 1re couleur + posé + 1re musique : sert aux polices A, couleur A, musique A, rythme posé
    base = make(out, "base", cfg, base_da(a.nom, F0, P0, R0), MUS0)
    jobs.add(base)
    for i, (sans, serif, lab, desc) in enumerate(FONTS):
        d = base if i == 0 else make(out, f"police-{'abcd'[i]}", cfg, base_da(a.nom, (sans, serif), P0, R0), MUS0)
        jobs.add(d)
        card(f"police-{'abcd'[i]}", "polices", lab, desc, d, {"fonts": {"sans": sans, "serif": serif, "sub": sans}, "subSize": round(52 * SCALES.get(sans, 1))})
    for i, (c, lab, desc) in enumerate(COLS):
        d = base if i == 0 else make(out, f"couleur-{'abcd'[i]}", cfg, base_da(a.nom, F0, palette(c), R0), MUS0)
        jobs.add(d)
        card(f"couleur-{'abcd'[i]}", "couleur", lab, desc + " Regarde le carton.", d, {"colors": {"text": "#FFFFFF", "halo": "0,0,0", "glow": "0,0,0", **palette(c)}})
    music_dirs = []
    for i, m in enumerate(MUS):
        d = base if i == 0 else make(out, f"musique-{'abcd'[i]}", cfg, base_da(a.nom, F0, P0, R0), m)
        music_dirs.append(d)
        lab = labels[i] if i < len(labels) and labels[i] else f"Musique {'ABCD'[i]}"
        card(f"musique-{'abcd'[i]}", "musique", lab, f"Touche la carte pour l'écouter : {os.path.splitext(os.path.basename(m['src']))[0]}.", d,
             {"music": [lab], "music_ref": os.path.basename(m["src"])}, sound=True)
    for i, (k, zg, lab, desc) in enumerate(RYTHME):
        d = base if i == 0 else make(out, "rythme-nerveux", cfg, base_da(a.nom, F0, P0, zg), MUS0)
        jobs.add(d)
        card(f"rythme-{k}", "rythme", lab, desc, d, {"rythme": "posé premium" if k == "pose" else "dynamique", "zoomGap": zg})

    print(f"rendu de {len(jobs)} variantes (3 en parallèle)…", flush=True)
    with cf.ThreadPoolExecutor(3) as ex: list(ex.map(render, sorted(jobs)))
    todo = sorted(jobs) + [d for d in music_dirs if d not in jobs]
    with cf.ThreadPoolExecutor(3) as ex: list(ex.map(lambda d: finish(d, None if d in jobs else base), todo))

    sections = [{"id": "da", "name": "Ton ambiance", "use": "4 ambiances avec ton visage. Garde celle qui te ressemble (une seule).", "order": 1},
                {"id": "polices", "name": "Tes polices", "use": "Même vidéo, seules les polices changent : sous-titres + mot fort en italique + carton.", "order": 2},
                {"id": "couleur", "name": "Ta couleur", "use": "Même vidéo, seule la couleur du carton change.", "order": 3},
                {"id": "musique", "name": "Ta musique", "use": "Même vidéo, seule la musique change. Ouvre chaque carte pour l'écouter avec le son.", "order": 4},
                {"id": "rythme", "name": "Ton rythme", "use": "Posé ou nerveux : la façon dont la caméra bouge.", "order": 5}]
    sections = [s for s in sections if any(c["section"] == s["id"] for c in cards)]
    for i, c in enumerate(cards): c["order"] = i + 1
    rnd = {"title": "Ton style de montage", "round": "1", "aspect": "9:16",
           "intro": "Une seule chose change par carte. Mets « Garder » sur UNE carte par section (Peut-être si tu hésites), une note si besoin, puis « Envoyer mon avis ».",
           "notes": ["Une carte gardée par section = ton style est verrouillé.", "Le reste (sous-titres au niveau du col, zones Insta, musique émotionnelle) est déjà réglé par le skill."]}
    json.dump({"round": rnd, "sections": sections, "cards": cards, "nom": a.nom}, open(os.path.join(out, "round.json"), "w"), ensure_ascii=False, indent=1)
    for c in cards:
        for k in ("file_full", "file_preview"):
            if not os.path.exists(c[k]): sys.exit(f"!! fichier manquant : {c[k]}")
    # planches (contrôle avant publication + plan B en QCM) : 1 vignette par carte, carton complet (juste avant sa fin), lettre A-D
    t_mid = cfg["card"]["end"] - 0.35
    fnt = os.path.join(SKILL, "fonts", "Montserrat.ttf")
    for s in sections:
        thumbs = []
        for j, c in enumerate(cc for cc in cards if cc["section"] == s["id"]):
            t = os.path.join(out, f"_thumb-{c['id']}.jpg")
            pre = [] if c["kind"] == "image" else ["-ss", f"{t_mid:.2f}"]
            sh(["ffmpeg", "-v", "error", "-y", *pre, "-i", c["file_full"], "-frames:v", "1", "-vf",
                f"scale=360:640:force_original_aspect_ratio=increase,crop=360:640,drawtext=fontfile={fnt}:text={'ABCD'[j]}:x=16:y=16:fontsize=44:fontcolor=white:box=1:boxcolor=black@0.6:boxborderw=8", t])
            thumbs.append(t)
        ins = sum((["-i", t] for t in thumbs), [])
        sh(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", f"hstack={len(thumbs)}" if len(thumbs) > 1 else "null", "-frames:v", "1", os.path.join(out, f"planche-{s['id']}.jpg")])
        for t in thumbs: os.remove(t)
    big = [c["id"] for c in cards if os.path.getsize(c["file_full"]) > 15e6]
    print(f"OK {len(cards)} cartes, {len(sections)} sections -> {os.path.join(out, 'round.json')}" + (f" ; > 15 Mo : {big}" if big else ""))


# ---------- verrouillage ----------
def lock(a):
    R = json.load(open(a.round))
    V = json.load(open(a.vote)) if a.vote else {"notes": {}}
    if isinstance(V, dict) and "data" in V: V = V["data"]
    if isinstance(V, dict) and "notes" in V: votes = {k: v for k, v in V["notes"].items()}
    else: votes = {d.get("card") or d.get("id"): d for d in (V if isinstance(V, list) else V.get("docs", V.get("items", [])))}
    picks = dict(p.split("=", 1) for p in (a.pick or []))
    chosen, doubt = {}, {}
    for s in R["sections"]:
        cs = [c for c in R["cards"] if c["section"] == s["id"]]
        if s["id"] in picks:
            chosen[s["id"]] = next(c for c in cs if c["id"] == picks[s["id"]]); continue
        keep = [c for c in cs if (votes.get(c["id"]) or {}).get("v") == "keep"]
        maybe = [c for c in cs if (votes.get(c["id"]) or {}).get("v") == "maybe"]
        pool = keep or maybe
        if len(pool) == 1: chosen[s["id"]] = pool[0]
        else: doubt[s["id"]] = [c["id"] + " (" + c["label"] + ")" for c in (pool or cs)]
    for cid, x in votes.items():
        if (x.get("note") or "").strip(): print(f"note {cid} : {x['note'].strip()}")
    if isinstance(V, dict) and (V.get("overall") or "").strip(): print(f"avis global : {V['overall'].strip()}")
    if doubt:
        for s, opts in doubt.items(): print(f"À TRANCHER {s} : {' / '.join(opts)}")
        print("-> poser la question en QCM, puis relancer avec --pick section=carte")
        sys.exit(3)
    out = a.out or str(reglages.MONTAGE)
    perso = json.load(open(out)) if os.path.exists(out) else {}
    da = perso.get("da", {})
    base = reglages.da()
    da.setdefault("broll", {"prompt_higgsfield": base["broll"]["prompt_higgsfield"]})
    m = {k: c["meta"] for k, c in chosen.items()}
    if "da" in m:
        da["ambiance"] = m["da"]["ambiance"]
        ref = os.path.expanduser("~/Documents/Contenu/medias/photos/ambiance-montage" + os.path.splitext(m["da"]["image_ref"])[1])
        os.makedirs(os.path.dirname(ref), exist_ok=True)
        shutil.copy(m["da"]["image_ref"], ref)
        da["image_ref"] = ref
        da["broll"]["prompt_higgsfield"] = da["broll"]["prompt_higgsfield"].replace("photorealistic", f"photorealistic, mood: {m['da']['ambiance']}", 1)
    if "polices" in m: da["fonts"] = m["polices"]["fonts"]; da["subSize"] = m["polices"]["subSize"]
    if "couleur" in m: da["colors"] = m["couleur"]["colors"]
    if "musique" in m: da["music"] = m["musique"]["music"]; da["_music_ref"] = m["musique"]["music_ref"]
    if "rythme" in m: da["rythme"] = m["rythme"]["rythme"]; da["zoomGap"] = m["rythme"]["zoomGap"]
    da["_style_lab"] = "Style Lab du " + __import__("datetime").date.today().strftime("%d/%m/%Y") + " : " + " ; ".join(f"{k} = {c['label']}" for k, c in chosen.items())
    perso["da"] = da
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    json.dump(perso, open(out, "w"), ensure_ascii=False, indent=2)
    print(f"OK {out}\n{da['_style_lab']}")


def dbfiles(a):
    """round.json + ids des assets uploadés -> 1 fichier JSON par document + la liste `writes` pour UN ArtifactData batch."""
    R = json.load(open(a.round))
    A = json.load(open(a.assets))
    A = {os.path.abspath(k): v for k, v in A.items()}
    out = os.path.join(os.path.dirname(os.path.abspath(a.round)), "db")
    os.makedirs(out, exist_ok=True)
    docs = [("round", "current", R["round"])]
    docs += [("sections", s["id"], {k: v for k, v in s.items() if k != "id"}) for s in R["sections"]]
    for c in R["cards"]:
        miss = [c[k] for k in ("file_preview", "file_full") if os.path.abspath(c[k]) not in A]
        if miss: sys.exit(f"!! pas d'id d'asset pour : {miss}")
        docs.append(("cards", c["id"], {"section": c["section"], "label": c["label"], "desc": c["desc"], "kind": c["kind"], "order": c["order"],
                                        "preview": A[os.path.abspath(c["file_preview"])], "full": A[os.path.abspath(c["file_full"])], "sound": c["sound"]}))
    if a.handle: docs.append(("profile", "current", {"handle": a.handle.lstrip("@"), "name": ""}))
    writes = []
    for col, did, data in docs:
        f = os.path.join(out, f"{col}-{did}.json")
        json.dump(data, open(f, "w"), ensure_ascii=False)
        writes.append({"op": "set", "collection": col, "doc_id": did, "file_path": f})
    if len(writes) > 50: sys.exit("!! plus de 50 documents : faire 2 batchs")
    print(json.dumps(writes, ensure_ascii=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    b = sp.add_parser("build")
    for k in ("--clip", "--words", "--keyword", "--card", "--out"): b.add_argument(k, required=True)
    for k in ("--start", "--end", "--card-at", "--card-end"): b.add_argument(k, type=float, required=True)
    b.add_argument("--music", nargs="*", default=[]); b.add_argument("--music-labels"); b.add_argument("--music-from", nargs="*", type=float)
    b.add_argument("--da-images", nargs="*"); b.add_argument("--da-labels"); b.add_argument("--brand"); b.add_argument("--fixes")
    b.add_argument("--nom", default="toi")
    l = sp.add_parser("lock")
    l.add_argument("--round", required=True); l.add_argument("--vote")
    l.add_argument("--out"); l.add_argument("--pick", nargs="*")
    d = sp.add_parser("db")
    d.add_argument("--round", required=True); d.add_argument("--assets", required=True, help='{"chemin du fichier": "id asset"}'); d.add_argument("--handle")
    a = ap.parse_args()
    {"build": build, "lock": lock, "db": dbfiles}[a.cmd](a)
