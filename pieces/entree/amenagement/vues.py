"""Vues de l'entrée, pour les deux variantes (principale, victor).

`vues(variante)` rend le dictionnaire des vues du type « aménagement ». Le plan et les coupes viennent de
dessin_principale.py et dessin_victor.py ; le texte long qui suivait chaque dessin est devenu son aria-label. Iso et
Caméra sont les rendus de `site/entree/amenagement/rendus/` (le texte d'origine de `RENDUS` en est l'alt). Explication
reprend le texte de `contenu()` de 3d/entree/plan.py et plan_victor.py, sans la section « Vues 3D ».
"""
from html import escape
from pathlib import Path

from commun.dessin import virg
from commun.modele import Element, Vue
from commun.position import mini_plan
from pieces.entree import piece
from pieces.entree.amenagement import dessin_principale, dessin_victor, document, victor

# (module de variante, module de dessin)
VARIANTES = {"principale": (document, dessin_principale), "victor": (victor, dessin_victor)}

# Calques du plan : (id, nom). Chaque id correspond à la classe `sans-<id>` posée sur la section par le JS ; les
# éléments SVG qu'il masque portent déjà ces classes (voir l'en-tête de dessin_principale.py).
CALQUES = (("cotes", "Cotes"), ("passages", "Passages libres"), ("coupes", "Traits de coupe"),
           ("voisines", "Pièces voisines"), ("annotations", "Annotations"))

# Trait de coupe sur le plan : axe du trait (h : horizontal, à y = repère ; v : vertical, à x = repère), bornes
RENDUS_SITE = Path(__file__).resolve().parents[3] / "site" / "entree" / "amenagement" / "rendus"
COINS = ("no", "ne", "so", "se")   # ordre des segments de l'iso, et des cônes de sa fiche « Position »
CAMERAS_PRISES = ("banc", "couloir")
MARGE_ISO = 26                     # cm entre l'enveloppe des murs et le point de vue d'un coin

TRAITS = {"A": ("h", -6, 270), "B": ("v", -6, 380), "C": ("h", -6, 360), "D": ("v", -6, 380)}


def _e(texte):
    return escape(str(texte), quote=True)


def _trait(D, lettre):
    axe, d0, d1 = TRAITS[lettre]
    coupe = getattr(D, f"COUPE_{lettre}")
    return (lettre, ((d0, coupe), (d1, coupe)) if axe == "h" else ((coupe, d0), (coupe, d1)))


def _zones(M, D, legende_principes):
    """Rectangles touchables du plan, un par meuble de `M.ZONES`."""
    rects = []
    for i, z in enumerate(M.ZONES):
        titre = legende_principes[z["principe"]][0]
        rects.append(f'<rect class="zone" data-meuble="{i}" x="{z["x0"]}" y="{z["y0"]}" width="{z["x1"] - z["x0"]}"'
                     f' height="{z["y1"] - z["y0"]}" rx="2" tabindex="0" role="button" aria-label="{_e(titre)}"/>')
    return "".join(rects)


def _modeles(M, principes):
    """Un `<template data-meuble>` par zone : le JS le recopie dans la fiche quand on touche le meuble."""
    modeles = []
    for i, z in enumerate(M.ZONES):
        titre, texte = principes[z["principe"]]
        cotes = z["cotes"] + (" cm" if z["cotes"][0].isdigit() else "")
        liens = ""
        if z["coupe"]:
            liens += f'<a class="btn" href="#coupes?k={z["coupe"]}">Coupe {z["coupe"]}</a>'
        liens += f'<a class="btn" href="#iso?k={z["iso"]}">Iso</a>'
        modeles.append(f'<template data-meuble="{i}" data-titre="{_e(titre)}"><p class="cotes">{_e(cotes)}</p>'
                       f'<p>{texte}</p><div class="actions">{liens}</div></template>')
    return "".join(modeles)


