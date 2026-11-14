"""Explication du meuble bas : le chapô, les chiffres clés, la structure (placard, porte, pieds, tenue), la colonne de
prises, les mesures, les points à vérifier sur place et le repère.

Textes repris de l'ancienne page sdb-meuble-bas.html (V8.5), mêmes formules ; deux nombres mal écrits y sont corrigés
(« 2,5 GPa », « ≈ 4,1 kg »). Les points à vérifier ajoutés et les chiffres clés sont calculés depuis la pièce et le modèle.
"""
from html import escape

from commun.blocs import a_verifier, chiffres, nombre, note_source, tete, vue_lecture
from commun.modele import Vue
from pieces.sdb import piece as P
from pieces.sdb.achats_communs import prix
from pieces.sdb.meuble_bas import modele as B

cm = B.cm


def _structure() -> str:
    t = B.tenue()
    return ("<h2>Structure</h2>\n"
            + f"""<p><b>Trois joues pleines</b> de {B.cm(B.EP)} debout autour de la machine, un <b>fond</b>, un <b>bas</b> et une <b>étagère</b> entre les joues nord et milieu, le <b>plateau</b> posé directement sur le tout. Rien n'est vissé au mur. Joues, fond, bas, étagère et porte en mélaminé blanc, plateau en chêne.</p>
<ul>
<li><b>Devant-derrière.</b> Une joue est un panneau plein : elle ne peut pas se déformer dans son plan. Le mur du fond arrête le recul.</li>
<li><b>Nord-sud.</b> Le fond empêche le placard de se déformer : vissé aux joues nord et milieu, il fait un U qui tient debout seul. Le plateau y relie la joue sud, et il est pris entre les murs, à {B.cm(B.JEU_MUR)} de chaque côté.</li>
<li><b>Devant la machine.</b> Les joues s'arrêtent au nu de sa façade : sa porte passe devant elles. Le plateau dépasse de {B.cm(B.JX0 - B.PX0)}.</li>
<li><b>Derrière la machine.</b> Rien ne passe : les {B.JEU_FOND} restent libres pour les tuyaux, et une encoche de {P.PASSE["l"]} × {P.PASSE["p"]} à {B.cm(P.ROBINET["y"])} du mur nord laisse monter l'arrivée d'eau au robinet.</li>
<li><b>Tapis anti-vibration.</b> {escape(B.TAPIS["nom"])} recoupée à {B.TAPIS["p"]} de profondeur. Elle monte la machine de {B.cm(B.TAPIS["ep"])}, et ses {B.TAPIS["l"]} de large entrent entre les joues.</li>
</ul>"""
            + "\n<h3>Placard</h3>\n"
            + f"""<ul>
<li><b>Étages.</b> L'étagère coupe la hauteur en deux étages égaux de {B.cm(B.NIV_H)} : du bas à l'étagère, puis de l'étagère au plateau.</li>
<li><b>Bas.</b> {B.cm(B.BAIE)} × {B.cm(B.ETAGERE_P)}, à {B.cm(B.BZ0)} du sol comme les joues. Le bac du bas pose dessus, rien ne touche le sol sauf les vérins.</li>
<li><b>Limite des bacs.</b> 3/4 de {B.cm(B.NIV_H)}, soit {B.cm(B.BAC_MAX)} de haut au maximum.</li>
<li><b>Bacs.</b> Deux <a href="https://www.ikea.com/fr/fr/p/slibb-panier-a-linge-blanc-70612723/">paniers IKEA SLIBB</a> de {B.BAC["litres"]} L, {B.BAC["p"]} × {B.BAC["l"]} × {B.BAC["h"]}, en plastique souple avec 4 poignées. Ils laissent {B.cm(B.BY0 - B.NY1)} de chaque côté et {B.cm(B.DX0 - B.BX1)} devant le fond, et ils montent à {B.cm(B.BAC["h"] / B.NIV_H * 100)} % de l'étage.</li>
<li><b>Étagère.</b> Mêmes dimensions que le bas. Les deux sont en retrait de {B.cm(B.EX0 - B.JX0)} sur le plan des joues, pour que la porte ferme sans y toucher.</li>
<li><b>Fond.</b> {B.cm(B.JOUE_H)} × {B.cm(B.BAIE)}, levé à {B.cm(B.JZ0)} du sol comme les joues, entre elles et au nu de leur arrière.</li>
<li><b>Assemblage.</b> {B.VIS_PANNEAU} vis 4 × 40 à chaque bout du fond, du bas et de l'étagère, à travers les joues, avant perçage Ø 2,5 et tête fraisée : ces têtes restent cachées, contre le mur côté nord et contre la machine côté milieu. {B.VIS_PANNEAU} vis de plus à travers le fond dans l'arrière du bas et de l'étagère.</li>
</ul>"""
            + "\n<h3>Porte</h3>\n"
            + f"""<ul>
<li><b>Dimensions.</b> {B.cm(B.PORTE_H)} × {B.cm(B.PORTE_L)}, en applique devant les joues nord et milieu, comme un meuble IKEA, avec {B.cm(B.JEU_PORTE)} de jeu autour. Sa face avant arrive au nu du plateau.</li>
<li><b>Découpes en U.</b> Une par étage, de {B.cm(B.FEN_L)} de large et {B.cm(B.FEN_H)} de haut, à fond arrondi. Le point le plus bas est à 3/4 de l'étage : à {B.cm(B.FENETRES[0][2])} et à {B.cm(B.FENETRES[1][2])} du sol. On jette le linge porte fermée, il tombe dans le bac placé dessous.</li>
<li><b>En haut.</b> La découpe est une encoche ouverte sur le bord de la porte : plus de bois au-dessus, et il reste 2 cornes de {B.MONTANT} × {B.cm(B.FEN_H)}. C'est le point fragile de la porte, à ne pas prendre pour attraper.</li>
<li><b>En bas.</b> La découpe reste fermée : l'ouvrir vers le haut couperait la porte en deux. Il reste {B.cm(B.EZ0 - B.FENETRES[0][3])} entre son haut et le dessous de l'étagère.</li>
<li><b>Bois gardé.</b> {B.MONTANT} de chaque côté des découpes, et {B.cm(B.FENETRES[1][2] - B.FENETRES[0][3])} entre les deux.</li>
<li><b>Découpe.</b> Fond arrondi à {B.cm(B.FEN_R)}, angles hauts de la découpe fermée à {B.cm(B.FEN_RH)} : percer un trou dans chaque angle fermé, couper à la scie sauteuse, adhésif de masquage sur le tracé. Plaquer le chant sur tout le tour pour que rien n'accroche.</li>
<li><b>Charnières.</b> 2 <a href="https://www.ikea.com/fr/fr/p/utrusta-charn-a-amort-integre-cuisine-80524882/">IKEA UTRUSTA {B.CHARNIERE["angle"]}°</a> amorties, côté mur nord, à {B.CHARN_Z[0]} et {B.CHARN_Z[1]} du sol. La haute reste sous la découpe. Cuvette Ø {B.cm(B.CUVETTE * 10)} mm à percer dans la porte, plaque vissée sur la joue nord. Cotes de perçage à reprendre sur la notice IKEA avant de percer : les caissons METOD sont percés d'usine, pas nos joues.</li>
<li><b>Poignée.</b> <a href="https://www.ikea.com/fr/fr/p/billsbro-poignee-blanc-50334303/">IKEA BILLSBRO blanc</a> de {B.POIGNEE["L"]}, à droite, dans le montant côté machine, entre les deux découpes, de {B.POI_Z0} à {B.POI_Z1} du sol. Elle convient aux portes de 16 à 19 mm. Le lot en contient 2, une seule sert.</li>
<li><b>Ouverture.</b> Porte d'entrée fermée, la porte du placard s'ouvre à environ {B.OUVERTURE}°, estimation à vérifier sur place : la poignée arrive contre la porte d'entrée. Les bacs sortent alors tout droit. <b>Porte d'entrée ouverte à 90°, elle ne s'ouvre que d'environ {B.ANGLE_VANTAIL:.0f}°</b> : le vantail n'est qu'à {B.cm(B.DEVANT_PORTE)} devant elle. Il faut donc fermer la porte d'entrée pour sortir un bac, pas pour jeter du linge.</li>
<li><b>Porte de la machine.</b> Elle s'ouvre vers le placard, et la poignée dépasse maintenant de {B.cm(B.JX0 - B.PORTE_X0 + B.POIGNEE["saillie"])} devant les joues. Son angle maximal n'a pas été relevé : à vérifier avant de percer pour la poignée.</li>
</ul>"""
            + "\n<h3>Pieds</h3>\n"
            + f"""<p>Le mélaminé ne touche jamais le sol. Sous chaque joue, <b>{B.VERIN["n"]} vérins réglables</b> encastrés dans le chant du bas, à {B.cm(B.VERINS_X[0] - B.JX0)} de chaque bord. Le fond, le bas et la porte restent suspendus, sans pied.</p>
<ul>
<li><b>Hauteur.</b> Le bas des joues est à {B.cm(B.JZ0)} du sol. Le vérin se règle de {B.cm(B.VERIN["cmin"])} à {B.cm(B.VERIN["cmax"])}, ce qui rattrape aussi un sol qui n'est pas droit.</li>
<li><b>Étanchéité.</b> Le trou de chaque vérin est garni de colle MS. Le chant du bas des joues, du fond et de la porte en est enduit : le mélaminé n'est pas hydrofuge, et son aggloméré gonfle à l'eau.</li>
<li><b>Écoulement.</b> Seuls les embouts plastique touchent le sol : l'eau et la serpillère passent dessous. On ne pose pas de joint au pied, il retiendrait l'eau.</li>
<li><b>Point à tester.</b> Le trou de {B.cm(B.VERIN["perce"] * 10)} mm laisse {B.cm((B.EP - B.VERIN["perce"]) / 2 * 10)} mm d'aggloméré de chaque côté : faire un essai sur une chute de tablette avant de percer les joues.</li>
</ul>"""
            + "\n<h3>Tenue</h3>\n"
            + f"""<div class="defile"><table><thead><tr><th>Contrôle</th><th class="num">Valeur</th></tr></thead><tbody>
<tr><td>Flèche du plateau sur la machine, 100 kg au milieu</td><td class="num">{B.cm(t["fleche"])} mm</td></tr>
<tr><td>Contrainte dans le plateau, même charge</td><td class="num">{B.cm(t["contrainte"])} MPa</td></tr>
<tr><td>Flèche de l'étagère, {B.LINGE} kg de linge répartis</td><td class="num">{B.cm(t["fleche_e"])} mm</td></tr>
<tr><td>Marge au basculement, 100 kg sur le bord avant</td><td class="num">× {B.cm(t["marge"])}</td></tr>
</tbody></table></div>"""
            + note_source(f"""{B.N_EQUERRES} équerres suffisent parce qu'elles ne portent pas : le plateau pose à plat sur les joues. Ordres de grandeur : chêne à {B.E_CHENE / 1e9:.0f} GPa et {B.RHO_CHENE} kg/m³, aggloméré à {nombre(B.E_AGGLO / 1e9)} GPa et {B.RHO_AGGLO} kg/m³, valeurs courantes non mesurées. Les vis dans le chant de l'aggloméré ne sont pas calculées : à éprouver à la main avant de rentrer la machine. Masse du meuble ≈ {t["masse"]:.0f} kg, dont ≈ {B.cm(t["porte"])} kg pour la porte."""))


