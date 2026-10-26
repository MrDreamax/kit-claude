#!/usr/bin/env node
/**
 * supermonteur : face cam -> compo HyperFrames (à lancer dans le dossier du projet, à côté de plan.json).
 *   node build.mjs --plan plan.json --out index.html
 * plan.json : da? (chemin d'une DA .json à la place de la tienne ; défaut = scripts/reglages.py da : ta marque + montage.json), cam, words, duration?, keywords (mots en serif italique), numbers (chiffres derrière la tête, fg = détourage),
 *             lists (cartons plein écran), bullets (pastilles 1-2-3), brolls (plans de coupe plein écran),
 *             inserts (images sur-mesure incrustées par-dessus la cam : {src, start, end, pos: top|center, w}),
 *             hook (ouverture : bandes noires qui s'écartent + viseur REC), bigwords (mot géant serif derrière la tête),
 *             proofs (pleins écrans preuve : curve | clock | dashboard), cta (feuille de commentaires « commente MOT »).
 * Écrit aussi cues.json (sons des nouveaux blocs) que mix.py lit tout seul.
 */
// Zones mortes Instagram (TOUS les montages, choix « zone organique ») : aucun texte ni élément animé
// au-dessus de 270 px (14 %, Meta Ads Guide Reels), à moins de 65 px des bords (6 %), sous 1480 px (pseudo + légende),
// ni à droite des sous-titres là où sont les boutons (sous-titres entre 120 et 960 px). Fonds et décors peuvent déborder.
// Contrôle après chaque montage : node scripts/zones.mjs <dossier> (0 élément attendu).
import { readFileSync, writeFileSync, mkdirSync, copyFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";

const SKILL = dirname(dirname(fileURLToPath(import.meta.url)));
const args = Object.fromEntries(process.argv.slice(2).reduce((a, v, i, arr) => (v.startsWith("--") && a.push([v.slice(2), arr[i + 1]]), a), []));
const plan = JSON.parse(readFileSync(args.plan, "utf8"));

// DA de la personne : polices + couleurs. Défaut = scripts/reglages.py (marque.json + montage.json de l'utilisateur) ;
// plan.da = chemin d'un fichier .json complet (même forme) qui remplace tout.
const DA = plan.da ? JSON.parse(readFileSync(plan.da, "utf8"))
  : JSON.parse(execFileSync("python3", [join(SKILL, "scripts", "reglages.py"), "da"]).toString());
DA.fonts = Object.assign({ sans: "Montserrat.ttf", serif: "InstrumentSerif-Italic.ttf" }, DA.fonts || {}, plan.fonts || {});
DA.colors = Object.assign({ text: "#FFFFFF", accent: "#2563EB", list: ["#111827", "#090D15", "#050709"], halo: "0,0,0", glow: "0,0,0" }, DA.colors || {});
const C = DA.colors;
// la DA du MONTAGE suit l'univers du RUSH (4/10 quand la charte a été plaquée sur un rush d'un autre univers) : plan.colors écrase la DA
Object.assign(C, plan.colors || {});
mkdirSync("fonts", { recursive: true });
// police des sous-titres à part si la DA en donne une (DA.fonts.sub ; Montserrat par défaut, Oswald testé et écarté) ; le reste (cartons, chiffres, CTA) garde DA.fonts.sans
DA.fonts.sub = DA.fonts.sub || DA.fonts.sans;
for (const f of new Set([DA.fonts.sans, DA.fonts.serif, DA.fonts.sub])) if (!existsSync(join("fonts", f))) copyFileSync(join(SKILL, "fonts", f), join("fonts", f));
const SUBSIZE = plan.subSize || DA.subSize || 52, SUBTRACK = plan.subTrack ?? DA.subTrack ?? .5;
const out = args.out || "index.html";
const esc = t => String(t).replace(/[<>&]/g, "");
const norm = t => t.toLowerCase().replace(/[«»“”"….,!?;:]/g, "").trim();

// mots : on recolle les élisions de Whisper ("t" + "'as" -> "t'as")
const raw = JSON.parse(readFileSync(plan.words, "utf8")).words;
const W = [];
for (const w of raw) {
  const text = w.text.trim();
  if (!text) continue;
  // ponctuation seule (« ? » rendu comme un mot par Whisper) : collée au mot d'avant, sinon bloc de sous-titre vide
  if ((/^['’-]/.test(text) || text === "%" || /^[.,!?…;:]+$/.test(text)) && W.length) { const p = W[W.length - 1]; p.text += (text === "%" ? " " : "") + text.replace("’", "'"); p.e = +w.end; continue; }
  W.push({ t: +w.start, e: +w.end, text });
}
const camDur = +execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", plan.cam]).toString();
// corrections des erreurs de Whisper (plan.fixes : {"boulettes": "bullet"}), relues par Claude avant chaque montage
const FIX = Object.fromEntries(Object.entries(plan.fixes || {}).map(([k, v]) => [norm(k), v]));
for (const w of W) { const k = norm(w.text); if (FIX[k] !== undefined) w.text = w.text.replace(/^[^.,!?]+/, FIX[k]); }
const dur = Math.min(plan.duration || camDur, camDur - 0.04);
const kw = new Set((plan.keywords || []).map(norm));
// règle (Style Lab final) : vidéo AVEC titre-question = ni mot géant derrière la tête, ni mot fort. Sans titre : les deux sont permis.
if (plan.title && (plan.bigwords || []).length) console.log(`titre présent : ${plan.bigwords.length} mot(s) géant(s) ignoré(s) (règle titre = ni mot géant ni mot fort)`);
const lists = plan.lists || [], proofs = plan.proofs || [], cta = plan.cta, bigwords = plan.title ? [] : plan.bigwords || [];
// style minimaliste (plan.mini) : les cartons typo plein écran comptent comme des pleins écrans (anti-flash, pas de sous-titres dessous)
const cards = (plan.mini || []).filter(m => m.type === "card");
// ---------- garde-fou anti-flash (la tête visible une fraction de seconde entre deux pleins écrans = « bug pour le cerveau ») :
//            entre deux pleins écrans, soit enchaînés direct, soit >= 1,5 s de face cam. Carton/preuve -> prolongé jusqu'au suivant ;
//            B-roll -> raccourci (ou retiré s'il tombe sous 1,2 s). ----------
{
  const GAP = 1.5, blocks = [...lists, ...proofs, ...cards, ...(cta ? [cta] : []), ...(plan.brolls || []).map(b => Object.assign(b, { _broll: true }))]
    .sort((a, b) => a.start - b.start);
  for (let i = 0; i + 1 < blocks.length; i++) {
    const a = blocks[i], b = blocks[i + 1], g = b.start - a.end;
    if (g <= 0 || g >= GAP) continue;
    if (!a._broll) { console.log(`anti-flash : plein écran ${a.start}-${a.end} prolongé jusqu'à ${b.start} (tête ${g.toFixed(2)} s évitée)`); a.end = b.start; }
    else if (b.start - GAP - a.start >= 1.2) { console.log(`anti-flash : B-roll ${a.start} raccourci à ${(b.start - GAP).toFixed(2)}`); a.end = +(b.start - GAP).toFixed(3); }
    else { console.log(`anti-flash : B-roll ${a.start}-${a.end} retiré (trop près du plein écran suivant)`); a._drop = true; }
  }
  if (plan.brolls) plan.brolls = plan.brolls.filter(b => !b._drop);
}
// plages plein écran sans sous-titres dessous : cartons liste, preuves, feuille de commentaires
// + B-rolls "nosub": true (graphique, capture d'écran : les sous-titres deviennent illisibles sur fond clair et cachent l'info)
const FULL = [...lists, ...proofs, ...cards, ...(cta ? [cta] : []), ...(plan.brolls || []).filter(b => b.nosub)];
const covered = t => FULL.some(l => t >= l.start - 0.02 && t < l.end);
// sortie douce seulement s'il reste >= 1,5 s de face cam derrière ; sinon coupe franche enchaînée au plein écran suivant (anti-flash)
const FS = [...lists, ...proofs, ...cards, ...(cta ? [cta] : []), ...(plan.brolls || [])];
const SOFT = (b, d) => Math.min(dur, ...FS.filter(x => x.start >= b - 0.02).map(x => x.start)) - b >= 1.5 ? d : 0;
// sous-titres dans la zone la plus lisible (sombre + unie, ex. t-shirt noir), calculée sur le rush
let SUBY = plan.subY;
if (SUBY == null) { try { SUBY = +execFileSync("python3", [join(SKILL, "scripts", "subzone.py"), plan.cam]).toString().trim(); } catch { SUBY = 1150; } console.log(`sous-titres à y=${SUBY}px`); }
// zones mortes Insta : encre d'un sous-titre 52 px = de +8 à +53 px sous son haut ; mot fort serif 132 px = de +16 à +143 px
// (jambages g, p, j compris), mesuré au navigateur. Rien sous 1480 px, rien au-dessus de 270 px.
const SUB_MAX = 1480 - Math.round(53 * SUBSIZE / 52), KW = plan.kwSize || 132, EMW = {};
const emLines = t => { if (EMW[t] == null) { try { EMW[t] = +execFileSync("python3", ["-c", "import sys;from PIL import ImageFont;print(ImageFont.truetype(sys.argv[1],int(sys.argv[3])).getlength(sys.argv[2]))", join("fonts", DA.fonts.serif), t, String(KW)]).toString(); } catch { EMW[t] = t.length * 0.42 * KW; } }
  return Math.max(1, Math.ceil(EMW[t] * 1.03 / 840)); };
const subY = (y, em) => Math.max(270, Math.min(y, em ? 1480 - Math.round(143 * KW / 132) - Math.round((emLines(em) - 1) * 1.05 * KW) : SUB_MAX));
if (SUBY > SUB_MAX) { console.log(`sous-titres remontés de ${SUBY} à ${SUB_MAX} px (zone morte du bas)`); SUBY = SUB_MAX; }
const ACC = C.accent || "#2563EB";   // 1 seul accent (guide OPUS : 2 neutres + 1 accent)
// dégradé des cartons minimalistes tiré de l'accent (même recette que outils/style-lab/round.py palette) : [haut gauche sombre, haut droit vif, bas gauche, bas droit clair, fond]
const gradFromAccent = a => {
  const [r, g, b] = [1, 3, 5].map(i => parseInt(a.slice(i, i + 2), 16) / 255), mx = Math.max(r, g, b), mn = Math.min(r, g, b), d = mx - mn;
  let h = d === 0 ? 0 : mx === r ? ((g - b) / d) % 6 : mx === g ? (b - r) / d + 2 : (r - g) / d + 4;
  h = ((h * 60) + 360) % 360 / 360; const s0 = mx === 0 ? 0 : d / mx;
  if (s0 < 0.15) return ["#0A0A0A", "#D9D9D9", "#3A3A3A", "#F2F2F2", "#1A1A1A"];
  const hx = (hh, ss, vv) => { const f = n => { const k = (n + hh * 6) % 6; return vv - vv * Math.min(1, ss) * Math.max(0, Math.min(k, 4 - k, 1)); }; return "#" + [f(5), f(3), f(1)].map(x => Math.round(Math.max(0, Math.min(1, x)) * 255).toString(16).padStart(2, "0")).join(""); };
  const ss = Math.max(s0, 0.6);
  return [hx(h, ss * .9, .11), hx(h, ss, .95), hx(h, ss * .85, .40), hx(h, ss * .35, .94), hx(h, ss * .8, .33)];
};

let layers = "", camLayers = "", ops = "";
const cues = [];   // sons des nouveaux blocs -> cues.json -> mix.py
// V() = visibilité en fonction pure du temps (4 fromTo qui se suivent) : le rendu parallèle peut sauter dans le désordre
// out = sortie douce en s (power2.in) au lieu d'une disparition sèche (NN/g, Ben Marriott)
const V = (sel, a, b, from = "{}", to = "{}", fin = 0.12, out = 0) => { ops += `V("${sel}",${a.toFixed(3)},${b.toFixed(3)},${from},${to},${fin},${out});`; };
// F() = une animation à l'instant t (to sans accolades) ; l'état avant t = celui du CSS
// strokeDashoffset : autoRound:false OBLIGATOIRE : GSAP arrondit au px entier, et avec pathLength=1 le tracé sautait de vide à plein
const F = (sel, from, to, t) => { ops += `tl.fromTo("${sel}",${from},{${to},immediateRender:false${/strokeDashoffset/.test(to) ? ",autoRound:false" : ""}},${(+t).toFixed(3)});`; };
// H() = tient un état de 0 à t (quand l'état de départ n'est pas exprimable en CSS, ex. yPercent)
const H = (sel, state, t) => { ops += `tl.fromTo("${sel}",${state},Object.assign(${state},{duration:${Math.max(+t, 0.001).toFixed(3)},immediateRender:false}),0);`; };
// compteur qui défile (texte remplacé à chaque image), format français 12 400
const COUNT = (id, to, t, d, dec = 0, ease = "power2.out") => { ops += `(function(){var o={v:0},el=document.getElementById("${id}");tl.fromTo(o,{v:0},{v:${to},duration:${d.toFixed(3)},ease:"${ease}",immediateRender:false,onUpdate:function(){el.textContent=o.v.toFixed(${dec}).replace(".",",").replace(/\\B(?=(\\d{3})+(?!\\d))/g,"\\u202f")}},${t.toFixed(3)});})();`; };
// coup de zoom d'impact : COUPÉ (les zooms brusques font saccader, « ça sort de la vidéo »)
const PUNCH = () => {};

// ---------- caméra : zoom LENT et doux seulement quand l'idée change (fin de phrase + au moins 5 s depuis le dernier),
//            large / serré en alternance, transition 1,4 s sinusoïdale puis dérive lente. Jamais de saut de cadre. ----------
const cuts = [0];
// écart mini entre 2 zooms : 5 s dans le hook (0-7 s), 8 s ensuite (mesuré 9,6-14,5 s sur des reels pros en face cam posée)
// rythme de la DA (Style Lab) : zoomGap = [écart dans le hook, écart ensuite] ; posé = [5, 8] (défaut), nerveux = [2.5, 4]
const ZG = plan.zoomGap || DA.zoomGap || [5, 8];
W.forEach((w, i) => { if (i && /[.!?]$/.test(W[i - 1].text) && w.t - cuts[cuts.length - 1] > (w.t < 7 ? ZG[0] : ZG[1])) cuts.push(+(w.t - 0.3).toFixed(3)); });
const lvl = [1.0, 1.07], DRIFT = 1.015, MOVE = 1.4;
// plan.zoom = false (famille « À plusieurs », podcast.py) : pas de zoom, c'est l'alternance split / plein écran qui donne le rythme
if (plan.zoom !== false) cuts.forEach((t, i) => {
  const d = (cuts[i + 1] ?? dur) - t, s = lvl[i % 2], from = i ? lvl[(i - 1) % 2] * DRIFT : s, mv = i ? Math.min(MOVE, d / 2) : 0;
  if (mv) ops += `tl.fromTo("#camwrap",{scale:${from.toFixed(4)}},{scale:${s},duration:${mv.toFixed(3)},ease:"sine.inOut",force3D:true,immediateRender:false},${t.toFixed(3)});`;
  ops += `tl.fromTo("#camwrap",{scale:${s}},{scale:${(s * DRIFT).toFixed(4)},duration:${(d - mv).toFixed(3)},ease:"none",force3D:true,immediateRender:false},${(t + mv).toFixed(3)});`;
});

// ---------- chiffres géants derrière la tête ----------
// compteur (recette officielle HyperFrames counting-dynamic-scale, greffe GitHub) : le chiffre GROSSIT de 55 % à 100 % pendant
// qu'il compte (même durée, même ease power3.out), chiffres à chasse fixe dans une boîte fixe (pas de tremblement 9 -> 10 -> 100),
// le suffixe arrive APRÈS le compte (son propre temps). Durée 1,2-2 s si la place le permet : en dessous de 0,8 s, ça se lit comme un flash.
(plan.numbers || []).forEach((n, i) => {
  const cd = n.count ? Math.max(0.6, Math.min(2.0, n.end - n.start - 0.6)) : 0, nc = String(n.count ?? "").length;
  camLayers += `<div class="num" id="n${i}"><span id="n${i}v"${n.count ? ` class="nct" style="min-width:calc(${nc}ch - ${nc * 12}px)"` : ""}>${esc(n.text)}</span>${n.suffix ? `<span class="suf" id="n${i}s">${esc(n.suffix)}</span>` : ""}</div>`;
  V(`#n${i}`, n.start, n.end, n.count ? `{filter:"blur(24px)"}` : `{scale:1.18,filter:"blur(24px)"}`, n.count ? `{filter:"blur(0px)",ease:"power3.out"}` : `{scale:1,filter:"blur(0px)",ease:"power3.out"}`, 0.32, SOFT(n.end, 0.25));
  if (n.count) {
    ops += `(function(){var o={v:0},el=document.getElementById("n${i}v");tl.fromTo(o,{v:0},{v:${n.count},duration:${cd.toFixed(3)},ease:"power3.out",immediateRender:false,onUpdate:function(){el.textContent=Math.round(o.v)}},${n.start.toFixed(3)});})();`;
    F(`#n${i}v`, "{scale:.55}", `scale:1,duration:${cd.toFixed(3)},ease:"power3.out"`, n.start);
    if (n.suffix) { H(`#n${i}s`, "{opacity:0,y:30}", n.start + cd); F(`#n${i}s`, "{opacity:0,y:30}", `opacity:1,y:0,duration:.3,ease:"expo.out"`, n.start + cd); }
  }
  if (n.fg) camLayers += `<video id="fg${i}" class="clip fg" src="${n.fg}" muted playsinline preload="auto" data-start="${n.fgStart.toFixed(3)}" data-duration="${(n.fgEnd - n.fgStart).toFixed(3)}" data-track-index="${2 + i}" data-has-audio="false"></video>`;
});

// ---------- MOTION DESIGN derrière la personne détourée (famille « Green screen », source.py -> plan.motion) ----------
//            univers = celui de la vidéo (pièce sombre, LED bleue), zéro visage, mouvements expo sans rebond, la personne repasse devant.
const BADGE = (id, sz) => `<svg id="${id}" class="mo-badge" width="${sz}" height="${sz}" viewBox="0 0 40 40"><path fill="${ACC}" d="M20 1.5l4.3 3.1 5.3-.3 1.6 5 4.4 3-1.6 5.1 1.6 5.1-4.4 3-1.6 5-5.3-.3L20 38.5l-4.3-3.1-5.3.3-1.6-5-4.4-3 1.6-5.1-1.6-5.1 4.4-3 1.6-5 5.3.3z"/><path fill="none" stroke="#fff" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round" d="M13 20.5l4.6 4.6L27.5 15"/></svg>`;
const MOTION = {
  // boîte de messages : les messages arrivent, puis celui avec la coche bleue passe en tête et ressort (« tu vas être mis en valeur »)
  dm(m, k) {
    const S = m.start, E = m.end, H = m.highlight ?? (S + (E - S) * 0.55), id = `mo${k}`;
    const W = [62, 48, 70, 54, 40], P = [80, 66, 58, 74, 52], AV = ["#3a4566", "#4a3f5c", "#2f4f5a", "#5a4a3a", "#3f5a46"];
    let rows = "";
    W.forEach((w, j) => rows += `<div class="mo-row" id="${id}r${j}" style="top:${118 + (j + 1) * 104}px"><i class="mo-av" style="background:${AV[j]}"></i><div class="mo-ln"><b style="width:${w}%"></b><s style="width:${P[j]}%"></s></div><em>${j + 2} min</em></div>`);
    const vip = `<div class="mo-row mo-vip" id="${id}v" style="top:118px"><i class="mo-av" style="background:linear-gradient(135deg,${ACC},#1c2a55)"></i><div class="mo-ln"><b style="width:46%"></b>${BADGE(id + "b", 34)}<s style="width:72%"></s></div><em>à l'instant</em></div>`;
    camLayers += `<div class="mo" id="${id}"><div class="mo-led"></div><div class="mo-panel" id="${id}p"><div class="mo-h">${esc(m.title || "Messages")}</div>${vip}${rows}</div></div>`;
    V(`#${id}`, S, E, "{}", "{}", 0.2);
    F(`#${id}p`, `{y:60,opacity:0}`, `y:0,opacity:1,duration:.7,ease:"expo.out"`, S);
    F(`#${id}p`, `{scale:1}`, `scale:1.04,duration:${(E - S).toFixed(3)},ease:"none"`, S);   // dérive lente : jamais figé
    W.forEach((_, j) => F(`#${id}r${j}`, `{opacity:0,x:-30}`, `opacity:1,x:0,duration:.45,ease:"power3.out"`, S + 0.25 + 0.14 * j));
    F(`#${id}v`, `{opacity:0,y:-40}`, `opacity:1,y:0,duration:.6,ease:"expo.out"`, H - 0.7);
    F(`#${id}b`, `{scale:0,rotation:-25}`, `scale:1,rotation:0,duration:.55,ease:"expo.out"`, H - 0.45);
    F(`#${id}v`, `{scale:1}`, `scale:1.06,duration:.6,ease:"power2.inOut"`, H);
    W.forEach((_, j) => F(`#${id}r${j}`, `{opacity:1}`, `opacity:.32,duration:.5,ease:"power2.inOut"`, H));
  },
  // profil (avatar SANS visage) : la coche bleue apparaît à côté du nom, puis un bandeau « rassurant » (quelqu'un arrive sur ta page)
  profile(m, k) {
    const S = m.start, E = m.end, id = `mo${k}`, d = E - S;
    camLayers += `<div class="mo" id="${id}"><div class="mo-led"></div><div class="mo-panel mo-prof" id="${id}p">
      <div class="mo-pav"></div><div class="mo-pname"><b>${esc(m.name || "ton_compte")}</b>${BADGE(id + "b", 46)}</div>
      <div class="mo-pstats"><div><b>412</b><span>publications</span></div><div><b>28,4 k</b><span>abonnés</span></div><div><b>310</b><span>suivi(e)s</span></div></div>
      <div class="mo-pbtn">Suivre</div><div class="mo-ptag" id="${id}t">${esc(m.tag || "Compte vérifié")}</div></div></div>`;
    V(`#${id}`, S, E, "{}", "{}", 0.2);
    F(`#${id}p`, `{y:60,opacity:0}`, `y:0,opacity:1,duration:.7,ease:"expo.out"`, S);
    F(`#${id}p`, `{scale:1}`, `scale:1.04,duration:${d.toFixed(3)},ease:"none"`, S);
    F(`#${id}b`, `{scale:0,rotation:-25}`, `scale:1,rotation:0,duration:.6,ease:"expo.out"`, S + d * 0.35);
    F(`#${id}t`, `{y:20,opacity:0}`, `y:0,opacity:1,duration:.5,ease:"expo.out"`, S + d * 0.62);
  },
  // UNE phrase « pas plus de X, en revanche plus de Y » = UN bloc : la barre X reste à plat, la barre Y monte au moment du pivot
  compare(m, k) {
    const S = m.start, E = m.end, id = `mo${k}`, P = m.pivot ?? (S + (E - S) * 0.5);
    const row = (j, lab, tag) => `<div class="mo-cr" id="${id}r${j}"><div class="mo-crl"><b>${esc(lab)}</b><span id="${id}t${j}">${esc(tag)}</span></div><div class="mo-gt"><div class="mo-gf" id="${id}g${j}" style="${j ? "" : "background:rgba(255,255,255,.45)"}"></div></div></div>`;
    camLayers += `<div class="mo" id="${id}"><div class="mo-led"></div><div class="mo-panel" id="${id}p" style="height:560px">
      ${row(0, m.a || "Visibilité", m.at || "= pareil")}${row(1, m.b || "Crédibilité", m.bt || "↑ en hausse")}</div></div>`;
    V(`#${id}`, S, E, "{}", "{}", 0.2);
    F(`#${id}p`, `{y:60,opacity:0}`, `y:0,opacity:1,duration:.7,ease:"expo.out"`, S);
    F(`#${id}p`, `{scale:1}`, `scale:1.04,duration:${(E - S).toFixed(3)},ease:"none"`, S);
    F(`#${id}r0`, `{opacity:0,x:-40}`, `opacity:1,x:0,duration:.5,ease:"expo.out"`, S + 0.3);
    F(`#${id}g0`, `{width:"10%"}`, `width:"24%",duration:.9,ease:"power2.out"`, S + 0.5);
    F(`#${id}r1`, `{opacity:0,x:-40}`, `opacity:1,x:0,duration:.5,ease:"expo.out"`, P - 0.2);
    F(`#${id}g1`, `{width:"10%"}`, `width:"92%",duration:${Math.max(1, E - P - 0.6).toFixed(3)},ease:"power2.inOut"`, P + 0.1);
    F(`#${id}r0`, `{opacity:1}`, `opacity:.45,duration:.4,ease:"power2.inOut"`, P);
  },
  // astuce prix : l'appli (plus chère, frais des stores) puis le Web / PC qui s'allume « prix réduit »
  webapp(m, k) {
    const S = m.start, E = m.end, id = `mo${k}`;
    const LAPTOP = `<svg viewBox="0 0 48 48" width="120" height="120"><rect x="9" y="10" width="30" height="20" rx="2.5" fill="none" stroke="#fff" stroke-width="3"/><path d="M4 36h40" stroke="#fff" stroke-width="3.4" stroke-linecap="round"/></svg>`;
    const PHONE = `<svg viewBox="0 0 48 48" width="120" height="120"><rect x="15" y="6" width="18" height="36" rx="4" fill="none" stroke="#fff" stroke-width="3"/><circle cx="24" cy="36.5" r="1.8" fill="#fff"/></svg>`;
    camLayers += `<div class="mo" id="${id}"><div class="mo-led"></div>
      <div class="mo-wc mo-wl" id="${id}a">${LAPTOP}<b>${esc(m.web || "Sur PC")}</b><span class="mo-wt mo-wok">${esc(m.webTag || "prix réduit")}</span></div>
      <div class="mo-wc mo-wr" id="${id}b">${PHONE}<b>${esc(m.app || "Sur l'appli")}</b><span class="mo-wt">${esc(m.appTag || "+ frais des stores")}</span></div></div>`;
    V(`#${id}`, S, E, "{}", "{}", 0.2);
    F(`#${id}b`, `{y:50,opacity:0}`, `y:0,opacity:1,duration:.6,ease:"expo.out"`, S + 0.2);
    F(`#${id}a`, `{y:50,opacity:0}`, `y:0,opacity:1,duration:.6,ease:"expo.out"`, (m.webAt ?? S + (E - S) * 0.5) - 0.3);
    F(`#${id}a`, `{scale:1}`, `scale:1.08,duration:.6,ease:"power2.inOut"`, m.webAt ?? S + (E - S) * 0.55);
    F(`#${id}b`, `{opacity:1}`, `opacity:.4,duration:.5,ease:"power2.inOut"`, m.appAt ?? S + (E - S) * 0.75);
  },
  // « Pour qui ? » : la mauvaise raison se fait barrer, la bonne s'allume (annonce les 2 passages suivants)
  versus(m, k) {
    const S = m.start, E = m.end, id = `mo${k}`, d = E - S;
    camLayers += `<div class="mo" id="${id}"><div class="mo-led"></div><div class="mo-vq" id="${id}q">${esc(m.q || "Pour qui ?")}</div>
      <div class="mo-vr" id="${id}n"><i class="mo-vi mo-vx">✕</i><span>${esc(m.no || "Pour frimer")}<b class="mo-vs" id="${id}s"></b></span></div>
      <div class="mo-vr mo-vy" id="${id}y"><i class="mo-vi mo-vc">✓</i><span>${esc(m.yes || "Pour les entrepreneurs")}</span></div></div>`;
    V(`#${id}`, S, E, "{}", "{}", 0.15);
    F(`#${id}q`, `{y:30,opacity:0}`, `y:0,opacity:1,duration:.5,ease:"expo.out"`, S);
    F(`#${id}n`, `{x:-80,opacity:0}`, `x:0,opacity:1,duration:.5,ease:"expo.out"`, S + d * 0.18);
    F(`#${id}s`, `{width:"0%"}`, `width:"100%",duration:.35,ease:"power2.inOut"`, S + d * 0.45);
    F(`#${id}n`, `{opacity:1}`, `opacity:.45,duration:.35,ease:"power2.inOut"`, S + d * 0.5);
    F(`#${id}y`, `{x:80,opacity:0}`, `x:0,opacity:1,duration:.5,ease:"expo.out"`, S + d * 0.5);
  },
  // page qui défile (y0 -> y1) ou image qui zoome / dézoome (push, cy) : GSAP au sous-pixel = fluide (ffmpeg saccadait)
  img(m, k) {
    const S = m.start, E = m.end, d = (E - S).toFixed(3), id = `mo${k}`;
    if (m.push == null) {
      camLayers += `<div class="mo moimg" id="${id}"><img class="moi-page" id="${id}i" src="${m.src}?b=${k}"></div>`;
      F(`#${id}i`, `{y:${-(m.y0 || 0)}}`, `y:${-(m.y1 ?? m.y0 ?? 0)},duration:${d},ease:"sine.inOut",force3D:true`, S);
    } else {
      const p = m.push, z0 = p > 0 ? 1 : 1 - p, z1 = p > 0 ? 1 + p : 1, oy = ((m.cy ?? 0.3) * 100).toFixed(1);
      camLayers += `<div class="mo moimg" id="${id}"><img class="moi-cover" id="${id}i" src="${m.src}?b=${k}" style="transform-origin:50% ${oy}%"></div>`;
      F(`#${id}i`, `{scale:${z0}}`, `scale:${z1},duration:${d},ease:"sine.inOut",force3D:true`, S);
    }
    V(`#${id}`, S, E, "{}", "{}", 0.01);
  },
  // courbe de portée qui reste plate (« ça ne va pas te faire gagner plus de visibilité ») : l'espoir (pointillés) monte, la réalité (bleu) reste à plat
  chart(m, k) {
    const S = m.start, E = m.end, id = `mo${k}`;
    camLayers += `<div class="mo" id="${id}"><div class="mo-led"></div><div class="mo-panel" id="${id}p"><div class="mo-h">${esc(m.title || "Portée")}</div>
      <div class="mo-kpi" id="${id}k">+0,3 %</div><div class="mo-kpil">${esc(m.label || "visibilité sur 30 jours")}</div>
      <svg class="mo-chart" viewBox="0 0 760 360"><g stroke="rgba(255,255,255,.08)" stroke-width="2"><line x1="0" y1="90" x2="760" y2="90"/><line x1="0" y1="180" x2="760" y2="180"/><line x1="0" y1="270" x2="760" y2="270"/></g>
      <path id="${id}h" pathLength="1" d="M10 300 C 200 280, 360 200, 520 120 S 700 40, 750 30" fill="none" stroke="rgba(255,255,255,.45)" stroke-width="5" stroke-dasharray="0.03 0.025" stroke-linecap="round"/>
      <path id="${id}r" pathLength="1" d="M10 300 C 120 296, 200 304, 300 299 S 480 296, 560 301 S 700 298, 750 300" fill="none" stroke="${ACC}" stroke-width="8" stroke-linecap="round" stroke-dasharray="1" stroke-dashoffset="1"/></svg>
      <div class="mo-leg"><i style="background:rgba(255,255,255,.45)"></i>${esc(m.hope || "ce que tu espères")}<i style="background:${ACC}"></i>${esc(m.real || "la réalité")}</div></div></div>`;
    V(`#${id}`, S, E, "{}", "{}", 0.2);
    F(`#${id}p`, `{y:60,opacity:0}`, `y:0,opacity:1,duration:.7,ease:"expo.out"`, S);
    F(`#${id}p`, `{scale:1}`, `scale:1.04,duration:${(E - S).toFixed(3)},ease:"none"`, S);
    F(`#${id}h`, `{opacity:0}`, `opacity:1,duration:.8,ease:"power2.out"`, S + 0.3);
    F(`#${id}r`, `{strokeDashoffset:1}`, `strokeDashoffset:0,duration:${Math.max(1, (E - S) * 0.6).toFixed(3)},ease:"power1.inOut"`, S + 0.5);
    F(`#${id}k`, `{opacity:0,y:20}`, `opacity:1,y:0,duration:.5,ease:"expo.out"`, S + 0.6);
  },
  // crédibilité : la coche bleue se dessine, puis la jauge « confiance » se remplit et 5 étoiles s'allument
  badge(m, k) {
    const S = m.start, E = m.end, id = `mo${k}`;
    const stars = [0, 1, 2, 3, 4].map(j => `<svg id="${id}s${j}" class="mo-star" viewBox="0 0 24 24"><path fill="${ACC}" d="M12 2l2.9 6.5 7.1.6-5.4 4.7 1.6 7L12 17l-6.2 3.8 1.6-7L2 9.1l7.1-.6z"/></svg>`).join("");
    camLayers += `<div class="mo" id="${id}"><div class="mo-led"></div>
      <svg class="mo-seal" id="${id}c" viewBox="0 0 40 40"><path fill="${ACC}" d="M20 1.5l4.3 3.1 5.3-.3 1.6 5 4.4 3-1.6 5.1 1.6 5.1-4.4 3-1.6 5-5.3-.3L20 38.5l-4.3-3.1-5.3.3-1.6-5-4.4-3 1.6-5.1-1.6-5.1 4.4-3 1.6-5 5.3.3z"/>
      <path id="${id}ck" pathLength="1" fill="none" stroke="#fff" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round" d="M13 20.5l4.6 4.6L27.5 15" stroke-dasharray="1" stroke-dashoffset="1"/></svg>
      <div class="mo-gauge"><div class="mo-gl">${esc(m.label || "Confiance")}</div><div class="mo-gt"><div class="mo-gf" id="${id}g"></div></div><div class="mo-stars">${stars}</div></div></div>`;
    V(`#${id}`, S, E, "{}", "{}", 0.2);
    F(`#${id}c`, `{scale:.4,opacity:0,rotation:-20}`, `scale:1,opacity:1,rotation:0,duration:.8,ease:"expo.out"`, S + 0.1);
    F(`#${id}c`, `{scale:1}`, `scale:1.06,duration:${(E - S - 0.9).toFixed(3)},ease:"none"`, S + 0.9);
    F(`#${id}ck`, `{strokeDashoffset:1}`, `strokeDashoffset:0,duration:.5,ease:"power2.out"`, S + 0.55);
    F(`#${id}g`, `{width:"14%"}`, `width:"93%",duration:${Math.max(1, (E - S) * 0.55).toFixed(3)},ease:"power2.inOut"`, S + 0.8);
    [0, 1, 2, 3, 4].forEach(j => F(`#${id}s${j}`, `{opacity:.15,scale:.7}`, `opacity:1,scale:1,duration:.35,ease:"expo.out"`, S + 1.1 + 0.18 * j));
  },
  // ouverture de démo : l'IA et Instagram se connectent (pas de logo de marque), des données circulent, puis « en moins de 20 s »
  connect(m, k) {
    const S = m.start, E = m.end, id = `mo${k}`;
    // les 2 tuiles glissent depuis les bords dans un cache à 65 px (zones mortes : elles naissent au bord de la zone sûre, jamais dans la marge)
    camLayers += `<div class="mo" id="${id}"><div class="mo-led"></div><div class="mo-cw"><div class="mo-cwi">
      <div class="mo-tile mo-ai" id="${id}a"><svg viewBox="0 0 40 40" width="150" height="150"><path fill="#fff" d="M20 3l3.2 12.6L36 19l-12.8 3.4L20 37l-3.2-14.6L4 19l12.8-3.4z"/></svg><span>${esc(m.left || "IA")}</span></div>
      <div class="mo-tile mo-ig" id="${id}b"><svg viewBox="0 0 40 40" width="150" height="150"><rect x="6" y="6" width="28" height="28" rx="8" fill="none" stroke="#fff" stroke-width="3.2"/><circle cx="20" cy="20" r="6.5" fill="none" stroke="#fff" stroke-width="3.2"/><circle cx="28" cy="12" r="2" fill="#fff"/></svg><span>${esc(m.right || "Instagram")}</span></div></div></div>
      <svg class="mo-link" viewBox="0 0 300 20"><path id="${id}l" pathLength="1" d="M0 10 H300" stroke="${ACC}" stroke-width="6" stroke-linecap="round" stroke-dasharray="1" stroke-dashoffset="1"/></svg>
      ${[0, 1, 2].map(j => `<i class="mo-dot" id="${id}d${j}"></i>`).join("")}
      <div class="mo-pill" id="${id}t">${esc(m.pill || "en moins de 20 secondes")}</div></div>`;
    V(`#${id}`, S, E, "{}", "{}", 0.2);
    F(`#${id}a`, `{x:-260,opacity:0}`, `x:0,opacity:1,duration:.8,ease:"expo.out"`, S + 0.1);
    F(`#${id}b`, `{x:260,opacity:0}`, `x:0,opacity:1,duration:.8,ease:"expo.out"`, S + 0.25);
    F(`#${id}l`, `{strokeDashoffset:1}`, `strokeDashoffset:0,duration:.6,ease:"power2.out"`, S + 0.9);
    const L = E - S - 1.6;
    // un point = 3 fromTo (apparaît, traverse le lien, s'efface), répété : pas de keyframes (fromTo seulement, règle HyperFrames)
    [0, 1, 2].forEach(j => { for (let r = 0; r * 1.2 + j * 0.3 + 1 < L; r++) { const t0 = S + 1.5 + r * 1.2 + j * 0.3;
      F(`#${id}d${j}`, `{opacity:0}`, `opacity:1,duration:.12,ease:"none"`, t0);
      F(`#${id}d${j}`, `{x:0}`, `x:300,duration:.8,ease:"sine.inOut"`, t0);
      F(`#${id}d${j}`, `{opacity:1}`, `opacity:0,duration:.12,ease:"none"`, t0 + 0.8); } });
    F(`#${id}t`, `{y:30,opacity:0}`, `y:0,opacity:1,duration:.6,ease:"expo.out"`, S + Math.min(m.pillAt ?? (E - S) * 0.6, E - S - 0.8));
    F(`#${id}a`, `{scale:1}`, `scale:1.04,duration:${(E - S).toFixed(3)},ease:"none"`, S);
  },
  // anneau qui se remplit jusqu'à `value` % (recettes officielles stat-bars-and-fills + counting-dynamic-scale, greffe GitHub) :
  // anneau et compteur partagent durée (≥ 0,8 s) et ease power3.out = un seul temps ; libellé en grosses capitales avant le pic, suffixe après
  ring(m, k) {
    const S = m.start, E = m.end, id = `mo${k}`, v = Math.max(0, Math.min(100, m.value ?? 92)), cd = Math.max(0.8, Math.min(2.0, E - S - 1.1));
    camLayers += `<div class="mo" id="${id}"><div class="mo-led"></div><div class="mo-rw" id="${id}w">
      <svg class="mo-ring" id="${id}g" viewBox="0 0 200 200"><circle cx="100" cy="100" r="84" fill="none" stroke="rgba(255,255,255,.10)" stroke-width="13"/>
      <path id="${id}r" pathLength="1" d="M100 16 A84 84 0 1 1 100 184 A84 84 0 1 1 100 16" fill="none" stroke="${ACC}" stroke-width="13" stroke-linecap="round" stroke-dasharray="1" stroke-dashoffset="1"/></svg>
      <div class="mo-rv"><span class="mo-rn" id="${id}n" style="min-width:${String(m.count ?? v).length}ch"><span id="${id}v">0</span></span><i id="${id}u">${esc(m.suffix ?? "%")}</i></div>
      ${m.label ? `<div class="mo-rl" id="${id}l">${esc(m.label)}</div>` : ""}</div></div>`;
    V(`#${id}`, S, E, "{}", "{}", 0.2);
    F(`#${id}g`, `{scale:.9,opacity:0,filter:"blur(12px)"}`, `scale:1,opacity:1,filter:"blur(0px)",duration:.6,ease:"expo.out"`, S);
    F(`#${id}w`, `{scale:1}`, `scale:1.04,duration:${(E - S).toFixed(3)},ease:"none"`, S);   // dérive lente : jamais figé (règle du skill)
    F(`#${id}r`, "{strokeDashoffset:1}", `strokeDashoffset:${(1 - v / 100).toFixed(3)},duration:${cd.toFixed(3)},ease:"power3.out"`, S + 0.3);
    F(`#${id}n`, "{scale:.55}", `scale:1,duration:${cd.toFixed(3)},ease:"power3.out"`, S + 0.3);
    COUNT(`${id}v`, m.count ?? v, S + 0.3, cd, m.decimals || 0, "power3.out");
    H(`#${id}u`, "{opacity:0,y:16}", S + 0.3 + cd); F(`#${id}u`, "{opacity:0,y:16}", `opacity:1,y:0,duration:.3,ease:"expo.out"`, S + 0.3 + cd);
    if (m.label) { H(`#${id}l`, "{opacity:0,y:20}", S + 0.3 + cd * 0.35); F(`#${id}l`, "{opacity:0,y:20}", `opacity:1,y:0,duration:.5,ease:"expo.out"`, S + 0.3 + cd * 0.35); }
  },
  // barres qui montent depuis la ligne de base (recette officielle stat-bars-and-fills) : les barres grises posent le contexte,
  // pause de 0,35 s (« virgule dramatique », motion-doctrine), puis la DERNIÈRE barre (accent) monte avec son chiffre qui compte = le résultat
  bars(m, k) {
    const S = m.start, E = m.end, id = `mo${k}`, vals = (m.values || [14, 18, 22, 61]).slice(0, 5), n = vals.length, mx = Math.max(...vals) || 1;
    const labs = m.labels || [], bw = n > 4 ? 120 : 150, t0 = S + 0.35, grey = t0 + 0.08 * Math.max(0, n - 2) + 0.6, ta = grey + 0.35, cd = Math.max(0.8, Math.min(1.6, E - ta - 0.5));
    const cols = vals.map((x, j) => `<div class="mo-bc"><div class="mo-bar${j === n - 1 ? " mo-bac" : ""}" id="${id}b${j}" style="width:${bw}px;height:${Math.max(16, Math.round(x / mx * 420))}px"></div>${labs[j] != null ? `<div class="mo-bl" id="${id}l${j}">${esc(labs[j])}</div>` : ""}</div>`).join("");
    const hasV = typeof m.value === "number";
    camLayers += `<div class="mo" id="${id}"><div class="mo-led"></div><div class="mo-bw" id="${id}w">
      ${m.title ? `<div class="mo-bt" id="${id}t">${esc(m.title)}</div>` : ""}
      ${hasV ? `<div class="mo-bv" id="${id}n">${esc(m.prefix || "")}<span id="${id}v">0</span>${esc(m.suffix || "")}</div>` : ""}
      <div class="mo-bars">${cols}</div></div></div>`;
    V(`#${id}`, S, E, "{}", "{}", 0.2);
    F(`#${id}w`, `{scale:1}`, `scale:1.04,duration:${(E - S).toFixed(3)},ease:"none"`, S);
    if (m.title) { H(`#${id}t`, "{opacity:0,y:-24}", S + 0.05); F(`#${id}t`, "{opacity:0,y:-24}", `opacity:1,y:0,duration:.5,ease:"expo.out"`, S + 0.05); }
    vals.forEach((_, j) => { const tj = j < n - 1 ? t0 + 0.08 * j : ta;
      if (j < n - 1) F(`#${id}b${j}`, "{scaleY:0}", `scaleY:1,duration:.6,ease:"power3.out"`, tj);
      if (labs[j] != null) { H(`#${id}l${j}`, "{opacity:0}", tj); F(`#${id}l${j}`, "{opacity:0}", `opacity:1,duration:.3,ease:"power2.out"`, tj); } });
    F(`#${id}b${n - 1}`, "{scaleY:0}", `scaleY:1,duration:${cd.toFixed(3)},ease:"power3.out"`, ta);
    if (hasV) {   // opacité en 0,3 s, taille sur toute la durée du compte (sinon le chiffre reste grisé pendant qu'il compte)
      H(`#${id}n`, "{opacity:0,scale:.55}", ta);
      F(`#${id}n`, "{opacity:0}", `opacity:1,duration:.3,ease:"power2.out"`, ta);
      F(`#${id}n`, "{scale:.55}", `scale:1,duration:${cd.toFixed(3)},ease:"power3.out"`, ta);
      COUNT(`${id}v`, m.value, ta, cd, m.decimals || 0, "power3.out");
    }
  },
};
// zones mortes Insta : chaque bloc a été dessiné à partir de ~150 px. Boîte [haut, bas] mesurée sur tout le bloc
// (dérive comprise) ; on le recale à 280 px. Plancher = 890 px (10 px d'air au-dessus des sous-titres du green screen, y 900) ou son bas
// d'origine s'il était plus bas (dm, chart, bars : jamais plus bas qu'avant). Simple descente s'il y a la place, sinon descente + réduction
// proportionnelle (dm, chart -16 %, bars -17 %, profile -16 %, ring -12 %). Le fond et la LED débordent toujours.
const MOBOX = { dm: [150, 940], profile: [150, 877], compare: [150, 732], webapp: [209, 800], versus: [190, 720], chart: [150, 940],
                badge: [161, 728], connect: [294, 777], ring: [154, 849], bars: [144, 931] };
const MO_TOP = 280, MO_FLOOR = 890;
(plan.motion || []).forEach((m, k) => {
  if (!MOTION[m.type]) { console.log(`motion inconnu : ${m.type}`); return; }
  const from = camLayers.length;
  MOTION[m.type](m, k);
  const box = MOBOX[m.type], led = `<div class="mo" id="mo${k}"><div class="mo-led"></div>`, at = camLayers.indexOf(led, from);
  if (box && at >= 0 && box[0] < MO_TOP) {
    const [T, B] = box, s = Math.min(1, (Math.max(MO_FLOOR, B) - MO_TOP) / (B - T)), ty = MO_TOP - T * s;
    camLayers = camLayers.slice(0, at + led.length) + `<div class="mo-safe" style="transform:translateY(${ty.toFixed(1)}px) scale(${s.toFixed(4)})">`
      + camLayers.slice(at + led.length).replace(/<\/div>\s*$/, "") + `</div></div>`;
  }
  // la personne détourée repasse devant le motion design (même échelle et place que source.py : bas, centrée)
  camLayers += `<div class="mo-fgw" style="transform:scale(${m.scale || 0.66})"><video id="mofg${k}" class="clip fg" src="${m.fg}" muted playsinline preload="auto" data-start="${m.start.toFixed(3)}" data-duration="${(m.end - m.start).toFixed(3)}" data-track-index="${60 + k}" data-has-audio="false"></video></div>`;
});

// ---------- mot géant derrière la tête (guide OPUS) : serif, lettre par lettre depuis le centre comme sorti d'une fente,
//            2 copies en contour qui dérivent en dessous, petit zoom d'impact, aspiration inversée calée sur le mot ----------
bigwords.forEach((w, i) => {
  const ch = [...String(w.text)], mid = (ch.length - 1) / 2, d = w.end - w.start;
  // taille = le mot tient dans 820 px (mesure exacte de la police si Pillow est là, sinon 0,47 em par lettre) : avec le zoom
  // d'impact il reste entre les marges de 65 px (zones mortes Insta ; avant 900 px = « dangereux » mordait les bords)
  const sans = w.font === "sans";
  let em = 0.47 * ch.length;
  try { em = +execFileSync("python3", ["-c", "import sys;from PIL import ImageFont;f=ImageFont.truetype(sys.argv[1],1000)\ntry: f.set_variation_by_axes([800])\nexcept Exception: pass\nprint(f.getlength(sys.argv[2])/1000)", join("fonts", sans ? DA.fonts.sans : DA.fonts.serif), sans ? String(w.text).toUpperCase() : String(w.text)]).toString() * 1.06; } catch {}
  const fs = w.size || Math.round(Math.min(sans ? 205 : 330, (sans ? 820 - 2 * ch.length : 820) / em));
  const letters = ch.map((c, k) => `<span class="lm"><span class="lc" id="w${i}c${k}">${c === " " ? "&nbsp;" : esc(c)}</span></span>`).join("");
  // "font": "sans" = police des sous-titres en capitales grasses (« VISIBILITÉ » derrière la tête) ; défaut serif italique
  const sty = sans ? `font-family:Mont;font-style:normal;font-weight:800;text-transform:uppercase;letter-spacing:2px;` : "";
  // DERRIÈRE la tête (Style Lab R4) : le bas du mot passe sous le haut des cheveux (headtop.py) ; avant, 170 px fixe = le mot flottait au-dessus
  const fsz = fs;   // sans : mesuré dans sa propre police (avant : 0,62 x la taille serif, pas mesuré = débordait)
  let top = w.top;
  if (top == null) {
    try { const ht = +execFileSync("python3", [join(SKILL, "scripts", "headtop.py"), plan.cam, String(w.start), String(w.end)], { stdio: ["ignore", "pipe", "ignore"] }).toString().trim();
          top = Math.max(270, Math.round(ht - 0.7 * fsz)); console.log(`mot géant « ${w.text} » : haut de la tête ${ht}px -> top ${top}px`); }
    catch { top = 270; }
  }
  camLayers += `<div class="bigw" id="w${i}" style="${sty}font-size:${fsz}px;top:${top}px"><div class="echo" id="w${i}e2">${esc(w.text)}</div><div class="echo" id="w${i}e1">${esc(w.text)}</div><div class="bwt">${letters}</div></div>`;
  V(`#w${i}`, w.start, w.end, "{}", "{}", 0.001);
  ch.forEach((_, k) => {
    const t = w.start + Math.abs(k - mid) * 0.05;
    H(`#w${i}c${k}`, "{yPercent:110}", t);
    F(`#w${i}c${k}`, "{yPercent:110}", `yPercent:0,duration:.6,ease:"expo.out"`, t);
  });
  F(`#w${i}e1`, "{y:0,opacity:0}", `y:${Math.round(fs * 0.4)},opacity:.5,duration:${d.toFixed(3)},ease:"power2.out"`, w.start + 0.2);
  F(`#w${i}e2`, "{y:0,opacity:0}", `y:${Math.round(fs * 0.8)},opacity:.22,duration:${d.toFixed(3)},ease:"power2.out"`, w.start + 0.3);
  PUNCH(w.start);
  cues.push({ kind: "reverse", at: w.start });
  if (w.fg) camLayers += `<video id="fgw${i}" class="clip fg" src="${w.fg}" muted playsinline preload="auto" data-start="${w.fgStart.toFixed(3)}" data-duration="${(w.fgEnd - w.fgStart).toFixed(3)}" data-track-index="${30 + i}" data-has-audio="false"></video>`;
});

// ---------- ouverture du hook : viseur REC + impact grave (bandes noires seulement si bars: true, déconseillées) ----------
if (plan.hook) {
  const hk = plan.hook, f = hk.focus ?? 750, s = hk.slit ?? 380;
  if (hk.bars === true) {   // bandes noires : testées et rejetées, coupées par défaut
    layers += `<div class="bar" id="barT" style="top:0;height:${f - s / 2}px"></div><div class="bar" id="barB" style="top:${f + s / 2}px;bottom:0"></div>`;
    F("#barT", "{yPercent:0}", `yPercent:-100,duration:.75,ease:"expo.inOut"`, 0.12);
    F("#barB", "{yPercent:0}", `yPercent:100,duration:.75,ease:"expo.inOut"`, 0.12);
  }
  if (hk.rec === true) {   // viseur REC : seulement si la vidéo parle de tournage (« REC, ça n'a rien à voir »)
    const re = hk.recEnd ?? 1.6;
    layers += `<div id="rec"><i class="cn c1"></i><i class="cn c2"></i><i class="cn c3"></i><i class="cn c4"></i><div class="rlab"><b id="rdot"></b>REC</div><div class="rtc" id="rtc">00:00:00</div></div>`;
    V("#rec", 0, re, "{}", "{}", 0.001);
    F("#rdot", "{opacity:1}", `opacity:.15,duration:.4,repeat:${Math.max(1, Math.floor(re / 0.4))},yoyo:true,ease:"none"`, 0);
    ops += `(function(){var o={v:0},el=document.getElementById("rtc");tl.fromTo(o,{v:0},{v:${re},duration:${re},ease:"none",immediateRender:false,onUpdate:function(){var f=Math.floor(o.v*30);el.textContent="00:00:"+String(Math.floor(f/30)).padStart(2,"0")+":"+String(f%30).padStart(2,"0")}},0);})();`;
    F("#rec", "{scale:1.04}", `scale:1,duration:${re},ease:"power1.out"`, 0);
  }
  if (hk.impact !== false) cues.push({ kind: "impact", at: 0 });
}

// ---------- cartons liste plein écran ----------
// zones mortes Insta : une page (2 colonnes) doit tenir entre 540 px et 1480 px. Taille du texte = la plus grande
// (43 px max, le style validé) pour laquelle la plus haute colonne tient dans 925 px (15 px de marge pour la montée d'entrée),
// mesurée avec la vraie police (retours à la ligne compris). 18 lignes longues par page débordaient sous les boutons de l'appli.
const LIST_FIT = `import sys,json
from PIL import ImageFont
d=json.load(sys.stdin);F={}
def font(fs):
  if fs not in F:
    f=ImageFont.truetype(d["font"],fs)
    try: f.set_variation_by_axes([600])
    except Exception: pass
    F[fs]=f
  return F[fs]
def lines(t,fs,w):
  n,cur=1,""
  for wd in t.split():
    nx=(cur+" "+wd).strip()
    if cur and font(fs).getlength(nx)>w: n+=1;cur=wd
    else: cur=nx
  return n
out=[]
for cols in d["pages"]:
  best=24
  for fs in range(43,23,-1):
    h=max(sum(lines(t,fs,d["w"])*fs*1.12 for t in c)+round(30*fs/43)*(len(c)-1) for c in cols if c)
    if h<=d["h"]: best=fs;break
  out.append(best)
print(json.dumps(out))`;
const listFit = pages => { try { return JSON.parse(execFileSync("python3", ["-c", LIST_FIT], { input: JSON.stringify({ font: join("fonts", DA.fonts.sans), w: 453, h: 925,
  pages: pages.map(items => { const h = Math.ceil(items.length / 2); return [items.slice(0, h), items.slice(h)]; }) }) }).toString()); } catch { return pages.map(() => 43); } };
lists.forEach((l, li) => {
  const pages = l.pages || [l.items];
  const pd = (l.end - l.start) / pages.length, fits = listFit(pages);
  fits.forEach((fs, pi) => fs < 43 && console.log(`liste ${li} page ${pi + 1} : texte ${fs} px (au lieu de 43) pour tenir au-dessus de 1480 px`));
  let html = `<div class="list" id="l${li}"><div class="lt"><div class="l1">${esc(l.title[0])}</div><div class="l2">${esc(l.title[1])}</div></div>`;
  pages.forEach((items, pi) => {
    const half = Math.ceil(items.length / 2);
    html += `<div class="page" id="l${li}p${pi}"${fits[pi] < 43 ? ` style="--fs:${fits[pi]}px"` : ""}><div class="col">${items.slice(0, half).map((it, k) => `<div class="it" id="l${li}p${pi}i${k}">${esc(it)}</div>`).join("")}</div>`
          + `<div class="col">${items.slice(half).map((it, k) => `<div class="it" id="l${li}p${pi}i${k + half}">${esc(it)}</div>`).join("")}</div></div>`;
    const a = l.start + pi * pd, b = a + pd;
    V(`#l${li}p${pi}`, a, b, "{}", "{}", 0.001);
    const step = Math.min(0.05, (pd * 0.45) / items.length);
    // cascade (recette officielle waterfall-entry, greffe GitHub) : chaque ligne monte de 40 px en 0,2 s power4.out, flou -> net
    items.forEach((_, k) => ops += `tl.fromTo("#l${li}p${pi}i${k}",{opacity:0,y:40,filter:"blur(6px)"},{opacity:1,y:0,filter:"blur(0px)",duration:.2,ease:"power4.out",immediateRender:false},${(a + 0.12 + k * step).toFixed(3)});`);
  });
  layers += html + `</div>`;
  V(`#l${li}`, l.start, l.end, `{scale:1.04}`, `{scale:1,ease:"power3.out"}`, 0.18, SOFT(l.end, 0.3));
  ops += `tl.fromTo("#l${li} .lt",{opacity:0,y:-20},{opacity:1,y:0,duration:.3,ease:"power3.out",immediateRender:false},${(l.start + 0.05).toFixed(3)});`;
});

// ---------- B-rolls plein écran (au-dessus de la cam, sous les sous-titres) : légère poussée, entrée nette ----------
(plan.brolls || []).forEach((b, i) => {
  const d = (b.end - b.start).toFixed(3), img = /\.(jpe?g|png|webp)$/i.test(b.src);
  layers += img
    ? `<div class="broll" id="b${i}"><div class="bw" id="b${i}m"><img class="bm" src="${esc(b.src)}"/></div></div>`
    : `<div class="broll" id="b${i}"><div class="bw" id="b${i}m"><video id="b${i}v" class="clip bm" src="${esc(b.src)}" muted playsinline preload="auto" data-start="${b.start.toFixed(3)}" data-duration="${d}" data-track-index="${10 + i}" data-has-audio="false"></video></div></div>`;
  V(`#b${i}`, b.start, b.end, "{}", "{}", 0.001);
  ops += `tl.fromTo("#b${i}m",{scale:1.12},{scale:1.02,duration:${d},ease:"power2.out",force3D:true,immediateRender:false},${b.start.toFixed(3)});`;
});

// ---------- incrustations : image sur-mesure (PNG détouré de préférence) posée sur la cam, entrée pop + flottement ----------
(plan.inserts || []).forEach((n, i) => {
  // top = au-dessus de la tête, jamais sur le visage (max 380 px de haut) ; center = carte qui couvre le visage, à garder court (≤ 2 s)
  const d = (n.end - n.start).toFixed(3), c = n.pos === "center";
  if (n.track) {   // TRACKING (track.py) : l'objet suit un point du corps (bout du doigt, à côté de la tête...), accroché au geste
    const T = JSON.parse(readFileSync(n.track, "utf8")).samples.filter(p => p.t >= n.start - 0.1 && p.t <= n.end + 0.1), [dx, dy] = n.offset || [0, 0];
    layers += `<div class="ins trk" id="i${i}"><div class="itk" id="it${i}"><div class="ictr"><div class="iw" id="i${i}m"><img id="i${i}g" src="${esc(n.src)}" style="width:${n.w || 300}px;max-height:none"/></div></div></div></div>`;
    V(`#i${i}`, n.start, n.end, "{}", "{}", 0.2, 0.25);
    F(`#i${i}g`, `{scale:.6,opacity:0,filter:"blur(8px)"}`, `scale:1,opacity:1,filter:"blur(0px)",duration:.4,ease:"power3.out"`, n.start);
    T.forEach((p, k) => { const q = T[k + 1] || p, t = Math.max(p.t, 0);
      ops += `tl.fromTo("#it${i}",{x:${(p.x + dx).toFixed(1)},y:${(p.y + dy).toFixed(1)}},{x:${(q.x + dx).toFixed(1)},y:${(q.y + dy).toFixed(1)},duration:${Math.max(q.t - p.t, 0.001).toFixed(3)},ease:"none",force3D:true,immediateRender:false},${t.toFixed(3)});`; });
    return;
  }
  layers += `<div class="ins" id="i${i}" style="top:${c ? 520 : 280}px"><div class="iw" id="i${i}m"><img src="${esc(n.src)}" style="max-width:${n.w || (c ? 860 : 640)}px;max-height:${c ? 900 : 380}px"/></div></div>`;
  V(`#i${i}`, n.start, n.end, `{scale:.94,y:24,filter:"blur(10px)"}`, `{scale:1,y:0,filter:"blur(0px)",ease:"power3.out"}`, 0.45, 0.25);   // fondu + montée douce, sans rebond (sobre, luxe discret)
  ops += `tl.fromTo("#i${i}m",{y:10},{y:-16,duration:${d},ease:"sine.inOut",force3D:true,immediateRender:false},${n.start.toFixed(3)});`;
});

// ---------- pleins écrans preuve (guide OPUS « montrer au lieu de dire ») : la voix continue, l'écran montre la preuve.
//            3 à 5 max par vidéo, 1 à 5 s chacun, 1 texture différente par type (papier / quadrillé / verre sombre) ----------
const f1 = v => (+v).toFixed(1);
const RGB = h => { const x = parseInt(h.slice(1), 16); return `${x >> 16},${(x >> 8) & 255},${x & 255}`; };
const GRAIN = id => `<svg class="grain"><filter id="${id}"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 .09 0"/></filter><rect width="100%" height="100%" filter="url(#${id})"/></svg>`;
const TITLE = (id, t, top = 290) => t && (t[0] || t[1]) ? `<div class="pt" id="${id}t" style="top:${top}px"><div class="p1">${esc(t[0] || "")}</div><div class="p2">${esc(t[1] || "")}</div></div>` : "";
// courbe lissée (Catmull-Rom -> Bézier)
const smooth = P => P.map((p, k) => {
  if (!k) return `M${f1(p[0])},${f1(p[1])}`;
  const p0 = P[k - 2] || P[k - 1], p1 = P[k - 1], p3 = P[k + 1] || p;
  return `C${f1(p1[0] + (p[0] - p0[0]) / 6)},${f1(p1[1] + (p[1] - p0[1]) / 6)} ${f1(p[0] - (p3[0] - p1[0]) / 6)},${f1(p[1] - (p3[1] - p1[1]) / 6)} ${f1(p[0])},${f1(p[1])}`;
}).join(" ");
const DRAW = (sel, t, d, ease = "power2.inOut") => F(sel, "{strokeDashoffset:1.05}", `strokeDashoffset:0,duration:${(+d).toFixed(3)},ease:"${ease}"`, t);
const SHOW = (sel, t, d = 0.35, y = 0) => F(sel, `{opacity:0${y ? `,y:${y}` : ""}}`, `opacity:1${y ? ",y:0" : ""},duration:${d},ease:"expo.out"`, t);

proofs.forEach((p, i) => {
  const id = `p${i}`, T = p.start, d = p.end - p.start;
  let inner = "", tex = "dark";
  if (p.type === "curve") {
    // courbe d'apprentissage : la ligne grise plafonne au niveau bas, la ligne accent monte d'un coup jusqu'en haut
    tex = "paper";
    const steps = p.steps || ["S1", "S2", "S3", "S4", "S5", "S6"], lv = p.levels || ["Débutant", "Expert"];
    const aDur = Math.max(0.5, Math.min(1.6, 0.42 * d));
    const bAt = p.climax ?? (T + 0.35 + aDur), bDur = Math.max(0.35, Math.min(0.7, p.end - bAt - 0.45));
    inner = GRAIN(`${id}g`) + TITLE(id, p.title) + `<svg class="chart" viewBox="0 0 960 860" style="top:600px">
      <line class="lvl" id="${id}v0" x1="120" y1="604" x2="910" y2="604"/><line class="lvl" id="${id}v1" x1="120" y1="150" x2="910" y2="150"/>
      <text class="lvt" id="${id}w0" x="138" y="588">${esc(lv[0])}</text><text class="lvt" id="${id}w1" x="138" y="134">${esc(lv[1])}</text>
      <line class="ax" pathLength="1" x1="120" y1="770" x2="910" y2="770"/><line class="ax" pathLength="1" x1="120" y1="770" x2="120" y2="80"/>
      ${steps.map((s, k) => `<text class="stp" id="${id}s${k}" x="${f1(120 + (k + 0.5) * 790 / steps.length)}" y="826" text-anchor="middle">${esc(s)}</text>`).join("")}
      <path class="pa" id="${id}a" pathLength="1" d="M120,770 C250,650 360,612 520,606 S800,604 905,604"/>
      <path class="pb" id="${id}b" pathLength="1" d="M120,770 C300,768 420,740 500,560 S600,170 905,150"/>
      <circle class="dotb" id="${id}o" cx="905" cy="150" r="17"/>
      <text class="la" id="${id}la" x="905" y="660" text-anchor="end">${esc(p.from || "")}</text>
      <text class="lb" id="${id}lb" x="905" y="112" text-anchor="end">${esc(p.to || "")}</text></svg>`;
    if (p.title) SHOW(`#${id}t`, T + 0.05, 0.45, -24);
    ops += `tl.fromTo("#${id} .ax",{strokeDashoffset:1.05},{strokeDashoffset:0,duration:.45,ease:"power2.inOut",immediateRender:false,autoRound:false},${(T + 0.1).toFixed(3)});`;
    [0, 1].forEach(k => { SHOW(`#${id}v${k}`, T + 0.3 + k * 0.08); SHOW(`#${id}w${k}`, T + 0.3 + k * 0.08); });
    steps.forEach((_, k) => SHOW(`#${id}s${k}`, T + 0.3 + k * 0.04, 0.3));
    DRAW(`#${id}a`, T + 0.35, aDur, "power1.inOut");
    SHOW(`#${id}la`, T + 0.3 + aDur, 0.4, 12);
    DRAW(`#${id}b`, bAt, bDur, "power3.inOut");
    F(`#${id}o`, `{opacity:0,scale:0,svgOrigin:"905 150"}`, `opacity:1,scale:1,svgOrigin:"905 150",duration:.4,ease:"expo.out"`, bAt + bDur - 0.05);
    SHOW(`#${id}lb`, bAt + bDur - 0.1, 0.45, 16);
    cues.push({ kind: "reverse", at: bAt + bDur });
  } else if (p.type === "clock") {
    // horloge qui se dessine puis s'emballe, traînée sur l'aiguille, anneau AN 1 -> AN N, tic-tac qui accélère
    tex = "grid";
    const N = p.years || 5, lab = p.label || "AN", spinAt = T + 0.75, spinDur = Math.max(1, d - 0.95), turns = p.turns || 3 * N;
    const P = (a, r) => `${f1(Math.cos(a * Math.PI / 180) * r)},${f1(Math.sin(a * Math.PI / 180) * r)}`;
    let ring = "", ticks = "";
    for (let k = 0; k < N; k++) {
      const a0 = -90 + k * 360 / N + 4, a1 = -90 + (k + 1) * 360 / N - 4, am = (a0 + a1) / 2, arc = `M${P(a0, 445)} A445,445 0 0 1 ${P(a1, 445)}`;
      ring += `<path class="ybg" d="${arc}"/><path class="yon" id="${id}y${k}" d="${arc}"/><text class="ylab" id="${id}l${k}" x="${P(am, 388).split(",")[0]}" y="${P(am, 388).split(",")[1]}" text-anchor="middle" dominant-baseline="middle">${esc(lab)} ${k + 1}</text>`;
      const tk = spinAt + Math.cbrt((k + 1) / N) * spinDur;   // l'aiguille accélère (power3.in) : l'année k s'allume quand elle y arrive
      F(`#${id}y${k}`, "{opacity:0}", `opacity:1,duration:.18,ease:"power2.out"`, tk - 0.1);
      F(`#${id}l${k}`, "{opacity:.3}", `opacity:1,duration:.18`, tk - 0.1);
    }
    for (let m = 1; m <= 2 * N; m++) cues.push({ kind: "tick", at: +(spinAt + Math.cbrt(m / (2 * N)) * spinDur - 0.1).toFixed(3) });
    for (let h = 0; h < 12; h++) ticks += `<line class="tick${h % 3 ? "" : " big"}" id="${id}k${h}" x1="${P(h * 30 - 90, h % 3 ? 300 : 280).split(",")[0]}" y1="${P(h * 30 - 90, h % 3 ? 300 : 280).split(",")[1]}" x2="${P(h * 30 - 90, 326).split(",")[0]}" y2="${P(h * 30 - 90, 326).split(",")[1]}"/>`;
    const ghosts = [3, 2, 1].map(j => `<g class="ghost" id="${id}g${j}"><line x1="0" y1="30" x2="0" y2="-285"/></g>`).join("");
    const ttl = p.title === undefined ? ["", "des années"] : p.title;
    inner = GRAIN(`${id}gr`) + TITLE(id, ttl, 200) + `<svg class="clock" viewBox="-500 -500 1000 1000">
      ${ring}<circle class="fill" id="${id}f" r="342"/><circle class="face" id="${id}c" r="342" pathLength="1" transform="rotate(-90)"/>${ticks}${ghosts}
      <g class="hand hh" id="${id}h"><line x1="0" y1="26" x2="0" y2="-185"/></g><g class="hand mh" id="${id}m"><line x1="0" y1="30" x2="0" y2="-285"/></g>
      <circle class="hub" id="${id}u" r="20"/></svg>`;
    if (ttl) SHOW(`#${id}t`, T + 0.05, 0.45, -24);
    SHOW(`#${id}f`, T + 0.1, 0.5);
    DRAW(`#${id}c`, T + 0.12, 0.6);
    for (let h = 0; h < 12; h++) SHOW(`#${id}k${h}`, T + 0.25 + h * 0.025, 0.25);
    [`#${id}h`, `#${id}m`, `#${id}u`].forEach(s => SHOW(s, T + 0.5, 0.3));
    F(`#${id}m`, `{rotation:0,svgOrigin:"0 0"}`, `rotation:${turns * 360},svgOrigin:"0 0",duration:${spinDur.toFixed(3)},ease:"power3.in"`, spinAt);
    F(`#${id}h`, `{rotation:0,svgOrigin:"0 0"}`, `rotation:${turns * 30},svgOrigin:"0 0",duration:${spinDur.toFixed(3)},ease:"power3.in"`, spinAt);
    [1, 2, 3].forEach(j => {
      F(`#${id}g${j}`, `{rotation:${-9 * j},svgOrigin:"0 0"}`, `rotation:${turns * 360 - 9 * j},svgOrigin:"0 0",duration:${spinDur.toFixed(3)},ease:"power3.in"`, spinAt);
      F(`#${id}g${j}`, "{opacity:0}", `opacity:${(0.36 / j).toFixed(2)},duration:${spinDur.toFixed(3)},ease:"power3.in"`, spinAt);
    });
  } else {
    // dashboard réaliste incliné en 3D (façon app Statistiques / TradingView) : chiffre qui défile, graphique qui se dessine
    tex = "dark";
    const ser = p.series || [4, 5, 5, 7, 8, 11, 13, 18, 24, 33, 46, 64];
    const mx = Math.max(...ser), mn = Math.min(0, ...ser);
    const pts = ser.map((v, k) => [20 + k / (ser.length - 1) * 780, 290 - (v - mn) / ((mx - mn) || 1) * 250]);
    const line = smooth(pts), vtxt = `${p.prefix || ""}${p.value ?? 0}${p.suffix || ""}`;
    const vfs = Math.round(Math.min(170, 1350 / Math.max(4, vtxt.length)));
    const tiles = (p.tiles || []).slice(0, 3), cd = Math.min(1.3, d * 0.5), ld = Math.min(1.4, d * 0.55);
    inner = TITLE(id, p.title, 290) + `<div class="persp" style="top:${p.title ? 560 : 400}px"><div class="card" id="${id}c"><div class="glare" id="${id}gl"></div>
      <div class="chd"><div class="cico"></div><div class="capp">${esc(p.app || "Statistiques")}</div><div class="cpill">${esc(p.period || "30 derniers jours")}</div></div>
      <div class="clab">${esc(p.label || "")}</div>
      <div class="cval" style="font-size:${vfs}px">${esc(p.prefix || "")}<span id="${id}v">0</span>${esc(p.suffix || "")}</div>
      ${p.delta ? `<div class="cdel" id="${id}d">${esc(p.delta)}</div>` : ""}
      <svg class="cchart" viewBox="0 0 820 320"><defs><linearGradient id="${id}ag" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${ACC}" stop-opacity=".45"/><stop offset="1" stop-color="${ACC}" stop-opacity="0"/></linearGradient></defs>
        <line class="cgl" x1="20" y1="40" x2="800" y2="40"/><line class="cgl" x1="20" y1="165" x2="800" y2="165"/><line class="cgl" x1="20" y1="290" x2="800" y2="290"/>
        <path class="car" id="${id}ar" fill="url(#${id}ag)" d="${line} L${f1(pts.at(-1)[0])},300 L${f1(pts[0][0])},300 Z"/>
        <path class="cln" id="${id}ln" pathLength="1" d="${line}"/>
        <circle class="cdot" id="${id}o" cx="${f1(pts.at(-1)[0])}" cy="${f1(pts.at(-1)[1])}" r="13"/></svg>
      ${tiles.length ? `<div class="tiles">${tiles.map((t, k) => `<div class="tile" id="${id}t${k}"><div class="tlb">${esc(t.label)}</div><div class="tv">${esc(t.prefix || "")}<span id="${id}tv${k}">${typeof t.value === "number" ? 0 : esc(t.value)}</span>${esc(t.suffix || "")}</div></div>`).join("")}</div>` : ""}
    </div></div>`;
    if (p.title) SHOW(`#${id}t`, T + 0.05, 0.45, -24);
    F(`#${id}c`, "{rotationX:17,rotationY:-15,y:60}", `rotationX:7,rotationY:-6,y:0,duration:${d.toFixed(3)},ease:"power2.out"`, T);
    F(`#${id}gl`, "{x:0}", `x:1500,duration:1.3,ease:"power2.inOut"`, T + 0.25);
    COUNT(`${id}v`, p.value ?? 0, T + 0.3, cd, p.decimals || 0);
    if (p.delta) SHOW(`#${id}d`, T + 0.3 + cd * 0.7, 0.35, 10);
    DRAW(`#${id}ln`, T + 0.35, ld);
    F(`#${id}ar`, "{opacity:0}", `opacity:1,duration:.6,ease:"power2.out"`, T + 0.35 + ld * 0.6);
    F(`#${id}o`, `{opacity:0,scale:0,svgOrigin:"${pts.at(-1).map(f1).join(" ")}"}`, `opacity:1,scale:1,svgOrigin:"${pts.at(-1).map(f1).join(" ")}",duration:.35,ease:"expo.out"`, T + 0.35 + ld);
    tiles.forEach((t, k) => { SHOW(`#${id}t${k}`, T + 0.55 + k * 0.12, 0.4, 20); if (typeof t.value === "number") COUNT(`${id}tv${k}`, t.value, T + 0.6 + k * 0.12, cd, t.decimals || 0); });
  }
  layers += `<div class="proof ${tex}" id="${id}">${inner}</div>`;
  V(`#${id}`, p.start, p.end, `{scale:1.05,filter:"blur(16px)"}`, `{scale:1,filter:"blur(0px)",ease:"expo.out"}`, 0.32, SOFT(p.end, 0.3));
  cues.push({ kind: "subdrop", at: p.start });
});

// ---------- CTA « commente MOT » : une vraie feuille de commentaires monte du bas, le mot se tape lettre par lettre
//            (clavier qui s'allume), puis se publie en haut de la liste. Champ de saisie au-dessus des 20 % du bas cachés par l'appli ----------
if (cta) {
  // zones mortes Insta : touches, champ et commentaires entre 270 et 1480 px, à 65 px des bords ; le fond de la feuille et
  // la plaque grise du clavier descendent jusqu'en bas (décor). Le contenu monte dans un cache qui s'arrête à 1480 px.
  const WD = String(cta.word || "GUIDE").toUpperCase(), T = cta.start, rowH = 130;
  const com = cta.comments || [["julie.coach", WD, "2 min"], ["marc_formation", WD, "4 min"], ["sandra.business", `${WD} stp`, "9 min"], ["thomas.entrepreneur", WD, "14 min"]];
  const AV = ["#6b7a99", "#99806b", "#6b9988", "#8a6b99", "#996b7a"];
  const heart = `<svg class="chh" viewBox="0 0 24 24"><path d="M12 20.5s-7.3-4.5-9.2-9C1.5 8.4 3.6 5 7 5c2 0 3.2 1.1 5 3 1.8-1.9 3-3 5-3 3.4 0 5.5 3.4 4.2 6.5-1.9 4.5-9.2 9-9.2 9z" fill="none" stroke="#8e8e93" stroke-width="1.8"/></svg>`;
  const row = (u, txt, tm, k, me) => `<div class="cr" id="${me ? "crme" : "cr" + k}"><div class="av" style="background:${me ? ACC : AV[k % AV.length]}">${esc(u[0].toUpperCase())}</div><div class="cb"><div class="cu">${esc(u)}<span>${esc(tm)}</span></div><div class="ct">${esc(txt)}</div><div class="cre">Répondre</div></div>${heart}</div>`;
  const KB = ["AZERTYUIOP", "QSDFGHJKLM", "WXCVBN"];
  const t0 = T + 0.85, step = 0.14, tP = t0 + WD.length * step + 0.35;
  layers += `<div class="cta" id="cta"><div class="sheet" id="sheet"><div class="kbbg"></div></div><div class="ctam"><div class="sheet sheetc" id="sheetc"><div class="grab"></div><div class="shh">Commentaires<span>${esc(cta.count || "1 284")}</span></div>
    <div class="cv"><div class="cl" id="cl">${row(cta.user || "toi", WD, "à l'instant", 0, true)}${com.slice(0, 4).map((c, k) => row(c[0], c[1], c[2] || "", k)).join("")}</div></div>
    <div class="inp"><div class="av" style="background:${ACC}">${esc((cta.user || "toi")[0].toUpperCase())}</div><div class="field"><span class="ph" id="ph">Ajouter un commentaire…</span><span id="typed">${[...WD].map((c, k) => `<span class="tch" id="tc${k}">${esc(c)}</span>`).join("")}</span><i class="caret" id="caret"></i></div><div class="send" id="send">Publier</div></div>
    <div class="kb">${KB.map(r => `<div class="kr">${[...r].map(c => `<div class="key" id="kb${c}">${c}</div>`).join("")}</div>`).join("")}<div class="kr"><div class="key sp">espace</div></div></div>
  </div></div></div>`;
  V("#cta", cta.start, cta.end, "{}", "{}", 0.25, SOFT(cta.end, 0.3));
  F("#sheet,#sheetc", "{y:1300}", `y:0,duration:.6,ease:"expo.out"`, T);
  F("#caret", "{opacity:1}", `opacity:0,duration:.3,repeat:${Math.max(1, Math.floor((cta.end - T) / 0.3) - 1)},yoyo:true,ease:"steps(1)"`, T + 0.6);
  F("#ph", "{opacity:1}", `opacity:0,duration:.01`, t0);
  F("#send", "{opacity:.35}", `opacity:1,duration:.2`, t0);
  [...WD].forEach((c, k) => {
    F(`#tc${k}`, `{display:"none"}`, `display:"inline",duration:.01`, t0 + k * step);
    if (/[A-Z]/.test(c)) F(`#kb${c}`, `{backgroundColor:"#9a9aa0"}`, `backgroundColor:"#4a4a4e",duration:.12,ease:"power2.out"`, t0 + k * step);
  });
  F("#send", "{scale:.86}", `scale:1,duration:.3,ease:"expo.out"`, tP);
  F("#typed", "{opacity:1}", `opacity:0,duration:.15`, tP + 0.05);
  F("#ph", "{opacity:0}", `opacity:1,duration:.2`, tP + 0.2);
  F("#cl", `{y:-${rowH}}`, `y:0,duration:.55,ease:"expo.out"`, tP + 0.1);
  F("#crme", `{backgroundColor:"rgba(${RGB(ACC)},.28)"}`, `backgroundColor:"rgba(${RGB(ACC)},0)",duration:1.6,ease:"power2.out"`, tP + 0.1);
  cues.push({ kind: "sheet", at: T + 0.25 }, { kind: "type", at: t0, dur: +(WD.length * step + 0.1).toFixed(3) }, { kind: "publish", at: tP });
}

// ---------- pastilles 1-2-3 ----------
if (plan.bullets) {
  const b = plan.bullets;
  layers += `<div class="bul" id="bul">${b.at.map((_, k) => `<div class="dot" id="d${k}">${k + 1}</div>`).join("")}</div>`;
  V("#bul", b.at[0] - 0.05, b.end, "{}", "{}", 0.15);
  b.at.forEach((t, k) => ops += `tl.fromTo("#d${k}",{opacity:.25,scale:.85,backgroundColor:"rgba(255,255,255,0)"},{opacity:1,scale:1,backgroundColor:"rgba(255,255,255,.14)",duration:.25,ease:"power3.out",immediateRender:false},${t.toFixed(3)});`);
}

// ---------- sous-titres (règles Style Lab) : Montserrat 700 blanc 52 px, 1-3 mots, majuscules ;
//            mot fort = serif italique blanc 132 px, SEUL à l'écran, groupe de 1-3 mots ; entrée fondu + petite montée ; hauteur = subzone.py (sous le col) ----------
// un bloc ne finit jamais sur un petit mot (« du », « pour »...) : il passe au bloc suivant
const SMALL = new Set(["du","de","des","la","le","les","un","une","et","pour","sur","à","ta","tes","ce","cette","ces","il","on","tu","je","que","qu'à","c'est","t'as","t'es","avec","parce","plus","dès"]);
//  aussi jamais en fin de bloc : pronoms devant le verbe (« plus ÇA / traîne », « VOUS / tire »), possessifs,
// prépositions, « très / trop » et adjectifs placés devant le nom (« un BON / coup ») -> CARRY
const CARRY = new Set([...SMALL, "vous","nous","elle","elles","ils","ça","me","te","se","lui","en","y","ne","n'","mon","ma","mes","ton","son","sa","ses",
  "notre","nos","votre","vos","leur","leurs","au","aux","dans","par","chez","sans","sous","vers","entre","très","trop","si","aussi","tout","toute","tous","toutes",
  "bon","bonne","grand","grande","petit","petite","gros","grosse","vrai","vraie","seul","seule","même","autre","beau","belle","nouveau","nouvelle",
  "premier","première","dernier","dernière","meilleur","meilleure","mauvais","mauvaise","qui","dont"]);
const isCarry = e => CARRY.has(e) || /^n['’]/.test(e);   // « CE N'EST / PAS » : la négation ne se coupe pas
const openEnd = j => isCarry(norm(W[j].text)) && !/[.,!?]$/.test(W[j].text);   // le bloc ne peut pas finir sur ce mot
// mots forts = mots OU groupes de 1 à 3 mots (« badge bleu »), Style Lab R2 : chaque mot porte l'id de sa phrase (-1 = normal)
// élision ignorée pour reconnaître le mot (« l'arnaque » = arnaque), le sous-titre garde « l'arnaque »
const normK = s => norm(s).replace(/^(?:l|d|j|t|s|c|n|m|qu)['’]/, "");
// règle Style Lab R5 : vidéo AVEC titre-question = AUCUN mot fort dans les sous-titres, sinon ça fait trop. Titre OU mots forts, jamais les deux.
if (plan.title && (plan.keywords || []).length) console.log(`titre présent : ${plan.keywords.length} mots forts ignorés (règle titre OU mot fort)`);
const KWP = (plan.title ? [] : plan.keywords || []).map(k => String(k).split(/\s+/).map(normK).filter(Boolean)).filter(p => p.length);
const kwOf = W.map(() => -1);
W.forEach((_, i) => KWP.forEach((ph, p) => { if (kwOf[i] < 0 && ph.every((s, k) => W[i + k] && kwOf[i + k] < 0 && normK(W[i + k].text) === s)) ph.forEach((_, k) => kwOf[i + k] = p * 1000 + i); }));
const kStart = i => kwOf[i] >= 0 && (i === 0 || kwOf[i - 1] !== kwOf[i]);
const kIn = i => kwOf[i] >= 0 && i > 0 && kwOf[i - 1] === kwOf[i];
const kEnd = i => kwOf[i] >= 0 && kwOf[i + 1] !== kwOf[i];
// découpage : au lieu de couper au fil de l'eau, on teste TOUTES les coupes d'une phrase et on garde la moins chère.
// Coût d'un bloc : 1 (moins de blocs) ; > 16 car. +3 (max 18, 4 mots) ; mot seul +2,5 (+0,5 si long) ; finit sur un petit mot +6,
// sur un pronom / adjectif / « très » +3 (sauf « ET QUE », « PARCE QUE ») ; pause > 0,25 s dans le bloc +4 (+1 après un mot CARRY).
const LINK = new Set(["et","parce","alors","pendant","tandis","ainsi","bien","dès","avant","après","sans","sauf"]);
const blockCost = (a, b, last) => {
  const n = b - a + 1, L = W.slice(a, b + 1).map(w => w.text).join(" ").length;
  if (n > 4 || (L > 18 && n > 1)) return Infinity;
  let c = 1 + (L > 16 ? 3 : 0);
  if (n === 1) c += W[a].text.length >= 9 ? 0.5 : 2.5;
  const e = norm(W[b].text);
  if (!last && !/[.,!?]$/.test(W[b].text) && !(/^qu/.test(e) && n === 2 && LINK.has(norm(W[a].text)))) c += SMALL.has(e) ? 6 : isCarry(e) ? 3 : 0;
  for (let j = a; j < b; j++) if (W[j + 1].t - W[j].e > .25) c += openEnd(j) ? 1 : 4;
  return c;
};
const splitBest = ids => {
  const N = ids.length, best = Array(N + 1).fill(Infinity), from = Array(N + 1).fill(0); best[0] = 0;
  for (let k = 1; k <= N; k++) for (let s = Math.max(0, k - 4); s < k; s++) {
    const c = best[s] + blockCost(ids[s], ids[k - 1], k === N);
    if (c < best[k]) { best[k] = c; from[k] = s; }
  }
  const out = []; for (let k = N; k > 0; k = from[k]) out.unshift(ids.slice(from[k], k));
  return out;
};
// morceaux = phrases (ponctuation ou pause >= 0,7 s) ; un mot fort (1-3 mots) reste un bloc à lui
let groups = [], chunk = [];
const flush = () => { if (chunk.length) groups.push(...splitBest(chunk)); chunk = []; };
W.forEach((w, i) => {
  if (kwOf[i] >= 0) { flush(); if (kStart(i)) groups.push([]); groups.at(-1).push(i); return; }
  chunk.push(i);
  const next = W[i + 1];
  if (!next || /[.,!?]$/.test(w.text) || next.t - w.e >= .7) flush();
});
flush();
// mot fort TOUJOURS SEUL à l'écran (Style Lab R2-R3) : la phrase s'efface, le mot fort arrive seul quand il est dit
groups = groups.flatMap(gr => { const out = []; let run = []; gr.forEach(j => { if (run.length && (kwOf[j] >= 0) !== (kwOf[run[0]] >= 0)) { out.push(run); run = []; } run.push(j); }); if (run.length) out.push(run); return out; });
// un bloc de petits mots seuls (« UN » avant « badge bleu ») se recolle au bloc normal d'avant s'il tient (même phrase, ≤ 18 caractères)
groups = groups.reduce((acc, gr, gi, all) => {
  const prev = acc.at(-1), txt = ws => ws.map(j => W[j].text).join(" "), nxt = all[gi + 1];
  const small = nxt && kwOf[nxt[0]] >= 0 && gr.every(j => kwOf[j] < 0 && SMALL.has(norm(W[j].text)));
  if (small && prev && kwOf[prev[0]] < 0 && !/[.,!?]$/.test(W[prev.at(-1)].text) && txt([...prev, ...gr]).length <= 18) prev.push(...gr); else acc.push(gr);
  return acc;
}, []);
// règle apprise : un chiffre ou un mot géant à l'écran sort du sous-titre (« DONNE-MOI » seul, pas « DONNE-MOI 30 »)
const squash = t => normK(t).replace(/\s/g, "");   // « l'arnaque » sort aussi du sous-titre quand ARNAQUE est à l'écran
const BIG = [...(plan.numbers || []).map(n => [n.start, n.end, squash(n.text + (n.suffix || ""))]), ...bigwords.map(w => [w.start, w.end, squash(w.text)])];
const onScreen = j => BIG.some(([s, e, k]) => W[j].t >= s - 0.4 && W[j].t < e && squash(W[j].text.replace(/[.,!?]$/, "")) === k);
const CAPT = [];   // [début, fin] de chaque sous-titre affiché (garde-fou chevauchement plus bas)
groups.forEach((grp, gi) => {
  const a = W[grp[0]].t, nextG = groups[gi + 1];
  let b = nextG ? W[nextG[0]].t : W[grp.at(-1)].e + 0.3;
  if (b - W[grp.at(-1)].e > 0.5) b = W[grp.at(-1)].e + 0.3;
  if (covered(a)) return;
  grp = grp.filter(j => !onScreen(j));
  if (!grp.length) return;
  const html = grp.map(j => { const t = W[j].text.replace(/[.,!?]$/, ""); return kwOf[j] >= 0 ? `<em>${esc(t.toLowerCase())}</em>` : esc(t.toUpperCase()); }).join(" ");
  const emTxt = grp.filter(j => kwOf[j] >= 0).map(j => W[j].text.replace(/[.,!?]$/, "").toLowerCase()).join(" ");
  const bEnd = Math.min(b, ...FULL.filter(l => l.start > a).map(l => l.start));
  // plan.subYAt (podcast.py) : hauteur par plage (jonction du split / col en plein écran). Un bloc à cheval sur un changement
  // de mise en page continue à la nouvelle hauteur (sans nouvelle entrée), jamais de trou ; morceau < 0,25 s = sauté (anti-flash)
  const ZS = plan.subYAt || [];
  const pts = [a, ...ZS.map(z => z.start).filter(t => t > a + 0.05 && t < bEnd - 0.05), bEnd];
  let first = true;
  pts.slice(0, -1).forEach((p0, k) => {
    const p1 = pts[k + 1];
    if (p1 - p0 < 0.25 && pts.length > 2) return;
    const zone = ZS.find(z => p0 >= z.start - 0.02 && p0 < z.end), id = `c${gi}${k ? "_" + k : ""}`;
    const y0 = zone ? zone.y : SUBY, y = subY(y0, emTxt);
    if (y !== y0) console.log(`sous-titre ${gi} « ${emTxt || W[grp[0]].text} » : y ${y0} -> ${y} (zones mortes)`);
    layers += `<div class="cap${zone && zone.light ? " onlight" : ""}" id="${id}"${zone || y !== y0 ? ` style="top:${y}px"` : ""}>${html}</div>`;
    CAPT.push([p0, p1]);
    if (first) V(`#${id}`, p0, p1, `{y:10}`, `{y:0,ease:"power2.out"}`, 0.1); else V(`#${id}`, p0, p1, "{}", "{}", 0.01);
    first = false;
  });
});

// ---------- titre-question en haut pendant le hook (Style Lab R4) : 2 lignes (petites MAJUSCULES + serif italique) sur un voile sombre,
//            fondu + petite montée. plan.title = {l1: "Le badge bleu Meta", l2: "une arnaque ?", start: 0, end: 4, top: 280} ----------
if (plan.title) {
  const T = plan.title;
  const tz = (plan.subYAt || []).find(z => (T.start ?? 0) >= z.start - 0.02 && (T.start ?? 0) < z.end);   // fond clair = pas de voile
  layers += `<div class="htitle${tz && tz.light ? " onlight" : ""}" id="htitle" style="top:${T.top ?? 280}px"><div class="ht1">${esc(T.l1 || "")}</div><div class="ht2">${esc(T.l2 || "")}</div></div>`;
  V("#htitle", T.start ?? 0, Math.min(T.end ?? 4, dur), `{y:10}`, `{y:0,ease:"power2.out"}`, 0.25);
}

// garde-fou : un objet suivi (badge sur la paume...) qui passe dans la bande des sous-titres pendant
// qu'un sous-titre est affiché = les deux se cachent. On ne bouge rien tout seul : on prévient pour corriger l'offset ou le moment.
(plan.inserts || []).forEach((n, i) => {
  if (!n.track) return;
  const [, dy] = n.offset || [0, 0], half = (n.w || 300) / 2, band = [SUBY - 20, SUBY + 150];
  const hits = JSON.parse(readFileSync(n.track, "utf8")).samples
    .filter(p => p.t >= n.start && p.t <= n.end && CAPT.some(([s, e]) => p.t >= s && p.t < e) && p.y + dy + half > band[0] && p.y + dy - half < band[1]);
  if (hits.length) console.log(`ATTENTION chevauchement : incrustation ${i} (${n.src}) passe sur les sous-titres de ${hits[0].t.toFixed(2)} à ${hits.at(-1).t.toFixed(2)} s -> monter l'offset, la réduire ou décaler le moment`);
});

// ---------- STYLE MINIMALISTE (degré « face caméra minimaliste ») : beaucoup d'air, zéro transition.
//            card = carton typo plein écran, le texte se construit mot par mot, calé sur la voix (MAJUSCULES + serif italique) ;
//            icon = icône au trait fin au-dessus de la tête (barrée d'une croix sur « non ») ;
//            shot = capture en carte arrondie qui flotte, un cercle se dessine à la main autour de LA chose dite.
//            Ça apparaît net (≤ 0,3 s, expo, sans rebond), ça disparaît net. Couleurs = celles du rush (C, plan.colors). ----------
const MINI_ICONS = {
  eye: `<path d="M3 24s7.5-13 21-13 21 13 21 13-7.5 13-21 13S3 24 3 24z"/><circle cx="24" cy="24" r="6.5"/>`,
  calendar: `<rect x="6" y="9" width="36" height="33" rx="4"/><path d="M6 18h36M15 5v8M33 5v8"/><path d="M14 26h4M22 26h4M30 26h4M14 33h4M22 33h4"/>`,
  user: `<circle cx="24" cy="16" r="8"/><path d="M8 42c2-9 8.5-13 16-13s14 4 16 13"/>`,
  users: `<circle cx="18" cy="17" r="7"/><path d="M4 40c1.6-7.5 7-11 14-11s12.4 3.5 14 11"/><circle cx="34" cy="15" r="5.5"/><path d="M33 26c6 0 10 3 11.5 9"/>`,
  chart: `<path d="M6 40h36"/><path d="M10 32l9-9 7 6 13-14"/><path d="M32 15h7v7"/>`,
  phone: `<rect x="14" y="4" width="20" height="40" rx="4"/><path d="M21 38h6"/>`,
  message: `<path d="M8 10h32a3 3 0 0 1 3 3v19a3 3 0 0 1-3 3H20l-9 7v-7H8a3 3 0 0 1-3-3V13a3 3 0 0 1 3-3z"/>`,
  clock: `<circle cx="24" cy="24" r="18"/><path d="M24 13v11l7 5"/>`,
  money: `<rect x="4" y="13" width="40" height="23" rx="3"/><circle cx="24" cy="24.5" r="5.5"/><path d="M10 19v11M38 19v11"/>`,
  badge: `<path d="M24 4l4.6 3.4 5.7-.3 1.7 5.4 4.7 3.3-1.7 5.5 1.7 5.5-4.7 3.3-1.7 5.4-5.7-.3L24 44l-4.6-3.4-5.7.3-1.7-5.4-4.7-3.3 1.7-5.5-1.7-5.5 4.7-3.3 1.7-5.4 5.7.3z"/><path d="M17 24.5l5 5 9-10"/>`,
  shield: `<path d="M24 4l16 6v12c0 10-7 17-16 21C15 39 8 32 8 22V10z"/><path d="M17 24l5 5 9-10"/>`,
  heart: `<path d="M24 41S6 30.5 6 18a9.5 9.5 0 0 1 18-4.3A9.5 9.5 0 0 1 42 18c0 12.5-18 23-18 23z"/>`,
  star: `<path d="M24 5l5.6 12.2 13.4 1.4-10 9 2.9 13.2L24 34l-11.9 6.8L15 27.6l-10-9 13.4-1.4z"/>`,
  idea: `<path d="M17 31c-3.5-2.6-6-6.5-6-11a13 13 0 0 1 26 0c0 4.5-2.5 8.4-6 11v5H17z"/><path d="M18 41h12"/>`,
  handshake: `<path d="M3 20l7-7 6 3 6-3 4 2"/><path d="M45 20l-7-7-6 2"/><path d="M10 13v15l10 10c1.5 1.5 3.5 1.5 5 0l11-11c1.5-1.5 1.5-3.5 0-5l-6-6-8 6c-1.6 1.2-3.8.9-5-.6"/>`,
};
const MPATH = (x, y, rx, ry, seed = 1) => {   // ellipse tracée à la main : rayon qui varie, dépasse son point de départ (comme au feutre)
  const pts = [], n = 28, a0 = -2.2;
  for (let k = 0; k <= n; k++) {
    const a = a0 + (k / n) * Math.PI * 2.18, w = 1 + 0.045 * Math.sin(k * 1.7 + seed) + (k / n) * 0.06;
    pts.push([x + Math.cos(a) * rx * w, y + Math.sin(a) * ry * w]);
  }
  return smooth(pts);
};
const fitPx = (text, file, base, maxW, upper) => {   // taille qui tient dans maxW px (mesure Pillow), plafonnée à base
  try { const em = +execFileSync("python3", ["-c", "import sys;from PIL import ImageFont;print(ImageFont.truetype(sys.argv[1],1000).getlength(sys.argv[2])/1000)", join("fonts", file), upper ? String(text).toUpperCase() : String(text)]).toString();
        return Math.round(Math.min(base, maxW / (em * 1.04))); } catch { return base; }
};
(plan.mini || []).forEach((m, i) => {
  const id = `mi${i}`, S = m.start, E = m.end;
  if (m.type === "card") {
    // fond : "grad" = dégradé doux aux couleurs du rush (C.grad), "flat" = uni sombre, ou une couleur "#hex"
    // 4 coins comme la réf (sombre en haut à gauche, couleur vive en haut à droite, clair en bas) ; défaut = nuit + bleu de ta marque
    const G = C.grad || gradFromAccent(ACC);
    const bg = m.bg && m.bg.startsWith("#") ? m.bg : m.bg === "flat" ? C.list[2] :
      `radial-gradient(85% 60% at 0% 0%,${G[0]} 0%,transparent 72%),radial-gradient(80% 60% at 100% 8%,${G[1]} 0%,transparent 72%),radial-gradient(90% 65% at 0% 100%,${G[2]} 0%,transparent 75%),radial-gradient(85% 60% at 100% 100%,${G[3]} 0%,transparent 72%),${G[4] || G[2]}`;
    const lines = m.lines || [];
    let row = 0, cur = W.findIndex(w => w.t >= S - 0.05);
    const html = lines.map((ln, j) => {
      if (!(j && ln.swap)) row++;
      const serif = ln.font === "serif", toks = String(ln.text).split(/\s+/).filter(Boolean);
      const fs = ln.size || fitPx(ln.text, serif ? DA.fonts.serif : DA.fonts.sans, serif ? 150 : 104, 900, !serif);
      let last = ln.at ?? S, first = null;
      const spans = toks.map((tk, k) => {
        let t = ln.at != null && ln.whole ? ln.at : null;
        if (t == null) {   // le mot apparaît quand il est dit (cherché dans la transcription, 3 s max après le mot d'avant)
          const f = W.findIndex((w, x) => x >= Math.max(cur, 0) && w.t >= last - 0.05 && w.t <= last + 3 && normK(w.text) === normK(tk));
          if (f >= 0) { t = W[f].t; cur = f + 1; } else t = last + (k ? 0.12 : 0);
        }
        t = Math.max(t, S); last = t; first ??= t;
        F(`#${id}l${j}w${k}`, "{opacity:0,y:8}", `opacity:1,y:0,duration:.14,ease:"power2.out"`, t);
        return `<span class="mw" id="${id}l${j}w${k}">${esc(serif ? tk : tk.toUpperCase())}</span>`;
      }).join(" ");
      // swap : la ligne remplace celle d'avant au même endroit (« IMPORTANT » -> « ASSET »)
      if (j && ln.swap) F(`#${id}l${j - 1}`, "{opacity:1}", `opacity:0,duration:.01`, (first ?? S) - 0.01);
      return `<div class="mcl${serif ? " ser" : ""}" id="${id}l${j}" style="grid-row:${row};font-size:${fs}px">${spans}</div>`;
    }).join("");
    layers += `<div class="mcard" id="${id}" style="background:${bg}"><div class="mstack">${html}</div></div>`;
    V(`#${id}`, S, E, "{}", "{}", 0.001);   // coupe sèche, pas de fondu (réf)
    cues.push({ kind: "list", at: S });
  } else if (m.type === "icon") {
    const names = [].concat(m.icon || "eye"), sz = m.size || 210, gap = 40, tot = names.length * sz + (names.length - 1) * gap;
    const svg = names.map((nm, k) => `<svg class="micon" id="${id}i${k}" viewBox="0 0 48 48" width="${sz}" height="${sz}" style="left:${Math.round(540 - tot / 2 + k * (sz + gap))}px">${MINI_ICONS[nm] || MINI_ICONS.eye}</svg>`).join("");
    const cross = m.cross != null ? `<svg class="mcross" viewBox="0 0 48 48" width="${sz * 1.1}" height="${sz * 1.1}" style="left:${Math.round(540 - sz * 0.55)}px;top:${-sz * 0.05}px"><path id="${id}x0" pathLength="1" d="M8 8L40 40"/><path id="${id}x1" pathLength="1" d="M40 8L8 40"/></svg>` : "";
    layers += `<div class="mico" id="${id}" style="top:${m.y ?? 380}px;height:${sz}px">${svg}${cross}</div>`;
    V(`#${id}`, S, E, "{}", "{}", 0.01);
    names.forEach((_, k) => F(`#${id}i${k}`, "{scale:.7,opacity:0}", `scale:1,opacity:1,duration:.32,ease:"expo.out"`, S + k * (m.stagger ?? 0.25)));
    if (m.cross != null) {
      F(`#${id}x0`, "{strokeDashoffset:1}", `strokeDashoffset:0,duration:.2,ease:"power2.out"`, m.cross);
      F(`#${id}x1`, "{strokeDashoffset:1}", `strokeDashoffset:0,duration:.2,ease:"power2.out"`, m.cross + 0.14);
      names.forEach((_, k) => F(`#${id}i${k}`, "{opacity:1}", `opacity:.45,duration:.25`, m.cross));
    }
  } else if (m.type === "shot") {
    // dimensions réelles de l'image (le cercle est donné en px de l'image source)
    let iw = 1080, ih = 600;
    try { [iw, ih] = execFileSync("python3", ["-c", "import sys;from PIL import Image;print(*Image.open(sys.argv[1]).size)", m.src]).toString().trim().split(" ").map(Number); } catch {}
    const w = m.w || 820, c = m.circle;
    const ring = c ? `<svg class="mring" viewBox="0 0 ${iw} ${ih}" preserveAspectRatio="none"><path id="${id}c" pathLength="1" d="${MPATH(c.cx, c.cy, c.rx, c.ry, i + 1)}" style="stroke:${c.color || "#fff"};stroke-width:${c.width || 7 * iw / w}"/></svg>` : "";
    // zones mortes : la carte grossit de 3 % depuis son centre (dérive) -> son haut remonte de 1,5 % de sa hauteur ; bas ≤ 1480 px
    const sh = Math.round(w * ih / iw), top = Math.min(Math.max(m.y ?? 290, 272 + Math.ceil(0.015 * sh)), Math.round(1478 - 1.015 * sh));
    layers += `<div class="mshot" id="${id}" style="top:${top}px"><div class="msw" id="${id}w" style="width:${w}px"><img src="${esc(m.src)}" style="width:${w}px"/>${ring}</div></div>`;
    V(`#${id}`, S, E, "{}", "{}", 0.01);
    F(`#${id}w`, "{scale:.9,opacity:0,y:20}", `scale:1,opacity:1,y:0,duration:.4,ease:"expo.out"`, S);
    F(`#${id}w`, "{scale:1}", `scale:1.03,duration:${(E - S - 0.4).toFixed(3)},ease:"none"`, S + 0.4);   // dérive lente : jamais figé
    if (c) F(`#${id}c`, "{strokeDashoffset:1}", `strokeDashoffset:0,duration:${c.dur || 0.5},ease:"power1.inOut"`, c.at);
  } else console.log(`mini inconnu : ${m.type}`);
});

const html = `<!doctype html><html><head><meta charset="utf-8"/>
<meta name="viewport" content="width=1080, height=1920"/>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
  @font-face{font-family:"Mont";src:url("fonts/${DA.fonts.sans}");font-weight:100 900}
  @font-face{font-family:"Serif";src:url("fonts/${DA.fonts.serif}");font-style:italic}
  @font-face{font-family:"Sub";src:url("fonts/${DA.fonts.sub}");font-weight:100 900}
  *{margin:0;padding:0;box-sizing:border-box}
  html,body{width:1080px;height:1920px;background:#000;overflow:hidden;font-family:"Mont",sans-serif}
  #root{position:relative;width:1080px;height:1920px;background:#000;overflow:hidden}
  #camwrap{position:absolute;inset:0;transform-origin:50% 32%;will-change:transform;backface-visibility:hidden;transform:translateZ(0)}
  #cam,.fg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
  #cam{filter:saturate(1.06)}
  .fg{z-index:3}
  .num{position:absolute;left:0;right:0;top:270px;z-index:2;opacity:0;text-align:center;color:${C.text};
       font-weight:600;font-size:440px;line-height:1;letter-spacing:-12px;text-shadow:0 10px 60px rgba(0,0,0,.25)}
  .num .suf{font-size:300px;margin-left:30px;letter-spacing:0;display:inline-block}
  .num .nct{display:inline-block;text-align:center;font-variant-numeric:tabular-nums;transform-origin:50% 85%}
  #vign{position:absolute;inset:0;z-index:4;pointer-events:none;background:radial-gradient(ellipse 85% 75% at 50% 42%,transparent 60%,rgba(0,0,0,.38) 100%)}
  .cap{position:absolute;left:120px;right:120px;top:${SUBY}px;z-index:10;opacity:0;text-align:center;color:${C.text};
       font-family:"Sub";font-weight:700;font-size:${SUBSIZE}px;line-height:1.05;letter-spacing:${SUBTRACK}px;text-shadow:0 3px 18px rgba(0,0,0,.55)}
  .cap em{font-family:"Serif";font-style:italic;font-weight:400;font-size:${plan.kwSize || 132}px;letter-spacing:0;text-transform:none;text-shadow:0 0 24px rgba(255,255,255,.25),0 3px 18px rgba(0,0,0,.5)}
  .mo{position:absolute;inset:0;z-index:2;opacity:0;background:radial-gradient(120% 70% at 50% 28%,#1a2444 0%,#0c1226 55%,#06080f 100%);overflow:hidden}
  .mo-led{position:absolute;left:-5%;right:-5%;top:1170px;height:10px;border-radius:10px;background:${ACC};opacity:.55;filter:blur(14px)}
  .mo-safe{position:absolute;inset:0;transform-origin:540px 0}
  .mo-cw{position:absolute;left:65px;right:65px;top:0;bottom:0;overflow:hidden}
  .mo-cwi{position:absolute;left:-65px;top:0;width:1080px;height:1920px}
  .mo-panel{position:absolute;left:120px;right:120px;top:150px;height:760px;border-radius:40px;background:rgba(18,26,52,.82);border:1px solid rgba(255,255,255,.10);box-shadow:0 30px 80px rgba(0,0,0,.45);transform-origin:50% 0}
  .mo-h{position:absolute;left:44px;top:40px;font-family:"Mont";font-weight:700;font-size:40px;color:#fff;letter-spacing:.5px}
  .mo-row{position:absolute;left:28px;right:28px;height:92px;border-radius:24px;display:flex;align-items:center;gap:22px;padding:0 22px;box-sizing:border-box;opacity:0;transform-origin:50% 50%}
  .mo-av{display:block;width:60px;height:60px;border-radius:50%;flex:none}
  .mo-ln{flex:1;display:flex;flex-wrap:wrap;align-items:center;gap:10px}
  .mo-ln b{display:block;height:16px;border-radius:8px;background:rgba(255,255,255,.85)}
  .mo-ln s{display:block;flex-basis:100%;height:12px;border-radius:6px;background:rgba(255,255,255,.28);max-width:var(--w,80%)}
  .mo-row em{font-family:"Mont";font-style:normal;font-size:22px;color:rgba(255,255,255,.45);flex:none}
  .mo-vip{background:rgba(79,155,255,.16);border:2px solid ${ACC}}
  .mo-badge{flex:none}
  .moimg{background:#fff}
  .moi-page{position:absolute;left:0;top:0;width:1080px;height:auto;will-change:transform}
  .moi-cover{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;will-change:transform}
  .mo-kpi{position:absolute;left:44px;top:110px;font-family:"Mont";font-weight:700;font-size:96px;color:#fff;opacity:0}
  .mo-kpil{position:absolute;left:48px;top:228px;font-family:"Mont";font-size:28px;color:rgba(255,255,255,.55)}
  .mo-chart{position:absolute;left:40px;right:40px;top:290px;width:760px;height:360px}
  .mo-leg{position:absolute;left:44px;bottom:36px;font-family:"Mont";font-size:24px;color:rgba(255,255,255,.7);display:flex;align-items:center;gap:12px}
  .mo-leg i{display:inline-block;width:34px;height:8px;border-radius:4px;margin-left:18px}
  .mo-seal{position:absolute;left:390px;top:170px;width:300px;height:300px;transform-origin:50% 50%}
  .mo-gauge{position:absolute;left:150px;right:150px;top:560px}
  .mo-gl{font-family:"Mont";font-weight:700;font-size:34px;color:#fff;margin-bottom:16px;letter-spacing:1px;text-transform:uppercase}
  .mo-gt{height:26px;border-radius:13px;background:rgba(255,255,255,.12);overflow:hidden}
  .mo-gf{height:100%;width:14%;border-radius:13px;background:${ACC}}
  .mo-stars{display:flex;gap:18px;margin-top:26px}
  .mo-star{width:58px;height:58px;opacity:.15}
  .mo-rw,.mo-bw{position:absolute;inset:0;transform-origin:50% 30%}
  .mo-ring{position:absolute;left:260px;top:170px;width:560px;height:560px;transform-origin:50% 50%}
  .mo-rv{position:absolute;left:0;right:0;top:372px;display:flex;align-items:baseline;justify-content:center;font-family:"Mont";font-weight:700;font-size:170px;line-height:1;color:#fff}
  .mo-rn{display:inline-block;text-align:center;font-variant-numeric:tabular-nums;transform-origin:50% 80%}
  .mo-rv i{display:inline-block;font-style:normal;font-size:84px;margin-left:6px}
  .mo-rl{position:absolute;left:90px;right:90px;top:752px;text-align:center;font-family:"Serif";font-style:italic;font-size:62px;line-height:1.1;color:#fff}
  .mo-bt{position:absolute;left:0;right:0;top:160px;text-align:center;font-family:"Serif";font-style:italic;font-size:96px;color:#fff}
  .mo-bv{position:absolute;left:0;right:0;top:290px;text-align:center;font-family:"Mont";font-weight:700;font-size:130px;line-height:1;color:#fff;font-variant-numeric:tabular-nums;transform-origin:50% 80%}
  .mo-bars{position:absolute;left:100px;right:100px;top:450px;height:420px;display:flex;align-items:flex-end;justify-content:center;gap:34px}
  .mo-bc{position:relative;height:100%;display:flex;align-items:flex-end}
  .mo-bar{border-radius:18px 18px 6px 6px;background:rgba(255,255,255,.22);transform:scaleY(0);transform-origin:50% 100%}
  .mo-bac{background:${ACC};box-shadow:0 0 40px rgba(${RGB(ACC)},.35)}
  .mo-bl{position:absolute;top:100%;left:-20px;right:-20px;margin-top:14px;text-align:center;font-family:"Mont";font-weight:600;font-size:28px;color:rgba(255,255,255,.6);white-space:nowrap}
  .mo-tile{position:absolute;top:300px;width:300px;height:300px;border-radius:64px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;box-shadow:0 30px 70px rgba(0,0,0,.45)}
  .mo-tile span{font-family:"Mont";font-weight:700;font-size:30px;color:#fff}
  .mo-ai{left:90px;background:linear-gradient(145deg,#1d2a52,#0f1630);border:2px solid rgba(255,255,255,.12)}
  .mo-ig{right:90px;background:linear-gradient(135deg,#7a3cf0,#e1306c 55%,#f7a23b)}
  .mo-link{position:absolute;left:390px;top:440px;width:300px;height:20px}
  .mo-dot{position:absolute;left:384px;top:438px;width:24px;height:24px;border-radius:50%;background:#fff;opacity:0}
  .mo-pill{position:absolute;left:0;right:0;margin:auto;top:680px;width:max-content;padding:20px 40px;border-radius:999px;background:${ACC};color:#0B0B0D;font-family:"Mont";font-weight:700;font-size:38px;opacity:0}
  .mo-vq{position:absolute;left:0;right:0;top:190px;text-align:center;font-family:"Serif";font-style:italic;font-size:120px;color:#fff;opacity:0}
  .mo-vr{position:absolute;left:130px;right:130px;height:130px;border-radius:32px;display:flex;align-items:center;gap:28px;padding:0 34px;box-sizing:border-box;background:rgba(18,26,52,.85);border:1px solid rgba(255,255,255,.12);opacity:0;top:420px}
  .mo-vy{top:590px;border:2px solid ${ACC};background:rgba(79,155,255,.14)}
  .mo-vr span{position:relative;font-family:"Mont";font-weight:700;font-size:44px;color:#fff}
  .mo-vi{display:flex;align-items:center;justify-content:center;width:70px;height:70px;border-radius:50%;font-style:normal;font-family:"Mont";font-weight:700;font-size:40px;flex:none}
  .mo-vx{background:rgba(255,255,255,.12);color:rgba(255,255,255,.75)}
  .mo-vc{background:${ACC};color:#0B0B0D}
  .mo-vs{position:absolute;left:0;top:50%;height:6px;width:0%;background:#fff;border-radius:3px}
  .mo-prof{height:700px}
  .mo-pav{position:absolute;left:50%;top:60px;margin-left:-95px;width:190px;height:190px;border-radius:50%;background:linear-gradient(135deg,${ACC},#1c2a55);border:6px solid rgba(255,255,255,.12)}
  .mo-pname{position:absolute;left:0;right:0;top:290px;display:flex;align-items:center;justify-content:center;gap:14px;font-family:"Mont";font-weight:700;font-size:46px;color:#fff}
  .mo-pstats{position:absolute;left:40px;right:40px;top:390px;display:flex;justify-content:space-around;text-align:center;font-family:"Mont";color:#fff}
  .mo-pstats b{display:block;font-size:44px}
  .mo-pstats span{font-size:24px;color:rgba(255,255,255,.55)}
  .mo-pbtn{position:absolute;left:60px;right:60px;top:520px;height:76px;border-radius:20px;background:${ACC};color:#0B0B0D;font-family:"Mont";font-weight:700;font-size:32px;display:flex;align-items:center;justify-content:center}
  .mo-ptag{position:absolute;left:0;right:0;margin:auto;top:625px;width:max-content;padding:10px 26px;border-radius:999px;background:rgba(255,255,255,.1);color:#fff;font-family:"Mont";font-weight:600;font-size:28px;opacity:0}
  .mo-cr{position:absolute;left:50px;right:50px;opacity:0}
  #mo0r0,.mo-cr:nth-child(1){top:90px}
  .mo-cr + .mo-cr{top:320px}
  .mo-crl{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:18px}
  .mo-crl b{font-family:"Mont";font-weight:700;font-size:48px;color:#fff}
  .mo-crl span{font-family:"Mont";font-weight:600;font-size:30px;color:rgba(255,255,255,.65)}
  .mo-wc{position:absolute;top:230px;width:390px;height:520px;border-radius:44px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:24px;background:rgba(18,26,52,.88);border:1px solid rgba(255,255,255,.12);box-shadow:0 30px 70px rgba(0,0,0,.45);opacity:0}
  .mo-wl{left:90px;border:3px solid ${ACC};background:rgba(79,155,255,.14)}
  .mo-wr{right:90px}
  .mo-wc b{font-family:"Mont";font-weight:700;font-size:46px;color:#fff}
  .mo-wt{padding:12px 26px;border-radius:999px;background:rgba(255,255,255,.12);color:#fff;font-family:"Mont";font-weight:600;font-size:30px}
  .mo-wok{background:${ACC};color:#0B0B0D}
  .mo-fgw{position:absolute;inset:0;z-index:3;transform-origin:50% 100%;filter:drop-shadow(0 16px 20px rgba(0,0,0,.45))}
  .cap em + em{margin-left:.16em}
  /* fond clair (green screen devant une page / une image blanche) : ombre serrée + diffuse au lieu d'une bande grise */
  .cap.onlight,.cap.onlight em{text-shadow:0 0 2px rgba(0,0,0,.9),0 2px 5px rgba(0,0,0,.8),0 6px 26px rgba(0,0,0,.55)}
  .htitle{position:absolute;left:0;right:0;z-index:11;opacity:0;text-align:center;color:#fff;text-shadow:0 3px 18px rgba(0,0,0,.55);
          padding:30px 60px 38px;background:linear-gradient(180deg,rgba(0,0,0,0),rgba(0,0,0,.5) 22%,rgba(0,0,0,.5) 78%,rgba(0,0,0,0))}
  .htitle.onlight{background:none;text-shadow:0 0 2px rgba(0,0,0,.9),0 2px 5px rgba(0,0,0,.8),0 6px 26px rgba(0,0,0,.55)}
  .ht1{font-family:"Sub";font-weight:700;font-size:${Math.round(SUBSIZE * 46 / 52)}px;letter-spacing:${plan.subTrack ?? DA.subTrack ?? 1}px;text-transform:uppercase}
  .ht2{font-family:"Serif";font-style:italic;font-size:104px;line-height:1.05}   /* 2 mots forts : sinon l'espace est celui de la petite police (« badgebleu ») */
  .list{position:absolute;inset:0;z-index:20;opacity:0;color:${C.text};
        background:radial-gradient(ellipse 90% 60% at 50% 45%,${C.list[0]} 0%,${C.list[1]} 55%,${C.list[2]} 100%)}
  .lt{position:absolute;top:290px;left:65px;right:65px;text-align:center;text-shadow:0 0 28px rgba(${C.halo},.45)}
  .l1{font-weight:600;font-size:76px;letter-spacing:-.5px}
  .l2{font-family:"Serif";font-style:italic;font-size:110px;line-height:1;margin-top:4px}
  .page{position:absolute;top:540px;left:65px;right:65px;display:flex;gap:24px;opacity:0}
  .col{flex:1;display:flex;flex-direction:column;gap:calc(var(--fs,43px)*30/43)}
  .it{font-weight:600;font-size:var(--fs,43px);line-height:1.12;text-align:center;opacity:0;text-shadow:0 0 18px rgba(${C.glow},.7),0 0 4px rgba(255,255,255,.35)}
  .broll{position:absolute;inset:0;z-index:6;opacity:0;overflow:hidden;background:#000}
  .bw{position:absolute;inset:0;will-change:transform;backface-visibility:hidden}
  .bm{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;filter:saturate(1.04)}
  .ins{position:absolute;left:0;right:0;z-index:8;opacity:0;display:flex;justify-content:center;pointer-events:none}
  .iw{will-change:transform;backface-visibility:hidden}
  .trk{inset:0;display:block}.itk{position:absolute;left:0;top:0;will-change:transform}.ictr{transform:translate(-50%,-50%)}
  .ins img{display:block;height:auto;filter:drop-shadow(0 18px 40px rgba(0,0,0,.55)) drop-shadow(0 0 30px rgba(${C.glow},.25))}
  .bul{position:absolute;left:70px;top:1330px;z-index:9;display:flex;gap:22px;opacity:0}
  .dot{width:96px;height:96px;border-radius:50%;border:3px solid rgba(255,255,255,.85);color:#fff;font-weight:600;font-size:50px;
       display:flex;align-items:center;justify-content:center;backdrop-filter:blur(6px)}
  /* --- guide OPUS : punch, mot géant, hook --- */
  #punch{position:absolute;inset:0;transform-origin:50% 38%;will-change:transform;backface-visibility:hidden}
  .bigw{position:absolute;left:0;right:0;z-index:2;opacity:0;text-align:center;font-family:"Serif";font-style:italic;line-height:1.22;color:${C.text};white-space:nowrap}
  .bwt{position:relative;text-shadow:0 10px 60px rgba(0,0,0,.25)}
  .lm{display:inline-block;overflow:hidden;vertical-align:top;padding:0 .14em;margin:0 -.14em}
  .lc{display:inline-block}
  .echo{position:absolute;left:0;right:0;top:0;opacity:0;color:transparent;-webkit-text-stroke:2px rgba(255,255,255,.85)}
  .bar{position:absolute;left:0;right:0;z-index:40;background:#000}
  #rec{position:absolute;inset:0;z-index:39;opacity:0;pointer-events:none}
  .cn{position:absolute;width:86px;height:86px;border:5px solid rgba(255,255,255,.9)}
  .c1{top:270px;left:70px;border-right:0;border-bottom:0}.c2{top:270px;right:70px;border-left:0;border-bottom:0}
  .c3{bottom:440px;left:70px;border-right:0;border-top:0}.c4{bottom:440px;right:70px;border-left:0;border-top:0}
  .rlab,.rtc{position:absolute;top:1350px;color:#fff;font-weight:600;font-size:38px;letter-spacing:3px;text-shadow:0 2px 12px rgba(0,0,0,.5)}
  .rlab{left:180px;display:flex;align-items:center;gap:14px}.rtc{right:180px;font-variant-numeric:tabular-nums}
  .rlab b{width:24px;height:24px;border-radius:50%;background:#ff3b30;display:block}
  /* --- pleins écrans preuve --- */
  .proof{position:absolute;inset:0;z-index:20;opacity:0;overflow:hidden}
  .paper{background:#F4F0E8;color:#1b1b1f}
  .grid{background-color:#fbfaf7;color:#1b1b1f;background-position:center;background-size:72px 72px;
        background-image:linear-gradient(rgba(20,20,30,.07) 2px,transparent 2px),linear-gradient(90deg,rgba(20,20,30,.07) 2px,transparent 2px)}
  .dark{color:#fff;background:radial-gradient(ellipse 90% 60% at 50% 40%,${C.list[0]} 0%,${C.list[1]} 55%,${C.list[2]} 100%)}
  .grain{position:absolute;inset:0;width:100%;height:100%;pointer-events:none}
  .pt{position:absolute;left:65px;right:65px;text-align:center;opacity:0}
  .p1{font-weight:600;font-size:58px;letter-spacing:-.5px}
  .p2{font-family:"Serif";font-style:italic;font-size:120px;line-height:1;margin-top:6px}
  .chart{position:absolute;left:60px;width:960px;height:860px;overflow:visible}
  .chart text{font-family:"Mont";font-weight:600}
  .ax{stroke:#1b1b1f;stroke-width:4;stroke-dasharray:1px 2px;stroke-dashoffset:1.05px}
  .lvl{stroke:rgba(27,27,31,.25);stroke-width:2;stroke-dasharray:8 10;opacity:0}
  .lvt{font-size:36px;fill:rgba(27,27,31,.5);opacity:0}
  .stp{font-size:34px;fill:rgba(27,27,31,.45);opacity:0}
  .pa{fill:none;stroke:#8f8b83;stroke-width:9;stroke-linecap:round;stroke-dasharray:1px 2px;stroke-dashoffset:1.05px}
  .pb{fill:none;stroke:${ACC};stroke-width:13;stroke-linecap:round;stroke-dasharray:1px 2px;stroke-dashoffset:1.05px;filter:drop-shadow(0 8px 18px rgba(${RGB(ACC)},.35))}
  .la{font-size:42px;fill:#6d6a63;opacity:0}
  .chart .lb{font-family:"Serif";font-style:italic;font-weight:400;font-size:70px;fill:${ACC};opacity:0}
  .dotb{fill:${ACC};opacity:0}
  .clock{position:absolute;left:90px;top:560px;width:900px;height:900px;overflow:visible}
  .clock .fill{fill:#fff;opacity:0;filter:drop-shadow(0 20px 40px rgba(0,0,0,.08))}
  .face{fill:none;stroke:#1b1b1f;stroke-width:7;stroke-dasharray:1px 2px;stroke-dashoffset:1.05px}
  .tick{stroke:#1b1b1f;stroke-width:5;stroke-linecap:round;opacity:0}.tick.big{stroke-width:9}
  .hand line{stroke:#1b1b1f;stroke-linecap:round}.hand{opacity:0}.mh line{stroke-width:10}.hh line{stroke-width:16}
  .ghost{opacity:0}.ghost line{stroke:${ACC};stroke-width:10;stroke-linecap:round}
  .hub{fill:${ACC};opacity:0}
  .ybg{fill:none;stroke:rgba(27,27,31,.08);stroke-width:26;stroke-linecap:round}
  .yon{fill:none;stroke:${ACC};stroke-width:26;stroke-linecap:round;opacity:0}
  .ylab{font-family:"Mont";font-weight:600;font-size:30px;fill:#1b1b1f;opacity:.3}
  .persp{position:absolute;left:90px;right:90px;perspective:1800px}
  .card{position:relative;border-radius:52px;padding:56px;overflow:hidden;background:linear-gradient(160deg,rgba(255,255,255,.14),rgba(255,255,255,.04));
        border:1.5px solid rgba(255,255,255,.16);box-shadow:0 60px 120px rgba(0,0,0,.55),inset 0 1px 0 rgba(255,255,255,.25);backdrop-filter:blur(30px)}
  .glare{position:absolute;top:-20%;left:-60%;width:40%;height:140%;background:linear-gradient(100deg,transparent,rgba(255,255,255,.10),transparent);transform:rotate(12deg)}
  .chd{display:flex;align-items:center;gap:18px;font-size:34px;font-weight:600}
  .cico{width:58px;height:58px;border-radius:16px;background:linear-gradient(135deg,${ACC},#14204f)}
  .capp{flex:1}
  .cpill{font-size:26px;font-weight:600;padding:10px 22px;border-radius:40px;background:rgba(255,255,255,.1);color:rgba(255,255,255,.75)}
  .clab{margin-top:40px;font-size:38px;font-weight:500;color:rgba(255,255,255,.6)}
  .cval{margin-top:6px;font-weight:600;line-height:1;letter-spacing:-5px;font-variant-numeric:tabular-nums;white-space:nowrap}
  .cdel{display:inline-block;margin-top:18px;font-size:32px;font-weight:600;padding:10px 24px;border-radius:40px;background:rgba(${RGB(ACC)},.22);color:#d6e2ff;opacity:0}
  .cchart{display:block;margin-top:30px;width:100%;height:300px;overflow:visible}
  .cgl{stroke:rgba(255,255,255,.08);stroke-width:2}
  .cln{fill:none;stroke:${ACC};stroke-width:7;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1px 2px;stroke-dashoffset:1.05px;filter:drop-shadow(0 0 14px rgba(${RGB(ACC)},.6))}
  .car{opacity:0}.cdot{fill:#fff;opacity:0}
  .tiles{display:flex;gap:20px;margin-top:30px}
  .tile{flex:1;border-radius:30px;padding:26px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);opacity:0}
  .tlb{font-size:26px;color:rgba(255,255,255,.55);font-weight:500}
  .tv{font-size:54px;font-weight:600;margin-top:8px;font-variant-numeric:tabular-nums;white-space:nowrap}
  /* --- CTA commentaires --- */
  .cta{position:absolute;inset:0;z-index:30;opacity:0;background:rgba(0,0,0,.28)}
  .sheet{position:absolute;left:0;right:0;top:600px;bottom:0;background:#1c1c1e;border-radius:44px 44px 0 0;transform:translateY(1300px);
         box-shadow:0 -20px 60px rgba(0,0,0,.4);color:#f5f5f5;overflow:hidden}
  .grab{width:90px;height:9px;border-radius:9px;background:#5a5a5e;margin:18px auto 0}
  .shh{text-align:center;font-weight:600;font-size:36px;margin-top:24px}
  .shh span{color:#8e8e93;font-weight:500;margin-left:12px;font-size:30px}
  .sheetc{background:none;box-shadow:none}
  .ctam{position:absolute;left:0;right:0;top:0;height:1480px;overflow:hidden}
  .kbbg{position:absolute;top:586px;left:0;right:0;bottom:0;background:#2c2c2e}
  .cv{position:absolute;top:110px;left:0;right:0;height:366px;overflow:hidden}
  .cl{transform:translateY(-130px)}
  .cr{height:130px;display:flex;align-items:flex-start;gap:24px;padding:14px 65px 0}
  .av{width:84px;height:84px;border-radius:50%;flex:none;display:flex;align-items:center;justify-content:center;font-weight:600;font-size:38px;color:#fff}
  .cb{flex:1}
  .cu{font-size:29px;font-weight:600;color:#c7c7cc}.cu span{color:#8e8e93;font-weight:500;margin-left:12px}
  .ct{font-size:38px;font-weight:600;margin-top:4px;letter-spacing:.5px}
  .cre{font-size:26px;color:#8e8e93;margin-top:8px;font-weight:500}
  .chh{width:46px;height:46px;margin-top:22px;flex:none}
  .inp{position:absolute;top:476px;left:0;right:0;height:110px;display:flex;align-items:center;gap:22px;padding:0 65px;border-top:1px solid #2c2c2e}
  .inp .av{width:76px;height:76px;font-size:34px}
  .field{flex:1;height:84px;border-radius:44px;border:2px solid #3a3a3c;display:flex;align-items:center;padding:0 30px;font-size:38px;font-weight:600;position:relative;letter-spacing:1px}
  .tch{display:none}
  .caret{display:block;width:4px;height:46px;background:${ACC};margin-left:4px}
  .ph{position:absolute;left:30px;color:#8e8e93;font-weight:500;font-size:34px;letter-spacing:0}
  .send{font-weight:700;font-size:34px;color:${ACC};opacity:.35}
  .kb{position:absolute;top:586px;left:65px;right:65px;padding:12px 0 0;display:flex;flex-direction:column;gap:10px}
  .kr{display:flex;justify-content:center;gap:10px}
  .key{width:86px;height:62px;border-radius:12px;background:#4a4a4e;color:#fff;font-size:34px;font-weight:500;display:flex;align-items:center;justify-content:center}
  .key.sp{width:520px;font-size:28px;color:#c7c7cc}
  /* --- style minimaliste (plan.mini) --- */
  .mcard{position:absolute;inset:0;z-index:20;opacity:0;display:flex;align-items:center;justify-content:center}
  .mstack{display:grid;justify-items:center;row-gap:4px;text-align:center;margin-top:-40px}
  .mcl{grid-column:1;font-family:"Mont";font-weight:800;color:#fff;line-height:1.02;letter-spacing:1px;white-space:nowrap}
  .mcl.ser{font-family:"Serif";font-style:italic;font-weight:400;letter-spacing:0;line-height:.98}
  .mw{display:inline-block;opacity:0}
  .mico{position:absolute;left:0;right:0;z-index:8;opacity:0;pointer-events:none}
  .micon{position:absolute;top:0;fill:none;stroke:#fff;stroke-width:1.3;stroke-linecap:round;stroke-linejoin:round;opacity:0;overflow:visible;filter:drop-shadow(0 4px 14px rgba(0,0,0,.5))}
  .mcross{position:absolute;fill:none;stroke:#FF453A;stroke-width:3.6;stroke-linecap:round;overflow:visible}
  .mcross path{stroke-dasharray:1;stroke-dashoffset:1}
  .mshot{position:absolute;left:0;right:0;z-index:8;opacity:0;display:flex;justify-content:center;pointer-events:none}
  .msw{position:relative;border-radius:34px;overflow:hidden;border:1.5px solid rgba(255,255,255,.14);box-shadow:0 30px 70px rgba(0,0,0,.55);will-change:transform;opacity:0}
  .msw img{display:block;height:auto}
  .mring{position:absolute;inset:0;width:100%;height:100%;overflow:visible}
  .mring path{fill:none;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1}
</style></head>
<body>
  <div id="root" data-composition-id="root" data-start="0" data-duration="${dur.toFixed(2)}" data-width="1080" data-height="1920" data-fps="30">
    <div id="punch"><div id="camwrap">
      <video id="cam" class="clip" src="${plan.cam}" muted playsinline preload="auto" data-start="0" data-duration="${dur.toFixed(2)}" data-track-index="0" data-has-audio="false"></video>
      ${camLayers}
    </div></div>
    <div id="vign"></div>
    ${layers}
  </div>
  <script>
    window.__timelines = window.__timelines || {};
    var tl = gsap.timeline({paused:true}), DUR = ${dur.toFixed(3)};
    function V(s, a, b, from, to, fin, out) {
      fin = Math.min(fin, Math.max(b - a, .001));
      out = Math.min(out || 0, Math.max((b - a - fin) / 2, 0));
      var X = {immediateRender:false, ease:"none"};
      tl.fromTo(s, {opacity:0}, Object.assign({opacity:0, duration:Math.max(a, .001)}, X), 0);
      tl.fromTo(s, Object.assign({opacity:0}, from), Object.assign({opacity:1, duration:fin}, X, {ease:"power2.out"}, to), a);
      tl.fromTo(s, {opacity:1}, Object.assign({opacity:1, duration:Math.max(b - a - fin - out, .001)}, X), a + fin);
      if (out > 0) tl.fromTo(s, {opacity:1}, {opacity:0, duration:out, ease:"power2.in", immediateRender:false}, b - out);
      tl.fromTo(s, {opacity:0}, Object.assign({opacity:0, duration:Math.max(DUR - b, .001)}, X), b);
    }
    ${ops}
    tl.to({},{duration:DUR},0);
    window.__timelines["root"] = tl;
  </script>
</body></html>`;
writeFileSync(out, html);
writeFileSync(join(dirname(out), "cues.json"), JSON.stringify(cues, null, 1));
console.log(`${W.length} mots · ${groups.length} sous-titres · ${cuts.length} plans · ${(plan.numbers || []).length} chiffres · ${bigwords.length} mots géants · ${lists.length} listes · ${proofs.length} preuves${cta ? " · CTA " + cta.word : ""}${plan.hook ? " · hook" : ""} -> ${out}`);
