"""Tracking : un objet suit un point du corps (le badge au bout du doigt quand la personne pointe : ce qui marche chez les monteurs pros).
  python3 track.py clip.mp4 START END --point index_tip --out track_badge.json
Points : index_tip (bout de l'index), thumb_tip, palm (paume), head_top (au-dessus de la tête),
         head_left / head_right (à côté de la tête, côté gauche / droit de l'écran), chin.
Sortie (coordonnées de clip.mp4, 1080x1920) : {"point", "samples": [{"t", "x", "y"}...]} à 15 i/s, lissé, trous comblés.
Dans plan.json : "inserts": [{"src", "start", "end", "track": "track_badge.json", "offset": [0, -140], "w": 300}]
Modèles MediaPipe (Google) dans ../models : hand_landmarker.task, face_landmarker.task.
"""
import json, os, subprocess, sys
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions

src, t0, t1 = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
point = sys.argv[sys.argv.index("--point") + 1] if "--point" in sys.argv else "index_tip"
out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "track.json"
side = sys.argv[sys.argv.index("--side") + 1] if "--side" in sys.argv else None   # left / right = main côté gauche / droit de l'écran
MOD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
FPS, W, H = 15, 540, 960   # analyse en demi-résolution, sorties remises en 1080x1920

raw = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", str(t0), "-t", str(t1 - t0), "-i", src,
                               "-vf", f"scale={W}:{H},fps={FPS}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
frames = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
hand = point in ("index_tip", "thumb_tip", "palm")
if hand:
    det = vision.HandLandmarker.create_from_options(vision.HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=os.path.join(MOD, "hand_landmarker.task")), num_hands=2,
        running_mode=vision.RunningMode.VIDEO))
else:
    det = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=os.path.join(MOD, "face_landmarker.task")),
        running_mode=vision.RunningMode.VIDEO))

pts = []
for k, f in enumerate(frames):
    r = det.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(f)), int(k * 1000 / FPS))
    p = None
    if hand and r.hand_landmarks:
        idx = {"index_tip": 8, "thumb_tip": 4, "palm": 9}[point]
        # 1re image : la main la plus haute (celle qui pointe / montre) ; ensuite TOUJOURS la même main (la plus proche
        # du point précédent), sinon l'objet saute d'une main à l'autre (bug : x 231 -> 745)
        last = next((q for q in reversed(pts) if q), None)
        cand = [(h[idx].x, h[idx].y) for h in r.hand_landmarks]
        if side: cand = [c for c in cand if (c[0] < 0.5) == (side == "left")] or []
        if not cand: pts.append(None); continue
        p = min(cand, key=lambda c: c[1]) if last is None else min(cand, key=lambda c: (c[0] - last[0]) ** 2 + (c[1] - last[1]) ** 2)
        if last is not None and ((p[0] - last[0]) ** 2 + (p[1] - last[1]) ** 2) ** .5 > 0.25: p = None   # la main suivie a disparu : on bouche le trou
    elif not hand and r.face_landmarks:
        f_ = r.face_landmarks[0]; top, chin, l, rr = f_[10], f_[152], f_[234], f_[454]
        fh = chin.y - top.y; fw = rr.x - l.x
        p = {"head_top": (top.x, top.y - 0.55 * fh), "chin": (chin.x, chin.y + 0.1 * fh),
             "head_left": (l.x - 0.55 * fw, (top.y + chin.y) / 2), "head_right": (rr.x + 0.55 * fw, (top.y + chin.y) / 2)}[point]
    pts.append(p)

ok = [i for i, p in enumerate(pts) if p]
if not ok: sys.exit(f"rien détecté pour {point} entre {t0} et {t1} s")
xs = np.interp(range(len(pts)), ok, [pts[i][0] for i in ok]); ys = np.interp(range(len(pts)), ok, [pts[i][1] for i in ok])
# lissage (moyenne glissante 5 images = 1/3 s) : suit le geste sans trembler
ker = np.ones(5) / 5
xs = np.convolve(np.pad(xs, 2, mode="edge"), ker, "valid"); ys = np.convolve(np.pad(ys, 2, mode="edge"), ker, "valid")
samples = [{"t": round(t0 + i / FPS, 3), "x": round(float(x) * 1080, 1), "y": round(float(y) * 1920, 1)} for i, (x, y) in enumerate(zip(xs, ys))]
json.dump({"point": point, "fps": FPS, "detected": round(len(ok) / len(pts), 2), "samples": samples}, open(out, "w"))
print(f"{out} : {point} détecté sur {len(ok)}/{len(pts)} images ({t0}-{t1} s)")
