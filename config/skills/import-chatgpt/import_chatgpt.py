#!/usr/bin/env python3
"""Transforme un export ChatGPT en fichiers Markdown lisibles par Claude.

Usage : python3 import_chatgpt.py <export.zip | dossier | conversations.json> [dossier_sortie]
Sortie par défaut : ~/Documents/Brain/_archives-chatgpt/
  - conversations/AAAA-MM-JJ-titre.md   une conversation par fichier
  - INDEX.md                             1 ligne par conversation (date · titre · nb messages)
  - mes-messages.txt                     tous les messages de l'utilisateur, datés (pour repérer
                                         qui il est, ce qu'il veut, ses projets)
  - instructions-perso.txt               ses « instructions personnalisées » ChatGPT si trouvées
Ne supprime rien. Relançable : écrase seulement ses propres fichiers de sortie.
"""
import datetime as dt
import glob
import io
import json
import os
import re
import sys
import zipfile


def load_conversations(src):
    """Renvoie la liste des conversations, quel que soit le format d'entrée."""
    blobs = []
    if os.path.isdir(src):
        for p in sorted(glob.glob(os.path.join(src, "**", "conversations*.json"), recursive=True)):
            with open(p, encoding="utf-8") as f:
                blobs.append(json.load(f))
    elif zipfile.is_zipfile(src):
        with zipfile.ZipFile(src) as z:
            for name in sorted(z.namelist()):
                if re.search(r"(^|/)conversations[^/]*\.json$", name):
                    with z.open(name) as f:
                        blobs.append(json.load(io.TextIOWrapper(f, encoding="utf-8")))
    else:
        with open(src, encoding="utf-8") as f:
            blobs.append(json.load(f))
    convs = []
    for b in blobs:
        if isinstance(b, list):
            convs.extend(b)
        elif isinstance(b, dict) and isinstance(b.get("conversations"), list):
            convs.extend(b["conversations"])
        elif isinstance(b, dict) and "mapping" in b:
            convs.append(b)
    return convs


def text_of(msg):
    """Texte lisible d'un message (ignore images, fichiers, appels d'outils)."""
    c = msg.get("content") or {}
    ct = c.get("content_type")
    if ct in ("text", "multimodal_text"):
        parts = [p for p in c.get("parts") or [] if isinstance(p, str)]
        return "\n".join(parts).strip()
    if ct == "code":
        return ("```\n%s\n```" % c.get("text", "")).strip() if c.get("text") else ""
    return ""


def custom_instructions(msg):
    c = msg.get("content") or {}
    if c.get("content_type") != "user_editable_context":
        return ""
    bits = [c.get("user_profile") or "", c.get("user_instructions") or ""]
    return "\n".join(b.strip() for b in bits if b and b.strip())


def thread(conv):
    """Messages du fil affiché (du début au dernier nœud), dans l'ordre."""
    mapping = conv.get("mapping") or {}
    node = conv.get("current_node")
    if not node or node not in mapping:  # repli : nœud sans enfant le plus récent
        leaves = [k for k, v in mapping.items() if not v.get("children")]
        node = leaves[-1] if leaves else None
    out, seen = [], set()
    while node and node in mapping and node not in seen:
        seen.add(node)
        m = mapping[node].get("message")
        if m:
            out.append(m)
        node = mapping[node].get("parent")
    return list(reversed(out))


def day(ts):
    try:
        return dt.datetime.fromtimestamp(float(ts)).strftime("%Y-%m-%d")
    except (TypeError, ValueError):
        return "0000-00-00"


def slug(s, n=60):
    s = re.sub(r"[^\w\s-]", "", (s or "sans-titre").lower(), flags=re.U)
    s = re.sub(r"[\s_-]+", "-", s).strip("-")
    return (s[:n].rstrip("-")) or "sans-titre"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    src = os.path.expanduser(sys.argv[1])
    out = os.path.expanduser(sys.argv[2] if len(sys.argv) > 2 else "~/Documents/Brain/_archives-chatgpt")
    convs = load_conversations(src)
    if not convs:
        print("Aucune conversation trouvée dans %s (fichier conversations*.json attendu)." % src)
        return 1
    os.makedirs(os.path.join(out, "conversations"), exist_ok=True)
    convs.sort(key=lambda c: c.get("create_time") or 0)

    index, mine, instr, used = [], [], set(), set()
    for conv in convs:
        title = (conv.get("title") or "Sans titre").strip()
        d = day(conv.get("create_time"))
        lines, n = ["# %s" % title, "", "Conversation ChatGPT du %s." % d, ""], 0
        for m in thread(conv):
            ci = custom_instructions(m)
            if ci:
                instr.add(ci)
            role = (m.get("author") or {}).get("role")
            if role not in ("user", "assistant"):
                continue
            t = text_of(m)
            if not t:
                continue
            n += 1
            lines += ["## %s" % ("Moi" if role == "user" else "ChatGPT"), "", t, ""]
            if role == "user":
                mine.append("[%s] %s" % (d, re.sub(r"\s+", " ", t)[:600]))
        if n == 0:
            continue
        base = "%s-%s" % (d, slug(title))
        name, k = base, 2
        while name in used:
            name, k = "%s-%d" % (base, k), k + 1
        used.add(name)
        with open(os.path.join(out, "conversations", name + ".md"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        index.append("- %s · %s · %d messages · conversations/%s.md" % (d, title, n, name))

    with open(os.path.join(out, "INDEX.md"), "w", encoding="utf-8") as f:
        f.write("# Archives ChatGPT (%d conversations)\n\n" % len(index))
        f.write("\n".join(reversed(index)) + "\n")
    with open(os.path.join(out, "mes-messages.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(mine) + "\n")
    if instr:
        with open(os.path.join(out, "instructions-perso.txt"), "w", encoding="utf-8") as f:
            f.write("\n\n---\n\n".join(sorted(instr)) + "\n")

    first = index[0].split(" · ")[0][2:] if index else "?"
    last = index[-1].split(" · ")[0][2:] if index else "?"
    print("OK : %d conversations (%s → %s), %d messages de toi." % (len(index), first, last, len(mine)))
    print("Instructions perso ChatGPT : %s" % ("trouvées" if instr else "aucune"))
    print("Dossier : %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
