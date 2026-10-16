"""FAMILLE « B-ROLL + TEXTE » : 1 plan (2 max) de 5-7 s, du texte AU-DESSUS DE LA TÊTE, musique, zéro voix.
  python3 brolltexte.py plan.json            -> final.mp4 + legende.txt (+ text.png pour contrôle)
plan.json :
  "brolls": [{"src": "<chemin absolu>", "from": 1.33 | "auto", "dur": 6}]   1 ou 2 plans, total 5-7 s
  "text": {"lines": ["Tu n'es pas nul en vidéo.", "Ton message est flou."], "strong": "flou", "cta": "Commente POSITION"}
           2 lignes (3 MAX), chacune tient sur UNE ligne ; "strong" = mot fort en serif italique ; "cta" FACULTATIF
  "style": "da" (défaut, VALIDÉ : police de la DA en majuscules blanches + mot fort serif italique, ombre douce)
           | "natif" (bandeau blanc arrondi, texte noir, casse mixte = l'outil texte d'Instagram)
  "y": 470          facultatif : force le centre du bloc texte (sinon calculé au-dessus de la tête)
  "music": {"src": "<wav Epidemic coupé à la durée, loopable>"}
  "caption": "..."  la légende du post (écrite par l'étape Copywriter)
  "da": "chemin.json"   facultatif : une DA de montage à la place de la tienne (voir scripts/reglages.py)
Règles 
- Texte TOUJOURS au-dessus de la tête. Le script mesure le haut de la tête sur tout le plan (5e centile = quand elle est
  la plus haute) ; pas assez de place -> le plan descend et le haut de l'image est prolongé en fondu (« place rajoutée »
  validée en montage viral). Pas de visage (de dos, mains, lieu) -> texte en haut de la zone sûre.
- CTA facultatif ; s'il y en a un : EN BAS, séparé du texte (bloc bas à 1 420 px max).
- Jamais de ponctuation en fin de texte ni de CTA (retirée toute seule, l'emoji final reste).
- Fond trop clair ou trop chargé sous le texte -> voile noir léger en haut (comme les titres-questions), tout seul ;
  "veil": true / false dans plan.json pour forcer.
- Zones mortes Insta : 270-1480 px en hauteur, 120-960 px en largeur.
"""
import json, os, subprocess, sys
import numpy as np

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if os.path.basename(os.path.dirname(os.path.abspath(__file__))) == "scripts" \
    else os.path.expanduser("~/.claude/skills/supermonteur")
plan_p = sys.argv[1]
here = os.path.dirname(os.path.abspath(plan_p))
plan = json.load(open(plan_p))
sys.path.insert(0, os.path.join(SKILL, "scripts"))
import reglages
CFG = reglages.charger()
DA = reglages.da()
if plan.get("da"):   # une DA complète donnée dans le plan
    DA = json.load(open(os.path.expanduser(plan["da"]) if os.path.isabs(os.path.expanduser(plan["da"])) else os.path.join(here, plan["da"])))
    DA.setdefault("fonts", {}).setdefault("sans", "Montserrat.ttf"); DA["fonts"].setdefault("serif", "InstrumentSerif-Italic.ttf")
    DA.setdefault("colors", {}).setdefault("text", "#fff")
W, H, FPS = 1080, 1920, 30
TOP, BOTTOM, LEFT, RIGHT = 270, 1480, 120, 960      # zones mortes Instagram
AIR, SMAX, FADE = 70, 480, 260                     # air entre texte et tête ; descente max du plan ; fondu (viral.py)
run = lambda *a: subprocess.run(a, check=True)
P = lambda n: os.path.join(here, n)

