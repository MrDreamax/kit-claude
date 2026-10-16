"""Résume les réponses vidIQ (outil vidiq_instagram_tiktok_outlier_search) : 1 bloc par reel Instagram.

Usage : python3 -I parse_vidiq.py <fichier_EN> EN <fichier_ES> ES <fichier_FR> FR
(seulement les marchés lancés ; stdlib seulement). Sort : créateur, vues, x médiane, abonnés, code du reel, concept, hook, style.
La partie TikTok de la réponse est ignorée."""
import json, re, sys

for path, tag in zip(sys.argv[1::2], sys.argv[2::2]):
    t = open(path, encoding="utf-8").read()
    if t.lstrip().startswith("["):  # parfois sauvé en JSON [{"type":"text","text":...}]
        t = "\n".join(x.get("text", "") for x in json.loads(t) if isinstance(x, dict))
    ig = t.split("## TikTok")[0]
    blocks = re.split(r"\n(?=\*\*@)", ig)
    for b in blocks:
        m = re.match(r"\*\*@([^*]+)\*\*", b)
        if not m:
            continue
        h = m.group(1)
        v = re.search(r"([\d.]+[KM]?) views \(([\d.]+)x their median of ([\d.]+[KM]?)\) · ([\d.]+[KM]?) followers", b)
        code = re.search(r"reel:(\S+)", b)
        concept = re.search(r"\*\*reel_concept\*\*: (.+)", b)
        hook = re.search(r"text: (.+)", b)
        style = re.search(r"style: (.+)", b)
        aud = re.search(r"culture_region: (.+)", b)
        print(f"[{tag}] @{h} | {v.group(1) if v else '?'} vues x{v.group(2) if v else '?'} | {v.group(4) if v else '?'} abo | {code.group(1) if code else '?'}")
        print(f"    C: {concept.group(1)[:230] if concept else ''}")
        print(f"    H: {hook.group(1)[:140] if hook else ''} | {style.group(1) if style else ''} | {aud.group(1)[:70] if aud else ''}")
