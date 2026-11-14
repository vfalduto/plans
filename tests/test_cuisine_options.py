"""Options « choix » de la cuisine/aménagement (Personnaliser) : Taille, Porte d'entrée, Porte du cellier, transparence
de la porte du cellier sur la coupe C. Chaque état est dessiné et marqué de son jeton (`data-si`) ; l'état d'origine
montre le même dessin qu'avant les options (valeurs figées de la tâche 5)."""
import re

from commun import modele
from pieces.cuisine import piece
from pieces.cuisine.amenagement import dessins, document, options
from tests.cuisine_anciens import FIXTURES

DOC = document.construire_document()
VUES = DOC.generer("")
ARIA = "Légende de l'appelant"
MEDIANS = ("cellier · ", "brut · ", "tableau noir · aimants", "L2 · LED")
CODE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def test_declarations():
    attendu = [("taille", "175", ["175", "180", "masquee"], "Visible sur les coupes A et C."),
               ("porte-entree", "fermee", ["fermee", "ouverte"], "Visible sur le plan. Rendus : fermée."),
               ("porte-cellier", "mi-ouverte", ["fermee", "mi-ouverte", "ouverte"],
                "Visible sur le plan. Rendus : ouverte ou fermée selon la vue."),
               ("transparence", "oui", ["non", "oui"], "Visible sur la coupe C.")]
    assert [(o.id, o.defaut, [v.code for v in o.valeurs], o.portee) for o in DOC.options] == attendu
    for o in DOC.options:
        assert o.type == "choix" and not o.filtre and re.match(r"^[a-z][a-z0-9-]*$", o.id)
        assert all(CODE.match(v.code) for v in o.valeurs)
    assert [o.nom for o in DOC.options] == ["Taille de la personne qui cuisine", "Porte d'entrée", "Porte du cellier",
                                            "Porte du cellier sur la coupe C"]
    assert DOC.options == options.OPTIONS


def test_rendue_selon_les_rendus():
    """Une valeur est « rendue » quand une image la montre. La porte du cellier : fermée sous les caméras réglées
    porte="fermee", repliée (ouverte) sous les autres (rendu.py, porte_cellier), jamais mi-ouverte ; la porte
    d'entrée : toujours fermée."""
    cellier = {"fermee" if c.reglages.get("porte") == "fermee" else "ouverte" for c in piece.CAMERAS}
    assert cellier == {"fermee", "ouverte"}
    assert {v.code for v in options.PORTE_CELLIER.valeurs if v.rendue} == cellier
    assert {v.code for v in options.PORTE_ENTREE.valeurs if v.rendue} == {"fermee"}


def test_jetons_connus():
    modele.verifier(DOC, VUES)
    tout = "".join(v.fiche + e.scene + e.fiche for v in VUES.values() for e in v.elements)
    jetons = {j for m in modele.JETON.findall(tout) for a in m for j in a.split()}
    attendus = {f"{o.id}:{v.code}" for o in DOC.options for v in o.valeurs if v.code != "masquee"}
    assert jetons == attendus


# ------------------------------------------------------------------ l'état d'origine : le dessin d'avant
def _defauts():
    return {o.id: o.defaut for o in DOC.options}


def _visible(svg, etat):
    """Ce que montre `etat` : chaque élément marqué d'un autre état retiré (avec son contenu), les marques ôtées."""
    montre = lambda attr: all(etat[j.split(":")[0]] == j.split(":")[1] for j in attr.split())
    sortie, pos, saut = [], 0, None   # saut : (nom de la balise sautée, profondeur)
    for m in re.finditer(r'<(/?)(\w+)([^>]*?)(/?)>', svg):
        nom, fermante, auto = m[2], m[1] == "/", m[4] == "/"
        if saut is None:
            sortie.append(svg[pos:m.start()])
        pos = m.end()
        if saut is not None:
            if nom == saut[0] and not auto:
                saut = (nom, saut[1] + (-1 if fermante else 1))
                if saut[1] == 0:
                    saut = None
            continue
        marque = re.search(r' data-si="([^"]*)"', m[3])
        if marque and not montre(marque[1]):
            if not auto:
                saut = (nom, 1)
            continue
        sortie.append(m[0].replace(marque[0], "") if marque else m[0])
    if saut is None:
        sortie.append(svg[pos:])
    return "".join(sortie)


