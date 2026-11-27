"""Le Gardien : bloque la livraison tant qu'une erreur DÉJÀ signalée par l'utilisateur revient.
  python3 gardien.py <dossier du reel>        -> ✅ / ❌ par contrôle, rapport gardien.json, code 1 si un ❌
  python3 gardien.py <dossier du reel> --derush -> DERUSH LAB : seulement les contrôles du dérush (mot coupé, respiration,
      plans >= 2 s, micro-coupure, silence, flash), sans plan.json ni rendu. Rapport gardien-derush.json.
  python3 gardien.py <dossier du reel> --avant -> AVANT LE RENDU : tout ce qui se voit sans la vidéo finale
      (plan, coupes, B-rolls, son de la voix, zones mortes, durée) + un APERÇU image par image (face cam + B-rolls + cartons
      collés en vignettes, ~10 s) pour les flashs. Rapport gardien-avant.json. Pourquoi : (Titanic), 5 rendus au lieu
      d'1, parce que le Gardien ne voyait les erreurs qu'après chaque rendu de 3 à 15 min.
Lit ce qui existe dans le dossier : plan.json, cut.segments.json, cut.mp4 (voix dérushée), final.mp4, cues.json, index.html.
Un contrôle sans son fichier = « sans objet ». Règle : chaque nouvelle note mesurable de l'utilisateur = un contrôle de plus ici
(avec la date et la note d'origine). Ne contrôle QUE ce qu'il a déjà signalé : pas de seuil inventé (sinon fausses alertes).
Pourquoi : sur Tesla/SpaceX, la note auto disait 8,9 aux v1, v2, v3 et v4 alors que l'utilisateur faisait 13, puis 8, puis 3 notes.
"""
import json, os, subprocess, sys
import numpy as np

DERUSH = "--derush" in sys.argv[1:]   # Derush Lab : le dérush seul, comme avant le rendu mais sans plan
AVANT = "--avant" in sys.argv[1:] or DERUSH
D = next((a for a in sys.argv[1:] if not a.startswith("--")), ".")
S = os.path.dirname(os.path.abspath(__file__))
J = lambda f: json.load(open(os.path.join(D, f))) if os.path.exists(os.path.join(D, f)) else None
P = lambda f: os.path.join(D, f) if os.path.exists(os.path.join(D, f)) else None
R = []  # (ok, nom, détail, origine)

def check(ok, nom, detail, origine):
    R.append({"ok": ok, "controle": nom, "detail": detail, "note_origine": origine})

