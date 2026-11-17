"""Vues de l'entrée, pour les deux variantes (principale, victor).

`vues(variante)` rend le dictionnaire des vues du type « aménagement ». Le plan et les coupes viennent de
dessin_principale.py et dessin_victor.py ; le texte long qui suivait chaque dessin est devenu son aria-label. Iso et
Caméra sont les rendus de `site/entree/amenagement/rendus/` (le texte d'origine de `RENDUS` en est l'alt). Explication
reprend le texte de `contenu()` des anciens 3d/entree/plan.py et plan_victor.py, sans la section « Vues 3D ».
"""
from html import escape
from pathlib import Path

from commun.blocs import (Achat, Carte, Coupe, Lieu, SectionAchats, Zone, a_verifier, achats, chiffres, cotes_meuble,
                          figure_rendu, materiaux, nombre, note_source, points_iso, principes, rendu, tete,
                          total_achats, vue_camera, vue_coupes, vue_iso, vue_lecture, vue_plan, zones_svg)
from commun.dessin import virg
from commun.modele import Vue
from pieces.entree import piece
from pieces.entree.amenagement import dessin_principale, dessin_victor, document, victor

# (module de variante, module de dessin)
VARIANTES = {"principale": (document, dessin_principale), "victor": (victor, dessin_victor)}

RENDUS_SITE = Path(__file__).resolve().parents[3] / "site" / "entree" / "amenagement" / "rendus"
CAMERAS_PRISES = ("banc", "couloir")
LIEU = Lieu(piece.SOL, piece.PORTES, "Position dans l'entrée")

# Trait de coupe sur le plan : axe du trait (h : horizontal, à y = repère ; v : vertical, à x = repère), bornes
TRAITS = {"A": ("h", -6, 270), "B": ("v", -6, 380), "C": ("h", -6, 360), "D": ("v", -6, 380)}
SAILLIE_PORTE = 14                 # cm : la zone d'une porte déborde de l'ouverture dans le couloir (maquette)
# surfaces recolorées dans les rendus, chacune à travers son masque (le premier : <rendu>-masque.png, puis -masque-<id>.png)
FILTRES = "teinte pax plinthe murs coussin"


def _e(texte):
    return escape(str(texte), quote=True)


def _trait(D, lettre):
    axe, d0, d1 = TRAITS[lettre]
    coupe = getattr(D, f"COUPE_{lettre}")
    return ((d0, coupe), (d1, coupe)) if axe == "h" else ((coupe, d0), (coupe, d1))


def _emprise_porte(p):
    """Ouverture d'une porte, de l'épaisseur du mur à `SAILLIE_PORTE` dans le couloir."""
    vers_couloir = 1 if p["mur"] in "no" else -1     # le couloir est au sud d'un mur nord, à l'est d'un mur ouest
    d0, d1 = sorted((p["face"] - vers_couloir * piece.EP, p["face"] + vers_couloir * SAILLIE_PORTE))
    return (d0, p["a"], d1, p["b"]) if p["mur"] in "eo" else (p["a"], d0, p["b"], d1)


def _zone(M, z):
    """Emprise (x0, y0, x1, y1) et cotes d'une zone de `M.ZONES`, tirées du meuble ou de la porte qu'elle nomme ; un
    bord donné par la zone remplace celui du meuble."""
    if "meuble" in z:
        m = getattr(M, z["meuble"])
        return tuple(z.get(c, m[c]) for c in ("x0", "y0", "x1", "y1")), cotes_meuble(m, z.get("plateau", False))
    if "porte" in z:
        p = next(p for p in piece.PORTES if p["nom"] == z["porte"])
        return _emprise_porte(p), f'vantail de {nombre(p["b"] - p["a"])}'
    return (z["x0"], z["y0"], z["x1"], z["y1"]), z["cotes"]


