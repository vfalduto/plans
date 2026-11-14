"""Explication du document salon/enfilade : tête, chiffres clés, le meuble, rendus, construction, matériaux, les deux
comparaisons (IKEA STOCKHOLM, trois METOD 80), points à valider, remarque finale.

Textes repris de 3d/salon/enfilade.py (page, section_meuble, section_construction, section_materiaux,
section_comparaison, section_metod, section_valider), montants au format de l'ancienne page (`chiffrage.prix`) ; les
textes sous les dessins deviennent leurs textes alternatifs. Toutes les valeurs viennent de document.py, volumes.py et
chiffrage.py.
"""
import math
from html import escape

from commun.blocs import a_verifier, chiffres, figure_rendu, note_source, rendu, tete, vue_lecture
from commun.blocs_construction import rendus_meuble
from commun.modele import Vue
from pieces.salon.amenagement.document import ALLEE_ENFILADE, CANAPE
from pieces.salon.enfilade.chiffrage import debit, degagements, lettre, prix, volume_utile
from pieces.salon.enfilade.dessins import comparaison_svg
from pieces.salon.enfilade.document import (CASTO_PT, CASTO_PT26, DESSUS, DOS, ENFILADE, EP, FORMATS, H_BOITE,
                                            IKEA_FR, JEU_METOD, LM_PT25, LM_PT26, LM_T20, METOD, METOD_CAISSON,
                                            METOD_MIXTE, METOD_PLAN_LM, METOD_RELEVE, NOIRS, NORD, PC, PIEDS_X,
                                            PROF_ETAGERE, RENDUS, STOCKHOLM, TRAV, VRENA, ZP, COULISSE, L, N, P, Z1)
from pieces.salon.enfilade.vues import RENDUS_SITE
from pieces.salon.enfilade.volumes import controle
from pieces.salon.etageres.document import MONTANTS
from pieces.salon.meubles import cote


def _lien(url, txt):
    return f'<a href="{escape(url)}">{escape(txt)}</a>' if url else escape(txt)


def _tableau(entete, lignes):
    """`<div class="defile"><table>` : `entete` HTML des `<th>`, `lignes` HTML des `<tr>`."""
    return f'<div class="defile"><table><thead><tr>{entete}</tr></thead><tbody>{lignes}</tbody></table></div>'


def _pieds(g):
    return len(g["pieds_y"]) * len(PIEDS_X)


# ------------------------------------------------------------------ tête et chiffres clés
def _tete(ch):
    chapo = (f"Le meuble bas de {cote(L)} × {cote(P)} × {cote(Z1)} sous les étagères, à construire soi-même, tout en "
             "chêne massif de 18 huilé : trois caissons liés sur place, chacun sous son dessus, façades sans poignée, "
             f"huit pieds réglables. Environ {round(ch['total'], -1):.0f} € de matériaux.")
    return tete(chapo, figure=figure_rendu(rendu(RENDUS_SITE, "", "iso"), RENDUS[0][1]))


def _chiffres(ch, n_etapes, total):
    g, ps = ch["g"], ch["ps"]
    d1, d2 = degagements(g)
    return chiffres([(controle(g), "Cotes hors tout (cm)"), (total, f"Matériaux, composition {ch['v']['cle']}"),
                     (f"{volume_utile(g):.0f} L", "Volume utile"), (str(len(debit(ps))), "Repères"),
                     (str(len(ps)), "Pièces à débiter"), (str(n_etapes), "Étapes de montage"),
                     (f"{cote(d1)} cm", "Devant la porte ouverte de M1"), (f"{cote(d2)} cm", "Devant un tiroir sorti")])


# ------------------------------------------------------------------ le meuble
def _meuble(ch):
    g = ch["g"]
    dessus = "un dessus en chêne d'une pièce" if DESSUS[1] == 1 else f"{lettre(N)} dessus en chêne, un par caisson"
    return ("<h2>Le meuble</h2>"
            f"<p>Trois caissons de {cote(g['W'][0])} posés côte à côte et liés par des vis, sur {_pieds(g)} pieds de "
            f"{cote(ZP)}, sous {dessus}. Tout en chêne massif de {cote(EP)}, dedans comme dehors. Façades à fleur du "
            "dessus, sans poignée : on appuie pour ouvrir. Cotes extérieures du modèle conservées : "
            f"{controle(g)}.</p>")


