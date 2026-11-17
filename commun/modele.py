"""Structures de données des documents, des vues et des variantes."""
import re
from collections.abc import Callable
from dataclasses import dataclass, field

VUES = {
    "amenagement": ("plan", "coupes", "iso", "camera", "explication"),
    "construction": ("plans", "iso", "decoupe", "montage", "achats", "explication"),
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
    couleur: str = ""  # #rrggbb, exigée pour un nuancier
    groupe: str = ""
    note: str = ""
    lien: str = ""
    rendue: bool = True  # False : les rendus ne montrent pas cette valeur


TYPES_OPTION = ("nuancier", "choix")

# jetons d'état des options « choix » : <id>:<code>
ID_CHOIX = re.compile(r"[a-z][a-z0-9-]*")
CODE_CHOIX = re.compile(r"[a-z0-9][a-z0-9-]*")
COULEUR = re.compile(r"#[0-9a-fA-F]{6}")


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

    def __post_init__(self):
        if self.type not in TYPES_OPTION:
            raise ValueError(f"option « {self.id} » : type « {self.type} » inconnu,"
                             f" attendu {' ou '.join(TYPES_OPTION)}")
        codes = [v.code for v in self.valeurs]
        for c in codes:
            if codes.count(c) > 1:
                raise ValueError(f"option « {self.id} » : code « {c} » en double")
        if self.defaut not in codes:
            raise ValueError(f"option « {self.id} » : valeur d'origine « {self.defaut} » absente des valeurs")
        if self.type == "nuancier":
            for v in self.valeurs:
                if not COULEUR.fullmatch(v.couleur):
                    raise ValueError(f"option « {self.id} » : couleur « {v.couleur} » de la valeur « {v.code} »"
                                     " hors du format #rrggbb")
            return
        if not ID_CHOIX.fullmatch(self.id):
            raise ValueError(f"option « {self.id} » : identifiant hors du motif {ID_CHOIX.pattern}")
        for c in codes:
            if not CODE_CHOIX.fullmatch(c):
                raise ValueError(f"option « {self.id} » : code « {c} » hors du motif {CODE_CHOIX.pattern}")
        if self.css or self.filtre:
            raise ValueError(f"option « {self.id} » : un choix n'a ni css ni filtre")


# attribut data-si, entre guillemets doubles ou simples : la valeur est le groupe 1 ou le groupe 2
JETON = re.compile(r"""\bdata-si=(?:"([^"]*)"|'([^']*)')""")


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


@dataclass(frozen=True)
class Annexe:
    """Page à part d'un document, écrite à `<dossier du document>/<nom>` : `ecrire(depuis)` reçoit son chemin sous
    site/ (« cuisine/amenagement/imprimable.html ») et rend la page complète."""
    nom: str
    ecrire: Callable[[str], str]


@dataclass
class Document:
    piece: str
    id: str
    nom: str
    type: str
    variantes: tuple[Variante, ...]
    generer: Callable[[str], dict[str, Vue]]
    options: tuple[Option, ...] = ()
    css: str = ""  # règles des dessins, filtrées et écrites dans dessins.css
    annexes: tuple[Annexe, ...] = ()  # pages à part, écrites après les variantes


@dataclass
class Piece:
    id: str
    nom: str
    documents: tuple[Document, ...]


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
    ids = [o.id for o in doc.options]
    for i in ids:
        if ids.count(i) > 1:
            raise ValueError(f"{doc.piece}/{doc.id} : deux options ont l'id « {i} »")
    connus = {f"{o.id}:{v.code}" for o in doc.options if o.type == "choix" for v in o.valeurs}
    for cle, vue in vues.items():
        textes = [vue.fiche] + [t for e in vue.elements for t in (e.scene, e.fiche)]
        for texte in textes:
            for doubles, simples in JETON.findall(texte):
                attribut = doubles or simples
                options = []
                for jeton in attribut.split():
                    if jeton not in connus:
                        raise ValueError(f"{doc.piece}/{doc.id} : jeton « {jeton} » inconnu dans la vue {cle}")
                    option = jeton.split(":")[0]
                    if option in options:
                        raise ValueError(f"{doc.piece}/{doc.id} : deux jetons de l'option « {option} » dans"
                                         f" data-si=\"{attribut}\" de la vue {cle} : un élément ne porte qu'un jeton par"
                                         " option")
                    options.append(option)
