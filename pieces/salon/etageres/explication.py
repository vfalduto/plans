"""Explication du document salon/etageres : tête, chiffres clés, dispositions, le mécanisme, présentoir, rendus,
matériaux, tenue, points à vérifier, remarque finale.

Textes repris de 3d/salon/etageres.py (page, section_dispositions, section_meuble, section_presentoir,
section_rendus, section_materiaux, section_charges, section_valider), f-strings telles quelles : les valeurs viennent
de document.py et calculs.py, comme avant. Deux phrases changent (plan, décision 6) : le choix d'une disposition et la
remarque finale. Les textes sous les dessins deviennent leurs textes alternatifs.
"""
from html import escape

from commun.blocs import a_verifier, chiffres, materiaux, note_source, tete, total_achats
from commun.blocs_construction import rendus_meuble
from pieces.salon.etageres import calculs
from pieces.salon.etageres.calculs import FACTEUR, PR, coincement, fixation, kn, prix, taux
from pieces.salon.etageres.dessins import DESSINS, legendes
from pieces.salon.etageres.document import (ARR, BANDE, CHARGE_LIVRES, ETAGERES as ET, ETUDE_MONTANTS as EU, KERF,
                                            L_MONTANT, MATERIAUX, MONTANTS as MO, NIVEAUX, P_CALCUL, P_RUINE, PANNEAU,
                                            R_ACIER, R_FLEX, R_JOUE, R_MONTANT, RA_COTE, RENDUS, SOURCES_TENUE,
                                            TASSEAU, TN, _b_rain, _levier, _t_rain)
from pieces.salon.etageres.vues import RENDUS_SITE, etapes_montage, sections_achats
from pieces.salon.dessin import f
from pieces.salon.meubles import cote as cm
from pieces.salon.piece import H

PAS = MO["pas"]
RA = ET["rainure"]
SALON = "../amenagement/"
FIXATIONS = "../../archives/salon-bibliotheque-fixation.html"


def _tableau(entete, lignes):
    return f'<div class="defile"><table><thead><tr>{entete}</tr></thead><tbody>{lignes}</tbody></table></div>'


def _liste(points):
    """Liste du site (`ul.liste`) : chaque point dans un `<span>`, une seule colonne."""
    return '<ul class="liste">' + "".join(f"<li><span>{p}</span></li>" for p in points) + "</ul>"


def _adresse(cle):
    return "./#explication" if cle == calculs.CLES[0] else f"{cle}.html#explication"


# ------------------------------------------------------------------ tête et chiffres clés (ET:1170-1179)
def _tete(e):
    chapo = ("<b>Étagères sur montants percés</b> : "
             f'{MO["n"]} montants peints en noir, vissés au mur ouest au-dessus de l\'enfilade sans toucher '
             f'ni elle ni le plafond, et {len(e.ts)} tablettes en chêne massif entaillées autour d\'eux, pincées par des '
             f'chevilles d\'acier : disposition <b>{escape(e.nom)}</b>, {cm(e.metres)} m de rayonnage, {e.n_tailles} '
             f'longueur{"s" if e.n_tailles > 1 else ""} de tablette, pour ≈ {e.total:.0f} € de matériaux.')
    return tete(chapo, liens=(("#plans", "Plans détaillés"), ("#achats", "Liste d'achats"), (SALON, "Le salon")))


def _chiffres(e):
    return chiffres(((e.kit, "longueurs des tablettes (cm)"), (f"{len(calculs.pieces(e))} repères", "pièces à débiter"),
                     (f"{len(etapes_montage())} étapes", "de la cloison sondée au montage"),
                     (total_achats(sections_achats(e), arrondi=False), "matériaux TTC, sans livraison ni outillage")))