# ------------------------------------------------------------------ construction
def _construction(ch):
    g = ch["g"]
    tiroir = next(fc for fc in g["facades"] if fc["type"] == "tiroir")
    porte_m1 = max(fc["y1"] - fc["y0"] for fc in g["facades"] if fc["k"] == 0)
    dessus_60 = ("dans toute la largeur des tablettes de 60 : leurs chants d'usine font le devant et l'arrière"
                 if P >= FORMATS["C18"]["l"] else "refendues dans des tablettes de 60")
    return (
        "<h2>Construction</h2>"
        "<h3>Trois caissons plutôt qu'un</h3>"
        f"<p>Un caisson d'une pièce de {cote(L)} ne passe pas facilement le couloir et demanderait des panneaux plus "
        f"longs que les tablettes de chêne vendues ({cote(FORMATS['C18']['L'])} chez Weldom). Trois caissons de "
        f"{cote(g['W'][0])}, un par module, se montent à plat, se portent à deux mains et se lient sur place par "
        f"{lettre(4)} vis de liaison par jonction (Ø 5, à travers les deux côtés). La jonction fait {cote(2 * EP)} "
        "d'épaisseur : on ne la voit pas, elle tombe dans le jeu entre façades.</p>"
        "<h3>Caisson</h3>"
        "<p>Chêne lamellé-collé de 18, comme les façades : deux côtés (fil vertical), un fond entre les côtés, deux "
        f"traverses de {cote(TRAV)} en haut (avant et arrière) à la place d'un plafond, puisque le dessus couvre tout. "
        "Côtés et fond ont le fil en travers de la profondeur : ils travaillent ensemble, on peut les coller. "
        "Assemblage collé et vissé (vis bois 4 × 50, avant-trous Ø 3) ; les têtes sont cachées par le caisson voisin "
        f"ou le dessus. Les deux bouts se voient ({cote(NORD)} libres de chaque côté) : le côté nord de M1 et le côté "
        "sud de M3 (joues) sont assemblés par tourillons et colle, sans vis apparente. Les chants vus devant sont du "
        f"chêne poncé et huilé : rien à plaquer. Dos en fibres dures de {cote(DOS)} vissé en applique tous les 15 cm : "
        "il met le caisson d'équerre et le raidit.</p>"
        "<h3>Dessus</h3>"
        f"<p>{lettre(N).capitalize()} pièces de chêne de {cote(DESSUS[0])}, une par caisson ({cote(g['W'][0])} × "
        f"{cote(P)}, {dessus_60}), posées bord à bord : les deux joints tombent au droit des jonctions des caissons, "
        f"dans l'alignement des jeux entre façades. Un dessus d'une pièce de {cote(L)} n'existe en chêne fin qu'en "
        "plan de travail : 36 (variante F) ou 25 sur commande. Chaque pièce couvre son caisson et le haut de ses "
        f"façades, à fleur devant, fixée par en dessous sur {lettre(4)} équerres à trou oblong : le bois massif bouge "
        "de 2 à 3 mm dans sa largeur avec les saisons, il doit pouvoir glisser. Les pieds réglés au niveau mettent les "
        "trois dessus dans le même plan ; deux tourillons Ø 8 non collés par joint les gardent affleurants. Huilés sur "
        "les deux faces pour qu'ils ne se cintrent pas.</p>"
        f"<h3>Socle : {_pieds(g)} pieds réglables</h3>"
        "<p>Pieds carrés en acier noir de 15, platine de 6 × 6 vissée sous les fonds, patin fileté M10 pour rattraper "
        f"le carrelage. Deux rangées ({cote(PIEDS_X[0])} du mur et {cote(P - ENFILADE['facade'] - PIEDS_X[1])} du nu "
        "du caisson, en retrait des façades) et quatre files : sous les deux bouts et à cheval sur chaque jonction, la "
        "platine vissée dans les deux fonds. Sans pied au milieu des jonctions, chaque fond de 18 porterait seul "
        f"vaisselle et vinyles sur {cote(g['W'][0])} : huit pieds de 50 kg suffisent largement.</p>"
        "<h3>Portes</h3>"
        f"<p>Chêne massif de 18, fil vertical, {lettre(2)} charnières invisibles Ø 35 à 110° en applique par porte, "
        "réglables en trois directions. Ouverture par poussoir magnétique (pas de poignée) : il faut alors des "
        "charnières sans amortisseur, sinon le poussoir ne repousse pas la porte. Avec "
        f"{cote(NORD)} entre la joue nord et le mur, la porte nord s'ouvre à 110° sans toucher le mur : plus de "
        f"fileur. Ouvertes, les portes de M1 prennent {cote(porte_m1)} des {cote(CANAPE['x0'] - P)} de l'allée.</p>"
        "<h3>Tiroirs</h3>"
        f"<p>Trois façades de {cote(tiroir['z1'] - g['za'])} de haut, boîtes en chêne de 18 (hauteur "
        f"{cote(H_BOITE)}, profondeur {cote(COULISSE)}, fond en fibres dures vissé dessous), coulisses à billes de "
        f"{cote(COULISSE * 10)} à sortie totale et ouverture par pression, 25 kg par paire : les couverts d'une "
        "famille (5 kg avec le range-couverts) et le linge de table y tiennent sans peine. La façade se visse par "
        "l'intérieur de la boîte une fois les jeux réglés.</p>"
        "<h3>Étagères</h3>"
        f"<p>Chêne de 18, {cote(PROF_ETAGERE)} de profondeur (refendues dans des tablettes de 60, "
        f"{cote(PC - PROF_ETAGERE)} en retrait des portes), sur taquets Ø 5 dans des rangées de trous tous les 3,2 "
        "cm : elles se déplacent. Les vinyles, lourds, restent sur le fond ; l'étagère de M1 ne porte que jeux et "
        "albums. Les trous évitent la hauteur des embases de charnières.</p>"
        "<h3>Fixation au mur</h3>"
        "<p>Une équerre acier par caisson, sous la traverse arrière, vissée dans la cloison à travers le dos : un "
        "tiroir sorti chargé ne doit pas faire basculer le meuble. La cloison (cellier, WC) n'est pas connue : "
        "chevilles Molly si c'est de la plaque de plâtre, chevilles nylon si c'est du carreau de plâtre ou de la "
        f"brique. Les pieds restent à {cote(PIEDS_X[0])} du mur : une plinthe de moins de "
        f"{cote(PIEDS_X[0] - 1.25)} d'épaisseur et de {cote(ZP)} de haut passe dessous.</p>"
        "<h3>Finition</h3>"
        f"<p>Huile dure incolore sur tout le chêne, dedans compris ({cote(ch['c']['chene_m2'], 1)} m² de panneaux, "
        f"{cote(ch['c']['chene_m2'] * 2, 1)} m² de faces), deux couches, toutes les faces avant montage, ponçage 120, "
        "180, puis 240 entre les couches. Les dessus se ravivent d'une couche quand ils ont soif. L'intérieur huilé "
        "se nettoie à l'éponge à peine humide ; une huile spéciale plan de travail (contact alimentaire) va mieux "
        "dans le module des assiettes et des verres.</p>")


