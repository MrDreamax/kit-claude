#!/usr/bin/env python3
"""Monteur EXPRESS : titre + sous-titres + musique, SANS le rendu HyperFrames.
  python3 express.py <dossier du reel>        (plan.json prêt, dérush fait : clip.mp4 + words.json, comme pour monte.sh)
Pourquoi : RUSH (style Minimaliste) = 6 min de machine par version, dont 5 min de rendu Chrome image par image pour
un titre fixe et des sous-titres. Ici : build.mjs garde le découpage et la place de chaque sous-titre (mêmes règles),
Pillow dessine chaque état de l'écran en PNG transparent, ffmpeg les pose sur clip.mp4 (puce vidéo du Mac), puis le
même mix.py et le même Gardien que monte.sh. Refuse tout plan qui a autre chose qu'un titre et des sous-titres -> monte.sh.
"""
import glob, html, json, os, re, subprocess, sys, time
from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = os.path.dirname(os.path.abspath(__file__))
# 14/11 (vitesse) : un seul rendu à la fois + Mac éveillé + durée notée = verrou.py (SUPERMONTEUR_VERROU=0 pour couper)
if not os.environ.get("SUPERMONTEUR_VERROU_TENU") and os.environ.get("SUPERMONTEUR_VERROU") != "0":
    os.execvp(sys.executable, [sys.executable, os.path.join(S, "verrou.py"), "--", sys.executable, os.path.abspath(__file__)] + sys.argv[1:])
D = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "."); os.chdir(D)
T0 = time.time()
def etape(m): print(f"▶ {m}  ({time.time() - T0:.0f} s)", flush=True)
# sortie 2 = « pas un montage express » : monter.py passe alors à monte.sh ; sortie 1 = vrai problème, on s'arrête
def stop(m, code=1): print(f"⛔ STOP ({time.time() - T0:.0f} s) : {m}"); sys.exit(code)
def run(cmd, log):
    with open(log, "w") as f: r = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT)
    return r.returncode

plan = json.load(open("plan.json"))
EN_TROP = [k for k in ("brolls", "bigwords", "numbers", "motions", "lists", "proofs", "inserts", "silences", "keywords", "cta", "ctaMenu", "mini", "zooms", "cartons")   # cartons = cartons.py dans monte.sh ; : mini et zooms oubliés = cartons perdus sans alerte (RUSH)
           if plan.get(k)]
if EN_TROP: stop(f"ce plan a {', '.join(EN_TROP)} : pas un montage express, lancer monte.sh", 2)
W, H, FPS = 1080, 1920, 30
os.environ["PATH"] = f"{os.path.expanduser('~/.local/bin')}:{os.path.expanduser('~/.local/node/bin')}:{os.environ['PATH']}"

# même fin propre que monte.sh (coupes d'un ancien dérush qui finissaient après le rush), avant le Gardien
r_ = subprocess.run(["python3", f"{S}/fin_propre.py", "plan.json"], capture_output=True, text=True)
print(r_.stdout.strip()) if r_.stdout.strip() else None
if r_.returncode: stop("fin_propre.py : " + (r_.stderr.strip().splitlines() or ["?"])[-1])
# 14/11 (vitesse : 8 rendus pour 1 utile) : rien n'a changé depuis le dernier rendu = pas de rendu. FORCE=1 pour forcer.
import hashlib
def _empreinte():
    h = hashlib.sha1()
    for p in ["plan.json", "words.json", "cut.segments.json", plan.get("cam", "clip.mp4")] + [os.path.join(S, x) for x in ("express.py", "build.mjs", "mix.py")]:
        if os.path.exists(p): h.update(p.encode()); h.update(str(os.path.getsize(p)).encode()); h.update(str(os.path.getmtime(p)).encode())
    return h.hexdigest()
EMP = _empreinte()
if os.environ.get("FORCE") != "1" and os.path.exists("final.mp4") and os.path.exists("renders/express.empreinte") and open("renders/express.empreinte").read() == EMP:
    open(os.path.expanduser("~/.cache/supermonteur/saute"), "w").close()   # verrou.py ne compte pas ce passage dans les durées
    print("✅ rien n'a changé depuis le dernier rendu : final.mp4 est déjà à jour (aucun rendu lancé, FORCE=1 pour forcer)"); sys.exit(0)
