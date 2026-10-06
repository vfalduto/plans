# Fige la proposition 9 V2, variante A, table carrée, dans les versions comparables de cuisine-v11.html.
#
#   python3 3d/v11/figer_p9.py
#
# Copie le contenu de cuisine-plan.html (plan et coupes de la variante A seulement) dans
# figees/P9 V2 A.html : sélecteurs et autres variantes retirés, CSS limité à un conteneur .p9,
# identifiants SVG suffixés pour ne pas entrer en conflit avec la version en cours.

import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(ROOT, "cuisine-plan.html")
OUT = os.path.join(HERE, "figees", "P9 V2 A.html")
SUFFIXE = "-p9"


def sans_div(html, marqueur):
    """Retire chaque <div …> dont la balise ouvrante contient marqueur, avec tout son contenu."""
    while True:
        i = html.find(marqueur)
        if i < 0:
            return html
        debut = html.rfind("<div", 0, i)
        n, k = 0, debut
        for m in re.finditer(r"<div\b|</div>", html[debut:]):
            n += 1 if m.group(0) == "<div" else -1
            if n == 0:
                k = debut + m.end()
                break
        html = html[:debut] + html[k:]


def selecteur(sel):
    sel = sel.strip()
    if not sel or sel.startswith(".ph"):
        return None
    m = re.match(r':root\[data-tbl="(\w+)"\](.*)', sel)
    if m:
        return ".p9" + m.group(2) if m.group(1) == "sq" else None
    for theme in (':root:not([data-theme="light"])', ':root[data-theme="dark"]'):
        if sel.startswith(theme):
            return theme + " .p9" + sel[len(theme):]
    if sel.startswith(":root"):
        return ".p9" + sel[5:]
    if sel in ("html", "body"):
        return ".p9"
    return ".p9 " + sel


def portee(css):
    """Préfixe chaque règle par .p9 (récursif dans les @media)."""
    out, i = [], 0
    while i < len(css):
        j = css.find("{", i)
        if j < 0:
            break
        tete = css[i:j].strip()
        n, k = 1, j + 1
        while n:
            n += {"{": 1, "}": -1}.get(css[k], 0)
            k += 1
        corps = css[j + 1:k - 1]
        if tete.startswith("@"):
            out.append(f"{tete}{{{portee(corps)}}}")
        else:
            sels = [s for s in (selecteur(x) for x in tete.split(",")) if s]
            if sels:
                out.append(f"{','.join(sels)}{{{corps}}}")
        i = k
    return "\n".join(out)


src = open(SRC, encoding="utf-8").read()
css = re.search(r"<style>(.*?)</style>", src, re.S).group(1)
css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)  # commentaires retirés : ils colleraient au sélecteur suivant
corps = src[src.index('<div class="wrap">') + len('<div class="wrap">'):src.index("<script>")]
corps = corps[:corps.rindex("</div>")]  # fin de .wrap
for marqueur in ('class="switch"', 'class="opts"', 'data-panel="a2"', 'data-panel="c"', 'data-panel="d"'):
    corps = sans_div(corps, marqueur)
# table carrée : les éléments .tbl-rd / .tbl-bq sont masqués par le CSS (:root[data-tbl="sq"] → .p9)
corps = re.sub(r"<div class=\"kicker\">.*?</div>",
               '<div class="kicker">Proposition 9 V2 · V3.6 · variante A · table carrée 70 × 70 · figée le 06/10/2026</div>',
               corps, count=1, flags=re.S)
for ident in set(re.findall(r'id="([^"]+)"', corps)):
    corps = corps.replace(f'id="{ident}"', f'id="{ident}{SUFFIXE}"').replace(f"url(#{ident})", f"url(#{ident}{SUFFIXE})")
    corps = corps.replace(f'href="#{ident}"', f'href="#{ident}{SUFFIXE}"')

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(f"<style>{portee(css)}</style>\n<div class=\"p9\">{corps}</div>\n")
print(OUT)
