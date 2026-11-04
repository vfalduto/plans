# Comparatif des quatre niveaux du meuble bas, lu par niveaux.py (contrat : ID, TITRE, section() → HTML sans le h2).
# Notes indépendantes : ce module lit les niveaux et ne les modifie pas. Les coûts sont ramenés à un périmètre unique (AJOUTS) ;
# la note de coût suit l'ancre appliquée au coût corrigé. Notes et raisons sont des données, les chiffres sont lus dans les modules.
#
# Estimations propres à ce module : gabarits, port, volume utile du panier du niveau 3, temps du niveau 4, prix du mélange.

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modele as M  # noqa: E402
import plan as PL  # noqa: E402
import niv_commun as NC  # noqa: E402
import niv_1 as N1  # noqa: E402
import niv_2 as N2  # noqa: E402
import niv_3 as N3  # noqa: E402
import niv_4 as N4  # noqa: E402

ID = "comparatif"
TITRE = "Les quatre niveaux en un coup d'œil"

cm = PL.cm
NIVEAUX = {1: N1, 2: N2, 3: N3, 4: N4}
CRITERES = ("cout", "difficulte", "praticite", "design")
LIBELLES = dict(cout="Coût", difficulte="Difficulté", praticite="Praticité", design="Design")


def euros(x):
    """Montant au centime, avec l'espace des milliers."""
    return PL.euros(x).replace(f"{int(x)}", f"{int(x):,}".replace(",", "\u00a0"), 1)


def _e(x):
    """Montant arrondi à l'euro, pour la lecture."""
    return f"{round(x):,}".replace(",", " ") + " €"


def _ligne(mod, debut):
    """Montant d'une ligne de chiffrage, trouvée par le début de son libellé."""
    l = next(l for l in mod.FICHE["lignes"] if l["libelle"].startswith(debut))
    return round(l["qte"] * l["pu"], 2)


# ------------------------------------------------------------------ périmètre unique
# Le meuble bas complet : plan et vernis, prises et leur matériel, vis, pots entiers, plaque anti-vibrations, port, outils à
# acheter. Hors périmètre, à tous les niveaux : caisson haut, machine, plomberie, électricien, et les outils d'un bricolage
# courant (pinceau, ponceuse, serre-joints).
_PLAQUE = M.WELDOM["tapis"][1]                  # comptée au meuble actuel, écartée par les quatre niveaux
_CHEVILLES = M.WELDOM["cheville"][0][1]
_CABLE = _ligne(N2, "Câble")                    # même point d'arrivée pour tous : 5 m
_FRAISE = _ligne(N3, "Fraise")
_ABRASIFS = _ligne(N3, "Abrasifs")
_CLOCHE = _ligne(N4, "Scie cloche")
_FORET = _ligne(N4, "Foret diamant")
_GABARIT_TOURILLON = 20.0                       # estimé
_GABARIT_BLUM = 20.0                            # estimé : le gabarit de perçage figure dans la notice Blum, prix non lu
_PORT_PRISES = 10.0                             # estimé : une commande d'appareillage en ligne

_P = ("Plaque anti-vibrations de la machine", _PLAQUE, "relevé")
_C = ("Câble 5 m", _CABLE, "estimé")
AJOUTS = {
    1: [_P, ("Câble porté de 3 à 5 m, comme au niveau 2", round(_CABLE - _ligne(N1, "Câble"), 2), "estimé"),
        ("Foret carrelage, listé dans ses outils", _FORET, "estimé"), ("Abrasifs", _ABRASIFS, "estimé")],
    2: [_P, ("Chevilles des cadres de prises", _CHEVILLES, "relevé"), ("Foret carrelage", _FORET, "estimé"),
        ("Fraise droite Ø 8", _FRAISE, "estimé"), ("Abrasifs", _ABRASIFS, "estimé"),
        ("Port de l'appareillage en ligne", _PORT_PRISES, "estimé")],
    3: [_P, _C, ("Scie cloche pour l'encastrement, comptée au niveau 4", _CLOCHE, "relevé"), ("Foret diamant", _FORET, "estimé"),
        ("Gabarit de tourillonnage", _GABARIT_TOURILLON, "estimé"), ("Port de la plaque et des prises", _PORT_PRISES, "estimé")],
    4: [_P, _C, ("Fraise pour la feuillure des traverses", _FRAISE, "estimé"), ("Gabarit de perçage Blum", _GABARIT_BLUM, "estimé")],
}


