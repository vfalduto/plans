import re
from pieces.sdb.meuble_bas import modele as B, vues
from tests.sdb_anciennes import corrige, entre, morceaux, page_achats, page_bas, section, texte

V = vues.vues("")


def _s(cle): return V[cle].elements[0].scene


def test_decoupe():
    s = _s("decoupe")
    assert s.startswith("<h2>Pièces</h2>") and s.split("<tbody>")[1].count("<tr>") == 7 and "<h2>Finition</h2>" in s
    assert "B à G : trois tablettes" in texte(s) and "Tablette 3, 250 × 50 : C (85) + G (69)" in texte(s)
    for m in morceaux(entre(page_bas(), '<h3 id="finition">', "<h3>Montage</h3>")):
        assert corrige(m) in texte(s), m


def test_montage():
    s = _s("montage")
    assert [h for h in re.findall(r"<h2>(.*?)</h2>", s)] == ["Montage", "Pose de la colonne"]
    assert s.count('<ol class="etapes"') == 2 and len(vues.etapes_montage()) == 13 and len(vues.pose_colonne()) == 5
    assert "<b>Mesurer l'alcôve</b>" in s and "Outils à réunir" not in s
    for m in morceaux(entre(page_bas(), "<h3>Montage</h3>", "<h3>Tenue</h3>")
                      + entre(page_bas(), "<h3>Pose de la colonne</h3>", '<h2 id="plan">')):
        assert corrige(m) in texte(s), m


def test_achats():
    s = _s("achats")
    assert re.findall(r"<h2>(.*?)</h2>", s) == ["Meuble bas", "Les deux meubles"]
    table = s.split("<tbody>")[1].split("</tbody>")[0]
    assert table.count("<tr>") == 16 and "Total du meuble bas" in table and "296,82 €" in table
    for nom, ref, q, pu, st in B.prix():
        assert ref in table and nom.replace("'", "&#x27;") in table
    assert "2 × 16,50 €, stock : 25" in table and "stock : 50" in table
    assert "Le détail est dans la liste d'achats." in texte(s) and "sdb-meuble-achats.html#bas" not in s
    assert "<td>Meuble bas</td>" in s and 'href="#achats"' not in s
    # le titre « Achats » de l'ancienne page est devenu l'onglet ; chaque paragraphe est pris entier
    vieux = entre(page_bas(), "<p>Le meuble bas entier", "</p>") + "</p>" \
        + section(page_achats(), "bas").split("<div", 1)[0] + "<p>" + section(page_achats(), "bas").split('<p class="note">', 1)[1]
    for m in morceaux(vieux):
        assert corrige(m) in texte(s), m


def test_sans_point_median_ni_chasse_fixe():
    for cle in ("decoupe", "montage", "achats"):
        assert "·" not in _s(cle) and "mono" not in _s(cle), cle


# ------------------------------------------------------------------ schémas du montage
def test_chaque_piece_a_une_etape():
    noms = {b.nom for b in B.blocs()}
    poses = {**B.POSE, **B.POSE_COLONNE}
    assert noms == set(poses)
    assert all(1 <= B.POSE[k] <= len(vues.etapes_montage()) for k in B.POSE)
    assert all(1 <= v <= len(vues.pose_colonne()) for v in B.POSE_COLONNE.values())
    for table in (B.ACCENT, B.CONTEXTE):
        assert all(1 <= n <= len(vues.etapes_montage()) and set(p) <= noms for n, p in table.items())
    assert all(1 <= n <= len(vues.pose_colonne()) and set(p) <= noms for n, p in B.ACCENT_COLONNE.items())


def test_figures_du_montage():
    avec = [i for i in range(1, 14) if vues.figure_montage(i)]
    assert avec == [1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13] and not vues.figure_montage(2)
    assert [i for i in range(1, 6) if vues.figure_colonne(i)] == [2, 3, 4]
    for i in avec:
        assert vues.figure_montage(i).startswith("<svg")
    s = _s("montage")
    assert s.count('<figure class="etape-figure"><svg') == 12 + 3
    # à l'étape 4 seuls les vérins sont en couleur ; à l'étape 13 la machine et le tapis
    assert vues.figure_montage(4).count("inew") == 6 * 3 and "imel" in vues.figure_montage(4) and "ihub" not in vues.figure_montage(12)
    assert "ihub" in vues.figure_montage(13)


def test_texte_des_etapes_inchange():
    s = _s("montage")
    sans_figure = re.sub(r'<figure class="etape-figure">.*?</figure>', "", s)
    attendu = "".join(f"<li><div><p>{t}</p></div></li>" for t in vues.etapes_montage())
    assert attendu in sans_figure
    attendu = "".join(f"<li><div><p>{t}</p></div></li>" for t in vues.pose_colonne())
    assert attendu in sans_figure


def test_schemas_du_montage_a_la_meme_echelle():
    """La largeur d'un schéma est proportionnelle à celle de son dessin : la porte seule reste plus petite que le meuble."""
    import re
    larg = lambda s: float(re.search(r"width:([\d.]+)%", s).group(1))
    assert larg(vues.figure_montage(3)) < 0.5 * larg(vues.figure_montage(12))
    assert larg(vues.figure_colonne(2)) < 0.3 * larg(vues.figure_colonne(3))
    assert all(larg(vues.figure_montage(i)) <= 100 for i in (1, 4, 13))
