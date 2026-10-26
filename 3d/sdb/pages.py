# Génère les trois pages du meuble linge (document V4, modèle V6.0) depuis modele.py :
#
#   sdb-meuble-v4.html        page principale : les deux meubles en place, matériaux communs, paniers, budget, changements
#   sdb-meuble-v4-bas.html    meuble bas : vue, notice de montage, découpe, achats, essence du plan
#   sdb-meuble-v4-haut.html   caisson haut : vue, notice de montage, découpe, achats, matériaux possibles
#
#   python3 3d/sdb/pages.py   (just sdb)
#
# Les dessins sont les projections isométriques de montage.py ; les listes et le calepinage viennent de plan.py.

import os
import sys
from collections import Counter
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modele as M  # noqa: E402
import plan as PL  # noqa: E402
import montage as MO  # noqa: E402
import calepinage as CAL  # noqa: E402

ENSEMBLE = "sdb-meuble-v4.html"
PAGES = {"bas": "sdb-meuble-v4-bas.html", "haut": "sdb-meuble-v4-haut.html"}
TITRES = {"bas": "Meuble bas", "haut": "Caisson haut"}
BUDGET = 400.00         # € TTC, les deux meubles, consommables et achats faits ailleurs compris (client, V6.0)
CLE = "sdb-v4"          # préfixe des préférences mémorisées (localStorage)
BADGE = '<span class="badge">retenu</span>'
COURANTE = ' aria-current="page"'


def cm(v):
    """Cote en cm affichée : 1 décimale au plus, virgule française."""
    return f"{round(v, 1):g}".replace(".", ",")


def mm(v):
    return f"{v * 10:.0f}"


def lettres(n, fem=False):
    """Petit nombre en toutes lettres (compté dans le modèle) ; au-delà de dix, en chiffres."""
    mots = ["zéro", "une" if fem else "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf", "dix"]
    return mots[n] if 0 <= n < len(mots) else str(n)


N_ECHELLES = len(M.ECHELLES)
N_SACS = len(M.SACS)
N_PORTES_HAUT = sum(1 for b in M.PIECES if b.rep == "K6")


# ------------------------------------------------------------------ achats et prix
def lignes_achats():
    """Calcul des achats, sans le HTML (sert aussi à PL.achats) : lignes (nom, réf., quantité, prix, stock) des
    consommables communs, du meuble bas et du caisson haut ; articles à acheter ailleurs ; consommables non chiffrés."""
    cal = PL.calepinage()
    tot = Counter()
    for _, _, q in M.ETAPES:
        tot.update(q)
    quinc = {"commun": [], "bas": [], "haut": []}
    manque = {"commun": [], "bas": [], "haut": []}
    for code, w in M.WELDOM.items():
        m = PL.code_meuble(code)
        if w is None:
            manque[m].append(M.QUINCAILLERIE[code])
        else:           # un article, ou une liste d'articles (chevilles, vis et rondelles)
            quinc[m] += [(x[0], x[4], x[2], x[1], x[3]) for x in (w if isinstance(w, list) else [w])]
    non_chiffres = [f"{tot[c]} × {M.QUINCAILLERIE[c]}" for c in M.CONSOMMABLES if c not in M.WELDOM and tot[c]]
    bas_p = [p for st in ("G", "M18", "D") for p in cal[st]["bas"]]
    neufs = [p for st in cal for p in cal[st]["neufs"]]
    lignes = {"commun": quinc["commun"], "bas": PL.ligne_panneaux(bas_p) + quinc["bas"],
              "haut": PL.ligne_panneaux(neufs) + quinc["haut"]}
    return dict(cal=cal, lignes=lignes, manque=manque, non_chiffres=non_chiffres)


def prix():
    """Budget en € : consommables communs, meuble bas, caisson haut, achats faits ailleurs (la toile des sacs ; les
    barres sont de récupération) et total ; lignes de chaque liste."""
    lignes = lignes_achats()["lignes"]
    s = {m: sum(n * px for _, _, n, px, _ in lignes[m]) for m in lignes}
    r = dict(consommables=s["commun"], bas=s["bas"], haut=s["haut"], ailleurs=M.TOILE["prix"], lignes=lignes)
    r["total"] = r["consommables"] + r["bas"] + r["haut"] + r["ailleurs"]
    return r


_ECO = []