def _fiche_plan(D):
    boutons = "".join(f'<button type="button" data-calque="{k}" aria-pressed="true">{n}</button>' for k, n in CALQUES)
    return ('<div class="fiche-meuble"><p>Touchez un meuble pour afficher sa fiche.</p></div>'
            f'<h3>Calques</h3><div class="calques">{boutons}</div>'
            f'<h3>Légende</h3>{dessin_principale.legende()}')


def _vue_plan(M, D):
    legendes, principes = D.legendes(M), D.principes(M)
    # role="group" (et non "img") : les zones sont des boutons, que les enfants d'une image masqueraient
    svg = D.plan_svg(M, aria=legendes["plan"], zones=_zones(M, D, principes))
    element = Element(k="", nom="Plan", titre="Plan", scene=svg, fiche=_modeles(M, principes))
    return Vue("plan", [element], fiche=_fiche_plan(D), outils=("zoom", "mesure"))


def _vue_coupes(M, D):
    legendes = D.legendes(M)
    lettres = list(D.SUJETS)
    elements = []
    for lettre in lettres:
        sujet = D.SUJETS[lettre]
        scene = getattr(D, f"coupe_{lettre.lower()}")(M, aria=legendes[lettre])
        elements.append(Element(k=lettre, nom=f"{lettre} {sujet}", titre=f"Coupe {lettre}-{lettre} : {sujet}", scene=scene))
    mini = mini_plan(piece.SOL, piece.PORTES, traits=[_trait(D, k) for k in lettres])
    return Vue("coupes", elements, fiche=f'<h3>Position</h3><div class="mini">{mini}</div>', outils=("zoom", "mesure"))


def _rendu_existe(variante, cle):
    return (RENDUS_SITE / f"{variante}-{cle}.jpg").exists()


def _figure(variante, cle, alt):
    """Le rendu et, par-dessus, sa copie recolorée par le filtre de l'option `teinte` (masque des surfaces India)."""
    base = f"rendus/{variante}-{cle}"
    masque = f"url({base}-masque.png)"
    return (f'<figure class="cadre rendu"><img src="{base}.jpg" alt="{_e(alt)}" draggable="false">'
            f'<img class="calque" src="{base}.jpg" alt="" aria-hidden="true" draggable="false"'
            f' style="filter:url(#filtre-teinte);-webkit-mask-image:{masque};mask-image:{masque}"></figure>')


def _alt(M, cle, repli):
    return dict(M.RENDUS).get(cle, repli)


def _coins_iso():
    """Position du point de vue de chaque coin : à `MARGE_ISO` de l'enveloppe des murs, visant son centre."""
    x0, x1 = min(b.x0 for b in piece.MURS), max(b.x1 for b in piece.MURS)
    y0, y1 = min(b.y0 for b in piece.MURS), max(b.y1 for b in piece.MURS)
    centre = ((x0 + x1) / 2, (y0 + y1) / 2)
    ou = {"no": (x0 - MARGE_ISO, y0 - MARGE_ISO), "ne": (x1 + MARGE_ISO, y0 - MARGE_ISO),
          "so": (x0 - MARGE_ISO, y1 + MARGE_ISO), "se": (x1 + MARGE_ISO, y1 + MARGE_ISO)}
    return {k: (ou[k], centre) for k in COINS}


def _fiche_position(cones):
    return f'<h3>Position</h3><div class="mini">{mini_plan(piece.SOL, piece.PORTES, cones=cones)}</div>'


def _vue_iso(variante, M):
    coins = _coins_iso()
    elements = []
    for k in COINS:
        cle = f"iso_{k}"
        actif = _rendu_existe(variante, cle)
        scene = _figure(variante, cle, _alt(M, cle, f"Vue isométrique, coin {k.upper()}")) if actif else ""
        elements.append(Element(k=k, nom=k.upper(), titre=f"Vue iso {k.upper()}", scene=scene, actif=actif))
    # le JS pose `ici` sur le cône de même rang que l'élément courant
    cones = [(*coins[k], False) for k in COINS]
    return Vue("iso", elements, fiche=_fiche_position(cones))


