"""Famille « Sans visage » (voix off, B-roll + texte, objets, mèmes) : une voix + un plan par phrase -> reel 9:16.
La voix pilote, les images remplissent tout l'écran : 1 plan par idée (1-3,5 s), coupe franche sur la fin de phrase,
poussée lente sur chaque plan (jamais figé), B-rolls BRUTS et STABLES (broll.py steady), aucune tête qui parle.

  python3 voixoff.py build plan.json      # clip.mp4 9:16 (plans + voix) ; plan.cam / zoom:false / subY écrits tout seuls

plan.json -> "voixoff": {"voice": "voice.mp4", "beats": [{"src": "<chemin absolu .mp4/.mov ou image>", "from": "auto", "end": 1.6}, ...]}
  voice = la voix dérushée (vidéo ou audio) ; elle donne la durée.
  beats = les plans dans l'ordre : chacun commence où le précédent finit, "end" = fin du plan sur la voix (fin de phrase / de mot).
          Le dernier va jusqu'au bout de la voix. "from": "auto" = le passage le plus stable du fichier. Image = poussée lente.
          "push": 0.04 (défaut) = zoom de 1.00 à 1.04 pendant le plan ; 0 = plan fixe.
Sous-titres au centre-bas (y = 1150, pas de visage à éviter). Mots forts = plan.keywords comme d'habitude.
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = (".jpg", ".jpeg", ".png", ".webp")
SUBY = 1150


def dur_of(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]))


def build(plan_p):
    here = os.path.dirname(os.path.abspath(plan_p))
    P = json.load(open(plan_p))
    vo = P["voixoff"]
    voice = os.path.join(here, vo["voice"])
    total = dur_of(voice)
    beats, t = [], 0.0
    for k, b in enumerate(vo["beats"]):
        end = total if k == len(vo["beats"]) - 1 else min(b["end"], total)
        if end - t < 0.5: print(f"!! plan {k} trop court ({end - t:.2f} s) : fusionné avec le suivant"); continue
        beats.append(dict(b, start=round(t, 3), end=round(end, 3))); t = end
    os.makedirs(os.path.join(here, "vo"), exist_ok=True)
    parts = []
    for k, b in enumerate(beats):
        d, push = b["end"] - b["start"], b.get("push", 0.04)
        out = os.path.join(here, "vo", f"p{k:02d}.mp4")
        z = f"(1+{push}*t/{d:.3f})"   # poussée lente, centrée (scale recalculé à chaque image ; crop ne sait pas zoomer dans le temps)
        move = (f"scale=w='trunc(1080*{z}/2)*2':h='trunc(1920*{z}/2)*2':eval=frame:flags=lanczos,"
                f"crop=1080:1920:'(iw-1080)/2':'(ih-1920)/2'")
        if b["src"].lower().endswith(IMG):
            cmd = ["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", "30", "-t", f"{d:.3f}", "-i", b["src"],
                   "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,{move},fps=30,format=yuv420p"]
        else:
            fr = b.get("from", "auto")
            if fr == "auto":
                o = subprocess.check_output(["python3", os.path.join(HERE, "broll.py"), "steady", b["src"], f"{d:.2f}"]).decode()
                fr = float(re.search(r"from ([\d.]+)s", o).group(1))
                if "INSTABLE" in o: print(f"!! plan {k} instable : {os.path.basename(b['src'])} -> en choisir un autre")
            b["from"] = fr
            cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{fr:.3f}", "-t", f"{d:.3f}", "-i", b["src"],
                   "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,{move},format=yuv420p"]
        subprocess.run(cmd + ["-an", "-frames:v", str(round(d * 30)), "-c:v", "libx264", "-crf", "16", "-preset", "fast", out], check=True)
        got = dur_of(out)
        if got < d - 0.05: print(f"!! plan {k} : le fichier source est trop court ({got:.2f} s sur {d:.2f}) -> prendre un autre passage")
        parts.append(out)
        print(f"  {b['start']:6.2f}-{b['end']:6.2f}  {os.path.basename(b['src'])}" + (f"  (from {b['from']:.1f} s)" if "from" in b and not b["src"].lower().endswith(IMG) else ""))
    lst = os.path.join(here, "vo", "list.txt")
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    clip = os.path.join(here, "clip.mp4")
    # bande sombre fondue derrière les sous-titres (illisibles sur plage, resto, table claire). 40 % max au centre,
    # gaussienne de ~200 px : les plans restent bruts (aucun étalonnage), seule la zone du texte est assombrie. "band": 0 = sans.
    suby, band = P.get("subY", SUBY), vo.get("band", 0.4)
    vf = (f"[0:v]null[v]" if not band else
          f"color=black:s=1080x1920:r=30,format=rgba,geq=r=0:g=0:b=0:a='{255 * band:.0f}*exp(-pow((Y-{suby + 45})/200,2))'[g];"
          f"[0:v][g]overlay=0:0:shortest=1,format=yuv420p[v]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-i", voice, "-filter_complex", vf,
                    "-map", "[v]", "-map", "1:a", "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-r", "30",
                    "-c:a", "aac", "-b:a", "192k", "-t", f"{total:.3f}", clip], check=True)
    vo["beats"] = beats
    P["cam"], P["zoom"], P["subY"], P["brolls"] = "clip.mp4", False, P.get("subY", SUBY), []
    json.dump(P, open(plan_p, "w"), ensure_ascii=False, indent=1)
    print(f"clip.mp4 : {total:.1f} s, {len(beats)} plans (moyenne {total / len(beats):.1f} s), sous-titres y={P['subY']}")


if __name__ == "__main__":
    if sys.argv[1:2] == ["build"]: build(sys.argv[2])
    else: sys.exit(__doc__)
