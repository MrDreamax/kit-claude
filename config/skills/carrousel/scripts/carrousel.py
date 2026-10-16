"""Monte un carrousel Instagram 1080x1440 (3:4) à partir d'un fichier de description : HTML -> PNG avec Google Chrome (aucun autre logiciel),
puis planche de contrôle + légende. Couleurs, polices, logo et nom viennent de ~/Documents/Brain/00-Moi/marque.json.
  python3 carrousel.py spec.json
Le fichier spec : voir ../exemples/exemple-v4.json. Types de slide :
  cover : photo + mot géant derrière la tête + 1 ligne en majuscules (couverture)
  photo : vraie photo étalonnée (prep.py) + titre + 1 phrase
  art   : illustration 2D (art.py "art" ou fichier "svg") + titre + 1 phrase | "steps" (liste 1-2-3) | "cta" (mot-clé)
Champs d'une slide : title, body, steps, cta, cta_line, title_size ; cover : word, word_top, word_size, caps, caps_size.
Champs d'une photo : src, fx, fy (centre du recadrage), zoom, bright, grad, detourage (false = pas de détourage).
Pas de numéro de slide ni de @ tant que marque.json n'a pas de « pseudo ». Flèche « swipe » sur toutes les slides sauf la dernière.
Contrôles automatiques (ALERTES) : texte qui touche l'illustration ou mange la photo, titre réduit pour tenir, mot seul sur une ligne,
mot de couverture trop large, photo trop serrée au-dessus de la tête, couverture sans détourage.
"""
import concurrent.futures
import hashlib
import html
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, str(pathlib.Path.home() / "Documents" / "Brain" / "_outils"))
import marque  # noqa: E402
from art import ARTS, BLUE, NAVY, PALE, SKY, WHITE, MIST, _mix  # noqa: E402

M = marque.charger()
C = M["couleurs"]
INK = C["texte"]
DEEP = _mix(NAVY, "#000000", 0.35)  # fond des slides photo (voile du bas)
SOFT = _mix(BLUE, "#FFFFFF", 0.5)  # la couleur de marque, éclaircie, pour les fonds sombres


def rgba(h, a):
    return "rgba(%d,%d,%d,%s)" % (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16), a)


def fonts_link(graisses="400;500;600;700;800"):
    return marque.lien_polices(graisses)


BASE = f"""<style>
:root{{--police-titre:'{M["polices"]["titre"]}';--police-texte:'{M["polices"]["texte"]}'}}
*{{box-sizing:border-box}} body{{margin:0;background:#888}}
.s{{display:none;position:relative;width:1080px;height:1440px;overflow:hidden;font-family:var(--police-texte),sans-serif;}}
.s.on{{display:block}}
.light{{background:{WHITE};color:{NAVY};}}
.dark{{background:{DEEP};color:{WHITE};}}
.ph{{position:absolute;inset:0;width:1080px;height:1440px;object-fit:cover;}}
.veil{{position:absolute;left:0;right:0;bottom:0;height:640px;background:linear-gradient(180deg,{rgba(DEEP, 0)} 0%,{rgba(DEEP, .82)} 45%,{rgba(DEEP, .95)} 100%);z-index:2;}}
.swp{{position:absolute;right:84px;bottom:84px;width:64px;height:2px;background:{BLUE};z-index:5;}}
.swp:after{{content:"";position:absolute;right:0;top:-6px;width:12px;height:12px;border-top:2px solid {BLUE};border-right:2px solid {BLUE};transform:rotate(45deg);}}
.dark .swp{{background:{WHITE};}} .dark .swp:after{{border-color:{WHITE};}}
.txt{{position:absolute;left:84px;right:84px;bottom:150px;z-index:4;}}
.titre{{font-family:var(--police-titre),sans-serif;font-weight:800;line-height:1.04;letter-spacing:-1px;text-wrap:balance;}}
.titre.ital{{font-style:italic;font-weight:600;}}
.caps{{font-family:var(--police-titre),sans-serif;font-weight:700;text-transform:uppercase;letter-spacing:5px;line-height:1.1;}}
.body{{font-weight:500;font-size:42px;line-height:1.38;margin-top:26px;text-wrap:pretty;}}
.light .body{{color:{rgba(NAVY, .82)};}} .dark .body{{color:rgba(255,255,255,.9);}}
.rule{{width:64px;height:3px;background:{BLUE};margin-bottom:32px;}}
.dark .rule{{background:{SOFT};}}
.shadow{{text-shadow:0 4px 28px rgba(0,0,0,.45);}}
.art{{position:absolute;left:0;top:0;width:1080px;height:900px;}}
.giant{{font-family:var(--police-titre),sans-serif;font-weight:800;letter-spacing:-.02em;line-height:1;white-space:nowrap;}}
.giant.ital{{font-style:italic;font-weight:600;}}
.id{{position:absolute;left:84px;bottom:92px;z-index:5;font-size:26px;font-weight:600;letter-spacing:.04em;opacity:.8}}
</style>"""

