"""Colle le son final sur le rendu HyperFrames (muet) : voix nettoyée -14 LUFS + musique qui baisse quand on parle + SFX
dont le PIC tombe pile sur l'événement.
  python3 mix.py plan.json render.mp4 voice.mp4 final.mp4
plan.json :
  "music": {"src", "from", "target"}  target = niveau voulu SOUS la voix (défaut config "music_target_lufs" = -29).
     Le script mesure CHAQUE segment après ducking et recale tout seul son niveau (lufs = point de départ, ±1 LU).
     ou une LISTE de segments quand le sujet / l'ambiance / le plan change :
     [{"src", "from", "start": 0, "end": 14.9, "lufs", "emotion": "tension"},
      {"src", "from", "start": 14.9, "end": 36.8, "transition": "douce" | "sec", "emotion": "espoir"}]
     douce = fondu enchaîné 1,5 s centré sur start ; sec = coupe nette + impact sur start. "fin": "naturelle" = pas de long
     fondu de sortie (morceau déjà coupé à la bonne durée par Epidemic EditRecording).
  "silences": [{"to": 8.30}]  -> UN SEUL par reel (ne pas abuser de l'effet de silence).
     "to" = début du mot punchline. "from" se cale tout seul sur la frontière de mot >= 0,4 s avant (jamais au milieu d'un mot).
     Riser qui monte et se coupe net sur "from" -> musique coupée sec (voix seule) -> retour + impact pile sur "to".
     (ancien format "music": {"silences": [...]} encore lu)
  "sfx": [{"src", "at", "volume"}]  -> facultatif : sinon SFX auto.
SFX auto : seulement les gros événements (config.json "sfx_auto", par priorité : hook, silence, plein écran, chiffre, CTA),
jamais deux à moins de "sfx_gap" s (1,5) : le moins prioritaire saute. Pas de clic, frappe ni whoosh de B-roll (« parasites »).
cues.json (écrit par build.mjs à côté de plan.json) : sons des blocs hook / mots géants / preuves / CTA, filtrés pareil.
Calage (guide OPUS) : swoosh, riser, aspiration = PIC sur l'événement ; impact, clic, frappe = DÉBUT sur l'événement ("align": "start").
"""
import json, os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reglages

plan_p, video, voice, out = sys.argv[1:]
plan = json.load(open(plan_p))
here = os.path.dirname(os.path.abspath(plan_p))
CFG = reglages.charger()
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video]))

# --- musique : 1 morceau ou des segments ---
m = plan.get("music")
segs = [] if not m else (m if isinstance(m, list) else [dict(m, start=0, end=dur)])
XF = 1.5   # fondu enchaîné d'une transition douce
# Garde-fou « fin naturelle » (musique coupée net) : « naturelle » = fondu de 0,15 s, valable SEULEMENT
# si le morceau finit vraiment là (edit Epidemic à la bonne durée). S'il continue après la vidéo, fondu de sortie normal.
if segs and segs[-1].get("fin") == "naturelle":
    _s = segs[-1]
    _left = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", _s["src"]])) \
        - _s.get("from", 0) - (_s.get("end", dur) - _s.get("start", 0))
    if _left > 1.5:
        print(f"!! musique : « fin naturelle » mais le morceau continue {_left:.0f} s après la vidéo (pas un edit Epidemic à la durée) "
              "-> fondu de sortie 1,2 s. Mieux : EditRecording à la durée exacte.")
        _s["fin"] = "fondu"

# --- LE silence : 1 seul, calé sur les mots ---
sil = plan.get("silences") or ((m or {}).get("silences", []) if isinstance(m, dict) else [])
if len(sil) > 1:
    main = [z for z in sil if z.get("main")] or sil[:1]
    print(f"!! {len(sil)} silences demandés -> 1 seul gardé (to={main[0]['to']}) : règle du skill")
    sil = main[:1]
words_p = plan.get("words") and os.path.join(here, plan["words"])
W = json.load(open(words_p)) if words_p and os.path.exists(words_p) else []
W = W.get("words", W) if isinstance(W, dict) else W
for z in list(sil):
    if W:   # "to" = début exact du mot punchline ; "from" = fin du mot d'avant : une VRAIE pause (voix + musique coupées)
        z["to"] = min((w["start"] for w in W), key=lambda s: abs(s - z["to"]))
        if "from" not in z:
            prev = [w["end"] for w in W if w["end"] <= z["to"] + 0.01]
            z["from"] = prev[-1] if prev else z["to"] - 0.8
    z.setdefault("from", z["to"] - 0.8)
    # 0,5 s de musique coupée sous la voix = trop court, on ne sent pas l'impact. Pas de vraie pause = pas de silence.
    if z["to"] - z["from"] < 0.6:
        print(f"!! pas de vraie pause avant la punchline ({z['to'] - z['from']:.2f} s < 0,6 s) : silence ABANDONNÉ. "
              "Garder la pause au dérush (derush.py --pause) ou la marquer au tournage.")
        sil.remove(z); continue
    print(f"silence : vraie pause {z['from']:.2f} -> {z['to']:.2f} s ({z['to'] - z['from']:.2f} s), riser avant, impact sur le mot")

