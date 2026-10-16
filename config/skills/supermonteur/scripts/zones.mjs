// Contrôle des zones mortes Instagram (choix « zone organique ») sur un montage HyperFrames :
// ouvre index.html, avance la timeline pas à pas et liste chaque texte (encre réelle des lettres) ou élément animé visible
// qui sort de la zone sûre : haut 270 px, bas 1480 px, côtés 65 px, sous-titres entre 120 et 960 px. Fonds, voiles, vidéos,
// pages plein cadre et plaques de décor (feuille CTA, clavier) ont le droit de déborder.
//   node zones.mjs <dossier du projet> [pas=0.25] [t0] [t1]      -> « OK : 0 ... » ou la liste (instants, élément, pire position)
// Utilise le Chrome et le puppeteer-core installés par HyperFrames (npx hyperframes). ~3 s pour 40 s de vidéo.
import http from "node:http";
import { readFileSync, existsSync, statSync } from "node:fs";
import { join, extname } from "node:path";
import { createRequire } from "node:module";
import { readdirSync } from "node:fs";
import { homedir } from "node:os";
const NPX = join(homedir(), ".npm", "_npx"), CH = join(homedir(), ".cache", "puppeteer", "chrome-headless-shell");
const mod = readdirSync(NPX).map(d => join(NPX, d, "node_modules")).find(d => existsSync(join(d, "hyperframes")) && existsSync(join(d, "puppeteer-core")));
if (!mod) { console.log("puppeteer-core introuvable : lancer une fois « npx --yes hyperframes@0.6.81 snapshot » puis recommencer"); process.exit(1); }
const require = createRequire(mod + "/");
const puppeteer = require("puppeteer-core");
const chrome = existsSync(CH) && readdirSync(CH).sort().reverse().map(v => join(CH, v)).flatMap(v => readdirSync(v).map(x => join(v, x, "chrome-headless-shell"))).find(existsSync);
if (!chrome) { console.log("chrome-headless-shell introuvable dans ~/.cache/puppeteer"); process.exit(1); }