# --- 1. plans : coupés, recadrés 1080x1920, bruts, enchaînés en coupe franche ---
parts = []
for i, b in enumerate(plan["brolls"]):
    start = b.get("from", 0)
    if start == "auto":
        out = subprocess.check_output(["python3", os.path.join(SKILL, "scripts/broll.py"), "steady", b["src"], str(b["dur"])]).decode()
        start = float(out.split("from ")[1].split("s")[0])
    p = P(f"_b{i}.mp4")
    run("ffmpeg", "-v", "error", "-y", "-ss", str(start), "-i", b["src"], "-t", str(b["dur"]), "-map", "0:v:0", "-an",
        "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},fps={FPS},format=yuv420p",
        "-c:v", "libx264", "-crf", "14", "-preset", "slow", p)
    parts.append(p)
open(P("_list.txt"), "w").write("".join(f"file '{p}'\n" for p in parts))
run("ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", P("_list.txt"), "-c", "copy", P("_broll.mp4"))
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", P("_broll.mp4")]))


def head_top(src):
    """Haut de la tête (cheveux compris, px) au moment où elle est la plus haute ; None si aucun visage."""
    import mediapipe as mp
    from mediapipe.tasks.python import vision, BaseOptions
    w, h = 540, 960
    raw = subprocess.check_output(["ffmpeg", "-nostdin", "-v", "error", "-i", src, "-vf", f"fps=4,scale={w}:{h}",
                                   "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
    fr = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)
    det = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=os.path.join(SKILL, "models", "face_landmarker.task")),
        running_mode=vision.RunningMode.IMAGE))
    tops = []
    for f in fr:
        r = det.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(f)))
        if r.face_landmarks:
            L = r.face_landmarks[0]
            tops.append(L[10].y * H - 0.45 * (L[152].y - L[10].y) * H)
    return int(np.percentile(tops, 5)) if len(tops) >= len(fr) * 0.3 else None


# --- 2. texte : HTML -> PNG transparent 1080x1920 (vraies polices, emoji Apple) ---
t = plan["text"]; style = plan.get("style", "da")
import re
def nopunct(x):
    """Pas de ponctuation à la fin d'un texte (l'emoji final reste)."""
    emo = re.search(r"[\s\U0001F000-\U0001FFFF\u2600-\u27BF\uFE0F]*$", x).group(0)
    core = x[:len(x) - len(emo)] if emo else x
    return re.sub(r"[\s.,;:!?…«»\"']+$", "", core) + (" " + emo.strip() if emo.strip() else "")
lines, cta = [nopunct(l) for l in t["lines"]], nopunct(t.get("cta", ""))
if len(lines) > 3: sys.exit(f"!! {len(lines)} lignes de texte : 2 conseillées, 3 MAX. Raccourcir.")
fonts = os.path.join(SKILL, "fonts")
strong = t.get("strong", "")
isemo = lambda c: ord(c) >= 0x1F000 or 0x2600 <= ord(c) <= 0x27BF or ord(c) == 0xFE0F


def row_html(s):
    if style == "da" and strong and strong in s:
        a, z = s.split(strong, 1)
        txt = "".join(c for c in z if not isemo(c)).strip(); emo = "".join(c for c in z if isemo(c))
        glue = txt if txt and not txt[0].isalnum() else ""          # ponctuation collée au mot fort
        rest = txt[len(glue):].strip() if glue else txt              # des mots après le mot fort = police normale
        mixed = bool(a.strip() or rest)
        h = (f'<span class="l">{a.strip().upper()} </span>' if a.strip() else "") + \
            f'<span class="s{" m" if mixed else ""}">{strong}{glue}</span>' + \
            (f'<span class="l"> {rest.upper()}</span>' if rest else "")
        return f'<div class="row">{h}' + (f'<span class="e">{emo}</span>' if emo else "") + "</div>"
    return f'<div class="row"><span class="l">{s.upper() if style == "da" else s}</span></div>'