def _vue_camera(variante, M):
    cameras = {c.id: c for c in piece.CAMERAS}
    elements = []
    for k in CAMERAS_PRISES:
        c = cameras[k]
        actif = _rendu_existe(variante, k)
        scene = _figure(variante, k, _alt(M, k, c.nom)) if actif else ""
        fiche = f'<p class="cotes">yeux à {c.yeux:g} cm, objectif {c.focale:g} mm</p>'
        elements.append(Element(k=k, nom=c.nom, titre=c.nom, scene=scene, fiche=fiche, actif=actif))
    cones = [(cameras[k].loc[:2], cameras[k].cible[:2], False) for k in CAMERAS_PRISES]
    return Vue("camera", elements, fiche=_fiche_position(cones))


# ------------------------------------------------------------------ Explication
def _chiffres(stats):
    return "".join(f"<div><dt>{_e(a)}</dt><dd>{_e(b)}</dd></div>" for a, b in stats)


def _principes(M, cartes):
    """Cartes « Principe » ; celles qui ont un meuble sur le plan lient vers sa zone (`rect.zone[data-meuble]`)."""
    zones = {}
    for i, z in enumerate(M.ZONES):
        zones.setdefault(z["principe"], i)
    def lien(r):
        return f'<a class="btn" href="#plan?k={zones[r]}">Montrer sur le plan</a>' if r in zones else ""
    return "".join(f"<li><h3>{_e(t)}</h3><p>{x}</p>{lien(r)}</li>" for r, (t, x) in enumerate(cartes))


def _achats(M, approx, note):
    lignes = "".join(f'<tr><td>{_e(n)}</td><td class="num">{r}</td><td class="num d">{q}</td>'
                     f'<td class="num d">{f"{q * p:g}".replace(".", ",")} €</td></tr>' for n, r, q, p in M.IKEA)
    total = round(sum(q * p for _, _, q, p in M.IKEA))
    return ('<div class="defile"><table><thead><tr><th>Article</th><th>Référence</th><th class="d">Qté</th>'
            f'<th class="d">Prix</th></tr></thead><tbody>{lignes}'
            f'<tr class="total"><td>Total</td><td></td><td></td><td class="num d">{"≈ " if approx else ""}{total} €</td></tr>'
            f'</tbody></table></div><p class="remarque">{note}</p>')


def _portes_caisson(M, note):
    lignes = "".join(f'<tr><td>{_e(n)}</td><td class="num d">{p} €</td></tr>' for n, p in M.PORTES_PAX)
    return ('<div class="defile"><table><thead><tr><th>Portes pour ce caisson, avec charnières</th>'
            f'<th class="d">Prix</th></tr></thead><tbody>{lignes}</tbody></table></div><p class="remarque">{note}</p>')


def _materiaux(lignes):
    corps = "".join(f'<tr><th scope="row">{_e(a)}</th><td>{b}</td></tr>' for a, b in lignes)
    return f"<table><tbody>{corps}</tbody></table>"


def _article(M, cle, chapo, stats, cartes, achats, materiaux, verifier, source, avant=""):
    liste = "".join(f"<li><span>{x}</span></li>" for x in verifier)
    # le premier rendu du coin sud-ouest, quand il existe, ouvre la page ; son texte est l'alt
    tete = _figure(cle, "iso_so", _alt(M, "iso_so", "Vue isométrique depuis le sud-ouest")) if _rendu_existe(cle, "iso_so") else ""
    return (f'<div class="tete-doc"><div><p class="chapo">{chapo}</p>'
            '<p class="actions"><a class="btn plein" href="#plan">Ouvrir le plan</a><a class="btn" href="#iso">Voir en iso</a></p>'
            f'</div>{tete}</div>'
            f'<dl class="chiffres">{_chiffres(stats)}</dl>'
            f'{avant}<h2>Principe</h2><ol class="principes">{_principes(M, cartes)}</ol>'
            f'<h2>Achats IKEA pour la penderie</h2>{achats}'
            f'<h2>Matériaux</h2>{materiaux}'
            f'<h2>Points à vérifier</h2><ul class="liste">{liste}</ul>'
            f'<p class="remarque">Repère : x vers l\'est depuis le mur ouest du couloir, y vers le sud depuis son mur nord, '
            f'z depuis le sol fini, en cm. {source}</p>')