def _colonne() -> str:
    z = [cm(x) for x in B.PRISES_Z]
    return ("<h2>Colonne de prises</h2>\n"
            + """<p>Un seul panneau de mélaminé qui coupe l'angle du mur du fond et du mur nord à 45°, posé sur le plateau et vissé au meuble haut. Rien n'est percé dans le carrelage.</p>"""
            + "\n"
            + f"""<ul>
<li><b>Panneau.</b> {B.cm(B.COL_L)} de large et {B.cm(B.COL_H)} de haut, chants longs biseautés à 45° à la scie circulaire. Il prend {B.cm(B.COL_JAMBE)} sur chaque mur, et les murs ferment le triangle. Il sort de la chute de la tablette du fond.</li>
<li><b>Prises.</b> 3 prises libres sur la face en diagonale, à {z[0]}, {z[1]} et {z[2]} du sol. Elles regardent vers la pièce et restent à {B.cm(P.ROBINET["y"] - B.COL_B[1])} du robinet.</li>
<li><b>LED.</b> Le kit se branche sur un transformateur. Il a son propre poste, à {B.PRISE_LED_Z} du sol, pour que les 3 autres restent libres. Son fil entre par un trou de Ø 1 juste au-dessus, monte derrière le panneau, sort par une encoche en haut côté mur nord, et file sous le meuble haut jusqu'au profil LED : ≈ {B.COL_C[0] - B.LED_X + B.Z_HAUT - B.PRISE_LED_Z:.0f} cm. Longueur du fil du kit et présence de l'interrupteur à vérifier sur la boîte : la fiche lue est celle d'une référence voisine.</li>
<li><b>Alimentation.</b> Le courant arrive en bas du mur nord, derrière la joue nord. Le câble traverse la joue, longe sa face intérieure en goulotte jusqu'à l'angle arrière, passe par une entaille de {B.GOUL} × {B.GOUL} dans l'étagère et par un trou Ø {B.cm(B.COL_TROU["d"] * 10)} mm dans le plateau, caché par la colonne. Le circuit, protégé en 30 mA, et le raccordement sont pour l'électricien. La machine garde sa prise à part, sur son circuit de 20 A.</li>
<li><b>À relever.</b> La hauteur de la sortie et sa distance au mur du fond. Dessin fait avec {B.ARRIVEE["z"]} du sol et {B.cm(P.X1 - B.ARRIVEE["x"])} du fond, à titre d'exemple. Le trajet reste valable si la sortie est au-dessus du bas du placard, à plus de {B.cm(B.BZ1)} du sol. Si une boîte dépasse du mur de plus de {B.cm(B.JEU_MUR)}, il faut aussi la dégager dans la joue.</li>
<li><b>Point à tester.</b> Les griffes de la boîte Batibox sont prévues pour les cloisons : faire un essai sur une chute de 18 avant de percer le panneau à Ø {B.cm(B.BOITE["d"] * 10)} mm.</li>
<li><b>Tenue.</b> Le panneau n'est tenu qu'à ses deux bouts, par {len(B.COL_VIS)} vis à chacun. Un cordon qu'on tire ne le sollicite pas beaucoup, mais à éprouver à la main avant de brancher.</li>
</ul>""")


