"""Détoure le sujet (Robust Video Matting, ONNX, local) pour chaque chiffre et chaque mot géant du plan -> la tête passe devant.
  python3 matte.py plan.json
Lit plan.cam + plan.numbers + plan.bigwords, écrit fg_<k>.webm / fgw_<k>.webm (VP9 + transparence) à côté du plan et remplit fg / fgStart / fgEnd.
Un détourage déjà fait sur la même plage est réutilisé (pas recalculé).
Chaque plage démarre 0.5 s plus tôt pour chauffer le modèle (contour stable) ; ces images ne sont pas écrites.
"""
import json, os, subprocess, sys
import numpy as np
import onnxruntime as ort

plan_p = sys.argv[1]
d = os.path.dirname(os.path.abspath(plan_p))
plan = json.load(open(plan_p))
model = os.path.expanduser("~/.cache/supermonteur/rvm_mobilenetv3_fp32.onnx")
sess = ort.InferenceSession(model, providers=["CPUExecutionProvider"])
W, H, FPS, WARM = 1080, 1920, 30, 0.5
src = os.path.join(d, plan["cam"])

# vidéo avec titre-question : pas de mot géant (règle), donc rien à détourer pour eux
jobs = [(n, f"fg_{k}.webm") for k, n in enumerate(plan.get("numbers", []))] + ([] if plan.get("title") else [(w, f"fgw_{k}.webm") for k, w in enumerate(plan.get("bigwords", []))])
for n, name in jobs:
    a, b = max(0.0, n["start"] - 0.1), n["end"] + 0.05
    a0 = max(0.0, a - WARM)
    if n.get("fg") == name and os.path.exists(os.path.join(d, name)) and abs(n.get("fgStart", -1) - round(a, 3)) < 1e-3 and abs(n.get("fgEnd", -1) - round(b, 3)) < 1e-3:
        print(f"{name}  déjà fait ({n['text']})")
        continue
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{a0:.3f}", "-i", src, "-t", f"{b - a0:.3f}",
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "6M",
                            "-auto-alt-ref", "0", os.path.join(d, name)], stdin=subprocess.PIPE)
    rec = [np.zeros([1, 1, 1, 1], np.float32)] * 4
    ratio = np.array([0.25], np.float32)
    i = 0
    while True:
        buf = dec.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        rgb = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        x = (rgb.astype(np.float32) / 255).transpose(2, 0, 1)[None]
        _, pha, *rec = sess.run(None, {"src": x, "r1i": rec[0], "r2i": rec[1], "r3i": rec[2], "r4i": rec[3], "downsample_ratio": ratio})
        if a0 + i / FPS >= a - 1e-3:
            enc.stdin.write(np.dstack([rgb, (np.clip(pha[0, 0], 0, 1) * 255).astype(np.uint8)]).tobytes())
        i += 1
    enc.stdin.close(); enc.wait(); dec.wait()
    n.update(fg=name, fgStart=round(a, 3), fgEnd=round(b, 3))
    print(f"{name}  {a:.2f}-{b:.2f}s  ({n['text']})")
json.dump(plan, open(plan_p, "w"), ensure_ascii=False, indent=1)