# ------------------------------------------------------------------ dispositions (ET:790-815)
def _dispositions(e):
    toutes = [calculs.etat(c) for c in calculs.CLES]
    d0 = toutes[0]
    k2 = next(d for d in toutes if d.cle == "rangs")
    vignettes = "".join(
        f'<a class="dispo" href="{_adresse(d.cle)}"{" aria-current=\"page\"" if d.cle == e.cle else ""}>'
        f'<b>{escape(d.nom)}</b><span>{escape(d.kit)}</span>{DESSINS["mini"](d)}<span>{escape(d.idee)}</span></a>'
        for d in toutes)
    lignes = "".join(
        f'<tr><td><b>{escape(d.nom)}</b></td><td>{len(d.ts)} : {escape(d.kit)}</td><td class="num">{d.n_tailles}</td>'
        f'<td class="num">{cm(d.metres)}</td><td>{len(d.niveaux)} ({d.niveaux[0]} → {d.niveaux[-1]})</td>'
        f'<td class="num">{round(d.libre_min)} → {round(d.libre_max)}</td><td class="num">{d.chevilles}</td>'
        f'<td class="num">{len(d.panneaux)}</td><td class="num">{prix(d.total)}</td></tr>' for d in toutes)
    entete = ('<th>Disposition</th><th>Tablettes</th><th class="num">Tailles</th><th class="num">Mètres</th>'
              '<th>Hauteurs de dessus</th><th class="num">Libre entre tablettes</th><th class="num">Chevilles</th>'
              '<th class="num">Plans</th><th class="num">Total</th>')
    regles = [
        f"<b>Dessus</b> de {NIVEAUX[0]} (la lampe posée sur l'enfilade passe dessous) à {NIVEAUX[1]} (la cheville "
        f"arrière reste sous le haut du montant), de {MO['pas_trous']} en {MO['pas_trous']}.",
        f"<b>Deux tablettes sur la même travée</b> : 25 au moins d'un dessus à l'autre, soit ≈ {cm(25 - ET['ep'])} de "
        "libre (poches, objets) ; 30 pour les livres courants, 40 pour les grands formats et les vinyles "
        f"({cm(31.5 + 0.5)} de haut).",
        "<b>Deux tablettes qui se partagent un montant</b> sans partager de travée (leurs débords l'un au-dessus de "
        "l'autre) : 15 au moins.",
        f"<b>Au même niveau</b> : une travée vide entre les deux ({cm(PAS - 2 * ET['debord'])} entre les bouts).",
    ]
    return (
        "<h2>Dispositions</h2>"
        f'<p>Les {MO["n"]} montants et leurs trous ne changent pas : percés de {NIVEAUX[0]} à {NIVEAUX[1]} de '
        f'{MO["pas_trous"]} en {MO["pas_trous"]}, ils portent toutes les dispositions ci-dessous. Seules les tablettes '
        "changent, en nombre, en longueur et en hauteur. Choisir une disposition change toute la page : élévation, "
        "vues de dessus, vue iso, composition, débit, achats et prix.</p>"
        f'<div class="dispos">{vignettes}</div>'
        + _tableau(entete, lignes)
        + "<h3>Deux longueurs seulement</h3>"
        f'<p>Hors disposition actuelle, toutes les tablettes font une travée (<b>79</b> : {ET["debord"]} + {PAS} + '
        f'{ET["debord"]}) ou deux (<b>134</b>) ; les longues de 189 et 244 sont divisées. Une bande refendue de '
        f'{cm(BANDE)} donne exactement une 134 et une 79 ({cm(BANDE - 134 - 79 - 2 * KERF)} de chute) ou trois 79 '
        f'({cm(BANDE - 3 * 79 - 3 * KERF)} de chute) : avec les deux mêmes plans de chêne qu\'aujourd\'hui, on tire '
        f'{k2.kit} (Rangs, Décalée) ou 2 × 134 + 8 × 79 (Escalier). Une troisième longueur (189) ne se marie avec '
        f'aucune autre dans 250 : elle laisserait {cm(BANDE - 189 - KERF)} de chute par bande. Les tablettes de même '
        "longueur sont <b>interchangeables</b> : Rangs et Décalée se recomposent l'une en l'autre sans rien racheter, "
        "en déplaçant les chevilles.</p>"
        f"<p>Diviser coûte des entailles et des chevilles en plus ({k2.chevilles} au lieu de {d0.chevilles}, un rond "
        f"d'acier de plus), et une tablette divisée laisse une travée vide à son niveau, entre ses deux morceaux (deux "
        f"bouts de {ET['debord']} ne peuvent pas se partager un montant au même niveau) : c'est ce vide, qui change de "
        "place d'un rang à l'autre, qui fait le dessin.</p>"
        "<h3>Règles de composition</h3>"
        + _liste(regles)
        + note_source(
            "Libre entre tablettes : du dessus d'une tablette au dessous de celle qui la couvre, sur une même travée ; "
            f"au-dessus de la plus haute, il reste au moins {cm(H - NIVEAUX[1])} jusqu'au plafond. Le plan du salon "
            "garde la disposition actuelle tant qu'aucune n'est choisie ; les rendus 3D ne montrent qu'elle."))


