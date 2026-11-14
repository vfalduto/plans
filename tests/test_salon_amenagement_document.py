"""Document du salon/aménagement (pieces/salon/amenagement/) : options, meubles touchables confrontés à leurs blocs,
textes de l'ancienne page (passages, tableaux, listes), vues, changements, versions figées, CSS des dessins, rendu et
bascule (site.py, redirections, ancien fichier supprimé)."""
import html
import py_compile
import re
from collections import Counter

import pytest

from commun import modele
from commun.construction import _dessins
from commun.css_dessins import css_dessins
from commun.journal import entrees
from commun.modele import Document, Piece, Site
from pieces.salon import piece
from pieces.salon.amenagement import dessins, document, explication, options, textes, vues, zones
from tests.outils import RACINE, charger_site

FIXTURES = RACINE / "tests" / "fixtures" / "salon"
DOC = document.DOCUMENT
VUES = DOC.generer("")
PLAN = VUES["plan"].elements[0]
S_EXPLICATION = VUES["explication"].elements[0].scene if VUES["explication"].elements else ""


def _texte(fragment):
    """Texte d'un fragment, balises ôtées sans espace (un lien dans une phrase ne la coupe pas)."""
    fragment = re.sub(r">\s+<", "><", fragment)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", fragment))).strip()


def _chiffres(t):
    """Décimales à la virgule ou au point, point médian et tirets de liaison : mêmes mots."""
    t = re.sub(r"(\d),(\d)", r"\1.\2", t.replace(" · ", ", ")).replace("  ", " ")
    return re.sub(r"(\d)\.0\b", r"\1", t)   # « 240,0 » : décimale inutile corrigée


@pytest.fixture(scope="module")
def ancienne_page():
    """La page salon-v4.html de la V4.26, figée à la bascule (ce que produisait 3d/salon/plan.py)."""
    return (FIXTURES / "amenagement-ancienne-page.html").read_text(encoding="utf-8")


# ------------------------------------------------------------------ options
def test_options_declarees():
    attendu = [("table", "Table", "quotidien", ["quotidien", "ouverte"]),
               ("siege", "Siège", "dyvlinge", ["dyvlinge", "chilienne"]),
               ("deco", "Décoration", "masquee", ["masquee", "affichee"]),
               ("bois", "Bois des meubles", "chene", ["chene", "noyer"])]
    assert [(o.id, o.nom, o.defaut, [v.code for v in o.valeurs]) for o in DOC.options] == attendu
    assert all(o.type == "choix" and not o.filtre for o in DOC.options)
    assert DOC.options == options.OPTIONS
    # les noms des valeurs de la table sont ceux du modèle : quotidien et ouverte, avec leur nombre de couverts
    assert [v.nom for v in options.TABLE.valeurs] == ["Au quotidien, 4 couverts", "Ouverte, 12 couverts"]
    assert [document.CONFIGS[c]["nom"] for c in "fo"] == ["quotidien", "ouverte"]
    assert [document.CONFIGS[c]["chaises"] for c in "fo"] == [4, 12]
    assert [v.code for v in options.BOIS.valeurs if v.rendue] == ["chene", "noyer"]
    assert [v.code for v in options.TABLE.valeurs if v.rendue] == ["quotidien"]


def test_jetons_connus_et_tous_poses():
    modele.verifier(DOC, VUES)
    tout = "".join(v.fiche + e.scene + e.fiche for v in VUES.values() for e in v.elements)
    jetons = {j for m in modele.JETON.findall(tout) for a in m for j in a.split()}
    # « masquee » n'a rien à dessiner : la déco masquée est l'absence de déco
    assert jetons == {f"{o.id}:{v.code}" for o in DOC.options for v in o.valeurs if v.code != "masquee"}


def test_marque_bloc():
    from pieces.salon.piece import Bloc
    b = Bloc("table", "x", 0, 1, 0, 1, 0, 1, config="o", deco=True, assise="chil")
    assert options.marque_bloc(b) == ' data-si="table:ouverte siege:chilienne deco:affichee"'
    assert options.marque_bloc(Bloc("mur", "m", 0, 1, 0, 1, 0, 1)) == ""