def economie_commune():
    """Calculée une fois (le calepinage du caisson haut seul est long). Pièces du caisson haut rangées dans les chutes des panneaux du meuble bas, et euros gagnés par rapport au caisson
    haut acheté seul (calepinage de ses seules pièces)."""
    if _ECO:
        return _ECO[0]
    cal = PL.calepinage()
    pieces = sum(1 for st in cal for p in cal[st]["bas"] for q in p.poses() if M.meuble(q[0]) == "haut")
    seul = CAL.calepinage([p for p in PL.debit() if M.meuble(p["rep"]) == "haut"])
    cout = lambda ps: sum(n * px for _, _, n, px, _ in PL.ligne_panneaux(ps))  # noqa: E731
    euros = cout([p for c in seul.values() for p in c["retenu"]["panneaux"]]) - cout([p for st in cal for p in cal[st]["neufs"]])
    if not _ECO:
        _ECO.append(dict(pieces=pieces, euros=round(euros, 2)))
    return _ECO[0]


def haut_dans_chutes():
    """Vrai si des pièces du caisson haut se taillent dans les chutes du bas, et si le panneau retenu pour le haut est
    celui des tablettes du meuble bas (même panneau acheté)."""
    r = next(m for m in M.MATERIAUX_HAUT if m["retenu"])
    meme = M.STOCK["K"] == M.STOCK["A"] and r["ref"] in {f["ref"] for f in M.PANNEAUX[M.STOCK["K"]]}
    return meme and economie_commune()["pieces"] > 0


# ------------------------------------------------------------------ gabarit commun
CSS = MO.CSS + """
.vbar .btn[aria-current="page"]{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.cartes2{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px;margin:14px 0}
.carte2{display:block;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 16px;color:var(--ink);text-decoration:none}
.carte2:hover{border-color:var(--ink)}
.carte2 b{display:block;font-size:18px}.carte2 span{font-size:14px;color:var(--muted)}
.carte2.bas{box-shadow:inset 6px 0 var(--bas)}.carte2.haut{box-shadow:inset 6px 0 var(--haut)}
.budget td.num{font-size:15px}.budget tr.tot td{border-top:2px solid var(--ink);font-weight:700}
.ok{color:var(--water);font-weight:700}.ko{color:var(--tri);font-weight:700}
tr.retenu td{background:var(--paper)}tr.retenu td:first-child{box-shadow:inset 5px 0 var(--water)}
.badge{display:inline-block;font:700 11px "JetBrains Mono",ui-monospace,monospace;text-transform:uppercase;letter-spacing:.06em;border:1px solid var(--water);color:var(--water);border-radius:999px;padding:1px 8px;margin-left:6px}
.choix{font-size:13px;color:var(--muted)}
.cmp{min-width:860px}
.ens svg{max-height:86vh}
@media (max-width:480px){.vbar{gap:4px;padding:8px 10px;flex-wrap:nowrap}.vbar .back{margin-right:2px;white-space:nowrap}.vbar a.btn{padding:4px 7px;white-space:nowrap}}
"""

SOMMAIRE = """
(function () {
  var toc = document.querySelector(".toc");
  if (!toc) return;
  function garde(k, v) { try { localStorage.setItem("%(cle)s-" + k, v); } catch (e) {} }
  function lit(k) { try { return localStorage.getItem("%(cle)s-" + k); } catch (e) { return null; } }
  var tol = toc.querySelector("ol"), tb = toc.querySelector(".tbtn");
  var hs = Array.prototype.slice.call(document.querySelectorAll("main h2"));
  hs.forEach(function (h) {
    var id = h.id || h.parentNode.id, li = document.createElement("li"), a = document.createElement("a");
    a.href = "#" + id;
    a.textContent = h.textContent.trim();
    li.appendChild(a);
    tol.appendChild(li);
  });
  function ouvert(on) {
    document.body.classList.toggle("toc-on", on);
    tb.setAttribute("aria-expanded", on);
    tb.textContent = on ? "« Sommaire" : "Sommaire »";
    garde("toc", on ? "1" : "0");
  }
  tb.addEventListener("click", function () { ouvert(!document.body.classList.contains("toc-on")); });
  ouvert(lit("toc") !== "0");
  function suivre() {
    var haut = document.querySelector(".vbar").offsetHeight, k = -1;
    toc.style.top = haut + "px";
    hs.forEach(function (h, i) { if (h.getBoundingClientRect().top < haut + 80) k = i; });
    tol.querySelectorAll("a").forEach(function (a, i) { a.classList.toggle("on", i === k); });
  }
  var attente = false;
  window.addEventListener("scroll", function () {
    if (!attente) { attente = true; requestAnimationFrame(function () { attente = false; suivre(); }); }
  }, {passive: true});
  window.addEventListener("resize", suivre);
  suivre();
})();
"""


