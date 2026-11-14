"""Vues du document salon/enfilade : Plans, Découpe, Montage, Achats ; l'Explication est dans explication.py.

Textes repris de 3d/salon/enfilade.py (section_meuble, section_iso, section_debit, section_achats, section_montage) ;
les textes sous les dessins deviennent leurs textes alternatifs (`alts`). Toutes les valeurs viennent de document.py,
volumes.py et chiffrage.py.
"""
from html import escape
from pathlib import Path

from commun.blocs import Achat, SectionAchats, achats, euros, note_source, vue_lecture
from commun.blocs_construction import (Calepin, Colonne, DessinMeuble, Etape, calepinage, etapes, tableau_debit,
                                       vue_plans)
from commun.modele import Vue
from pieces.salon.enfilade import chiffrage
from pieces.salon.enfilade.chiffrage import debit, degagements, format_de, lettre, poids_caisson, volume_utile
from pieces.salon.enfilade.dessins import (ECHELLES, decoupe_svg, dessus_svg, eclate_svg, en_cm, face_svg,
                                           formule_longueur, iso, profil_svg)
from pieces.salon.enfilade.document import (COULISSE, DESSUS, DOS, ETAGERES_CAISSONS, FAC, FORMATS, GROUPES, H_BOITE,
                                            HUILE, JEU, MAGASINS, NORD, ORDRE_MAG, OUTILLAGE, PC, PIEDS_X, PREFIXE,
                                            RELEVE, TAMPON, TRAIT, L, P)
from pieces.salon.meubles import cote

RENDUS_SITE = Path(__file__).resolve().parents[3] / "site" / "salon" / "enfilade" / "rendus"


# ------------------------------------------------------------------ Plans
def alts(ch: dict) -> dict[str, str]:
    """Textes alternatifs des six dessins : les textes sous les dessins de l'ancienne page."""
    g = ch["g"]
    portes = [fc for fc in g["facades"] if fc["type"] == "porte"]
    l1 = portes[0]["y1"] - portes[0]["y0"]
    l3 = portes[-1]["y1"] - portes[-1]["y0"]
    d_porte, d_tiroir = degagements(g)
    et = ETAGERES_CAISSONS
    return {
        "elevation": (
            "Vu de la pièce, regard vers l'ouest : le nord (mur, module M1) est à droite. Tireté sur les portes : la "
            "pointe montre le côté des charnières (cercles : coupelles Ø 35). Les tiretés verticaux marquent les "
            f"jonctions des caissons{' et les joints du dessus' if DESSUS[1] > 1 else ''}. "
            f"{lettre(len(portes)).capitalize()} portes de {cote(l1)}"
            f"{'' if abs(l1 - l3) < 0.05 else f' (M1) et {cote(l3)} (M3)'}, {cote(NORD)} libres entre le meuble et "
            f"le mur nord ; jeux de {cote(JEU * 10)} mm entre façades."),
        "iso": (
            "L'enfilade fermée en vue isométrique, depuis la pièce, côté sud et en hauteur (le mur ouest au fond, le "
            "sud à gauche, le nord à droite ; étagères et mur non dessinés) : "
            + ("dessus d'une pièce en chêne" if DESSUS[1] == 1 else "trois dessus en chêne bord à bord")
            + f", façades à fleur du dessus, joues nord et sud sans vis apparente, {cote(NORD)} libres à chaque bout, "
            "pieds noirs en retrait."),
        "ouverte": (
            "Ouverte : la porte nord de M1 et la porte sud de M3 tournées à 90° sur leurs charnières, le tiroir du "
            f"haut de M2 sorti de toute sa course ({cote(COULISSE)}). On voit l'étagère de M1 ({cote(et[0][0])} libres "
            "dessous pour les vinyles), les deux étagères de M3, et la boîte du tiroir (chêne, fond en fibres dures). "
            "La porte nord de M3 et la porte sud de M1 restent fermées : ouvertes, elles heurteraient le tiroir "
            "sorti."),
        "profil": (
            f"Profil : dos de {cote(DOS)} vissé en applique, côtés de {cote(PC)}, tampons de {cote(TAMPON * 10)} mm, "
            f"façades de {cote(FAC)} : {cote(P)} en tout. En M1, les vinyles tiennent debout sur le fond "
            f"({cote(et[0][0])} libres) ; l'équerre sous la traverse arrière retient le meuble au mur. En M2, trois "
            f"boîtes de {cote(H_BOITE)} sur coulisses de {cote(COULISSE * 10)} à sortie totale. M3 est comme M1 avec "
            f"deux étagères ({cote(et[2][0])} libres pour les assiettes et les plats, {cote(et[2][1])} pour les "
            "verres, le haut pour les tasses)."),
        "dessus": (
            "Vue de dessus, dessus enlevé : portes ouvertes à 90° (elles vont jusqu'à 110°) et tiroir sorti. La porte "
            f"la plus large de M1 laisse {cote(d_porte)} avant le canapé ; un tiroir sorti en laisse {cote(d_tiroir)}. "
            f"Volume utile : {volume_utile(g):.0f} litres environ."),
        "eclate": (
            "Vue éclatée : chaque caisson se monte à l'atelier et passe seul dans le couloir "
            f"({cote(g['W'][0])} × {cote(PC + DOS)} × {cote(g['HC'])}) ; les trois se lient sur place, puis reçoivent "
            f"les pieds et {'le dessus' if DESSUS[1] == 1 else 'chacun son dessus'}."),
    }


