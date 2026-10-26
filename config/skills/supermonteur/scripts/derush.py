"""Dérush : coupe les silences, les respirations et les répétitions, sans jamais couper un mot ni une phrase en deux.
  python3 derush.py clip.mp4 words.json cut.mp4 [--drop drop.json] [--pause 57]
--pause i = indice (dans words.json source) du mot PUNCHLINE qui aura LE silence du reel : on GARDE la vraie pause avant lui
(jusqu'à 0,9 s) au lieu de la resserrer. Sans pause dans le rush, pas de silence possible (le dire à l'utilisateur : marquer un temps avant la phrase choc au tournage).
drop.json = [[i, j], ...] plages d'indices de mots à supprimer (répétitions, phrases ratées : on garde la DERNIÈRE prise).
On ne coupe que dans les blancs entre deux mots :
  - fin de phrase (ponctuation) : blanc + respiration supprimés, on garde 0.06 s avant le mot suivant
  - milieu de phrase : le blanc est seulement resserré à 0.15 s (la phrase reste d'un seul tenant)
Écrit aussi cut.segments.json (plages gardées dans la source, dans l'ordre).
"""
import json, math, subprocess, sys

src, words_p, out = sys.argv[1:4]
drop = json.load(open(sys.argv[sys.argv.index("--drop") + 1])) if "--drop" in sys.argv else []
W = json.load(open(words_p))["words"]
dead = {k for a, b in drop for k in range(a, b + 1)}
PAUSE = int(sys.argv[sys.argv.index("--pause") + 1]) if "--pause" in sys.argv else None
keep = [w for i, w in enumerate(W) if i not in dead]
PRE, POST, MID, MAXGAP = 0.06, 0.12, 0.15, 0.25

segs = []
for i, w in enumerate(keep):
    s, e = w["start"] - PRE, w["end"] + POST
    if segs:
        prev = keep[i - 1]
        gap = w["start"] - prev["end"]
        end_of_sentence = prev["text"].rstrip()[-1:] in ".!?,"
        jumped = W.index(w) != W.index(prev) + 1          # une répétition a sauté entre les deux
        if W.index(w) == PAUSE and not jumped:            # LE silence du reel : vraie pause gardée (max 0,9 s)
            if gap <= 0.9: segs[-1][1] = e; continue
            segs[-1][1] = prev["end"] + 0.45; s = w["start"] - 0.45
            segs.append([s, e]); continue
        if not jumped and gap <= MAXGAP:
            segs[-1][1] = e; continue                    # parole continue
        if not jumped and not end_of_sentence:
            segs[-1][1] = prev["end"] + MID / 2          # milieu de phrase : on resserre seulement
            s = w["start"] - MID / 2
        else:
            segs[-1][1] = min(segs[-1][1], w["start"] - 0.01)
    segs.append([max(0.0, s), e])
segs = [[a, b] for a, b in segs if b - a > 0.05]
# Entrée et sortie (sinon « ça coupe sec » au hook et à la fin) : avant, la vidéo démarrait 0,06 s
# avant le 1er mot et s'arrêtait 0,12 s après le dernier. On garde LEAD avant le 1er mot (assez court pour ne pas garder
# la respiration) et TAIL après le dernier (la phrase retombe, la musique peut finir). --lead / --tail pour régler.
LEAD = float(sys.argv[sys.argv.index("--lead") + 1]) if "--lead" in sys.argv else 0.15
TAIL = float(sys.argv[sys.argv.index("--tail") + 1]) if "--tail" in sys.argv else 0.6
if segs:
    segs[0][0] = max(0.0, min(segs[0][0], keep[0]["start"] - LEAD))
    segs[-1][1] = max(segs[-1][1], keep[-1]["end"] + TAIL)
# Synchro image/son : chaque plage est calée sur la grille des images (début arrondi en dessous, fin au-dessus).
# Avant, l'image se coupait à l'image près et le son ailleurs : sur 40 coupes, la bouche pouvait se décaler.
# Plages qui se touchent ou se chevauchent = fusionnées (sinon le fondu anti-clic doublerait le volume au raccord).
FPS = eval(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate",
                                    "-of", "csv=p=0", src]).decode().strip())
snapped = []
for a, b in segs:
    a, b = math.floor(a * FPS + 1e-6) / FPS, math.ceil(b * FPS - 1e-6) / FPS
    if snapped and a <= snapped[-1][1] + 1e-6: snapped[-1][1] = max(snapped[-1][1], b)
    else: snapped.append([a, b])
segs = [[round(a, 4), round(b, 4)] for a, b in snapped]
HALF = 0.5 / FPS   # image : on prend les images de a à b exclu -> exactement (b - a) s, comme le son

vexpr = "+".join(f"between(t,{a - HALF:.4f},{b - HALF:.4f})" for a, b in segs)   # demi-image de marge : insensible aux arrondis
expr = "+".join(f"between(t,{a},{b})" for a, b in segs)
# Anti-clic (Vashi Nedomansky) : micro-fondu au début et à la fin de chaque plage gardée, sinon chaque coupe
# peut claquer. 0,03 s : tient dans la marge avant le mot (PRE 0,06 s), ne mange jamais une syllabe.
# asetnsamples=64 : trames audio de 1,3 ms, sinon le fondu (et la coupe) se calent sur des trames de 21 ms.
AFADE = 0.03
fade = "+".join(f"clip(min((t-{a})/{AFADE},({b}-t)/{AFADE}),0,1)" for a, b in segs)
subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-i", src,
    "-vf", f"select='{vexpr}',setpts=N/FRAME_RATE/TB",
    "-af", f"asetnsamples=n=64,volume='{fade}':eval=frame,aselect='{expr}',asetpts=N/SR/TB",
    "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-c:a", "aac", "-b:a", "192k", out])
json.dump(segs, open(out.rsplit(".", 1)[0] + ".segments.json", "w"))
# Mots recalés sur la version coupée : <out>.words.json = la transcription du rush (souvent meilleure que celle
# refaite sur le montage coupé, qui a perdu son contexte) avec les temps de la version coupée.
off, moved = 0.0, []
for a, b in segs:
    for i, w in enumerate(W):
        if i not in dead and a <= w["start"] < b:
            moved.append({**w, "start": round(off + w["start"] - a, 3), "end": round(off + min(w["end"], b) - a, 3)})
    off += b - a
json.dump({"words": moved}, open(out.rsplit(".", 1)[0] + ".words.json", "w"), ensure_ascii=False)
before = W[-1]["end"]; after = sum(b - a for a, b in segs)
print(f"{len(segs)} plages · {before:.1f}s -> {after:.1f}s · {len(dead)} mots retirés -> {out}")