# ------------------------------------------------------------------ meubles du plan
def test_zones_confrontees_aux_blocs():
    """Chaque zone est l'union des blocs de son meuble, calculée ici bloc par bloc et non par le motif de zones.py."""
    def union(pred):
        bs = [b for b in document.MEUBLES + document.ENVELOPPE if pred(b.nom)]
        assert bs
        return (min(b.x0 for b in bs), min(b.y0 for b in bs), max(b.x1 for b in bs), max(b.y1 for b in bs))

    zs = {(z.id, z.si): z for z in zones.zones()}
    attendu = {
        ("enfilade", ""): union(lambda n: n.startswith("enfilade_")),
        ("canape", ""): union(lambda n: n.startswith("canape_")),
        ("desserte", ""): union(lambda n: n.startswith("desserte_") or n.startswith("vinyles_")),
        ("meuble-bas", ""): union(lambda n: n.startswith("console_")),
        ("clim", ""): union(lambda n: n == "clim"),
        ("projecteur", ""): union(lambda n: n == "projecteur"),
        ("table", "table:quotidien"): union(lambda n: n.startswith(("table_plateau_f", "table_pied_f"))),
        ("table", "table:ouverte"): union(lambda n: n.startswith(("table_plateau_o", "table_pied_o"))),
        ("chaises", "table:quotidien"): union(lambda n: n.startswith("chaise_f_")),
        ("chaises", "table:ouverte"): union(lambda n: n.startswith("chaise_o_")),
        ("table-basse", "table:quotidien"): union(lambda n: n.startswith("table_basse_f")),
        ("table-basse", "table:ouverte"): union(lambda n: n.startswith("table_basse_o")),
        ("siege", "table:quotidien siege:dyvlinge"): union(lambda n: n.startswith("dyvlinge_f_")),
        ("siege", "table:ouverte siege:dyvlinge"): union(lambda n: n.startswith("dyvlinge_o_")),
        ("siege", "table:quotidien siege:chilienne"): union(lambda n: n in ("chilienne_toile", "chilienne_dos")),
        ("siege", "table:ouverte siege:chilienne"): union(lambda n: n == "chilienne_pliee"),
    }
    for cle, emprise in attendu.items():
        assert zs[cle].emprise == emprise, cle
    # les étagères : la moitié ouest de l'emprise des montants et des tablettes, cotes de l'emprise entière
    x0, y0, x1, y1 = union(lambda n: re.fullmatch(r"(montant|etagere)_\d+", n) is not None)
    assert zs[("etageres", "")].emprise == (x0, y0, x0 + (x1 - x0) / 2, y1)
    # l'écran : une bande de 6 contre le mur sud, cotes de l'image
    e = zs[("ecran", "")]
    assert e.emprise[3] == piece.P and e.emprise[3] - e.emprise[1] == 6
    assert e.cotes == "image 200 × 112, bas à 80"


def test_cotes_des_fiches_calculees():
    zs = {(z.id, z.si): z for z in zones.zones()}
    assert zs[("enfilade", "")].cotes == "240 × 60, h 80"
    assert zs[("canape", "")].cotes == "198 × 99, h 73, dessous à 10"
    assert zs[("desserte", "")].cotes == "129 × 45, h 82"
    assert zs[("table", "table:quotidien")].cotes == "100 × 100, h 75"
    assert zs[("table", "table:ouverte")].cotes == "280 × 100, h 75"
    assert zs[("meuble-bas", "")].cotes == "160 × 35, h 55"


def test_ids_stables_et_boutons_de_fiche():
    zs = zones.zones()
    ids = [z.id for z in zs]
    assert list(dict.fromkeys(ids)) == ["enfilade", "etageres", "canape", "desserte", "chaises", "table", "table-basse",
                                        "siege", "meuble-bas", "ecran", "projecteur", "clim"]
    coupes = {e.k for e in VUES["coupes"].elements}
    coins = {e.k for e in VUES["iso"].elements if e.actif}
    for z in zs:
        assert z.coupe in coupes and z.iso in coins, z.id
        assert z.texte and "·" not in z.texte
    assert len(re.findall(r'<rect class="zone"', PLAN.scene)) == len(zs)
    for k in (z.id for z in zs):
        assert f'data-meuble="{k}"' in PLAN.scene
    assert k not in {e.k for e in VUES["plan"].elements}


def test_cartes_principe_montrent_un_meuble_du_plan():
    ids = {z.id for z in zones.zones()}
    cartes = explication.cartes()
    assert [c.titre for c in cartes][:3] == ["① Enfilade", "② Étagères sur montants", "③ Canapé"]
    assert {c.meuble for c in cartes if c.meuble} <= ids
    assert [c.meuble for c in cartes if c.titre in ("Dégagements", "Déco", "Rideau", "Suspension")] == [""] * 4