# ------------------------------------------------------------------ matériaux
def _materiaux(chs):
    a = next(c for c in chs if c["v"].get("retenu"))
    lignes = []
    for ch in chs:
        v = ch["v"]
        cais = "mélaminé blanc" if v["caisson"] == "mel" else FORMATS[v["caisson"]]["court"]
        des = (f'{FORMATS["PT36"]["court"]}, une pièce' if v["dessus"][1] == 1
               else f'{FORMATS[v["facade"]]["court"]}, {v["dessus"][1]} pièces')
        ecart = ch["total"] - a["total"]
        lignes.append(f'<tr><td><b>{v["cle"]}</b>{" retenu" if v.get("retenu") else ""}</td>'
                      f'<td>{escape(v["nom"])}</td><td>{escape(cais)}</td>'
                      f'<td>{escape(FORMATS[v["facade"]]["court"])}</td><td>{escape(des)}</td>'
                      f'<td class="num">{prix(ch["total"])}</td>'
                      f'<td class="num">{"—" if v.get("retenu") else ("+" if ecart > 0 else "−") + prix(abs(ecart))}</td>'
                      "</tr>")
    b = next(ch for ch in chs if ch["v"]["cle"] == "B")
    f_ = next(ch for ch in chs if ch["v"]["cle"] == "F")
    minces = ", ".join(c["v"]["cle"] for c in chs if c["v"]["dessus"][0] < 3)
    c18 = FORMATS["C18"]["prix"]
    entete = ('<th>Variante</th><th>Composition</th><th>Caisson</th><th>Façades</th><th>Dessus</th>'
              '<th class="num">Total TTC</th><th class="num">Écart</th>')
    return (
        "<h2>Matériaux</h2>"
        f'<p><b>Retenu ({a["v"]["cle"]})</b> : tout en chêne massif de 18, caissons, étagères et boîtes de tiroir '
        "compris, et un dessus de 18 en trois pièces plutôt que le plan de travail de 36, jugé trop épais. Le meuble "
        "ouvert est aussi chaud que fermé, et il n'y a qu'une matière à acheter, couper et huiler. Le chêne est du "
        "lamellé-collé massif (lames collées sur chant), pas du placage : il se ponce, s'huile et se répare.</p>"
        + _tableau(entete, "".join(lignes))
        + note_source("Chaque total est recalculé avec la même quincaillerie et sa propre découpe (nombre de tablettes "
                      f"ou de plaques). Avec un dessus de 1,8 ({minces}), le caisson et les façades gagnent 1,8 de "
                      f"haut : la hauteur totale reste {cote(Z1)}.")
        + "<ul>"
        f"<li><b>A et B, intérieur en mélaminé blanc</b> : le chêne seulement où il se voit (façades, dessus, joues). "
        f"B (même dessus de 18 en trois pièces) coûte {prix(a['total'] - b['total'])} de moins que {a['v']['cle']} ; "
        "un intérieur blanc éclaire la vaisselle mais fait cuisine.</li>"
        f"<li><b>F, dessus d'une pièce de 36</b> : pas de joint, mais {prix(f_['total'] - a['total'])} de plus et un "
        "plateau deux fois plus épais que les façades.</li>"
        "<li><b>D, contreplaqué</b> : caisson plus léger et plus raide que le mélaminé, chants de contreplaqué "
        "apparents (à huiler ou plaquer). Le contreplaqué de feuillus de 12 de Castorama (244 × 122, 84,90 €) est trop "
        "mince pour les coupelles de charnières (12 à 13 mm de profondeur).</li>"
        "<li><b>E, tout mélaminé</b> : le moins cher, mais un décor chêne imprimé, des chants à plaquer partout et un "
        "dessus qui ne se ponce pas.</li>"
        f'<li>Autres dessus d\'une pièce : Leroy Merlin vend un <a href="{LM_PT25}">plan chêne massif pleines lames '
        "300 × 80 × 2,5</a> (385,19 € en promotion, livré en 8 jours, relevé en ligne), "
        f"{prix(385.19 - c18 * 2)} de plus environ que les tablettes des trois dessus ; Castorama un plan de "
        f'300 × 62 × 4 (<a href="{CASTO_PT}">GoodHome</a>, 299,90 € hors promotion), plus épais encore ; les plans de '
        f"250 × 65 × 2,6 en chêne lamellé, d'une pièce, couvrent les {cote(L)} : 99 € chez Castorama "
        f'(<a href="{CASTO_PT26}">fiche</a>, en rupture le 30/10/2026), 109 € chez Leroy Merlin '
        f'(<a href="{LM_PT26}">fiche</a>), moins que deux tablettes ({prix(2 * c18)}) mais 2,6 d\'épaisseur au lieu '
        f'de 1,8. Pour des façades de 20 (l\'épaisseur du modèle), Leroy Merlin vend une <a href="{LM_T20}">tablette '
        "chêne pleine lame 250 × 60 × 2</a> à 119 €.</li>"
        "</ul>")