# ------------------------------------------------------------------ le mécanisme (ET:853, ET:856)
def _mecanisme():
    return (
        "<h2>Le mécanisme</h2>"
        f"<p>La <b>rainure</b> : sous chaque tablette, au droit de la cheville avant, {cm(RA['l'] * 10)} mm de large et "
        f"{cm(RA['prof'] * 10)} mm de profondeur (la moitié de la cheville), sur {f(RA['long'])} centrés sur chaque "
        f"entaille ({cm(RA_COTE)} de chaque côté). La cheville avant y est logée : la tablette ne peut plus avancer "
        "vers la pièce (il faudrait la faire passer de toute son épaisseur entre les deux chevilles, en levant le "
        "devant de plus de 10°, et le montant dans l'entaille l'en empêche), et la cheville ne peut plus glisser en "
        "long dans son trou, les deux bouts de la rainure l'arrêtent. Rien ne se voit de face ; de dessous, une fente "
        f"de {f(RA['long'])} autour de chaque montant, presque cachée par les bouts de cheville.</p>"
        f"<p>Une tablette se monte ou se descend de {MO['pas_trous']} en {MO['pas_trous']}, et peut glisser d'un "
        f"montant : toutes les entailles sont à {PAS} l'une de l'autre, seule sa longueur est fixée.</p>")


# ------------------------------------------------------------------ présentoir (ET:859-881)
def _presentoir(e):
    arr = MO["x_av"] - MO["x_ar"]
    cas = [("au milieu de la tablette", ET["p"] / 2), ("contre le rebord", ET["p"] - 3),
           ("tout contre les montants", MO["p"] + 2)]
    lig = "".join(f'<tr><td>{a}</td><td class="num">{f(x)}</td><td class="num">{cm(round(2 * (x - MO["x_av"]) / arr + 1, 1))}</td>'
                  f'<td class="num">{f"{coincement(x):.2f}".replace(".", ",")}</td><td class="num">{cm(round(0.2 / coincement(x), 1))}</td></tr>'
                  for a, x in cas)
    entete = ('<th>Poids posé</th><th class="num">à … du mur</th><th class="num">serrage / poids</th>'
              '<th class="num">frottement minimal</th><th class="num">marge avec 0,2</th>')
    return (
        "<h2>Présentoir</h2>"
        f"<p>Possible à la place d'une courte, dans n'importe quelle disposition : une tablette dédiée, penchée de "
        f"{PR['deg']}° vers la pièce, pour une pochette de vinyle ou un livre d'art posé de face, sur les mêmes trous "
        "qu'une tablette à plat. Aucune disposition n'en a.</p>"
        f'<figure class="calepin">{DESSINS["presentoir"](e, aria=legendes(e)["presentoir"])}</figure>'
        "<h3>Ce qui l'empêche de glisser vers la pièce</h3>"
        f"<p>Penchée, la tablette est poussée le long de sa pente (flèche verte) par ≈ {round(PR['s'] * 100)} % du "
        "poids posé. Deux choses la retiennent.</p>"
        + _liste([
            "<b>La rainure</b>, qui l'arrête quoi qu'il arrive : chargée ou vide, cognée par-dessous, ou le devant "
            "soulevé pour glisser une pochette. Pour avancer, la tablette devrait passer de toute son épaisseur "
            f"({cm(ET['ep'])}) entre les deux chevilles : il faudrait lever le devant de plus de {PR['deg'] + 10}° (de "
            f"{PR['deg']}° penchée à 10° relevée), ce que le montant, dans l'entaille, ne laisse pas faire.",
            "<b>Le coincement (arc-boutement)</b>, comme un tiroir qu'on tire par un coin et qui se bloque : plus on "
            "charge le devant, plus les deux chevilles serrent la tablette, et le frottement grandit avec ce serrage. "
            f"Les chevilles n'étant qu'à {f(arr)} l'une de l'autre, ce serrage vaut plusieurs fois le poids posé ; la "
            "condition de non-glissement ne dépend alors pas du poids, seulement de la géométrie et du frottement. "
            "Chargée, la tablette ne pousse donc presque pas sur la rainure."])
        + _tableau(entete, lig)
        + note_source(
            f"Frottement minimal = tan {PR['deg']}° / (2 d / {f(arr)} + 1), d = distance du poids à la cheville avant. "
            "Acier sur bois : 0,2 à 0,6 selon les tableaux de frottement (voir les sources de la section Tenue). Le "
            "coincement disparaît dès qu'on soulève le devant : c'est la rainure qui tient alors.")
        + _liste([
            f"<b>Rainure du présentoir</b> : axe à {cm(PR['axe'])} du chant arrière (mesuré sur le dessous), "
            f"{cm(PR['l'] * 10)} × {cm(PR['prof'] * 10)} mm, sur {f(RA['long'])} centrés sur chaque entaille comme à "
            f"plat ; il reste {cm((ET['ep'] - PR['prof']) * 10)} mm de chêne au-dessus, assez pour une tablette "
            "d'objets (≈ 10 kg). Profondeur à ajuster à l'essai sur une chute : la tablette doit se pincer à "
            f"{PR['deg']}°, sans jeu.",
            "<b>Pose et retrait</b> : comme une tablette à plat (chevilles avant, tablette posée dessus, chevilles "
            "arrière glissées par-dessus) ; pour la retirer, on sort les chevilles arrière."]))