# ------------------------------------------------------------------ textes de l'ancienne page
def test_paragraphe_sous_le_plan_rien_ne_se_perd(ancienne_page):
    """Chaque mot du paragraphe de l'ancienne page est dans les passages, aux écarts voulus près (textes.py)."""
    cap = re.search(r'<p class="cap">(.*?)</p>', ancienne_page, re.S)[1]
    brut = lambda t: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t)))   # noqa: E731
    mots = lambda t: Counter(re.findall(r"[\w'’,.→×≈/-]+", _chiffres(brut(t)).lower()))   # noqa: E731
    ancien, nouveau = mots(cap), mots(textes.texte_alternatif_plan())
    perdus = ancien - nouveau
    # « bouton » (×2), « barre du haut » : les boutons n'existent plus ; « 25 » : 26 ; « 8.8 » etc. : même nombre écrit
    # à la française (« 8,8 » devient « 8.8 » dans _chiffres des deux côtés, donc absent d'ici sauf mot isolé)
    assert {m for m in perdus if re.search(r"[a-zà-ÿ]", m)} <= {"bouton", "barre", "haut", "dans", "la", "d'", "table",
                                                              "ronde", "ouverte"}
    assert perdus["bouton"] == 2 and "25" in perdus
    assert "26" in (nouveau - ancien)
    # les deux liens produits de l'ancien paragraphe (UGGLERUM, DYVLINGE) sont dans les passages
    assert re.findall(r'<a href="(https://[^"]+)"', cap) == re.findall(
        r'<a href="(https://[^"]+)"', "".join(c for _, _, c in textes.PASSAGES))[:2]
    assert textes.texte_alternatif_plan().startswith("Échelle : 1 unité = 1 cm ; ouest à gauche, nord en haut.")
    assert PLAN.scene.count('aria-label="Échelle : 1 unité') == 1


def test_tableaux_et_listes_de_l_ancienne_page(ancienne_page):
    def sections(h2):
        m = re.search(rf"<h2[^>]*>{h2}</h2>(.*?)(?=<h2|<section|<p class=\"note\")", ancienne_page, re.S)
        return _chiffres(_texte(m[1]))

    nouveau = _chiffres(_texte(S_EXPLICATION))
    for h2 in ("Matériaux", "Pistes déco", "Rangements", "Tables qui se replient", "Meubles à fabriquer",
               "Points à vérifier"):
        a = sections(h2)
        # le début de la section (jusqu'à la première note) se retrouve tel quel
        for morceau in re.split(r"(?<=\.)\s", a):
            if len(morceau) > 25 and "Source" not in morceau:
                assert morceau in nouveau, (h2, morceau)


def test_chapo_et_repere(ancienne_page):
    pitch = re.search(r'<p class="pitch">(.*?)</p>', ancienne_page, re.S)[1]
    assert explication.CHAPO == html.unescape(pitch)
    assert explication.CHAPO in html.unescape(S_EXPLICATION)
    assert "3d/salon" not in S_EXPLICATION and "just salon" not in S_EXPLICATION
    assert "Rendus 3D sur demande" in S_EXPLICATION


def test_sections_de_l_explication():
    titres = re.findall(r"<h2>([^<]*)</h2>", S_EXPLICATION)
    assert titres == ["Principe", "Matériaux", "Pistes déco", "Rangements", "Tables qui se replient",
                      "Meubles à fabriquer", "Points à vérifier"]
    assert S_EXPLICATION.count('<div class="defile">') == 2   # rangements, tables qui se replient
    assert 'href="../etageres/"' in S_EXPLICATION and 'href="../enfilade/"' in S_EXPLICATION
    assert "salon-etageres.html" not in S_EXPLICATION and "salon-enfilade.html" not in S_EXPLICATION
    assert "<input" not in S_EXPLICATION and "Copier" not in S_EXPLICATION
    assert len(re.findall(r'href="https://', S_EXPLICATION)) >= 13


def test_sans_point_median_ni_chasse_fixe():
    for cle, vue in VUES.items():
        for t in (vue.fiche, *(x for e in vue.elements for x in (e.scene, e.fiche))):
            assert "·" not in t, cle
    assert "·" not in dessins.CSS_DESSINS and "mono" not in dessins.CSS_DESSINS.lower()
    assert "·" not in "".join(c.texte for c in DOC.variantes[0].changements)