def annonce(n):
    return NC.cout(NIVEAUX[n].FICHE)


def corrige(n):
    return round(annonce(n) + sum(a[1] for a in AJOUTS[n]), 2)


def part_estimee(n):
    """Part du coût corrigé qui repose sur un prix estimé, non relevé."""
    e = sum(l["qte"] * l["pu"] for l in NIVEAUX[n].FICHE["lignes"] if l["statut"] == "estimé")
    e += sum(a[1] for a in AJOUTS[n] if a[2] == "estimé")
    return e / corrige(n)


def ancre_cout(x):
    return 5 if x <= 250 else 4 if x <= 400 else 3 if x <= 650 else 2 if x <= 1000 else 1


# ------------------------------------------------------------------ faits lus dans les modules, sur une même base
VOLUME_ACTUEL = M.VOLUME_BAC                    # un sac du meuble actuel
OUVERTURE_ACTUELLE = M.BAC["ouverture"]         # porte basculante à 20°
# Le niveau 3 annonce son volume hors tout ; volume utile : parois de 1 cm, fond de 1 cm, doublure ≈ 1,5 L (estimé).
UTILE_N3 = round((N3.PANIER["l"] - 2) * (N3.PANIER["p"] - 2) * (N3.PANIER["h"] - 1) / 1000 - 1.5)
LINGE_N3 = UTILE_N3 * N3.DENSITE_LINGE
# Bouche du niveau 1 mesurée au corps du panier, comme aux autres niveaux : le module la mesure au bord extérieur du rebord.
BOUCHE_N1 = N1.OUV_HAUT - N1.PANIER["rebord"]
PRISES_N3 = _ligne(N3, "Plaque Legrand") + _ligne(N3, "Prise 2P+T") + _ligne(N3, "Support Batibox") + _CLOCHE + _FORET
PORTE_ENTREE = {1: N1.ANG_PORTE, 2: math.degrees(math.atan2(N2.Y_R0, NC.X_PORTE - (N2.X_PF - N2.S_BUTEE))),
                3: N3.ANGLE_ENTREE, 4: N4.A_ENTREE}
TEMPS_N4 = (35, 50)                             # estimé : une menuiserie comparable au niveau 3, moins les rainures, plus Blum

