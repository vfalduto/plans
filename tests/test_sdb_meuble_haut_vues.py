"""Les dessins et les cinq vues du meuble haut ; rien ne se perd de l'ancienne page sdb-meuble-haut.html (V6.4)."""
import re
from html import escape

from commun.css_dessins import css_dessins
from commun.modele import Document, Variante, verifier
from pieces.sdb.meuble_haut import dessins as D, modele as H, vues
from tests.outils import RACINE
from tests.sdb_anciennes import FIXTURES, dessin, morceaux, sans_aria, texte

M = H.M
V = vues.vues("")
VIEUX = (FIXTURES / "sdb-meuble-haut.html").read_text(encoding="utf-8")


def _scenes(v):
    return "".join(e.scene + e.fiche for e in v.elements) + v.fiche


def test_61_dessins_de_l_ancienne_page_repris():
    """Les 61 SVG de l'ancienne page : 1 iso, 9 cartes, 3 étapes, 1 éclatée, 23 faces, 6 calepinages, 1 perçage type,
    2 poses, 15 icônes."""
    assert len(re.findall(r"<svg", VIEUX)) == 61
    nouveau = "".join(_scenes(v) for v in V.values())
    compte = {"iso": nouveau.count('aria-label="Caisson haut, vue iso"'),
              "cartes": len(re.findall(r'class="vignette"', nouveau)),
              "faces": len(re.findall(r'<svg class="face"', nouveau)),
              "calepinages": len(re.findall(r'viewBox="-4 -4 ', nouveau)),
              "icones": len(re.findall(r'<svg class="ico"', _scenes(V["montage"])))}
    assert compte == {"iso": 1, "cartes": 9, "faces": 23, "calepinages": 6, "icones": 15}
    # 1 iso + 9 cartes + 3 étapes + 1 éclatée + 23 faces + 6 calepinages + 1 perçage type + 2 poses + 15 icônes = 61 ;
    # les 2 de plus sont les icônes des boutons Découpe et Montage de la fiche de Plans
    assert len(re.findall(r"<svg", nouveau)) == 61 + 2      


def test_dessins_comme_l_ancienne_page():
    assert sans_aria(D.iso_meuble("x")) == sans_aria(dessin(VIEUX, "Caisson haut"))
    for n in (8, 9, 10):
        assert D.dessin_etape(n) == dessin(VIEUX, f"Étape {n}")
    eclatee = re.findall(r'<svg[^>]*aria-label="Caisson haut".*?</svg>', VIEUX, re.S)[1]
    assert sans_aria(D.vue_eclatee("x")) == sans_aria(eclatee)
    assert D.percage_type() == dessin(VIEUX, "Perçage type")
    for rep in {p["rep"] for p in H.debit_haut()}:
        nom = next(p["nom"] for p in H.debit_haut() if p["rep"] == rep)
        assert sans_aria(D.piece_seule(rep, nom)) == sans_aria(dessin(VIEUX, nom)), rep


def test_poses_comme_l_ancienne_page_avec_un_motif_par_dessin():
    face = dessin(VIEUX, "Pose du caisson haut, de face").replace('stroke="var(--muted)" stroke-width=".3"', "")
    nouveau = D.pose_de_face().replace('style="stroke:var(--muted);stroke-width:.3"', "")
    assert re.sub(r' aria-label="[^"]*"', "", face).replace("carreau", "c") == \
        re.sub(r' aria-label="[^"]*"', "", nouveau).replace("carreau-face", "c")
    assert 'id="carreau-face"' in D.pose_de_face() and 'id="carreau-coupe"' in D.pose_en_coupe()
    assert "carreau-coupe" not in D.pose_de_face() and 'id="carreau"' not in "".join(_scenes(v) for v in V.values())


def test_cinq_vues_et_verifier():
    doc = Document("sdb", "meuble-haut", "Meuble haut", "construction", (Variante("", "Meuble haut", "V6.4", ()),),
                   vues.vues)
    verifier(doc, V)
    assert list(V) == ["plans", "decoupe", "montage", "achats", "explication"]
    try:
        vues.vues("autre")
    except ValueError:
        pass
    else:
        raise AssertionError("une seule variante")


def test_plans():
    p = V["plans"]
    assert [e.k for e in p.elements] == ["iso", "eclate", "elevation", "coupe"]
    assert [e.nom for e in p.elements] == ["Vue iso", "Vue éclatée", "Pose, de face", "Pose, en coupe"]
    assert p.outils == ("zoom", "mesure")
    for e in p.elements:
        assert e.scene.startswith('<svg data-mesure="non"') == (e.k in ("iso", "eclate"))
        assert f'aria-label="{escape(vues.alt(e.k), quote=True)}"' in e.scene
    assert "114 × 45, de 158 à 248 du sol" in p.fiche and 'href="#decoupe"' in p.fiche