def test_formats_corriges():
    t = textes.texte_alternatif_plan() + "".join(textes.alt_coupe_a() + textes.alt_coupe_b() + textes.alt_coupe_c())
    assert "215.0" not in t and "(303.5" not in t and "1.8 déduits" not in S_EXPLICATION
    assert "centrée en (303,5, 215)" in t and "panneaux de 1,8 déduits" in S_EXPLICATION
    assert "26 de plus que le canapé" in t and "25 de plus" not in t
    assert "② 5 étagères suspendues" in dessins.plan_svg("x")


# ------------------------------------------------------------------ vues
def test_vues_et_elements():
    assert list(VUES) == ["plan", "coupes", "iso", "camera", "explication"]
    assert [e.k for e in VUES["coupes"].elements] == ["A", "B", "C", "D"]
    assert [e.titre for e in VUES["coupes"].elements] == ["Coupe A-A : mur ouest", "Coupe B-B : baie et desserte",
                                                          "Coupe C-C : à travers la table", "Coupe D-D : mur sud, écran"]
    assert {e.k: e.actif for e in VUES["iso"].elements} == {"no": True, "ne": False, "so": False, "se": True}
    assert VUES["camera"].elements == []
    assert VUES["explication"].elements


def test_coupes_alt_et_traits():
    for e, alt in zip(VUES["coupes"].elements, (textes.alt_coupe_a(), textes.alt_coupe_b(), textes.alt_coupe_c(),
                                                textes.alt_coupe_d())):
        assert f'aria-label="{html.escape(alt, quote=True)}"' in e.scene.split(">", 1)[0]
    traits = {t["data-k"]: t for t in __import__("tests.outils", fromlist=["balises"]).balises(
        VUES["coupes"].fiche, "line", classe="sec")}
    assert list(traits) == ["A", "B", "C", "D"]
    assert vues.TRAITS["A"] == ((70, 0), (70, 367)) and vues.TRAITS["D"] == ((0, 300), (547, 300))
    assert vues.TRAITS["C"] == ((0, 215), (547, 215))


def test_iso_une_image_par_bois():
    for k, nom in (("se", "iso_se"), ("no", "iso_no")):
        (e,) = [x for x in VUES["iso"].elements if x.k == k]
        assert f'src="rendus/{nom}.jpg"' in e.scene and f'src="rendus/{nom}-noyer.jpg"' in e.scene
        assert 'data-si="bois:chene"' in e.scene and 'data-si="bois:noyer"' in e.scene
        assert "modèle V4." in e.scene
        assert "pas encore rendu" not in e.scene
    for nom in ("iso_se", "iso_se-noyer", "iso_no", "iso_no-noyer"):
        assert (RACINE / "site/salon/amenagement/rendus" / f"{nom}.jpg").exists(), nom


def test_images_rendues():
    """Les quatre images (iso sud-est et nord-ouest, chêne et noyer) existent, en JPEG : refaites par `just rendu`
    (14/11/2026, scène V4.26) ; leur empreinte de rendu est celle du cache."""
    for nom in ("iso_se", "iso_se-noyer", "iso_no", "iso_no-noyer"):
        octets = (RACINE / "site/salon/amenagement/rendus" / f"{nom}.jpg").read_bytes()
        assert octets[:3] == b"\xff\xd8\xff" and len(octets) > 50_000, nom


# ------------------------------------------------------------------ document
def test_document():
    assert (DOC.piece, DOC.id, DOC.nom, DOC.type) == ("salon", "amenagement", "Aménagement", "amenagement")
    (v,) = DOC.variantes
    assert (v.id, v.nom, v.version) == ("", "Principale", "V4.26")
    assert DOC.css == dessins.CSS_DESSINS
    assert document.DOCUMENT is DOC


def test_changements_et_journal():
    (v,) = DOC.variantes
    assert len(v.changements) == 28 and v.changements[0].version == "V4.26" and v.changements[-1].version == "V4.0"
    for c, (version, date, texte) in zip(v.changements, document.CHANGEMENTS, strict=True):
        assert (c.version, c.date, c.texte) == (version, date, texte.replace(" · ", ", "))
    site = Site((Piece("salon", "Salon", (DOC,)),))
    lignes = [e for e in entrees(site) if (e.piece, e.document) == ("Salon", "Aménagement")]
    assert len(lignes) == 28 and all(e.variante is None for e in lignes)


def test_figees():
    (v,) = DOC.variantes
    assert v.figees == document.FIGEES_ANCIENNES == (("V3.1", "archives/salon-amenagement-v3.1.html"),
                                                      ("V2.1", "archives/salon-amenagement-v2.html"),
                                                      ("V1", "archives/salon-amenagement-v1.html"))
    for _, chemin in v.figees:
        assert (RACINE / "site" / chemin).exists(), chemin


