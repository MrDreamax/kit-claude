"""Super (29/10/2026) : les 4 Super dans UNE fenêtre.
10/11/2026 : Super devient un STUDIO. On arrive sur le studio (studio.html) : des robots en discussion qui pilotent
les vrais outils (SuperMonteur, SuperCarrousel, SuperVeille, publication). Les anciens onglets restent sur /onglets.
Les outils refusent les ordres venant d'une autre page : Super leur transmet donc les demandes du studio (/x/<outil>/...),
de serveur à serveur. http://localhost:8800 · /api/etat = qui répond · POST /api/rallumer/<outil> = relance son lancer.sh.
"""
import glob, http.client, io, json, os, re, shutil, subprocess, sys, urllib.parse, urllib.request, zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ICI = os.path.dirname(os.path.abspath(__file__))
APPS = os.path.dirname(ICI)
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8800
OUTILS = {"veille": ("superveille", 8811), "da": ("superda", 8781), "monteur": ("supermonteur", 8801), "carrousel": ("supercarrousel", 8797)}
OUTILS = {k: v for k, v in OUTILS.items() if os.path.isdir(os.path.join(APPS, v[0]))}   # 20/11 : kit client = seulement les outils installés
MONTAGES = os.path.join(APPS, "supermonteur", "reels")
DEMO_F = os.path.join(ICI, "demo.json")
ESSAI_F = os.path.join(ICI, "essai.on")   # 11/11 : mode essai tenu par le SERVEUR (live) : aucune publication ne part, quelle que soit la page
essai = lambda: os.path.exists(ESSAI_F)

# ---- 10/11/2026 : chaque robot = un vrai Claude Code avec son skill, le studio n'est que l'écran. ----
# Sécurité : aucun MCP (donc ni publication ni message), aucune écriture, aucune commande libre.
# Le robot lit les notes et lance seulement les commandes de sa liste. Seule la page Super peut lui parler (autorise()).
DOSSIER = os.environ.get("SUPER_DOSSIER") or os.path.expanduser("~/Documents/Stratosphere")
def prenom_du_mac():   # 11/11 : le Studio dit bonjour au prénom de celui qui l'utilise (kit client compris), jamais un nom écrit en dur
    try: return (subprocess.run(["id", "-F"], capture_output=True, text=True, timeout=3).stdout.split() or [""])[0][:30]
    except Exception: return ""
NOM = os.environ.get("SUPER_NOM") or prenom_du_mac() or "toi"
SKILLS = os.path.expanduser("~/.claude/skills")
COMMUN = ("Tu parles à {nom} depuis le Studio : une simple fenêtre de chat, pas un terminal. Il est grand débutant. "
          "Réponds en français, très court : 3 phrases courtes maximum avant les boutons, une seule chose à regarder, jamais de date ni de nom de fichier, mots simples, une idée par ligne, pas de tiret cadratin, pas de tableau, pas de chemin de fichier, pas de jargon. "
          "Ne dis jamais « le moteur », « l'analyse », « version 3 » ni rien de la cuisine interne : parle à la 1re personne (j'ai coupé, j'ai baissé) et de ce qu'il voit. "
          "Un défaut que tu as déjà signalé : ne le répète pas, propose juste le bouton qui le corrige. "
          "Dès que tu signales un vrai défaut (pas une question de goût), le bouton qui le corrige est le premier et porte « ! » devant. "
          "Ne commence par « c'est bon » ou « c'est fait » que si tout est bon : s'il reste un défaut, dis-le en premier. Un moment de la vidéo se dit toujours pareil (vers 4 s), jamais une autre plage que celle que tu as annoncée. "
          "Pour demander quelque chose, écris la question en une ligne. Va vite. "
          "Termine CHAQUE réponse par une dernière ligne seule : BOUTONS: choix 1 | choix 2 | choix 3 "
          "(2 ou 3 réponses qu'il peut cliquer, 1 à 4 mots chacune, ton conseil en premier). Si un défaut doit être corrigé avant de valider ou de publier, mets « ! » devant ce premier bouton (ex : BOUTONS: !Enlève le CTA | Autre chose). ")