def barre(courante):
    liens = [(ENSEMBLE, "Ensemble", "ensemble"), (PAGES["bas"], "Meuble bas", "bas"), (PAGES["haut"], "Caisson haut", "haut")]
    btn = "".join(f'<a class="btn" href="{h}"{COURANTE if k == courante else ""}>{t}</a>'
                  for h, t, k in liens)
    return f'<div class="vbar"><a class="back" href="index.html">← Plans</a><span class="sp"></span>{btn}</div>'


def gabarit(titre, courante, corps):
    return f"""{PL.entete(titre, "", CSS)}
<body class="explications changements">
{barre(courante)}
<nav class="toc" aria-label="Sommaire"><button type="button" class="tbtn" aria-expanded="true">Sommaire</button><ol></ol></nav>
<main class="wrap">
{corps}
</main>
<script>{PL.ANCRES}</script>
<script>{SOMMAIRE % {"cle": CLE}}</script>
</body>
</html>
"""


def kicker(suite):
    return (f'<div class="kicker">Salle de bain · alcôve {cm(M.ALCOVE["nord"])} (nord) et {cm(M.ALCOVE["sud"])} (sud) × '
            f'{cm(M.Y1)} · {suite} · {M.VERSION}</div>')


def table_budget(p):
    lignes = [("Consommables, communs aux deux meubles", p["consommables"]), ("Meuble bas", p["bas"]),
              ("Caisson haut", p["haut"]),
              (f"Ailleurs : toile des sacs ({M.TOILE['magasin'].split(',')[0]}) ; barres de récupération", p["ailleurs"])]
    corps = "".join(f'<tr><td>{escape(n)}</td><td class="num">{PL.euros(v)}</td></tr>' for n, v in lignes)
    ok = p["total"] <= BUDGET
    ecart = (f'<span class="ok">{PL.euros(BUDGET - p["total"])} sous le budget de {PL.euros(BUDGET)}</span>' if ok else
             f'<span class="ko">{PL.euros(p["total"] - BUDGET)} au-dessus du budget de {PL.euros(BUDGET)}</span>')
    return (f'<table class="budget"><tbody>{corps}<tr class="tot"><td>Total TTC</td><td class="num">'
            f'{PL.euros(p["total"])}</td></tr></tbody></table><p>{ecart}. Sans livraison : tout se retire en magasin, '
            f'au Weldom et, pour la toile, chez {escape(M.TOILE["magasin"].split(",")[0])}. Le plombier n’est pas '
            'compté.</p>')


# ------------------------------------------------------------------ page principale
def note_paniers():
    co = M.CORNO
    return (f'<p>Le L basculant peut être remplacé par deux paniers à linge étroits à roulettes <b>Wenko Corno</b>, '
            f'{cm(co["l"])} × {cm(co["p"])} × {cm(co["h"])} ({co["litres"]} L chacun), à {PL.euros(co["prix"])} pièce '
            f'({escape(co["source"])}), soit {PL.euros(2 * co["prix"])} les deux. Ils se roulent côte à côte entre les '
            'échelles du bac, <b>sans porte</b> : on ne fait plus la porte, le plateau, les contrefiches, le rail avant, '
            'les butées, les barres ni les sacs. Les pages des deux meubles décrivent le L.</p>')