def _explication_principale(M, D):
    b, c, pe, mi, mh = M.BANC, M.CHAUSSURES, M.PENDERIE, M.MIROIR, M.MEUBLE_HAUT
    lp = pe["x1"] - pe["x0"]
    total = round(sum(q * p for _, _, q, p in M.IKEA))
    chapo = (f"Le couloir ({virg(M.SURFACE)} m²) dessert cinq portes et le passage du salon : il faut ranger sans gêner. "
             "Un banc sous le tableau électrique, un meuble à chaussures étroit avec miroir dans la branche d'entrée, "
             "relié par un angle arrondi à une penderie face à la salle de bain. Un meuble suspendu au plafond marque "
             "l'entrée ; au-delà, murs, plafond et porte sont peints en India Yellow.")
    stats = [(f"PAX {lp} × 35", f"penderie IKEA, ≈ {total} €"), (f"≈ {M.PAIRES} paires", "meuble à chaussures"),
             (f'{c["x0"]} cm', "passage le plus étroit"), (f"{virg(M.SURFACE)} m²", "surface du couloir")]
    achats = _achats(M, True, "Prix IKEA France relevés sur les fiches produit le 13/11/2026, en blanc ; les portes « avec "
                     "charnières » comprennent leurs 4 charnières KOMPLEMENT à fermeture silencieuse. Les deux tablettes "
                     "sont à retirer si le caisson en fournit (le guide d'achat PAX en annonce, la fiche française n'en "
                     "parle pas). Bandeau (chute de mélaminé blanc) et fixation murale (fournie) non comptés.")
    achats += _portes_caisson(M, "En 25 de large, IKEA ne fait que FORSAND, ÅHEIM (miroir) et FARDAL. Plum Living fait des "
                              "portes de 37 pour PAX : deux portes égales au lieu de 50 + 25, dans toutes ses teintes ; pas de "
                              "porte coulissante sur un seul caisson de 75.")
    materiaux = _materiaux([
        ("Sol", f'Carrelage {M.CARRELAGE["nom"]}, pose droite, joints fins.'),
        ("Murs", f'Blanc chaud, comme la cuisine et le salon ({M.MUR_COULEUR}) ; l\'entrée, au sud du meuble haut : murs, '
                 f'plafond, porte et flanc ouest de la penderie en {M.INDIA["nom"]} ({M.INDIA["couleur"]}, valeur affichée '
                 "par plum-living.com ; à voir sur échantillon)."),
        ("Meubles", "Proposition des rendus : banc, meuble à chaussures, angle, plateau et meuble haut en chêne miel (comme "
                    "le salon) ; penderie PAX blanche (FORSAND), de la couleur des murs, pour qu'elle se fasse oublier ; "
                    "son flanc ouest, dans l'entrée, en India. À choisir.")])
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
        f'<b>Cadres</b> : galerie de {M.CADRES["colonnes"] * M.CADRES["rangs"]} cadres {M.CADRES["l"]} × {M.CADRES["h"]} sur '
        f'le mur ouest de l\'entrée (grille {M.CADRES["colonnes"]} × {M.CADRES["rangs"]}, {M.CADRES["ecart"]} d\'écart, '
        f'centre à {M.CADRES["zc"]}), entre le meuble haut et l\'interphone ; ils ne dépassent que de '
        f'{virg(M.CADRES["ep"])} dans le passage.',
        f'<b>Interphone</b> : au mur ouest, à droite de la porte d\'entrée vue de l\'intérieur ; dessiné à '
        f'{M.INTERPHONE["y0"]} du mur nord, haut à {M.INTERPHONE["z1"]} : position et taille à relever.',
        "<b>Meuble haut</b> : vérifier qu'il n'y a ni spot, ni détecteur, ni bouche d'aération au plafond à cet endroit, "
        "et la nature des deux murs pour les fixations.",
        "<b>Sens de la porte d'entrée</b> : sur le relevé, les paumelles sont à droite (côté salle de bain) et la porte "
        "ouvre vers l'intérieur. Si elles sont à gauche, le vantail se range contre le mur ouest.",
        "<b>Portes du mur nord</b> : la gauche est celle de la cuisine (coulissante côté cuisine), la droite celle du WC, "
        "d'après le plan du salon.",
        f"<b>Hauteur sous plafond</b> : {M.H}, reprise de la salle de bain ; le salon a été relevé à 254,5.",
        f'<b>Passage du salon</b> : {M.PORTES[2]["b"] - M.PORTES[2]["a"]} de large sur ce relevé, 82 sur le relevé du '
        "salon (V4.12) : à remesurer."]
    return _article(M, "principale", chapo, stats, D.principes(M), achats, materiaux, verifier,
                    "Dimensions : pieces/entree/amenagement/document.py.")