ROLES = {
    "scripteur": {
        "consigne": ("Tu es Le Scripteur. Suis le skill scripteur, section 0 (écrire comme ses reels, vite). "
                     "Livre TOUJOURS le script COMPLET, mot à mot, à lire tel quel face caméra : jamais des points à improviser, jamais de PDF ni de maquette. "
                     "Mets le script entre une ligne ===SCRIPT=== et une ligne ===FIN===. Dans ce bloc : 1re ligne = le titre, puis une phrase par ligne. "
                     "Avant le bloc, une seule phrase. Après le bloc, rien d'autre que la ligne BOUTONS, avec des retouches (ex : Plus court | Autre accroche) : l'écran ajoute déjà le bouton pour valider. "
                     "Longueur d'un reel : 35 à 55 secondes dites, soit 90 à 140 mots, sauf s'il demande plus long. "
                     "La phrase avant le bloc dit l'angle choisi en mots simples (ex : J'ai pris l'angle de la confiance.), jamais tes règles ni ce que tu as évité. "
                     "Écris pour l'oral : phrases courtes qui se disent d'un souffle, zéro phrase de remplissage. "
                     "Accroche en 2 temps qui arrête le pouce : un choc, puis la conséquence, en parlant à « tu » (ex : Un client te demande une remise. Tu cèdes. Tu viens de le perdre.). "
                     "Ses clients en général : au masculin générique (ceux qui...). "
                     "Si on te demande une autre accroche : propose 3 accroches numérotées sans réécrire le script, et BOUTONS: Accroche 1 | Accroche 2 | Accroche 3 ; quand il en choisit une, redonne le script complet avec. "
                     "Ses règles en mémoire et dans le Brain passent avant le skill : relis-les (par exemple, s'il a dit zéro appel à l'action dans ses reels, n'en mets aucun). "),
        "outils": ["Read", "Glob", "Grep", "Skill", f"Bash(python3 {SKILLS}/scripteur/scripts/mes_reels.py:*)"],
    },
    "monteur": {
        "consigne": ("Tu es Le Monteur. Tu suis les règles du skill supermonteur, mais tu ne montes jamais toi-même : le moteur SuperMonteur monte, l'écran le lance pour toi. "
                     "Un rush = le dossier apps/supermonteur/reels/<id>/ (words.rush.json ou words.json = ce qu'il dit, devine.json = analyse, etat.json = état ; après montage : cut.words.json, gardien.json). "
                     "Quand une vidéo arrive : lis ce qu'il dit et l'analyse, et regarde l'image de la planche (champ planche de devine.json) : l'analyse rate souvent un visage filmé de loin, alors ne dis jamais qu'on ne le voit pas sans l'avoir vérifié sur la planche, et ne parle jamais de l'analyse ni de ses erreurs. Puis en 2 lignes max : de quoi parle la vidéo en une phrase, et dis-lui que tu la montes sobre (lui + sous-titres) ; lance TOUT DE SUITE le montage en Minimaliste, sans lui demander de choisir (12/11, choix de l'utilisateur : Minimaliste pour TOUS les montages). Ajoute : « Tu veux des images, des textes ou de la musique en plus ? Dis-le dans tes notes à la fin. » NOMS DE STYLE = POUR TOI SEUL : Dynamique, Minimaliste, Comparatif, Interview, Inspiration ; n'écris JAMAIS ces noms à l'utilisateur. Un autre style seulement s'il le demande clairement (une vidéo exemple en lien = Inspiration avec ce lien). "
                     "Pour lancer le montage : une phrase, puis une dernière ligne seule ===MONTER <id> <Style>=== (Inspiration : ===MONTER <id> Inspiration <lien du reel à reprendre>===, demande le lien avant). "
                     "Pour une retouche : une phrase, puis une dernière ligne seule ===RETOUCHE <id> | <sa demande réécrite clairement pour le moteur>===. Si la retouche demande d'ajouter des images, de changer de style, de refaire le montage, ou de couper quelque chose qu'il dit (un mot, un « euh », une hésitation, une reprise) : ===RETOUCHE <id> lourde | <sa demande>=== (plus long, environ 10 min, dis-le). "
                     "Avec ces lignes, pas de BOUTONS : l'écran lance le moteur, suit le montage et te prévient. N'invente jamais de souci (permission, Mac) : si quelque chose rate, dis exactement quoi. Si le moteur bloque à cause d'une de ses règles (ex : un plan de moins de 2 s), explique-la en 3 lignes maximum et en mots simples et propose en BOUTONS des retouches qui passent (ex : remettre le mot coupé). "
                     "Quand l'écran dit que le montage est fini : lis cut.words.json et gardien.json, vérifie qu'aucun mot n'est coupé ni répété, et dis en 2 lignes ce que tu as fait et ce qu'il faut regarder, honnêtement. Jamais de durée (l'écran l'affiche), jamais de mots techniques (contrôles, gardien, plan, bloc, dérush, secondes de coupe) : parle de ce qu'il voit et entend. 3 lignes maximum. "
                     "BOUTONS = des retouches (l'écran ajoute déjà le bouton pour valider). "
                     "Ses notes peuvent arriver posées sur l'image exacte de la vidéo (« à 3,2 s : ... ») : réponds en une phrase qui reprend ce que tu vas changer, puis UNE seule ligne ===RETOUCHE <id> | <résumé de toutes les notes>=== (lourde si l'une d'elles demande des images, un autre style, de tout refaire, OU de couper quelque chose qu'il dit : un mot, un « euh », une hésitation, une reprise, un bout de phrase ; la retouche rapide ne sait pas recouper) ; l'écran envoie lui-même chaque note au moteur avec son moment exact. "
                     "Il peut rouvrir une ancienne vidéo : le message te le dit, travaille alors sur ce rush-là. "
                     "Changer la police, la couleur ou le style de TOUTES ses vidéos : dis-lui d'appuyer sur « Mon style » en haut de la discussion (aucune ligne d'ordre). Pour cette vidéo seulement : retouche. "),
        "outils": ["Read", "Glob", "Grep", "Skill"],
        "effort": "medium",   # 11/11 l'utilisateur : moyen (mesuré : élevé 2x plus lent à relire, pas meilleur)
    },
    "carrousel": {
        "consigne": ("Tu es Le Carrousel. Tu suis les règles du skill carrousel (ses vraies photos, jamais d'image IA), mais tu ne dessines jamais toi-même : le moteur SuperCarrousel fabrique, l'écran le lance pour toi. "
                     "Un projet = apps/supercarrousel/projets/<id>/ (demande.json, brouillon.json, v<N>/description.json = textes et légende). "
                     "Si l'idée est claire, lance tout de suite sans rien demander : une phrase avec le titre de la cover et la promesse, puis une dernière ligne seule "
                     "===CARROUSEL idee | <l'idée précise avec ton angle>=== (n'annonce pas la phrase exacte de la cover : le moteur l'écrit, l'écran la montre). Depuis son script : ===CARROUSEL script=== . Depuis un reel : ===CARROUSEL reel | <lien>=== . Depuis sa vidéo montée : ===CARROUSEL video=== . "
                     "Pour une retouche : une phrase, puis ===RETOUCHE <id> <numéro de l'image, 1 si c'est tout le carrousel> | <sa demande réécrite clairement>=== . "
                     "Avec ces lignes, pas de BOUTONS : l'écran fabrique (2 à 4 min) et te prévient. N'invente jamais de souci : si quelque chose rate, dis exactement quoi. "
                     "Quand l'écran dit que c'est fini : lis v<N>/description.json et réponds en 2 phrases maximum : 1) il est prêt, avec les mots de la cover tels qu'ils sont ; 2) s'il y en a une, LA chose à regarder. Ne résume jamais le contenu des images. La légende qu'il voit et qu'il publie = legendes.instagram (courte, sans hashtag) : ne juge que celle-là, jamais les champs caption ni hashtags. "
                     "Quand c'est fini, regarde aussi les images. Un défaut évident sur une image (carte ou cadre vide, phrase coupée en deux, texte qui déborde ou illisible) : corrige-le tout de suite toi-même, sans rien lui demander : une phrase (« Je vois un souci sur l'image 2, je le corrige. »), puis la ligne ===RETOUCHE <id> <numéro de l'image> | <la correction>=== . Une seule fois : si le message te dit que tu l'as déjà corrigé seul, présente honnêtement. Un choix de goût (photo, couleur, angle) n'est pas un défaut : propose-le en bouton. "
                     "La dernière image « Commente <mot> » fait partie du modèle du carrousel (skill carrousel) : ce n'est pas un défaut, ne la signale pas comme un souci et ne propose pas de l'enlever, sauf s'il le demande. "
                     "BOUTONS = des retouches (l'écran ajoute déjà le bouton pour valider). "
                     "Ses notes peuvent arriver image par image (« image 2 : ... ») : une phrase qui reprend ce que tu vas changer, puis UNE seule ligne ===RETOUCHE <id> 1 | <résumé de toutes les notes>=== ; l'écran envoie lui-même chaque note au moteur avec son numéro d'image. "
                     "Il peut rouvrir un ancien carrousel : le message te le dit, travaille alors sur ce projet-là. S'il veut le refaire en entier : ===CARROUSEL idee | <même sujet, nouvel angle>===. "
                     "Changer la police, la couleur ou le modèle de TOUS ses carrousels : dis-lui d'appuyer sur « Mon style » en haut de la discussion (aucune ligne d'ordre). "),
        "outils": ["Read", "Glob", "Grep", "Skill"],
    },
    "publieur": {
        "consigne": ("Tu es Le Publieur. Tu suis les règles du skill publieur et de son carnet (3 posts par jour maximum, aux heures où son audience est là), "
                     "mais tu ne publies jamais toi-même : l'écran programme, et seulement après sa double confirmation. "
                     "Quand il te donne la liste de ce qui est prêt : une phrase qui dit ton plan, puis le plan en dernières lignes, exactement : "
                     "une ligne ===PLAN=== , puis une ligne par post « <id> | AAAA-MM-JJ HH:MM | <titre court et clair, 3 à 7 mots, tiré de ce qu'il dit dans la vidéo si le titre donné est coupé> » (heure de son Mac, à partir de demain), puis une ligne ===FIN=== . "
                     "Ce qui est fait aujourd'hui passe en premier. Ta phrase avant le plan tient en 2 lignes maximum : le rythme, d'où viennent les heures (ses vrais chiffres, ou des heures par défaut), et un seul point d'attention s'il y en a un. "
                     "BOUTONS = des changements de plan (ex : Plus tôt | Seulement la vidéo) ; jamais de bouton pour garder ou valider le plan, l'écran ajoute déjà le bouton pour programmer. "
                     "S'il demande un changement, redonne le plan complet au même format. "),
        "outils": ["Read", "Glob", "Grep", "Skill"],
    },
}
for _r in ROLES.values():
    _r["consigne"] = _r["consigne"].replace("MONTAPI", "http://localhost:8801/api")
    _r["outils"] = [o.replace("MONTAPI", "http://localhost:8801/api") for o in _r["outils"]]


