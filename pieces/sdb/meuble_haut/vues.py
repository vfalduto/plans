"""Les vues du meuble haut : Plans (iso, éclatée, pose de face et en coupe), Découpe, Montage, Achats, Explication.

Une seule variante (id vide), pas d'option. Les textes qui étaient sous les dessins de l'ancienne page deviennent leur
texte alternatif : rien n'est écrit sous un dessin. Les textes repris de sdb-meuble-haut.html (V6.4) gardent leurs
formules ; les cotes qui se calculent sont calculées depuis le modèle.
"""
from html import escape

from commun.blocs import Achat, note_source, tableau_achats, vue_lecture
from commun.blocs_construction import Calepin, Colonne, DessinMeuble, Etape, calepinage, etapes, tableau_debit, vue_plans
from commun.modele import Vue
from pieces.sdb.achats_communs import deux_meubles, note_article, prix
from pieces.sdb.meuble_haut import calepinage as CAL, dessins as D, modele as H
from pieces.sdb.meuble_haut.explication import vue_explication

M, cm = H.M, H.cm

NOMS = {"iso": "Vue iso", "eclate": "Vue éclatée", "elevation": "Pose, de face", "coupe": "Pose, en coupe"}
# texte alternatif : l'aria-label de l'ancienne page, puis le texte qui était sous le dessin (figcaption)
ALTS = {
    "iso": "Caisson haut, vue iso",
    "eclate": "Caisson haut, vue éclatée : les pièces écartées du centre, leurs trous marqués",
    "elevation": lambda: f"Pose du caisson haut, de face. Chevilles (points noirs) toutes au-dessus du carrelage, deux "
                         f"cales de {cm(M.Z_HAUT - M.Z_DESSUS)} sur le plan pour porter le caisson pendant qu'on perce "
                         "et qu'on visse.",
    "coupe": "Pose du caisson haut, en coupe. La vis traverse le fond du caisson et entre dans la cheville, dans le "
             "mur nu au-dessus du carrelage ; la cale tient le caisson à la bonne hauteur.",
}


def alt(k: str) -> str:
    a = ALTS[k]
    return a() if callable(a) else a


# ------------------------------------------------------------------ Plans
def _plans() -> Vue:
    ch = M.CH
    scenes = {"iso": D.iso_meuble(alt("iso")), "eclate": D.vue_eclatee(alt("eclate")),
              "elevation": D.pose_de_face(alt("elevation")), "coupe": D.pose_en_coupe(alt("coupe"))}
    dessins = [DessinMeuble(k, NOMS[k], scenes[k], mesure=k in ("elevation", "coupe")) for k in NOMS]
    return vue_plans(dessins, "Meuble haut",
                     formule=f"{cm(ch['y1'] - ch['y0'])} × {cm(ch['x1'] - ch['x0'])}, de {cm(ch['z0'])} à {cm(ch['z1'])} du sol")


# ------------------------------------------------------------------ Découpe
def _debit() -> str:
    cm_ = cm
    cols = (Colonne("Rep.", "repere"), Colonne("Pièce"), Colonne("Qté", "nombre"), Colonne("Longueur", "cote"),
            Colonne("Largeur", "cote"), Colonne("Usinages, remarques", "note"))
    lignes = H.debit_haut()
    tab = tableau_debit(cols, [(p["rep"], p["nom"], p["q"], p["L"], H.section(p), p["u"]) for p in lignes], titre="Pièces")
    mats = []
    for m in sorted({p["mat"] for p in lignes}):
        nom, usage, _ = M.MATERIAUX[m]
        mats.append(f"<li><b>{m}</b>, {escape(nom)} : {escape(H.USAGES.get(m, usage))}</li>")
    surf = {}
    for p in lignes:
        if p["mat"] not in "EG":
            surf[p["mat"]] = surf.get(p["mat"], 0) + p["q"] * p["L"] * p["l"] / 1e6
    tot = ", ".join(f"{m} {H.virg(v, 2)} m²" for m, v in sorted(surf.items()))
    ml = sum(p["q"] * p["L"] for p in lignes if p["mat"] == "G") / 1000
    if ml:
        tot += f", G {H.virg(ml, 2)} m linéaires"
    return (tab + f"<ul>{''.join(mats)}</ul>"
            + f'<p class="remarque">Cotes en mm, pièces finies. Surfaces nettes : {tot}.</p>')