def peak(src):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", src, "-ac", "1", "-ar", "8000", "-f", "s16le", "-"])
    import array
    a = array.array("h", raw)
    i = max(range(len(a)), key=lambda k: abs(a[k]))
    return i / 8000

# --- SFX auto : gros événements seulement, anti-collision ---
if "sfx" not in plan:
    kit = {k: v for k, v in CFG.get("sfx", {}).items() if os.path.exists(v["src"])}
    prio = CFG.get("sfx_auto", ["impact", "riser", "subdrop", "list", "number", "sheet"])
    gap = CFG.get("sfx_gap", 1.5)
    ev = [("number", n["start"] + 0.05, {}) for n in plan.get("numbers", [])] + [("list", l["start"], {}) for l in plan.get("lists", [])]
    ev += [("bullet", t, {}) for t in (plan.get("bullets") or {}).get("at", [])]
    ev += [("broll", b["start"], {}) for b in plan.get("brolls", [])]
    ev += [("broll", n["start"], {}) for n in plan.get("inserts", [])]   # whoosh b-roll / insert : COUPÉ par défaut ("broll" absent de sfx_auto)
    for z in sil:
        ev += [("riser", z["from"], {"cut_at_peak": True, "solo": True})]
        if z.get("hit", True): ev += [("impact", z["to"], {"dur": 1.6})]
    for s in segs[1:]:
        if s.get("transition") == "sec": ev += [("impact", s["start"], {"dur": 1.6})]
    cues_p = os.path.join(here, "cues.json")
    for c in (json.load(open(cues_p)) if os.path.exists(cues_p) else []):
        ev.append((c["kind"], c["at"], {"dur": c["dur"]} if "dur" in c else {}))
    ev = sorted([e for e in ev if e[0] in prio and e[0] in kit], key=lambda e: (prio.index(e[0]), e[1]))
    keep, dropped = [], []
    for k, t, extra in ev:
        if extra.get("solo") or all(abs(t - t2) >= gap for _, t2, x2 in keep if not x2.get("solo")): keep.append((k, t, extra))
        else: dropped.append(f"{k}@{t:.2f}")
    keep.sort(key=lambda e: e[1])
    plan["sfx"] = [dict(kit[k], at=t, kind=k, **extra) for k, t, extra in keep]
    print("SFX : " + ", ".join(f"{k}@{t:.2f}" for k, t, _ in keep) + (f"  (sautés, trop proches : {', '.join(dropped)})" if dropped else ""))

def gate(sil):
    """Coupe SÈCHE de la musique sur le silence (le riser fait la montée), retour sec sur le mot (0,04 s)."""
    if not sil: return ""
    g = "*".join(f"min(1,max(0,max(({z['from']:.3f}-t)/0.04,(t-{z['to']:.3f})/0.04)))" for z in sil)
    return f",volume='{g}':eval=frame"

DUCK_KINDS = {"impact", "subdrop", "list", "sheet"}
def duck(sfx):
    """Experts (Murch : 2,5 couches max) : la musique s'efface de 5 dB autour d'un GROS effet (impact, sub drop,
    plein écran, CTA), de 0,15 s avant à 1 s après, puis revient en 0,4 s. 3 couches max : voix + musique + 1 effet."""
    ev = [x["at"] for x in sfx if x.get("kind") in DUCK_KINDS or x.get("duck")]
    if not ev: return ""
    g = "*".join(f"(1-0.44*clip(min((t-{t - 0.25:.3f})/0.1,({t + 1.4:.3f}-t)/0.4),0,1))" for t in ev)
    return f",volume='{g}':eval=frame"

# Voix : config "voice_lufs" (défaut -14) ou plan "voice_lufs". Experts (Curtis Judd, Boykin, EBU) : -16 possible pour la parole sur mobile ; -14 par défaut.
# La musique et les SFX suivent la voix : l'équilibre validé (musique ~15-17 dB sous une voix à -14) ne bouge pas.
VOICE = plan.get("voice_lufs", CFG.get("voice_lufs", -14))
TARGET = CFG.get("music_target_lufs", -29) + (VOICE + 14)
SFXG = 10 ** ((VOICE + 14) / 20)
for s_ in segs: s_.setdefault("lufs", s_.get("target", TARGET) + 5)   # point de départ, recalé par la mesure