# ------------------------------------------------------------------ notes et raisons
NOTES = {
    1: dict(
        cout=(4, f"{_e(corrige(1))} corrigés : les {_e(annonce(1))} annoncés passaient sous 250 € sans la plaque de la machine, le foret carrelage et les abrasifs."),
        difficulte=(4, f"Coupes droites et vissage en {N1.FICHE['heures'][0]} à {N1.FICHE['heures'][1]} h ; seule la refente des traverses demande de tomber entre {cm(N1.T_MIN * 10)} et {cm(N1.T_MAX * 10)} mm, et la rater coûte un tasseau à 6,10 €."),
        praticite=(2, f"Chaque vidage demande de fermer deux portes, de décrocher une cordelette {cm(N1.X_MUR - N1.SORTIE - M.FACE)} cm sous le plan, puis de porter {cm(N1.M_PLEIN)} kg par un rebord de 15 mm (estimé), dans une boîte qui frotte et n'aère pas."),
        design=(1, "Le plastique transparent montre le linge sale entre des tasseaux à nœuds et têtes de vis apparentes, avec un bloc de prises et une moulure en PVC blanc sur le carrelage."),
    ),
    2: dict(
        cout=(4, f"{_e(corrige(2))} corrigés contre {_e(annonce(2))} annoncés ; {_e(2 * (N2.PANIER['prix'] - 6.92))} de moins si les paniers sont en rayon chez Action à 6,92 €."),
        difficulte=(3, f"Rainures à la défonceuse et rail à {cm(N2.JEU_GUIDE * 10)} mm de jeu, à régler sur un rebord encore estimé ; la tablette de mélaminé coûte 16,50 €, donc un raté se rattrape."),
        praticite=(3, f"À la butée, la bouche de {cm(N2.BOUCHE_L)} × {cm(N2.BOUCHE_B)} cm n'ouvre pas plus que les {cm(OUVERTURE_ACTUELLE)} cm de la porte actuelle à 20° : il faut appuyer sur la poignée pour passer à {cm(N2.BOUCHE_LG)} cm, mais une pièce se jette sans tirer, en haut comme en bas."),
        design=(3, f"Mélaminé blanc et tricot crème, sans vis de face : c'est propre et discret, mais le linge se devine par les jours et rien ne répond au chêne du plan."),
    ),
    3: dict(
        cout=(2, f"{_e(corrige(3))} corrigés contre {_e(annonce(3))} annoncés : les prises encastrées et leur outillage pèsent à eux seuls {_e(PRISES_N3)}."),
        difficulte=(2, f"Chêne visible partout, rainures à régler sur l'épaisseur réelle, tourillons apparents, {N3.N_TABLETTES} tablettes à {euros(N3.TAB['prix'])} sans marge de débit et {N3.FICHE['heures'][0]} à {N3.FICHE['heures'][1]} h, plus des doublures à coudre sans machine dans son équipement."),
        praticite=(3, f"Tiré à fond, le panier est libre et la doublure à anses se vide d'un geste, mais il tient ≈ {UTILE_N3} L utiles (estimé), moins que les {M.VOLUME_BAC:.0f} L d'un sac actuel, et la poignée du bas est à {cm(N3.Z_PT[0] + N3.H_POIGNEE)} cm du sol."),
        design=(4, f"Chêne verni partout, rotin blond et toile unie, sans plastique ; il reste {cm(N3.YI1 - N3.YI0 - N3.PANIER['l'])} cm de vide en largeur autour de chaque panier et le poteau de {cm(N3.H_POTEAU)} cm à la vue."),
    ),
    4: dict(
        cout=(1, f"{_e(corrige(4))} corrigés contre {_e(annonce(4))} annoncés, soit {_e(corrige(4) - 1000)} au-dessus du seuil de 1 000 € avec {part_estimee(4) * 100:.0f} % d'estimé : la note est fragile, le prix du panier Elfa peut la faire remonter à 2."),
        difficulte=(2, f"Une planche à 119 € sans droit à l'erreur pour des façades à fil continu et joints de 3 mm, des côtés de 18 mm là où Blum en admet 16, et trois carottages Ø 68 dans le carrelage."),
        praticite=(4, f"Bouche entière de {cm(N4.PANIER['corps_l'])} × {cm(N4.PANIER['corps_p'])} cm, {N4.LITRES:.0f} L estimés par panier, sortie amortie sans toucher à l'autre ; la gêne : rien ne se jette tiroir fermé et 2 vis au mur reviennent sur le choix d'un meuble non fixé."),
        design=(5, f"Un seul panneau de chêne pleine lame sans aboutage, façades à fil continu sans poignée, joints de 3 mm : ni linge, ni coulisse, ni plastique à la vue tiroirs fermés."),
    ),
}

for _n, _nt in NOTES.items():
    assert set(_nt) == set(CRITERES)
    assert all(v[0] in (1, 2, 3, 4, 5) and v[1] for v in _nt.values())
    assert _nt["cout"][0] == ancre_cout(corrige(_n)), f"niveau {_n} : la note de coût suit l'ancre"

# ------------------------------------------------------------------ le mélange : caisson du niveau 2, coulisses et paniers du niveau 4
MIX = [("le niveau 2 corrigé", corrige(2)),
       ("moins ses paniers", -_ligne(N2, "Panier Curver")),
       ("coulisses, attaches et axes Blum", _ligne(N4, "Paire de coulisses") + _ligne(N4, "Attache") + _ligne(N4, "Axe")),
       ("gabarit de perçage", _GABARIT_BLUM),
       ("paniers Elfa", _ligne(N4, "Panier filet")),
       ("port Blum et Elfa (estimé)", 30.0),
       ("colle et troisième tablette de mélaminé", _ligne(N3, "Colle") + M.PANNEAUX["M18"][0]["prix"])]
