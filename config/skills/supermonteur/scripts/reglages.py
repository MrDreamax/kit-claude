"""Réglages du monteur, au même endroit pour tous les scripts.

Trois sources, de la plus faible à la plus forte :
  1. config.json (dans le skill) : dossiers par défaut (~/Documents/Contenu/medias/...), niveaux de son, kit SFX.
  2. ~/Documents/Brain/00-Moi/marque.json (lu par Brain/_outils/marque.py) : tes couleurs et ta police de marque.
  3. ~/Documents/Brain/00-Moi/montage.json (facultatif, à toi, jamais écrasé par une mise à jour du kit) :
     ta DA de montage et tes réglages. Mêmes clés que config.json, plus un bloc "da" :
       {"higgsfield": true,
        "da": {"fonts": {"sans": "Montserrat.ttf", "serif": "InstrumentSerif-Italic.ttf"},
               "colors": {"text": "#FFFFFF", "accent": "#2563EB"}, "subSize": 52, "zoomGap": [5, 8],
               "ambiance": "lumière chaude, bois, décor sobre", "music": ["motivation", "piano"]}}
     Écrit par outils/style-lab (round.py lock) ou à la main par Claude après tes réponses.

Utilisation dans un script :
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import reglages
    CFG = reglages.charger()     # dict, tous les "~" sont développés
    DA = reglages.da()           # polices (fichiers de fonts/), couleurs, taille des sous-titres, rythme
En ligne de commande : `python3 reglages.py da` ou `python3 reglages.py config` (JSON sur la sortie standard).
"""
import json, os, pathlib, sys

SKILL = pathlib.Path(__file__).resolve().parent.parent
BRAIN = pathlib.Path(os.environ.get("KIT_BRAIN", pathlib.Path.home() / "Documents" / "Brain"))
MONTAGE = BRAIN / "00-Moi" / "montage.json"

# police de marque (Google Fonts) -> fichier libre fourni dans fonts/ (sinon Montserrat)
POLICES_FOURNIES = {"montserrat": "Montserrat.ttf", "inter": "Inter.ttf", "oswald": "Oswald.ttf", "poppins": "Poppins-SemiBold.ttf",
                    "bebas neue": "BebasNeue-Regular.ttf"}


def _lire(p):
    try:
        return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _fusion(a, b):
    for k, v in b.items():
        if k.startswith("_"):
            continue
        if isinstance(v, dict) and isinstance(a.get(k), dict):
            _fusion(a[k], v)
        elif v not in (None, ""):
            a[k] = v
    return a


def _tilde(o):
    if isinstance(o, str):
        return os.path.expanduser(o) if o.startswith("~") else o
    if isinstance(o, dict):
        return {k: _tilde(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_tilde(v) for v in o]
    return o


def charger():
    """config.json du skill + montage.json de l'utilisateur, "~" développé."""
    c = _lire(SKILL / "config.json")
    _fusion(c, {k: v for k, v in _lire(MONTAGE).items() if k != "da"})
    return _tilde(c)


def marque():
    """Couleurs et polices de marque (marque.json, valeurs neutres par défaut si absent)."""
    sys.path.insert(0, str(BRAIN / "_outils"))
    try:
        import marque as m
        return m.charger()
    except Exception:
        return {"couleurs": {"principale": "#2563EB", "foncee": "#111827", "clair": "#FFFFFF"}, "polices": {"titre": "Archivo", "texte": "Inter"}}


def _mix(h, vers, t):
    h = h.lstrip("#")
    a = [int(h[i:i + 2], 16) for i in (0, 2, 4)]
    return "#%02X%02X%02X" % tuple(round(x + (v - x) * t) for x, v in zip(a, vers))


def da():
    """DA de montage = valeurs par défaut du skill, puis ta marque, puis montage.json (bloc "da")."""
    m = marque()
    c = m.get("couleurs", {})
    fonce = c.get("foncee", "#111827")
    police = POLICES_FOURNIES.get(str(m.get("polices", {}).get("titre", "")).lower(), "Montserrat.ttf")
    d = {
        "fonts": {"sans": police, "serif": "InstrumentSerif-Italic.ttf"},
        "colors": {"text": "#FFFFFF", "accent": c.get("principale", "#2563EB"),
                   "list": [fonce, _mix(fonce, (0, 0, 0), .45), _mix(fonce, (0, 0, 0), .7)], "halo": "0,0,0", "glow": "0,0,0"},
        "zoomGap": [5, 8],
        "broll": {"prompt_higgsfield": "isolated single object, true real-world colors and shape (use a reference image of the real object), "
                                       "lit to match the scene of the rush: {lumiere_rush}, soft realistic shadow, plain flat background for cut-out, "
                                       "photorealistic, no text"},
    }
    perso = _lire(MONTAGE).get("da", {})
    _fusion(d, perso)
    d["fonts"].setdefault("sub", d["fonts"]["sans"])
    if not perso.get("fonts", {}).get("sub"):
        d["fonts"]["sub"] = d["fonts"]["sans"]
    return _tilde(d)


if __name__ == "__main__":
    quoi = sys.argv[1] if len(sys.argv) > 1 else "config"
    print(json.dumps(da() if quoi == "da" else charger(), ensure_ascii=False, indent=1))