etape("Composition (découpage des sous-titres du moteur)")
if run(["node", f"{S}/build.mjs", "--plan", "plan.json", "--out", "index.html"], "build.log"): stop("build.mjs (voir build.log)")
print(open("build.log").read().strip().splitlines()[-1])

etape("Gardien avant rendu")
run(["python3", f"{S}/gardien.py", ".", "--avant"], "gardien-avant.log")
g = open("gardien-avant.log").read()
print("\n".join(l for l in g.splitlines() if "❌" in l or "GARDIEN" in l))
if "le rendu peut partir" not in g: stop("corriger plan.json puis relancer (aucun rendu lancé)")

# ---------- ce que build.mjs a posé : textes, places, temps ----------
page = open("index.html", encoding="utf-8").read()
css = lambda pat, default=None: (re.search(pat, page) or [None, default])[1]
times = {m[0]: (float(m[1]), float(m[2])) for m in re.findall(r'V\("#([\w-]+)",([\d.]+),([\d.]+)', page)}
SUBY = int(css(r"\.cap\{position:absolute;[^}]*?top:(\d+)px"))
SUBSIZE = int(css(r'\.cap\{[^}]*?font-family:"Sub";font-weight:700;font-size:(\d+)px'))
SUBTRACK = float(css(r'\.cap\{[^}]*?font-size:\d+px;line-height:[\d.]+;letter-spacing:([\d.]+)px', 0))
caps = []
for cls, cid, top, txt in re.findall(r'<div class="(cap[^"]*)" id="(c[\d_]+)"(?: style="top:(\d+)px")?>(.*?)</div>', page):
    if "<" in re.sub(r'<span style="color:#[0-9A-Fa-f]{6}">[^<]*</span>', "", txt): stop(f"sous-titre {cid} avec mot fort ({txt}) : lancer monte.sh", 2)
    a, b = times[cid]; caps.append((a, b, txt, int(top or SUBY)))   # txt garde les <span> de plan.couleurs
# (RUSH écran coupé, sous-titres sur l'animation claire) : la couleur de plan.typo.sub (CSS .cap) est suivie ;
# une couleur foncée n'a pas d'ombre (l'ombre noire floute le texte foncé). Avant : toujours blanc.
_col = re.search(r"\.cap\{font-weight:[^}]*?color:(#[0-9A-Fa-f]{6})", page)
SUBCOL = tuple(int(_col[1][i:i + 2], 16) for i in (1, 3, 5)) if _col else (255, 255, 255)
SUBOMBRE = sum(SUBCOL) / 3 > 140
FONT = os.path.join("fonts", re.search(r'font-family:"Sub";src:url\("fonts/([^"]+)"', page)[1])
title = None
if plan.get("title"):
    T = plan["title"]; ta, tb = times["htitle"]
    # (Fable 5.2 version B) : titre recollé sur 1 ligne par build.mjs (règle) = pas de div ht2 -> plantage. ht2 devient optionnelle.
    l1 = re.search(r'<div class="ht1">(.*?)</div>', page)[1]; l2 = (re.search(r'<div class="ht2">(.*?)</div>', page) or [None, ""])[1]
    _st = {k: re.findall(rf"\.{k}\{{([^}}]*)\}}", page) for k in ("ht1", "ht2")}
    st = {k: (_st[k] or _st["ht1"])[-1] for k in ("ht1", "ht2")}   # la DERNIÈRE règle gagne (comme le CSS)
    num = lambda k, p, d=0: float((re.search(p, st[k]) or [None, d])[1])
    # police lue dans la règle CSS de la ligne, pas devinée (T1 / T2 n'existent qu'avec plan.typo : sans typo = plantage)
    fam = lambda k: re.search(r'font-family:"([^"]+)"', st[k])[1]
    tf = lambda k: os.path.join("fonts", re.search(rf'font-family:"{fam(k)}";src:url\("fonts/([^"]+)"', page)[1])
    coul = lambda k: (re.search(r"color:(#\w+)", st[k]) or [None, "#FFFFFF"])[1]   # sans couleur : celle de .htitle, blanc
    box = re.search(r'id="htitle" style="top:(\d+)px[^"]*"><div style="display:inline-block;background:([^;]+);border-radius:(\d+)px;padding:(\d+)px (\d+)px (\d+)px', page)
    pad_top = int(css(r"\.htitle\{[^}]*?padding:(\d+)px", 30))
    MAJ = lambda k, t: t.upper() if "text-transform:uppercase" in st[k] else t   # titre en majuscules (typo caps) perdu en express
    forte = 'class="htitle onlight"' in page or (plan.get("typo") or {}).get("shadow") == "forte"
    ombre = [(3, 0, .95), (8, 2, .85), (34, 0, .7), (70, 0, .45)] if forte else [(26, 4, .55), (3, 1, .35)]
    title = dict(ombre=ombre, a=ta, b=tb, top=int(box[1]) + pad_top if box else int(T.get("top", 250)), box=box,
                 lines=[(MAJ("ht1", html.unescape(l1)), tf("ht1"), num("ht1", r"font-size:(\d+)px"), num("ht1", r"line-height:([\d.]+)", 1.25),
                         num("ht1", r"letter-spacing:([\d.]+)px"), int(num("ht1", r"font-weight:(\d+)", 700)), coul("ht1")),
                        (MAJ("ht2", html.unescape(l2)), tf("ht2"), num("ht2", r"font-size:(\d+)px"), num("ht2", r"line-height:([\d.]+)", 1.1),
                         num("ht2", r"letter-spacing:([\d.]+)px"), int(num("ht2", r"font-weight:(\d+)", 400)), coul("ht2"))])
    # (RUSH « L'antiviralité ? » sur une ligne) : une ligne vide gardait sa hauteur = encadré blanc trop haut, texte collé en haut
    title["lines"] = [l for l in title["lines"] if l[0].strip()] or title["lines"][:1]