# Limite haute du bloc de texte (px depuis le haut de la slide) : en dessous le texte touche l'illustration ou mange la photo
LIMITE = {"art": 860, "photo": 760}

SCRIPT = """<script>
const P=new URLSearchParams(location.search), S=[...document.querySelectorAll('.s')];
function lignes(el){ // nombre de lignes et largeur de la dernière, par les rectangles du texte
  const r=document.createRange(); r.selectNodeContents(el);
  const rects=[...r.getClientRects()].filter(x=>x.width>2&&x.height>2); if(!rects.length) return {n:0,last:0};
  const tops=[...new Set(rects.map(x=>Math.round(x.top/8)))].sort((a,b)=>a-b);
  const last=rects.filter(x=>Math.round(x.top/8)===tops[tops.length-1]).reduce((s,x)=>s+x.width,0);
  return {n:tops.length,last};
}
function fit(sl){
  const rep={n:+sl.dataset.i,notes:[]}, top0=sl.getBoundingClientRect().top;
  const g=sl.querySelector('.giant');
  if(g){let fs=parseFloat(getComputedStyle(g).fontSize),f0=fs;while(g.getBoundingClientRect().width>1000&&fs>110){fs-=6;g.style.fontSize=fs+'px'}
    if(fs<f0*0.8) rep.notes.push('mot géant réduit de '+f0+' à '+fs+' px pour tenir dans la slide');
    if(g.getBoundingClientRect().width>1000) rep.notes.push('DÉBORDE : le mot géant est trop long, choisis un mot plus court');
    rep.word_bottom=Math.round(g.getBoundingClientRect().bottom-top0);}
  const t=sl.querySelector('.txt'), lim=+(sl.dataset.limite||0);
  if(t&&lim){const ti=t.querySelector('.titre');let fs=parseFloat(getComputedStyle(ti).fontSize),f0=fs;
    while(t.getBoundingClientRect().top-top0<lim&&fs>58){fs-=4;ti.style.fontSize=fs+'px'}
    if(fs<f0) rep.notes.push('titre réduit de '+f0+' à '+fs+' px pour tenir : trop de mots ?');
    if(t.getBoundingClientRect().top-top0<lim) rep.notes.push('DÉBORDE : le texte remonte sur '+(sl.dataset.zone==='art'?"l'illustration":'la photo')+', coupe le texte');}
  for(const el of sl.querySelectorAll('.titre,.body')){const l=lignes(el),w=el.getBoundingClientRect().width;
    if(l.n>=2&&l.last<w*0.2) rep.notes.push('mot seul en dernière ligne (« '+el.textContent.trim().split(/\\s+/).slice(-1)[0]+' ») : ajoute &nbsp; ou <br>');}
  return rep;
}
function show(i){S.forEach((s,j)=>s.classList.toggle('on',j===i-1));return fit(S[i-1])}
// Les slides cachées ne chargent aucune police : on les charge à la main AVANT de mesurer.
const cs0=getComputedStyle(document.documentElement);
const FAMS=[...new Set(['--police-titre','--police-texte'].map(v=>cs0.getPropertyValue(v).replace(/['"]/g,'').trim()))];
const pret=()=>Promise.all(FAMS.flatMap(f=>['normal','italic'].flatMap(st=>['400','500','600','700','800'].map(w=>document.fonts.load(st+' '+w+' 40px "'+f+'"').catch(()=>0))))).then(()=>document.fonts.ready);
function chargee(f){const c=document.createElement('canvas').getContext('2d'); // une police absente = largeur de la police de secours demandée à sa place
  const w=(fb)=>{c.font='800 48px "'+f+'",'+fb;return c.measureText('mmmmmmWWWiii 123').width};
  return w('monospace')===w('serif')}
pret().then(()=>{
  if(P.has('report')){const out=S.map((s,j)=>show(j+1));const pre=document.createElement('pre');pre.id='rapport';pre.textContent=JSON.stringify({slides:out,polices_manquantes:FAMS.filter(f=>!chargee(f))});document.body.appendChild(pre);}
  else show(+P.get('s')||1);
});
</script>"""


