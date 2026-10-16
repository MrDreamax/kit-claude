#!/usr/bin/env python3
"""Indexe ta bibliothèque de B-rolls pour que le monteur retrouve « le bon plan » (broll.py search).

Tes vidéos et photos vont dans ~/Documents/Contenu/medias/brolls/ (en vrac ou rangées en dossiers, peu importe).
  python3 indexer.py scan [--root DIR]      ajoute à _INDEX.csv les fichiers pas encore indexés (durée, format, date : automatique),
                                            crée une vignette par fichier (_vignettes/) et des PLANCHES numérotées (_planches/)
                                            que Claude REGARDE pour décrire chaque plan.
  python3 indexer.py todo                   liste les fichiers pas encore décrits.
  python3 indexer.py fill decrits.json      Claude écrit sa description : [{"fichier": "x.mp4", "theme": "travail", "action": "ecrit-clavier-bureau",
                                            "lieu": "bureau", "tenue": "t-shirt noir", "personne_visible": true, "qualite": "ok"}, ...]
  python3 indexer.py check                  signale les lignes dont le fichier a disparu.
Colonnes de _INDEX.csv : fichier, dossier, theme, action, tenue, lieu, orientation, resolution, duree_s, qualite, personne_visible,
date_tournage, usage. `qualite` = ok (net, stable, beau) ou moyen (non proposé). `usage` = souvenir pour une photo du passé
(proposée seulement quand tu parles de ton passé). Plans à ne jamais proposer : une ligne par plan dans <brolls>/_exclus.txt.
Rien n'est copié, déplacé ni supprimé : les originaux ne bougent pas.
"""
import csv, json, os, pathlib, subprocess, sys

SKILL = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SKILL / "scripts"))
import reglages

CFG = reglages.charger()
VID = (".mp4", ".mov", ".m4v")
IMG = (".jpg", ".jpeg", ".png", ".webp", ".heic")
FIELDS = ["fichier", "dossier", "theme", "action", "tenue", "lieu", "orientation", "resolution", "duree_s", "qualite",
          "personne_visible", "date_tournage", "usage"]
args = sys.argv[1:]
ROOT = pathlib.Path(args[args.index("--root") + 1]).expanduser() if "--root" in args else pathlib.Path(CFG["brolls_root"])
INDEX = ROOT / "_INDEX.csv"
VIG, PLA = ROOT / "_vignettes", ROOT / "_planches"


def lire():
    if not INDEX.exists():
        return []
    return list(csv.DictReader(open(INDEX, encoding="utf-8")))


def ecrire(rows):
    ROOT.mkdir(parents=True, exist_ok=True)
    with open(INDEX, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def probe(p):
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(p)],
                                  capture_output=True, text=True).stdout or "{}")
    st = next((s for s in j.get("streams", []) if s.get("codec_type") == "video"), None)
    if not st:
        return None
    w, h = st["width"], st["height"]
    if any(abs(int(d.get("rotation", 0))) % 180 == 90 for d in st.get("side_data_list", [])):
        w, h = h, w
    fmt = j.get("format", {})
    dur = float(fmt.get("duration") or 0) if str(p).lower().endswith(VID) else 0.0
    date = (fmt.get("tags", {}).get("creation_time") or st.get("tags", {}).get("creation_time") or "")[:10]
    if not date:
        import datetime
        date = datetime.date.fromtimestamp(p.stat().st_mtime).isoformat()
    m = max(w, h)
    return {"orientation": "V" if h > w else "H", "resolution": "4K" if m >= 3000 else "HD" if m >= 1280 else "SD",
            "duree_s": round(dur, 1), "date_tournage": date}


def vignette(p, dur):
    out = VIG / (p.stem + ".jpg")
    if out.exists():
        return out
    VIG.mkdir(parents=True, exist_ok=True)
    pre = ["-ss", f"{dur * .4:.2f}"] if dur else []
    subprocess.run(["ffmpeg", "-v", "error", "-y", *pre, "-i", str(p), "-frames:v", "1", "-vf", "scale=360:-2", str(out)], check=False)
    return out if out.exists() else None


