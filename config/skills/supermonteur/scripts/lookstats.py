"""Mesure le « look » d'une rush, d'un b-roll ou d'une image (experts colorimétrie : mesurer AVANT de toucher).
  python3 lookstats.py clip.mp4 [--json look.json] [--face]
Sort : noirs (P1), médiane (P50), hautes lumières (P95, P99) de la luminance 0-255, couleur de la lumière (rouge/bleu des
hautes lumières), % de pixels « néon », netteté, palette de 5 couleurs ; avec --face : joue, yeux et visage dans le cadre.
Bornes (Darren Mostyn, Cullen Kelly ; seuils à tester) : P1 entre 1 et 8 (noirs ni bouchés ni relevés), P99 <= 235, néon < 0,5 %.
Elles valent pour la CAM et les visuels ajoutés, pas pour un final (vignettage, cartons et vrais logos faussent P1 et néon).
Cadre : une rush FILMÉE serré = yeux ~35 %, visage ~33 % de la largeur ; une rush filmée large = yeux ~48 %, visage ~25 %. Un monteur humain NE recadre PAS : la différence vient du tournage.
Utilisé aussi comme module par match_look.py, univers_check.py et score.py.
"""
import json, os, subprocess, sys
import numpy as np

SK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = (".png", ".jpg", ".jpeg", ".webp")
REF = {"yeux_y": 35.3, "visage_x": 49.1, "visage_largeur": 33.4}   # repère : rush filmée serré, mesurée sur des reels pros


def _size(path):
    s = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_streams",
                                            "-show_entries", "format=duration", "-of", "json", path]))
    st = s["streams"][0]; w, h = st["width"], st["height"]
    # téléphone filmé debout = fichier 3840x2160 + rotation 90 : ffmpeg tourne l'image au décodage, donc on raisonne en taille AFFICHÉE
    if any(abs(int(d.get("rotation", 0))) % 180 == 90 for d in st.get("side_data_list", [])): w, h = h, w
    return w, h, float(s.get("format", {}).get("duration") or 0)


def frames(path, n=10, t0=0.0, t1=None, long_side=480):
    """Images RGBA (uint8) : 1 pour une image, n réparties entre t0 et t1 pour une vidéo. Taille réduite, proportions gardées."""
    w, h, dur = _size(path)
    k = long_side / max(w, h); W, H = max(2, int(w * k) // 2 * 2), max(2, int(h * k) // 2 * 2)
    def grab(extra):
        raw = subprocess.check_output(["ffmpeg", "-v", "error", *extra, "-i", path, "-frames:v", "1", "-vf", f"scale={W}:{H}",
                                       "-f", "rawvideo", "-pix_fmt", "rgba", "-"])
        return np.frombuffer(raw, np.uint8).reshape(H, W, 4)
    if path.lower().endswith(IMG) or dur <= 0:
        return [grab([])]
    t1 = min(t1 if t1 is not None else dur, dur - 0.05)
    return [grab(["-ss", f"{t0 + (t1 - t0) * (i + 0.5) / n:.3f}"]) for i in range(n)]


def _lab(rgb):
    c = rgb / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    xyz = c @ np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]).T
    xyz /= np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[:, 1] - 16, 500 * (f[:, 0] - f[:, 1]), 200 * (f[:, 1] - f[:, 2])], 1)


def palette(rgb, k=5, seed=0):
    """k-means (Lab) sur un échantillon : [(hex, part %, lab)], la plus présente d'abord."""
    rng = np.random.default_rng(seed)
    px = rgb[rng.choice(len(rgb), min(5000, len(rgb)), replace=False)]
    lab = _lab(px); cen = lab[rng.choice(len(lab), k, replace=False)]
    for _ in range(15):
        lbl = ((lab[:, None] - cen[None]) ** 2).sum(2).argmin(1)
        cen = np.array([lab[lbl == j].mean(0) if (lbl == j).any() else cen[j] for j in range(k)])
    out = []
    for j in np.argsort(-np.bincount(lbl, minlength=k)):
        m = px[lbl == j].mean(0) if (lbl == j).any() else np.zeros(3)
        out.append(("#%02x%02x%02x" % tuple(int(v) for v in m), round(100 * (lbl == j).mean(), 1), cen[j].round(1).tolist()))
    return out


def sharp(fr):
    """Netteté = variance du laplacien de la luminance (à comparer entre 2 fichiers mesurés à la même taille)."""
    v = []
    for f in fr:
        y = f[..., :3].astype(np.float32) @ np.array([0.2126, 0.7152, 0.0722], np.float32)
        lap = -4 * y[1:-1, 1:-1] + y[:-2, 1:-1] + y[2:, 1:-1] + y[1:-1, :-2] + y[1:-1, 2:]
        al = f[..., 3] > 200   # intérieur seulement : pas les bords d'un PNG détouré (le contour net fausserait tout)
        a = al[1:-1, 1:-1] & al[:-2, 1:-1] & al[2:, 1:-1] & al[1:-1, :-2] & al[1:-1, 2:]
        if a.sum() > 50: v.append(float(lap[a].var()))
    return round(float(np.median(v)), 1) if v else None