def _plans(ch):
    g, a = ch["g"], alts(ch)
    dessins = [
        DessinMeuble("elevation", "Élévation", en_cm(face_svg(g, a["elevation"]), ECHELLES["elevation"])),
        DessinMeuble("iso", "Vue iso", iso(False, a["iso"]), mesure=False),
        DessinMeuble("ouverte", "Iso ouverte", iso(True, a["ouverte"]), mesure=False),
        DessinMeuble("profil", "Profils", en_cm(profil_svg(g, a["profil"]), ECHELLES["profil"])),
        DessinMeuble("dessus", "Dessus", en_cm(dessus_svg(g, a["dessus"]), ECHELLES["dessus"])),
        DessinMeuble("eclate", "Éclatée", en_cm(eclate_svg(g, a["eclate"]), ECHELLES["eclate"])),
    ]
    return vue_plans(dessins, titre="Enfilade du mur ouest", formule=formule_longueur(g))


# ------------------------------------------------------------------ Découpe
COLONNES = (Colonne("Rep.", "repere"), Colonne("Pièce"), Colonne("L × l", "cote"), Colonne("Ép.", "cote"),
            Colonne("Qté", "nombre"), Colonne("Matière", "detail"), Colonne("Où", "detail"), Colonne("Note", "note"))


def _decoupe(ch):
    v, ps = ch["v"], ch["ps"]
    lignes_debit = debit(ps)
    lignes = [(d["rep"], d["nom"], f"{cote(d['L'])} × {cote(d['l'])}", cote(d["ep"]), d["n"],
               FORMATS[format_de(d, v)]["court"], ", ".join(d["ous"]), d["note"]) for d in lignes_debit]
    legende = " ".join(f"{PREFIXE[k]} : {GROUPES[k][0].lower() + GROUPES[k][1:]}." for k in GROUPES)
    sous_titre = ("Cotes finies en cm, longueur dans le sens du fil (ou de la longueur de la tablette) × largeur. "
                  f"{len(ps)} pièces, {len(lignes_debit)} repères. {legende}")
    plans = []
    for cle, pans in ch["cal"].items():
        panneaux = [decoupe_svg(cle, pa, n + 1) for n, pa in enumerate(pans)]
        plans.append(calepinage([Calepin(t, s) for t, s in panneaux], titre=f"{FORMATS[cle]['nom']} × {len(pans)}"))
    hdf = [d for d in lignes_debit if d["grp"] == "fond"]
    surf = sum(d["L"] * d["l"] * d["n"] for d in hdf) / 1e4
    return (tableau_debit(COLONNES, lignes, titre="Débit et découpe", sous_titre=sous_titre)
            + "<h2>Plan de découpe</h2>"
            "<p>Refente d'abord (bandes sur la longueur), tronçonnage ensuite ; trait de scie de "
            f"{cote(TRAIT * 10)} mm compté. Mettre devant le chant le plus beau de chaque pièce. "
            '<span class="lg chene"></span>chêne <span class="lg chute"></span>chute.</p>'
            + "".join(plans)
            + f"<p>Dos et fonds de tiroir ({', '.join(d['rep'] for d in hdf)}) : {cote(surf, 2)} m² de fibres dures, "
            "commandés découpés aux cotes chez Leroy Merlin. Les chutes de 15 × 200 laissées par les dessus et les "
            "étagères servent aux essais de teinte d'huile et aux cales. Faire couper en magasin si le service le "
            "prend, sinon scie circulaire sur rail.</p>")