def planches(items):
    """items = [(numero, fichier, vignette)] -> _planches/planche-NN.jpg, 5 x 3 vignettes numérotées."""
    from PIL import Image, ImageDraw, ImageFont
    PLA.mkdir(parents=True, exist_ok=True)
    fnt = ImageFont.truetype(str(SKILL / "fonts" / "Montserrat.ttf"), 26)
    try:
        fnt.set_variation_by_axes([800])   # Montserrat variable : graisse extra-bold, lisible sur une vignette
    except Exception:
        pass
    TW, TH, COLS, ROWS = 216, 384, 5, 3
    for k in range(0, len(items), COLS * ROWS):
        page = items[k:k + COLS * ROWS]
        sheet = Image.new("RGB", (TW * COLS, TH * ((len(page) + COLS - 1) // COLS)), (30, 30, 30))
        d = ImageDraw.Draw(sheet)
        for i, (num, name, v) in enumerate(page):
            if not v:
                continue
            im = Image.open(v).convert("RGB")
            im.thumbnail((TW, TH))
            x, y = (i % COLS) * TW, (i // COLS) * TH
            sheet.paste(im, (x + (TW - im.width) // 2, y + (TH - im.height) // 2))
            d.rectangle([x, y, x + 62, y + 34], fill=(0, 0, 0))
            d.text((x + 6, y + 2), str(num), font=fnt, fill=(255, 235, 80))
        sheet.save(PLA / f"planche-{k // (COLS * ROWS) + 1:02d}.jpg", quality=82)
    return (len(items) + COLS * ROWS - 1) // (COLS * ROWS)


def scan():
    rows = lire()
    connus = {(r["dossier"], r["fichier"]) for r in rows}
    nouveaux = []
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file() or p.name.startswith(".") or p.suffix.lower() not in VID + IMG:
            continue
        if any(part.startswith("_") for part in p.relative_to(ROOT).parts[:-1]):
            continue
        dossier = str(p.parent.relative_to(ROOT))
        dossier = "" if dossier == "." else dossier
        if (dossier, p.name) in connus:
            continue
        info = probe(p)
        if not info:
            print("illisible, ignoré :", p)
            continue
        r = {"fichier": p.name, "dossier": dossier, "theme": "", "action": "", "tenue": "", "lieu": "", "qualite": "", "personne_visible": "", "usage": ""}
        r.update(info)
        rows.append(r)
        nouveaux.append((p, r))
    ecrire(rows)
    items = []
    for i, (p, r) in enumerate(nouveaux, 1):
        items.append((i, p.name, vignette(p, r["duree_s"])))
    n = planches(items) if items else 0
    if items:
        json.dump([{"n": i, "fichier": name} for i, name, _ in items], open(PLA / "numeros.json", "w"), ensure_ascii=False, indent=1)
    print(f"{len(nouveaux)} nouveaux fichiers indexés ({len(rows)} au total) -> {INDEX}")
    if n:
        print(f"{n} planche(s) à regarder : {PLA}/planche-NN.jpg (numéros -> noms : {PLA}/numeros.json)")
        print("Puis écrire les descriptions dans un JSON et lancer : indexer.py fill decrits.json")


def fill(path):
    desc = {d["fichier"]: d for d in json.load(open(path, encoding="utf-8"))}
    rows = lire()
    n = 0
    for r in rows:
        d = desc.get(r["fichier"])
        if not d:
            continue
        for k in ("theme", "action", "tenue", "lieu", "qualite", "usage"):
            if d.get(k) is not None:
                r[k] = str(d[k])
        if "personne_visible" in d:
            r["personne_visible"] = str(bool(d["personne_visible"]))
        n += 1
    ecrire(rows)
    print(f"{n} description(s) écrites dans {INDEX}")


def todo():
    t = [r for r in lire() if not r["action"]]
    for r in t:
        print(os.path.join(r["dossier"], r["fichier"]))
    print(f"{len(t)} à décrire")


def check():
    manque = [r for r in lire() if not (ROOT / r["dossier"] / r["fichier"]).exists()]
    for r in manque:
        print("introuvable :", os.path.join(r["dossier"], r["fichier"]))
    print(f"{len(manque)} ligne(s) sans fichier")


if __name__ == "__main__":
    cmd = args[0] if args else "scan"
    if cmd == "fill" and len(args) > 1:
        fill(args[1])
    elif cmd in ("scan", "todo", "check"):
        globals()[cmd]()
    else:
        sys.exit(__doc__)