def pcm(path, sr=8000):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                         capture_output=True).stdout
    x = np.frombuffer(raw, dtype=np.float32); n = len(x) // (sr // 100) * (sr // 100)
    return 20 * np.log10(np.sqrt((x[:n].reshape(-1, sr // 100) ** 2).mean(1)) + 1e-9)  # dB toutes les 10 ms

def runs(mask, min_len):  # plages True d'au moins min_len cases de 10 ms -> [(début s, fin s)]
    out, i = [], 0
    while i < len(mask):
        if mask[i]:
            j = i
            while j < len(mask) and mask[j]: j += 1
            if j - i >= min_len: out.append((i / 100, j / 100))
            i = j
        else: i += 1
    return out

def gris(path, ss=0.0, t=None):  # vignettes grises 36 x 64 à 30 i/s (une ligne par image)
    cmd = ["ffmpeg", "-v", "error"] + (["-ss", f"{ss:.3f}"] if ss else []) + ["-i", path] + (["-t", f"{t:.3f}"] if t else [])
    raw = subprocess.run(cmd + ["-vf", "fps=30,scale=36:64,format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.uint8).reshape(-1, 64 * 36).astype(np.float32)

def flashs(fr):  # une image (ou 2 à 6) qui saute puis revient, ou qui ne ressemble ni à l'avant ni à l'après -> [(instant, durée)]
    d = np.abs(np.diff(fr, axis=0)).mean(1)                  # d[i] = écart image i -> i+1
    T = max(12.0, float(np.percentile(d, 99)) * 0.6); fl = []
    for i in np.where(d > T)[0]:
        for L in range(1, 7):                                # flash de L images : saut en i, puis autre saut en i+L
            j = i + L
            if j + 1 >= len(fr): break
            # tête qui bouge vite en continu (fin de Titanic 61 s) = ramp d'écarts AVANT et APRÈS, pas un intrus isolé
            if L == 1 and i > 0 and j + 1 < len(d) and d[i - 1] > T * 0.6 and d[j + 1] > T * 0.6: break
            if d[j] > T and np.abs(fr[i + L + 1] - fr[i]).mean() > T:
                # l'image courte ne ressemble ni à l'avant (i) ni à l'après (i+L+1) : c'est un intrus
                if np.abs(fr[i + 1] - fr[i]).mean() > T and np.abs(fr[i + L] - fr[i + L + 1]).mean() > T:
                    fl.append((round(float(i + 1) / 30, 2), round(L / 30, 2))); break
    return fl

def duree(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                                capture_output=True, text=True).stdout.strip() or 0)

plan = {} if DERUSH else (J("plan.json") or {})
# build.mjs DÉPLACE les B-rolls et cartons (calage sur les coupes, anti-flash) sans toucher plan.json ; il écrit les
# vraies positions dans timeline.json. Le Gardien contrôle donc ce qui sera rendu, pas le brouillon.
tl = None if DERUSH else J("timeline.json")
# MIXSEUL (monte.sh, seul le son a changé) = la vidéo rendue est gardée telle quelle : ses vraies places sont dans
# timeline.json même si plan.json a été réécrit depuis (sinon le Gardien relit les places brutes du plan = fausses alertes).
if tl and (os.environ.get("MIXSEUL") == "1" or os.path.getmtime(P("timeline.json")) >= os.path.getmtime(P("plan.json") or P("timeline.json"))):
    for k in ("brolls", "inserts", "lists", "mini", "proofs"):
        if k in tl: plan[k] = tl[k]
segs = J("cut.segments.json")
voix, final = P("cut.mp4") or P(plan.get("cam", "clip.mp4")), P("final.mp4")   # voix = la face cam dérushée (plan.cam)
if AVANT: final = None   # un final.mp4 d'une ancienne version ne compte pas
cam = P(plan.get("cam", "clip.mp4"))
dur_v = duree(final) if final else min(plan.get("duration") or 1e9, duree(cam) - 0.04) if cam else None

# 1. Micro-coupes (Tesla v1,, « micro rush inutile qui saccade »)
if segs is None: check(None, "Micro-coupes", "pas de cut.segments.json", "Tesla v1")
else:
    bad = [(round(a, 2), round(b - a, 2)) for a, b in segs if b - a < 0.6]
    check(not bad, "Micro-coupes", f"{len(bad)} bout(s) de face cam < 0,6 s : {bad[:6]}" if bad else f"{len(segs)} plans, aucun < 0,6 s", "Tesla v1")

# 1 quater. Coupes à jour : cut.segments.json ne doit jamais annoncer plus que la durée réelle du clip (dérush qui finit
# après la fin du rush, ou fichier retouché à la main). Le Gardien mesure les plans sur ces
# coupes : si elles décrivent plus de vidéo qu'il n'y en a, il voit des plans fantômes (« 0,11 s » en fin) et rate les vrais.
# Un clip PLUS long que les coupes est permis (dernière image tenue pour passer 60 s, monter.rallonge_60).
if segs and cam:
    _ecart = sum(b - a for a, b in segs) - duree(cam)
    check(_ecart <= 0.1, "Coupes à jour", f"cut.segments.json = {_ecart:+.2f} s de plus que {os.path.basename(cam)}" + (" : ces coupes ne décrivent pas cette vidéo, refaire le dérush (fin_propre.py ne répare que la fin posée après le rush)" if _ecart > 0.1 else ""), "studio Super v4")

# 1 quinquies (1er mot de phrase mangé, vu seulement après plusieurs rendus) : vérifié EN TEXTE, avant le rendu,
# sur les mots du rush (words.rush.json) et les coupes (cut.segments.json, en temps du rush).
_wr = (J("words.rush.json") or {}).get("words", []) if segs else []
if _wr and segs:
    _dans = lambda w: any(a - 0.02 <= w["start"] and w["end"] <= b + 0.02 for a, b in segs)
    _coupes = [w["text"] for w in _wr for a, b in segs
               if (w["start"] < a - 0.03 and w["end"] > a + 0.08) or (w["start"] < b - 0.08 and w["end"] > b + 0.03)]
    # Signalé, pas bloquant : les fins de mots de la transcription sont approximatives (à 0,1 s près sur un reel validé) ;
    # le vrai blocage reste le contrôle au son « Pas de mot coupé ».
    if _coupes: check(None, "Mot à cheval sur une coupe ? (texte)", f"à relire : {_coupes[:6]}", "règle vitesse")
    # mot retiré collé au début d'un plan gardé, voix continue (< 0,25 s) : souvent le 1er mot d'une phrase perdu. Signalé, pas bloquant.
    _perdus = []
    for a, b in segs:
        av = [w for w in _wr if a - 0.6 < w["end"] <= a + 0.02 and not _dans(w)]
        ap = [w for w in _wr if w["start"] >= a - 0.02]
        if av and ap and ap[0]["start"] - av[-1]["end"] < 0.25: _perdus.append(f'{a:.2f} s « {av[-1]["text"]} »')
    if _perdus: check(None, "1er mot perdu ? (texte)", f"à relire : mot retiré juste avant un plan gardé : {_perdus[:6]}", "règle vitesse")
# 1 sexies (14/11) : musique toujours, sauf « sans musique » demandé en toutes lettres (plan.sans_musique = true)
_cs = plan.get("cases") or {}
if not plan.get("sans_musique"):
    check(_cs.get("musique", True) is not False and bool(plan.get("music")), "Musique présente (texte)",
          "musique décochée ou absente : la remettre (sans musique seulement si écrit, plan.sans_musique = true)" if (_cs.get("musique", True) is False or not plan.get("music")) else "musique prévue", "musique toujours")
# 1 septies (14/11) : 2 versions du même reel (dossier X et X-insta) = plan.variantes posé dès le départ (même musique permise)
_nom = os.path.basename(os.path.abspath(D)); _base = _nom[:-6] if _nom.endswith("-insta") else _nom
_soeur = [x for x in (_base, _base + "-insta") if x != _nom and os.path.isdir(os.path.join(os.path.dirname(os.path.abspath(D)), x))]
if _soeur:
    _v = {os.path.basename(str(v).rstrip("/")) for v in plan.get("variantes", [])}
    check(all(x in _v for x in _soeur), "2e version liée (texte)", f"version sœur {_soeur} absente de plan.variantes" if not all(x in _v for x in _soeur) else f"variantes = {sorted(_v)}", "2 versions")

# 2. Silence qu'on entend dans la voix (1 seul silence voulu au plus)
if not voix: check(None, "Silences entendus", "pas de voix dérushée (cut.mp4 / plan.cam)", "Tesla v2")
else:
    db = pcm(voix); thr = np.percentile(db, 95) - 30
    gaps = [g for g in runs(db < thr, 50) if g[0] > 0.3 and g[1] < len(db) / 100 - 0.3]  # blancs > 0,5 s, hors bords
    allowed = 1 if (plan.get("silences") or "--pause" in json.dumps(plan)) else 0
    # (RUSH v2 : « enlève le carton plein écran de l’utilisateur ») : le petit temps naturel AVANT la signature finale
    # (« … avec le cœur. [temps] l’utilisateur ») n'est pas une hésitation : couper = plan de 1,1 s (micro-coupure), cacher = carton
    # refusé. Avec "pause_signature": true dans plan.json, UN blanc de 0,8 s au plus dans les 2,5 dernières secondes de voix passe.
    # La musique continue dessous et la voix garde le bruit de la pièce (derush.py) : pas de trou.
    if plan.get("pause_signature"):
        _vend = max((b for a, b in runs(db >= thr, 5)), default=len(db) / 100)
        gaps = [g for g in gaps if not (g[1] - g[0] <= 0.8 and g[1] >= _vend - 2.5)]
    # un blanc gardé EXPRÈS en milieu de phrase
    # (cut.voice.json "pauses_phrase", écrit par derush.py) n'est pas une hésitation à couper : signalé, pas bloquant.
    _pp = (J("cut.voice.json") or {}).get("pauses_phrase", [])
    _ph = [g for g in gaps if any(pa - 0.15 <= g[0] and g[1] <= pb + 0.15 for pa, pb in _pp)]
    if _ph: check(True, "Blancs en milieu de phrase", f"{len(_ph)} blanc(s) gardé(s) (on ne coupe pas une phrase) : {[(round(a,2), round(b-a,2)) for a,b in _ph][:6]} (à écouter)", "règle phrase")
    gaps = [g for g in gaps if g not in _ph]
    extra = gaps[allowed:] if allowed else gaps
    check(not extra, "Silences entendus", f"{len(gaps)} blanc(s) > 0,5 s dans la voix : {[(round(a,2), round(b-a,2)) for a,b in gaps][:6]}" if extra else "aucun blanc > 0,5 s", "Tesla v2")

# 2 bis. Trou de son (RUSH v2 à 11 s) : un blanc coupé à zéro (-180 dB) au milieu de la voix fait
# disparaître le bruit de la pièce d'un coup = on croit à une panne. derush.py baisse les respirations de 22 dB, jamais à zéro.
if voix:
    _W = (J(plan.get("words", "words.json")) or {}).get("words") or []
    _fin = (_W[-1]["end"] + 0.3) if _W else len(db) / 100
    # (RUSH v1 : « dès que j'arrête de parler, il y a un gros silence ») : la fin de la voix est contrôlée aussi.
    # derush.py ne descend plus jamais sous le bruit de la pièce, même après le dernier mot (seul le fondu des 0,05 s finales).
    trous = [g for g in runs(db < -80, 6) if 0.2 < g[0] < len(db) / 100 - 0.1]   # un silence qui démarre avant les 0,1 s finales
    # (RUSH, faux ❌ à 53,95 s) : pièce très calme (bruit du rush à -78 dB, sous le seuil d'écoute). Sa fin baissée
    # au niveau de la pièce tombe sous -80 dB sans qu'on entende rien disparaître : un trou ne s'entend que si la pièce s'entend.
    _fl = (J("cut.voice.json") or {}).get("floor")
    # pièce à -71,75 dB : faux ❌ (même cas qu'une pièce à -78) : une pièce à -70 dB ne s'entend pas non plus.
    if _fl is not None and _fl <= -70:
        trous = [g for g in runs(db < -120, 6) if 0.2 < g[0] < len(db) / 100 - 0.1]   # pièce inaudible : seul un vrai zéro compte
    check(not trous, "Pas de trou de son", f"{len(trous)} silence(s) total(aux) dans la voix : {[(round(a, 2), round(b - a, 2)) for a, b in trous][:6]}"
          if trous else "aucun", "RUSH v2")

# 2 quater. Mot coupé (RUSH v1) : derush.py
# écrit cut.voice.json = chaque endroit du RUSH où la voix s'arrête (fin de plage, blanc baissé, fin de voix) ou reprend.
#  - fin : la voix s'arrête avant la fin réelle du mot (queue_mot.py, même définition que derush.py : voix douce qui traîne,
#    queue sourde de 0,25 s au plus, explosion d'un « t » après sa fermeture) = « t » de « script », « x » de « l’utilisateur » ;
#  - début : la trame juste avant la reprise est déjà de la voix (voisée, > bruit + 15 dB) = l'attaque est mangée (« M » de « Mr »).
# Testé : la v1 d'RUSH est bloquée (script, l’utilisateur, Mr), la v2 passe.
vj = J("cut.voice.json")
if vj and os.path.exists(vj.get("src", "")):
    _rr = subprocess.run(["ffmpeg", "-v", "error", "-i", vj["src"], "-vn", "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout
    _rx = np.frombuffer(_rr, dtype=np.float32); _nn = len(_rx) // 160 * 160
    _rdb = np.convolve(20 * np.log10(np.sqrt((_rx[:_nn].reshape(-1, 160) ** 2).mean(1)) + 1e-9), np.ones(3) / 3, "same")
    _fl, _q = vj["floor"], vj["q"]
    def _voisee(k):
        f = _rx[k * 160: k * 160 + 480].astype(np.float64); f = f - f.mean()
        if len(f) < 480 or (f * f).sum() <= 0: return False
        return max((f[:-l] * f[l:]).sum() / np.sqrt((f[:-l] ** 2).sum() * (f[l:] ** 2).sum() + 1e-12) for l in range(40, 200, 2)) > 0.55
    def _plus_long(m):
        best = cur = 0
        for v in m: cur = cur + 1 if v else 0; best = max(best, cur)
        return best
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from queue_mot import fin_du_mot
    coupes = []
    _mots = J("words.rush.json") or []; _mots = _mots.get("words", []) if isinstance(_mots, dict) else _mots
    _serrees = vj.get("serrees", [])   # coupe sans blanc choisie (phrase retirée collée au mot d'avant) : signalée, pas bloquante
    for e in vj.get("ends", []) + [vj.get("voice_end")]:
        if e is None or any(abs(e - x) < 0.02 for x in _serrees): continue
        k = int(e * 100); j = k
        while j > max(0, k - 60) and _rdb[j] < _q + 6: j -= 1          # dernière trame de voix forte avant la coupe
        if _rdb[j] < _q + 6: continue
        nx = k
        while nx < len(_rdb) - 1 and nx < k + 150 and _rdb[nx] < _q + 6: nx += 1   # reprise de la voix forte
        # (RUSH, rush dehors : grondement grave < 200 Hz à -21 dB sous toute la voix, 10 dB sous la parole) : le son ne
        # redescend JAMAIS sous le seuil de voix à la coupe (nx == k), la queue du mot n'est pas mesurable à l'énergie et
        # fin_du_mot rendait toujours « coupé » (4 fausses alertes, coupes 0,25 s APRÈS « refaire », « hasard », « aussi »).
        # Dans ce cas seulement : on juge sur la fin du dernier mot (words.rush.json, recalée sur le son).
        if nx == k and _mots:
            _fin = max((w["end"] for w in _mots if w["start"] < e), default=None)
            if _fin is not None and e >= _fin + 0.03: continue
        if e < fin_du_mot(_rdb, _voisee, _q, _fl, j / 100, nx / 100) - 0.03: coupes.append(("fin", round(e, 2)))
    for s0 in vj.get("starts", []):
        if any(abs(s0 - x) < 0.02 for x in _serrees): continue   # v5 : début posé à la main sur la timeline (signalé, pas bloquant)
        k = int(s0 * 100) - 1
        if _rdb[k] >= _fl + 15 and _voisee(k): coupes.append(("début", round(s0, 2)))
    if _serrees: check(True, "Coupes serrées", f"{len(_serrees)} coupe(s) posée(s) à la main au ras de la voix (secondes du rush) : {_serrees[:6]} (à écouter)", "cockpit v4")
    check(not coupes, "Pas de mot coupé", f"{len(coupes)} mot(s) coupé(s) (où, seconde du rush) : {coupes[:6]}" if coupes
          else f"{len(vj.get('ends', [])) + 1} fins et {len(vj.get('starts', []))} reprises de voix entières", "RUSH v1")

# 2 ter. Respiration en début de phrase : on l'enlève toujours, dès le départ. Une inspiration peut être presque aussi forte que la voix :
# on la reconnaît parce qu'elle n'a pas de note (trame non voisée). Au début de chaque plage, 0,20 s ou plus de son sans note
# avant la 1re note de voix = bloquant (calé : v2 refusée = 0,24 / 0,33 / 0,38 s ; v3 validée « parfait » = 0,16 s au plus).
if voix and segs:
    _raw = subprocess.run(["ffmpeg", "-v", "error", "-i", voix, "-vn", "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout
    _x = np.frombuffer(_raw, dtype=np.float32).astype(np.float64)
    _p95 = np.percentile(db, 95)
    def _trame(k):   # k = trame de 10 ms -> (dB, note de voix 0-1, part d'aigus > 2 kHz)
        f = _x[k * 160: k * 160 + 480]
        if len(f) < 480: return -120, 0, 0
        f = f - f.mean(); e = 10 * np.log10((f * f).mean() + 1e-12)
        r = max((f[:-l] * f[l:]).sum() / np.sqrt((f[:-l] ** 2).sum() * (f[l:] ** 2).sum() + 1e-12) for l in range(40, 200, 4))
        F = np.abs(np.fft.rfft(f * np.hanning(480))) ** 2; fr = np.fft.rfftfreq(480, 1 / 16000)
        return e, r, F[fr > 2000].sum() / (F.sum() + 1e-12)
    souffles, t = [], 0.0
    _libres = set((vj or {}).get("souffle_garde", []))   # souffle gardé EXPRÈS par la personne (cockpit, --bords de derush.py)
    for _k, (a, b) in enumerate(segs):
        if _k in _libres: t += b - a; continue
        n = 0
        for k in range(int(t * 100), int(min(t + 1.0, t + b - a) * 100)):
            e, r, hi = _trame(k)
            if e > _p95 - 11 and r > 0.55: break          # 1re note de voix : la phrase commence
            if e > _p95 - 30 and r < 0.45: n += 1        # souffle (aigu ou grave, bouche ouverte) : pas de note, mais du son
        if n >= 20: souffles.append((round(t, 2), round(n / 100, 2)))
        t += b - a
    check(not souffles, "Pas de respiration en début de phrase", f"{len(souffles)} début(s) de phrase avec du souffle (instant, durée) : {souffles[:6]}"
          if souffles else f"{len(segs)} débuts de phrase propres", "RUSH v1 + v2")

# 3. Musique coupée en plein milieu (Tesla v1)
sil = plan.get("silences") or []
check(not sil, "Musique jamais coupée", f"le plan coupe la musique : silences {sil}" if sil else "aucune coupure de musique prévue", "Tesla v1")
mus = plan.get("music") or []

# un morceau déjà monté dans un des 3 reels précédents (musiques_utilisees.csv, écrit par mix.py) = bloquant.
_mj = os.path.join(S, "..", "musiques_utilisees.csv")
if os.path.exists(_mj) and plan.get("music"):
    import csv as _csv
    _un = os.path.abspath
    # (RUSH monté en Dynamique ET Minimaliste pour comparer) : plan.variantes = dossiers du même reel dans un autre style
    _var = {_un(v) for v in plan.get("variantes", [])}
    _rows = [r for r in _csv.DictReader(open(_mj)) if _un(r["reel"]) != _un(D) and _un(r["reel"]) not in _var]
    _reels = []
    for r in _rows:
        if _un(r["reel"]) not in _reels: _reels.append(_un(r["reel"]))
    _rec = {os.path.basename(r["musique"]): os.path.basename(_un(r["reel"])) for r in _rows if _un(r["reel"]) in _reels[-3:]}
    _mus = [m.get("src", "") for m in (plan["music"] if isinstance(plan["music"], list) else [plan["music"]])]
    _dbl = [f"{os.path.basename(m)} ({_rec[os.path.basename(m)]})" for m in _mus if os.path.basename(m) in _rec]
    check(not _dbl, "Musique variée", f"déjà dans un des 3 derniers reels : {_dbl}" if _dbl else "aucune des 3 derniers reels", "RUSH")
m0 = min((m.get("start", 0) for m in mus), default=None) if isinstance(mus, list) else None
if m0 is not None:
    check(m0 <= 0.05, "Musique dès 0 s", f"la musique démarre à {m0} s" if m0 > 0.05 else "démarre à 0 s", "Tesla v1")
if final:
    db = pcm(final); trou = [g for g in runs(db < -50, 30) if g[0] > 0.2 and g[1] < len(db) / 100 - 0.2]
    check(not trou, "Aucun trou de son", f"{len(trou)} trou(s) muet(s) > 0,3 s : {trou[:5]}" if trou else "le son ne s'arrête jamais", "Tesla v1")

# 4. Fin muette (voix off)
if final:
    db = pcm(final); queue = float(db[-100:].mean())
    check(queue > -45, "Pas de fin muette", f"dernière seconde à {queue:.0f} dB" + ("" if queue > -45 else " : on n'entend plus rien"), "voix off")

# 5. Écran noir au départ (conf : la vidéo commençait à 0,021 s, aucune image à 0 s)
if final:
    st = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=start_time", "-select_streams", "v:0",
                         "-of", "csv=p=0", final], capture_output=True, text=True).stdout.strip()
    img = subprocess.run(["ffmpeg", "-v", "error", "-i", final, "-frames:v", "1", "-vf", "scale=64:-1,format=gray",
                          "-f", "rawvideo", "-"], capture_output=True).stdout
    luma = float(np.frombuffer(img, dtype=np.uint8).mean()) if img else 0
    ok = st in ("0", "0.000000") and luma > 12
    check(ok, "Image dès 0 s", f"start_time {st}, 1re image luminosité {luma:.0f}/255" + ("" if ok else " : écran noir ou décalé"), "conf")

# 1 bis. Plans >= 2 s : une micro-coupure donne l'impression que la vidéo bugue ; chaque plan dure au moins 2 secondes,
# B-rolls compris. Un plan = ce qu'on voit entre deux changements d'image : coupe de dérush NON cachée, début / fin de B-roll,
# capture, carton, liste. Une coupe cachée sous un B-roll ou un carton ne compte pas.
ovl = [(x["start"], x["end"]) for x in (plan.get("brolls") or []) + (plan.get("inserts") or []) + (plan.get("lists") or [])]
ovl += [(m["start"], m["end"]) for m in (plan.get("mini") or []) if m.get("type") == "card"]
ovl += [(m["start"], m["end"]) for m in (plan.get("proofs") or [])]
if segs:
    cuts, t = [], 0.0
    for a, b in segs: t += b - a; cuts.append(round(t, 3))
    # la fin = celle de la vidéo, calculée comme build.mjs et fin_propre.py (durée face cam - 0,04 s, ou la vidéo finale),
    # pas la somme des coupes : un écart de 0,04 à 0,1 s (ou une dernière image tenue, rallonge_60) faisait voir un plan fantôme.
    dur = dur_v or cuts[-1]; cuts = cuts[:-1]   # (cuts garde l'ordre des segments : la règle des micro-coupures s'en sert)
    # la fin d'un plein écran qui finit SOUS un autre (B-roll prolongé 0,35 s sous le carton ou le B-roll suivant,
    # B-roll qui démarre sous un carton) ne se voit pas : ce n'est pas un plan (sinon fausse alerte « 0,35 s »).
    lay = [(x["start"], x["end"], 6) for x in plan.get("brolls") or []]
    lay += [(x["start"], x["end"], 20) for x in [m for m in (plan.get("mini") or []) if m.get("type") == "card"] + (plan.get("lists") or []) + (plan.get("proofs") or [])]
    dessous = lambda v, o: any(y is not o and y[0] + 0.05 < v < y[1] - 0.05 and (y[2] > o[2] or (y[2] == o[2] and y[0] > o[0])) for y in lay)
    bounds = {0.0, dur} | {round(v, 3) for o in lay for v in o[:2] if not dessous(v, o) and v < dur}   # après la fin : invisible
    bounds |= {round(v, 3) for x in plan.get("inserts") or [] for v in (x["start"], x["end"]) if v < dur}
    bounds |= {c for c in cuts if c < dur - 0.01 and not any(a + 0.05 < c < b - 0.05 for a, b in ovl)}
    bs = sorted(bounds); merged = [bs[0]]
    for v in bs[1:]:
        if v - merged[-1] > 0.08: merged.append(v)
    shots = [(round(a, 2), round(b - a, 2)) for a, b in zip(merged, merged[1:])]
    # un carton punchline calé sur la voix (« tu es déjà mort ») peut durer < 2 s, il ne doit juste pas dépasser la phrase
    cardiv = [(m["start"], m["end"]) for m in (plan.get("mini") or []) if m.get("type") == "card"]
    short = [s_ for s_ in shots if s_[1] < 1.95 and not any(ca - 0.06 <= s_[0] and s_[0] + s_[1] <= cb + 0.06 for ca, cb in cardiv)]
    # la règle des 2 secondes n'est pas absolue (une phrase entière peut durer moins) : un plan court qui contient une phrase
    # ENTIÈRE (il démarre au début d'une phrase et finit sur . ? ! … : ou ,) passe.
    _P = (J(plan.get("words", "words.json")) or {}).get("words") or []
    _fin = lambda w: w["text"].rstrip(" »\"'").endswith((".", "?", "!", "…", ":", ","))
    def phrase_entiere(t0, d):
        dans = [k for k, w in enumerate(_P) if t0 - 0.1 <= w["start"] < t0 + d - 0.05]
        # Le DERNIER mot de la vidéo finit une phrase, même si la transcription a oublié le point.
        return bool(dans) and (dans[0] == 0 or _fin(_P[dans[0] - 1])) and (_fin(_P[dans[-1]]) or dans[-1] == len(_P) - 1)
    short = [s_ for s_ in short if not phrase_entiere(*s_)]
    # coupe visible qui ne gagne presque rien (< 0,45 s) = micro-coupure (MINCUT,« plus de micro-coupures ») : à cacher
    micro = []
    for k in range(1, len(segs)):
        g = segs[k][0] - segs[k - 1][1]; c = cuts[k - 1]
        if 0 < g < 0.15 and not any(a + 0.05 < c < b - 0.05 for a, b in ovl): micro.append((round(c, 2), round(g, 2)))   # serré par défaut (RUSH)
    check(not micro, "Zéro micro-coupure", f"{len(micro)} coupe(s) visible(s) qui gagnent < 0,15 s (instant, gain) : {micro} -> cacher sous un B-roll / carton" if micro else "aucune coupe visible pour rien", "Mode difficile v2")
    # CTA dit 2 fois (2 prises différentes gardées, ex. « Pour t'inscrire, commente… » puis « Pour t'inscrire, le lien est dans
    # ma bio ») : dans les 20 dernières secondes, deux phrases qui commencent par les 2 mêmes mots = une reprise oubliée.
    _norm = lambda t: t.lower().strip(" ,.;:!?…«»\"'")
    _ph, _cur = [], []
    for w in _P:
        _cur.append(w)
        if w["text"].rstrip(" »\"'").endswith((".", "?", "!", "…")): _ph.append(_cur); _cur = []
    if _cur: _ph.append(_cur)
    _fin_v = (_P[-1]["end"] if _P else 0) - 20
    _vus, doublon = {}, []
    for ph in _ph:
        if len(ph) < 3 or ph[0]["start"] < _fin_v: continue
        k = (_norm(ph[0]["text"]), _norm(ph[1]["text"]))
        if k in _vus: doublon.append((round(_vus[k], 2), round(ph[0]["start"], 2), " ".join(k)))
        else: _vus[k] = ph[0]["start"]
    check(not doublon, "CTA dit une seule fois", f"2 prises gardées à la fin (instant 1, instant 2, début) : {doublon} -> garder une seule prise (drop.json)" if doublon else "aucune phrase reprise à la fin", "CTA en double")
    check(not short, "Plans ≥ 2 s", f"{len(short)} plan(s) < 2 s (début, durée) : {short[:8]}" if short else f"{len(shots)} plans, tous ≥ 2 s ou phrase entière", "Mode difficile v2, phrase entière")

# un « flash » au MILIEU d'une prise continue de
# la face cam, à plus de 0,15 s de toute coupe et de tout plein écran, c'est un GESTE FILMÉ (caméra tournée vers la softbox à 4 s,
# main devant l'objectif à 27,7 s), pas un montage raté : rien à recaler, on ne bloque pas. Restent bloquants : les flashs près
# d'un montage (coupe de dérush, B-roll, carton, liste, preuve, capture) et ceux DANS un B-roll (tête tournée trop vite, Titanic).
_cuts_g, _t = [], 0.0
for _a, _b in (segs or []): _t += _b - _a; _cuts_g.append(_t)
_edits = _cuts_g + [v for a, b in ovl for v in (a, b)]
def geste(t, L):
    # marge 0,15 s : un flash de montage colle toujours à une coupe (1 image entre 2 pleins écrans, 1re image d'une prise,
    # bout de 0,18 s entre 2 coupes) ; la main d'RUSH arrive 0,30 s après la coupe de 27,43 s
    if any(a - 0.15 < t + L and t < b + 0.15 for a, b in ovl): return False
    return not any(abs(e - x) < 0.15 for e in _edits for x in (t, t + L))
# (RUSH : 3 « flashs » bloquants à 9,1 / 18,9 / 24,1 s ; images vérifiées une à une = coupes NETTES) : une coupe de dérush
# qui entre dans (ou sort d') un plan où le téléphone bouge (l'image change à chaque frame) donne « saut de la coupe, puis saut du
# mouvement » : ça ressemblait à une image intruse. Ce n'en est pas une quand l'un des deux sauts est une coupe de dérush (loin de
# tout B-roll / carton), que l'autre n'est pas un montage, et que le mouvement CONTINUE de l'autre côté (image d'après / d'avant
# encore > 0,6 x seuil). Les flashs dans ou près d'un B-roll / carton (Mode difficile v3, Titanic) restent bloquants.
def mouvement(t, L, fr):
    d = np.abs(np.diff(fr, axis=0)).mean(1); T = max(12.0, float(np.percentile(d, 99)) * 0.6)
    i = int(round(t * 30)) - 1; j = i + int(round(L * 30))
    if any(a - 0.15 < t + L and t < b + 0.15 for a, b in ovl): return False
    coupe = lambda x: any(abs(c - x) < 0.02 for c in _cuts_g)
    if coupe(t) and not coupe(t + L): return j + 1 < len(d) and d[j + 1] > T * 0.6
    if coupe(t + L) and not coupe(t): return i >= 1 and d[i - 1] > T * 0.6
    # aucun des deux sauts n'est une coupe : c'est DANS une prise filmée (main qui sort du cadre 0,1 s avant une coupe, RUSH
    # 19,4 s) ; un montage ne peut pas y glisser d'image intruse. Gardé seulement si le mouvement est continu d'un côté.
    if not coupe(t) and not coupe(t + L): return (i >= 1 and d[i - 1] > T * 0.6) or (j + 1 < len(d) and d[j + 1] > T * 0.6)
    return False
def tri_flashs(fl, fr=None):
    g = [f for f in fl if geste(*f)]
    m = [f for f in fl if fr is not None and f not in g and mouvement(*f, fr)]
    return ([f for f in fl if f not in g and f not in m], (f" ({len(g)} geste(s) filmé(s) ignoré(s), loin de tout montage : {g[:4]})" if g else "")
            + (f" ({len(m)} coupe(s) dans un plan qui bouge, pas un flash : {m[:4]})" if m else ""))

# 1 ter. Flash d'image réel : 1 image de la tête entre deux pleins écrans enchaînés, invisible dans plan.json et ratée
# par scdet. Image par image (30 i/s, vignettes grises) : une image (ou 2 à 6) qui saute puis revient vers ce
# qu'il y avait avant OU qui ne ressemble ni à l'avant ni à l'après = flash.
if final:
    _gf = gris(final); fl, _gn = tri_flashs(flashs(_gf), _gf)
    check(not fl, "Pas de flash d'image", f"{len(fl)} plan(s) éclair dans la vidéo finale (instant, durée) : {fl[:8]}" if fl else "aucun plan éclair (image par image)" + _gn, "Mode difficile v3")
elif AVANT and cam and dur_v:
    # APERÇU avant rendu = la face cam, avec par-dessus chaque B-roll (vraies images, au bon passage) puis les cartons
    # (aplat), aux positions de timeline.json. Les flashs (1re image d'une prise sous un B-roll mal calé, tête tournée
    # trop vite dans le plan de la montre, bout de face cam de 0,18 s avant « Faux ») s'y voient comme dans la vidéo finale.
    n = int(round(dur_v * 30)); fr = gris(cam)[:n].copy()
    k_ = lambda t: max(0, min(n, int(np.ceil(t * 30 - 1e-6))))   # 1re image où l'élément est visible (t >= début)
    for b in plan.get("brolls") or []:
        src = b["src"] if os.path.isabs(b["src"]) else os.path.join(D, b["src"])
        if not os.path.exists(src): continue
        img = src.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
        a, z = k_(b["start"]), k_(b["end"])
        if z <= a: continue
        bf = gris(src)[:1] if img else gris(src, float(b.get("from") or 0), (z - a) / 30 + 0.2)
        if len(bf): fr[a:z] = bf[np.minimum(np.arange(z - a), len(bf) - 1)]
    for m in [x for x in (plan.get("mini") or []) if x.get("type") == "card"] + (plan.get("lists") or []) + (plan.get("proofs") or []):
        fr[k_(m["start"]):k_(m["end"])] = 30.0               # carton plein écran = aplat sombre
    fl, _gn = tri_flashs(flashs(fr), fr)
    check(not fl, "Pas de flash d'image (aperçu)", f"{len(fl)} plan(s) éclair prévus (instant, durée) : {fl[:8]} -> recaler le B-roll / carton ou prendre un passage plus calme" if fl else "aucun plan éclair dans l'aperçu (image par image)" + _gn, "Mode difficile v3 + Titanic")

# 11. Plus d'1 minute (Titanic : monétisation TikTok = vidéos de plus d'1 min ; 60,7 s validé). "duree_min": 0 pour un client.
dmin = plan.get("duree_min", 60.0)
if dur_v and dmin:
    check(dur_v > dmin, "Plus d'1 minute", f"{dur_v:.1f} s" + ("" if dur_v > dmin else f" : il faut plus de {dmin:.0f} s (prolonger le dernier plan face cam : derush.py --tail)"), "Titanic TikTok")

# 11 bis. Fin basse : la dernière phrase finit sur un point ET la voix descend (fin_basse.py). Bloquant, toutes les vidéos.
_fv = voix
_fw = P("cut.words.json") if _fv and _fv.endswith("cut.mp4") else P(plan.get("words", "words.json"))
if _fv and _fw:
    _r = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "fin_basse.py"), _fv, _fw], capture_output=True, text=True)
    _l = [x for x in (_r.stdout or "").splitlines() if x.strip()]
    check(_r.returncode == 0, "Fin basse", (_l[-2] + " · " if len(_l) > 1 else "") + ("voix qui descend sur une phrase finie" if _r.returncode == 0 else "fin qui monte ou phrase pas finie -> fin_basse.py <rush> <words> --candidats --de --a, puis finir sur une fin BASSE"), "fin basse")

# 12. La musique va jusqu'au bout (Titanic : mix.py coupe la vidéo là où la musique s'arrête, 61,5 s prévus -> 60,7 s)
if isinstance(mus, list) and mus and dur_v and not final:
    m1 = max(m.get("end", dur_v) for m in mus)
    check(m1 >= dur_v - 0.15, "Musique jusqu'au bout", f"musique jusqu'à {m1:.2f} s, vidéo {dur_v:.2f} s" + ("" if m1 >= dur_v - 0.15 else " : la vidéo sera coupée à la fin de la musique"), "Titanic 61 s")

# 13. Aucun B-roll HDR (Titanic : 1 plan iPhone HDR = rendu en mode HDR, mot géant et chiffres cachés derrière la tête)
hdrs = []
for b in (plan.get("brolls") or []) + (plan.get("inserts") or []):
    src = b["src"] if os.path.isabs(b["src"]) else os.path.join(D, b["src"])
    if os.path.exists(src) and not src.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        t = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=color_transfer",
                            "-of", "csv=p=0", src], capture_output=True, text=True).stdout.strip()
        if t in ("arib-std-b67", "smpte2084"): hdrs.append(os.path.basename(src))
check(not hdrs, "B-rolls sans HDR", f"{len(hdrs)} plan(s) HDR : {hdrs} -> broll.py prep les convertit" if hdrs else "aucun plan HDR", "Titanic HDR")

# 13 bis. Vidéos assez longues (RUSH : rendu calé 3 fois à 77 % = un écran coupé plus court que sa place, ~40 min perdues).
# build.mjs rallonge seul une vidéo trop courte ; ce contrôle vérifie qu'aucune ne passe au rendu (sinon Chrome cale).
courtes = []
for b in plan.get("brolls") or []:
    src = b["src"] if os.path.isabs(b["src"]) else os.path.join(D, b["src"])
    if os.path.exists(src) and not src.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        try:
            fd = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src],
                                      capture_output=True, text=True).stdout.strip())
        except ValueError:
            continue
        if fd < b["end"] - b["start"] + 0.1 - 0.02: courtes.append((os.path.basename(src), round(fd, 2), round(b["end"] - b["start"] + 0.1, 2)))
