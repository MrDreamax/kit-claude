"""Mesure par image : tremblement (même méthode que scripts/broll.py shakes), luminosité, netteté.
Usage : python3 analyse.py <dossier_rushs> <dossier_sortie>"""
import os, sys, subprocess
import numpy as np
from multiprocessing import Pool

W, H, FPS = 270, 480, 15
SRC, OUT = sys.argv[1], sys.argv[2]
WIN = np.outer(np.hanning(H), np.hanning(W)).astype(np.float32)

def one(name):
    out = os.path.join(OUT, name + ".npz")
    if os.path.exists(out): return name, "deja"
    hw = ["-hwaccel", "videotoolbox"] if sys.platform == "darwin" else []   # accélération Mac, sinon décodage normal
    cmd = ["ffmpeg", "-v", "error", *hw, "-i", os.path.join(SRC, name), "-vf",
           f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}",
           "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    d, lum, sharp, prev = [], [], [], None
    while True:
        buf = p.stdout.read(W * H)
        if len(buf) < W * H: break
        x = np.frombuffer(buf, np.uint8).reshape(H, W).astype(np.float32)
        lum.append(x.mean())
        lap = x[1:-1, 1:-1] * 4 - x[:-2, 1:-1] - x[2:, 1:-1] - x[1:-1, :-2] - x[1:-1, 2:]
        sharp.append(lap.var())
        F = np.fft.fft2(x * WIN)
        if prev is not None:
            R = prev * np.conj(F); R /= np.abs(R) + 1e-9; r = np.abs(np.fft.ifft2(R))
            y, xx = np.unravel_index(r.argmax(), r.shape)
            y, xx = (y - H if y > H // 2 else y), (xx - W if xx > W // 2 else xx)
            d.append((xx * xx + y * y) ** .5 / 2)
        prev = F
    p.wait()
    np.savez(out, d=np.array(d, np.float32), lum=np.array(lum, np.float32), sharp=np.array(sharp, np.float32))
    return name, len(lum)

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    names = sorted(f for f in os.listdir(SRC) if f.lower().endswith((".mp4", ".mov", ".m4v")) and not f.startswith("."))
    with Pool(4) as pool:
        for n, r in pool.imap_unordered(one, names):
            print(n, r, flush=True)
    print("FINI", flush=True)