def materiaux_communs():
    e = economie_commune()
    if e["euros"] > 0:
        _, liste = PL.liste(lignes_achats()["lignes"]["commun"], "Consommables communs")
        return (f'<p>Les deux meubles partagent les tablettes mélaminées : {e["pieces"]} pièce{"s" if e["pieces"] > 1 else ""} '
                f'du caisson haut se taille{"nt" if e["pieces"] > 1 else ""} dans les chutes des tablettes du meuble bas, '
                f'ce qui fait <b>{PL.euros(e["euros"])}</b> d’économie par rapport au caisson haut acheté seul. '
                'Les consommables (vis, chant, silicone, vernis) servent aussi aux deux : on les achète une fois, avec le '
                'meuble bas.</p>' + liste)
    n = e["pieces"]
    chutes = (f'{n} pièce{"s" if n > 1 else ""} du caisson haut se taille{"nt" if n > 1 else ""} bien dans les chutes '
              'des tablettes du meuble bas, mais le caisson haut acheté seul reviendrait au même prix en tablettes neuves'
              if n else 'les chutes du meuble bas ne reçoivent aucune pièce du caisson haut')
    return (f'<p>Acheter les deux meubles ensemble ne fait aucune économie de panneau : {chutes}. On peut donc les '
            'acheter séparément. Seuls les consommables (vis, chant, silicone, vernis) servent aux deux : on les achète une fois, '
            'avec le meuble bas.</p>')


def page_ensemble():
    tout = [b for b in M.version("d") if b.role != "prise"]
    iso = MO.dessin(tout, murs=True, reperes=False, carrelage=M.CARRELAGE, titre="Meuble linge en place dans l'alcôve")
    p = prix()
    lignes = "".join(f'<tr><td class="mono">{v}</td><td class="mono">{d}</td><td>{escape(x)}</td></tr>'
                     for v, d, x in M.CHANGEMENTS)
    corps = f"""{kicker("document V4")}
<h1>Meuble linge</h1>
<p class="pitch">Deux meubles, achetés et montés séparément. En bas, {lettres(N_ECHELLES, True)} échelles en tasseaux portent un plan de travail en chêne à {cm(M.Z_DESSUS)} ; la machine est posée au sol dessous, et à côté une porte basculante en L ouvre {lettres(N_SACS)} sacs à linge. En haut, au-dessus de la niche, un caisson en mélaminé blanc jusqu'au plafond.</p>
<div class="cartes2">
<a class="carte2 bas" href="{PAGES["bas"]}"><b>Meuble bas →</b><span>Échelles, porte basculante, plan de travail : notice, découpe, achats ({PL.euros(p["bas"])})</span></a>
<a class="carte2 haut" href="{PAGES["haut"]}"><b>Caisson haut →</b><span>Caisson, étagères, portes coulissantes : notice, découpe, achats ({PL.euros(p["haut"])})</span></a>
</div>

<h2 id="ensemble">Les deux meubles en place</h2>
<div class="fig ens">{iso}
<p class="cap">Vue depuis la salle de bain, le nord à gauche. Le carrelage (bleu clair) monte à {M.CARRELAGE} sur les murs : le meuble bas n'y est pas fixé, calé par {M.COINS["n"]} coins contre les murs nord et sud ; le caisson haut est chevillé au-dessus. Au mur du fond, derrière la machine, le siphon d'évacuation à {cm(M.TUYAUX["evacuation_z"])} et l'arrivée d'eau à {cm(M.TUYAUX["arrivee_z"])}, qui monte au robinet de la niche par l'encoche du plan.</p></div>

<h2 id="materiaux-communs">Matériaux communs</h2>
{materiaux_communs()}

<h2 id="paniers">Remplacer le L par deux paniers</h2>
{note_paniers()}

<h2 id="budget">Budget</h2>
{table_budget(p)}
<p class="note">Prix TTC relevés en ligne : {escape(M.MAGASIN["nom"])} ({escape(M.MAGASIN["adresse"])}) le {M.MAGASIN["releve"]} et le {M.RELEVE_V6}, toile chez {escape(M.TOILE["magasin"])} le {M.TOILE["releve"]}. Détail ligne à ligne dans les pages <a href="{PAGES["bas"]}#achats">Meuble bas</a> et <a href="{PAGES["haut"]}#achats">Caisson haut</a>.</p>

<p class="note">Repère : origine à l'angle nord-ouest intérieur, x vers l'est, y vers le sud, z depuis le sol, cotes en cm (débit en mm). Source : <span class="mono">3d/sdb/modele.py</span> ; pages : <span class="mono">3d/sdb/pages.py</span> (<span class="mono">just sdb</span>).</p>

<section id="changements">
<h2>Changements</h2>
<div class="scroll"><table><thead><tr><th>Version</th><th>Date</th><th>Changements</th></tr></thead>
<tbody>{lignes}</tbody></table></div>
</section>"""
    return gabarit("Meuble linge", "ensemble", corps)