def _reference(nom):
    """Le dessin de la page d'origine dans ses états par défaut (règle 1,75 m, entrée fermée, cellier mi-ouvert, coupe C
    en transparence) : ce que son CSS cachait retiré, points médians remplacés, sans aria-label ni role."""
    svg = (FIXTURES / "dessins" / f"{nom}.svg").read_text(encoding="utf-8")
    for m in MEDIANS:
        svg = svg.replace(m, m.replace(" · ", ", "))
    svg = re.sub(r'<g class="regle" data-t="180">.*?</g>(?=<g class="regle"|</svg>)', "", svg, flags=re.S)
    svg = re.sub(r'<g class="ouv">.*?</g>(?=<g class="(?:fer|mi)">)', "", svg, flags=re.S)
    svg = re.sub(r'(<g class="vt" data-vt="cellier") data-etat="mi">(.*?)<g class="fer">.*?</g></g>', r"\1>\2</g>",
                 svg, flags=re.S)
    svg = re.sub(r'(<g class="vt" data-vt="entree") data-etat="ferme">', r"\1>", svg)
    return _sans_tete(svg)


def _sans_tete(svg):
    tete, reste = svg.split(">", 1)
    tete = re.sub(r' (aria-label|role)="[^"]*"', "", tete)
    reste = re.sub(r'<rect class="zone"[^>]*/>', "", reste)
    return tete + ">" + reste


def _normal(svg):
    """Classes d'état propres à l'ancienne page (ouv, mi, fer, regle, trp, trp-lbl) et doublons d'enveloppe retirés."""
    svg = re.sub(r'<g class="(?:ouv|mi|fer)">', "<g>", svg)
    svg = re.sub(r"<g>((?:(?!<g[ >]).)*?)</g>", r"\1", svg, flags=re.S)
    return svg


def test_defaut_inchange():
    etat = _defauts()
    for nom, dessin in (("plan", dessins.plan_svg), ("coupe-a", dessins.coupe_a), ("coupe-c", dessins.coupe_c)):
        nouveau = _normal(_sans_tete(_visible(dessin(ARIA), etat)))
        assert nouveau == _normal(_reference(nom)), nom


def test_chaque_etat_dessine():
    plan, a, c = dessins.plan_svg(ARIA), dessins.coupe_a(ARIA), dessins.coupe_c(ARIA)
    for jeton in ("porte-entree:fermee", "porte-entree:ouverte", "porte-cellier:fermee", "porte-cellier:mi-ouverte",
                  "porte-cellier:ouverte"):
        assert plan.count(f'data-si="{jeton}"') == 1, jeton
    for svg in (a, c):
        assert svg.count('data-si="taille:175"') == svg.count('data-si="taille:180"') == 1
        assert 'data-si="taille:masquee"' not in svg
    assert 'data-si="transparence:non"' in c and 'data-si="transparence:oui"' in c
    assert all('data-si="transparence:oui"' in t for t in re.findall(r"<text[^>]*trp-lbl[^>]*>", c))
    # en transparence, la porte du cellier (tiretée) ; opaque, la même porte pleine
    oui = _visible(c, {**_defauts(), "transparence": "oui"})
    non = _visible(c, {**_defauts(), "transparence": "non"})
    assert "trp" in oui and "trp" not in non and oui != non


def test_css_fige_retire():
    css = dessins.CSS_DESSINS
    assert '.regle[data-t="175"]{display:inline}' not in css and ".regle{display:none}" not in css
    assert ".vt[" not in css and not re.search(r"\.(?:ouv|mi|fer)\b[^{]*\{[^}]*display:none", css)
    assert "display:none" not in css
    assert not re.search(r"\.trp-lbl[^{]*\{[^}]*display:none", css)


def test_masquee():
    """Hors modèle du socle : la coupe garde sa viewBox élargie de la règle quand la taille est masquée ; seule la
    règle disparaît (aucun `<g class="regle">` sans jeton)."""
    for svg in (dessins.coupe_a(ARIA), dessins.coupe_c(ARIA)):
        vb = re.search(r'viewBox="([^"]+)"', svg).group(1)
        assert vb == re.search(r'data-vb1="([^"]+)"', svg).group(1)
        masquee = _visible(svg, {**_defauts(), "taille": "masquee"})
        assert 'class="regle"' not in masquee and f'viewBox="{vb}"' in masquee
