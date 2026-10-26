"""Famille « Toi + une source » (green screen, réaction, démonstration) : face cam + ce qu'on montre -> reel 9:16.
Face cam plein écran quand on parle (hook, conclusion, CTA) ; pendant chaque passage « source », la source remplit le fond et
La personne reste à l'écran selon la mise en page :
  greenscreen = la personne détourée en bas au centre devant la source (le format « green screen » d'Instagram / TikTok)
  split       = source en haut, visage en bas (comme la famille À plusieurs)
  bubble      = source plein écran + visage dans une bulle ronde en bas à gauche

  python3 source.py layout plan.json          # clip.mp4 9:16 + plan.cam / subY / subYAt / zoom:false
  python3 source.py compare plan.json A B     # 3 mises en page côte à côte de A à B s (choix au visuel)

plan.json -> "source": {"cam": "cam.mp4", "layout": "greenscreen", "items": [
     {"src": "src/page2.png", "start": 7.6, "end": 10.9, "y0": 0, "y1": 400},     # capture de page : défilement doux de y0 à y1 (px)
     {"src": "src/ecran.mp4", "start": 16.0, "end": 23.7, "from": 3.0}]}            # enregistrement d'écran / vidéo à commenter
  Une capture se fait avec une largeur de 1080 px (page mobile x2). Entre deux items = face cam.
  DÉMO FILMÉE (écran filmé au téléphone, pas de visage pendant la démo) : {"src": "@cam", "start", "end", "zoom": [cx, cy, z]}
     = zoom sur la zone utile de l'écran (cx, cy en px de la cam 1080x1920, z = 1,3 à 2,2), lu dans "cam_hd" (le rush 4K dérushée
     avec le même drop.json) pour rester net. Une coupe par étape (« tu cliques sur Ajouter » = zoom sur Ajouter).
  "solo": true = la source seule en plein écran, sans personne (carte « Le prompt » pendant un écran qui charge).
  REACT : {"src": "web/clip.mp4", "start", "end", "fit": true, "credit": "Source - Nom de la chaîne (YouTube)", "pre": "delogo=..."}
     = quelques secondes d'une vidéo du web (droit de courte citation : bref, commenté, source affichée), muette, en haut ; lui détouré devant.
  MOTION DESIGN : {"src": "@motion", "start", "end", "type": "dm", ...} = bloc animé HyperFrames (build.mjs) derrière lui, zéro visage.
  "push": 0.05 = image d'illustration (Higgsfield, fond BLANC/CLAIR, sujet en haut) qui avance doucement au lieu de défiler.
  greenscreen lit fg_0.webm (matte.py sur toute la cam) : lancé tout seul s'il manque (~10 s par seconde de vidéo).
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = (".jpg", ".jpeg", ".png", ".webp")
GS_SCALE, SEAM, ZOOM_SUBY = 0.66, 960, 1150
SUBY = {"greenscreen": 900, "split": SEAM - 34, "bubble": 880}


def dur_of(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]))


def src_chain(it, d, h=1920):
    """Entrée ffmpeg + filtre qui donne la source en 1080 x h pour la durée d (capture qui défile ou vidéo recadrée)."""
    if it["src"].lower().endswith(IMG) and it.get("push"):   # illustration (image Higgsfield) : poussée lente + ZOOM marqué
        # "punch": [moment 0-1, zoom final, cy 0-1] = vers ce moment, zoom rapide (0,35 s, smoothstep) vers le point cy (sujet en haut)
        # (v4) : zoom ou dézoom PROGRESSIF seulement, jamais de zoom brusque -> "punch" ignoré
        cy = it.get("cy", 0.3)
        pu = it["push"]
        z = f"(1+{pu}*t/{d:.3f})" if pu > 0 else f"(1+{-pu}*(1-t/{d:.3f}))"   # push < 0 = dézoom (part serré, s'élargit)
        return (["-loop", "1", "-framerate", "30", "-t", f"{d:.3f}", "-i", it["src"]],
                f"scale=1080:{h}:force_original_aspect_ratio=increase,crop=1080:{h},"
                f"scale=w='trunc(1080*{z}/2)*2':h='trunc({h}*{z}/2)*2':eval=frame:flags=lanczos,crop=1080:{h}:'(iw-1080)/2':'(ih-{h})*{cy}',fps=30")
    if it["src"].lower().endswith(IMG):
        y0, y1 = it.get("y0", 0), it.get("y1", it.get("y0", 0))
        ease = f"(1-cos(PI*min(t/{d:.3f},1)))/2"     # défilement doux, départ et arrivée lents
        return (["-loop", "1", "-framerate", "30", "-t", f"{d:.3f}", "-i", it["src"]],
                f"scale=1080:-2,crop=1080:{h}:0:'min(ih-{h},{y0}+({y1}-{y0})*{ease})',fps=30")
    fr = it.get("from", 0)
    if it.get("fit"):   # REACT : vidéo 16:9 du web en entier en haut, fond = elle-même floutée, source citée, SANS son
        top = it.get("top", 330)   # zones mortes Insta : crédit à top - 56 = 274 px, dans la zone sûre (avant 230 = crédit à 174 px)
        pre = it.get("pre", "")   # ex. "delogo=x=4:y=770:w=280:h=300," pour flouter une bulle webcam (pas de 2e visage)
        font = os.path.join(os.path.dirname(HERE), "fonts", "Montserrat.ttf")
        credit = it.get("credit", "")
        lab = (f",drawtext=fontfile={font}:text='{credit}':fontsize=28:fontcolor=white@0.9:x=(w-tw)/2:y={top - 56}:"
               f"shadowcolor=black@0.6:shadowx=0:shadowy=2") if credit else ""
        return (["-ss", f"{fr:.3f}", "-t", f"{d:.3f}", "-i", it["src"]],
                f"fps=30,{pre}split[rx0][rx1];[rx0]scale=1080:{h}:force_original_aspect_ratio=increase,crop=1080:{h},"
                f"drawbox=x=0:y=0:w=iw:h=ih:color={it.get('bg', '0x0E1220')}:t=fill[rxb];[rx1]scale=950:-2[rxf];[rxb][rxf]overlay=65:{top}{lab}")   # fond bleu nuit de la DA (le flou faisait une traînée orange) ; vidéo en 950 px entre les marges de 65 px (330-864 px, au-dessus des sous-titres à 900)
    if fr == "auto":   # passage le plus stable du B-roll (broll.py steady), comme en voix off
        import re
        o = subprocess.check_output(["python3", os.path.join(HERE, "broll.py"), "steady", it["src"], f"{d:.2f}"]).decode()
        fr = float(re.search(r"from ([\d.]+)s", o).group(1))
    zoom = ""
    if it.get("push"):   # B-roll derrière le détourage : poussée marquée pour garder le mouvement
        z = f"(1+{it['push']}*t/{d:.3f})"
        zoom = (f",scale=w='trunc(1080*{z}/2)*2':h='trunc({h}*{z}/2)*2':eval=frame:flags=lanczos,"
                f"crop=1080:{h}:'(iw-1080)/2':'(ih-{h})/2'")
    return (["-ss", f"{fr:.3f}", "-t", f"{d:.3f}", "-i", it["src"]],
            f"scale=1080:{h}:force_original_aspect_ratio=increase,crop=1080:{h},fps=30{zoom}")


def render_span(here, cam, fg, a, b, kind, it, layout, out, face_y, band_y=None, fg_off=0.0):
    d = b - a
    cam_in = ["-ss", f"{a:.3f}", "-t", f"{d:.3f}", "-i", cam]
    if kind == "face":
        cmd = cam_in + ["-filter_complex", "[0:v]fps=30,format=yuv420p[v]"]
    elif it and (it.get("src") == "@motion" or it.get("_html")):   # fond neutre : build.mjs dessine (motion / image / page) puis la personne devant
        cmd = ["-f", "lavfi", "-t", f"{d:.3f}", "-i", "color=c=0x0A0F1F:s=1080x1920:r=30", "-filter_complex", "[0:v]format=yuv420p[v]"]
    elif it and it.get("solo"):   # source seule plein écran (carte, capture) : pas de personne (ex. démo filmée sans visage)
        sin, sf = src_chain(it, d)
        cmd = sin + ["-filter_complex", f"[0:v]{sf},format=yuv420p[v]"]
    elif it and it.get("zoom"):
        # DÉMO FILMÉE (écran du Mac filmé au téléphone) : coupe franche sur la zone utile puis poussée lente de 5 %,
        # prise dans la version 4K (source.cam_hd) : zoom x2 = toujours net en 1080. "zoom": [cx, cy, z] en coordonnées 1080x1920.
        cx, cy, z = it["zoom"]; k = it["_k"]; n = max(1, round(d * 30))
        zz = f"({z}*(1+0.05*on/{n}))"
        cmd = ["-ss", f"{a:.3f}", "-t", f"{d:.3f}", "-i", it["_hd"], "-filter_complex",
               f"[0:v]fps=30,zoompan=z='{zz}':x='max(0,min(iw-iw/zoom,{cx * k:.0f}-iw/zoom/2))':"
               f"y='max(0,min(ih-ih/zoom,{cy * k:.0f}-ih/zoom/2))':d=1:s=1080x1920:fps=30,format=yuv420p[v]"]
    elif layout == "greenscreen":
        sin, sf = src_chain(it, d)
        fw, fh = int(1080 * GS_SCALE) // 2 * 2, int(1920 * GS_SCALE) // 2 * 2
        # PAS de -ss sur la vidéo détourée : un saut dans un webm VP9 + transparence rend la 1re image SANS alpha
        # (rectangle noir, à 36,45 s) -> on décode depuis le début et on coupe à l'image près (trim)
        cmd = sin + ["-c:v", "libvpx-vp9", "-i", fg, "-filter_complex",
                     f"[0:v]{sf}[bg];[1:v]trim=start={a - fg_off:.3f}:duration={d:.3f},setpts=PTS-STARTPTS,fps=30,"
                     f"scale={fw}:{fh}:flags=lanczos,format=yuva420p[p];"
                     # ombre douce sous la personne pour la poser dans la page (pas un détourage « collé »)
                     f"[p]split[p1][p2];[p2]alphaextract,boxblur=18:2,format=gray,lutyuv=y='val*0.55'[sh];"
                     f"color=black:s={fw}x{fh}:r=30,format=yuva420p[blk];[blk][sh]alphamerge[shadow];"
                     f"[bg][shadow]overlay=(W-w)/2+10:H-h+14:shortest=1[b2];[b2][p1]overlay=(W-w)/2:H-h:shortest=1,format=yuv420p[v]"]
    elif layout == "split":
        sin, sf = src_chain(it, d, 960)
        y = int(min(max(face_y - 0.42 * 960, 0), 1920 - 960))
        cmd = sin + cam_in + ["-filter_complex",
                              f"[0:v]{sf}[top];[1:v]fps=30,crop=1080:960:0:{y}[bot];[top][bot]vstack,"
                              f"drawbox=x=0:y={SEAM - 2}:w=1080:h=4:color=black@0.9:t=fill,format=yuv420p[v]"]
    else:   # bubble
        sin, sf = src_chain(it, d)
        r, y = 400, int(min(max(face_y - 0.45 * 1080, 0), 1920 - 1080))
        cmd = sin + cam_in + ["-filter_complex",
                              f"[0:v]{sf}[bg];[1:v]fps=30,crop=1080:1080:0:{y},scale={r}:{r},format=yuva420p,"
                              f"geq=lum='lum(X,Y)':cb='cb(X,Y)':cr='cr(X,Y)':a='255*lte(hypot(X-{r / 2},Y-{r / 2}),{r / 2 - 2})'[c];"
                              f"color=white:s={r + 12}x{r + 12}:r=30,format=yuva420p,geq=lum=255:cb=128:cr=128:"
                              f"a='255*lte(hypot(X-{(r + 12) / 2},Y-{(r + 12) / 2}),{(r + 12) / 2 - 1})'[ring];"
                              f"[bg][ring]overlay=65:{1440 - r - 6}:shortest=1[b1];[b1][c]overlay=71:{1440 - r}:shortest=1,format=yuv420p[v]"]   # bulle à 65 px du bord (zones mortes)
    if False and band_y is not None and kind != "face":   # bande retirée : traînée grise sur fond blanc -> ombre renforcée côté build.mjs (zone "light")
        fc = cmd[cmd.index("-filter_complex") + 1].replace("format=yuv420p[v]", "format=yuv420p[v0]")
        fc += (f";color=black:s=1080x1920:r=30,format=rgba,geq=r=0:g=0:b=0:a='115*exp(-pow((Y-{band_y + 45})/170,2))'[g];"
               f"[v0][g]overlay=0:0:shortest=1,format=yuv420p[v]")
        cmd[cmd.index("-filter_complex") + 1] = fc
    subprocess.run(["ffmpeg", "-v", "error", "-y", *cmd, "-map", "[v]", "-an", "-frames:v", str(round(d * 30)),
                    "-c:v", "libx264", "-crf", "16", "-preset", "fast", out], check=True)


def spans_of(S, total):
    items = sorted(S["items"], key=lambda x: x["start"])
    sp, t = [], 0.0
    for it in items:
        if 0 < it["start"] - t < 0.5 and sp:   # trou < 0,5 s entre deux sources = flash du visage : le passage d'avant le comble
            a0, _, k0, i0 = sp[-1]; sp[-1] = (a0, it["start"], k0, i0); t = it["start"]
        if it["start"] - t > 0.05: sp.append((t, it["start"], "face", None))
        sp.append((max(t, it["start"]), min(it["end"], total), "src", it)); t = min(it["end"], total)
    if total - t > 0.05: sp.append((t, total, "face", None))
    return sp


def prep(here, P, lay):
    S = P["source"]
    cam = os.path.join(here, S["cam"])
    total = dur_of(cam)
    fg = os.path.join(here, S.get("fg", "fg_0.webm"))
    gs = [it for it in S["items"] if not it.get("zoom") and not it.get("solo")]   # (les blocs @motion en ont besoin aussi)
    fg_off = 0.0
    if lay == "greenscreen" and gs:   # détourage seulement sur la plage des passages green screen (ex. ouverture d'une démo)
        mp = os.path.join(here, "matte_plan.json")
        a, b = round(min(it["start"] for it in gs), 3), round(min(max(it["end"] for it in gs), total - 0.06), 3)
        old = json.load(open(mp))["numbers"][0] if os.path.exists(mp) else {}
        if not (os.path.exists(fg) and old.get("fgStart", old.get("start", 9e9)) <= a + 0.11 and old.get("fgEnd", old.get("end", -1)) >= b - 0.06):
            json.dump({"cam": S["cam"], "numbers": [{"text": "cam", "start": a, "end": b}]}, open(mp, "w"))
            print(f"détourage de {a:.1f} à {b:.1f} s (~{(b - a) * 10 / 60:.0f} min)…")
            subprocess.run(["python3", os.path.join(HERE, "matte.py"), mp], check=True)
        n = json.load(open(mp))["numbers"][0]
        fg_off = n.get("fgStart", n.get("start", 0.0))
    face_y = subzone_face(cam)
    return cam, fg, total, face_y, fg_off


def subzone_face(cam):
    """Hauteur des yeux (px) dans la cam, pour cadrer le visage en split / bulle."""
    import numpy as np, mediapipe as mp
    from mediapipe.tasks.python import vision, BaseOptions
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", cam, "-vf", "fps=1,scale=540:960", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
    fr = np.frombuffer(raw, np.uint8).reshape(-1, 960, 540, 3)
    det = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=os.path.join(os.path.dirname(HERE), "models", "face_landmarker.task"))))
    ys = [np.mean([p.y for p in r.face_landmarks[0]]) * 1920 for f in fr
          if (r := det.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(f)))).face_landmarks]
    return float(np.median(ys)) if ys else 800.0


def layout(plan_p, layout_override=None, a0=None, b0=None, out_name="clip.mp4", write_plan=True):
    here = os.path.dirname(os.path.abspath(plan_p))
    P = json.load(open(plan_p))
    S = P["source"]
    lay = layout_override or S.get("layout", "greenscreen")
    cam, fg, total, face_y, fg_off = prep(here, P, lay)
    sp = spans_of(S, total)
    suby = dict(SUBY)
    # green screen : la tête détourée commence vers 1920 - h + 0,66 x (yeux - 260) ; texte (et mot fort 132 px) au-dessus
    suby["greenscreen"] = int(max(560, 1920 - int(1920 * GS_SCALE) + GS_SCALE * (face_y - 260) - 200))
    if a0 is not None:
        sp = [(max(a, a0), min(b, b0), k, it) for a, b, k, it in sp if b > a0 and a < b0]
    os.makedirs(os.path.join(here, "src_parts"), exist_ok=True)
    parts = []
    for i, (a, b, k, it) in enumerate(sp):
        it2 = dict(it) if it else None
        if it2 and a0 is not None and it2["src"].lower().endswith(IMG):   # extrait : le défilement reprend au bon endroit
            full = it["end"] - it["start"]; y0, y1 = it.get("y0", 0), it.get("y1", it.get("y0", 0))
            import math
            e = lambda t: (1 - math.cos(math.pi * min(t / full, 1))) / 2
            it2["y0"], it2["y1"] = y0 + (y1 - y0) * e(a - it["start"]), y0 + (y1 - y0) * e(b - it["start"])
        if it2 and not it2["src"].lower().endswith(IMG) and a0 is not None: it2["from"] = it.get("from", 0) + (a - it["start"])
        if it2 and lay == "greenscreen" and it2["src"].lower().endswith(IMG) and not it2.get("solo"):
            it2["_html"] = True   # défilement / zoom dans HyperFrames : ffmpeg bouge au pixel entier = saccades (« pas fluide »)
        if it2 and it2.get("zoom"):
            it2["_hd"] = os.path.join(here, S.get("cam_hd", S["cam"]))
            it2["_k"] = int(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width",
                                                     "-of", "csv=p=0", it2["_hd"]]).decode().split()[0]) / 1080
        out = os.path.join(here, "src_parts", f"{lay}_{i:02d}.mp4")
        render_span(here, cam, fg, a, b, k, it2, lay, out, face_y, ZOOM_SUBY if it2 and (it2.get("zoom") or it2.get("solo")) else suby[lay], fg_off)   # bande pour toutes les mises en page : la jonction du split passe aussi sur la page
        parts.append(out)
    lst = os.path.join(here, "src_parts", f"{lay}.txt")
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    start, end = (a0 or 0.0), (b0 or total)
    clip = os.path.join(here, out_name)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-ss", f"{start:.3f}", "-t", f"{end - start:.3f}",
                    "-i", cam, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "16", "-r", "30", "-c:a", "aac", "-b:a", "192k",
                    "-t", f"{end - start:.3f}", clip], check=True)
    if write_plan:
        mo = []
        html = lambda it: it and (it.get("src") == "@motion" or (lay == "greenscreen" and it["src"].lower().endswith(IMG) and not it.get("solo")))
        for k, (a, b, kd, it) in enumerate([x for x in sp if html(x[3])]):
            name = f"mo_fg_{k}.webm"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-c:v", "libvpx-vp9", "-i", fg, "-vf",
                            f"trim=start={a - fg_off:.3f}:duration={b - a:.3f},setpts=PTS-STARTPTS,fps=30", "-c:v", "libvpx-vp9",
                            "-pix_fmt", "yuva420p", "-b:v", "6M", "-auto-alt-ref", "0", "-deadline", "realtime", "-cpu-used", "8", "-row-mt", "1",
                            "-an", os.path.join(here, name)], check=True)   # VP9 « realtime » : 10 segments en ~1 min au lieu de 10+
            blk = {k2: v for k2, v in it.items() if k2 != "src"} if it["src"] == "@motion" else dict(it, type="img")
            mo.append(dict(blk, start=round(a, 3), end=round(b, 3), fg=name, scale=GS_SCALE))
        P["motion"] = mo
        face_sub = int(subprocess.check_output(["python3", os.path.join(HERE, "subzone.py"), cam]).decode().strip().splitlines()[-1])
        P["cam"], P["zoom"], P["subY"] = out_name, False, face_sub
        P["subYAt"] = [{"start": round(a, 3), "end": round(b, 3), "y": face_sub if k == "face" else (ZOOM_SUBY if it and (it.get("zoom") or it.get("solo")) else suby[lay]),
                         **({"light": True} if k != "face" and not (it and it.get("src") == "@motion") else {})} for a, b, k, it in sp]
        P["source"]["spans"] = [[round(a, 3), round(b, 3), k] for a, b, k, _ in sp]
        json.dump(P, open(plan_p, "w"), ensure_ascii=False, indent=1)
        print(f"{out_name} : {total:.1f} s · {lay} · " + " | ".join(f"{k} {a:.1f}-{b:.1f}" for a, b, k, _ in sp))
        print(f"sous-titres : face y={face_sub}, source y={suby[lay]}")
    return clip


def compare(plan_p, a, b):
    here = os.path.dirname(os.path.abspath(plan_p))
    outs = [layout(plan_p, lay, a, b, f"cmp_{lay}.mp4", False) for lay in ("greenscreen", "split", "bubble")]
    font = os.path.join(os.path.dirname(HERE), "fonts", "Montserrat.ttf")
    lab = lambda t: f"drawtext=fontfile={font}:text='{t}':fontsize=60:fontcolor=white:box=1:boxcolor=0x0b1a33@0.85:boxborderw=22:x=(w-tw)/2:y=60"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", outs[0], "-i", outs[1], "-i", outs[2], "-filter_complex",
                    f"[0:v]{lab('A · GREEN SCREEN')}[x];[1:v]{lab('B · SPLIT')}[y];[2:v]{lab('C · BULLE')}[z];"
                    "[x][y][z]hstack=3,pad=iw+60:ih:30:0:color=white,scale=1620:-2[v]",
                    "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac",
                    os.path.join(here, "comparatif_mises_en_page.mp4")], check=True)
    print("comparatif_mises_en_page.mp4")


if __name__ == "__main__":
    c = sys.argv[1:2]
    if c == ["layout"]: layout(sys.argv[2])
    elif c == ["compare"]: compare(sys.argv[2], float(sys.argv[3]), float(sys.argv[4]))
    else: sys.exit(__doc__)