# ------------------------------------------------------------------ comparaison avec IKEA STOCKHOLM
def _lignes(lignes):
    return "".join(f'<tr><td>{escape(a)}</td><td>{escape(b)}</td><td>{escape(c)}</td><td class="num">{escape(d)}</td>'
                   "</tr>" for a, b, c, d in lignes)


def _comparaison(ch):
    g, S = ch["g"], STOCKHOLM
    vol = volume_utile(g)
    vs = math.prod(S["interieur"]) / 1000
    lt = NORD * 2 + L
    lignes = [("Longueur", cote(L), cote(S["l"]), f"{'+' if L > S['l'] else '−'}{cote(abs(L - S['l']))}"),
              ("Profondeur", cote(P), cote(S["p"]), f"+{cote(P - S['p'])}"),
              ("Hauteur", cote(Z1), cote(S["h"]), f"−{cote(S['h'] - Z1)}"),
              ("Surface du dessus", f"{cote(L * P / 1e4, 2)} m²", f"{cote(S['l'] * S['p'] / 1e4, 2)} m²",
               f"× {cote(L * P / (S['l'] * S['p']), 1)}"),
              ("Volume intérieur", f"{vol:.0f} L", f"≈ {vs:.0f} L (estimé)", f"× {cote(vol / vs, 1)}"),
              ("Rangement", f"4 portes, 3 tiroirs, {len(g['etageres'])} étagères", S["contenu"], ""),
              ("Matière", "chêne massif de 18, huilé", S["materiau"], ""),
              ("Place sur le mur", f"{cote(NORD)} libres à chaque bout",
               f"{cote((lt - S['l']) / 2)} libres à chaque bout (centré)", ""),
              ("Prix", f"{prix(ch['total'])} de matériaux, à construire", f"{prix(S['prix'])}, à monter",
               f"+{prix(ch['total'] - S['prix'])}"),
              ("Prix au litre", f"{prix(ch['total'] / vol)}", f"≈ {prix(S['prix'] / vs)}", "")]
    alt = (f"À la même échelle sur le mur ouest ({cote(lt)} entre le mur nord et le cadre du passage), les deux "
           "meubles centrés. Tiretés : jonctions des trois caissons.")
    entete = f'<th></th><th>Cette enfilade</th><th>{escape(S["nom"])}</th><th class="num">Écart</th>'
    return (
        "<h2>Comparaison avec IKEA STOCKHOLM</h2>"
        f'<p>Le buffet <a href="{S["url_fr"]}">STOCKHOLM 2025</a> en chêne plaqué ({prix(S["prix"])} sur la '
        f'<a href="{S["url"]}">fiche IKEA Belgique</a>, prix France non lu) est la référence du genre : même esprit, '
        "sans poignée, sur pieds.</p>"
        f'<figure class="schema">{comparaison_svg(g, titre=alt)}</figure>'
        + _tableau(entete, _lignes(lignes))
        + note_source(f"STOCKHOLM : cotes hors tout et intérieur des tiroirs ({cote(S['tiroir'][0])} × "
                      f"{cote(S['tiroir'][1])}) d'après la fiche IKEA, charges de {S['charges']}. IKEA ne donne pas "
                      "les cotes intérieures : le volume est estimé avec des panneaux de 1,8 (deux côtés, une "
                      "séparation, dessus et fond), 4 de dos et 12 de pieds, soit "
                      f"{' × '.join(cote(v, 1) for v in S['interieur'])} utiles. Volume de l'enfilade : comme dans "
                      "« Le meuble », sous les traverses.")
        + "<ul>"
        f"<li>Sur ce mur, un STOCKHOLM laisse {cote(lt - S['l'])} vides ; deux ({cote(2 * S['l'])}) ne tiennent "
        "pas.</li>"
        f"<li>L'enfilade range environ {cote(vol / vs, 1)} fois plus, pour {prix(ch['total'] - S['prix'])} de plus "
        "en matériaux, deux week-ends de travail et l'outillage. Elle est en chêne massif (se ponce, se répare), le "
        "STOCKHOLM en placage.</li>"
        f"<li>Elle est un peu plus basse ({cote(Z1)} contre {cote(S['h'])}) et plus profonde ({cote(P)} contre "
        f"{cote(S['p'])}) : à hauteur égale des étagères au-dessus, elle laisse {cote(MONTANTS['z0'] - Z1)} sous les "
        f"montants, le STOCKHOLM {cote(MONTANTS['z0'] - S['h'])}.</li>"
        "</ul>")