const dir = process.argv[2], step = +(process.argv[3] || 0.25);
const MIME = { ".html": "text/html", ".js": "text/javascript", ".png": "image/png", ".jpg": "image/jpeg", ".webp": "image/webp", ".svg": "image/svg+xml", ".ttf": "font/ttf", ".otf": "font/otf", ".woff2": "font/woff2", ".json": "application/json" };
const srv = http.createServer((q, r) => {
  const p = join(dir, decodeURIComponent(q.url.split("?")[0]));
  // pas de vidéo/son : le contrôle ne regarde que le DOM
  if (!existsSync(p) || statSync(p).isDirectory() || /\.(mp4|webm|mov|wav|mp3|m4a)$/i.test(p)) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { "content-type": MIME[extname(p).toLowerCase()] || "application/octet-stream" }); r.end(readFileSync(p));
}).listen(0);
const port = srv.address().port;
const browser = await puppeteer.launch({ executablePath: chrome, args: ["--no-sandbox"] });
const page = await browser.newPage();
await page.setViewport({ width: 1080, height: 1920 });
await page.goto(`http://127.0.0.1:${port}/${process.env.ZFILE || "index.html"}`, { waitUntil: "networkidle0", timeout: 60000 });
await page.evaluate(() => document.fonts.ready);
const dur = await page.evaluate(() => window.__timelines.root.duration());
const t0 = +(process.argv[4] || 0), t1 = +(process.argv[5] || dur);
const hits = new Map();
for (let t = t0; t <= t1 + 1e-6; t += step) {
  const res = await page.evaluate((t) => {
    const tl = window.__timelines.root; tl.seek(t, false);
    const T = 270, B = 1480, L = 65, R = 1015, out = [];
    const cv = (window.__zcv = window.__zcv || document.createElement("canvas").getContext("2d"));
    // décor autorisé à déborder : fonds, voiles, vidéos, images plein cadre (pages/articles qui défilent), feuille CTA (fond)
    const DECOR = /^(mo|mo-led|moimg|moi-page|moi-cover|clip|fg|mo-fgw|vign|camwrap|punch|root|sheet|kbbg|ctam|veil|tveil|voile|bg|band|bande|crme|inp|kb)$/;
    const op = el => { let o = 1; for (let e = el; e && e.nodeType === 1; e = e.parentElement) { const s = getComputedStyle(e); if (s.display === "none" || s.visibility === "hidden") return 0; o *= +s.opacity; } return o; };
    const clipBox = el => { // intersection avec les parents overflow:hidden + l'écran
      let b = { l: 0, t: 0, r: 1080, b: 1920 };
      for (let e = el.parentElement; e && e !== document.body; e = e.parentElement) { const s = getComputedStyle(e); if (s.overflow === "hidden" || s.overflowX === "hidden" || s.overflowY === "hidden") { const r = e.getBoundingClientRect(); b = { l: Math.max(b.l, r.left), t: Math.max(b.t, r.top), r: Math.min(b.r, r.right), b: Math.min(b.b, r.bottom) }; } }
      return b;
    };
    const name = el => { const c = typeof el.className === "string" ? el.className : (el.className && el.className.baseVal) || ""; const own = el.id ? "#" + el.id : el.tagName.toLowerCase() + (c.trim() ? "." + c.trim().split(/\s+/).join(".") : "");
      if (el.id) return own; const p = el.parentElement && el.parentElement.closest("[id]"); return p ? `${own} (dans #${p.id})` : own; };
    const check = (el, rect, kind, label) => {
      const c = clipBox(el), l = Math.max(rect.left, c.l), r = Math.min(rect.right, c.r), tp = Math.max(rect.top, c.t), bt = Math.min(rect.bottom, c.b);
      if (r - l < 2 || bt - tp < 2) return; // hors écran / masqué
      const isSub = el.closest && el.closest(".cap");
      const LL = isSub ? 120 : L, RR = isSub ? 960 : R, bad = [];
      if (tp < T - 1) bad.push(`haut ${Math.round(tp)}`); if (bt > B + 1) bad.push(`bas ${Math.round(bt)}`);
      if (l < LL - 1) bad.push(`gauche ${Math.round(l)}`); if (r > RR + 1) bad.push(`droite ${Math.round(r)}`);
      if (bad.length) out.push({ kind, who: label, t: tp, b: bt, l, r, LL, RR });
    };
    // 1) textes
    const tw = document.createTreeWalker(document.getElementById("root") || document.body, NodeFilter.SHOW_TEXT);
    for (let n; (n = tw.nextNode());) {
      const s = n.textContent.trim(); if (!s) continue; const el = n.parentElement; if (!el || /^(SCRIPT|STYLE)$/.test(el.tagName)) continue;
      if (op(el) < 0.05) continue;
      const rg = document.createRange(); rg.selectNodeContents(n);
      // encre réelle des lettres (pas la boîte de ligne, qui ajoute du vide au-dessus des capitales et sous la ligne de base)
      const cs = getComputedStyle(el); let txt = cs.textTransform === "uppercase" ? s.toUpperCase() : s;
      cv.font = `${cs.fontStyle} ${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily.split(",").map(f => `"${f.trim().replace(/["']/g, "")}"`).join(",")}`; try { cv.letterSpacing = cs.letterSpacing === "normal" ? "0px" : cs.letterSpacing; } catch {}
      const lines = [...rg.getClientRects()].filter(r => r.width > 0 && r.height > 0);
      for (const rr of lines) {
        const m = cv.measureText(txt), fa = m.fontBoundingBoxAscent, fd = m.fontBoundingBoxDescent, k = rr.height / (fa + fd);
        const one = lines.length === 1;
        const ink = { top: rr.top + (fa - m.actualBoundingBoxAscent) * k, bottom: rr.top + (fa + m.actualBoundingBoxDescent) * k,
                      left: one ? rr.left - m.actualBoundingBoxLeft * k : rr.left, right: one ? rr.left + m.actualBoundingBoxRight * k : rr.right };
        check(el, ink, "texte", `${name(el)} « ${s.slice(0, 24)} »`);
      }
    }
    // 2) éléments graphiques (svg, img, blocs avec fond ou bordure) hors décor
    for (const el of document.querySelectorAll("#root *")) {
      if (/^(SCRIPT|STYLE|VIDEO|AUDIO|BR)$/.test(el.tagName)) continue;
      if (el.closest("svg") && el.tagName.toLowerCase() !== "svg") continue;
      const cls = (typeof el.className === "string" ? el.className : (el.className && el.className.baseVal) || "").trim().split(/\s+/);
      if (cls.some(c => DECOR.test(c)) || DECOR.test(el.id)) continue;
      const s = getComputedStyle(el), rect = el.getBoundingClientRect();
      const graphic = el.tagName === "IMG" || el.tagName.toLowerCase() === "svg" || (s.backgroundColor !== "rgba(0, 0, 0, 0)" && s.backgroundColor !== "transparent") || s.backgroundImage !== "none" || parseFloat(s.borderTopWidth) > 0 || parseFloat(s.borderLeftWidth) > 0;
      if (!graphic) continue;
      if (rect.width >= 1070 && rect.height >= 1900) continue; // plein cadre = fond
      if (op(el) < 0.05) continue;
      if (el.tagName.toLowerCase() === "svg") {   // svg : on mesure ce qui est dessiné (tracés, textes), pas la boîte (souvent vide sur les bords)
        let u = null;
        for (const g of el.querySelectorAll("path,line,circle,rect,ellipse,polyline,polygon,text,image,use")) {
          if (op(g) < 0.05 || g.closest("defs,clipPath,mask")) continue; const c = g.getBoundingClientRect(); if (c.width < 0.5 && c.height < 0.5) continue;
          u = u ? { left: Math.min(u.left, c.left), top: Math.min(u.top, c.top), right: Math.max(u.right, c.right), bottom: Math.max(u.bottom, c.bottom) } : { left: c.left, top: c.top, right: c.right, bottom: c.bottom };
        }
        if (u) check(el, u, "élément", name(el));
        continue;
      }
      check(el, rect, "élément", name(el));
    }
    return out;
  }, t);
  for (const h of res) { const key = `${h.kind}|${h.who}`; const o = hits.get(key);
    if (!o) hits.set(key, { ...h, first: t, last: t, n: 1 });
    else { o.last = t; o.n++; o.t = Math.min(o.t, h.t); o.b = Math.max(o.b, h.b); o.l = Math.min(o.l, h.l); o.r = Math.max(o.r, h.r); } }
}
await browser.close(); srv.close();
if (!hits.size) console.log(`OK : 0 texte / élément animé dans les zones mortes (${t0.toFixed(2)}-${t1.toFixed(2)} s, pas ${step} s)`);
else { console.log(`${hits.size} élément(s) dans les zones mortes :`); for (const h of hits.values()) { const w = [];
  if (h.t < 269) w.push(`haut ${Math.round(h.t)}`); if (h.b > 1481) w.push(`bas ${Math.round(h.b)}`); if (h.l < h.LL - 1) w.push(`gauche ${Math.round(h.l)}`); if (h.r > h.RR + 1) w.push(`droite ${Math.round(h.r)}`);
  console.log(`  ${h.first.toFixed(2)}-${h.last.toFixed(2)} s (${h.n}x)  ${h.kind}  ${h.who}  -> ${w.join(" ")}`); } }