# ------------------------------------------------------------------ rendus (ET:828-831)
def _rendus(e):
    if e.cle == calculs.CLES[0]:
        return (rendus_meuble(RENDUS_SITE, e.cle, RENDUS, titre="Rendus 3D")
                + note_source("Disposition actuelle seulement ; les autres dispositions se rendent sur demande."))
    return ("<h2>Rendus 3D</h2>"
            + note_source(f'Rendus de la disposition Actuelle seulement (<a href="{_adresse(calculs.CLES[0])}">les '
                          "voir</a>) ; les autres dispositions se rendent sur demande."))


# ------------------------------------------------------------------ matériaux (ET:884-889)
def _materiaux():
    lignes = [(p, f"{escape(r)}<br><small>{escape(w)}</small><br><small>Autres possibilités : {escape(a)}</small>")
              for p, r, w, a in MATERIAUX]
    return materiaux(lignes) + note_source(
        f"Le modèle est dessiné avec des montants de {cm(MO['l'])} × {MO['p']} et des tablettes de {cm(ET['ep'])} ; "
        f"les bruts retenus font {cm(TASSEAU['s'][0])} × {cm(TASSEAU['s'][1])} et {cm(PANNEAU['ep'])}. L'écart ne "
        "change ni l'aspect ni les charges, mais le perçage se règle sur les pièces réelles (voir le montage).")


# ------------------------------------------------------------------ tenue (ET:973-1026)
def tenue_dispo(e):
    ch, fx = e.ch, fixation(e)
    return (f'<p><b>Disposition {escape(e.nom)}</b> : ≈ {ch["poids"]:.0f} kg pleine ; le montant le plus chargé, '
            f'M{ch["m"] + 1}, porte ≈ {ch["max"]:.0f} kg. Sur ses vis : ≈ {fx["v"] / 9.81:.0f} kg de cisaillement chacune, '
            f'et ≈ {fx["t"] / 9.81:.0f} kg d\'arrachement sur celle du haut (la charge est à ≈ {cm(TN["e"])} du mur, le '
            f'montant bascule sur son pied), soit ≈ {kn(fx["r"])} kN sur la vis du haut.</p>')