# ------------------------------------------------------------------ comparaison avec trois METOD 80
def _metod(ch):
    g, Mx, Mt = ch["g"], METOD_MIXTE, METOD
    vol = volume_utile(g)
    interieur = (80 - 2 * 1.8, 57.5, 80 - 2 * 1.8)   # tablette UTRUSTA 76,4 × 57,5 ; côtés, fond et dessus de 1,8
    vm = 3 * math.prod(interieur) / 1000
    lt = NORD * 2 + L

    def ecart(v):
        return f"{'+' if v > 0 else '−'}{cote(abs(v))}" if v else "="

    def plus_moins(v, ref):
        return "plus" if v > ref else "moins"

    autres = [(Mx["nom"], Mx["l"], Mx["p"], Mx["h"], METOD_CAISSON["pieds"], True, [NORD + 80, NORD + 160])]
    lignes = [("Longueur", cote(L), f"{cote(Mx['l'])} (joues de {cote(Mx['joue'])} aux bouts)",
               ecart(round(Mx["l"] - L, 1))),
              ("Profondeur", cote(P),
               f"{cote(Mx['p'])} (caisson {cote(METOD_CAISSON['prof'])} sans rail, façade {cote(Mx['facade'])})",
               ecart(round(Mx["p"] - P, 1))),
              ("Hauteur", cote(Z1),
               f"{cote(Mx['h'])} (pieds {cote(METOD_CAISSON['pieds'])}, caisson {cote(METOD_CAISSON['h'])}, plan "
               f"{cote(Mx['dessus'])})", ecart(round(Mx["h"] - Z1, 1))),
              ("Volume intérieur", f"{vol:.0f} L", f"≈ {vm:.0f} L", f"× {cote(vm / vol, 2)}"),
              ("Rangement", f"4 portes, 3 tiroirs, {len(g['etageres'])} étagères",
               "4 portes, 3 tiroirs, 4 tablettes (2 par caisson)", ""),
              ("Ce qui se voit", "chêne massif de 18, huilé",
               "chêne massif huilé (façades, joues, plan), plinthe anthracite", ""),
              ("Intérieur", "chêne massif", "aggloméré mélaminé noir-gris, tiroirs en acier gris foncé", ""),
              ("Pieds", f"{_pieds(g)} pieds acier noir de {cote(ZP)}",
               f"12 pieds plastique de {cote(METOD_CAISSON['pieds'])} derrière une plinthe", ""),
              ("Travail", "deux week-ends, outillage", "montage IKEA, découpe et huile du chêne, perçage des charnières",
               ""),
              ("Prix", prix(ch["total"]), prix(Mx["total"]),
               f"{'+' if Mx['total'] > ch['total'] else '−'}{prix(abs(Mx['total'] - ch['total']))}")]
    postes = [("Caissons, tablettes", "METOD noir-gris", "les mêmes, achetés nus",
               "les pièces du système : perçages, pieds et tiroirs METOD s'y montent sans adaptation"),
              ("Tiroirs", "KNIVSHULT, coulisses amorties", "les mêmes",
               "55 à 70 € le tiroir, coulisses amorties comprises ; un tiroir maison demande caisson, coulisses et "
               "réglages"),
              ("Plan", f"VRENA chêne plaqué sur aggloméré 2,8, {prix(VRENA)}",
               f"chêne massif lamellé 2,6 Leroy Merlin, {prix(109)} brut", "massif (se ponce, se répare), plus mince, "
               "moitié prix ; à huiler"),
              ("Façades", "NICKEBO anthracite, film plastique sur aggloméré",
               "chêne massif de 18, débitées dans les tablettes Weldom",
               "les façades de l'enfilade ; un choc se ponce ; coupelles de charnière à percer"),
              ("Bouts", "côtés du caisson noir-gris", f"joues de chêne de {cote(Mx['joue'])}, du sol au plan",
               "le meuble se lit en chêne, pas en caisson de cuisine"),
              ("Charnières", "110° avec amortisseur (dans les combinaisons)", "UTRUSTA 95° sans amortisseur",
               "avec des poussoirs, l'amortisseur freine la poussée"),
              ("Pieds, plinthe, poussoirs", "METOD, FÖRBÄTTRA, UTRUSTA, KNIVSHULT", "les mêmes",
               "5 € la paire de pieds ; plinthe sur le devant seulement, les joues ferment les bouts")]
    choix = "".join(f"<tr><td>{escape(a)}</td><td>{escape(b)}</td><td>{escape(c)}</td><td>{escape(d)}</td></tr>"
                    for a, b, c, d in postes)
    achats = "".join(
        f'<tr><td>{escape(x["nom"])}<br><small>{escape(x["note"])}</small></td><td>{escape(x["ou"])}</td>'
        f'<td>{escape(x["ref"])}</td><td class="num">{x["q"]}</td><td class="num">{prix(x["pu"])}</td>'
        f'<td>{x["st"]}</td><td>{_lien(x["url"], "fiche") if x["url"] else "—"}</td>'
        f'<td class="num">{prix(x["q"] * x["pu"])}</td></tr>' for x in Mx["postes"])
    achats += f'<tr class="total"><td colspan="7">Total TTC</td><td class="num">{prix(Mx["total"])}</td></tr>'
    totaux = [("Tout IKEA : noir-gris, façades NICKEBO anthracite, plan VRENA", Mt["total"]),
              ("IKEA, sauf le plan en chêne massif Leroy Merlin", METOD_PLAN_LM),
              ("Mixte : IKEA dedans, chêne massif dehors (façades, joues, plan)", Mx["total"]),
              ("Cette enfilade (variante retenue)", ch["total"])]
    tot = "".join(f'<tr><td>{escape(n)}</td><td class="num">{prix(v)}</td><td class="num">'
                  f'{(("+" if v > ch["total"] else "−") + prix(abs(v - ch["total"]))) if v != ch["total"] else "—"}'
                  "</td></tr>" for n, v in totaux)
    noirs = "".join(f'<tr><td>{_lien(IKEA_FR + u, n)}</td><td>{escape(d)}</td><td class="num">{prix(pu)}</td></tr>'
                    for n, pu, d, u in NOIRS)
    alt = (f"À la même échelle sur le mur ouest ({cote(lt)}), centrés. METOD sur plinthe anthracite de "
           f"{cote(METOD_CAISSON['pieds'])}, joues et plan de chêne. Tiretés : jonctions des caissons.")
    return (
        "<h2>Comparaison avec trois METOD 80</h2>"
        "<p>Le même meuble sur trois caissons de cuisine IKEA METOD de 80 × 60 × 80, deux à portes (M1, M3) et un à "
        "trois tiroirs (M2), comme l'enfilade. Chaque poste est pris là où il vaut le mieux pour son prix : chez IKEA "
        "ce qui fait le système (caissons, tiroirs, charnières, poussoirs, pieds), ailleurs ce qui se voit (plan en "
        "chêne massif chez Leroy Merlin, façades et joues dans les tablettes de chêne de Weldom). Prix relevés en "
        f"ligne le {METOD_RELEVE}.</p>"
        f'<figure class="schema">{comparaison_svg(g, autres, alt)}</figure>'
        + _tableau(f'<th></th><th>Cette enfilade</th><th>{escape(Mx["nom"])}</th><th class="num">Écart</th>',
                   _lignes(lignes))
        + "<h3>Poste par poste</h3>"
        + _tableau("<th>Poste</th><th>Tout IKEA</th><th>Mixte</th><th>Pourquoi</th>", choix)
        + _tableau('<th>Composition</th><th class="num">Total TTC</th><th class="num">Écart avec l\'enfilade</th>', tot)
        + "<h3>Achats de la composition mixte</h3>"
        + _tableau('<th>Poste</th><th>Où</th><th>Réf.</th><th class="num">Qté</th><th class="num">Prix unit.</th>'
                   '<th>Prix</th><th>Source</th><th class="num">Total</th>', achats)
        + note_source(f"Façades aux cotes IKEA ({cote(80 - JEU_METOD)} × {cote(40 - JEU_METOD)} pour une porte de "
                      f"40 × 80, faces de {cote(80 - JEU_METOD)} × {cote(20 - JEU_METOD)} et {cote(80 - JEU_METOD)} × "
                      f"{cote(40 - JEU_METOD)}), à vérifier sur la notice METOD. Dans chaque tablette de 200 × 60 : "
                      "deux pièces de 80 de long, chacune de 40 et de 20 de large. Joues de 60 : elles s'arrêtent à "
                      f"{cote(round(Mx['p'] - 60, 1))} du mur. Volume METOD : intérieur du caisson "
                      f"({' × '.join(cote(v) for v in interieur)}, d'après la tablette UTRUSTA et des panneaux de "
                      "1,8) ; tiroirs non déduits, comme pour l'enfilade.")
        + "<ul>"
        f"<li>Le plan VRENA est le plus mauvais poste du tout IKEA : {prix(VRENA)} pour un placage de chêne sur "
        f'aggloméré. Le <a href="{LM_PT26}">plan brut en chêne lamellé 250 × 65 × 2,6</a> de Leroy Merlin, vendu par '
        f"l'enseigne et disponible dans la plupart de ses magasins, coûte {prix(109)}, d'une pièce, en massif. Ce "
        f"seul changement fait passer le tout IKEA à {prix(METOD_PLAN_LM)}. Castorama a le même format à 99 € "
        f'(<a href="{CASTO_PT26}">fiche</a>), mais en rupture à Marseille St-Loup et en livraison le '
        f"{METOD_RELEVE}.</li>"
        f"<li>Passer des façades NICKEBO aux façades et joues en chêne coûte {prix(abs(Mx['total'] - METOD_PLAN_LM))} "
        f"de {plus_moins(Mx['total'], METOD_PLAN_LM)} (tablettes, huile, charnières et tablettes UTRUSTA achetées à "
        "part), pour un meuble qui se lit en chêne comme l'enfilade. Ce qui reste IKEA ne se voit qu'ouvert : "
        "mélaminé noir-gris et tiroirs en acier gris foncé, au lieu du chêne partout.</li>"
        f"<li>Prix : le mixte coûte {prix(Mx['total'])}, {prix(abs(Mx['total'] - ch['total']))} de "
        f"{plus_moins(Mx['total'], ch['total'])} que l'enfilade, et range environ {cote(vm / vol, 2)} fois plus. Ce "
        "qu'on gagne : les caissons et les tiroirs tout faits, les plus longs à fabriquer. Il reste une journée de "
        "montage, la découpe de neuf pièces de chêne (scie circulaire ou découpe en magasin) et la recoupe du plan, "
        "l'huile et huit coupelles de Ø 35 à percer (mèche Forstner avec butée, dans l'outillage de l'enfilade).</li>"
        f"<li>Hauteur : {cote(Mx['h'])} au lieu de {cote(Z1)}. Il reste {cote(round(MONTANTS['z0'] - Mx['h'], 1))} "
        f"sous les montants des étagères au lieu de {cote(MONTANTS['z0'] - Z1)}. Le plan de 2,6 est plus mince que le "
        "VRENA (2,8) et que le plan de 3,6 jugé trop épais, mais plus épais que les dessus de 1,8 de l'enfilade.</li>"
        f"<li>Profondeur : {cote(Mx['p'])}, {cote(round(Mx['p'] - P, 1))} de plus que l'enfilade dans l'allée de "
        f"{ALLEE_ENFILADE}. Sans rail de suspension, une équerre par caisson le tient au mur.</li>"
        "<li>Pour un meuble noir, on garde les façades IKEA. Le noir lisse n'existe qu'en anthracite mat ; le vrai "
        "noir seulement en portes à cadre (porte 40 × 80, ikea.com/fr) :</li>"
        "</ul>"
        + _tableau('<th>Porte 40 × 80</th><th>Aspect</th><th class="num">Prix</th>', noirs)
        + note_source("À vérifier en magasin : les charnières UTRUSTA de 95° sur une porte de 1,8 (les portes IKEA font "
                      "1,6) ; le contenu d'un jeu de poussoirs KNIVSHULT ; la fixation des faces de chêne sur les "
                      "tiroirs KNIVSHULT ; la teinte du caisson noir-gris dans les jeux entre façades."))


