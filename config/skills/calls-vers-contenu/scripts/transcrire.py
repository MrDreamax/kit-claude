"""Transcrit un fichier audio ou vidéo (mp3, m4a, wav, mp4, mov...) en texte horodaté, 100 % sur ton ordinateur.

Usage : python3 transcrire.py <fichier> [dossier_de_sortie] [--langue fr] [--modele small]
Sort  : <dossier>/<nom>.txt avec une ligne par segment : [MM:SS] texte
        (pas de noms de personnes : l'outil ne sépare pas les voix)
Besoin : pip3 install faster-whisper   (le modèle se télécharge au premier lancement, quelques centaines de Mo)
Modèles : tiny (rapide, approximatif) · base · small (défaut, bon équilibre) · medium (plus précis, plus lent)
"""
import argparse, pathlib, sys

p = argparse.ArgumentParser()
p.add_argument('fichier')
p.add_argument('sortie', nargs='?', default='.')
p.add_argument('--langue', default=None, help="code langue (fr, en, es...). Vide = détection automatique")
p.add_argument('--modele', default='small')
a = p.parse_args()

src = pathlib.Path(a.fichier).expanduser()
if not src.exists():
    sys.exit(f'Fichier introuvable : {src}')
try:
    from faster_whisper import WhisperModel
except ImportError:
    sys.exit("faster-whisper n'est pas installé. Lance : pip3 install faster-whisper")

out = pathlib.Path(a.sortie).expanduser()
out.mkdir(parents=True, exist_ok=True)
dest = out / (src.stem + '.txt')

model = WhisperModel(a.modele, device='cpu', compute_type='int8')
segments, info = model.transcribe(str(src), language=a.langue, vad_filter=True)
lignes = []
for s in segments:
    t = int(s.start)
    texte = s.text.strip()
    if texte:
        lignes.append(f'[{t // 60:02d}:{t % 60:02d}] {texte}')
dest.write_text('\n'.join(lignes) + '\n', encoding='utf-8')
print(f'ok : {dest} ({len(lignes)} segments, langue {info.language})')