def steps_html(items):
    return "".join(f'<div style="display:flex;gap:24px;align-items:baseline;margin-top:18px"><div class="titre" style="font-size:64px;color:{BLUE};min-width:44px">{i}</div>'
                   f'<div class="body" style="margin-top:0">{t}</div></div>' for i, t in enumerate(items, start=1))


def cta_html(word, line):
    return (f'<div style="display:flex;align-items:center;gap:26px;margin-top:36px"><div class="caps" style="font-size:40px">Commente</div>'
            f'<div style="background:{BLUE};padding:18px 32px 14px;border-radius:12px"><div class="caps" style="font-size:62px;font-weight:800;letter-spacing:8px;line-height:1;color:{WHITE}">{word}</div></div></div>'
            f'<div class="body" style="margin-top:22px">{line}</div>')


def text_block(s, ital):
    body = f'<div class="body">{s["body"]}</div>' if s.get("body") else ""
    if s.get("steps"):
        body += steps_html(s["steps"])
    if s.get("cta"):
        body += cta_html(s["cta"], s.get("cta_line", ""))
    cls = "titre ital" if ital else "titre"
    return f'<div class="rule"></div><div class="{cls}" style="font-size:{s.get("title_size", 84)}px">{s["title"]}</div>{body}'


def identite(n, total):
    """@ et numéro : seulement si l'utilisateur a rempli « pseudo » dans marque.json."""
    ps = (M.get("pseudo") or "").strip()
    return f'<div class="id">{html.escape(ps)} · {n}/{total}</div>' if ps else ""


def render(s, i, total, spec_dir, photos, tete, ital):
    last = i == total
    arrow = "" if last else '<div class="swp"></div>'
    ident = identite(i, total)
    cls_giant = "giant ital" if ital else "giant"
    if s["type"] == "cover":
        p = photos[s["photo"]]
        size = s.get("word_size", 270)
        # sans valeur donnée : le mot passe à moitié derrière la tête (haut de la tête - 60 % de la hauteur du mot)
        default_top = max(120, min(420, (tete.get(s["photo"]) or 560) - round(0.6 * size))) if p["fg"] else 150
        top = s.get("word_top", default_top)
        fg = f'<img class="ph" src="{p["fg"]}" style="z-index:3">' if p["fg"] else ""
        return (f'<section class="s dark" data-i="{i}" data-cover="1"><img class="ph" src="{p["bg"]}"><div class="veil" style="height:520px"></div>'
                f'<div class="shadow" style="position:absolute;left:0;right:0;top:{top}px;text-align:center;color:{WHITE};z-index:{2 if p["fg"] else 3}"><span class="{cls_giant}" style="display:inline-block;font-size:{size}px">{s["word"]}</span></div>'
                f'{fg}<div class="caps shadow" style="position:absolute;left:72px;right:72px;bottom:170px;text-align:center;font-size:{s.get("caps_size", 54)}px;z-index:4">{s["caps"]}</div>'
                f'{arrow}{ident}</section>')
    if s["type"] == "photo":
        p = photos[s["photo"]]
        return (f'<section class="s dark" data-i="{i}" data-zone="photo" data-limite="{LIMITE["photo"]}"><img class="ph" src="{p["bg"]}"><div class="veil"></div>'
                f'<div class="txt shadow">{text_block(s, ital)}</div>{arrow}{ident}</section>')
    if s["type"] == "art":
        if s.get("svg"):
            art = open(os.path.join(spec_dir, os.path.expanduser(s["svg"])), encoding="utf-8").read()
        else:
            art = ARTS[s["art"]](**s.get("args", {}))
        return (f'<section class="s light" data-i="{i}" data-zone="art" data-limite="{LIMITE["art"]}">{art}'
                f'<div class="txt">{text_block(s, ital)}</div>{arrow}{ident}</section>')
    raise SystemExit(f"type de slide inconnu : {s['type']} (cover, photo ou art)")


