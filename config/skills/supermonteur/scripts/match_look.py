"""Cale chaque visuel ajouté (insert PNG, image, b-roll) SUR le rush, jamais l'inverse (Deakins, Waqas Qazi).
  python3 match_look.py clip.mp4 ins/badge.png broll/x.mp4 ...        -> mesure et dit ce qui ne colle pas
  python3 match_look.py clip.mp4 ins/badge.png ... --fix [--color] [--force] [--w 400]   -> écrit <nom>.cale.<ext> à côté
  --w = largeur de l'objet à l'écran en px (comme "w" dans plan.inserts, défaut 400) : la netteté se compare à taille d'écran.
Deux cas :
- OBJET (PNG détouré) : il est éclairé par la pièce. S'il est plus lumineux que le rush (P99 rush + 15), on baisse son EXPOSITION
  (même facteur sur les 3 couleurs). Sa VRAIE couleur ne bouge pas (règle : un objet réel garde sa couleur).
- PLAN (b-roll, image pleine) : raccord seulement. Blancs brûlés (P99 > 235) ramenés, noirs relevés (voile gris) redescendus.
  Ses plans restent BRUTS (règle : jamais de filtre créatif). --force = caler aussi noirs et blancs sur le rush.
Objet trop net par rapport au rush (x 1,6, mesuré à sa taille d'écran) -> flou de 0,6 px à l'écran. Plan : info seulement. --color = couleur de la lumière rapprochée à moitié
de celle du rush (seulement pour un visuel GÉNÉRÉ, jamais un objet réel ni ses vrais plans).
Néon et différence de médiane : affichés pour info (un néon se corrige en refaisant le visuel, pas en filtrant).
"""
import os, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lookstats import frames, stats, sharp, _size, IMG

WSCR, args, it = 400, [], iter(sys.argv[1:])
for a in it:
    if a == "--w": WSCR = int(next(it))
    elif not a.startswith("--"): args.append(a)
FIX, COLOR, FORCE = "--fix" in sys.argv, "--color" in sys.argv, "--force" in sys.argv
cam, items = args[0], args[1:]
R = stats(frames(cam))
print(f"rush {os.path.basename(cam)} : P1 {R['p1']} · P50 {R['p50']} · P99 {R['p99']} · lumière R/B {R['rb_lumiere']} · netteté {R['nettete']}")


def chain(lo, hi, lo2, hi2, gain, gains, sigma):
    k = (hi2 - lo2) / max(hi - lo, 1)
    lut = {c: f"clip(clip((val-{lo:.1f})*{k:.4f}+{lo2:.1f},0,255)*{gain:.4f}*{g:.4f},0,255)" for c, g in zip("rgb", gains)}
    f = f"format=rgba,lutrgb=r='{lut['r']}':g='{lut['g']}':b='{lut['b']}'"
    return f + (f",format=gbrap,gblur=sigma={sigma:.2f}:planes=7,format=rgba" if sigma else "")


for p in items:
    S = stats(frames(p, 6 if not p.lower().endswith(IMG) else 1))
    obj = S["transparent"] > 2
    # netteté comparée à TAILLE D'ÉCRAN (le rush est mesuré à 1/4 : 270x480) : objet = --w px de large, plan = plein écran 1080x1920
    w, h, _ = _size(p)
    scr = (WSCR / w if obj else max(1080 / w, 1920 / h))          # px à l'écran (1080) par px du fichier
    sh = sharp(frames(p, 6 if not p.lower().endswith(IMG) else 1, long_side=max(8, int(max(w, h) * scr * 0.25))))
    ratio = sh / R["nettete"] if sh and R["nettete"] else 1
    lo, hi = S["p1"], S["p99"]; lo2, hi2 = lo, hi; gain = 1.0; why = []; notes = []
    if obj:
        # objet éclairé par la pièce : on baisse son EXPOSITION (même facteur sur R, V, B = mêmes couleurs), jamais son contraste
        if hi > R["p99"] + 15: gain = (R["p99"] + 15) / hi; why.append(f"plus lumineux que la pièce (P99 {hi} > rush {R['p99']} + 15) : exposition x {gain:.2f}")
    elif FORCE:
        if abs(lo - R["p1"]) > 4: lo2 = R["p1"]; why.append(f"noirs {lo} -> rush {R['p1']}")
        if abs(hi - R["p99"]) > 25: hi2 = R["p99"]; why.append(f"blancs {hi} -> rush {R['p99']}")
    else:
        if hi > 235: hi2 = max(R["p99"], 220); why.append(f"blancs brûlés P99 {hi} > 235")
        if lo > R["p1"] + 8: lo2 = R["p1"] + 4; why.append(f"voile gris : noirs {lo} > rush {R['p1']} + 8")
    sigma = 0
    if ratio > 1.6:
        if obj or FORCE:
            sigma = 0.6 / scr; why.append(f"trop net (x {ratio:.1f} par rapport au rush) : flou {sigma:.1f} px")
        else: notes.append(f"plus net que le rush (x {ratio:.1f}) : gardé brut")
    gains = (1, 1, 1)
    dl = S["rb_lumiere"] - R["rb_lumiere"]
    if abs(dl) > 0.15:
        if COLOR:
            t = S["rb_lumiere"] - dl / 2; g = (t / S["rb_lumiere"]) ** 0.5; gains = (g, 1, 1 / g)
            why.append(f"lumière R/B {S['rb_lumiere']} -> {t:.2f} (rush {R['rb_lumiere']})")
        else: notes.append(f"lumière R/B {S['rb_lumiere']} contre rush {R['rb_lumiere']} (--color seulement pour un visuel généré)")
    if S["neon"] >= 0.5: notes.append(f"néon {S['neon']} % : visuel généré = cheap, à refaire ; vrai logo = normal")
    notes.append(f"P50 {S['p50']} (rush {R['p50']})")
    kind = "objet" if obj else "plan"
    print(f"{'OK  ' if not why else 'CALE'} {kind:5} {os.path.basename(p)} : " + (" ; ".join(why) if why else "colle au rush") + " · " + " · ".join(notes))
    if not why or not FIX: continue
    base, ext = os.path.splitext(p)
    out = f"{base}.cale{ext if ext.lower() in IMG else '.mp4'}"
    vf = chain(lo, hi, lo2, hi2, gain, gains, sigma)
    if p.lower().endswith(IMG):
        cmd = ["ffmpeg", "-y", "-v", "error", "-i", p, "-vf", vf + (",format=rgba" if ext.lower() == ".png" else ",format=rgb24"), "-frames:v", "1", out]
    else:
        cmd = ["ffmpeg", "-y", "-v", "error", "-i", p, "-vf", vf + ",format=yuv420p", "-an", "-c:v", "libx264", "-crf", "16", "-preset", "fast", out]
    subprocess.check_call(cmd)
    print(f"     -> {out}  (mettre ce fichier dans plan.json à la place de l'original)")