def test_classes_des_dessins_ont_une_regle():
    """Chaque classe des dessins a une règle dans dessins.css (filtré comme à la construction) ou site.css, hors les
    classes sans style : `zone` et `sec` (traits de coupe) ont la leur dans site.css."""
    css = css_dessins(DOC.css, _dessins(VUES), ".d-salon")
    site_css = (RACINE / "commun/site.css").read_text(encoding="utf-8")

    def regle(c, feuille):
        return re.search(rf"\.{re.escape(c)}(?![\w-])", feuille) is not None

    for vue in ("plan", "coupes"):
        for e in VUES[vue].elements:
            classes = {c for m in re.findall(r'class="([^"]+)"', e.scene) for c in m.split()}
            assert classes, (vue, e.k)
            assert sorted(c for c in classes if not regle(c, css) and not regle(c, site_css)) == [], (vue, e.k)


def test_classes_de_la_page_sans_collision():
    """`cadre` et `tapis` sont des classes de la page (site.css) : les dessins n'emploient pas ces noms, dont les règles
    de page s'appliqueraient aux rectangles."""
    for vue in ("plan", "coupes"):
        for e in VUES[vue].elements:
            classes = {c for m in re.findall(r'class="([^"]+)"', e.scene) for c in m.split()}
            assert not classes & {"cadre", "tapis", "rendu", "scene", "element", "fiche"}, (vue, e.k)


# ------------------------------------------------------------------ rendu
RENDU = RACINE / "pieces/salon/amenagement/rendu.py"


def test_rendu_compile_et_ne_lit_que_les_nouveaux_modules():
    py_compile.compile(str(RENDU), doraise=True, cfile=str(RACINE / "cache" / "rendu-salon.pyc"))
    t = RENDU.read_text(encoding="utf-8")
    for interdit in ("import modele", "import commun", "import etageres", "import rendu as R", "/Applications/Blender.app",
                     "dirname(dirname(HERE))", "HERE"):
        assert interdit not in t, interdit
    for attendu in ("pieces.salon import piece", "pieces.salon.amenagement import document", "pieces.salon.etageres",
                    "pieces.salon.meubles", "SALON_ESSENCE", "SALON_APERCU", "SALON_SORTIE"):
        assert attendu in t, attendu


# vues de 3d/salon/rendu.py (V4.26), relevées à la bascule : (ortho, position, cible, motif des murs cachés)
COUPES_SE = ("^(mur__(mur_sud|mur_est_n|mur_est_s|couloir)|sol__couloir|linteau__linteau_baie|poutre__|plafond__|clim__"
             "|plinthe__(sud|est_)|baie__|rideau__|tringle__)")
COUPES_NO = ("^(mur__(mur_nord|mur_nord_decroche|mur_ouest_n|mur_ouest_s|couloir)|sol__couloir|papier_peint__"
             "|linteau__linteau_passage|cadre__cadre_passage|cadre_mur__|plafond__|plinthe__(nord|ouest_n))")


def test_rendu_vues_sont_les_cameras_de_la_piece():
    """Les deux caméras de la pièce sont les vues de l'ancien script, avec leurs murs cachés."""
    cams = {c.id: c for c in piece.CAMERAS}
    assert list(cams) == ["iso_se", "iso_no"]
    attendu = {"iso_se": (8.2, (912, 779, 600), (272, 179, 70), COUPES_SE),
               "iso_no": (8.2, (-368, -421, 600), (272, 179, 70), COUPES_NO)}
    for k, c in cams.items():
        assert (c.ortho, tuple(c.loc), tuple(c.cible), c.reglages["coupes"]) == attendu[k], k


def test_cache_declare():
    c = document.CACHE_RENDU
    assert c.variantes == {"": ("pieces.salon.piece", "pieces.salon.etageres.document",
                                "pieces.salon.amenagement.document")}
    assert c.code == ("pieces/salon/amenagement/rendu.py", "pieces/salon/etageres/volumes.py", "pieces/salon/meubles.py",
                      "3d/rendu.py")
    assert (c.script, c.png) == ("pieces/salon/amenagement/rendu.py", "salon-{camera}.png")
    for chemin in document.CACHE_RENDU.code:
        assert (RACINE / chemin).is_file(), chemin