def _calepinage() -> str:
    seul = H.calepinage_seul()
    tas, tab = seul[M.STOCK["G"]], seul[M.STOCK["K"]]
    g12 = next(p for p in H.debit_haut() if p["rep"] == "G12")
    barres = [Calepin(*D.tablette_svg(p, k + 1)) for k, p in enumerate(tas["retenu"]["panneaux"])]
    tablettes = [Calepin(*D.tablette_svg(p, k + 1)) for k, p in enumerate(tab["retenu"]["panneaux"])]
    n = H.rouleaux_haut()
    lot = H.lettres(M.PANNEAUX["G"][0]["lot"])
    return (calepinage(barres, "Barre de tasseau")
            + f"<p>Tasseau de joint du fond G12 ({g12['L']} mm) : tronçonné dans une barre de {M.PANNEAUX['G'][0]['L']} "
              f"(lot de {lot} au magasin). Trait de scie de {CAL.TRAIT} mm compté.</p>"
            + calepinage(tablettes, "Tablettes mélaminées")
            + f"<p>Tablettes mélaminées du caisson haut : refente en bandes sur la longueur, puis tronçonnage (trait de "
              f"scie de {CAL.TRAIT} mm compté). Chants coupés visibles plaqués de chant thermocollant : "
              f"{H.virg(H.metres_chant(), 2)} m, chants d'usine des tablettes tournés vers l'extérieur ; "
              f"{H.lettres(n)} rouleau{'x' if n > 1 else ''} de {cm(M.CHANT['rouleau'] / 1000)} m.</p>"
            + '<p class="remarque">Faire débiter au magasin (service « découpe bois », tarif à demander) ou à la scie '
              "circulaire sur rail.</p>")


def _percages() -> str:
    return ("<h2>Perçages pièce par pièce</h2>"
            "<p>Chaque pièce à plat, face par face, cotes en mm depuis le coin en bas à gauche ; la vue éclatée du caisson "
            'est dans <a href="#plans?k=eclate">Plans</a>. <span class="lg fta"></span> on perce à travers (passage, '
            'fraisure ou lamage) ; <span class="lg ftb"></span> avant-trou de la vis qui arrive ; '
            '<span class="lg fent"></span> entaille.</p>'
            f'<div class="fiches">{D.fiches()}</div>')


def _decoupe() -> str:
    return _debit() + _calepinage() + _percages()


# ------------------------------------------------------------------ Montage
def _outils() -> str:
    r = M.RAINURE
    lst = [
        "perceuse-visseuse et embouts cruciformes PZ2",
        "forets bois Ø 2,5 et 4 ; fraise à noyer",
        "défonceuse et règle de guidage : rainures des portes",
        f"fraise droite Ø {r['l'] * 10:.0f} (ou Ø {r['l'] * 5:.0f} en deux passes) : la vôtre",
        "scie circulaire et règle de guidage pour les tablettes mélaminées (ou découpe en magasin)",
        "fer à repasser (chant thermocollant) et cutter",
        "gabarit à taquets et foret Ø 5 avec butée (trous des étagères)",
        "perceuse à percussion ou perforateur, foret selon le mur (béton / maçonnerie Ø 8, ou foret bois-métal pour le placo)",
        "détecteur de câbles et de tuyaux (les prises de la niche et le robinet sont juste en dessous)",
        "niveau à bulle de 60 ou plus, mètre, crayon",
        "deux cales de la hauteur de la niche, escabeau",
        "deux personnes pour présenter le caisson",
    ]
    return "<ul>" + "".join(f"<li>{escape(o)}</li>" for o in lst) + "</ul>"


def _pieces() -> str:
    cartes = "".join(
        f'<div class="vignette"><div class="cdes">{D.piece_seule(p["rep"], p["nom"])}</div><div class="cpied">'
        f'<b class="crep">{p["rep"]}</b><span class="cq">{p["q"]} ×</span></div><div class="cnom">{escape(p["nom"])}</div>'
        f'<div class="cdim">{p["L"]} × {p["l"]} × {p["e"]}</div></div>' for p in H.debit_haut())
    return (f'<h2>Pièces</h2><div class="vignettes">{cartes}</div>'
            '<p class="remarque">Cotes en mm (longueur × largeur × épaisseur) ; usinages dans la <a href="#decoupe">découpe</a>.</p>')


def _puces_quinc(q: dict) -> str:
    return "".join(f'<span class="hw">{D.icone(k)}<b>{n} ×</b><span>{escape(M.QUINCAILLERIE[k])}</span></span>'
                   for k, n in q.items())


def _quincaillerie() -> str:
    return f'<h2>Quincaillerie</h2><div class="quinc">{_puces_quinc(H.quincaillerie_totale())}</div>'