def chrome_cmd(user_dir, extra):
    return [marque.chrome(), "--headless=new", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files", "--use-mock-keychain",
            "--force-device-scale-factor=1", f"--user-data-dir={user_dir}", "--virtual-time-budget=9000"] + extra


def preparer_photos(spec, spec_dir, cache):
    """Recadre, étalonne et détoure chaque photo du spec (résultat gardé en cache : relancer ne refait que ce qui change)."""
    import prep
    os.makedirs(cache, exist_ok=True)
    out, tete = {}, {}
    for nom, p in spec.get("photos", {}).items():
        src = os.path.expanduser(p["src"])
        if not os.path.isfile(src):
            raise SystemExit(f"Photo introuvable : {src} (photo « {nom} » du spec). Choisis-la avec planches.py.")
        args = {k: p[k] for k in ("fx", "fy", "zoom", "bright", "grad", "detourage") if k in p}
        st = os.stat(src)
        cle = hashlib.sha1(json.dumps([src, st.st_mtime, st.st_size, args, C["foncee"], C["principale"], C["teinte"]], sort_keys=True).encode()).hexdigest()[:8]
        base = f"{nom}-{cle}"
        bg, fg = os.path.join(cache, base + "-bg.jpg"), os.path.join(cache, base + "-fg.png")
        meta = os.path.join(cache, base + ".json")
        if os.path.exists(bg) and os.path.exists(meta):
            y = json.load(open(meta))["tete"]
        else:
            try:
                y = prep.preparer(src, base, cache, **args)
            except ImportError as e:
                raise SystemExit(f"Il manque un module Python ({e}). Installe : pip3 install pillow numpy onnxruntime")
            json.dump({"tete": y}, open(meta, "w"))
            print(f"photo {nom} préparée, tête y≈ {y}")
        out[nom] = {"bg": bg, "fg": fg if os.path.exists(fg) else None}
        tete[nom] = y
    return out, tete