def stats(fr):
    px = np.concatenate([f.reshape(-1, 4) for f in fr])
    alpha = (px[:, 3] < 128).mean()
    rgb = px[px[:, 3] >= 128][:, :3].astype(np.float32)
    y = rgb @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    mx, mn = rgb.max(1), rgb.min(1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    hi = rgb[y >= np.percentile(y, 90)]
    return {
        "p1": round(float(np.percentile(y, 1)), 1), "p50": round(float(np.percentile(y, 50)), 1),
        "p95": round(float(np.percentile(y, 95)), 1), "p99": round(float(np.percentile(y, 99)), 1),
        "rb": round(float(rgb[:, 0].mean() / max(rgb[:, 2].mean(), 1)), 3),
        "rb_lumiere": round(float(hi[:, 0].mean() / max(hi[:, 2].mean(), 1)), 3),
        "neon": round(float(100 * ((sat > 0.9) & (mx / 255 > 0.8)).mean()), 3),
        "nettete": sharp(fr), "transparent": round(float(100 * alpha), 1),
        "palette": palette(rgb),
    }


def face(path, n=12, t0=0.0, t1=None):
    """Yeux (% hauteur), centre du visage (% largeur), largeur du visage (%), luminance de la joue, sur n images."""
    import mediapipe as mp
    from mediapipe.tasks.python import vision, BaseOptions
    det = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=os.path.join(SK, "models", "face_landmarker.task"))))
    res = []
    fr = frames(path, n, t0, t1, long_side=960)
    for f in fr:
        rgb = np.ascontiguousarray(f[..., :3]); H, W = rgb.shape[:2]
        r = det.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb))
        if not r.face_landmarks: continue
        L = r.face_landmarks[0]
        cheek = []
        for i in (50, 280):
            cx, cy = int(L[i].x * W), int(L[i].y * H)
            p = rgb[max(0, cy - 4):cy + 5, max(0, cx - 4):cx + 5].reshape(-1, 3).astype(np.float32)
            if len(p): cheek.append(float((p @ np.array([0.2126, 0.7152, 0.0722])).mean()))
        res.append((100 * (L[33].y + L[263].y) / 2, 100 * L[1].x, 100 * abs(L[454].x - L[234].x), np.mean(cheek) if cheek else np.nan))
    if not res: return {"visage_vu": 0}
    a = np.array(res)
    return {"visage_vu": round(100 * len(res) / len(fr)), "yeux_y": round(float(np.median(a[:, 0])), 1),
            "yeux_dans_30_40": round(float(100 * ((a[:, 0] >= 30) & (a[:, 0] <= 40)).mean())),
            "visage_x": round(float(np.median(a[:, 1])), 1), "visage_largeur": round(float(np.median(a[:, 2])), 1),
            "joue": round(float(np.nanmedian(a[:, 3])), 1)}


def verdicts(s):
    v = []
    if not (1 <= s["p1"] <= 8): v.append(f"noirs P1 {s['p1']} hors 1-8 ({'relevés : voile gris' if s['p1'] > 8 else 'bouchés'})")
    if s["p99"] > 235: v.append(f"hautes lumières P99 {s['p99']} > 235 (blancs brûlés)")
    if s["neon"] >= 0.5: v.append(f"néon {s['neon']} % >= 0,5 % (cheap)")
    return v


def measure(path, with_face=False):
    s = stats(frames(path))
    if with_face and not path.lower().endswith(IMG): s.update(face(path))
    return s


if __name__ == "__main__":
    p = sys.argv[1]
    s = measure(p, "--face" in sys.argv)
    if "--json" in sys.argv: json.dump(s, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1, ensure_ascii=False)
    print(f"{os.path.basename(p)} : P1 {s['p1']} · P50 {s['p50']} · P95 {s['p95']} · P99 {s['p99']} (bornes : P1 1-8, P99 <= 235)")
    print(f"  lumière R/B {s['rb_lumiere']} ({'chaude' if s['rb_lumiere'] > 1.08 else 'froide' if s['rb_lumiere'] < 0.92 else 'neutre'}) · néon {s['neon']} % · netteté {s['nettete']}")
    print("  palette : " + "  ".join(f"{h} {pc}%" for h, pc, _ in s["palette"]))
    if "yeux_y" in s:
        print(f"  visage vu {s['visage_vu']} % · yeux à {s['yeux_y']} % ({s['yeux_dans_30_40']} % des images entre 30 et 40) · "
              f"visage à {s['visage_x']} % · largeur {s['visage_largeur']} % · joue {s['joue']}  (repère : tournage serré, yeux 35 %, largeur 33 %)")
    for x in verdicts(s): print("  !! " + x)
    if not verdicts(s): print("  OK : noirs, hautes lumières et néon dans les bornes")