print(f"{len(caps)} sous-titres · titre {'oui' if title else 'non'} · police {os.path.basename(FONT)} {SUBSIZE} px · y {SUBY}")

# ---------- dessin (mêmes mesures que le CSS : interlignage centré, espacement des lettres, ombre douce) ----------
_fonts = {}
def font(path, size, weight):
    k = (path, size, weight)
    if k not in _fonts:
        f = ImageFont.truetype(path, size)
        try: f.set_variation_by_axes([weight if a["name"] in (b"Weight", "Weight") else a["default"] for a in f.get_variation_axes()])
        except Exception: pass
        _fonts[k] = f
    return _fonts[k]
def largeur(t, f, track): return f.getlength(t) + track * len(t)
def ecrit(draw, x, base, t, f, track, fill):
    for i, ch in enumerate(t): draw.text((x + f.getlength(t[:i]) + track * i, base), ch, font=f, fill=fill, anchor="ls")
def baseline(top, size, lh, f):
    asc, desc = f.getmetrics(); return top + (size * lh - (asc + desc)) / 2 + asc

def mots_colores(raw):
    """« LIVE » en <span style="color:#FFD60A"> (plan.couleurs) -> [(mot, couleur ou None)]."""
    out = []
    for m in re.finditer(r'<span style="color:(#[0-9A-Fa-f]{6})">([^<]*)</span>|([^<]+)', raw):
        col = tuple(int(m[1][i:i + 2], 16) for i in (1, 3, 5)) if m[1] else None
        out += [(html.unescape(w), col) for w in (m[2] if m[1] else m[3]).split()]
    return out