def graph():
    inp = ["-i", video, "-i", voice]
    f = [f"[1:a]highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,loudnorm=I={VOICE}:TP=-1.5:LRA=7,"
         "aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[vo][key]"]
    mix = ["[vo]"]
    n = 2
    if segs:
        parts = []
        for i, s in enumerate(segs):
            douce_in = i > 0 and s.get("transition", "douce") == "douce"
            douce_out = i + 1 < len(segs) and segs[i + 1].get("transition", "douce") == "douce"
            t0 = max(0.0, s["start"] - (XF / 2 if douce_in else 0))
            t1 = min(dur, s.get("end", dur) + (XF / 2 if douce_out else 0))
            fi = XF if douce_in else (0.6 if i == 0 else 0.03)
            fo = XF if douce_out else (0.03 if i + 1 < len(segs) else (0.15 if s.get("fin") == "naturelle" else 1.2))
            inp += ["-ss", str(s.get("from", 0)), "-i", s["src"]]
            # creux de -4 dB vers 1,2 kHz : la musique laisse la place à la voix au lieu de seulement baisser (Curtis Judd)
            # fondus à puissance constante (qsin) : un fondu enchaîné linéaire de 2 morceaux perd 3 dB au milieu (Epidemic)
            ms = round(t0 * 1000)
            # LRA 6 (et plus 11) : sur un morceau contrasté, les passages calmes à -35 dB rendaient la musique inaudible : la musique est
            # resserrée pour rester audible du début à la fin, au lieu de disparaître sous la voix dans ses creux
            f.append(f"[{n}:a]atrim=0:{t1 - t0:.3f},asetpts=PTS-STARTPTS,loudnorm=I={s['lufs']}:TP=-3:LRA={s.get('lra', 6)},"
                     f"equalizer=f=1200:width_type=q:width=0.45:g=-4,"
                     f"aformat=sample_rates=48000:channel_layouts=stereo,afade=t=in:d={fi}:curve=qsin,"
                     f"afade=t=out:st={max(0, t1 - t0 - fo):.3f}:d={fo}:curve=qsin,adelay={ms}|{ms}[m{i}]")
            parts.append(f"[m{i}]"); n += 1
        join = f"{''.join(parts)}amix=inputs={len(parts)}:normalize=0:duration=longest," if len(parts) > 1 else f"{parts[0]}"
        f += [f"{join}{'' if len(parts) > 1 else 'anull,'}apad,atrim=0:{dur:.3f}" + gate(sil) + duck(plan.get("sfx", [])) + "[mraw]",
              "[mraw][key]sidechaincompress=threshold=0.05:ratio=2.5:attack=30:release=450[mus]"]   # 30/450 ms : la musique remonte en douceur entre les phrases (Boykin, Judd)
        mix.append("[mus]")
    else:
        f.append("[key]anullsink")
    n_music_inp = len(inp)
    for i, s in enumerate(plan.get("sfx", [])):
        pk = PEAKS.setdefault(s["src"], peak(s["src"]))
        at = s["at"] if s.get("align") == "start" else max(0.0, s["at"] - pk)
        ms = round(at * 1000)
        inp += ["-i", s["src"]]
        if s.get("cut_at_peak"): cut = f"atrim=0:{pk + 0.02:.3f},afade=t=out:st={max(0, pk - 0.02):.3f}:d=0.04,"   # riser coupé net sur son pic
        elif s.get("dur"): cut = f"atrim=0:{s['dur']},afade=t=out:st={max(0, s['dur'] - 0.3):.2f}:d=0.3,"
        else: cut = ""
        f.append(f"[{n}:a]{cut}volume={s.get('volume', 0.3) * SFXG:.4f},aformat=sample_rates=48000:channel_layouts=stereo,adelay={ms}|{ms}[s{i}]")
        mix.append(f"[s{i}]"); n += 1
    # Plafond -2 dBTP (limiteur à -2,3 dB : l'encodage AAC remonte la crête de ~0,1-1 dB) (EBU Tech 3344 : Instagram ré-encode, à -1 une crête peut saturer après coup) ; suréchantillonné pour
    # attraper les crêtes ENTRE les échantillons. level=0 : sinon alimiter REMONTE tout jusqu'à 0 dBFS.
    f.append(f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0:duration=longest,"
             f"aresample=192000,alimiter=limit={10 ** (LIM_DB / 20):.4f}:attack=5:release=50:level=0,aresample=48000,apad,atrim=0:{dur:.3f}[a]")
    return inp, f, n_music_inp

