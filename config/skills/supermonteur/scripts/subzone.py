"""Hauteur des sous-titres (Style Lab R1-R2, « au niveau du col du t-shirt, jamais sur le cou ni le menton »).
  python3 subzone.py clip.mp4            -> imprime le y (px, en 1080x1920) à mettre dans plan.json "subY"
Règle validée : haut du bloc ≈ 95 px sous le bas du col. Mesurée sur le visage (MediaPipe) pour suivre le cadrage :
  y = menton bas (90e centile, quand la tête descend le plus) + 0,41 x hauteur du visage   (exemple : 1177 + 0,41 x 322 = 1310)
Bornes 1100-1340 : en dessous de 1340, le mot fort seul (132 px) reste au-dessus de la zone cachée par l'appli (1479).
Pas de visage (plan sans face cam) : ancienne méthode, la bande la plus SOMBRE et la plus UNIE entre 55 et 80 % de la hauteur.
"""
import os, subprocess, sys
import numpy as np

src = sys.argv[1]
MOD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "face_landmarker.task")
K, LO, HI = 0.41, 1100, 1340


def by_face():
    import mediapipe as mp
    from mediapipe.tasks.python import vision, BaseOptions
    W, H = 540, 960
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", src, "-vf", f"fps=2,scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
    fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    det = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MOD), running_mode=vision.RunningMode.IMAGE))
    chin, face = [], []
    for f in fr:
        r = det.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(f)))
        if r.face_landmarks:
            L = r.face_landmarks[0]
            chin.append(L[152].y * 1920); face.append((L[152].y - L[10].y) * 1920)
    if len(chin) < 0.3 * len(fr): return None
    y = np.percentile(chin, 90) + K * np.median(face)
    print(f"sous-titres sous le col : menton {np.percentile(chin, 90):.0f} + 0,41 x visage {np.median(face):.0f} = {y:.0f}px", file=sys.stderr)
    return y


def by_contrast():
    W, H = 108, 192
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", src, "-vf", f"fps=2,scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "gray", "-"])
    f = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32)
    band, best = 11, None   # 11 px à 1/10 = 110 px
    for y in range(int(H * 0.55), int(H * 0.80) - band):
        zone = f[:, y:y + band, 15:W - 15]
        score = np.percentile(zone.mean(axis=(1, 2)), 90) + 0.6 * zone.std(axis=(1, 2)).mean()
        if best is None or score < best[0]: best = (score, y)
    print(f"pas de visage : zone la plus sombre et unie y={best[1] * 10}px", file=sys.stderr)
    return best[1] * 10


try:
    y = by_face()
except Exception as e:
    print(f"détection visage impossible ({e})", file=sys.stderr); y = None
if y is None: y = by_contrast()
y = int(round(min(max(y, LO), HI)))
if y == HI: print("attention : visage très proche, le texte peut toucher le cou (bloqué à 1340 pour rester hors de la zone de l'appli)", file=sys.stderr)
print(y)
