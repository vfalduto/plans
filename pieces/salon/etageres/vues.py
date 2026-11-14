"""Vues du document salon/etageres : Plans, Découpe, Montage, Achats ; l'Explication est dans explication.py.

Une variante par disposition (`calculs.CLES`). Textes repris de 3d/salon/etageres.py (section_meuble, section_debit,
section_achats, section_montage) ; les textes sous les dessins deviennent leurs textes alternatifs
(`dessins.legendes`). Toutes les valeurs viennent de document.py, volumes.py et calculs.py.
"""
import functools
from html import escape
from pathlib import Path

from commun.blocs import Achat, SectionAchats, achats, euros, note_source, vue_lecture
from commun.blocs_construction import (Calepin, Colonne, DessinMeuble, Etape, calepinage, etapes, tableau_debit,
                                       vue_plans)
from commun.modele import Vue
from pieces.salon.etageres import calculs
from pieces.salon.etageres.calculs import prix
from pieces.salon.etageres.dessins import DESSINS, ECHELLES, cadre_commun, en_cm, legendes, recadrer
from pieces.salon.etageres.document import (DATE, ETAGERES as ET, L_MONTANT, MAGASINS, MONTANTS as MO)
from pieces.salon.meubles import cote as cm
from pieces.salon.dessin import f

RENDUS_SITE = Path(__file__).resolve().parents[3] / "site" / "salon" / "etageres" / "rendus"
PAS = MO["pas"]
RA = ET["rainure"]


# ------------------------------------------------------------------ Plans
REPERES = (("elevation", "Élévation"), ("iso", "Vue iso"), ("dessus", "Vues de dessus"), ("profil", "Profil"),
           ("travee", "Travée de face"), ("detail", "Détail d'une entaille"))
RECADRES = ("iso", "dessus")          # les seuls dont le cadre change d'une disposition à l'autre


@functools.cache
def cadres() -> dict[str, str]:
    """ViewBox commun aux quatre dispositions des dessins `iso` et `dessus`, à l'échelle de l'ancienne page."""
    return {k: cadre_commun([DESSINS[k](calculs.etat(c)) for c in calculs.CLES]) for k in RECADRES}


def _scene(e, k):
    svg = DESSINS[k](e, aria=legendes(e)[k])
    if k in RECADRES:
        svg = recadrer(svg, cadres()[k])
    if k in ECHELLES:
        svg = en_cm(svg, ECHELLES[k])
    return svg


def plans(e) -> Vue:
    dessins = [DessinMeuble(k, nom, _scene(e, k), mesure=k not in ("iso", "detail")) for k, nom in REPERES]
    return vue_plans(dessins, titre=f"Disposition {e.nom}", formule=e.kit, liens=("decoupe", "montage"))


# ------------------------------------------------------------------ Découpe
COLONNES_DEBIT = (Colonne("Repère", "repere"), Colonne("Pièce"), Colonne("Nb", "nombre"),
                  Colonne("Dimensions", "cote"), Colonne("Matière", "detail"), Colonne("Tirée de", "note"))


def decoupe(e) -> str:
    lignes = [(p["rep"], p["nom"], p["n"], p["dims"], p["matiere"], p["de"]) for p in calculs.pieces(e)]
    leg = legendes(e)
    sous_titre = f"Disposition {e.nom} : {len(lignes)} repères, {sum(p[2] for p in lignes)} pièces à débiter."
    figures = [("Tablettes : refente des plans de chêne", "refente"), ("Montants et chevilles", "barres"),
               ("Perçage d'un montant", "percage"), ("Entaille d'une tablette", "entaille")]
    return (tableau_debit(COLONNES_DEBIT, lignes, titre="Débit et découpe", sous_titre=sous_titre)
            + calepinage([Calepin(t, DESSINS[k](e, aria=leg[k])) for t, k in figures], titre="Découpe et perçage"))


# ------------------------------------------------------------------ Montage
def libre_txt(t):
    vals = sorted({round(v) for v, plafond in t["libres"] if not plafond})
    plaf = any(plafond for _, plafond in t["libres"])
    s = " et ".join(f"{v}" for v in vals)
    return (s + (" ; " if s else "") + "plafond") if plaf else s


