"""Les cinq dessins du salon/aménagement (pieces/salon/amenagement/dessins.py) contre ceux de l'ancienne page
(tests/fixtures/salon/amenagement-*.svg, produits par 3d/salon/plan.py) : dans chacun des huit états des options Table,
Siège et Déco, ce que montre le nouveau dessin est ce que montrait l'ancien, aux écarts voulus près (point médian,
classes renommées, deux étiquettes recalculées)."""
import itertools
import re

import pytest

from pieces.salon.amenagement import dessins, options
from tests.outils import RACINE

FIXTURES = RACINE / "tests" / "fixtures" / "salon"

ARIA = "Légende de l'appelant"
ETATS = [dict(table=t, siege=s, deco=d) for t, s, d in
         itertools.product(("quotidien", "ouverte"), ("dyvlinge", "chilienne"), ("masquee", "affichee"))]
# classe de l'ancienne page : jeton de l'option qui la remplace
CLASSES_ETAT = {"cf": ("table", "quotidien"), "co": ("table", "ouverte"), "adyv": ("siege", "dyvlinge"),
                "achil": ("siege", "chilienne"), "dz": ("deco", "affichee")}
ORDRE = ("table", "siege", "deco")
DESSINS = {
    "plan": ("amenagement-plan-du-salon.svg", lambda: dessins.plan_svg(ARIA)),
    "coupe-a": ("amenagement-coupe-a-x-70-regard-vers-l-ouest-{}.svg", lambda: dessins.coupe_a(ARIA)),
    "coupe-b": ("amenagement-coupe-a-x-480-regard-vers-l-est-{}.svg", lambda: dessins.coupe_b(ARIA)),
    "coupe-c": ("amenagement-coupe-a-y-215-regard-vers-le-nord-{}.svg", lambda: dessins.coupe_c(ARIA)),
    "coupe-d": ("amenagement-coupe-a-y-300-regard-vers-le-sud-{}.svg", lambda: dessins.coupe_d(ARIA)),
}
# écarts voulus : texte de l'ancienne page -> texte de la nouvelle
ECARTS = (("Enfilade 240 × 60 · h 80", "Enfilade 240 × 60, h 80"), ("④ Desserte · platine vinyle", "④ Desserte, platine vinyle"),
          ("12 couverts · 4 allonges", "12 couverts, 4 allonges"), ("② 4 étagères", "② 5 étagères"),
          # nombres du modèle : « 215.0 » sans décimale inutile, centre d'un texte tourné arrondi comme les autres
          ('y1="215.0"', 'y1="215"'), ('y2="215.0"', 'y2="215"'), ("rotate(-90 568 174.75)", "rotate(-90 568 174.8)"))
TAG = re.compile(r"<(/?)(\w+)([^>]*?)(/?)>")


def _etat(attr):
    return [tuple(j.split(":")) for j in attr.split()]


def _converti(svg):
    """L'ancien dessin à la manière du nouveau : les classes d'état (cf co adyv achil dz) deviennent un `data-si` en
    fin de balise, dans l'ordre table, siège, déco ; `cadre`, `tapis` et `lbl muted` prennent leurs nouveaux noms."""
    for ancien, nouveau in ECARTS:
        svg = svg.replace(ancien, nouveau)
    # cotes à la virgule : « 254.5 » devient « 254,5 » dans les textes du dessin (pas dans les attributs)
    svg = re.sub(r">([^<>]*)<", lambda m: ">" + re.sub(r"(\d)\.(\d)", r"\1,\2", m[1]) + "<", svg)

    def balise(m):
        ferme, nom, attrs, auto = m.groups()
        if ferme or 'class="' not in attrs:
            return m[0]
        classe = re.search(r'class="([^"]*)"', attrs)
        mots = classe[1].split()
        etat = [CLASSES_ETAT[c] for c in mots if c in CLASSES_ETAT]
        # chaque `c<config>` posé par cfg_cls sur un bloc a son équivalent dans `cf` et `co`
        mots = ["cadrep" if w == "cadre" else "tapisd" if w == "tapis" else w for w in mots if w not in CLASSES_ETAT]
        if mots == ["lbl", "muted"]:
            mots = ["roomt"]
        attrs = attrs.replace(classe[0], f'class="{" ".join(mots)}"' if mots else "").replace("  ", " ")
        if etat:
            si = " ".join(f"{o}:{v}" for o, v in sorted(etat, key=lambda e: ORDRE.index(e[0])))
            attrs = attrs.rstrip() + f' data-si="{si}"'
        return f"<{nom}{' ' if attrs and not attrs.startswith(' ') else ''}{attrs}{auto}>"
    return TAG.sub(balise, svg)


def _montre(attr, etat):
    return all(etat[o] == v for o, v in _etat(attr))