# ------------------------------------------------------------------ pages des deux meubles
def etapes(meuble):
    haut0 = M.MEUBLE_HAUT_ETAPES[0]
    return range(0, haut0) if meuble == "bas" else range(haut0, len(M.ETAPES))


def iso_meuble(meuble):
    tout = [b for b in M.version("d") if b.role != "prise"]
    if meuble == "bas":
        bl = [b for b in tout if b.groupe != "caisson_haut"]       # ossature, L, sacs, plan, machine et tuyaux
    else:
        bl = [b for b in tout if b.groupe == "caisson_haut"]
    return MO.dessin(bl, reperes=False, titre=TITRES[meuble])


def sacs():
    pt, c = M.PATRON, M.COUTURE
    bw, bl = pt["bande"]
    sw, sh = pt["soufflet"]
    return (f'<h3>Sacs à coudre</h3><div class="fig"><div class="scroll">{PL.patron_svg()}</div>'
            f'<p class="cap">{lettres(N_SACS).capitalize()} sacs dans {cm(M.TOILE["achat_m"])} m de toile en {pt["tissu"]} de laize. Chaque sac : '
            f'une bande de {cm(bw)} × {cm(bl)} (devant, fond et dos, un fourreau à chaque bout) et deux soufflets en '
            f'trapèze de {cm(sh)} de haut, {cm(pt["soufflet_haut"])} en haut et {cm(pt["soufflet_bas"])} en bas ; '
            f'coutures de {cm(c)} comprises.</p></div>'
            f'<p>Sac fini : {cm(pt["largeur"])} de large, {cm(pt["fond"])} de fond, {cm(pt["hauteur"])} de haut, deux '
            f'fourreaux de {cm(M.FOURREAU - 1.5)} pour les barres rondes. Surfiler, ourler le haut des soufflets, '
            f'assembler soufflets et bande endroit contre endroit à {cm(c)} du bord, piquer les fourreaux, retourner.</p>')


def montage(meuble):
    n_ = etapes(meuble)
    deb = [p for p in PL.debit() if M.meuble(p["rep"]) == meuble]
    cartes = "".join(MO.carte_piece(p) for p in deb)
    quinc = sum((Counter(M.ETAPES[n][2]) for n in n_), Counter())
    outils = "".join(f"<li>{escape(o)}</li>" for o in MO.OUTILS[meuble])
    legende = ('<p class="note">Plans des sous-ensembles : vue éclatée, puis chaque pièce à plat, face par face, cotes '
               'en mm depuis le coin en bas à gauche. <span class="lg fta"></span> on perce à travers (passage, fraisure '
               'ou lamage) · <span class="lg ftb"></span> avant-trou de la vis qui arrive · <span class="lg fent"></span> '
               'entaille.</p>')
    extra = sacs() if meuble == "bas" else f'<h3>Fixer le caisson haut au mur</h3>{MO.fixation_haut()}'
    return f"""<h2 id="montage">Notice de montage</h2>
<p>{len(n_)} étapes. Dans chaque dessin, les pièces de l'étape sont en orange avec leur repère, celles déjà posées en blanc, et les trous à percer en points noirs ; le tableau Perçages de chaque étape donne forets, vis et positions.</p>
<h3>Pièces</h3>
<div class="cartes">{cartes}</div>
<p class="note">Cotes en mm (longueur × largeur × épaisseur) ; usinages dans la <a href="#decoupe">découpe</a>.</p>
<h3>Outils</h3>
<ul class="outils">{outils}</ul>
<h3>Quincaillerie</h3>
<div class="hws">{MO.puces_quinc(quinc)}</div>
{extra}
{legende}
{MO.plans_sous_ensembles(meuble)}
{"".join(MO.bloc_etape(n) for n in n_)}"""