def composition(e) -> str:
    """Composition de la disposition (ET:835-845) : une ligne par tablette."""
    lignes = "".join(
        f'<tr><td>{t["rep"]}</td><td>{t["type"]}</td><td>{t["z"]}</td>'
        f'<td>M{t["a"] + 1} → M{t["b"] + 1}</td><td class="num">{cm(t["l"])}</td><td class="num">{t["n"]}</td>'
        f'<td class="num">{libre_txt(t)}</td></tr>' for t in e.ts)
    return ('<h2>Composition</h2><div class="defile"><table><thead><tr><th>Repère</th><th>Longueur</th><th>Dessus</th>'
            '<th>Montants</th><th class="num">Débit</th><th class="num">Entailles</th>'
            f'<th class="num">Libre au-dessus</th></tr></thead><tbody>{lignes}</tbody></table></div>')


def _etapes():
    return [
        ("Sonder la cloison ouest", "Percer un trou d'essai Ø 6 à l'emplacement d'une vis, derrière l'enfilade : poussière blanche et "
         "résistance franche = carreau de plâtre ; rouge = brique ; vide après 1,3 = plaque sur ossature (pas à 60, voir les points à valider). "
         "Passer le détecteur de réseaux sur toute la zone."),
        ("Débiter", "Refendre les plans en bandes de 32, puis couper les tablettes à longueur ; couper les montants à "
         f"{cm(L_MONTANT)} et les chevilles à {cm(ET['cheville'])}, bouts chanfreinés à la lime."),
        ("Faire le gabarit de perçage", "Dans la chute du dernier tasseau, percer à la perceuse à colonne deux trous Ø 10 "
         f"traversants aux cotes du plan de perçage (à {MO['x_ar']} et {MO['x_av']} du dos, décalés de l'épaisseur mesurée de la "
         f"tablette plus 1, moins {cm(RA['prof'] * 10)} mm de rainure). Vérifier avec une vraie tablette rainurée et deux chevilles : elle doit entrer sans forcer et ne pas jouer."),
        ("Percer les montants", "Pointer les trous sur un montant avec le gabarit, puis percer à la colonne avec une butée de "
         "profondeur et une cale de bout : les cinq montants identiques, bout bas contre la cale. Mèche à pointe de centrage, "
         "martyr dessous (le bois éclate à la sortie). Lamages Ø 15 et avant-trous des vis sur la face avant."),
        ("Entailler les tablettes", f"Tracer les axes depuis un bout ({ET['debord']}, puis tous les {PAS}), présenter chaque "
         f"tablette sur les montants couchés côte à côte pour vérifier, puis scier et ciseler les entailles {cm(ET['entaille'][0])} × "
         f"{cm(ET['entaille'][1])}. Puis les rainures, dessous : défonceuse, fraise droite Ø 10, guide parallèle contre le "
         f"chant arrière (axe à {f(MO['x_av'])}), deux largeurs décalées de 1 mm, deux passes en profondeur jusqu'à "
         f"{cm(RA['prof'] * 10)} mm ; {f(RA['long'])} de long centrés sur chaque entaille, bouts tracés au crayon et "
         "équarris au ciseau. Essayer d'abord sur la chute : la tablette doit se pincer entre les chevilles sans jeu."),
        ("Finir", "Poncer (120 puis 180). Tablettes : trois couches d'huile sur toutes les faces, entailles comprises. Montants : "
         "deux couches de laque noire mate. Chevilles : dégraisser, apprêt antirouille, une couche de laque."),
        ("Essai de charge", "Une chute de tablette entaillée sur la chute de montant, deux chevilles, 15 kg de livres pendant une "
         "semaine : la tablette ne doit ni pencher ni tasser le bois autour de la cheville avant."),
        ("Poser les montants", f"Tracer au laser l'horizontale du bas des montants (z {MO['z0']}) et les verticales des axes "
         f"(à {cm(MO['axes'][0])} du coin nord puis tous les {PAS}). Présenter chaque montant, pointer, percer le mur, "
         "cheviller, visser ; contrôler l'aplomb au niveau sur deux faces avant de serrer. Un écart de 2 mm de hauteur entre "
         "deux montants se voit sur une tablette de 134 : contrôler au laser les trous d'un même niveau."),
        ("Monter les tablettes", "Pour chaque tablette, du bas vers le haut : chevilles avant dans les trous voulus, tablette "
         "posée dessus (les montants dans les entailles, les chevilles avant dans les rainures), chevilles arrière "
         "glissées par-dessus. Reboucher les lamages, retoucher la laque."),
    ]


def etapes_montage() -> list[Etape]:
    """Les neuf étapes de l'ancienne page (ET:1045-1074), titre et texte tels quels."""
    return [Etape(t, f"<p>{escape(c)}</p>") for t, c in _etapes()]


