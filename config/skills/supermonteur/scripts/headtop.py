"""Haut de la tête (cheveux compris) sur une plage, pour poser le mot géant DERRIÈRE la tête .
  python3 headtop.py clip.mp4 START END   -> imprime le y (px, 1080x1920) du haut des cheveux
MediaPipe : front (point 10) médian - 0,45 x hauteur du visage (exemple mesuré : front 850, visage 322, cheveux ≈ 705).
Avant, le mot était toujours posé à 170 px : sur un cadrage plus large il flottait au-dessus de la tête, sans passer derrière.
"""
import os, subprocess, sys
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions

src, t0, t1 = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
MOD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "face_landmarker.task")
W, H = 540, 960
raw = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", str(t0), "-t", str(max(t1 - t0, 0.2)), "-i", src,
                               "-vf", f"fps=6,scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
det = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MOD), running_mode=vision.RunningMode.IMAGE))
top, chin = [], []
for f in fr:
    r = det.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(f)))
    if r.face_landmarks:
        L = r.face_landmarks[0]; top.append(L[10].y * 1920); chin.append(L[152].y * 1920)
if not top: sys.exit("pas de visage")
y = np.median(top) - 0.45 * np.median(np.array(chin) - np.array(top))
print(int(round(y)))
