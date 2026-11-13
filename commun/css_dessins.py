"""CSS des dessins : les règles dont toutes les classes apparaissent dans les dessins, préfixées par la pièce."""
import re


def css_dessins(css: str, dessins: list[str], prefixe: str) -> str:
    """Garde les règles dont toutes les classes figurent dans `dessins`, sans `@media`, sans règle sans classe ni
    règle visant `body|html|main|nav|button|table|h1-6`, et préfixe chaque sélecteur par `prefixe`. Une règle répétée
    (le CSS d'un document réunit celui de ses variantes, qui partagent leurs règles communes) n'est gardée qu'une fois,
    à sa première place."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"@media[^{]*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\}", "", css)
    classes = set()
    for s in dessins:
        for c in re.findall(r'class="([^"]+)"', s):
            classes.update(c.split())
    out = []
    for sel, decl in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        gardes = []
        for s in sel.split(","):
            cl = re.findall(r"\.([\w-]+)", s)
            if cl and all(c in classes for c in cl) and not re.search(r"\b(body|html|main|nav|button|table|h\d)\b", s):
                gardes.append(f"{prefixe} {s.strip()}")
        regle = ",".join(gardes) + "{" + decl.strip() + "}"
        if gardes and regle not in out:
            out.append(regle)
    return "\n".join(out)