css = f"""
@font-face{{font-family:Mont;src:url("file://{fonts}/{DA['fonts']['sans']}");font-weight:100 900}}
@font-face{{font-family:Serif;src:url("file://{fonts}/{DA['fonts']['serif']}");font-style:italic}}
html,body{{margin:0;width:{W}px;height:{H}px;background:transparent}}
.blk{{position:absolute;left:{LEFT}px;width:{RIGHT-LEFT}px;text-align:center}}
.row,.cta{{display:block;white-space:nowrap}}
"""
if style == "natif":
    css += """
.l,.c{font-family:Mont,'Apple Color Emoji';font-weight:600;font-size:50px;line-height:1.32;color:#111;background:#fff;
   padding:4px 22px 6px;border-radius:14px}
.row{margin:0 0 -2px}
"""
else:
    acc = DA["colors"].get("text", "#fff")
    sh = "text-shadow:0 2px 6px rgba(0,0,0,.55),0 0 28px rgba(0,0,0,.45)"
    css += f"""
.l{{font-family:Mont,'Apple Color Emoji';font-weight:700;font-size:56px;letter-spacing:.5px;line-height:1.18;color:{acc};{sh}}}
.s{{font-family:Serif;font-style:italic;font-size:124px;line-height:1.0;color:{acc};{sh}}}
.s.m{{font-size:96px}}
.e{{font-family:'Apple Color Emoji';font-size:64px;margin-left:10px;vertical-align:12px}}
.c{{font-family:Mont,'Apple Color Emoji';font-weight:600;font-size:42px;letter-spacing:.5px;color:{acc};{sh}}}
.row{{margin:0 0 6px}}
"""


def render(ytop, veil=0):
    """Écrit le HTML (bloc texte dont le HAUT est à ytop ; CTA en bas ; voile noir jusqu'à veil px), capture le PNG,
    rend [haut, bas, ok, cta_haut, cta_bas]."""
    vl = (f'<div style="position:absolute;left:0;top:0;width:{W}px;height:{veil + 170}px;background:linear-gradient(180deg,'
          f'rgba(0,0,0,.5) 0,rgba(0,0,0,.45) {veil}px,rgba(0,0,0,0) {veil + 170}px)"></div>') if veil else ""
    html = f"<!doctype html><meta charset=utf-8><style>{css}</style>" + vl + \
           f'<div id=b class=blk style="top:{ytop}px">' + "".join(row_html(s) for s in lines) + "</div>" + \
           (f'<div id=c class="blk cta" style="bottom:{H - (BOTTOM - 60)}px"><span class="c">{cta}</span></div>' if cta else "")
    open(P("_text.html"), "w").write(html)
    js = f"""
import {{ createRequire }} from "node:module";
import {{ existsSync, readdirSync }} from "node:fs";
import {{ join }} from "node:path";
import {{ homedir }} from "node:os";
// puppeteer-core + Chrome installés par HyperFrames (même recherche que zones.mjs) ; secours : Google Chrome
const NPX = join(homedir(), ".npm", "_npx"), CH = join(homedir(), ".cache", "puppeteer", "chrome-headless-shell");
const mod = existsSync(NPX) && readdirSync(NPX).map(d => join(NPX, d, "node_modules")).find(d => existsSync(join(d, "puppeteer-core")));
if (!mod) {{ console.log("puppeteer-core introuvable : lancer une fois « npx --yes hyperframes@0.6.81 browser ensure »"); process.exit(1); }}
const puppeteer = createRequire(mod + "/")("puppeteer-core");
const hs = existsSync(CH) && readdirSync(CH).sort().reverse().map(v => join(CH, v)).flatMap(v => readdirSync(v).map(x => join(v, x, "chrome-headless-shell"))).find(existsSync);
const gc = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
let exe = hs || (existsSync(gc) && gc);
if (!exe) {{ try {{ exe = (await import("node:child_process")).execSync("npx --yes hyperframes@0.6.81 browser path", {{encoding: "utf8"}}).trim().split("\\n").pop(); }} catch (e) {{}} }}
if (!exe) {{ console.log("Chrome introuvable (ni chrome-headless-shell ni Google Chrome)"); process.exit(1); }}
const b = await puppeteer.launch({{executablePath: exe, headless: "new", args: ["--allow-file-access-from-files", "--no-sandbox"]}});
const p = await b.newPage(); await p.setViewport({{width: {W}, height: {H}, deviceScaleFactor: 1}});
await p.goto("file://{P('_text.html')}"); await p.evaluate(() => document.fonts.ready);
// chaque ligne doit tenir dans {RIGHT-LEFT} px : la police rétrécit (min 44 px pour le texte, 34 px pour le CTA)
const ok = await p.evaluate((maxW) => {{
  let ok = true;
  for (const row of document.querySelectorAll(".row,.cta")) {{
    const els = [...row.querySelectorAll("span")];
    const min = row.classList.contains("cta") ? 34 : 44;
    let k = 1;
    while (row.scrollWidth > maxW && k > 0.5) {{
      k -= 0.02;
      for (const e of els) {{ e.dataset.fs ||= parseFloat(getComputedStyle(e).fontSize); e.style.fontSize = (e.dataset.fs * k) + "px"; }}
    }}
    const l = els.find(e => e.classList.contains("l") || e.classList.contains("c"));
    if (row.scrollWidth > maxW || (l && parseFloat(getComputedStyle(l).fontSize) < min)) ok = false;
  }}
  return ok;
}}, {RIGHT-LEFT});
const r = await p.evaluate(() => {{ const f = id => {{ const e = document.getElementById(id); if (!e) return [0, 0];
  const q = e.getBoundingClientRect(); return [Math.round(q.top), Math.round(q.bottom)]; }}; return [...f("b"), ...f("c")]; }});
console.log(JSON.stringify([r[0], r[1], ok, r[2], r[3]]));
await p.screenshot({{path: "{P('text.png')}", omitBackground: true}}); await b.close();
"""
    open(P("_shot.mjs"), "w").write(js)
    return json.loads(subprocess.check_output(["node", P("_shot.mjs")]).decode().strip().splitlines()[-1])