def binaire_claude():
    w = shutil.which("claude")
    if w: return w
    c = glob.glob(os.path.expanduser("~/Library/Application Support/Claude/claude-code/*/*/claude.app/Contents/MacOS/claude"))
    def version(x):
        try: return tuple(int(n) for n in re.search(r"claude-code/([\d.]+)/", x).group(1).split("."))
        except Exception: return (0,)
    return max(c, key=version) if c else None


def etape(outil, entree):
    cmd = str((entree or {}).get("command", ""))
    if "mes_reels" in cmd: return "Je relis tes derniers reels…"
    if outil == "Skill": return "J'ouvre ma méthode…"
    if "supermonteur/reels" in str((entree or {}).get("file_path", "")) + str((entree or {}).get("path", "")): return "Je regarde ta vidéo…"
    if outil in ("Read", "Glob", "Grep"): return "Je lis tes notes…"
    return "Je travaille…"


_TITRES = {}
def titres_reels():
    out = {}
    for d in glob.glob(os.path.join(MONTAGES, "*")):
        for n in ("cut.words.json", "words.json", "words.rush.json"):
            f = os.path.join(d, n)
            if not os.path.exists(f): continue
            m = os.path.getmtime(f); k = os.path.basename(d)
            if _TITRES.get(k, (0,))[0] != m:
                try:
                    W = [w.get("text", "").strip() for w in json.load(open(f, encoding="utf-8")).get("words", [])]
                    W = [w for w in W if w and not w.endswith("--")]
                    W = " ".join(W).replace(" '", "'").replace("' ", "'").split()
                    if W and W[0][:3].lower() in ("'ai", "’ai"): W[0] = "J" + W[0]   # mot coupé par la transcription
                    W = " ".join(W).lstrip("'’,.;: ").split()
                    t, fin = [], False
                    for w in W:
                        c = lambda x: x.lower().strip(",.?!:;")
                        if t and c(w) == c(t[-1]): continue
                        t.append(w)
                        for n in (2, 3, 4):   # « prends ton objectif prends ton objectif » : bégaiement retiré
                            if len(t) >= 2 * n and [c(x) for x in t[-n:]] == [c(x) for x in t[-2 * n:-n]]: del t[-n:]
                        if w[-1] in ".?!": fin = True; break
                        if len(" ".join(t)) > 40: break
                    t = " ".join(t).rstrip(",;:").strip()
                    if len(t) > 46: t = t[:44].rsplit(" ", 1)[0]
                    if not fin: t = t.rstrip(",;: ") + "…"
                    t = t.rstrip(".")
                    _TITRES[k] = (m, t[:1].upper() + t[1:])
                except Exception: _TITRES[k] = (m, "")
            if _TITRES[k][1]: out[k] = _TITRES[k][1]
            break
    return out