def _vu(svg, etat):
    """Ce que montre `etat` : chaque élément marqué d'un autre état retiré avec son contenu, les marques ôtées, les
    groupes sans attribut défaits ; sans aria-label ni role ni zones du plan."""
    sortie, pos, saut = [], 0, None
    for m in TAG.finditer(svg):
        nom, ferme, auto = m[2], m[1] == "/", m[4] == "/"
        if saut is None:
            sortie.append(svg[pos:m.start()])
        pos = m.end()
        if saut is not None:
            if nom == saut[0] and not auto:
                saut = (nom, saut[1] + (-1 if ferme else 1))
                if saut[1] == 0:
                    saut = None
            continue
        marque = re.search(r' data-si="([^"]*)"', m[3])
        if marque and not _montre(marque[1], etat):
            if not auto:
                saut = (nom, 1)
            continue
        sortie.append(m[0].replace(marque[0], "") if marque else m[0])
    if saut is None:
        sortie.append(svg[pos:])
    texte = "".join(sortie)
    texte = re.sub(r'<rect class="zone"[^>]*/>', "", texte)
    texte = re.sub(r' aria-label="[^"]*"| role="[^"]*"', "", texte, count=2)
    return re.sub(r"</?g>", "", texte)


@pytest.mark.parametrize("etat", ETATS, ids=lambda e: "-".join(e.values()))
@pytest.mark.parametrize("nom", DESSINS)
def test_dessin_dans_chaque_etat(nom, etat):
    fichier, dessiner = DESSINS[nom]
    config = {"quotidien": "f", "ouverte": "o"}[etat["table"]]
    ancien = (FIXTURES / fichier.format(config)).read_text(encoding="utf-8")
    attendu, montre = _vu(_converti(ancien), etat), _vu(dessiner(), etat)
    # les étiquettes des volumes (« ⑦ », contenus) de l'ancienne page ne suivaient pas leur volume : celle d'un siège
    # caché restait affichée. Ici chacune suit son volume : jamais une étiquette de plus, une de moins seulement pour ⑦.
    etiquette = re.compile(r'<text class="lbl[bc]"[^>]*>[^<]*</text>')
    vus, anciens = etiquette.findall(montre), etiquette.findall(attendu)
    assert etiquette.sub("", montre) == etiquette.sub("", attendu)
    assert [e for e in vus if e not in anciens] == []
    assert {re.sub(r"<[^>]+>", "", e) for e in anciens if e not in vus} <= {"⑦"}


def test_plan_sans_classe_d_etat():
    for nom, (_, dessiner) in DESSINS.items():
        svg = dessiner()
        for ancienne in ("cf", "co", "adyv", "achil", "dz"):
            assert not re.search(rf'class="[^"]*\b{ancienne}\b', svg), (nom, ancienne)
        assert "·" not in svg, nom


def test_jetons_des_dessins_sont_ceux_des_options():
    connus = {f"{o.id}:{v.code}" for o in options.OPTIONS for v in o.valeurs}
    for _, dessiner in DESSINS.values():
        for attr in re.findall(r' data-si="([^"]*)"', dessiner()):
            assert set(attr.split()) <= connus
            assert len({j.split(":")[0] for j in attr.split()}) == len(attr.split())


def test_zones_du_plan_et_role():
    svg = dessins.plan_svg(ARIA, '<rect class="zone" x="0" y="0" width="1" height="1"/>')
    assert svg.endswith('<rect class="zone" x="0" y="0" width="1" height="1"/></svg>')
    assert ' role="group"' in svg.split(">", 1)[0] and ' role="img"' in dessins.plan_svg(ARIA).split(">", 1)[0]


def test_voisines_ont_la_classe_des_calques():
    """Les noms des pièces voisines sont `roomt` : le calque « Pièces voisines » les cache avec leurs fonds."""
    svg = dessins.plan_svg(ARIA)
    for nom in ("Cellier", "WC", "Couloir", "Pièce 1", "Chambre"):
        assert re.search(rf'<text class="roomt"[^>]*>{nom}</text>', svg), nom


def test_cotes_a_la_virgule():
    for nom, (_, dessiner) in DESSINS.items():
        assert not re.search(r">[^<>]*\d\.\d[^<>]*<", dessiner()), nom
    assert ">254,5<" in dessins.coupe_a(ARIA) and "baie 204,5" in dessins.plan_svg(ARIA)
    assert "dessous à 231,7" in dessins.plan_svg(ARIA)


def test_cotes_formatees():
    """« Coupe à y 215.0 » et « 240,0 » : les nombres du modèle sont écrits sans décimale inutile."""
    assert 'aria-label="Coupe à y 215' in dessins.coupe_c("Coupe à y 215")
    for nom, (_, dessiner) in DESSINS.items():
        assert not re.search(r">[^<]*\d\.0\b[^<]*<", dessiner()), nom