# ------------------------------------------------------------------ Montage
OUTILS = ["perceuse-visseuse, forets bois Ø 3, 5 et 8, mèche Forstner Ø 35",
          "scie circulaire sur rail (ou découpe en magasin), scie sauteuse",
          "4 serre-joints, équerre, mètre, niveau, compas", "ponceuse orbitale et abrasifs, chiffons pour l'huile",
          "gabarit de perçage des taquets (ou tasseau percé)"]


def etapes_montage(g: dict) -> list[str]:
    return [
        "Faire débiter : refentes et tronçonnages du plan de découpe (service découpe du magasin, ou scie circulaire "
        "sur rail). Commander dos et fonds de tiroir découpés. Marquer chaque pièce de son repère au crayon, sur une "
        "face cachée.",
        "Chêne : poncer 120 puis 180, huiler deux couches toutes faces (égrener au 240 entre les couches), laisser "
        "sécher selon la notice avant de manipuler.",
        "Percer à plat, avant d'assembler : rangées de trous Ø 5 pour les taquets (gabarit, foret à butée, 12 mm de "
        "profondeur) dans les côtés de M1 et M3, coupelles Ø 35 dans les portes (axe à 2,2 du chant, à 10 du haut et "
        "du bas, 12 mm de profondeur), embases de charnières et coulisses sur les côtés.",
        "Monter chaque caisson : fond et traverses entre les côtés, collés et vissés 4 × 50 avec avant-trous Ø 3 "
        "(trois par about de fond, deux par traverse). Joue nord de M1 et joue sud de M3 par tourillons Ø 8 collés. "
        "Contrôler l'équerrage (diagonales égales).",
        "Visser le dos (fibres dures) en applique, vis 3,5 × 16 tous les 15 cm, caisson d'équerre : le caisson devient "
        "rigide.",
        "Tiroirs : boîtes vissées 4 × 50, fond vissé dessous ; coulisses sur les côtés de M2 et sur les boîtes ; "
        "essayer à vide.",
        "Sur place : poser les trois caissons sur le dos (sur une couverture), les aligner, serre-joints, percer Ø 5 à "
        "travers les deux côtés et poser quatre vis de liaison par jonction.",
        f"Visser les {len(g['pieds_y']) * len(PIEDS_X)} pieds (platines vissées 3,5 × 16, à cheval sur les jonctions), "
        "redresser, pousser contre le mur, régler les patins au niveau sur toute la longueur ; centrer le meuble "
        f"sur le mur ({cote(NORD)} de chaque côté).",
        "Fixer au mur : une équerre sous chaque traverse arrière, chevilles adaptées à la cloison.",
        "Poser les trois dessus, un par caisson, bord à bord : deux tourillons Ø 8 non collés par joint pour "
        "l'affleurement, équerres à trou oblong sous les traverses (trou oblong en travers du fil), vis 3,5 × 30 dans "
        "le dessus, sans colle.",
        "Portes : clipser sur les embases, régler les jeux de 3 mm ; poser poussoirs et tampons. Façades de tiroir : "
        "caler les jeux, visser par l'intérieur 3,5 × 30. Taquets et étagères en dernier.",
    ]


def _montage(ch):
    g = ch["g"]
    outils = "<ul>" + "".join(f"<li>{escape(o)}</li>" for o in OUTILS) + "</ul>"
    return (etapes([Etape("", f"<p>{escape(e)}</p>") for e in etapes_montage(g)], titre="Outils et montage",
                   outils=outils)
            + note_source("Compter deux week-ends : un pour la découpe, le ponçage et l'huile (séchage), un pour "
                          "l'assemblage et la pose. Deux personnes pour la mise en place : un caisson en chêne pèse "
                          f"{poids_caisson(g)} kg environ, vide et sans façades."))


# ------------------------------------------------------------------ Achats
def _lien(m):
    return f'<a href="{escape(MAGASINS[m]["url"])}">{escape(MAGASINS[m]["nom"])}</a>'