def test_aucune_description_sous_les_dessins():
    for v in V.values():
        visible = texte(re.sub(r'aria-label="[^"]*"', "", _scenes(v)))
        for k in vues.ALTS:
            assert texte(vues.alt(k)) not in visible


def test_classes_ont_une_regle_et_pas_de_chasse_fixe():
    tous = [e.scene + e.fiche for v in V.values() for e in v.elements] + [v.fiche for v in V.values()]
    css = css_dessins(D.CSS_DOCUMENT, tous, ".d-sdb")
    site = (RACINE / "commun/site.css").read_text(encoding="utf-8")
    regle = lambda c, t: re.search(rf"\.{re.escape(c)}(?![\w-])", t) is not None   # noqa: E731
    classes = {c for s in tous for m in re.findall(r'class="([^"]+)"', s) for c in m.split()}
    assert {"inew", "ical", "imur", "isac", "iapp", "ihub", "fta", "ftb", "fent", "tb", "pvis", "dg", "top", "w"} <= classes
    assert sorted(c for c in classes if not regle(c, css) and not regle(c, site)) == []
    for interdit in ("JetBrains", "monospace", "var(--bas)", "var(--haut)", "var(--tile)", "var(--dg)", "uppercase"):
        assert interdit not in D.CSS_DOCUMENT
    assert "·" not in "".join(tous)                                          # pas de point médian


def test_titres_des_calepinages():
    titres = re.findall(r"<figcaption>(.*?)</figcaption>", _scenes(V["decoupe"]))
    assert titres[0] == "B1, 2000 × 38, 43 % utilisés" and len(titres) == 6 and titres[1].startswith("T1, 2500 × 500")
    assert 'aria-label="Barre 1, 2000 × 38"' in V["decoupe"].elements[0].scene


def test_decoupe_montage_achats_explication():
    d, m, a, e = (texte(_scenes(V[k])) for k in ("decoupe", "montage", "achats", "explication"))
    assert "Surfaces nettes : K 5,24 m², G 0,86 m linéaires." in d and "5,04 m" in d and "54 m," not in d
    assert "deux rouleaux de 5 m" in d and "lot de six au magasin" in d
    assert "G12, 864" in d and "·" not in d
    assert "3 étapes" in m and "Fixer le caisson haut au mur" in m and "Outils à réunir" in m and "Comment percer" in m
    assert m.count("Contrôle") == 4 and m.count("Attention") == 1 + 1      # 4 contrôles, 1 attention (+ l'intro)
    assert "179,82 €" in a and "476,64 €" in a and "Total du meuble haut" in a and "Meuble bas" in a
    assert "Matériaux possibles" in e and "Choix laissé au constructeur" in e and "179,82 €" in e


# changements de forme voulus : textes retirés ou adaptés (décisions de la spec, ou rulings du rapport)
RETIRES = (
    "3 étapes, dans l'ordre",                         # intro : « À côté » devient « Dessous », plus la légende
    "8. Caisson haut", "9. Pose du caisson haut", "10. Finitions",          # ordre de travail : les étapes elles-mêmes
    "Le résultat de l’étape",                         # note sous le dessin : légende de l'intro du Montage
    "9.1Poser le caisson haut sur deux cales",        # son lien devient une phrase
    "Une vue éclatée par sous-ensemble",              # légende des fiches : l'éclatée est dans Plans
    "Long.", "Larg.",                                  # en-têtes : « Longueur », « Largeur »
    "Le caisson haut, acheté seul",                   # section Achats : liens retirés
    "Tablette mélaminée blancheretenu",               # badge : « (retenu) »
    "Repère : origine",                               # note finale : chemins de l'ancien générateur
)


def _normalise(t):
    t = re.sub(r"^(\w+) — (.*?) · ", r"\1, \2 : ", t)
    return t.replace(" · ", ", ").replace(" → ", ", vers ")


def test_rien_ne_se_perd_de_l_ancienne_page():
    nouveau = texte(" ".join(_scenes(v) for v in V.values()))
    manque = [m for m in morceaux(VIEUX) if not m.startswith(RETIRES) and _normalise(m) not in nouveau]
    assert manque == []
    assert 'aria-label="Repère"' not in nouveau and "Repère : origine à l'angle nord-ouest" in nouveau


def test_fixation_au_mur_huit_consignes():
    m = V["montage"].elements[0].scene
    consignes = re.search(r'<h2>Fixer le caisson haut au mur</h2>.*?<ol class="pistes">(.*?)</ol>', m, re.S)[1]
    assert consignes.count("<li>") == 8 and 'href="#plans?k=elevation"' in m and 'href="#plans?k=coupe"' in m
    assert "six vis" in consignes and f"à {M.CARRELAGE}" in consignes


def test_pas_de_li_dans_les_etapes():
    """Un <li> dans une étape prendrait la pastille numérotée de .etapes li."""
    m = V["montage"].elements[0].scene
    for etape in re.findall(r"<ol class=\"etapes\".*?</ol>", m, re.S):
        assert etape.count("<li>") == 3
