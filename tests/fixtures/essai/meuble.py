"""Document de construction d'essai : une étagère murale à trois variantes, dans la pièce « Atelier ».

Toutes ses longueurs viennent de `TABLETTES`, `PROFONDEUR` et `EPAISSEUR`. `actuelle` a toutes les vues remplies
(Plans à deux dessins, l'iso sans Mesurer) ; `rangs` n'a pas de Montage (« Sans objet ») ; `escalier` n'a qu'une
élévation et une ligne d'achat non chiffrée.
"""
from commun.blocs import Achat, SectionAchats, achats, chiffres, nombre, tete, total_achats, vue_lecture
from commun.blocs_construction import (Calepin, Colonne, DessinMeuble, Etape, calepinage, etapes, tableau_debit,
                                       vues_plans)
from commun.modele import Changement, Document, Piece, Site, Variante, Vue

VARIANTES = (
    Variante("actuelle", "Actuelle", "V1.2", (
        Changement("V1.2", "12/11/2026", "Tablette du haut allongée."),
        Changement("V1.1", "10/11/2026", "Tasseaux cachés."),
    )),
    Variante("rangs", "Rangs", "V0.3", (Changement("V0.3", "13/11/2026", "Deux tablettes égales."),)),
    Variante("escalier", "Escalier", "V0.1", (Changement("V0.1", "13/11/2026", "Première version."),)),
)
NOMS = {v.id: v.nom for v in VARIANTES}

TABLETTES = {"actuelle": (120, 80, 80), "rangs": (100, 100), "escalier": (60, 90, 120)}  # longueurs, de haut en bas
PROFONDEUR = 32
EPAISSEUR = 2.7

BOIS, TRAIT, ENCRE = "#D9BF94", "#6B5535", "#4A4038"

COLONNES = (Colonne("Repère", "repere"), Colonne("Pièce"), Colonne("Nb", "nombre"),
            Colonne("Dimensions (cm)", "cote"), Colonne("Matière", "detail"), Colonne("Tirée de", "note"))
# `escalier` déclare sa quantité après les dimensions (ordre de l'enfilade) : la carte mobile la garde en tête
COLONNES_ESCALIER = COLONNES[:2] + (COLONNES[3], COLONNES[2]) + COLONNES[4:]

CHAPOS = {
    "actuelle": "Une étagère de chêne sur tasseaux cachés, la tablette du haut plus longue que les deux autres.",
    "rangs": "Deux tablettes égales, posées sur des équerres visibles.",
    "escalier": "Trois tablettes de plus en plus longues vers le bas, en escalier.",
}

ACHATS = {
    "actuelle": (
        SectionAchats("Magasin A", (Achat("Planche de chêne", "CH-27", 1, 64.9, note="rabotée, débitée en magasin"),
                                    Achat("Tasseau caché", "TC-8", 3, 12.5))),
        SectionAchats("Magasin B", (Achat("Chevilles et vis", "VC-60", 1, 6.95),
                                    Achat("Huile dure", "HD-1", 1, 18.4))),
    ),
    "rangs": (SectionAchats("", (Achat("Planche de chêne", "CH-27", 1, 64.9), Achat("Équerre", "EQ-20", 4, 3.2))),),
    "escalier": (SectionAchats("Magasin A", (Achat("Planche de chêne", "CH-27", 1, 64.9),
                                             Achat("Tasseau caché", "TC-8", 3, None, note="à commander"))),),
}


# deux sections avec des centimes : au centime, pour que sous-totaux et total s'additionnent à l'œil
ARRONDI = {"actuelle": False}


def _y(i, n, hauteur):
    """Hauteur de la tablette `i` sur `n`, réparties dans `hauteur`."""
    return round(hauteur * (i + 1) / (n + 1), 1)


def _elevation(v):
    longueurs = TABLETTES[v]
    morceaux = [f'<line x1="10" y1="132" x2="290" y2="132" stroke="{TRAIT}" stroke-width="0.6"/>']
    for i, l in enumerate(longueurs):
        x, y = (300 - l) / 2, _y(i, len(longueurs), 130)
        morceaux.append(f'<rect x="{x:g}" y="{y:g}" width="{l:g}" height="{EPAISSEUR:g}" fill="{BOIS}"'
                        f' stroke="{TRAIT}" stroke-width="0.4"/>'
                        f'<text x="150" y="{y - 4:g}" text-anchor="middle" font-size="8" fill="{ENCRE}">'
                        f'{nombre(l)}</text>')
    return (f'<svg viewBox="0 0 300 140" role="img" aria-label="Élévation, variante {NOMS[v]}">'
            + "".join(morceaux) + "</svg>")


def _iso(v):
    longueurs = TABLETTES[v]
    dx, dy = PROFONDEUR * 0.87, PROFONDEUR * 0.5   # profondeur fuyant à 30°
    morceaux = []
    for i, l in enumerate(longueurs):
        x, y = (300 - l - dx) / 2, _y(i, len(longueurs), 200) + dy / 2
        dessus = f"{x:g},{y:g} {x + l:g},{y:g} {x + l + dx:g},{y - dy:g} {x + dx:g},{y - dy:g}"
        morceaux.append(f'<polygon points="{dessus}" fill="{BOIS}" stroke="{TRAIT}" stroke-width="0.4"/>'
                        f'<rect x="{x:g}" y="{y:g}" width="{l:g}" height="{EPAISSEUR:g}" fill="{TRAIT}"/>')
    return (f'<svg viewBox="0 0 300 200" role="img" aria-label="Vue iso, variante {NOMS[v]}">'
            + "".join(morceaux) + "</svg>")