def _mesures() -> str:
    relevees = [
        ("Plafond", f"{P.H}", "Confirmé par le client"),
        ("Mur du fond, de nord à sud", cm(P.Y1 - P.Y0), "Relevé client"),
        ("Mur de retour nord", f'{P.ALCOVE["nord"]}', "Relevé client"),
        ("Mur de retour sud", f'{P.ALCOVE["sud"]}', "Relevé client"),
        ("Gonds de la porte d'entrée, depuis le mur du fond", f"{P.GONDS}", "Relevé client"),
        ("Largeur de la porte d'entrée", f'{P.PORTE["l"]}', "Porte standard, d'après le client"),
        ("Chambranle, saillie sur le mur nord", cm(P.CHAMBRANLE), "Relevé client"),
        ("Carrelage, hauteur", f"{P.CARRELAGE}", "Relevé client"),
        ("Machine, largeur × profondeur × hauteur", f'{B.cm(P.MACHINE["l"])} × {B.cm(P.MACHINE["p"])} × {B.cm(P.MACHINE["h"])}', "Relevé client"),
    ]
    reprises = [
        ("Machine, côté", "à droite, au sud", "Choix du client depuis la V3.8"),
        ("Porte de la machine", "s'ouvre à gauche", "Validé par le client ; débattement non relevé"),
        ("Machine, jeu derrière", cm(B.JEU_FOND), "Reprise de la V6.2, pour les coudes des tuyaux"),
        ("Machine, distance au mur sud", cm(B.JEU_SUD), f"Joue de {B.cm(B.EP)} + {B.JEU_MACHINE} de jeu + {B.cm(B.JEU_MUR)} au mur"),
        ("Tapis sous la machine, épaisseur", cm(B.TAPIS["ep"]), "Plaque Noma Rub, épaisseur de la fiche Weldom"),
        ("Plateau, profondeur", f"{B.PLATEAU_P}", "Demande du client"),
        ("Siphon d'évacuation, à " + cm(P.ROBINET["y"]) + " du mur nord", f'{P.TUYAUX["evacuation_z"]} de haut', "Position de la V6.0, à vérifier sur place"),
        ("Arrivée d'eau, même axe", f'{P.TUYAUX["arrivee_z"]} de haut', "Position de la V6.0, à vérifier sur place"),
        ("Robinet d'arrêt, même axe", f'{P.ROBINET["z"]} de haut', "Position de la V5.7, à recaler sur le nouveau plateau"),
        ("Dessous du meuble haut", f"{B.Z_HAUT}", f"Page du meuble haut {B.VERSION_HAUT}"),
    ]

    def table(lignes):
        corps = "".join(f'<tr><td>{escape(n)}</td><td class="num">{escape(v)}</td><td>{escape(s)}</td></tr>' for n, v, s in lignes)
        return (f'<div class="defile"><table><thead><tr><th>Mesure</th><th class="num">Valeur</th><th>Origine</th></tr></thead>'
                f'<tbody>{corps}</tbody></table></div>')
    deduites = [
        ("Placard, largeur entre les joues nord et milieu", cm(B.BAIE)),
        ("Placard, profondeur des joues au fond", cm(B.PROF_LIBRE)),
        ("Bas des joues au-dessus du sol", cm(B.JZ0)),
        ("Chaque étage, hauteur", cm(B.NIV_H)),
        ("Entre la porte du placard et le vantail ouvert", cm(B.DEVANT_PORTE)),
        ("Entre le dessus du plateau et le dessous du meuble haut", cm(B.RESTE_NIV)),
    ]
    li = "".join(f"<li>{escape(n)} : <b>{v}</b></li>" for n, v in deduites)
    return ("<h2>Mesures</h2>\n<p>Toutes les cotes sont en cm.</p>\n<h3>Relevées</h3>\n" + table(relevees)
            + "\n<h3>Reprises des versions précédentes</h3>\n" + table(reprises)
            + f"\n<h3>Ce qu'il reste</h3>\n<ul>{li}</ul>")