def decoupe(meuble):
    cal = PL.calepinage()
    leg = ('<p class="leg">Code couleur des découpes :<span class="sw bas"></span>meuble bas'
           '<span class="sw haut"></span>caisson haut</p>')
    nb = len(cal["M18"]["bas"])
    if meuble == "bas":
        barres = "".join(PL.tablette_svg(p, k + 1) for k, p in enumerate(cal["G"]["bas"]))
        tabs = "".join(PL.tablette_svg(p, k + 1) for k, p in enumerate(cal["M18"]["bas"]))
        plan_ = "".join(PL.tablette_svg(p, "P") for p in cal["D"]["bas"])
        pd = M.PANNEAUX["D"][0]
        chutes_bas = " Les pièces du caisson haut (en bleu) se taillent dans leurs chutes." if haut_dans_chutes() else ""
        lg = cal["D"]["bas"][0].poses()[0][3]
        figs = f"""<div class="fig"><div class="tabs">{barres}</div>
<p class="cap">Tasseaux de {M.PANNEAUX["G"][0]["L"]} : chaque barre est tronçonnée (trait de scie de {CAL.TRAIT} compté). Scier les montants G3 ensemble pour qu'ils aient la même longueur. Les coins de calage se taillent dans les chutes.</p></div>
<div class="fig"><div class="tabs">{tabs}</div>
<p class="cap">Tablettes mélaminées achetées avec le meuble bas : refente en bandes sur la longueur, puis tronçonnage.{chutes_bas} Chants coupés visibles plaqués de chant thermocollant.</p></div>
<div class="fig"><div class="tabs">{plan_}</div>
<p class="cap">Plan de travail {pd["L"]} × {pd["l"]} × {mm(M.PT)} recoupé en longueur à {lg} : la profondeur reste celle de la tablette, chants d'usine devant et derrière. Chute de {pd["L"] - lg - CAL.TRAIT} × {pd["l"]} en chêne.</p></div>"""
    else:
        tabs = "".join(PL.tablette_svg(p, nb + k + 1) for k, p in enumerate(cal["M18"]["neufs"]))
        pris = Counter()
        for k, p in enumerate(cal["M18"]["bas"]):
            for q in p.poses():
                if M.meuble(q[0]) == "haut":
                    pris[(q[0], k + 1)] += 1
        li = "".join(f'<li><b>{r}</b> {escape(M.NOMS.get(r, ""))} × {n}, tablette T{t}</li>'
                     for (r, t), n in sorted(pris.items(), key=lambda x: (x[0][1], x[0][0][0], int(x[0][0][1:]))))
        chutes = (f'<p>Pièces prises dans les chutes des tablettes du meuble bas (dessinées sur la page '
                  f'<a href="{PAGES["bas"]}#decoupe">Meuble bas</a>) :</p><ul class="pistes">{li}</ul>' if li else
                  '<p>Aucune pièce du caisson haut ne se prend dans les chutes du meuble bas.</p>')
        figs = (f'<div class="fig"><div class="tabs">{tabs}</div><p class="cap">Tablettes neuves du caisson haut : refente '
                f'en bandes, puis tronçonnage (trait de scie de {CAL.TRAIT} compté).</p></div>{chutes}')
    return f"""<h2 id="decoupe">Découpe</h2>
<div class="fig">{PL.table_debit(meuble)}</div>
{leg}
{figs}
<p class="note">Faire débiter au magasin (service « découpe bois », tarif à demander) ou à la scie circulaire sur rail.</p>"""


def achats(meuble):
    a = lignes_achats()
    p = prix()
    mg = M.MAGASIN
    o = [f'<h2 id="achats">Achats</h2><p>Chez <b>{escape(mg["nom"])}</b> ({escape(mg["adresse"])}, {mg["tel"]}), '
         f'à retirer en magasin.</p>']
    if meuble == "bas":
        _, l0 = PL.liste(a["lignes"]["commun"], "Consommables")
        o.append(f'<h3>Consommables, communs aux deux meubles</h3><p>Achetés avec le meuble bas.</p>{l0}')
        if a["non_chiffres"]:
            o.append(f'<p class="note">Non chiffrés, en rayon : {escape(" ; ".join(a["non_chiffres"]))}.</p>')
    _, l1 = PL.liste(a["lignes"][meuble], TITRES[meuble])
    o.append(f'<h3>{TITRES[meuble]}</h3>{l1}')
    ail = [x for m in ("commun", meuble) for x in a["manque"][m]]
    if ail:
        o.append(f'<p><b>À acheter ailleurs</b> : {escape(" ; ".join(ail))}.</p>')
    if meuble == "bas":
        sous = p["consommables"] + p["bas"] + p["ailleurs"]
        o.append(f'<p><b>Sous-total : {PL.euros(sous)}</b> (consommables {PL.euros(p["consommables"])}, meuble bas '
                 f'{PL.euros(p["bas"])}, toile {PL.euros(p["ailleurs"])}).</p>')
    else:
        o.append(f'<p><b>Sous-total : {PL.euros(p["haut"])}</b>.</p>')
    o.append(f'<p>Total des deux meubles : <b>{PL.euros(p["total"])}</b>, pour un budget de {PL.euros(BUDGET)} '
             f'(<a href="{ENSEMBLE}#budget">détail</a>).</p>'
             f'<p class="note">Stock : nombre affiché sur la fiche produit pour ce magasin (« — » : non lu). Prix TTC '
             f'relevés en ligne le {M.MAGASIN["releve"]} et le {M.RELEVE_V6} (plan, vernis et consommables ajoutés en '
             f'{M.VERSION}).</p>')
    return "\n".join(o)


