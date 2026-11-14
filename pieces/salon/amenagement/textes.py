"""Les textes du salon/aménagement tirés de l'ancienne page (3d/salon/plan.py) : le long paragraphe sous le plan (4 299
caractères) découpé en passages, un par meuble ou par principe, et les textes sous les coupes.

Chaque passage sert trois fois : la fiche du meuble touchable (zones.py), la carte « Principe » de l'Explication
(explication.py) et, mis bout à bout, le texte alternatif du plan (`texte_alternatif_plan`). Rien n'est perdu : les
passages, dans l'ordre, redonnent tout le paragraphe. Écarts avec l'ancienne page, seulement ces quatre :
- les références aux boutons (« bouton Siège », « bouton dans la barre du haut ») disent l'option de « Personnaliser » ;
- les nombres sont à la française, sans « .0 » (« centrée en (303,5, 215) » et non « (303.5, 215.0) ») ;
- le tapis dépasse le canapé de la valeur du modèle (26) et non de 25, écrit en dur depuis la V4.8 et faux depuis ;
- ② donne les tablettes du modèle (5) quand l'ancienne étiquette en disait 4 (voir dessins.py).
Les cotes viennent du modèle ; ce qui n'y est pas (70 d'un côté de la table, 1,5 fois la largeur de l'image, zoom courant
1,2 à 1,6, 25 au-dessus du meuble bas…) est repris tel quel de l'ancienne page.
"""
import re
from html import escape, unescape

from pieces.salon import piece
from pieces.salon.amenagement import document as M
from pieces.salon.amenagement import dessins
from pieces.salon.meubles import cote as c


def _modules() -> str:
    return " ; ".join(f"M{k + 1} {escape(ct)}" for k, (_, ct) in enumerate(M.MODULES))