def _explication_victor(M, D):
    b, pe, mi, pl, cd = M.CHAUSSURES, M.PENDERIE, M.MIROIR, M.PLANCHE, M.CADRES
    lp, pp = pe["y1"] - pe["y0"], pe["x1"] - pe["x0"] - pe["facade"]
    total = round(sum(q * p for _, _, q, p in M.IKEA))
    chapo = (f'Variante de l\'<a href="./">aménagement {M.BASE}</a>. Le mur sous le tableau électrique reste '
             "libre. Un meuble à chaussures bas à abattants, deux étagères flottantes au-dessus, prend la place de la "
             "penderie face à la salle de bain ; il file jusqu'à la penderie et s'y termine en arrondi. La penderie, un "
             "PAX d'IKEA de 75 × 35 qui monte presque au plafond, passe dans la branche d'entrée ; une planche à "
             "chaussures court sous les patères. En face, sur le mur ouest peint en India, des cadres et un miroir à côté "
             "de l'interphone.")
    stats = [(f"PAX {lp} × {pp}", f"penderie IKEA, ≈ {total} €"), (f"≈ {M.PAIRES} paires", "meuble à abattants et planche"),
             (f'{pe["x0"]} cm', "passage le plus étroit"), (f'{b["y0"]} cm', "devant le meuble à chaussures")]
    achats = _achats(M, False, "Prix IKEA France relevés sur les fiches produit le 13/11/2026, en blanc. Charnières "
                     "KOMPLEMENT en plus (nombre et prix à lire sur la fiche des portes), bandeau et fixation murale non comptés.")
    materiaux = _materiaux([
        ("Sol", f'Carrelage {M.CARRELAGE["nom"]}, comme la {M.BASE}.'),
        ("Murs", f'Blanc chaud ({M.MUR_COULEUR}) ; l\'entrée en {M.INDIA["nom"]} ({M.INDIA["couleur"]}).'),
        ("Meubles", "Proposition des rendus : meuble à chaussures, étagères flottantes et planche en chêne miel ; penderie "
                    "PAX (caisson, portes FORSAND, bandeau) peinte en India comme les murs ; cadres noirs fins, "
                    "passe-partout blanc. À choisir.")])
    verifier = [
        f'<b>Passage</b> : {pe["x0"]} cm entre la penderie et le mur ouest, contre 85 en {M.BASE} ; {pl["x0"]} devant la '
        f'planche. Porte de 50 ouverte, il reste {pe["x0"] - pe["portes"][0]} cm.',
        "<b>Peinture du PAX</b> : caisson et portes FORSAND sont en mélaminé blanc : poncer légèrement, sous-couche "
        "d'accrochage, puis la peinture des murs (ou une laque teintée à l'identique). Autre piste : des façades sur "
        "mesure pour PAX dans la teinte (Plum Living en propose, à vérifier). India n'existe chez Plum Living qu'en laque "
        "de façade, pas en peinture murale (relevé du 13/11/2026) : avec India, faire teinter la peinture sur échantillon ; "
        "l'option « Teinte » de « Personnaliser » indique pour chaque couleur les gammes où elle existe.",
        f'<b>Plafond</b> : IKEA demande au moins 1 cm au-dessus du caisson pour monter et ouvrir des portes battantes ; '
        f'avec {M.H} sous plafond, il en reste {M.H - pe["z1"]}.',
        "<b>Porte d'entrée</b> : ouverte à 90°, elle s'arrête contre la planche ; un tampon sur le chant évite les marques.",
        f'<b>Planche</b> : {pl["z1"] - pl["ep"]} cm sous la planche, assez pour des baskets et des chaussures de ville, '
        "pas pour des bottes (à ranger dessus).",
        "<b>Étagères flottantes</b> : fixations cachées dans la cloison de la salle de bain : vérifier sa nature (carreaux "
        "de plâtre, placo) et la charge admise.",
        f'<b>Interphone</b> : le miroir est calé {M.INTERPHONE["y0"] - mi["y1"]} cm à côté ; sa position est à relever.',
        f'<b>Tableau électrique, plafond</b> : mêmes points que la <a href="./">{M.BASE}</a>.']
    c = M.CHAUSSURES
    lpl, ppl = pl["y1"] - pl["y0"], pl["x1"] - pl["x0"]
    ncd = cd["colonnes"] * cd["rangs"]
    diff = [
        ("Sous le tableau électrique", "Banc 95 × 38", "Rien : mur libre"),
        ("Face nord de la salle de bain", "Penderie 84 × 40 toute hauteur",
         f'Meuble à chaussures {c["x1"] - c["xa"]} × {b["y1"] - b["y0"]}, un niveau d\'abattants, arrondi jusqu\'au PAX, '
         "deux étagères flottantes au-dessus"),
        ("Angle", "Quart de cercle R 25 à étagères ouvertes",
         f'Quart de cercle plein R {b["r"]} centré sur le coin de la salle de bain, bout du meuble à chaussures'),
        ("Cloison de la salle de bain, après le coin", "Meuble à chaussures, premier module (83)",
         f'Penderie IKEA PAX {lp} × {pp} × {pe["z1"]}, bandeau jusqu\'au plafond'),
        ("Cloison de la salle de bain, côté porte", "Meuble à chaussures, second module (83), miroir",
         f'Planche à chaussures {lpl} × {ppl} à {pl["z1"]}, les 4 patères au-dessus, applique'),
        ("Meuble haut", "En travers de la branche d'entrée, 110 × 40", "Supprimé : deux tablettes en haut de la penderie"),
        ("Mur ouest de l'entrée", "Interphone",
         f'{ncd} cadres, miroir {mi["y1"] - mi["y0"]} × {mi["z1"] - mi["z0"]}, interphone'),
        ("Chaussures", "≈ 24 paires", f"≈ {M.PAIRES} paires"),
        ("Passage le plus étroit", "85 (devant le meuble à chaussures)", f'{pe["x0"]} (devant la penderie)')]
    lignes = "".join(f"<tr><td>{_e(a)}</td><td>{_e(x)}</td><td>{_e(y)}</td></tr>" for a, x, y in diff)
    avant = (f'<h2>Différences avec la {M.BASE}</h2><div class="defile"><table><thead><tr><th>Élément</th>'
             f'<th>{M.BASE}</th><th>Version Victor</th></tr></thead><tbody>{lignes}</tbody></table></div>')
    return _article(M, "victor", chapo, stats, D.principes(M), achats, materiaux, verifier,
                    "Dimensions : pieces/entree/amenagement/victor.py.", avant)


def _vue_explication(variante, M, D):
    ecrire = _explication_principale if variante == "principale" else _explication_victor
    element = Element(k="", nom="Explication", titre="Explication", scene=ecrire(M, D))
    return Vue("explication", [element])


def vues(variante: str) -> dict[str, Vue]:
    M, D = VARIANTES[variante]
    return {
        "plan": _vue_plan(M, D),
        "coupes": _vue_coupes(M, D),
        "iso": _vue_iso(variante, M),
        "camera": _vue_camera(variante, M),
        "explication": _vue_explication(variante, M, D),
    }