def _comment_percer() -> str:
    pl = M.AVANT_TROU_PLAN
    return ('<h2>Comment percer</h2>'
            f'<div class="percage">{D.percage_type()}</div><ul class="pistes">'
            '<li><b>Toujours deux forets</b> : dans la pièce qu’on traverse, un trou du diamètre de la vis (la vis serre '
            'les pièces au lieu de les écarter), fraisé pour noyer la tête ; dans la pièce reçue, un avant-trou plus fin '
            '(le bois massif ne fend pas, l’aggloméré n’éclate pas). Les diamètres de chaque vissage sont dans le tableau '
            'Perçages de l’étape.</li>'
            '<li><b>Où</b> : chaque étape dessine les trous (points noirs sur la face par où on perce). En bout de pièce, '
            'les trous sont dans l’axe, répartis sur la section ; le long d’une pièce, un trou près de chaque bout puis '
            f'au plus tous les {M.PAS} cm.</li>'
            '<li><b>Percer droit</b> : serrer les deux pièces en place (serre-joint, équerre), percer à travers la '
            'première jusque dans la seconde avec le foret fin, puis repercer la première au diamètre de la vis, fraiser, '
            'visser (sans colle).</li>'
            f'<li><b>Profondeur</b> : un ruban adhésif sur le foret ; indispensable sous le plan de travail ({pl} mm au '
            'plus dans le chêne) et dans la porte (vis 4 × 16 des supports).</li></ul>')


def _operation(n: int, k: int, o: dict) -> str:
    voir = " Voir « Fixer le caisson haut au mur », plus bas." if o["voir"] == "fixer-haut" else ""
    ctrl = f'<p class="ctrl"><b>Contrôle</b> {escape(o["ctrl"])}</p>' if o["ctrl"] else ""
    att = f'<p class="att"><b>Attention</b> {escape(o["att"])}</p>' if o["att"] else ""
    return (f'<div class="op"><span class="opn">{n}.{k}</span><div class="opc"><p>{escape(o["texte"])}{voir}</p>'
            f'{ctrl}{att}</div></div>')


def _table_percages(n: int) -> str:
    lignes = D.percages(n)
    if not lignes:
        return ""
    corps = "".join(f'<tr><td>{escape(ou)}</td><td class="num">{q}</td><td>{escape(pas)}</td><td>{escape(avant)}</td>'
                    f'<td>{escape(vis)}</td><td>{escape(pos)}</td></tr>' for ou, q, pas, avant, vis, pos in lignes)
    return ('<details class="perc" open><summary>Perçages</summary><div class="defile"><table><thead><tr>'
            '<th>Assemblage (on perce la première pièce)</th><th class="num">Trous</th><th>Pièce traversée</th>'
            '<th>Pièce reçue</th><th>Vis</th><th>Position</th></tr></thead>'
            f'<tbody>{corps}</tbody></table></div></details>')


def _etape(n: int) -> Etape:
    titre, but, ops, _ = M.ETAPES[n]
    pieces = "".join(f'<span class="piece"><b>{r}</b> × {q}</span>' for r, q in D.pieces_etape(n))
    quinc = _puces_quinc(H.quantites(n))
    besoin = ""
    if pieces or quinc:
        besoin = ('<div class="besoin">' + (f'<div class="pieces">{pieces}</div>' if pieces else "")
                  + (f'<div class="quinc">{quinc}</div>' if quinc else "") + "</div>")
    lis = "".join(_operation(n, k + 1, o) for k, o in enumerate(ops))
    corps = f'<p><b>Résultat</b> {escape(but)}</p>{besoin}<div class="ops">{lis}</div>{_table_percages(n)}'
    return Etape(titre, corps, D.dessin_etape(n))