PRIX_MIX = round(sum(m[1] for m in MIX), 2)
NOTES_MIX = dict(cout=ancre_cout(PRIX_MIX), difficulte=3, praticite=4, design=4)
assert NOTES_MIX["cout"] == 3
# Les façades de 18 sortent de la tablette du plan et le pot de 0,75 L suffit
_LONG_MIX = NC.PLAN.y1 - NC.PLAN.y0 + 2 * N4.H_F + 0.6
assert _LONG_MIX <= M.PANNEAUX["D"][0]["L"] / 10 and N4.YF[1] - N4.YF[0] <= M.PANNEAUX["D"][0]["l"] / 10
_M2_FACADES = 2 * (2 * (N4.YF[1] - N4.YF[0]) * N4.H_F + 2 * (N4.YF[1] - N4.YF[0] + N4.H_F) * 1.8) / 1e4
_LITRES_MIX = M.VERNIS["litres"] + _M2_FACADES * M.VERNIS["couches"] / M.VERNIS["rendement"]
assert _LITRES_MIX <= 0.75
# Avec une façade de 18 au lieu de 20, le rebord sorti dégage mieux le nu du plan
_DEGAGE_MIX = M.FACE - (M.FACE + 1.8 + N4.PANIER["p"] - N4.COUL["course"])
assert _DEGAGE_MIX >= N4.DEGAGE
# Deux tiroirs pleins sortis et 30 kg sur une façade, ramenés sur le poteau du niveau 2 (masses du niveau 4, estimé)
POUSSEE_MIX = ((2 * N4.M_PLEIN * N4.BRAS_SORTI + N4.APPUI_ADULTE * N4.BRAS_APPUI - N4.M_STAB)
               / ((N2.POTEAU.x0 + N2.POTEAU.x1) / 2 - N4.X_PIED))

# ------------------------------------------------------------------ présentation
STYLE = """<style>
.cmp-synth th,.cmp-synth td{padding:6px 3px}
.cmp-synth th{font-size:11.5px;font-weight:600;color:var(--muted);line-height:1.2;vertical-align:bottom}
.cmp-synth td{vertical-align:middle;font-size:13px}
.cmp-empile td b.cmp-c{display:none}
@media (max-width:680px){
.cmp-empile thead{display:none}
.cmp-empile,.cmp-empile tbody,.cmp-empile tr,.cmp-empile td{display:block;width:auto}
.cmp-empile tr{border-bottom:2px solid var(--line);padding:6px 0}
.cmp-empile td{border:0;padding:4px 0;text-align:left;white-space:normal}
.cmp-empile td b.cmp-c{display:inline}
}
</style>"""


def _points(n):
    """Une note : le chiffre, et dessous cinq petits carrés dont n sont pleins."""
    cases = "".join(f'<span style="display:block;width:6px;height:6px;border-radius:1px;'
                    f'background:{"var(--wood)" if i < n else "transparent"};'
                    f'border:1px solid {"var(--wood)" if i < n else "var(--line)"}"></span>' for i in range(5))
    return (f'<span style="display:inline-block" title="{n} sur 5"><b style="display:block;font-size:15px;line-height:1.2;'
            f'color:var(--ink)">{n}</b><span style="display:flex;gap:1px;margin-top:2px">{cases}</span></span>')


def _nom(n):
    f = NIVEAUX[n].FICHE
    return f'<a href="#{NIVEAUX[n].ID}">{n} · {f["nom"]}</a>'