top0, bot0, ok, _, _ = render(TOP + 30)
if not ok: sys.exit("!! une ligne ne tient pas sur une ligne même en petit : raccourcir la phrase.")
hb = bot0 - top0                                   # hauteur du bloc texte

# --- 3. place au-dessus de la tête ---
S, head = 0, None
if "y" in plan:
    ytop = int(plan["y"] - hb / 2)
    print(f"texte forcé : centre à {plan['y']} px")
else:
    head = head_top(P("_broll.mp4"))
    if head is None:
        ytop = TOP + 30
        print("pas de visage dans le plan : texte en haut de la zone sûre")
    else:
        room = head - AIR - (TOP + 30)             # place entre la zone sûre et la tête
        S = int(min(SMAX, max(0, hb - room)))
        ytop = int(TOP + 30 + max(0, (room + S - hb) / 2))
        print(f"haut de tête {head} px · bloc texte {hb} px · place {room} px -> plan descendu de {S} px")
        if hb - room > SMAX:
            print(f"!! même descendu de {SMAX} px, le texte touche la tête : prendre un plan plus large (tête plus basse)")
cam = P("_broll.mp4")
if S > 0:                                          # fondu « place rajoutée » (même recette que viral.py)
    from PIL import Image
    ramp = np.ones((H, W), np.float32); x = np.linspace(0, 1, FADE)
    ramp[:FADE] = (x * x * (3 - 2 * x))[:, None]
    Image.fromarray((ramp * 255).astype(np.uint8)).save(P("_mask.png"))
    band = max(120, min((head or 420) - 60, 360))  # haut de l'image (mur, ciel), sans la tête (comme viral.py)
    fc = (f"[0:v]split[a][b];[a]crop={W}:{band}:0:0,scale={W}:{S + FADE},boxblur=28:2,eq=brightness=-0.05,pad={W}:{H}:0:0:black[bg];"
          f"[b]format=rgba[c];[1:v]format=gray,scale={W}:{H}[m];[c][m]alphamerge[fg];[bg][fg]overlay=0:{S}:shortest=1,format=yuv420p[v]")
    run("ffmpeg", "-nostdin", "-v", "error", "-y", "-i", cam, "-loop", "1", "-framerate", str(FPS), "-i", P("_mask.png"),
        "-filter_complex", fc, "-map", "[v]", "-t", str(dur), "-c:v", "libx264", "-crf", "14", "-preset", "fast", P("_place.mp4"))
    os.remove(P("_mask.png")); cam = P("_place.mp4")