def _zones(M, D):
    """Meubles touchables du plan, un par zone de `M.ZONES` ; leur id est leur rang."""
    principes = D.principes(M)
    zones = []
    for i, z in enumerate(M.ZONES):
        titre, texte = principes[z["principe"]]
        emprise, cotes = _zone(M, z)
        zones.append(Zone(id=str(i), titre=titre, emprise=emprise, cotes=cotes, texte=texte,
                          coupe=z["coupe"] or "", iso=z["iso"], si=z.get("si", "")))
    return zones


def _vue_plan(M, D):
    zones = _zones(M, D)
    # role="group" (et non "img") : les zones sont des boutons, que les enfants d'une image masqueraient
    svg = D.plan_svg(M, aria=D.legendes(M)["plan"], zones=zones_svg(zones))
    return vue_plan(svg, zones, dessin_principale.legende())


def _vue_coupes(M, D):
    legendes = D.legendes(M)
    coupes = [Coupe(k=lettre, nom=f"{lettre} {sujet}", titre=f"Coupe {lettre}-{lettre} : {sujet}",
                    scene=getattr(D, f"coupe_{lettre.lower()}")(M, aria=legendes[lettre]), trait=_trait(D, lettre))
              for lettre, sujet in D.SUJETS.items()]
    return vue_coupes(coupes, LIEU)


def _vue_iso(variante, M):
    enveloppe = (min(b.x0 for b in piece.MURS), min(b.y0 for b in piece.MURS),
                 max(b.x1 for b in piece.MURS), max(b.y1 for b in piece.MURS))
    return vue_iso(RENDUS_SITE, variante, LIEU, points_iso(enveloppe), alts=dict(M.RENDUS), filtre=FILTRES)


def _vue_camera(variante, M):
    cameras = {c.id: c for c in piece.CAMERAS}
    return vue_camera(RENDUS_SITE, variante, LIEU, [cameras[k] for k in CAMERAS_PRISES], alts=dict(M.RENDUS),
                      filtre=FILTRES)


# ------------------------------------------------------------------ Explication
def _cartes(M, D):
    """Cartes « Principe » ; celles qui ont un meuble sur le plan lient vers sa première zone (son rang)."""
    zones = {}
    for i, z in enumerate(M.ZONES):
        zones.setdefault(z["principe"], str(i))
    return [Carte(t, x, zones.get(r, "")) for r, (t, x) in enumerate(D.principes(M))]


def _sections(M):
    return [SectionAchats("", [Achat(n, r, q, p) for n, r, q, p in M.IKEA])]


def _achats(M, approx, note):
    return achats(_sections(M), titre="Achats IKEA pour la penderie", note=note, approx=approx)


def _portes_caisson(M, note):
    lignes = "".join(f'<tr><td>{_e(n)}</td><td class="num d">{p} €</td></tr>' for n, p in M.PORTES_PAX)
    return ('<div class="defile"><table><thead><tr><th>Portes pour ce caisson, avec charnières</th>'
            f'<th class="d">Prix</th></tr></thead><tbody>{lignes}</tbody></table></div><p class="remarque">{note}</p>')


def _article(M, D, cle, chapo, stats, achats, matieres, verifier, source, avant=""):
    # le premier rendu du coin sud-ouest, quand il existe, ouvre la page ; son texte est l'alt
    figure = figure_rendu(rendu(RENDUS_SITE, cle, "iso_so"),
                          dict(M.RENDUS).get("iso_so", "Vue isométrique depuis le sud-ouest"), filtre=FILTRES)
    return (tete(chapo, [("#plan", "Ouvrir le plan"), ("#iso", "Voir en iso")], figure)
            + chiffres(stats) + avant + principes(_cartes(M, D)) + achats + materiaux(matieres)
            + a_verifier(verifier, titre="Points à vérifier")
            + note_source("Repère : x vers l'est depuis le mur ouest du couloir, y vers le sud depuis son mur nord, "
                          f"z depuis le sol fini, en cm. {source}"))