def _passages() -> list[tuple[str, str, str]]:
    """[(id, titre, corps HTML)], dans l'ordre de l'ancien paragraphe. L'id est celui de la zone du plan quand le passage
    est celui d'un meuble (zones.py), sinon un mot qui nomme le principe."""
    e, et, mo, cn, d, t, dg = M.ENFILADE, M.ETAGERES, M.MONTANTS, M.CANAPE, M.DESSERTE, M.TABLE, M.DEGAGEMENTS
    tb, dy, ch, k, ec, pj, cl = M.TABLE_BASSE, M.DYVLINGE, M.CHILIENNE, M.CONSOLE, M.ECRAN, M.PROJECTEUR, M.CLIM
    lm = e["modules"][0][1] - e["modules"][0][0]
    xr, yr = t["ronde"]
    return [
        ("enfilade", "① Enfilade",
         f'Contre le mur ouest, {c(e["y1"] - e["y0"])} centrés entre le coin nord et le cadre du passage ({c(e["y0"])} '
         f'libres à chaque bout), profondeur {c(e["p"])} (caisson {c(e["p"] - e["facade"])} + façades {c(e["facade"])}), '
         f'dessus à {c(e["z1"])}, sur pieds de {c(e["pieds"])} ; trois modules de {c(lm)} : {_modules()}. '
         'Le meuble a <a href="../enfilade/">sa page</a>.'),
        ("etageres", "② Étagères sur montants",
         f'Tireté sur le plan : {mo["n"]} montants noirs vissés au mur au-dessus de l\'enfilade, à {c(mo["pas"])} d\'axe en axe, et '
         f'{len(M.TABLETTES)} tablettes en chêne de {c(et["p"])} de profondeur, décalées, sur {c(M.METRES_ETAGERES)} m '
         '(voir la page <a href="../etageres/">Étagères</a>).'),
        ("canape", "③ Canapé",
         f'{escape(cn["nom"])} {cn["l"]} × {cn["p"]} dos au mur nord, tourné vers le sud, à {M.ALLEE_ENFILADE} de '
         "l'enfilade : l'allée laisse ouvrir les portes du module nord."),
        ("desserte", "④ Desserte",
         f'{c(d["x1"] - d["x0"])} × {c(d["y1"] - d["y0"])} sur roulettes, contre le mur nord, dans le décroché nord-est '
         f'(x {c(d["x0"])} → {c(d["x1"])}), façade au sud : à côté de la baie, sans rien devant le vitrage. Platine au '
         f"milieu du dessus, vinyles sur deux niveaux (≈ {round(M.VINYLES, -1):.0f})."),
        ("table-quotidien", "⑤ Table, au quotidien",
         f'À volets et allonges (type Louis-Philippe). Au quotidien, <b>ronde</b> Ø {c(t["d"])} (volets levés) dans '
         f'l\'angle sud-est, face à la baie, centrée en ({c(xr)}, {c(yr)}), avec {M.CONFIGS["f"]["chaises"]} chaises en '
         'biais et la suspension au-dessus.'),
        ("table-ouverte", "⑤ Table, ouverte",
         f'Pour recevoir, on la tire au milieu et on ajoute {t["allonges"]} allonges de {t["allonge"]} : <b>ouverte</b>, '
         f'ovale de {c(t["ouvert"])} × {c(t["d"])} centrée en ({c(t["cx"])}, {c(t["cy"])}), est-ouest (nord-sud, il '
         f'faudrait {c(t["ouvert"] + 2 * 70)} pour {M.P}), {M.CONFIGS["o"]["chaises"]} chaises à pas de '
         f'{M.PAS_CHAISES:.0f}, une à chaque bout ; les {M.CHAISES_PLIANTES} chaises de plus sont pliantes, rangées dans '
         'le kafoutche extérieur.'),
        ("table-basse", "⑥ Table basse",
         f'<a href="{escape(tb["url"])}">{escape(tb["nom"])}</a> {tb["l"]} × {tb["p"]} ({tb["prix"]} €), dessus à '
         f'{tb["z1"]} (à peine au-dessus de l\'assise, {cn["assise"]}), à {tb["ecart"]} devant le canapé, centrée sur lui.'),
        ("siege", "⑦ Siège",
         f'Au choix, option Siège de Personnaliser : <a href="{escape(dy["url"])}">IKEA DYVLINGE</a> pivotant ({dy["l"]} × {dy["p"]} × {dy["h"]}, '
         f'assise à {dy["assise"]}, {dy["prix"]} €) à l\'est de la table basse, tourné vers le canapé ; il pivote vers '
         f'l\'écran ou la baie. Variante : chilienne {ch["long"]} × {ch["l"]}, tête à l\'est.'),
        ("meuble-bas", "⑧ Meuble bas",
         f'Style enfilade scandinave {k["l"]} × {k["p"]} × {k["z1"]} sur pieds, contre le mur sud en face du canapé, '
         'centré sur lui ; peu profond pour laisser passer la table ouverte.'),
        ("ecran", "Écran",
         f'Le mur sud au-dessus du meuble bas sert d\'écran : image {c(ec["l"])} × {c(ec["h"])} (16/9), bas à '
         f'{c(ec["bas"])}, vue du canapé à ≈ {c(pj["recul"])} (1,5 fois la largeur de l\'image, le confort habituel).'),
        ("projecteur", "Vidéoprojecteur",
         f'Au plafond au-dessus du canapé, à {c(pj["recul"])} du mur : il faut un rapport de projection de '
         f'{c(pj["rapport"], 2)} (zoom courant 1,2–1,6).'),
        ("clim", "Clim",
         f'Existante sur le mur sud, tout à l\'est (x {c(cl["x0"])} → {c(cl["x1"])}, h {c(cl["z0"])} → {c(cl["z1"])}, à '
         'relever).'),
        ("rangement-table-ouverte", "Table ouverte, les rangements",
         "La table basse se range debout dans l'allée de l'enfilade (on n'ouvre pas le module nord pendant le dîner), le "
         "DYVLINGE recule contre le mur nord à côté de la desserte, la chilienne se plie contre le mur sud."),
        ("degagements", "Dégagements",
         f'En rouge sur le plan : au quotidien, {c(dg["canape_basse"])} entre le canapé et la table basse, puis '
         f'{c(k["y0"] - tb["pos"]["f"][3])} jusqu\'au meuble bas ; ouverte, {c(dg["canape_table"])} entre le canapé et la '
         f'table, {c(dg["table_sud"])} jusqu\'au meuble bas, {c(dg["bout_ouest"])} entre son bout ouest et l\'enfilade, '
         f'{c(dg["bout_est"])} à l\'est. À {M.CONFIGS["o"]["chaises"]}, il reste {c(dg["derriere_chaises"])} derrière les '
         "chaises côté canapé et côté meuble bas : on s'assoit, on ne circule plus derrière."),
        ("deco", "Déco",
         f'Option Décoration de Personnaliser, proportions d\'aménagement : un seul tapis, {M.TAPIS["l"]} × '
         f'{M.TAPIS["p"]}, sous le coin canapé ({c((M.TAPIS["l"] - cn["l"]) / 2)} de plus que le canapé de chaque côté, '
         "pieds avant du canapé et de la chilienne dessus), rien sous la table à manger ; lampadaire de lecture contre "
         "l'accoudoir est du canapé, derrière l'épaule de qui est dans le siège, hors du passage devant la desserte ; "
         "lampe à poser sur l'enfilade, sous la première tablette, et petite lampe au bout de la desserte ; plantes (vert : "
         "une grande à droite du meuble bas, hors de l'image et loin du souffle de la clim, des branches sur l'enfilade) ; "
         f'paire de cadres 55 × 70 au-dessus du canapé (2/3 de sa largeur, bas à 20 du dossier), cadre 80 × 60 au-dessus de '
         "la desserte (bas à 135 : le capot de la platine s'ouvre) ; livres sur les étagères, avec un objet au bout de "
         "chaque tablette (vase, petite plante, bol) et la tablette du haut, trop basse pour des livres, garnie de deux "
         "plantes retombantes et d'un vase ; deux livres d'art et un bol sur la table basse, un vase bas au centre de la "
         "table ronde."),
        ("rideau", "Rideau",
         f'De lin écru (beige) sur rail au plafond, tiré au sud de la baie sur le trumeau (au nord, la desserte) : '
         f'replié, {c(M.RIDEAU["y1"] - M.RIDEAU["y0"])} de plis dont 15 sur le bord du vitrage.'),
        ("suspension", "Suspension",
         f'Ø {c(M.SUSPENSION["d"])} (tireté jaune, la moitié de la table) au-dessus de la table ronde : table ouverte, '
         "elle n'est plus centrée (à prévoir : un second point lumineux ou une suspension déplaçable)."),
    ]