def _synthese():
    tete = "".join(f"<th>{LIBELLES[c]} /5</th>" for c in CRITERES)
    lignes = ""
    for n in NOTES:
        h = NIVEAUX[n].FICHE["heures"]
        notes = "".join(f"<td>{_points(NOTES[n][c][0])}</td>" for c in CRITERES)
        lignes += (f'<tr><td>{_nom(n)}</td><td class="num" style="font-size:12.5px">{_e(corrige(n))}</td>{notes}'
                   f'<td>{h[0]} à {h[1]}&nbsp;h{"*" if n == 4 else ""}</td></tr>')
    return (f'<table class="cmp-synth"><thead><tr><th>Niveau</th><th class="num" style="font-family:inherit;white-space:normal">Coût<br>corrigé</th>{tete}<th>Temps</th></tr></thead>'
            f'<tbody>{lignes}</tbody></table>'
            f'<p class="note">Note de 1 à 5, 5 étant le plus favorable (pour la difficulté, le plus facile). Les notes ne s\'additionnent pas : '
            f'les critères ne se valent pas. Coût : 5 jusqu\'à 250 €, 4 jusqu\'à 400 €, 3 jusqu\'à 650 €, 2 jusqu\'à 1 000 €, 1 au-delà, '
            f'plan compris. Temps annoncé par chaque niveau, tous estimés. * Les {N4.FICHE["heures"][0]} à {N4.FICHE["heures"][1]} h du niveau 4 '
            f'me semblent courtes à côté des {N3.FICHE["heures"][0]} à {N3.FICHE["heures"][1]} h du niveau 3, pour autant de chêne à vernir : '
            f'plutôt {TEMPS_N4[0]} à {TEMPS_N4[1]} h (estimé).</p>')


def _raisons():
    tete = "".join(f"<th>{LIBELLES[c]}</th>" for c in CRITERES)
    lignes = ""
    for n in NOTES:
        cases = "".join(f'<td><b class="cmp-c">{LIBELLES[c]} : </b><b>{NOTES[n][c][0]}.</b> {NOTES[n][c][1]}</td>' for c in CRITERES)
        lignes += f"<tr><td><b>{_nom(n)}</b></td>{cases}</tr>"
    return (f'<table class="cmp-empile"><thead><tr><th>Niveau</th>{tete}</tr></thead><tbody>{lignes}</tbody></table>'
            f'<p class="note">Pour situer : le meuble actuel a deux sacs liés de {M.VOLUME_BAC:.0f} L chacun et s\'ouvre de {cm(OUVERTURE_ACTUELLE)} cm à 20°. '
            f'Par panier, utile : {N1.PANIER["litres"]} L au niveau 1, {N2.PANIER["litres"]} L au niveau 2, ≈ {UTILE_N3} L au niveau 3, '
            f'{N4.LITRES:.0f} L au niveau 4. Bouche à l\'arrêt normal, mesurée au corps du panier : {cm(N1.OUV_L)} × {cm(BOUCHE_N1)}, '
            f'{cm(N2.BOUCHE_L)} × {cm(N2.BOUCHE_B)}, {cm(N3.PANIER["l"] - 2)} × {cm(N3.PANIER["p"] - 2)}, {cm(N4.PANIER["corps_l"])} × {cm(N4.PANIER["corps_p"])} cm. '
            f'Les paniers sont indépendants aux quatre niveaux. Les poids de linge reposent sur 0,12 kg par litre (estimé).</p>')