check(not courtes, "Vidéos assez longues", f"{len(courtes)} vidéo(s) plus courte(s) que leur place (fichier, durée, place) : {courtes} -> relancer build.mjs (il les rallonge)"
      if courtes else "chaque B-roll / écran coupé couvre sa place", "RUSH rendu calé")


# 6. Plans trop courts (Tesla v3,, capture >= 1,2 s)
ins = (plan.get("brolls") or []) + (plan.get("inserts") or [])
court = [(x["src"].split("/")[-1], round(x["end"] - x["start"], 2)) for x in ins if x["end"] - x["start"] < 1.2]
check(not court, "Plans ≥ 1,2 s", f"{len(court)} plan(s) trop court(s) : {court[:6]}" if court else f"{len(ins)} B-rolls / captures, tous ≥ 1,2 s", "Tesla v3")

# 7. Flash de tête entre deux pleins écrans (« tête visible une fraction de seconde = effet bug »)
iv = sorted((x["start"], x["end"]) for x in ins); flash = []
for (a1, b1), (a2, b2) in zip(iv, iv[1:]):
    if 0.01 < a2 - b1 < 0.6: flash.append((round(b1, 2), round(a2 - b1, 2)))
check(not flash, "Pas de flash de tête", f"{len(flash)} flash(s) : {flash}" if flash else "aucun", "OPUS v2")

