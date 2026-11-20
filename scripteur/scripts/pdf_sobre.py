#!/usr/bin/env python3
"""PDF sobre (titre + numéro bleu + script complet, rien d'autre).
Usage : python3 pdf_sobre.py <scripts.json> <dossier_de_sortie>
scripts.json : {"titre": "Scripts de la semaine", "sous_titre": "Tournage jeudi",
                "scripts": [{"titre": "...", "texte": ["paragraphe 1", "paragraphe 2"]}]}
"""
import html, json, pathlib, re, subprocess, sys

src, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
d = json.loads(src.read_text(encoding="utf-8"))

def fr(x):
    x = html.escape(x)
    for a, b in ((" ?", "\u00a0?"), (" !", "\u00a0!"), (" »", "\u00a0»"), ("« ", "«\u00a0")):
        x = x.replace(a, b)
    return re.sub(r"(\d+) (\w)", "\\1\u00a0\\2", x)

STYLE = """@page{size:A4;margin:24mm 24mm 22mm}
body{margin:0;font-family:Inter,sans-serif;font-size:13pt;line-height:1.55;color:#1B2230;orphans:3;widows:3}
h1{font-weight:700;font-size:24pt;color:#13253F;margin:0}
.date{color:#7A8494;font-size:11pt;margin:1mm 0 10mm}
h2{display:flex;font-weight:700;font-size:15.5pt;color:#13253F;margin:0 0 3mm;break-after:avoid}
h2 .n{color:#0A77BD;min-width:9mm;flex:0 0 9mm}
.v{margin-bottom:11mm}.body{padding-left:9mm}p{margin:0 0 3mm}"""
FONTS = '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">'

blocs = "".join(
    f'<div class="v"><h2><b class=n>{i}</b><span>{fr(s["titre"])}</span></h2><div class="body">'
    + "".join(f"<p>{fr(p)}</p>" for p in s["texte"]) + "</div></div>"
    for i, s in enumerate(d["scripts"], 1))
titre = d.get("titre", "Scripts")
body = f'<h1>{fr(titre)}</h1><div class="date">{fr(d.get("sous_titre", ""))}</div>{blocs}'
page = out / "scripts.html"
page.write_text(f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>{fr(titre)}</title>{FONTS}<style>{STYLE}</style></head><body>{body}</body></html>', encoding="utf-8")
pdf = out / (re.sub(r"[^\w-]+", "-", titre).strip("-") + ".pdf")
subprocess.run(["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--headless=new", "--use-mock-keychain",
                "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=4000", f"--print-to-pdf={pdf}", page.as_uri()],
               capture_output=True)
print(pdf if pdf.exists() else "ERREUR : PDF non créé")