def _recommandation():
    m = NOTES_MIX
    detail = ", ".join(f"{l} ({_e(abs(v))})" for l, v in MIX[2:])
    return f"""<p><b>Aucun des quatre tel quel : je prendrais un mélange</b>, à ≈ {_e(PRIX_MIX)} (estimé, pas dessiné). Le caisson en mélaminé et les prises en saillie du niveau 2, les coulisses cachées et les paniers grillagés du niveau 4, sans déclencheur, et deux façades en chêne coupées dans la tablette du plan : {cm(_LONG_MIX)} cm sur les 200 de la planche, et le pot de vernis suffit.</p>
<ul>
<li><b>Ce qu'il garde du niveau 4 :</b> les deux craintes sont réglées de la même façon, avec une bouche de {cm(N4.PANIER["corps_l"])} × {cm(N4.PANIER["corps_p"])} cm, {N4.LITRES:.0f} L par panier (estimé), une sortie amortie et un panier qui se lève tout droit.</li>
<li><b>Ce qu'il retire :</b> ≈ {_e(corrige(4) - PRIX_MIX)}, les trois carottages et les deux vis dans le mur. Le poteau du niveau 2 remplace les vis : ≈ {POUSSEE_MIX:.0f} kgf en compression dans le pire cas (estimé). On tire par une rainure de prise, faite à la défonceuse dans le haut de la façade.</li>
<li><b>Mes notes pour ce mélange :</b> coût {m["cout"]}, difficulté {m["difficulte"]}, praticité {m["praticite"]}, design {m["design"]}. Il bat le niveau 3 sur les quatre critères, et le niveau 4 sur le coût et la difficulté à praticité égale. Il ne lui cède que le design, car le panneau uni en pleine lame disparaît.</li>
<li><b>Le prix :</b> {_e(MIX[0][1])} pour le niveau 2 corrigé, moins ses paniers ({_e(abs(MIX[1][1]))}), plus {detail}. Il reste {_e(650 - PRIX_MIX)} sous le seuil de 650 €, et le prix du panier Elfa n'a pas été lu pour cette hauteur.</li>
<li><b>Sa vraie limite :</b> des côtés de 18 mm là où Blum en admet 16, comme au niveau 4. Je construirais d'abord un seul tiroir avec une paire de coulisses et un panier (≈ 100 €, estimé), avant de couper le reste.</li>
</ul>
<p><b>Selon ce qui est visé :</b></p>
<ul>
<li><b>Moins de 400 €, sans commande compliquée :</b> le niveau 2, à {_e(corrige(2))}. Il garde une pièce jetée sans tirer aux deux étages, ce qu'aucun tiroir ne permet. Avant de débiter, il faut un panier en main : la photo du produit montre des angles arrondis et un rebord en bourrelet, moins franc que les {cm(N2.PANIER["levre"] * 10)} mm estimés. Si le rebord ne porte pas, on change de panier ou de niveau.</li>
<li><b>Une pièce qui se montre :</b> le niveau 4, si {_e(corrige(4))} ne gêne pas et si le poteau ou les deux vis sont acceptés. C'est le seul niveau qui mérite le 5 en design.</li>
<li><b>Le niveau 1 :</b> seulement pour essayer l'idée quelques mois. Il économise {_e(corrige(2) - corrige(1))} sur le niveau 2 et perd sur la praticité et le design.</li>
<li><b>Le niveau 3 :</b> je ne le prendrais pas. Il coûte plus que le mélange et ses ≈ {2 * UTILE_N3} L au total font moins que les {M.VOLUME_CASE:.0f} L d'aujourd'hui. Seule une préférence nette pour le rotin et le bois sans métal ni plastique le justifie.</li>
</ul>
<p><b>Ce qui ferait changer d'avis :</b> un premier tiroir qui ne fonctionne pas avec ses côtés feuillurés, et je reviendrais au niveau 2. Pas de caisson haut chevillé, et aucun poteau n'est possible : il faudrait fixer le meuble au mur ou renoncer aux sorties complètes. L'envie de jeter une pièce sans rien ouvrir, si c'est le geste de tous les jours, et le niveau 2 passe devant le mélange.</p>"""