def _tenue(e):
    av, ar = EU["avant"], EU["arriere"]
    lig = [
        ("Cheville d'acier", "pli d'un bout (Ø 10, porte-à-faux de " + cm(ET["cheville_ext"]) + ")",
         av * FACTEUR, R_ACIER, taux(av * FACTEUR, R_ACIER, bois=False), f"acier courant S235, {TN['fy']} MPa"),
        ("Montant (sapin)", "écrasement du bois sous la cheville avant, dans le sens du fil",
         av * FACTEUR, R_MONTANT, taux(av * FACTEUR, R_MONTANT),
         f"portance Eurocode 5 : 0,082 (1 − 0,01 d) ρk = {cm(TN['fh0'])} MPa, ρk {TN['rho']} (bois non classé, pris en C18)"),
        ("Tablette (chêne) sur la cheville avant", "écrasement de la joue, en travers du fil",
         av * FACTEUR, R_JOUE, taux(av * FACTEUR, R_JOUE),
         f"compression transversale D30 : {cm(TN['fc90'])} MPa sur 1 × 3 par bout (contact de 1,5 et diffusion de 1,5)"),
        ("Tablette (chêne) sous la cheville arrière", "même chose, sur le dessus",
         ar * FACTEUR, R_JOUE, taux(ar * FACTEUR, R_JOUE), "idem"),
        ("Tablette (chêne) au droit de la rainure", "flexion du porte-à-faux là où elle est amincie",
         EU["effort"] * FACTEUR, R_FLEX, taux(EU["effort"] * FACTEUR, R_FLEX),
         f"flexion D30 : {TN['fm']} MPa, sur {cm(_t_rain / 10)} d'épaisseur et {cm(_b_rain / 10)} de large seulement "
         f"(la rainure moins l'entaille), charge à {cm(_levier)} de la cheville avant"),
    ]
    verdict = lambda u: "large" if u < 0.4 else ("correct" if u < 0.8 else ("juste" if u <= 1 else "insuffisant"))  # noqa: E731
    rows = "".join(f'<tr><td><b>{a}</b> <small>{b}</small></td><td class="num">{F / 9.81:.0f} kg</td>'
                   f'<td class="num">{R / 9.81:.0f} kg</td><td class="num">{round(u * 100)} %</td><td>{verdict(u)}</td>'
                   f'<td>{escape(n)}</td></tr>' for a, b, F, R, u, n in lig)
    entete = ('<th>Pièce</th><th class="num">Effort</th><th class="num">Résistance</th><th class="num">Taux</th>'
              '<th>Verdict</th><th>Base</th>')
    fx = fixation(max((calculs.etat(c) for c in calculs.CLES), key=lambda d: d.ch["max"]))
    src = [f'<a href="{u}">{escape(t)}</a>' for u, t in SOURCES_TENUE]
    flex = taux(EU["effort"] * FACTEUR, R_FLEX)
    return (
        "<h2>Tenue : poids et chute</h2>"
        "<p>Recherche faite sur les règles de l'Eurocode 5 (assemblages par broches), les classes de bois EN 338 et les "
        "fiches de chevilles fischer (sources en bas de section). Le mécanisme est une <b>pince</b> : la tablette "
        f"pivote sur la cheville avant, et la cheville arrière, à {f(ARR)} seulement derrière, retient l'arrière qui "
        f"veut se soulever. Avec la charge à ≈ {cm(TN['e'])} du mur, la cheville arrière reprend ≈ "
        f"{cm(round(EU['arriere'] / EU['effort'], 1))} fois le poids posé, et la cheville avant ce poids plus ce "
        f"qu'elle retient. Cas étudié : {PAS} de tablette pleine de livres ({CHARGE_LIVRES} kg/m) par montant, × "
        f"{cm(FACTEUR)} au montant du milieu d'une longue (le plus chargé).</p>"
        "<h3>Ce qui peut céder</h3>"
        + _tableau(entete, rows)
        + note_source(
            f"Résistance caractéristique ; taux = effort × {cm(TN['gq'])} / (résistance × {cm(TN['kmod'])} / "
            f"{cm(TN['gm'])}) pour le bois, effort × {cm(TN['gq'])} / résistance pour l'acier (méthode de l'Eurocode 5, "
            "coefficients de mémoire). En dessous de 100 %, la pièce tient avec la sécurité de la norme. Les modèles de "
            "la joue et de la rainure sont prudents : la joue, calculée comme une broche dans un trou, porterait "
            "plusieurs fois plus ; en flexion, toute la longueur de la tablette participe, pas seulement les "
            f"{cm(_b_rain / 10)} autour de l'entaille.")
        + _liste([
            "<b>Le poids des livres : ça tient.</b> Les points les plus chargés sont dans la tablette en chêne, au "
            f"milieu d'une longue pleine : la flexion là où la rainure l'amincit ({round(flex * 100)} %, calcul très "
            f"prudent ; {round(flex * ((ET['ep'] - RA['prof']) / ET['ep']) ** 2 * 100)} % sans rainure) et son appui "
            f"sur les chevilles ({round(taux(av * FACTEUR, R_JOUE) * 100)} %) : la marge existe, sans être énorme ; une "
            f"rainure plus profonde que {cm(RA['prof'] * 10)} mm n'apporterait rien et affaiblirait la tablette. Avec "
            "le temps, le chêne peut se marquer d'un demi-millimètre sous les chevilles : la tablette pencherait alors "
            f"un peu vers l'avant (≈ 0,5 mm sur {f(ARR)} de levier, soit ≈ 5 mm au bord). L'acier "
            f"({round(taux(av * FACTEUR, R_ACIER, bois=False) * 100)} %) et le montant "
            f"({round(taux(av * FACTEUR, R_MONTANT) * 100)} %) sont larges. Correction de V1.4 : le montant est chargé "
            f"dans le sens du fil (portance ≈ {cm(TN['fh0'])} MPa), pas en travers (2,5).",
            f"<b>Quelqu'un qui s'appuie ou s'accroche au bord</b> d'une courte : ≈ {P_CALCUL:.0f} kg tirés au bord avec "
            f"la sécurité de la norme, et vers {round(P_RUINE, -1):.0f} kg les joues de chêne s'écrasent et la tablette "
            "pique du nez (les chevilles d'acier ne cassent pas). C'est une étagère, pas une échelle : un enfant qui "
            "grimpe est le vrai risque.",
            "<b>Les chevilles peuvent-elles glisser de côté ?</b> La cheville avant, celle qui porte, non : elle est "
            "logée dans la rainure, dont les deux bouts l'arrêtent. La tablette ne peut pas non plus avancer vers la "
            "pièce. La cheville arrière, elle, n'est arrêtée par rien : chargée, le frottement la tient (≈ 0,2 à 0,6 "
            "fois l'effort, des dizaines de kilos) ; sur une tablette vide ou qu'on cogne, elle pourrait sortir de 1,5 "
            "et la tablette basculer de ce côté. Parade : un ajustement serré (la cheville entre au maillet, sortie "
            "avec un chasse-goupille), vérifié sur le gabarit ; ou un tour de gaine thermorétractable noire sur la "
            "partie dans le montant.",
            "<b>Les trous sont près des faces du montant.</b> L'Eurocode 5 demande au moins 3 d (30) entre une broche "
            f"et le bord du bois ; ici {f(MO['x_ar'] * 10)} côté mur et {f((MO['p'] - MO['x_av']) * 10)} côté pièce. "
            f"L'entraxe dans une colonne ({MO['pas_trous'] * 10} = 5 d) et entre les colonnes ({f(ARR * 10)} = 3 d) est "
            "juste conforme. Les efforts sont faibles, mais le risque est la fente du montant le long d'une colonne de "
            "trous, au perçage ou sur un nœud : percer à la mèche à pointe de centrage avec un martyr, refuser un "
            "tasseau à nœuds dans la zone percée. Un montant de 44 × 95 (Leroy Merlin) remettrait les pinces aux "
            "normes (trous à 3 et 6,5 du mur) et allongerait le levier de la cheville arrière "
            f"({cm(3.5)} au lieu de {f(ARR)}, −15 % d'effort) : à décider."])
        + "<h3>Fixation au mur</h3>"
        + tenue_dispo(e)
        + "<p>C'est la cloison ouest (cellier et WC) qui porte tout, comme pour les variantes Vitsoe et fait maison de "
        f'la <a href="{FIXATIONS}">page Fixations</a> : sa nature décide de la quincaillerie. Repère : une cheville '
        "fischer DuoPower 8 × 40 est donnée pour 62 kg en brique pleine, 15 kg en plaque de plâtre de 12,5 et ≈ 0,25 kN "
        "en carreau de plâtre (fiche fischer, sécurité de 7 comprise ; la colonne du carreau de plâtre est lue dans "
        f"l'ordre des tailles, à confirmer). Au pire, la vis du haut reçoit ≈ {kn(fx['r'])} kN.</p>"
        + _liste([
            f"<b>Brique ou béton</b> : {EU['vis']} vis Ø 6 × 120 par montant (à 5, 60 et 115 du bas, par la face avant), "
            "chevilles nylon 8 × 50, têtes noyées dans un lamage Ø 15 bouché et peint : large.",
            f"<b>Carreau de plâtre</b> : la vis du haut est à la charge recommandée. Passer à {EU['vis'] + 1} vis par "
            "montant (une de plus en haut, à 100), avec des chevilles de 10 (≈ 0,35 kN en carreau de plâtre chez "
            "fischer) ou des chevilles spéciales carreau de plâtre.",
            "<b>Plaque de plâtre sur ossature</b> : les rails sont à 60 ; passer le pas à 60 pour visser chaque "
            "montant dans un rail (débords ramenés à ≈ 9 aux deux bouts, tablettes plus longues), ou renforcer la "
            "cloison. Des chevilles dans la plaque seule : non.",
            "<b>Réseaux</b> : repérer les gaines du mur ouest avant de percer (détecteur), surtout côté WC."])
        + note_source("Sources consultées le 30/10/2026 :")
        + _liste(src)
        + note_source(
            "Non trouvé en ligne et pris de mémoire, à vérifier : kmod et γM de l'Eurocode 5, nuance de l'acier des "
            "ronds Weldom (supposé S235), classe du sapin Weldom (non classé, pris en C18). L'essai de charge du "
            "montage (chute de tablette, deux chevilles, 15 kg pendant une semaine) reste la vérification qui compte."))