def _a_verifier() -> str:
    ecart = P.GONDS - P.ALCOVE["nord"]
    return a_verifier([
        f"Le mur de retour nord s'arrête à {P.ALCOVE['nord']} du fond et les gonds sont à {P.GONDS}. Ces {ecart} cm "
        "d'écart ne sont pas relevés ; le plan les dessine en mur continu.",
        f"Profondeur de la salle de bain : {cm(P.SDB['p'])} sur le plan du meuble, {cm(max(y for _, y in P.SOL))} sur le "
        "plan de l'appartement.",
        f"Gonds de la porte d'entrée : à {P.GONDS} du mur du fond sur le plan du meuble (relevé client), à "
        f"{cm(P.X1 - P.PORTE_ACCUEIL['x1'])} sur le plan de l'appartement.",
    ])


def vue_explication() -> Vue:
    from pieces.sdb.meuble_bas.vues import etapes_montage
    stats = [(f"{cm(P.Y1 - P.Y0)} × {P.ALCOVE['nord']} à {P.ALCOVE['sud']}", "Alcôve (cm)"),
             (prix(B.total()), "Meuble bas entier"),
             (str(sum(q for _, _, q, _, _ in B.PIECES_DEBIT)), "Panneaux à découper"),
             (str(len(etapes_montage())), "Étapes de montage")]
    return vue_lecture("explication", tete(f"""Trois joues et un fond en mélaminé blanc de {B.cm(B.EP)}, levés sur des vérins, portent directement un plateau en chêne de {B.PLATEAU_P} de profondeur sur toute la longueur, sans aucune fixation au mur. À côté de la machine, un placard à deux étages reçoit deux bacs à linge, derrière une porte découpée en U pour jeter le linge sans l'ouvrir. Une colonne de prises en diagonale monte dans l'angle jusqu'au meuble haut. <a href="../../archives/sdb-meuble-v4-bas.html">L'ancien meuble bas</a> reste dans les archives.""") + chiffres(stats) + _structure() + _colonne() + _mesures()
                       + _a_verifier()
                       + note_source("Repère : origine à l'angle nord-ouest intérieur, x vers l'est, y vers le sud, z "
                                     "depuis le sol, cotes en cm. Cotes et données : pieces/sdb/piece.py pour la pièce, "
                                     "pieces/sdb/meuble_bas/ pour le meuble."))