# 8. Bruitages collés (jamais 2 SFX à moins de 1,5 s)
cues = J("cues.json")
if cues is not None:
    t = sorted(c["at"] for c in cues); col = [(round(a, 2), round(b - a, 2)) for a, b in zip(t, t[1:]) if b - a < 1.5]
    check(not col, "Bruitages espacés", f"{len(col)} paire(s) à < 1,5 s : {col}" if col else f"{len(t)} sons, tous espacés", "OPUS")

# 9. Volume (note-10 : LUFS entre -15 et -13)
if final:
    out = subprocess.run(["ffmpeg", "-i", final, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    lufs = float(out.rsplit("I:", 1)[1].split("LUFS")[0]) if "I:" in out else None
    check(lufs is not None and -15 <= lufs <= -13, "Volume", f"{lufs} LUFS (cible -15 à -13)", "note-10")

# 10. Zones mortes Instagram (rien au-dessus de 270 px, sous 1 480 px, à moins de 65 px des bords)
if P("index.html"):
    # un Chrome qui ne répond plus ne bloque plus le montage pour toujours : 2 min max, un 2e essai, puis la vraie raison
    txt = []
    for _essai in range(2):
        try:
            z = subprocess.Popen(["node", os.path.join(S, "zones.mjs"), D], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                 start_new_session=True)   # son propre groupe : en cas de blocage, Chrome est tué avec node
            try:
                out_, _ = z.communicate(timeout=120)
            except subprocess.TimeoutExpired:
                import signal
                try: os.killpg(z.pid, signal.SIGKILL)
                except Exception: pass
                z.communicate()
                raise
            txt = out_.strip().splitlines()
            if any(l.startswith("OK : 0") or "zones mortes :" in l for l in txt): break   # verdict rendu (bon ou mauvais)
        except subprocess.TimeoutExpired:
            txt = ["zones.mjs : Chrome n'a pas répondu en 2 min (Mac en veille ou trop chargé), contrôle non fait"]
    ok = any(l.startswith("OK : 0") for l in txt)
    check(ok, "Zones mortes Insta", txt[-1][:160] if txt else "zones.mjs n'a rien dit", "zones mortes")

# Derush Lab : on ne garde que ce que le dérush peut casser (le reste dépend du montage : musique, B-rolls, durée, zones)
LAB = {"Micro-coupes": "micro-coupure", "Zéro micro-coupure": "micro-coupure", "Pas de mot coupé": "mot coupé",
       "Pas de respiration en début de phrase": "respiration", "Plans ≥ 2 s": "plans ≥ 2 s", "Silences entendus": "silence",
       "Pas de trou de son": "silence", "Blancs en milieu de phrase": "silence", "Coupes serrées": "mot coupé",
       "Pas de flash d'image (aperçu)": "flash"}
if DERUSH:
    R = [{**r, "groupe": LAB[r["controle"]]} for r in R if r["controle"] in LAB]
json.dump(R, open(os.path.join(D, "gardien-derush.json" if DERUSH else "gardien-avant.json" if AVANT else "gardien.json"), "w"), ensure_ascii=False, indent=1)
for r in R:
    print({True: "✅", False: "❌", None: "➖"}[r["ok"]], f"{r['controle']} : {r['detail']}  ({r['note_origine']})")
rouges = [r for r in R if r["ok"] is False]
if DERUSH:
    print(f"\nGARDIEN DÉRUSH : {'❌ ' + str(len(rouges)) + ' point(s) à régler dans le Derush Lab' if rouges else '✅ dérush propre'}")
elif AVANT:
    print(f"\nGARDIEN AVANT RENDU : {'❌ ' + str(len(rouges)) + ' erreur(s) : corriger plan.json, NE PAS LANCER LE RENDU' if rouges else '✅ le rendu peut partir'}")
else:
    print(f"\nGARDIEN : {'❌ ' + str(len(rouges)) + ' erreur(s) déjà signalée(s) par l’utilisateur, NE PAS LIVRER' if rouges else '✅ rien de ce que l’utilisateur a déjà signalé'}")
sys.exit(1 if rouges else 0)
