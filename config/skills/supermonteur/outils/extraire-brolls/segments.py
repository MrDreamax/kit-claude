"""Passages stables 3-10 s -> vignettes + visages + dédoublonnage dans un même rush + planches.
Usage : python3 segments.py <dossier_rushs> <dossier_ana> <dossier_sortie>"""
import os, sys, json, math, subprocess
import numpy as np, cv2
SKILL = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SRC, ANA, OUT = sys.argv[1:4]
FPS, SHAKE, PEAK = 15, 1.2, 6.0          # mêmes seuils que scripts/broll.py
MIN_S, MAX_S, TRIM = 3.0, 10.0, 3        # durées en s, rognage en images à 15 i/s
LUM_MIN = float(os.environ.get("LUM_MIN", 18))
SIM = float(os.environ.get("SIM", 0.80))
os.makedirs(f"{OUT}/thumbs", exist_ok=True); os.makedirs(f"{OUT}/sheets", exist_ok=True)

def runs(mask):
    i, n = 0, len(mask)
    while i < n:
        if mask[i]:
            j = i
            while j < n and mask[j]: j += 1
            yield i, j
            i = j
        else: i += 1

segs = []
for f in sorted(os.listdir(ANA)):
    if not f.endswith(".npz"): continue
    clip = f[:-4]; z = np.load(f"{ANA}/{f}"); d, lum, sharp = z["d"], z["lum"], z["sharp"]
    if len(d) < MIN_S * FPS: continue
    roll = np.convolve(d, np.ones(FPS) / FPS, "same")
    lum_t = np.minimum(lum[:-1], lum[1:])
    ok = (d <= PEAK) & (roll <= SHAKE) & (lum_t >= LUM_MIN)
    for a, b in runs(ok):
        a, b = a + TRIM, b - TRIM
        L = b - a
        if L < MIN_S * FPS: continue
        k = math.ceil(L / (MAX_S * FPS)); step = L / k
        for c in range(k):
            s, e = int(a + c * step), int(a + (c + 1) * step)
            w = d[s:e]
            segs.append(dict(clip=clip, start=round(s / FPS, 2), end=round(e / FPS, 2), dur=round((e - s) / FPS, 2),
                             shake=round(float(w.mean()), 2), peak=round(float(w.max()), 1),
                             sharp=round(float(sharp[s:e + 1].mean()), 1), lum=round(float(lum[s:e + 1].mean()), 1)))
print(len(segs), "passages stables bruts")

from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision
import mediapipe as mp
lm = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
    base_options=mpt.BaseOptions(model_asset_path=os.path.join(SKILL, "models", "face_landmarker.task")),
    num_faces=4, min_face_detection_confidence=0.3, min_face_presence_confidence=0.3))

for i, g in enumerate(segs):
    g["id"] = i
    t = f"{OUT}/thumbs/{i:04d}.jpg"
    if not os.path.exists(t):
        mid = (g["start"] + g["end"]) / 2
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{mid:.2f}", "-i", f"{SRC}/{g['clip']}", "-frames:v", "1",
                        "-vf", "scale=540:960", "-q:v", "3", t], check=True)
    im = cv2.imread(t); rgb = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    res = lm.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb)))
    faces = []
    for pts in res.face_landmarks:
        xs = [p.x for p in pts]; ys = [p.y for p in pts]
        faces.append([min(xs), min(ys), max(xs), max(ys)])
    faces.sort(key=lambda b: -(b[2] - b[0]) * (b[3] - b[1]))
    g["faces"] = [[round(v, 3) for v in b] for b in faces]
    g["face_h"] = round(faces[0][3] - faces[0][1], 3) if faces else 0
    small = cv2.resize(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), (18, 32), interpolation=cv2.INTER_AREA).astype(np.float32).ravel()
    g["_v"] = (small - small.mean()) / (small.std() + 1e-6)
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    h = cv2.calcHist([hsv], [0, 1], None, [16, 8], [0, 180, 0, 256]); g["_h"] = cv2.normalize(h, None).ravel()
    g["score"] = round(-g["shake"] - g["peak"] / 10 + 0.3 * math.log(g["sharp"] + 1) + (0.6 + 2 * g["face_h"] if faces else 0)
                       + 0.05 * g["dur"], 3)

# dédoublonnage dans un même rush : on garde 2 plans max par groupe de plans semblables
for clip in sorted({g["clip"] for g in segs}):
    cs = sorted([g for g in segs if g["clip"] == clip], key=lambda g: -g["score"]); groups = []
    for g in cs:
        for grp in groups:
            r = grp[0]
            sim = 0.5 * float(np.dot(g["_v"], r["_v"]) / len(g["_v"])) + 0.5 * float(cv2.compareHist(g["_h"], r["_h"], cv2.HISTCMP_CORREL))
            if sim >= SIM: grp.append(g); break
        else: groups.append([g])
    for gi, grp in enumerate(groups):
        for k, g in enumerate(grp): g["group"] = f"{clip}-{gi}"; g["kept"] = k < 2

kept = [g for g in segs if g["kept"]]
print(len(kept), "gardés après dédoublonnage par rush")

TW, TH, FH, COLS, ROWS = 144, 256, 120, 10, 4
for si in range(0, len(kept), COLS * ROWS):
    page = kept[si:si + COLS * ROWS]
    sheet = np.full(((TH + FH) * ROWS, TW * COLS, 3), 30, np.uint8)
    for k, g in enumerate(page):
        im = cv2.imread(f"{OUT}/thumbs/{g['id']:04d}.jpg"); x, y = (k % COLS) * TW, (k // COLS) * (TH + FH)
        sheet[y:y + TH, x:x + TW] = cv2.resize(im, (TW, TH), interpolation=cv2.INTER_AREA)
        if g["faces"]:
            b = g["faces"][0]; H_, W_ = im.shape[:2]; cx, cy = (b[0] + b[2]) / 2 * W_, (b[1] + b[3]) / 2 * H_
            s = max((b[2] - b[0]) * W_, (b[3] - b[1]) * H_) * 0.8
            x0, y0, x1, y1 = int(max(0, cx - s)), int(max(0, cy - s)), int(min(W_, cx + s)), int(min(H_, cy + s))
            sheet[y + TH:y + TH + FH, x + 12:x + 12 + FH] = cv2.resize(im[y0:y1, x0:x1], (FH, FH))
        cv2.putText(sheet, str(g["id"]), (x + 3, y + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 4)
        cv2.putText(sheet, str(g["id"]), (x + 3, y + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.rectangle(sheet, (x, y), (x + TW - 1, y + TH + FH - 1), (80, 80, 80), 1)
    cv2.imwrite(f"{OUT}/sheets/sheet_{si // (COLS * ROWS) + 1:02d}.jpg", sheet, [cv2.IMWRITE_JPEG_QUALITY, 80])

for g in segs: g.pop("_v"); g.pop("_h")
json.dump(segs, open(f"{OUT}/segments.json", "w"), indent=1)
print("planches :", math.ceil(len(kept) / (COLS * ROWS)))