def _explication_principale(M, D):
    c, pe = M.CHAUSSURES, M.PENDERIE
    lp = pe["x1"] - pe["x0"]
    chapo = (f"Le couloir ({virg(M.SURFACE)} m²) dessert cinq portes et le passage du salon : il faut ranger sans gêner. "
             "Un banc sous le tableau électrique, un meuble à chaussures étroit sur plinthe, arrondi côté penderie, dans la branche "
             "d'entrée, relié par son angle à une penderie face à la salle de bain ; côté porte, des patères au-dessus "
             "du sol libre, et en face un miroir à côté de l'interphone. Au-delà de la penderie, murs, plafond et porte "
             "sont peints en India ; le reste du couloir prend la teinte choisie.")
    total = total_achats(_sections(M), approx=True)   # « ≈ … € », le total du tableau des achats
    stats = [(f"PAX {lp} × {pe['caisson']}", f"penderie IKEA, {total}"), (f"≈ {M.PAIRES} paires", "meuble à chaussures et bas de la PAX"),
             (f'{c["x0"]} cm', "passage le plus étroit"), (f"{virg(M.SURFACE)} m²", "surface du couloir")]
    achats = _achats(M, True, "Prix IKEA France relevés sur les fiches produit le 13/11/2026, en blanc ; les portes « avec "
                     "charnières » comprennent leurs 4 charnières KOMPLEMENT à fermeture silencieuse. Les deux tablettes "
                     "sont à retirer si le caisson en fournit (le guide d'achat PAX en annonce, la fiche française n'en "
                     "parle pas). Bandeau (chute de mélaminé blanc) et fixation murale (fournie) non comptés.")
    achats += _portes_caisson(M, "En 25 de large, IKEA ne fait que FORSAND, ÅHEIM (miroir) et FARDAL. Plum Living fait des "
                              "portes de 37 pour PAX : deux portes égales au lieu de 50 + 25, dans toutes ses teintes ; pas de "
                              "porte coulissante sur un seul caisson de 75.")
    matieres = [
        ("Sol", f'Carrelage {M.CARRELAGE["nom"]}, pose droite, joints fins.'),
        ("Murs", "Couloir : teinte Plum Living au choix dans « Personnaliser », Galet par défaut (la peinture murale la "
                 f"plus proche du blanc chaud de la cuisine et du salon, {M.MUR_COULEUR}) ; l'entrée, au sud du nu de la "
                 f'penderie : murs, plafond, porte et flanc ouest de la penderie en {M.INDIA["nom"]} ({M.INDIA["couleur"]}, '
                 "valeur affichée par plum-living.com ; à voir sur échantillon)."),
        ("Meubles", "Proposition des rendus : banc, meuble à chaussures, angle arrondi et plateau en chêne miel (comme "
                    "le salon) ; meuble haut en chêne au-dessus, portes de placard ; penderie PAX blanche (FORSAND) par défaut, teinte Plum Living au choix dans « Personnaliser » ; "
                    "son flanc ouest, dans l'entrée, en India. À choisir.")]
    verifier = [
        "<b>Tableau électrique</b> : encastré entre la cuisine et le WC (indiqué par le client) ; sa position et sa "
        "hauteur sont à relever. Si ses commandes les plus basses sont sous 1 m, le banc gêne l'accès : le raccourcir ou "
        "le décaler.",
        "<b>Teinte India</b> : India de Plum Living (Beige 11) n'existe qu'en laque de façade : il n'est pas dans les 30 "
        "peintures murales de plum-living.com (relevé du 13/11/2026). Pour les murs, faire teinter une peinture à partir "
        "d'un échantillon, ou choisir une teinte qui existe dans les deux gammes (option « Teinte » de « Personnaliser », "
        "premier groupe). Le flanc du PAX (mélaminé blanc) se peint après une sous-couche d'accrochage, ou se couvre d'un "
        "panneau de finition Plum Living 37 × 236 (218 €).",
        "<b>PAX</b> : 9 cm restent libres à l'est du caisson, avant l'huisserie de la salle de bain ; caisson fixé au mur "
        "de la salle de bain (vérifier la nature de la cloison). Hauteur sous plafond d'au moins 237 pour le monter debout.",
        f'<b>Prise fibre</b> : dessinée sur la cloison de la salle de bain à {M.PRISE_FIBRE["axe"]} du sol, '
        f'{M.PRISE_FIBRE["y0"] - 208} cm au sud du coin de la salle de bain : relever sa position exacte pour placer la '
        "découpe du dos ; vérifier que la box tient dans le compartiment du bas (37 de haut, 23 de profondeur) "
        "et qu'une prise de courant est à portée, et percer la tablette pour l'aération.",
        f'<b>Cadres et miroir</b> : galerie de {M.CADRES["colonnes"] * M.CADRES["rangs"]} cadres {M.CADRES["l"]} × '
        f'{M.CADRES["h"]} (grille {M.CADRES["colonnes"]} × {M.CADRES["rangs"]}, {M.CADRES["ecart"]} d\'écart, centre à '
        f'{virg(M.CADRES["zc"])}) entre l\'alignement du coin de la salle de bain et le miroir, '
        f'{virg(M.CADRES["y0"] - M.CADRES_Y0)} cm de chaque côté. Miroir {M.MIROIR["y1"] - M.MIROIR["y0"]} × '
        f'{M.MIROIR["z1"] - M.MIROIR["z0"]} calé {M.INTERPHONE["y0"] - M.MIROIR["y1"]} cm au nord de l\'interphone. '
        f'Ils ne dépassent que de {virg(M.CADRES["ep"])} dans le passage.',
        f'<b>Porte d\'entrée ouverte</b> : calculée avec une béquille de {M.BEQUILLE["saillie"]} de saillie, axe à '
        f'{M.BEQUILLE["axe"]} du chant, à {M.BEQUILLE["z"]} du sol, et des paumelles côté salle de bain : à 90°, la '
        f'béquille passe à {M.OUVERTURE["jeu_meuble"]:.0f} cm du bout du meuble à chaussures ; la porte s\'ouvre '
        f'jusqu\'à {M.OUVERTURE["max"]:.0f}°, où {M.OUVERTURE["cause"]}. Mesurer la béquille réelle et '
        f'poser un butoir de sol à {M.OUVERTURE["butoir"]}°. Un manteau sur la première patère arrêtera la porte '
        'un peu avant.',
        f'<b>Penderie et salon</b> : {M.PAX_MUR["d"]:.0f} cm en diagonale du coin nord-est de la penderie (façade) au '
        f'coin du mur qui sépare le salon du couloir et de la chambre ({M.PAX_MUR["b"][0] - M.PAX_MUR["a"][0]} en x, '
        f'{M.PAX_MUR["a"][1] - M.PAX_MUR["b"][1]} en y), d\'après le relevé : à vérifier au mètre.',
        f'<b>Interphone</b> : au mur ouest, à droite de la porte d\'entrée vue de l\'intérieur ; dessiné à '
        f'{M.INTERPHONE["y0"]} du mur nord, haut à {M.INTERPHONE["z1"]} : position et taille à relever.',
        f'<b>Meuble haut</b> : de {M.MEUBLE_HAUT["z0"]} à {M.MEUBLE_HAUT["z1"]} (fileur au-dessus) sur le meuble à chaussures, fixé à la cloison '
        "de la salle de bain (vérifier sa nature et la charge admise) ; ses portes battantes ouvrent au-dessus du "
        "passage, hors de portée de tête.",
        "<b>Carrelage</b> : texture des rendus tirée de la photo du sol en place ; les carreaux y sont dessinés en "
        "60 × 60 : relever leur taille réelle et le sens de pose.",
        "<b>Sens de la porte d'entrée</b> : sur le relevé, les paumelles sont à droite (côté salle de bain) et la porte "
        "ouvre vers l'intérieur. Si elles sont à gauche, le vantail se range contre le mur ouest.",
        "<b>Portes du mur nord</b> : la gauche est celle de la cuisine (coulissante côté cuisine), la droite celle du WC, "
        "d'après le plan du salon.",
        f"<b>Hauteur sous plafond</b> : {M.H}, reprise de la salle de bain ; le salon a été relevé à 254,5.",
        f'<b>Passage du salon</b> : {M.PORTES[2]["b"] - M.PORTES[2]["a"]} de large sur ce relevé, 82 sur le relevé du '
        "salon (V4.12) : à remesurer."]
    return _article(M, D, "principale", chapo, stats, achats, matieres, verifier,
                    "Dimensions : pieces/entree/amenagement/document.py.")