def _reperes(v):
    """(repère, longueur, nombre) par longueur distincte, dans l'ordre des tablettes."""
    longueurs = list(dict.fromkeys(TABLETTES[v]))
    return [(chr(ord("A") + i), l, TABLETTES[v].count(l)) for i, l in enumerate(longueurs)]


def _debit(v):
    dims = {r: f"{nombre(l)} × {nombre(PROFONDEUR)} × {nombre(EPAISSEUR)}" for r, l, _ in _reperes(v)}
    if v == "escalier":
        colonnes = COLONNES_ESCALIER
        lignes = [(r, "Tablette", dims[r], n, "Chêne massif", "Planche 1") for r, _, n in _reperes(v)]
    else:
        colonnes = COLONNES
        lignes = [(r, "Tablette", n, dims[r], "Chêne massif", "Planche 1") for r, _, n in _reperes(v)]
    return tableau_debit(colonnes, lignes, sous_titre="Une ligne par longueur de tablette.")


def _calepin(v):
    """Les tablettes côte à côte dans la planche."""
    jeu = 1
    longueur = sum(TABLETTES[v]) + jeu * (len(TABLETTES[v]) + 1)
    morceaux, x = [], jeu
    for l in TABLETTES[v]:
        morceaux.append(f'<rect x="{x:g}" y="{jeu}" width="{l:g}" height="{PROFONDEUR:g}" fill="{BOIS}"'
                        f' stroke="{TRAIT}" stroke-width="0.4"/>'
                        f'<text x="{x + l / 2:g}" y="{jeu + PROFONDEUR / 2 + 3:g}" text-anchor="middle"'
                        f' font-size="8" fill="{ENCRE}">{nombre(l)}</text>')
        x += l + jeu
    svg = (f'<svg viewBox="0 0 {longueur:g} {PROFONDEUR + 2 * jeu:g}" role="img"'
           ' aria-label="Planche 1 et ses tablettes">'
           f'<rect width="{longueur:g}" height="{PROFONDEUR + 2 * jeu:g}" fill="none" stroke="{ENCRE}"'
           ' stroke-width="0.6"/>' + "".join(morceaux) + "</svg>")
    return calepinage([Calepin("Planche 1, chêne massif", svg)])


def _etapes(v):
    """Étapes du montage ; aucune pour `rangs` (Montage sans objet)."""
    if v == "rangs":
        return []
    poser = Etape("Poser les tasseaux", "<p>Tracer les niveaux au laser, percer, cheviller, visser les tasseaux.</p>",
                  figure=_elevation(v) if v == "actuelle" else "")
    return [Etape("Préparer les tablettes", "<p>Poncer, huiler deux couches, laisser sécher une nuit.</p>"),
            poser,
            Etape("Enfiler les tablettes", "<p>Enfiler chaque tablette sur ses tiges, de bas en haut.</p>")]


def _montage(liste, v):
    outils = "<p>Laser, perceuse, foret à béton, visseuse, ponceuse.</p>" if v == "actuelle" else ""
    return etapes(liste, outils=outils)


def vues(variante: str) -> dict[str, Vue]:
    nom = NOMS[variante]
    formule = " + ".join(nombre(l) for l in TABLETTES[variante]) + " cm"
    liste = _etapes(variante)
    contenus = {"decoupe": _debit(variante) + (_calepin(variante) if variante == "actuelle" else ""),
                "montage": _montage(liste, variante)}
    dessins = [DessinMeuble("elevation", "Élévation", _elevation(variante))]
    if variante != "escalier":
        dessins.append(DessinMeuble("iso", "Vue iso", _iso(variante), mesure=False, iso=True))
    liens = (("#plans", "Plans détaillés"),) if variante == "actuelle" else ()
    explication = tete(CHAPOS[variante], liens) + chiffres((
        (formule, "Tablettes"),
        (str(len(_reperes(variante))), "Repères"),
        (str(len(liste)), "Étapes"),
        (total_achats(ACHATS[variante], arrondi=ARRONDI.get(variante, True)), "Total"),
    ))
    return {
        **vues_plans(dessins, titre=f"Étagère {nom}", formule=formule,
                     liens=[k for k in ("decoupe", "montage") if contenus[k]]),
        "decoupe": vue_lecture("decoupe", contenus["decoupe"]),
        "montage": vue_lecture("montage", contenus["montage"]),
        "achats": vue_lecture("achats", achats(ACHATS[variante], arrondi=ARRONDI.get(variante, True))),
        "explication": vue_lecture("explication", explication),
    }


DOCUMENT = Document("atelier", "etagere", "Étagère", "construction", VARIANTES, vues)

SITE = Site((Piece("atelier", "Atelier", (DOCUMENT,)),))