def _a_trancher():
    p = PORTE_ENTREE
    return f"""<ul>
<li><b>Porte de la machine, à mesurer.</b> Diamètre de {cm(NC.HUBLOT["d"])} cm, charnière et angle de {NC.HUBLOT["angle"]}° sont estimés partout. Aux quatre niveaux, à 90° elle fait un mur entre le panier sorti et le hublot : on sort le panier d'abord, on ouvre ensuite.</li>
<li><b>Panier en main avant de couper.</b> Rebord et corps ne sont pas relevés aux niveaux 1, 2 et 4, et les jeux se comptent en millimètres. À essayer chargé de 6 kg.</li>
<li><b>Caisson haut.</b> Le poteau qui empêche le meuble de basculer aux niveaux 1, 2 et 3 s'appuie dessous. Sans lui, {cm(N1.APPUI_MAX)} kg au niveau 1, {N2.APPUI:.0f} kg au niveau 2 et {cm(N3.APPUI_MAX)} kg au niveau 3 appuyés sur le bord sorti soulèvent l'arrière (estimé, coins de calage non comptés).</li>
<li><b>Prises, à voir avec l'électricien.</b> Elles sont à environ 126 cm du sol à tous les niveaux : Legrand et IZI by EDF donnent 130 cm au maximum, Engie donne ce chiffre comme un minimum. Restent aussi le point d'arrivée du câble, la nature du mur et le 30 mA. Au niveau 1, il faut vérifier que le bloc se raccorde à un câble fixe : il est rangé parmi les multiprises.</li>
<li><b>Porte d'entrée, à accepter.</b> Un panier sorti l'arrête après ≈ {p[1]:.0f}° au niveau 1, ≈ {p[2]:.0f}° au niveau 2, ≈ {p[3]:.0f}° au niveau 3 et moins de {math.ceil(p[4])}° au niveau 4. Personne n'entre tant qu'il n'est pas repoussé.</li>
<li><b>« Posé sur deux traverses », à trancher.</b> Au niveau 3, le panier est posé sur un plateau, et c'est le plateau qui court dans les traverses. Au niveau 4 et dans le mélange, les traverses sont les côtés d'un tiroir. Si la demande se lit à la lettre, seuls les niveaux 1 et 2 la suivent.</li>
</ul>"""


def _perimetre():
    lignes = ""
    for n in NOTES:
        ajouts = " ; ".join(f"{a[0]} {euros(a[1])}" + (" (estimé)" if a[2] == "estimé" else "") for a in AJOUTS[n])
        lignes += (f'<tr><td><b>{_nom(n)}</b></td><td class="num"><b class="cmp-c">Annoncé : </b>{euros(annonce(n))}</td><td><b class="cmp-c">Ajouté : </b>{ajouts}</td>'
                   f'<td class="num"><b class="cmp-c">Corrigé : </b>{euros(corrige(n))}</td><td class="num"><b class="cmp-c">Écart : </b>+{euros(corrige(n) - annonce(n))}</td>'
                   f'<td class="num"><b class="cmp-c">Part estimée : </b>{part_estimee(n) * 100:.0f} %</td></tr>')
    return (f'<table class="cmp-empile"><thead><tr><th>Niveau</th><th class="num">Annoncé</th><th>Ajouté pour un même périmètre</th>'
            f'<th class="num">Corrigé</th><th class="num">Écart</th><th class="num">Part estimée</th></tr></thead><tbody>{lignes}</tbody></table>'
            f'<p class="note">Même périmètre : meuble bas complet avec plan et vernis, prises et leur matériel, vis, pots entiers, plaque anti-vibrations, port et outils à acheter. '
            f'Sans caisson haut, machine, plomberie ni électricien. Une machine à coudre, une ponceuse, des serre-joints et un pinceau sont supposés disponibles. '
            f'Non corrigé, car incertain : un petit pot de vernis en plus au niveau 1 si le sapin boit davantage (20,90 €). La part estimée est celle du coût corrigé dont le prix n\'a pas été relevé.</p>')


def section():
    return f"""{STYLE}
{_synthese()}

<h3>Les raisons de chaque note</h3>
{_raisons()}

<h3>Ce que je prendrais</h3>
{_recommandation()}

<h3>À trancher ou à mesurer avant d'acheter</h3>
{_a_trancher()}

<h3>Les prix ramenés à un même périmètre</h3>
{_perimetre()}"""


if __name__ == "__main__":
    for _n in NOTES:
        print(_n, annonce(_n), corrige(_n), f"{part_estimee(_n) * 100:.1f} %", {c: NOTES[_n][c][0] for c in CRITERES})
    print("mélange", PRIX_MIX, NOTES_MIX, f"long {_LONG_MIX:.1f} vernis {_LITRES_MIX:.2f} L poussée {POUSSEE_MIX:.0f} kgf dégagé {_DEGAGE_MIX:.1f}")
    print("portes", {k: round(v, 1) for k, v in PORTE_ENTREE.items()}, "utile n3", UTILE_N3, "prises n3", PRISES_N3)