top, bot, ok, ctop, cbot = render(ytop)
# contraste sous le texte (« fond légèrement noir en haut » quand le contraste n'est pas bon)
x0, x1 = LEFT - 20, RIGHT + 20
ch, cy = (bot - top) // 2 * 2, top // 2 * 2          # ffmpeg arrondit le crop au pair sur du 4:2:0 : on le fait nous-mêmes
raw = subprocess.check_output(["ffmpeg", "-nostdin", "-v", "error", "-i", cam, "-vf",
                               f"fps=2,crop={x1 - x0}:{ch}:{x0}:{cy},format=gray", "-f", "rawvideo", "-"])
g = np.frombuffer(raw, np.uint8).reshape(-1, ch, x1 - x0).astype(np.float32)
clair, charge = float(np.percentile(g, 85)), float(np.mean([f.std() for f in g]))
veil = plan.get("veil", clair > 140 or charge > 45)
print(f"fond sous le texte : clair {clair:.0f}/255, chargé {charge:.0f} -> " + ("voile noir en haut" if veil else "pas de voile"))
if veil:
    top, bot, ok, ctop, cbot = render(ytop, veil=bot + 20)
print(f"bloc texte {top} -> {bot} px" + (f" · CTA {ctop} -> {cbot} px" if cta else ""))
if top < TOP or bot > BOTTOM or (cta and cbot > BOTTOM): print(f"!! hors zone Insta (autorisé {TOP}-{BOTTOM})")

# --- 4. image + son ---
fin = P("final.mp4")
m = plan.get("music")
cmd = ["ffmpeg", "-v", "error", "-y", "-i", cam, "-loop", "1", "-i", P("text.png")]
fc = "[0:v][1:v]overlay=0:0:shortest=1,format=yuv420p[v]"
if m:
    cmd += ["-i", m["src"]]
    # musique seule à -14 LUFS (pas de voix) : gain mesuré (loudnorm en 1 passe rate la cible sur 6 s) ;
    # fondus très courts pour que la boucle Instagram ne claque pas
    meas = subprocess.run(["ffmpeg", "-nostats", "-t", str(dur), "-i", m["src"], "-af", "ebur128", "-f", "null", "-"],
                          capture_output=True, text=True).stderr
    I = float([l for l in meas.splitlines() if l.strip().startswith("I:")][-1].split()[1])
    fc += f";[2:a]atrim=0:{dur},asetpts=N/SR/TB,volume={-14 - I:.2f}dB,alimiter=limit=0.79:attack=1:release=50:level=false," \
          f"afade=t=in:d=0.05,afade=t=out:st={dur-0.12}:d=0.12[a]"
cmd += ["-filter_complex", fc, "-map", "[v]"] + (["-map", "[a]", "-c:a", "aac", "-b:a", "192k", "-ar", "48000"] if m else []) + \
       ["-t", str(dur), "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-r", str(FPS), "-movflags", "+faststart", fin]
run(*cmd)
if plan.get("caption"):
    open(P("legende.txt"), "w").write(plan["caption"].strip() + "\n")
for f in parts + [P("_list.txt"), P("_broll.mp4"), P("_shot.mjs"), P("_place.mp4"), P("_text.html")]:
    if os.path.exists(f): os.remove(f)
print("OK", fin, f"{dur:.1f} s")