# ------------------------------------------------------------------ points à valider
def _points(ch, chs):
    nc18 = next(li["q"] for li in ch["lignes"] if li["poste"] == FORMATS["C18"]["nom"])
    g = ch["g"]
    f_ = next(c for c in chs if c["v"]["cle"] == "F")
    p1 = [fc for fc in g["facades"] if fc["k"] == 0][0]
    p3 = [fc for fc in g["facades"] if fc["type"] == "porte"][-1]
    return [
        f"Dessus de {cote(DESSUS[0])} en trois pièces, deux joints au droit des jonctions ; d'une pièce, il faudrait "
        f"le plan de 3,6 (variante F, {prix(f_['total'] - ch['total'])} de plus) ou celui de 2,5 livré par Leroy "
        "Merlin.",
        f"Les façades s'arrêtent sous le dessus, à {cote(g['zb'])} (le modèle les montre jusqu'à {cote(Z1 - 0.2)}).",
        "Intérieur en chêne huilé plutôt qu'en mélaminé : choisir une huile pour contact alimentaire pour le module de "
        "la vaisselle.",
        f"Meuble centré sur le mur, {cote(NORD)} libres à chaque bout (à garder libres ou pour un pied de lampe fin "
        f"côté passage) ; portes de {cote(p1['y1'] - p1['y0'])}.",
        f"{_pieds(g)} pieds carrés noirs de 2,5 au lieu de 4 pieds ronds : forme et couleur (chêne possible, non "
        "réglable, plus cher).",
        "Ouverture par pression (poussoirs, coulisses à ouverture par pression) ou poignées discrètes ; la charnière "
        "Weldom 9154863 doit être sans amortisseur pour les poussoirs, et son prix de 5,35 € s'entendre à l'unité.",
        f"Chêne massif de 18 pour des portes de {cote(p3['z1'] - p3['z0'], 0)} × {cote(p3['y1'] - p3['y0'], 0)} et "
        f"des dessus de {cote(g['W'][0], 0)} × {cote(P)} : risque de léger tuilage ; choisir des tablettes bien "
        "planes, huiler les deux faces pareil.",
        "Nature de la cloison ouest (chevilles), hauteur et épaisseur de la plinthe derrière le meuble.",
        f"Service de découpe des tablettes chez Weldom à confirmer, et {lettre(nc18)} tablettes de chêne 200 × 60 en "
        "stock.",
        "Coulisses de 500 à ouverture par pression et poussoirs : références à choisir en rayon, prix estimés.",
        "Table ouverte rangée debout dans l'allée devant M1 : elle bloque alors les portes de M1.",
        "Dos en fibres dures brut (brun) visible à l'intérieur, à côté du chêne : contreplaqué chêne de 3 ou 4 mm plus "
        "cher, à chiffrer si le brun dérange.",
    ]


# ------------------------------------------------------------------ la vue
def vue_explication(ch: dict, chs: list[dict], n_etapes: int, total: str) -> Vue:
    """`total` : le total de la vue Achats (`total_achats(<ses sections>, arrondi=False)`), repris tel quel."""
    return vue_lecture("explication", (
        _tete(ch) + _chiffres(ch, n_etapes, total) + _meuble(ch)
        + rendus_meuble(RENDUS_SITE, "", RENDUS, titre="Rendus 3D")
        + _construction(ch) + _materiaux(chs) + _comparaison(ch) + _metod(ch)
        + a_verifier([escape(p) for p in _points(ch, chs)], titre="Points à valider")
        + note_source("Cotes et données du meuble : pieces/salon/enfilade/ (document.py, volumes.py), dans le repère "
                      "du salon (pieces/salon/piece.py). Plan du salon : "
                      '<a href="../../salon-v4.html">Salon, aménagement</a>.')))