def _note_achat(li):
    if li["unite"] == "m²":
        calcul = f"{cote(li['q'], 1)} m² × {euros(li['pu'])} le m²"
    else:
        calcul = f"{li['q']} × {euros(li['pu'])}"
    source = ""
    if li["url"]:
        source = f', <a href="{escape(li["url"])}">{"fiche" if li["statut"] == "relevé" else "repère"}</a>'
    return f"{escape(li['note'])}<br>{li['statut']}, {calcul}{source}"


def _poste(ch, choisit, nom):
    """La ligne d'achat dont le poste est choisi par `choisit` ; aucune : erreur qui nomme le poste cherché."""
    for li in ch["lignes"]:
        if choisit(li["poste"]):
            return li
    raise ValueError(f"salon/enfilade, achats : poste inconnu : « {nom} »")


def _sections_achats(ch):
    """Un tableau par magasin, dans l'ordre des magasins ; les panneaux d'abord."""
    lignes = sorted(ch["lignes"], key=lambda li: (ORDRE_MAG.index(li["mag"]), not li["panneau"]))
    return [SectionAchats(MAGASINS[m]["nom"], [Achat(li["poste"], li["ref"], li["q"], li["pu"],
                                                     note=_note_achat(li)) for li in lignes if li["mag"] == m])
            for m in ORDRE_MAG if any(li["mag"] == m for li in lignes)]


def _achats(ch, sections):
    c18 = _poste(ch, lambda p: p == FORMATS["C18"]["nom"], FORMATS["C18"]["nom"])
    huile = _poste(ch, lambda p: p.startswith("Huile"), "Huile…")
    chapo = (f'<p class="chapo">{_lien("weldom")} d\'abord, puis {_lien("lm")} pour ce que Weldom n\'a pas (fibres '
             f"dures découpées, pieds, coulisses). Prix TTC recherchés en ligne le {RELEVE}, sans visite en magasin : "
             "relevé = prix lu en ligne ou déjà connu, estimé = ordre de grandeur à relever en rayon.</p>")
    total = (f'<p><b>Total (composition {ch["v"]["cle"]}) : {euros(ch["total"])}</b>, dont {euros(ch["releve"])} '
             f'de prix relevés ({round(100 * ch["releve"] / ch["total"])} %) et {euros(ch["estime"])} d\'estimations. '
             f'Les {c18["q"]} tablettes de chêne en font {euros(c18["total"])} ; l\'huile, {euros(huile["total"])} '
             f'(rendement estimé de {HUILE["rendement"]} m² par litre et par couche).</p>')
    outillage = ("<p>Outillage, seulement si l'atelier ne l'a pas (hors total) :</p><ul>"
                 + "".join(f"<li>{escape(n)} : {euros(p)} (estimé)</li>" for n, p in OUTILLAGE) + "</ul>")
    note = note_source(
        "Weldom ne vend ni plaques entières ni 12 mm : tout le débit Weldom se fait dans des tablettes. Les prix "
        "Weldom des tablettes et des charnières sont ceux déjà relevés, à reconfirmer au magasin (stock non lu : il "
        f"faut {lettre(c18['q'])} tablettes de chêne de 200 × 60, à choisir bien planes et de teinte voisine). Fiches "
        'Weldom : chercher la référence sur <a href="https://www.weldom.fr/">weldom.fr</a>.')
    return chapo + achats(sections, titre="Achats et prix", arrondi=False) + total + outillage + note


# ------------------------------------------------------------------ Document
def vues(variante: str) -> dict[str, Vue]:
    if variante != "":
        raise ValueError(f"salon/enfilade : variante « {variante} » inconnue (une seule variante, d'id vide)")
    from pieces.salon.enfilade.explication import vue_explication   # explication.py importe RENDUS_SITE d'ici
    chs = chiffrage.chiffrages()
    ch = chiffrage.retenu(chs)
    sections = _sections_achats(ch)
    return {
        "plans": _plans(ch),
        "decoupe": vue_lecture("decoupe", _decoupe(ch)),
        "montage": vue_lecture("montage", _montage(ch)),
        "achats": vue_lecture("achats", _achats(ch, sections)),
        "explication": vue_explication(ch, chs, len(etapes_montage(ch["g"]))),
    }