def repond(port):
    try:
        urllib.request.urlopen(f"http://localhost:{port}/", timeout=1.5)
        return True
    except Exception:
        return False


class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def fichier(self, f, ctype):   # 20/11 : envoie une image ou une vidéo, par morceaux si le lecteur le demande (pour avancer dans la vidéo)
        taille = os.path.getsize(f); debut, fin = 0, taille - 1
        m = re.match(r"bytes=(\d*)-(\d*)", self.headers.get("Range") or "")
        if m and (m.group(1) or m.group(2)):
            if m.group(1): debut = int(m.group(1)); fin = int(m.group(2)) if m.group(2) else fin
            else: debut = max(0, taille - int(m.group(2)))
            fin = min(fin, taille - 1)
            self.send_response(206); self.send_header("Content-Range", f"bytes {debut}-{fin}/{taille}")
        else:
            self.send_response(200)
        self.send_header("Content-Type", ctype); self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(fin - debut + 1)); self.send_header("Cache-Control", "no-store"); self.end_headers()
        with open(f, "rb") as h:
            h.seek(debut); reste = fin - debut + 1
            try:
                while reste > 0:
                    b = h.read(min(1 << 20, reste))
                    if not b: break
                    self.wfile.write(b); reste -= len(b)
            except (BrokenPipeError, ConnectionResetError): pass

    def envoyer(self, code, corps, ctype="application/json; charset=utf-8"):
        corps = json.dumps(corps, ensure_ascii=False).encode() if isinstance(corps, (dict, list)) else corps
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(corps)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(corps)

    def vide_corps(self):   # 11/11 : un refus doit lire la demande, sinon ses restes cassent la demande suivante (connexion gardée)
        n = int(self.headers.get("Content-Length") or 0)
        while n > 0:
            b = self.rfile.read(min(1 << 16, n))
            if not b: break
            n -= len(b)

    def page(self, nom):
        return self.envoyer(200, open(os.path.join(ICI, nom), "rb").read(), "text/html; charset=utf-8")

    # ---- relais vers un outil (même machine, sans en-tête Origin) ----
    def relais(self, methode):
        m = re.match(r"^/x/(\w+)(/.*)$", self.path)
        if not m or m.group(1) not in OUTILS: self.vide_corps(); return self.envoyer(404, {"erreur": "outil inconnu"})
        if methode != "GET" and essai() and re.search(r"/publier\b", m.group(2)):
            self.vide_corps(); return self.envoyer(403, {"erreur": "mode essai : rien ne part"})
        port = OUTILS[m.group(1)][1]
        entetes = {}
        for k in ("Content-Type", "Content-Length", "X-Nom", "X-Seul", "Range"):
            if self.headers.get(k): entetes[k] = self.headers[k]
        try:
            c = http.client.HTTPConnection("127.0.0.1", port, timeout=600)
            n = int(self.headers.get("Content-Length") or 0)
            c.putrequest(methode, m.group(2), skip_accept_encoding=True)
            for k, v in entetes.items(): c.putheader(k, v)
            c.endheaders()
            while n > 0:   # gros rushs : on transmet par blocs, sans tout charger en mémoire
                bloc = self.rfile.read(min(1 << 20, n))
                if not bloc: break
                c.send(bloc)
                n -= len(bloc)
            r = c.getresponse()
        except Exception as x:
            return self.envoyer(502, {"erreur": f"l'outil {m.group(1)} ne répond pas ({x.__class__.__name__}). Relance Super."})
        self.send_response(r.status)
        longueur = r.getheader("Content-Length")
        for k in ("Content-Type", "Content-Length", "Content-Range", "Accept-Ranges", "Content-Disposition", "Cache-Control"):
            v = r.getheader(k)
            if v: self.send_header(k, v)
        if not longueur: self.send_header("Connection", "close")
        self.end_headers()
        try:
            while True:
                bloc = r.read(1 << 16)
                if not bloc: break
                self.wfile.write(bloc)
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            c.close()
        if not longueur: self.close_connection = True

    def do_GET(self):
        p = self.path.split("?")[0]
        if p in ("/", "/index.html", "/studio"): return self.page("studio.html")
        if p == "/onglets": return self.page("index.html")
        if p == "/favicon.svg": return self.envoyer(200, open(os.path.join(ICI, "favicon.svg"), "rb").read(), "image/svg+xml")
        if p == "/api/etat": return self.envoyer(200, {k: repond(port) for k, (_, port) in OUTILS.items()})
        if p == "/api/chemin-montage":   # le Carrousel part d'une vidéo montée : il lui faut son chemin sur le Mac
            rid = re.sub(r"[^\w-]", "", urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("id", [""])[0])
            try:
                e = json.load(open(os.path.join(MONTAGES, rid, "etat.json")))
                f = (e.get("versions") or [{}])[-1].get("fichier")
                chemin = os.path.join(MONTAGES, rid, f) if f else ""
                return self.envoyer(200 if chemin and os.path.isfile(chemin) else 404, {"chemin": chemin})
            except Exception:
                return self.envoyer(404, {"erreur": "montage introuvable"})
        if p == "/api/zip-carrousel":   # 11/11 : le client télécharge les images de son carrousel + la légende, en un zip
            pid = re.sub(r"[^\w-]", "", urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("id", [""])[0])
            base = os.path.join(APPS, "supercarrousel", "projets")
            try: pr = json.load(urllib.request.urlopen(f"http://127.0.0.1:{OUTILS['carrousel'][1]}/api/projet/{pid}", timeout=10))
            except Exception: return self.envoyer(404, {"erreur": "carrousel introuvable"})
            buf, n = io.BytesIO(), 0
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_STORED) as z:
                for i, u in enumerate(pr.get("slides") or [], 1):
                    f = os.path.normpath(os.path.join(base, urllib.parse.unquote(u.split("?")[0][3:])))
                    if f.startswith(base + os.sep) and os.path.isfile(f): z.write(f, f"{i:02d}.png"); n += 1
                try:
                    d = json.load(open(os.path.join(base, pid, f"v{pr.get('version')}", "description.json")))
                    cap = (d.get("legendes") or {}).get("instagram") or d.get("caption") or ""
                    if cap: z.writestr("legende.txt", cap)
                except Exception: pass
            if not n: return self.envoyer(404, {"erreur": "aucune image"})
            titre = re.sub(r"[^\w-]+", "-", ((pr.get("etat") or {}).get("titre") or pid).lower()).strip("-")[:50] or pid
            corps = buf.getvalue()
            self.send_response(200)
            self.send_header("Content-Type", "application/zip")
            self.send_header("Content-Length", str(len(corps)))
            self.send_header("Content-Disposition", f'attachment; filename="carrousel-{titre}.zip"'.encode("latin-1", "replace").decode("latin-1"))
            self.end_headers()
            return self.wfile.write(corps)
        if p == "/api/compte":   # nom du compte Metricool branché (lecture seule, aucun secret)
            try: return self.envoyer(200, {"nom": NOM, "essai": essai(), "compte": json.load(open(os.path.join(APPS, "supermonteur", "metricool.json"))).get("compte", "")})
            except Exception: return self.envoyer(200, {"nom": NOM, "essai": essai(), "compte": ""})
        if p == "/api/demo-avant":
            try: return self.envoyer(200, json.load(open(DEMO_F.replace(".json", ".avant.json"))))
            except Exception: return self.envoyer(200, {})
        if p == "/api/demo":   # 11/11 : la démo du live gardée sur le Mac (revient même si le navigateur oublie tout)
            try: return self.envoyer(200, json.load(open(DEMO_F)))
            except Exception: return self.envoyer(200, {})
        if p == "/api/activite":   # 11/11 vitrine : ce que chaque robot fait, écrit par Claude depuis le chat (activite.py)
            try: return self.envoyer(200, json.load(open(os.path.join(ICI, "activite.json"))))
            except Exception: return self.envoyer(200, {})
        if p == "/api/neuf":   # 11/11 : Studio « à neuf » : rien d'avant cette date ne s'affiche (fichiers gardés). Effacer neuf.json = tout revient.
            try: return self.envoyer(200, json.load(open(os.path.join(ICI, "neuf.json"))))
            except Exception: return self.envoyer(200, {"depuis": 0})
        if p == "/api/titres":   # 11/11 : un reel sans titre (IMG_7158, CAM20008) prend ses premiers mots dits, jamais un nom de fichier
            return self.envoyer(200, titres_reels())
        if p.startswith("/api/hist/"):   # 20/11 : historique à jour = les registres du Brain + les montages (historique.py)
            import historique as H
            k = p.rsplit("/", 1)[1]
            f = {"scripteur": H.scripts, "carrousel": H.carrousels, "publieur": H.publications, "monteur": lambda: H.montages(MONTAGES)}.get(k)
            if not f: return self.envoyer(404, {"erreur": "robot inconnu"})
            try: return self.envoyer(200, f()[:40])
            except Exception as e: return self.envoyer(500, {"erreur": str(e)})
        if p == "/api/media":   # 20/11 : image ou vidéo d'un historique (seulement Brain, Contenu, montages)
            import historique as H, mimetypes
            f = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("p", [""])[0]
            if not H.media_autorise(f, [H.BRAIN, os.path.expanduser("~/Documents/Contenu"), MONTAGES, DOSSIER]): return self.envoyer(403, {"erreur": "refusé"})
            return self.fichier(f, mimetypes.guess_type(f)[0] or "application/octet-stream")
        if p == "/api/scripts":   # 11/11 vitrine : scripts écrits par Claude dans le chat (rendus/scripts/*.md), les plus récents d'abord
            fs = sorted(glob.glob(os.path.join(ICI, "rendus", "scripts", "*.md")), key=os.path.getmtime, reverse=True)[:12]
            out = []
            for f in fs:
                t = open(f, encoding="utf-8").read()
                l = t.strip().split("\n", 1)
                out.append({"titre": l[0].lstrip("# ").strip(), "texte": (l[1] if len(l) > 1 else "").strip(), "date": os.path.getmtime(f)})
            return self.envoyer(200, out)
        if p == "/api/publies":   # 12/11 : fiche du Publieur = historique de ce qui est déjà parti (publication.json des reels et carrousels)
            out = []
            for quoi, motif in (("reel", os.path.join(MONTAGES, "*", "publication.json")), ("carrousel", os.path.join(APPS, "supercarrousel", "projets", "*", "publication.json"))):
                for pf in glob.glob(motif):
                    try: e = json.load(open(pf, encoding="utf-8"))
                    except Exception: continue
                    if e.get("statut") not in ("programme", "publie"): continue
                    out.append({"id": os.path.basename(os.path.dirname(pf)), "quoi": quoi, "titre": e.get("titre", ""), "reseaux": [x.strip() for x in (e.get("reseaux") or [])] if isinstance(e.get("reseaux"), list) else [x.strip() for x in str(e.get("reseaux") or "").replace(" et ", ",").split(",") if x.strip()],
                                "date": e.get("fini_le") or e.get("demande_le") or __import__("datetime").datetime.fromtimestamp(os.path.getmtime(pf)).strftime("%Y-%m-%dT%H:%M:%S"), "heure": e.get("heure") or e.get("fini_le") or ""})
            out.sort(key=lambda x: x["date"], reverse=True)
            vus = set(); out = [x for x in out if not ((x["quoi"], x["id"]) in vus or vus.add((x["quoi"], x["id"])))]   # 1 ligne par contenu
            return self.envoyer(200, out)
        if p.startswith("/x/"): return self.relais("GET")
        self.envoyer(404, {"erreur": "introuvable"})

    def autorise(self):
        o = self.headers.get("Origin")   # seule la page Super peut donner des ordres
        return not o or o in (f"http://localhost:{PORT}", f"http://127.0.0.1:{PORT}")

    def do_PUT(self):
        if not self.autorise(): self.vide_corps(); return self.envoyer(403, {"erreur": "refusé"})
        if self.path.startswith("/x/"): return self.relais("PUT")
        self.vide_corps(); self.envoyer(404, {"erreur": "introuvable"})

    # ---- discussion avec le Claude du robot : ses morceaux arrivent au fur et à mesure (une ligne JSON par morceau) ----
    def claude(self, robot):
        if robot not in ROLES: return self.envoyer(404, {"erreur": "robot inconnu"})
        try: q = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
        except Exception: return self.envoyer(400, {"erreur": "demande illisible"})
        msg, session = (q.get("message") or "").strip()[:4000], re.sub(r"[^\w-]", "", q.get("session") or "")
        b = binaire_claude()
        if not msg: return self.envoyer(400, {"erreur": "message vide"})
        if not b: return self.envoyer(500, {"erreur": "Claude Code n'est pas installé sur ce Mac"})
        r = ROLES[robot]
        cmd = [b, "-p", msg, "--output-format", "stream-json", "--verbose", "--include-partial-messages",
               "--append-system-prompt", COMMUN.format(nom=NOM) + r["consigne"], "--strict-mcp-config",
               "--tools", *[o.split("(")[0] for o in r["outils"]], "--allowedTools", *r["outils"],
               "--add-dir", os.path.expanduser("~/Documents/Brain"), SKILLS]
        if session and not glob.glob(os.path.expanduser("~/.claude/projects/*/" + session + ".jsonl")):
            session = ""  # conversation effacée par Claude Code : on repart, avec le rappel envoyé par le Studio
            rappel = (q.get("rappel") or "").strip()[:4000]
            if rappel: cmd[2] = "Rappel de notre conversation d'avant (ta mémoire de cette conversation a été effacée, reprends comme si de rien n'était, sans le dire) :\n" + rappel + "\n\nMaintenant, je te dis : " + msg
        if r.get("effort"): cmd += ["--effort", r["effort"]]
        if session: cmd += ["--resume", session]
        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "close")
        self.end_headers()
        self.close_connection = True
        def dire(**x):
            self.wfile.write((json.dumps(x, ensure_ascii=False) + "\n").encode()); self.wfile.flush()
        pr = subprocess.Popen(cmd, cwd=DOSSIER, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL, text=True, bufsize=1)
        fini = False
        try:
            for ligne in pr.stdout:
                try: e = json.loads(ligne)
                except Exception: continue
                t = e.get("type")
                if t == "system" and e.get("subtype") == "init" and e.get("session_id"): dire(t="session", v=e["session_id"])
                elif t == "stream_event":
                    ev = e.get("event") or {}
                    if ev.get("type") == "content_block_delta" and (ev.get("delta") or {}).get("type") == "text_delta":
                        dire(t="txt", v=ev["delta"]["text"])
                    elif ev.get("type") == "message_start": dire(t="neuf")
                elif t == "assistant":
                    for c in (e.get("message") or {}).get("content") or []:
                        if c.get("type") == "tool_use": dire(t="etape", v=etape(c.get("name"), c.get("input")))
                elif t == "result":
                    fini = True
                    dire(t="fin", v=e.get("result") or "", session=e.get("session_id") or session, erreur=bool(e.get("is_error")))
            pr.wait(timeout=30)
            if not fini: dire(t="fin", v="", session=session, erreur=True, detail=(pr.stderr.read() or "")[-300:])
        except (BrokenPipeError, ConnectionResetError):
            pr.terminate()
        except Exception as x:
            pr.terminate()
            try: dire(t="fin", v="", session=session, erreur=True, detail=str(x))
            except Exception: pass

    def do_POST(self):
        if not self.autorise(): self.vide_corps(); return self.envoyer(403, {"erreur": "refusé"})
        if self.path.startswith("/x/"): return self.relais("POST")
        if self.path.startswith("/api/claude/"): return self.claude(self.path.rsplit("/", 1)[-1])
        if self.path == "/api/essai":   # {"on": true|false}
            try: on = bool(json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}").get("on"))
            except Exception: return self.envoyer(400, {"erreur": "demande illisible"})
            if on: open(ESSAI_F, "w").write("1")
            elif essai(): os.remove(ESSAI_F)
            return self.envoyer(200, {"essai": essai()})
        if self.path.startswith("/api/demo"):
            if "copie=1" in self.path:   # avant « repartir de zéro » : la démo d'avant est mise de côté
                if os.path.exists(DEMO_F): shutil.copyfile(DEMO_F, DEMO_F.replace(".json", ".avant.json"))
                return self.envoyer(200, {"ok": True})
            try:
                n = int(self.headers.get("Content-Length") or 0)
                if n > 2_000_000: self.vide_corps(); return self.envoyer(413, {"erreur": "trop gros"})
                d = json.loads(self.rfile.read(n) or b"{}")
                if not isinstance(d, dict) or any(not k.startswith("studio.") or not isinstance(v, str) for k, v in d.items()): raise ValueError
                tmp = DEMO_F + ".part"
                with open(tmp, "w") as f: json.dump(d, f, ensure_ascii=False)
                os.replace(tmp, DEMO_F)
                return self.envoyer(200, {"ok": True})
            except Exception:
                return self.envoyer(400, {"erreur": "démo illisible"})
        k = self.path.rsplit("/", 1)[-1]
        if not self.path.startswith("/api/rallumer/") or k not in OUTILS: self.vide_corps(); return self.envoyer(404, {"erreur": "introuvable"})
        dossier, port = OUTILS[k]
        subprocess.run(["bash", os.path.join(APPS, dossier, "lancer.sh")], cwd=os.path.join(APPS, dossier), capture_output=True, timeout=60)
        self.envoyer(200, {"ok": repond(port)})


if __name__ == "__main__":
    print(f"Super : http://localhost:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
