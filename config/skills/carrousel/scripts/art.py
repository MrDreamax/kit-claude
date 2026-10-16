"""Illustrations 2D façon motion design pour les carrousels (SVG dessinés, JAMAIS d'image IA).
Les couleurs de marque viennent de ~/Documents/Brain/00-Moi/marque.json (via marque.py) : change ta DA, les dessins suivent.
Zone de dessin : 1080 x 900 (haut de la slide). Chaque fonction renvoie un <svg class="art">…</svg> prêt à poser dans une slide « art ».
Un sujet nouveau = une nouvelle fonction ici (mêmes couleurs, même fond MIST, 2 à 4 éléments deco) ou un .svg à part.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path.home() / "Documents" / "Brain" / "_outils"))
import marque  # noqa: E402


def _mix(a, b, t):
    ra = [int(a.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    rb = [int(b.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    return "#%02X%02X%02X" % tuple(round(ra[i] * (1 - t) + rb[i] * t) for i in range(3))


_C = marque.charger()["couleurs"]
# Couleurs de marque (marque.json) : NAVY = foncée, BLUE = principale, WHITE = fond, MIST = teinte claire.
NAVY, BLUE, WHITE, MIST = _C["foncee"], _C["principale"], _C["clair"], _C["teinte"]
SKY, PALE = _mix(BLUE, WHITE, 0.35), _mix(BLUE, WHITE, 0.8)  # déclinaisons de la couleur principale
# Petites touches d'appoint, les mêmes pour toutes les marques (2 à 4 par dessin, jamais plus).
YELLOW, CORAL, MINT = "#FFC845", "#FF6B5B", "#2EC4A6"
# Couleurs d'objets (la métaphore des pommes) : ne suivent pas la marque.
GREEN, GREEN_D, LEAF, STEM = "#9CCB52", "#7DB03A", "#3E9A4F", "#5A3A28"
RED, RED_D = "#E5484D", "#C2363B"
FONT = "font-family:var(--police-titre),sans-serif"


def frame(inner, deco_items=()):
    """Fond commun : grand cercle MIST + petits éléments déco, puis le dessin."""
    return (f'<svg class="art" viewBox="0 0 1080 900"><circle cx="540" cy="450" r="400" fill="{MIST}"/>'
            f'{deco(deco_items)}{inner}</svg>')


def deco(items):
    """Petits éléments motion design : ("dot"|"ring"|"plus"|"spark"|"dots", x, y, couleur). Jamais en haut à droite sur le texte."""
    out = []
    for kind, x, y, c in items:
        if kind == "dot":
            out.append(f'<circle cx="{x}" cy="{y}" r="16" fill="{c}"/>')
        elif kind == "ring":
            out.append(f'<circle cx="{x}" cy="{y}" r="20" fill="none" stroke="{c}" stroke-width="7"/>')
        elif kind == "plus":
            out.append(f'<path d="M{x - 18},{y} H{x + 18} M{x},{y - 18} V{y + 18}" stroke="{c}" stroke-width="8" stroke-linecap="round"/>')
        elif kind == "spark":
            out.append(f'<path d="M{x},{y - 26} Q{x + 4},{y - 4} {x + 26},{y} Q{x + 4},{y + 4} {x},{y + 26} '
                       f'Q{x - 4},{y + 4} {x - 26},{y} Q{x - 4},{y - 4} {x},{y - 26} Z" fill="{c}"/>')
        elif kind == "dots":
            out.append("".join(f'<circle cx="{x + i * 22}" cy="{y + j * 22}" r="4" fill="{c}"/>' for i in range(4) for j in range(3)))
    return "".join(out)


# ---------- pommes (métaphore « tous pareils / sois différent ») ----------
APPLE = "M0,-30 C18,-50 54,-42 54,-8 C54,30 30,54 9,49 C4,48 -4,48 -9,49 C-30,54 -54,30 -54,-8 C-54,-42 -18,-50 0,-30 Z"


def apple(x, y, s, body=GREEN, shade=GREEN_D, uid="a"):
    return (f'<g transform="translate({x},{y}) scale({s})">'
            f'<ellipse cx="0" cy="58" rx="34" ry="6" fill="{NAVY}" opacity=".08"/>'
            f'<clipPath id="c{uid}"><path d="{APPLE}"/></clipPath>'
            f'<path d="{APPLE}" fill="{body}"/>'
            f'<ellipse cx="50" cy="12" rx="24" ry="56" fill="{shade}" clip-path="url(#c{uid})"/>'
            f'<ellipse cx="-26" cy="-12" rx="7" ry="15" transform="rotate(-20 -26 -12)" fill="#FFFFFF" opacity=".55"/>'
            f'<path d="M0,-30 C1,-40 3,-46 6,-52" stroke="{STEM}" stroke-width="5" fill="none" stroke-linecap="round"/>'
            f'<path d="M5,-46 C14,-62 34,-60 36,-54 C28,-43 13,-41 5,-46 Z" fill="{LEAF}"/></g>')


def apples_grid(red_at=None):
    """12 pommes vertes identiques ; red_at=[ligne, colonne] en met une rouge, entourée et étincelante."""
    out, k = [], 0
    for r, y in enumerate((250, 450, 650)):
        for c, x in enumerate((225, 435, 645, 855)):
            k += 1
            if red_at and list(red_at) == [r, c]:
                out.append(f'<circle cx="{x}" cy="{y}" r="112" fill="{WHITE}"/>'
                           f'<circle cx="{x}" cy="{y}" r="112" fill="none" stroke="{YELLOW}" stroke-width="6" stroke-dasharray="2 16" stroke-linecap="round"/>')
                out.append(apple(x, y, 1.62, RED, RED_D, f"r{k}"))
                out.append(deco([("spark", x + 98, y - 92, YELLOW), ("spark", x - 104, y + 70, YELLOW)]))
            else:
                out.append(apple(x, y, 1.45, uid=f"g{k}"))
    return frame("".join(out), [("dot", 120, 120, YELLOW), ("ring", 975, 260, CORAL), ("plus", 960, 800, MINT), ("dots", 70, 760, SKY)])


# ---------- téléphones (copier les gros comptes, contenu identique) ----------
TILES = [SKY, YELLOW, MINT, CORAL, BLUE, PALE, MINT, SKY, YELLOW]


def phone(x, y, s, frame_c=NAVY, avatar=CORAL, op=1):
    tiles = "".join(f'<rect x="{-96 + c * 66}" y="{40 + r * 66}" width="58" height="58" rx="10" fill="{TILES[r * 3 + c]}" opacity="{op}"/>'
                    for r in range(3) for c in range(3))
    return (f'<g transform="translate({x},{y}) scale({s})">'
            f'<rect x="-128" y="-230" width="256" height="460" rx="40" fill="{WHITE}" stroke="{frame_c}" stroke-width="8"/>'
            f'<circle cx="0" cy="-130" r="44" fill="{avatar}" opacity="{op}"/>'
            f'<rect x="-70" y="-66" width="140" height="16" rx="8" fill="{NAVY}" opacity="{op}"/>'
            f'<rect x="-50" y="-36" width="100" height="12" rx="6" fill="{PALE}"/>{tiles}</g>')


def copies():
    """Un gros compte (badge vérifié) recopié 3 fois en plus pâle."""
    big = phone(330, 450, 1.25)
    badge = (f'<g transform="translate(398,240)"><circle r="30" fill="{BLUE}" stroke="{WHITE}" stroke-width="6"/>'
             '<path d="M-12,1 L-3,10 L13,-9" stroke="#fff" stroke-width="6" fill="none" stroke-linecap="round" stroke-linejoin="round"/></g>')
    smalls, arrows = [], []
    for x, y in ((800, 210), (860, 450), (800, 690)):
        smalls.append(phone(x, y, 0.5, "#9DB8D2", CORAL, 0.55))
        arrows.append(f'<path d="M500,450 C600,450 {x - 160},{y} {x - 80},{y}" stroke="{BLUE}" stroke-width="5" fill="none" stroke-dasharray="4 14" stroke-linecap="round"/>'
                      f'<path d="M{x - 96},{y - 12} L{x - 78},{y} L{x - 96},{y + 12}" stroke="{BLUE}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    return frame("".join(arrows) + big + badge + "".join(smalls), [("spark", 150, 150, YELLOW), ("ring", 120, 760, MINT), ("dots", 960, 790, SKY)])


# ---------- escalier (méthode en 3 étapes) ----------
def stairs():
    steps = [(250, 560, 180, PALE, NAVY), (460, 430, 310, SKY, WHITE), (670, 300, 440, BLUE, WHITE)]
    out = [f'<rect x="190" y="740" width="740" height="10" rx="5" fill="{PALE}"/>']
    for i, (x, y, h, fill, ink) in enumerate(steps, start=1):
        out.append(f'<rect x="{x}" y="{y}" width="190" height="{h}" rx="18" fill="{fill}"/>'
                   f'<text x="{x + 95}" y="{y + 118}" text-anchor="middle" style="{FONT};font-weight:800" font-size="120" fill="{ink}">{i}</text>')
    out.append(f'<line x1="765" y1="300" x2="765" y2="150" stroke="{NAVY}" stroke-width="7" stroke-linecap="round"/>'
               f'<path d="M768,154 L862,182 L768,212 Z" fill="{YELLOW}"/>')
    return frame("".join(out), [("spark", 940, 300, YELLOW), ("dot", 640, 220, CORAL), ("plus", 170, 300, MINT), ("ring", 930, 560, CORAL), ("dots", 120, 600, SKY)])


# ---------- courbe qui monte (résultats, croissance, preuve) ----------
def chart_up():
    bars = [(250, 600, PALE), (390, 520, SKY), (530, 430, MINT), (670, 320, BLUE)]
    out = [f'<rect x="200" y="700" width="680" height="10" rx="5" fill="{PALE}"/>']
    for x, y, c in bars:
        out.append(f'<rect x="{x}" y="{y}" width="100" height="{700 - y}" rx="16" fill="{c}"/>')
    out.append(f'<path d="M250,560 C380,520 470,470 560,380 S720,220 820,170" stroke="{CORAL}" stroke-width="10" fill="none" stroke-linecap="round"/>'
               f'<path d="M790,150 L838,160 L812,202" stroke="{CORAL}" stroke-width="10" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    return frame("".join(out), [("spark", 880, 330, YELLOW), ("dot", 180, 200, YELLOW), ("plus", 940, 760, MINT), ("dots", 90, 560, SKY)])


# ---------- messages privés (DM, setting, closing) ----------
def chat():
    out = [f'<rect x="280" y="120" width="520" height="660" rx="48" fill="{WHITE}" stroke="{NAVY}" stroke-width="8"/>',
           f'<circle cx="350" cy="190" r="26" fill="{CORAL}"/><rect x="392" y="178" width="160" height="14" rx="7" fill="{NAVY}"/>',
           f'<rect x="320" y="250" width="300" height="74" rx="30" fill="{PALE}"/>',
           f'<rect x="460" y="350" width="300" height="74" rx="30" fill="{BLUE}"/>',
           f'<rect x="320" y="450" width="250" height="74" rx="30" fill="{PALE}"/>',
           f'<rect x="420" y="550" width="340" height="74" rx="30" fill="{BLUE}"/>',
           f'<g transform="translate(372,690)"><circle cx="0" cy="0" r="9" fill="{SKY}"/><circle cx="30" cy="0" r="9" fill="{SKY}"/><circle cx="60" cy="0" r="9" fill="{SKY}"/></g>',
           f'<g transform="translate(800,140)"><circle r="40" fill="{CORAL}"/><text x="0" y="16" text-anchor="middle" style="{FONT};font-weight:700" font-size="44" fill="#fff">3</text></g>']
    return frame("".join(out), [("spark", 180, 260, YELLOW), ("ring", 900, 700, MINT), ("dots", 110, 640, SKY)])


# ---------- checklist (erreurs à éviter, étapes faites) ----------
def checklist(n=3):
    out = [f'<rect x="270" y="130" width="540" height="640" rx="40" fill="{WHITE}" stroke="{NAVY}" stroke-width="8"/>',
           f'<rect x="460" y="105" width="160" height="56" rx="16" fill="{BLUE}"/>']
    for i in range(n):
        y = 260 + i * 160
        out.append(f'<rect x="330" y="{y}" width="72" height="72" rx="16" fill="{MIST}" stroke="{SKY}" stroke-width="5"/>'
                   f'<path d="M346,{y + 38} L362,{y + 54} L388,{y + 20}" stroke="{MINT}" stroke-width="9" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
                   f'<rect x="436" y="{y + 14}" width="300" height="16" rx="8" fill="{NAVY}"/><rect x="436" y="{y + 44}" width="200" height="12" rx="6" fill="{PALE}"/>')
    return frame("".join(out), [("spark", 900, 250, YELLOW), ("dot", 170, 640, CORAL), ("plus", 180, 220, MINT), ("dots", 900, 700, SKY)])


ARTS = {"apples_grid": apples_grid, "copies": copies, "stairs": stairs, "chart_up": chart_up, "chat": chat, "checklist": checklist}