def test_empreinte_des_rendus():
    from tests.outils import verifier_empreinte
    verifier_empreinte("pieces.salon.piece", "pieces.salon.etageres.document", "pieces.salon.amenagement.document")


def test_recettes_du_justfile():
    j = (RACINE / "justfile").read_text(encoding="utf-8")
    for recette in ("rendu page echantillons=", "rendu-apercu page *vues"):
        assert f"\n{recette}" in j, recette
    assert "\nsalon-amenagement" not in j   # recettes génériques : `just rendu salon/amenagement`, `just site …`
    # le bois rendu (un Blender par essence) est déclaré par le document, pas par une recette
    from pieces.salon.amenagement import options
    assert document.CACHE_RENDU.reglages == "pieces.salon.amenagement.options:essences_rendues"
    assert options.essences_rendues() == [("SALON_ESSENCE", "chene", ""), ("SALON_ESSENCE", "noyer", "-noyer")]


# ------------------------------------------------------------------ bascule
def _redirections():
    return {r.ancienne: r for r in charger_site().REDIRECTIONS}


def _traduire(r, ancre):
    if ancre in r.pages:
        return r.pages[ancre], ""
    if ancre in r.ancres:
        return r.cible, r.ancres[ancre]
    for motif, gabarit in r.motifs:
        m = re.search(motif, ancre)
        if m:
            return r.cible, re.sub(r"\{(\d+)\}", lambda g: (m.group(int(g[1])) or "").upper(), gabarit)
    return r.cible, ""


def test_document_dans_site_et_ancienne_page_supprimee():
    (salon,) = [p for p in charger_site().SITE.pieces if p.id == "salon"]
    assert [d.id for d in salon.documents] == ["amenagement", "etageres", "enfilade"]
    assert salon.documents[0] is DOC and isinstance(DOC, Document)
    assert not (RACINE / "salon-v4.html").exists() and not (RACINE / "salon-v4-3d").exists()


@pytest.mark.parametrize("ancre,attendu", [
    ("plan", ("salon/amenagement/", "plan")),
    ("coupe-a-a-mur-ouest", ("salon/amenagement/", "coupes?k=A")),
    ("coupe-b-b-baie-et-desserte", ("salon/amenagement/", "coupes?k=B")),
    ("coupe-c-c-a-travers-la-table", ("salon/amenagement/", "coupes?k=C")),
    ("coupe-d-d-mur-sud-ecran", ("salon/amenagement/", "coupes?k=D")),
    ("rendu-3d", ("salon/amenagement/", "iso")),
    ("materiaux", ("salon/amenagement/", "explication")),
    ("pistes-deco", ("salon/amenagement/", "explication")),
    ("rangements", ("salon/amenagement/", "explication")),
    ("tables-qui-se-replient", ("salon/amenagement/", "explication")),
    ("meubles", ("salon/amenagement/", "explication")),
    ("points-a-verifier", ("salon/amenagement/", "explication")),
    ("changements", ("salon/amenagement/historique.html", "")),
    ("courante-3", ("salon/amenagement/", "")),
    ("", ("salon/amenagement/", "")),
])
def test_redirection_ancres(ancre, attendu):
    assert _traduire(_redirections()["salon-v4.html"], ancre) == attendu


def test_chaque_h2_de_l_ancienne_page_est_traduit(ancienne_page):
    """Chaque titre h2 de l'ancienne page a une ancre (son slug, comme 3d/ancres.js) traduite hors de la vue par défaut,
    sauf les deux titres sans ancre utile."""
    def slug(t):
        t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", t))).strip().lower()
        import unicodedata
        t = unicodedata.normalize("NFD", t).encode("ascii", "ignore").decode()
        return re.sub(r"[^a-z0-9]+", "-", t).strip("-")

    r = _redirections()["salon-v4.html"]
    for attrs, h2 in re.findall(r"<h2([^>]*)>(.*?)</h2>", ancienne_page, re.S):
        ancre = (re.search(r'id="([^"]+)"', attrs) or [None, slug(h2)])[1]   # un id posé en dur garde son nom
        assert _traduire(r, ancre) != ("salon/amenagement/", ""), ancre


def test_liens_vers_les_deux_meubles_et_retour():
    """Les deux meubles renvoient au salon par sa nouvelle adresse."""
    for chemin in ("pieces/salon/etageres/explication.py", "pieces/salon/enfilade/explication.py"):
        t = (RACINE / chemin).read_text(encoding="utf-8")
        assert "salon-v4.html" not in t and "../amenagement/" in t, chemin