def materiaux_haut():
    corps = "".join(
        f'<tr class="{"retenu" if m["retenu"] else ""}"><td><b>{escape(m["nom"])}</b>'
        f'{BADGE if m["retenu"] else ""}</td><td class="num">{mm(m["ep"])}</td>'
        f'<td class="u">{escape(m["format"])}</td><td>{escape(m["qualites"])}</td><td>{escape(m["defauts"])}</td>'
        f'<td>{escape(m["finition"])}</td><td class="num">{PL.euros(m["prix"])}</td>'
        f'<td class="u">{escape(m["magasin"])}{" réf. " + m["ref"] if m["ref"] else ""}</td></tr>'
        for m in M.MATERIAUX_HAUT)
    r = next(m for m in M.MATERIAUX_HAUT if m["retenu"])
    commun = (", et le même panneau que la porte et le plateau du meuble bas, dont les chutes reçoivent une partie du "
              "caisson" if haut_dans_chutes() else "")
    return f"""<h2 id="materiaux">Matériaux possibles</h2>
<p>Le caisson haut est au-dessus de la niche, loin des projections : il ne prend presque pas d'eau. Pas besoin de vernis marin ni de bois massif ; un panneau de {mm(min(m["ep"] for m in M.MATERIAUX_HAUT))} ou {mm(max(m["ep"] for m in M.MATERIAUX_HAUT))} mm suffit. Un panneau brut se peint (sous-couche, puis deux couches).</p>
<div class="scroll"><table class="debit cmp"><thead><tr><th>Panneau</th><th class="num">Ép. (mm)</th><th>Format</th><th>Qualités</th><th>Défauts</th><th>Finition</th><th class="num">Prix</th><th>Magasin</th></tr></thead>
<tbody>{corps}</tbody></table></div>
<p><b>Retenu : {escape(r["nom"].lower())}</b>. Le moins cher qui convient : {escape(r["qualites"])}, rien à peindre{commun}. Son défaut ({escape(r["defauts"])}) compte peu si haut : {escape(r["finition"])}. <span class="choix">Choix laissé au constructeur.</span></p>
<p class="note">Prix TTC du panneau entier relevés en ligne le {M.RELEVE_V6}, stock non lu.</p>"""