def calque_sous_titre(img, raw, top):
    f = font(FONT, SUBSIZE, 700); lh = 1.05
    mc = mots_colores(raw); txt = " ".join(w for w, _ in mc)
    mots, lignes, cur = txt.split(), [], ""
    for m in mots:   # boîte de 840 px (left/right 120) : retour à la ligne comme le navigateur
        essai = (cur + " " + m).strip()
        if cur and largeur(essai, f, SUBTRACK) > W - 240: lignes.append(cur); cur = m
        else: cur = essai
    lignes.append(cur)
    # (RUSH : 50 s de dessin) : tout se dessine dans une bande de 80 px autour du texte, plus sur l'écran entier :
    # le flou (portée ~30 px) n'atteint jamais le bord de la bande, donc même image au pixel près, ~8 x moins de calcul
    y0 = max(0, int(top) - 80); y1 = min(H, int(top + len(lignes) * SUBSIZE * lh) + 80)
    texte = Image.new("L", (W, y1 - y0), 0); dt = ImageDraw.Draw(texte)
    masques = {}   # couleur -> masque des seuls mots de cette couleur
    k = 0
    for i, l in enumerate(lignes):
        x0, base = (W - largeur(l, f, SUBTRACK)) / 2, baseline(top + i * SUBSIZE * lh, SUBSIZE, lh, f) - y0
        ecrit(dt, x0, base, l, f, SUBTRACK, 255)
        pos = 0
        for w in l.split(" "):
            col = mc[k][1] if k < len(mc) else None; k += 1
            if col:
                if col not in masques: masques[col] = Image.new("L", texte.size, 0)
                dm = ImageDraw.Draw(masques[col])
                for c in range(pos, pos + len(w)):
                    dm.text((x0 + f.getlength(l[:c]) + SUBTRACK * c, base), l[c], font=f, fill=255, anchor="ls")
            pos += len(w) + 1
    if SUBOMBRE:
        ombre = texte.filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v * 0.55))   # text-shadow 0 3px 18px rgba(0,0,0,.55)
        noir = Image.new("RGBA", texte.size, (0, 0, 0, 0)); noir.putalpha(ombre)
        img.alpha_composite(noir, (0, y0 + 3))
    blanc = Image.new("RGBA", texte.size, SUBCOL + (0,)); blanc.putalpha(texte); img.alpha_composite(blanc, (0, y0))
    for col, m in masques.items():   # mots en couleur posés par-dessus, au même endroit
        cl = Image.new("RGBA", texte.size, col + (0,)); cl.putalpha(m); img.alpha_composite(cl, (0, y0))

def calque_titre(img):
    t = title; box = t["box"]
    fs = [font(p, int(sz), wt) for (_, p, sz, _, _, wt, _) in t["lines"]]
    lw = [largeur(l, f, tr) for (l, _, _, _, tr, _, _), f in zip(t["lines"], fs)]
    pt, px, pb = (int(box[4]), int(box[5]), int(box[6])) if box else (0, 0, 0)
    hh = [sz * lh for (_, _, sz, lh, _, _, _) in t["lines"]]
    bw, bh = max(lw) + 2 * px, pt + sum(hh) + pb; x0, y0 = (W - bw) / 2, t["top"]
    if box:   # boîte arrondie dessinée 4x plus grand puis réduite = bords lisses
        k = 4; m = Image.new("L", (int(bw * k), int(bh * k)), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, bw * k - 1, bh * k - 1], radius=int(box[3]) * k, fill=255)
        m = m.resize((round(bw), round(bh)), Image.LANCZOS)
        # la boîte peut être translucide (rgba du CSS, que Pillow ne lit pas) : l'opacité passe dans le masque
        rgba = re.fullmatch(r"rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([\d.]+)\s*\)", box[2].strip())
        if rgba: m = m.point(lambda v, a=float(rgba[4]): int(v * a))
        c = Image.new("RGBA", m.size, tuple(int(rgba[i]) for i in (1, 2, 3)) if rgba else box[2].strip()); c.putalpha(m)
        img.alpha_composite(c, (round(x0), round(y0)))
    # l'ombre du titre comme le CSS de build.mjs
    # (.htitle douce ; onlight / typo.shadow "forte" = ombre forte en 4 couches). Avant : titre express sans aucune ombre.
    if not box:
        masque = Image.new("L", (W, H), 0); dm = ImageDraw.Draw(masque); y = y0 + pt
        for ((l, _, sz, lh, tr, _, col), f, w, h) in zip(t["lines"], fs, lw, hh):
            ecrit(dm, (W - w) / 2, baseline(y, sz, lh, f), l, f, tr, 255); y += h
        for flou, dy, force in t["ombre"]:
            o = masque.filter(ImageFilter.GaussianBlur(flou / 2)) if flou else masque
            noir = Image.new("RGBA", (W, H), (0, 0, 0, 0)); noir.putalpha(o.point(lambda v, k=force: int(v * k)))
            img.alpha_composite(noir, (0, dy))
    d = ImageDraw.Draw(img); y = y0 + pt
    for ((l, _, sz, lh, tr, _, col), f, w, h) in zip(t["lines"], fs, lw, hh):
        ecrit(d, (W - w) / 2, baseline(y, sz, lh, f), l, f, tr, col); y += h