PASSAGES = _passages()
ECHELLE = "Échelle : 1 unité = 1 cm ; ouest à gauche, nord en haut."


def _texte(fragment: str) -> str:
    """Le texte d'un fragment HTML : balises ôtées, entités lues, espaces simples."""
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", "", fragment))).strip()


def texte_alternatif_plan() -> str:
    """Tout le paragraphe de l'ancienne page, en texte brut : l'échelle, puis chaque passage sous son titre."""
    morceaux = [ECHELLE]
    for _, titre, corps in PASSAGES:
        morceaux.append(f"{_texte(titre)} : {_texte(corps)}")
    return " ".join(morceaux)


# ------------------------------------------------------------------ sous les coupes (texte alternatif de chaque coupe)
def alt_coupe_a() -> str:
    e, et, mo = M.ENFILADE, M.ETAGERES, M.MONTANTS
    zs = ", ".join(str(z) for z in et["zs"])
    return (f'Coupe à x {dessins.COUPE_A}, regard vers l\'ouest : le sud est à gauche. Enfilade sur pieds de {c(e["pieds"])}, '
            f'dessus à {c(e["z1"])} ; au-dessus, {mo["n"]} montants noirs percés tous les {c(mo["pas_trous"])} (z {c(mo["z0"])} '
            f'→ {c(mo["z1"])}, ils ne touchent pas l\'enfilade) et des tablettes de chêne de {c(et["ep"])} décalées, dessus à '
            f'{zs} (un premier vide de {c(et["zs"][0] - et["ep"] - e["z1"])} au-dessus de l\'enfilade pour poser lampes et '
            f'objets, puis {c(et["zs"][1] - et["zs"][0] - et["ep"])} de hauteur libre entre tablettes : les livres courants '
            f'font 18 à 30). À gauche, le passage vers le couloir ({c(piece.PASSAGE["y1"] - piece.PASSAGE["y0"])} × '
            f'{piece.PASSAGE["h"]}) avec son cadre.')


def alt_coupe_b() -> str:
    d = M.DESSERTE
    return (f'Coupe à x {dessins.COUPE_B}, regard vers l\'est : le nord est à gauche. Desserte h {d["z1"]} sur roulettes de '
            f'{d["roulettes"]} : deux niveaux de vinyles debout (pochettes 31,5) et la platine dessus, dont le plateau arrive '
            f'vers {d["z1"] + 10}, à hauteur de main debout. Elle est coupée à gauche, contre le mur nord, à côté de la baie '
            'qui reste entièrement dégagée (tireté au milieu = jonction des vantaux). Table ronde et ses chaises devant la '
            'baie ; grande plante et cadre (déco) à droite, contre le trumeau sud.')


def alt_coupe_c() -> str:
    t = M.TABLE
    return (f'Coupe à y {c(dessins.COUPE_C)} (axe de la table ouverte), regard vers le nord : l\'ouest est à gauche. '
            'Enfilade et étagères coupées à gauche, canapé contre le mur nord au fond, desserte et platine au fond à droite, '
            f'baie coupée. Au quotidien : table basse devant le canapé, chilienne coupée, table ronde coupée à droite ; '
            f'ouverte : table coupée au milieu (plateau à {t["z1"]}), table basse poussée au fond à côté du canapé. '
            f'Suspension Ø {c(M.SUSPENSION["d"])}, bas à {M.SUSPENSION["z0"]}, soit {c(M.SUSPENSION["z0"] - t["z1"])} '
            'au-dessus du plateau.')


def alt_coupe_d() -> str:
    k, ec, cl = M.CONSOLE, M.ECRAN, M.CLIM
    return (f'Coupe à y {dessins.COUPE_D}, regard vers le sud : l\'est est à gauche. Meuble bas {k["l"]} × {k["p"]}, dessus à '
            f'{k["z1"]}, trois façades (deux portes, un abattant au milieu pour la box et les câbles) ; au-dessus, l\'image '
            f'{c(ec["l"])} × {c(ec["h"])} de {ec["bas"]} à {c(ec["bas"] + ec["h"])}, sous la clim (h {cl["z0"]}) qui reste hors '
            'de l\'image, à gauche. À droite, le passage vers le couloir. Table ronde et chaises coupées au premier plan à '
            'gauche ; ouverte, la table coupée au milieu.')


def alt_rendu(cle: str) -> str:
    """Titre et version du modèle du rendu `iso_se` ou `iso_no`, comme la note sous l'image de l'ancienne page."""
    titre, version, _ = M.RENDUS[0 if cle == "iso_se" else 1]
    return f"{titre} (modèle {version})"
