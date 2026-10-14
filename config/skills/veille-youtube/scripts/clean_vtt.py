#!/usr/bin/env python3
"""Nettoie un fichier .vtt (sous-titres YouTube auto) en texte lisible.

Les sous-titres auto-générés de YouTube utilisent un affichage "rolling" :
chaque cue répète la ligne précédente + un mot. On déduplique pour obtenir
un transcript propre, une phrase par bloc, sans timestamps ni balises.

Usage: python3 clean_vtt.py input.vtt > output.txt
"""
import re
import sys


def clean(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        raw = f.read()

    lines = raw.splitlines()
    out: list[str] = []
    for line in lines:
        # En-têtes / métadonnées WEBVTT
        if line.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")):
            continue
        # Lignes de timing  00:00:01.000 --> 00:00:03.000 ...
        if "-->" in line:
            continue
        # Numéros de cue isolés
        if re.fullmatch(r"\d+", line.strip()):
            continue
        # Balises inline <00:00:01.000><c> ... </c>
        line = re.sub(r"<[^>]+>", "", line)
        line = line.strip()
        if not line:
            continue
        # Déduplication "rolling" : on saute si identique à la dernière ligne
        if out and out[-1] == line:
            continue
        # On saute si la ligne est un préfixe de la précédente (caption partielle)
        if out and out[-1].startswith(line):
            continue
        # On saute si la précédente est un préfixe de celle-ci (on remplace)
        if out and line.startswith(out[-1]):
            out[-1] = line
            continue
        out.append(line)

    return "\n".join(out)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python3 clean_vtt.py input.vtt")
    print(clean(sys.argv[1]))