def essence_plan():
    def lien(e):
        return f'<a href="{e["source"]}">Wood Database</a>' if e["source"] else "—"
    corps = "".join(
        f'<tr class="{"retenu" if e["retenu"] else ""}"><td><b>{escape(e["nom"])}</b>'
        f'{BADGE if e["retenu"] else ""}</td><td class="num">{mm(e["ep"])}</td>'
        f'<td class="u">{escape(e["format"])}</td><td class="num">'
        f'{"—" if e["retrait_t"] is None else cm(e["retrait_t"]) + " %"}</td><td>{escape(e["qualites"])}</td>'
        f'<td>{escape(e["defauts"])}</td><td>{escape(e["finition"])}</td><td class="num">{PL.euros(e["prix"])}</td>'
        f'<td class="u">{escape(e["magasin"])}{" réf. " + e["ref"] if e["ref"] else ""}</td><td class="u">{lien(e)}</td></tr>'
        for e in M.ESSENCES_PLAN)
    r = next(e for e in M.ESSENCES_PLAN if e["retenu"])
    hetre = next(e for e in M.ESSENCES_PLAN if e["nom"].startswith("Hêtre"))
    jeu = (M.LL_ZONE - M.LL["l"]) / 2
    x0, x1, y0, y1, z0, z1 = M.TUYAUX["zone"]
    return f"""<h2 id="essence">Essence du plan de travail</h2>
<p>Le plan est la seule pièce exposée à l'eau : il reçoit le vernis marin, {M.VERNIS["couches"]} couches sur toutes les faces. Le retrait tangentiel (de l'état vert à l'état sec) dit combien un bois bouge avec l'humidité : plus il est faible, moins le plan se voile.</p>
<div class="scroll"><table class="debit cmp"><thead><tr><th>Essence</th><th class="num">Ép. (mm)</th><th>Format</th><th class="num">Retrait tang.</th><th>Qualités</th><th>Défauts</th><th>Finition</th><th class="num">Prix</th><th>Magasin</th><th>Source</th></tr></thead>
<tbody>{corps}</tbody></table></div>
<p><b>Retenu : {escape(r["nom"].lower())}</b> ({escape(r["magasin"])}, réf. {r["ref"]}). Il bouge moins que le hêtre ({cm(r["retrait_t"])} % de retrait tangentiel contre {cm(hetre["retrait_t"])} %), résiste à la pourriture, et se retire au magasin sans livraison, au prix qui tient le budget. <span class="choix">Choix laissé au constructeur.</span></p>
<h3>Rigidité</h3>
<p>Le meuble bas n'est vissé à aucun mur. Il tient par {M.COINS["n"]} coins de calage, taillés dans les chutes de tasseau et enfoncés au maillet entre les montants des deux échelles du bord et les murs nord et sud ; par le plan, vissé par-dessous sur les {len(M.ECHELLES)} échelles, qui les relie en tête ; et par les {len(M.ECHARPES)} écharpes, une par échelle, qui les rendent indéformables d'avant en arrière. Derrière la machine, rien ne passe entre {cm(z0)} et {cm(z1)} de haut, sur {cm(y1 - y0)} de large au droit du robinet : la zone des tuyaux reste libre. La machine ne touche jamais le meuble ({cm(jeu)} de jeu de chaque côté, {mm(M.JEU_PLAN)} mm sous le plan, tapis antivibration) : ses vibrations ne passent pas au plan.</p>"""


def page_meuble(meuble):
    assert meuble in PAGES, meuble
    pitch = {
        "bas": f"{lettres(N_ECHELLES, True).capitalize()} échelles en tasseaux de sapin debout sur le carrelage, le plan de travail en chêne posé sur leur tête à {cm(M.Z_DESSUS)}, la machine au sol dessous, et à côté la porte basculante en L qui ouvre {lettres(N_SACS)} sacs à linge.",
        "haut": f"Le caisson de {cm(M.Z_HAUT)} à {cm(M.Z_HAUT1)}, au-dessus de la niche : serviettes au nord, pharmacie au sud, {lettres(N_PORTES_HAUT, True)} portes coulissantes, fileur jusqu'au plafond. Chevillé au mur du fond, au-dessus du carrelage.",
    }[meuble]
    fin = essence_plan() if meuble == "bas" else materiaux_haut()
    corps = f"""{kicker(TITRES[meuble].lower())}
<h1>{TITRES[meuble]}</h1>
<p class="pitch">{pitch}</p>

<h2 id="iso">Le meuble</h2>
<div class="fig">{iso_meuble(meuble)}</div>

{montage(meuble)}

{decoupe(meuble)}

{achats(meuble)}

{fin}

<p class="note">Page générée depuis <span class="mono">3d/sdb/modele.py</span> par <span class="mono">3d/sdb/pages.py</span> (<span class="mono">just sdb</span>). Changements : <a href="{ENSEMBLE}#changements">page principale</a>.</p>"""
    return gabarit(f"{TITRES[meuble]} · meuble linge", meuble, corps)


def ecrire():
    for nom, html in ((ENSEMBLE, page_ensemble()), (PAGES["bas"], page_meuble("bas")), (PAGES["haut"], page_meuble("haut"))):
        chemin = os.path.join(PL.ROOT, nom)
        with open(chemin, "w", encoding="utf-8") as fh:
            fh.write(html)
        print(chemin)


if __name__ == "__main__":
    ecrire()