def measure(inp, f, n_music_inp):
    """Niveau RÉEL de chaque segment de musique une fois baissée sous la voix (mesurer CHAQUE segment)."""
    g = ";".join([f[0]] + [x for x in f if ("[mraw]" in x or "[mus]" in x or x.endswith(tuple(f"[m{i}]" for i in range(len(segs)))))
                           and "[a]" not in x]) + ";[vo]anullsink;[mus]ebur128[o]"
    # le gate du silence est AVANT le sidechain : placé après, ffmpeg 6.0 ne propage plus la fin du flux.
    # ebur128 (et pas anull) en sortie : avec anull, ffmpeg 6 se bloque sur ce graphe (asplit -> anullsink + sidechain), testé
    tmp = out + ".musique.wav"
    r = subprocess.run(["ffmpeg", "-nostdin", "-y", "-v", "error", *inp[:n_music_inp], "-filter_complex", g, "-map", "[o]",
                        "-t", f"{dur:.3f}", tmp], capture_output=True, text=True, timeout=300)
    if r.returncode: sys.exit("mesure musique impossible :\n" + r.stderr[-800:])
    res = []
    for s in segs:
        a, b = s.get("start", 0), min(dur, s.get("end", dur))
        e = subprocess.run(["ffmpeg", "-nostdin", "-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", tmp, "-af", "ebur128", "-f", "null", "-"],
                           capture_output=True, text=True, timeout=120).stderr
        hits = [l for l in e.splitlines() if " I:" in l]
        v = float(hits[-1].split()[1]) if hits else None
        res.append(v if v is not None and v > -69 else None)
    os.remove(tmp)
    return res

PEAKS = {}
LIM_DB = -2.3   # plafond du limiteur ; abaissé tout seul si l'AAC fait remonter la crête (voir boucle finale)
inp, f, n_music_inp = graph()
if segs:   # recalage automatique : chaque segment à sa cible ±1 LU (le ducking est piloté par la voix, donc la correction est linéaire)
    for tour in range(3):
        got = measure(inp, f, n_music_inp)
        off = [(s, g) for s, g in zip(segs, got) if g is not None and abs(g - s.get("target", TARGET)) > 1.0]
        if not off or tour == 2: break
        for s, g in off: s["lufs"] = round(s["lufs"] + s.get("target", TARGET) - g, 1)
        inp, f, n_music_inp = graph()
    for i, (s, g) in enumerate(zip(segs, got)):
        tg = s.get("target", TARGET)
        verdict = "?" if g is None else ("  <- TROP BAS, inaudible" if g < tg - 3 else ("  <- trop fort" if g > tg + 1.5 else "  OK"))
        print(f"musique {i + 1} : {os.path.basename(s['src'])} {s.get('start', 0):.1f}-{s.get('end', dur):.1f} s · sous la voix {g} LUFS "
              f"(cible {tg}, réglage lufs {s['lufs']})" + (f" ({s.get('transition', 'douce')})" if i else "")
              + (f" · {s['emotion']}" if s.get("emotion") else "") + verdict)
# Boucle de crête : le mix sortait à -2,3 dBTP pile mais l'AAC le remontait à -1,2 (+1,1 dB sur une
# musique très percussive, pas 0,1-0,3 comme prévu). On MESURE après encodage et on rabaisse le limiteur de l'excès, 3 essais max.
for essai in range(3):
    # écran noir au départ : le rendu HyperFrames commence
    # à 0,021 s avec une « edit list » vide devant ; Chrome l'ignore mais AVFoundation (QuickTime, iPhone, Instagram) ne trouve AUCUNE
    # image à 0 s. On recale la vidéo à 0 (setts) sans edit list + faststart (moov en tête). Vérifié : image à 0,00 s, segment unique.
    subprocess.check_call(["ffmpeg", "-nostdin", "-y", "-v", "error", *inp, "-filter_complex", ";".join(f), "-map", "0:v", "-map", "[a]",
                           "-c:v", "copy", "-bsf:v", "setts=ts=TS-STARTPTS", "-use_editlist", "0", "-movflags", "+faststart",
                           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", f"{dur:.3f}", out])
    e = subprocess.run(["ffmpeg", "-nostdin", "-i", out, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    I = [l for l in e.splitlines() if " I:" in l]; P = [l for l in e.splitlines() if "Peak:" in l]
    i_, p_ = (float(I[-1].split()[1]), float(P[-1].split()[1])) if I and P else (None, None)
    if p_ is None or p_ <= -2.0 or essai == 2: break
    LIM_DB = round(LIM_DB - (p_ + 2.0) - 0.2, 2)
    print(f"crête {p_} dBTP après AAC -> limiteur abaissé à {LIM_DB} dB, nouvel encodage")
    inp, f, n_music_inp = graph()
print(f"{out} : voix{' + musique' if segs else ''} + {len(plan.get('sfx', []))} SFX, {dur:.1f}s")
if p_ is not None:
    print(f"final : {i_} LUFS, crête vraie {p_} dBTP" + ("  <- crête trop haute (> -2)" if p_ > -2.0 else "  OK"))
