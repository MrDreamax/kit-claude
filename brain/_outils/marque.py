"""La marque de l'utilisateur (couleurs, polices, logo, nom) pour tous les skills contenu.

Lit ~/Documents/Brain/00-Moi/marque.json (rempli par le skill bienvenue ou directeur-artistique).
Fichier absent ou incomplet : valeurs neutres par défaut, rien ne casse.

Dans un moteur de skill :
    import sys, pathlib; sys.path.insert(0, str(pathlib.Path.home() / 'Documents/Brain/_outils'))
    import marque
    m = marque.charger()            # dict complet
    marque.css_vars({'--blue': 'principale', '--navy': 'foncee'})   # -> "<style>:root{...}</style>"
    marque.lien_polices()           # -> balise <link> Google Fonts des 2 polices
    marque.chrome()                 # -> chemin de Chrome / Chromium (Mac, Windows, Linux)
    marque.chrome_run(['--print-to-pdf=out.pdf', url])   # lance Chrome headless, relance s'il se bloque
"""
import json, os, pathlib, shutil, signal, subprocess, tempfile

BRAIN = pathlib.Path(os.environ.get('KIT_BRAIN', pathlib.Path.home() / 'Documents' / 'Brain'))
FICHIER = BRAIN / '00-Moi' / 'marque.json'

DEFAUT = {
    'nom': '',            # pied de page des PDF, signature des carrousels
    'pseudo': '',         # @ Instagram (vide = jamais affiché)
    'logo': '',           # chemin d'un PNG (vide = pas de logo)
    'couleurs': {
        'principale': '#2563EB',  # boutons, numéros, mots forts
        'foncee': '#111827',      # titres, fonds sombres
        'texte': '#1F2937',
        'doux': '#6B7280',        # textes secondaires
        'ligne': '#E5E7EB',
        'teinte': '#EFF4FF',      # fonds clairs (encadrés)
        'clair': '#FFFFFF',       # fond
    },
    'polices': {'titre': 'Archivo', 'texte': 'Inter'},  # Google Fonts
}


def charger():
    m = json.loads(json.dumps(DEFAUT))
    try:
        perso = json.loads(FICHIER.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return m
    for k, v in perso.items():
        if isinstance(v, dict) and isinstance(m.get(k), dict):
            m[k].update({a: b for a, b in v.items() if b})
        elif v:
            m[k] = v
    return m


def couleur(nom):
    return charger()['couleurs'].get(nom, DEFAUT['couleurs'].get(nom, '#000000'))


def css_vars(correspondance):
    """correspondance = {'--var-du-gabarit': 'nom de couleur'} -> bloc <style> à coller après le CSS du gabarit."""
    c = charger()['couleurs']
    lignes = ';'.join(f'{var}:{c.get(nom, nom)}' for var, nom in correspondance.items())
    p = charger()['polices']
    return f"<style>:root{{{lignes};--police-titre:'{p['titre']}';--police-texte:'{p['texte']}'}}</style>"


def lien_polices(graisses='400;500;600;700;800'):
    p = charger()['polices']
    fam = '&'.join(f"family={f.replace(' ', '+')}:wght@{graisses}" for f in dict.fromkeys([p['titre'], p['texte']]))
    return f'<link href="https://fonts.googleapis.com/css2?{fam}&display=swap" rel="stylesheet">'


def logo():
    """Chemin du logo s'il existe, sinon None."""
    l = charger().get('logo') or ''
    p = pathlib.Path(os.path.expanduser(l)) if l else None
    return p if p and p.is_file() else None


def chrome():
    for c in ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
              '/Applications/Chromium.app/Contents/MacOS/Chromium',
              r'C:\Program Files\Google\Chrome\Application\chrome.exe',
              r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
              os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe')]:
        if os.path.isfile(c):
            return c
    for n in ['google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser', 'chrome']:
        if shutil.which(n):
            return shutil.which(n)
    raise SystemExit('Chrome introuvable : installe Google Chrome (skill logiciels), puis relance.')


def chrome_run(args, essais=4, delai=45):
    """Lance Chrome sans interface et rend sa sortie texte. Chrome se bloque parfois au démarrage
    (mise à jour, trousseau) : on le tue et on réessaie avec un profil neuf."""
    exe = chrome()
    for _ in range(essais):
        prof = tempfile.mkdtemp(prefix='chrome-')
        p = subprocess.Popen([exe, '--headless=new', '--use-mock-keychain', '--disable-gpu', '--no-first-run',
                              f'--user-data-dir={prof}', '--virtual-time-budget=5000'] + list(args),
                             stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                             text=True, start_new_session=True)
        try:
            sortie = p.communicate(timeout=delai)[0]
            shutil.rmtree(prof, ignore_errors=True)
            return sortie
        except subprocess.TimeoutExpired:
            try:
                os.killpg(p.pid, signal.SIGKILL)
            except Exception:  # Windows : pas de groupe de processus
                p.kill()
            p.communicate()
            shutil.rmtree(prof, ignore_errors=True)
    raise SystemExit('Chrome ne répond pas après 4 essais : ferme les fenêtres Chrome inutiles, puis relance.')