def main():
    spec_path = os.path.abspath(sys.argv[1])
    spec, spec_dir = json.load(open(spec_path, encoding="utf-8")), os.path.dirname(spec_path)
    out = os.path.expanduser(spec["out"])
    os.makedirs(out, exist_ok=True)
    slides = spec["slides"]
    if not 6 <= len(slides) <= 10:
        print(f"ALERTE : {len(slides)} slides (8 par défaut, 6 minimum, 10 maximum)")
    photos, tete = preparer_photos(spec, spec_dir, os.path.join(out, "_photos"))
    ital = spec.get("titre_style") == "italique"
    manquantes = [s["photo"] for s in slides if s["type"] in ("cover", "photo") and s.get("photo") not in photos]
    if manquantes:
        raise SystemExit(f"Photo(s) non déclarée(s) dans « photos » du spec : {manquantes}")

    build = tempfile.mkdtemp(prefix="carrousel-")
    try:
        # les photos sont copiées à côté du HTML (Chrome ne lit pas toujours ~/Documents)
        os.makedirs(os.path.join(build, "photos"))
        for p in photos.values():
            for k in ("bg", "fg"):
                if p[k]:
                    shutil.copy(p[k], os.path.join(build, "photos", os.path.basename(p[k])))
                    p[k + "_page"] = "photos/" + os.path.basename(p[k])
        pages = {k: {"bg": v["bg_page"], "fg": v.get("fg_page")} for k, v in photos.items()}
        body = "".join(render(s, i, len(slides), spec_dir, pages, tete, ital) for i, s in enumerate(slides, start=1))
        page = f'<!doctype html><html><head><meta charset="utf-8">{fonts_link()}{BASE}</head><body>{body}{SCRIPT}</body></html>'
        pathlib.Path(build, "deck.html").write_text(page, encoding="utf-8")
        url = pathlib.Path(build, "deck.html").as_uri()

        # 1. contrôles (le script de la page mesure chaque slide et écrit son rapport dans la page)
        dom = subprocess.run(chrome_cmd(os.path.join(build, "chrome-r"), ["--dump-dom", url + "?report=1"]),
                             capture_output=True, text=True, timeout=180).stdout
        m = re.search(r'<pre id="rapport">(.*?)</pre>', dom, re.S)
        alerts = []
        if not m:
            alerts.append("contrôles impossibles : la page n'a pas rendu de rapport (Chrome ou polices Google bloqués ?)")
        else:
            rap = json.loads(html.unescape(m.group(1)))
            for r in rap["slides"]:
                for n in r["notes"]:
                    alerts.append(f"slide {r['n']} · {n}")
            for f in rap.get("polices_manquantes", []):
                alerts.append(f"POLICE « {f} » non chargée (Internet coupé ou nom inconnu de Google Fonts) : les slides utilisent une police de secours")
        for i, s in enumerate(slides, start=1):
            if s["type"] == "cover":
                y = tete.get(s["photo"])
                if not photos[s["photo"]]["fg"]:
                    alerts.append(f"slide {i} · couverture SANS détourage : le mot passe devant la tête (voir « Détourage » dans SKILL.md)")
                elif y is not None and y < 260:
                    alerts.append(f"slide {i} · tête trop haute (y≈{y}) : pas de place pour le mot géant, prends une photo plus large (zoom plus petit)")
            if len(re.sub(r"<[^>]+>", " ", (s.get("word", "") + " " + s.get("caps", ""))).split()) > 7:
                alerts.append(f"slide {i} · couverture : plus de 7 mots (le mot géant + la ligne)")

        # 2. images (une par slide, en parallèle)
        def shoot(i):
            png = os.path.join(out, f"slide-{i}.png")
            subprocess.run(chrome_cmd(os.path.join(build, f"chrome-{i}"), [f"--window-size=1080,1440", f"--screenshot={png}", url + f"?s={i}"]),
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
            return png
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
            pngs = list(ex.map(shoot, range(1, len(slides) + 1)))
    finally:
        shutil.rmtree(build, ignore_errors=True)

    from PIL import Image
    ims = [Image.open(p) for p in pngs]
    for p, im in zip(pngs, ims):
        if im.size != (1080, 1440):
            alerts.append(f"{os.path.basename(p)} : taille {im.size[0]}x{im.size[1]} au lieu de 1080x1440")
    cols = 4
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 556 + 8, rows * 736 + 8), "#888888")
    for k, im in enumerate(ims):
        sheet.paste(im.convert("RGB").resize((540, 720), Image.LANCZOS), (8 + (k % cols) * 556, 8 + (k // cols) * 736))
    sheet.save(os.path.join(out, "00-planche.png"))
    with open(os.path.join(out, "legende.txt"), "w", encoding="utf-8") as f:
        f.write(spec.get("caption", "") + "\n\n" + " ".join("#" + h for h in spec.get("hashtags", [])) + "\n")
    json.dump(spec, open(os.path.join(out, "spec.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(ims)} slides -> {out}")
    print("\n".join(["ALERTES :"] + alerts) if alerts else "0 alerte")


if __name__ == "__main__":
    main()