OUTILS = ("<p>scie circulaire et rail de guidage (ou découpe en magasin si le service existe, à vérifier), scie sauteuse, "
          "ciseau à bois de 20, défonceuse et fraise droite Ø 10 (celle de la SDB), perceuse à colonne (ou support de "
          f"perceuse ; à main, les trous ne traversent pas {cm(MO['l'])} d'équerre), mèches bois Ø 10 et Forstner Ø 15, "
          "perceuse et mèche Ø 8 pour le mur, scie à métaux et étau, lime, ponceuse, laser croix, niveau, détecteur de "
          "réseaux, pinceaux.</p>")


def montage(e) -> str:
    return composition(e) + etapes(etapes_montage(), titre="Outils et montage", outils=OUTILS)


# ------------------------------------------------------------------ Achats
def _source(a):
    court = calculs.nom_magasin(a)
    return f'<a href="{escape(a["url"])}">{escape(court)}</a>' if a["url"] else escape(court)


def sections_achats(e) -> list[SectionAchats]:
    """Une section par magasin, dans l'ordre d'apparition des achats ; poste, prix unitaire, source et statut dans la
    note de chaque ligne, avec la note d'origine."""
    ordre = list(dict.fromkeys(a["magasin"] for a in e.achats))
    sections = []
    for m in ordre:
        lignes = []
        for a in (a for a in e.achats if a["magasin"] == m):
            note = f"{escape(a['poste'])}, {euros(a['pu'])} l'unité, {_source(a)}, prix {a['statut']}"
            if a.get("note"):
                note += f" ; {escape(a['note'])}"
            lignes.append(Achat(a["article"], a["ref"], a["qte"], a["pu"], note))
        sections.append(SectionAchats(MAGASINS[m]["nom"], lignes))
    return sections


NOTE_ACHATS = (f"Prix relevés : lus sur la fiche du produit par une recherche web le {DATE} (sauf la cheville nylon, "
               "relevée le 26/10/2026 pour le meuble SDB) ; un écart existe parfois entre la fiche et la liste du rayon "
               "(laque : 27,70 € et 25,90 €). Prix estimés : ordre de grandeur du rayon, sans fiche. À prévoir si "
               "l'atelier ne les a pas : mèche à bois Ø 10 à pointe de centrage, mèche Forstner Ø 15, lame de scie à "
               "métaux (non comptées).")


def _apres_titre(html: str, ajout: str) -> str:
    """`ajout` juste après le premier `</h2>` de `html` ; pas de titre : erreur."""
    if "</h2>" not in html:
        raise ValueError("salon/etageres, achats : pas de </h2> après lequel placer l'introduction")
    return html.replace("</h2>", "</h2>" + ajout, 1)


def achats_vue(e) -> str:
    mg = MAGASINS["weldom"]
    intro = (f'<p>D\'abord chez <b><a href="{mg["url"]}">{mg["nom"]}</a></b> ({mg["adresse"]}) ; il n\'a pas de plan '
             "de chêne de 2,6 : les tablettes viennent de <b>Castorama</b> (Leroy Merlin n'a pas de chêne dans ce "
             f"format en ligne). Prix TTC lus en ligne le {DATE}, stock non vérifié : tout est à confirmer en magasin.</p>")
    n_rel = sum(1 for a in e.achats if a["statut"] == "relevé")
    total = (f"<p><b>Total : {prix(e.total)}</b>, dont {prix(e.releve)} de prix relevés ({n_rel} lignes) et "
             f"{prix(e.estime)} estimés. Sans livraison ni outillage.</p>")
    transport = ("<p>Les plans de 250 font ≈ 31 kg chacun : il faut un véhicule assez long, ou la livraison Castorama "
                 "(non comptée). Seuls les plans de chêne et les ronds d'acier changent d'une disposition à "
                 "l'autre.</p>")
    corps = achats(sections_achats(e), titre="Achats et prix", arrondi=False)
    corps = _apres_titre(corps, intro + f'<p class="sous-titre">Disposition {escape(e.nom)}</p>')
    return corps + total + transport + note_source(NOTE_ACHATS)


# ------------------------------------------------------------------ Document
def vues(variante: str) -> dict[str, Vue]:
    if variante not in calculs.CLES:
        raise ValueError(f"salon/etageres : variante « {variante} » inconnue ; connues : {', '.join(calculs.CLES)}")
    from pieces.salon.etageres.explication import explication   # explication.py importe ce module
    e = calculs.etat(variante)
    return {
        "plans": plans(e),
        "decoupe": vue_lecture("decoupe", decoupe(e)),
        "montage": vue_lecture("montage", montage(e)),
        "achats": vue_lecture("achats", achats_vue(e)),
        "explication": vue_lecture("explication", explication(e)),
    }
