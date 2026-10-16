"""Découpe les plans choisis et les range dans ta bibliothèque de B-rolls (+ _INDEX.csv).
Après analyse.py et segments.py, tu (ou Claude) regardes les planches de seg/sheets/ et notes les plans gardés dans selection.json :
  [{"ids": [4, 5, 6], "garder": 2, "theme": "travail", "action": "ecrit-clavier-bureau", "tenue": "t-shirt noir",
    "lieu": "bureau", "personne_visible": true}, ...]      ids = numéros des planches (plans semblables), garder = combien en prendre
    (les mieux notés par segments.py), theme/action/lieu sans accents, action = 2 à 5 mots en kebab-case qui décrivent EXACTEMENT ce qu'on voit.
  python3 export.py <dossier_seg> <dossier_rushs> selection.json [--dry]
Écrit dans <brolls_root>/<theme>/ (h264, son gardé, résolution d'origine), une vignette dans _vignettes/, et ajoute les lignes à _INDEX.csv.
Les rushs d'origine ne sont jamais modifiés.
"""
import csv, json, os, pathlib, re, subprocess, sys

SKILL = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SKILL / "scripts"))
import reglages

CFG = reglages.charger()
SEG, SRC, SEL = sys.argv[1:4]
DRY = "--dry" in sys.argv
B = pathlib.Path(CFG["brolls_root"])
INDEX = B / "_INDEX.csv"
FIELDS = ["fichier", "dossier", "theme", "action", "tenue", "lieu", "orientation", "resolution", "duree_s", "qualite",
          "personne_visible", "date_tournage", "usage"]
S = {g["id"]: g for g in json.load(open(f"{SEG}/segments.json"))}
sel = json.load(open(SEL, encoding="utf-8"))
enc = ["-c:v", "h264_videotoolbox", "-b:v", "40M"] if sys.platform == "darwin" else ["-c:v", "libx264", "-crf", "16", "-preset", "medium"]


def slug(x):
    import unicodedata
    x = unicodedata.normalize("NFD", x.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", x)).strip("-")[:48] or "plan"


def dims(p):
    j = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_streams", "-of", "json", p]))["streams"][0]
    w, h = j["width"], j["height"]
    if any(abs(int(d.get("rotation", 0))) % 180 == 90 for d in j.get("side_data_list", [])):
        w, h = h, w
    return w, h


old = list(csv.DictReader(open(INDEX, encoding="utf-8"))) if INDEX.exists() else []
num = {}
for r in old:
    m = re.match(r".*_(\d{3})\.\w+$", r["fichier"])
    if m:
        num[r["theme"]] = max(num.get(r["theme"], 0), int(m.group(1)))
new = []
for it in sel:
    best = sorted(it["ids"], key=lambda i: -S[i]["score"])[:int(it.get("garder", 1))]
    theme = slug(it["theme"])
    for i in best:
        g = S[i]
        src = os.path.join(SRC, g["clip"])
        w, h = dims(src)
        o = "V" if h > w else "H"
        res = "4K" if max(w, h) >= 3000 else "HD" if max(w, h) >= 1280 else "SD"
        num[theme] = num.get(theme, 0) + 1
        name = f"{theme}_{slug(it['action'])}_{o}_{res}_{num[theme]:03d}.mp4"
        dst = B / theme / name
        print("PLAN", i, g["clip"], g["start"], g["dur"], "->", f"{theme}/{name}")
        if not DRY:
            dst.parent.mkdir(parents=True, exist_ok=True)
            subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-ss", f"{g['start']:.3f}", "-i", src, "-t", f"{g['dur']:.3f}", "-map_metadata", "0",
                                   *enc, "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(dst)])
            (B / "_vignettes").mkdir(exist_ok=True)
            subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-ss", f"{g['dur'] * .4:.2f}", "-i", str(dst), "-frames:v", "1", "-vf", "scale=360:-2",
                                   str(B / "_vignettes" / (name[:-4] + ".jpg"))])
        new.append(dict(fichier=name, dossier=theme, theme=theme, action=slug(it["action"]), tenue=it.get("tenue", ""), lieu=it.get("lieu", ""),
                        orientation=o, resolution=res, duree_s=round(g["dur"], 1), qualite="ok", personne_visible=str(bool(it.get("personne_visible"))),
                        date_tournage=__import__("datetime").date.fromtimestamp(os.path.getmtime(src)).isoformat(), usage=""))
print(f"{len(new)} plans" + (" (essai à blanc, rien écrit)" if DRY else ""))
if not DRY and new:
    B.mkdir(parents=True, exist_ok=True)
    if INDEX.exists():
        import shutil
        shutil.copy2(INDEX, B / "_INDEX_avant_export.csv")
    with open(INDEX, "w", encoding="utf-8", newline="") as f:
        w_ = csv.DictWriter(f, FIELDS, extrasaction="ignore")
        w_.writeheader()
        w_.writerows(old + new)
    print("index :", len(old), "->", len(old) + len(new), "lignes")