def _explication_victor(M, D):
    b, pe, mi, cd, co, mh = M.CHAUSSURES, M.PENDERIE, M.MIROIR, M.CADRES, M.CONSOLE, M.MEUBLE_HAUT
    lp, pp = pe["y1"] - pe["y0"], pe["x1"] - pe["x0"] - pe["facade"]
    chapo = (f'Variante de l\'<a href="./">aménagement {M.BASE}</a>. Une console sous le tableau électrique ; en '
             "face, un banc à chaussures bas à abattants, avec son coussin, prend la place de la penderie face à la salle "
             "de bain, une étagère flottante et un meuble haut de même forme au-dessus ; il file jusqu'à la penderie et "
             "s'y termine par un bout plein au coin arrondi. La penderie, un PAX d'IKEA de 75 × 35 sur plinthe, passe "
             "dans la branche d'entrée ; sol libre sous les patères. En face, sur le mur ouest peint en India, des cadres "
             "et un miroir à côté de l'interphone.")
    total = total_achats(_sections(M), approx=True)
    stats = [(f"PAX {lp} × {pp}", f"penderie IKEA, {total}"), (f"≈ {M.PAIRES} paires", "banc et bas de la PAX"),
             (f'{pe["x0"]} cm', "passage le plus étroit"), (f'{b["y0"] - co["y1"]} cm', "entre la console et le banc")]
    achats = _achats(M, False, "Prix IKEA France relevés sur les fiches produit le 13/11/2026, en blanc. Charnières "
                     "KOMPLEMENT en plus (nombre et prix à lire sur la fiche des portes), bandeau et fixation murale non comptés.")
    matieres = [
        ("Sol", f'Carrelage {M.CARRELAGE["nom"]}, comme la {M.BASE}.'),
        ("Murs", "Couloir : teinte Plum Living au choix dans « Personnaliser », Galet par défaut ; l'entrée en "
                 f'{M.INDIA["nom"]} ({M.INDIA["couleur"]}).'),
        ("Meubles", "Proposition des rendus : banc à chaussures, étagère, meuble haut et console en chêne miel ; coussin "
                    "en tissu, teinte au choix dans « Personnaliser » ; penderie PAX (caisson, portes FORSAND, bandeau) "
                    "peinte en India comme les murs ; cadres noirs fins, passe-partout blanc. À choisir.")]
    verifier = [
        f'<b>Passage</b> : {pe["x0"]} cm entre la penderie et le mur ouest, contre 85 en {M.BASE}. Porte de 50 ouverte, '
        f'il reste {pe["x0"] - pe["portes"][0]} cm.',
        "<b>Peinture du PAX</b> : caisson et portes FORSAND sont en mélaminé blanc : poncer légèrement, sous-couche "
        "d'accrochage, puis la peinture des murs (ou une laque teintée à l'identique). Autre piste : des façades sur "
        "mesure pour PAX dans la teinte (Plum Living en propose, à vérifier). India n'existe chez Plum Living qu'en laque "
        "de façade, pas en peinture murale (relevé du 13/11/2026) : avec India, faire teinter la peinture sur échantillon ; "
        "l'option « Teinte » de « Personnaliser » indique pour chaque couleur les gammes où elle existe.",
        f'<b>Plafond</b> : IKEA demande au moins 1 cm au-dessus du caisson pour monter et ouvrir des portes battantes ; '
        f'avec {M.H} sous plafond et la plinthe de {pe["socle"]}, il en reste {M.H - pe["z1"]}.',
        f'<b>Console</b> : sous le tableau électrique (bas dessiné à {M.TABLEAU["z0"]}, à relever), dessus à {co["z1"]} ; '
        "posée, pour la déplacer quand il faut ouvrir le tableau.",
        f'<b>Meuble haut</b> : {mh["z1"] - mh["z0"]} de haut, de {mh["z0"]} à {mh["z1"]} et un fileur jusqu\'au plafond, fixé à la cloison de la salle de '
        "bain : vérifier sa nature (carreaux de plâtre, placo) et la charge admise, comme pour l'étagère flottante.",
        "<b>Porte d'entrée</b> : sans la planche, rien ne l'arrête ; poser un butoir de sol.",
        f'<b>Banc et salon</b> : {M.BANC_MUR["d"]:.0f} cm en diagonale du coin nord-est du banc (façade) au coin du mur '
        f'qui sépare le salon du couloir et de la chambre ({M.BANC_MUR["b"][0] - M.BANC_MUR["a"][0]} en x, '
        f'{M.BANC_MUR["a"][1] - M.BANC_MUR["b"][1]} en y), d\'après le relevé : à vérifier au mètre.',
        f'<b>Interphone</b> : le miroir est calé {M.INTERPHONE["y0"] - mi["y1"]} cm à côté ; sa position est à relever.',
        f'<b>Tableau électrique, plafond</b> : mêmes points que la <a href="./">{M.BASE}</a>.']
    c = M.CHAUSSURES
    ncd = cd["colonnes"] * cd["rangs"]
    diff = [
        ("Sous le tableau électrique", "Banc 95 × 38", f'Console {co["x1"] - co["x0"]} × {co["y1"] - co["y0"]} à {co["z1"]}'),
        ("Face nord de la salle de bain", "Penderie 84 × 40 toute hauteur",
         f'Banc à chaussures {c["x1"] - c["x0"]} × {b["y1"] - b["y0"]}, un niveau d\'abattants, coussin, jusqu\'au PAX ; '
         "une étagère flottante et un meuble haut de même forme au-dessus"),
        ("Angle", "Quart de cercle R 25", f'Bout plein en chêne, coin R {b["r"]}, sur plinthe'),
        ("Cloison de la salle de bain, après le coin", "Meuble à chaussures, premier module (83)",
         f'Penderie IKEA PAX {lp} × {pp} × {pe["h"]} sur plinthe, bandeau jusqu\'au plafond'),
        ("Cloison de la salle de bain, côté porte", "Meuble à chaussures, second module (83), miroir",
         "Sol libre, les 4 patères, applique"),
        ("Meuble haut", "En travers de la branche d'entrée, 110 × 40",
         f'Au-dessus du banc et de l\'étagère, de {mh["z0"]} à {mh["z1"]} + fileur, 2 portes de placard'),
        ("Mur ouest de l'entrée", "Interphone",
         f'{ncd} cadres, miroir {mi["y1"] - mi["y0"]} × {mi["z1"] - mi["z0"]}, interphone'),
        ("Chaussures", "≈ 24 paires", f"≈ {M.PAIRES} paires"),
        ("Passage le plus étroit", "85 (devant le meuble à chaussures)", f'{pe["x0"]} (devant la penderie)')]
    lignes = "".join(f"<tr><td>{_e(a)}</td><td>{_e(x)}</td><td>{_e(y)}</td></tr>" for a, x, y in diff)
    avant = (f'<h2>Différences avec la {M.BASE}</h2><div class="defile"><table><thead><tr><th>Élément</th>'
             f'<th>{M.BASE}</th><th>Version Victor</th></tr></thead><tbody>{lignes}</tbody></table></div>')
    return _article(M, D, "victor", chapo, stats, achats, matieres, verifier,
                    "Dimensions : pieces/entree/amenagement/victor.py.", avant)


def _vue_explication(variante, M, D):
    ecrire = _explication_principale if variante == "principale" else _explication_victor
    return vue_lecture("explication", ecrire(M, D))


def vues(variante: str) -> dict[str, Vue]:
    M, D = VARIANTES[variante]
    return {
        "plan": _vue_plan(M, D),
        "coupes": _vue_coupes(M, D),
        "iso": _vue_iso(variante, M),
        "camera": _vue_camera(variante, M),
        "explication": _vue_explication(variante, M, D),
    }