etape("Dessin des sous-titres")
os.makedirs("express", exist_ok=True)
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", plan.get("cam", "clip.mp4")]))
bornes = sorted({0.0, dur, *[x for a, b, *_ in caps for x in (a, b)], *([title["a"], min(title["b"], dur)] if title else [])})
bornes = [round(round(x * FPS) / FPS, 4) for x in bornes if x <= dur]   # calé sur les images : pas de demi-image
bornes = sorted(set(bornes))
liste, vu, TITRE_SEUL = [], {}, []
for i, (a, b) in enumerate(zip(bornes, bornes[1:])):
    if b - a < 1e-6: continue
    mid = (a + b) / 2
    on = [c for c in caps if c[0] <= mid < c[1]]
    tit = bool(title and title["a"] <= mid < title["b"])
    cle = (tuple((c[2], c[3]) for c in on), tit)
    if cle not in vu:
        # le titre (4 flous sur tout l'écran) se dessine UNE fois, puis chaque état part d'une copie
        if tit and not TITRE_SEUL: TITRE_SEUL.append(Image.new("RGBA", (W, H), (0, 0, 0, 0))); calque_titre(TITRE_SEUL[0])
        img = TITRE_SEUL[0].copy() if tit else Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for c in on: calque_sous_titre(img, c[2], c[3])
        p = f"express/e{len(vu):03d}.png"; img.save(p, compress_level=1); vu[cle] = p
    liste.append((vu[cle], b - a))
with open("express/calques.txt", "w") as f:
    for p, d_ in liste: f.write(f"file '{os.path.basename(p)}'\nduration {d_:.4f}\n")
    f.write(f"file '{os.path.basename(liste[-1][0])}'\n")
print(f"{len(vu)} images de calque pour {len(liste)} moments")

etape("Rendu express (puce vidéo du Mac)")
os.makedirs("renders", exist_ok=True)
R = f"renders/express_{time.strftime('%Y-%m-%d_%H-%M-%S')}.mp4"
# couleurs : on garde la plage et l'espace de la source (piège 1), décodage au processeur (piège 2 : image verte)
if run(["ffmpeg", "-nostdin", "-y", "-v", "error", "-i", plan.get("cam", "clip.mp4"),
        "-f", "concat", "-safe", "0", "-i", "express/calques.txt",
        "-filter_complex", f"[1:v]fps={FPS},format=rgba[o];[0:v][o]overlay=0:0:eof_action=pass:format=auto,format=yuv420p[v]",
        "-map", "[v]", "-an", "-r", str(FPS), "-c:v", "h264_videotoolbox", "-profile:v", "high", "-b:v", "16M",
        "-color_range", "tv", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-t", f"{dur:.3f}", R],
       "render.log"): stop("rendu ffmpeg (voir render.log)")

etape("Mix")
if run(["python3", f"{S}/mix.py", "plan.json", R, plan.get("cam", "clip.mp4"), "final.mp4"], "mix.log"): stop("mix.py (voir mix.log)")
# (disque plein : 20 Go d'anciens rendus) : on garde seulement le dernier rendu, final.mp4 est déjà fait
for vieux in glob.glob("renders/express_*.mp4"):
    if os.path.abspath(vieux) != os.path.abspath(R):
        try: os.remove(vieux)
        except OSError: pass
print("\n".join(l for l in open("mix.log").read().splitlines() if l.startswith(("musique", "final"))))

etape("Gardien final")
G = run(["python3", f"{S}/gardien.py", "."], "gardien.log")
print("\n".join(l for l in open("gardien.log").read().splitlines() if "❌" in l or "GARDIEN" in l))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "final.mp4", "-vf", "fps=1,scale=144:-1,tile=10x7", "-frames:v", "1", "planche.jpg"])
if G: stop("le Gardien final bloque : NE PAS LIVRER")
# Juge = sous-agent Claude séparé (Gemini retiré)
fd = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "final.mp4"]))
t = time.time() - T0
open("renders/express.empreinte", "w").write(EMP)
print(f"✅ final.mp4 ({fd:.2f} s) en {int(t // 60)} min {int(t % 60)} s · planche.jpg")
