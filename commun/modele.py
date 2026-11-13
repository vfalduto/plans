"""Structures de données des documents, des vues et des variantes."""
from collections.abc import Callable
from dataclasses import dataclass, field

VUES = {
    "amenagement": ("plan", "coupes", "iso", "camera", "explication"),
    "construction": ("plans", "decoupe", "montage", "achats", "explication"),
}

NOMS_VUES = {
    "plan": "Plan",
    "coupes": "Coupes",
    "iso": "Iso",
    "camera": "Caméra",
    "explication": "Explication",
    "plans": "Plans",
    "decoupe": "Découpe",
    "montage": "Montage",
    "achats": "Achats",
}

COMPARABLES = ("plan", "coupes", "iso", "camera", "plans")

# Vues sans scène dessinée
LECTURE = ("explication", "decoupe", "montage", "achats")


@dataclass(frozen=True)
class Changement:
    version: str
    date: str  # jj/mm/aaaa
    texte: str


@dataclass(frozen=True)
class Camera:
    """Une variante peut changer `reglages`, jamais loc, cible, ortho ni focale."""
    id: str
    nom: str
    loc: tuple
    cible: tuple
    ortho: float | None = None
    focale: float | None = None
    yeux: float | None = None
    reglages: dict = field(default_factory=dict)  # murs, expo, ombres, humain


@dataclass
class Valeur:
    code: str
    nom: str
    couleur: str
    groupe: str = ""
    note: str = ""
    lien: str = ""


@dataclass
class Option:
    id: str
    nom: str
    surfaces: tuple
    type: str  # "nuancier" ou "choix"
    defaut: str
    valeurs: tuple[Valeur, ...]
    portee: str
    css: str = ""  # propriété CSS posée sur :root (--india)
    filtre: bool = False  # rendus recolorés par masque
    ref: float = 0.80


@dataclass
class Element:
    """Une coupe, un coin iso, une caméra ou un dessin d'un meuble."""
    k: str
    nom: str
    titre: str
    scene: str
    fiche: str = ""
    actif: bool = True


@dataclass
class Vue:
    """Une liste `elements` vide donne un onglet grisé."""
    id: str
    elements: list[Element]
    fiche: str = ""
    outils: tuple = ("zoom",)
    vide: str = "Pas encore rendu"


@dataclass
class Variante:
    """`figees` : paires (version, chemin sous site/). Sans variante, une seule, d'id vide."""
    id: str
    nom: str
    version: str
    changements: tuple[Changement, ...]
    figees: tuple[tuple[str, str], ...] = ()


@dataclass
class Document:
    piece: str
    id: str
    nom: str
    type: str
    variantes: tuple[Variante, ...]
    generer: Callable[[str], dict[str, Vue]]
    options: tuple[Option, ...] = ()


@dataclass
class Passerelle:
    """Document pas encore migré, désigné par sa page à la racine."""
    piece: str
    id: str
    nom: str
    type: str
    page: str


@dataclass
class Piece:
    id: str
    nom: str
    documents: tuple[Document | Passerelle, ...]


@dataclass
class Site:
    pieces: tuple[Piece, ...]


def verifier(doc: Document, vues: dict[str, Vue]) -> None:
    attendues = VUES[doc.type]
    for cle in vues:
        if cle not in attendues:
            raise ValueError(f"{doc.piece}/{doc.id} : vue « {cle} » inconnue pour le type {doc.type}")
    for cle in attendues:
        if cle not in vues:
            raise ValueError(f"{doc.piece}/{doc.id} : vue « {cle} » manquante")
    for cle, vue in vues.items():
        vus = set()
        for e in vue.elements:
            if e.k in vus:
                raise ValueError(f"{doc.piece}/{doc.id} : repère « {e.k} » en double dans la vue {cle}")
            vus.add(e.k)
    ids = [v.id for v in doc.variantes]
    if len(set(ids)) != len(ids):
        raise ValueError(f"{doc.piece}/{doc.id} : deux variantes ont le même id")