# ------------------------------------------------------------------ à vérifier sur place (ET:1081-1094)
def _a_verifier(e):
    return a_verifier([
        f"<b>Disposition</b> à choisir parmi les {len(calculs.CLES)} ; le plan du salon et les rendus montrent "
        "l'actuelle.",
        f"<b>Composition {escape(e.nom)}</b> : {len(e.ts)} tablettes ({escape(e.kit)}), {cm(e.metres)} m, dessus à "
        f"{', '.join(str(z) for z in e.niveaux)}.",
        f"<b>Rainures</b> : profondeur ({cm(RA['prof'] * 10)} mm à plat, {cm(PR['prof'] * 10)} pour un présentoir) et "
        "décalage des trous à essayer sur une chute avec le gabarit avant de rainurer les tablettes : la tablette doit "
        "se pincer sans jeu.",
        f"<b>Pas des montants</b> : {PAS} si la cloison est pleine (carreau de plâtre, brique) ; 60 si c'est une "
        "plaque sur ossature, pour visser dans les rails.",
        "<b>Nature de la cloison ouest</b> : à relever (sondage, étape 1 du montage) ; elle décide des chevilles.",
        f"<b>Sections réelles</b> : tasseaux Weldom {cm(TASSEAU['s'][0])} × {cm(TASSEAU['s'][1])} et plan Castorama de "
        f"{cm(PANNEAU['ep'])}, contre {cm(MO['l'])} × {MO['p']} et {cm(ET['ep'])} dans le modèle ; longueur réelle des "
        f"tasseaux (deux montants de {cm(L_MONTANT)} dans {cm(TASSEAU['l'])}).",
        "<b>Stock et prix</b> en magasin (Weldom d'abord), transport des plans de 250.",
    ])


REMARQUE = ("Repère : origine au coin nord-ouest du salon, y vers le sud, z depuis le sol, cotes en cm. Dimensions : "
            "pieces/salon/etageres/document.py (DISPOSITIONS). Le reste du salon : "
            f'<a href="{SALON}">plan du salon</a>.')


def explication(e) -> str:
    return (_tete(e) + _chiffres(e) + _dispositions(e) + _mecanisme() + _presentoir(e) + _rendus(e) + _materiaux()
            + _tenue(e) + _a_verifier(e) + note_source(REMARQUE))