def _fixation() -> str:
    zf = sorted({round(t["z"]) for t in M.TROUS if t["vis"] == "cheville"})
    etapes_ = [
        f"<b>Où</b> : six vis à travers le fond K8, toutes au-dessus du carrelage (il s'arrête à {M.CARRELAGE}) : deux "
        f"rangées de trois, à {zf[0]} et {zf[-1]} du sol, à 10 des côtés et de part et d'autre du montant central. Le "
        "carreau n'est jamais percé.",
        "<b>Le mur</b> : faire un trou d'essai dans la zone cachée par le caisson. Poussière rouge ou grise et dure : "
        "brique ou béton, chevilles nylon Ø 8 (ou chevilles « tout matériau ») ; ça traverse vite et sonne creux : placo "
        "ou brique creuse, chevilles à expansion métalliques (type Molly) Ø 8 ou chevilles pour corps creux. Vis "
        f"6 × {M.VIS_MUR['L']} tête fraisée dans tous les cas, la tête noyée dans le fond (fraisure).",
        f"<b>L'épaisseur du carrelage</b> : le relevé est pris sur le carreau ; au-dessus de {M.CARRELAGE}, le mur nu est "
        f"en retrait d'environ {cm(M.EP_CARRELAGE)} (carreau + colle, à mesurer au bord du carrelage). Le fond du "
        "caisson s'appuie sur le carreau en bas ; derrière chaque cheville, glisser une cale de cette épaisseur (cales "
        "de menuisier en plastique empilées, ou chute de bois) pour que le caisson reste d'aplomb et ne se tord pas "
        "en serrant. Longueur des vis (règle du fabricant de chevilles Fischer : cheville + épaisseur fixée + un "
        f"diamètre de vis) : {M.VIS_MUR['cheville']} + {M.TH * 10:.0f} de fond + {M.EP_CARRELAGE * 10:.0f} de cale + "
        f"{M.VIS_MUR['d']} = {M.VIS_MUR['L_min']:.0f} au moins, d'où des vis de {M.VIS_MUR['L']} et des trous de "
        f"{M.VIS_MUR['trou']} dans le mur.",
        "<b>Les réseaux</b> : passer le détecteur sur toute la zone avant de percer ; les fils des prises de la niche "
        "et le tuyau du robinet montent souvent à la verticale au-dessus d'eux.",
        f"<b>Présenter</b> : à deux, poser le caisson sur deux cales de {cm(M.Z_HAUT - M.Z_DESSUS)} posées sur le "
        "plan (le dessous du caisson tombe à la bonne hauteur), le plaquer au mur du fond, vérifier le niveau sur le "
        "dessus.",
        "<b>Marquer et percer</b> : percer les six trous Ø 6 à travers le fond jusqu'au mur pour marquer, les fraiser côté intérieur, retirer le "
        "caisson, percer le mur au foret du mur choisi (percussion seulement sur brique ou béton), poser les chevilles.",
        "<b>Visser</b> : remettre le caisson sur ses cales, visser d'abord les deux trous du haut aux coins, contrôler le "
        "niveau, puis les quatre autres. Retirer les cales.",
        "<b>Charge</b> : caisson vide ≈ 25 kg (estimation), plus les serviettes et les produits ; six chevilles adaptées au "
        "mur suffisent largement (de mémoire, à vérifier sur l'emballage des chevilles).",
    ]
    return ("<h2>Fixer le caisson haut au mur</h2>"
            '<p class="actions"><a class="btn" href="#plans?k=elevation">Pose, de face</a>'
            '<a class="btn" href="#plans?k=coupe">Pose, en coupe</a></p>'
            '<ol class="pistes">' + "".join(f"<li>{e}</li>" for e in etapes_) + "</ol>")


def _montage() -> str:
    n = len(H.ETAPES)
    intro = (f"<p>{n} étapes, dans l'ordre. Chacune dit d'abord ce qu'on obtient et ce qu'il faut sous la main, puis "
             "donne les opérations une à une avec leurs cotes ; <b>Contrôle</b> : ce qu'on vérifie avant de passer à la "
             "suite ; <b>Attention</b> : le piège. Dessous, le dessin du résultat de l'étape : les pièces de l'étape en "
             "orange, les trous à percer en points noirs.</p>")
    return (intro + _pieces() + _quincaillerie() + _comment_percer()
            + etapes([_etape(i) for i in H.ETAPES], titre="Étapes", outils=_outils(), debut=H.ETAPES[0])
            + _fixation())


# ------------------------------------------------------------------ Achats
def _achats() -> str:
    total = H.total()
    return ("<h2>Meuble haut</h2>"
            f"<p>Le caisson haut, acheté seul, coûte <b>{prix(total)}</b>. Sa liste est celle que suit la découpe de "
            "cette page : tout le caisson, K1 et G12 compris. Pour les deux meubles ensemble, voir le total plus bas.</p>"
            + tableau_achats([Achat(nom, ref, q, pu, note_article(q, pu, st)) for nom, ref, q, pu, st in H.lignes()],
                             "Total du meuble haut", arrondi=False)
            + deux_meubles({"bas": "../meuble-bas/#achats", "haut": ""}))


def vues(variante: str) -> dict[str, Vue]:
    if variante != "":
        raise ValueError(f"meuble haut : variante « {variante} » inconnue (une seule, d'id vide)")
    return {"plans": _plans(), "decoupe": vue_lecture("decoupe", _decoupe()),
            "montage": vue_lecture("montage", _montage()), "achats": vue_lecture("achats", _achats()),
            "explication": vue_explication()}
