"""Pages de redirection des anciennes adresses.

Chaque page publiée avant la refonte garde son adresse : elle devient une page qui mène au document qui la remplace.
La table « ancienne adresse → nouvelle adresse » est celle de la spec (docs/superpowers/specs/2026-11-13-refonte-site-design.md,
section Migration) ; site.py (REDIRECTIONS) en tient la version à jour, une `Redirection` par page migrée.
"""
import json
from dataclasses import dataclass, field
from html import escape

from commun.gabarit import relatif


@dataclass(frozen=True)
class Redirection:
    """`ancienne` : page d'origine, relative à site/ ; `cible` : adresse du nouveau document, relative à site/.

    `ancres` traduit un identifiant d'ancre de l'ancienne page en fragment de la nouvelle (« plan » → « plan »).
    `motifs` : paires (regex, gabarit) essayées quand l'ancre n'est pas dans `ancres` ; `{1}` est le premier groupe,
    en majuscule (`(r"^coupe-([a-d])-", "coupes?k={1}")`). Sans correspondance, la page s'ouvre sur la vue par défaut.
    `pages` : ancres qui mènent à une autre page que `cible`, adresse relative à site/ (« changements » → l'historique
    du document) ; elles passent avant `ancres` et `motifs`."""
    ancienne: str
    cible: str
    ancres: dict[str, str] = field(default_factory=dict)
    motifs: tuple[tuple[str, str], ...] = ()
    pages: dict[str, str] = field(default_factory=dict)


SCRIPT = """\
(function () {
  var t = JSON.parse(document.getElementById("traduction").textContent);
  var id = decodeURIComponent(location.hash.slice(1)), frag = "";
  var a = function (table) { return Object.prototype.hasOwnProperty.call(table, id); };
  if (a(t.pages)) { location.replace(t.pages[id]); return; }
  if (a(t.ancres)) frag = t.ancres[id];
  else for (var i = 0; id && i < t.motifs.length; i++) {
    var m = new RegExp(t.motifs[i][0]).exec(id);
    if (m) { frag = t.motifs[i][1].replace(/\\{(\\d+)\\}/g, function (_, n) { return (m[n] || "").toUpperCase(); }); break; }
  }
  location.replace(t.cible + (frag ? "#" + frag : ""));
})();"""


def _json(valeur) -> str:
    """JSON sûr dans un `<script>` : pas de `</script>` ni de `<!--` possibles."""
    return json.dumps(valeur, ensure_ascii=False).replace("<", "\\u003c")


def page_redirection(r: Redirection, depuis: str) -> str:
    """Page écrite à `depuis` (chemin relatif à site/) : `meta refresh` vers la cible sans fragment, plus un script qui
    traduit `location.hash` (autre page, ancre exacte, puis motifs, sinon aucun fragment) et un lien visible."""
    cible = relatif(r.cible, depuis)
    donnees = {"cible": cible, "ancres": r.ancres, "motifs": [list(m) for m in r.motifs],
               "pages": {ancre: relatif(page, depuis) for ancre, page in r.pages.items()}}
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cette page a changé d'adresse</title>
<meta http-equiv="refresh" content="0; url={escape(cible)}">
<script type="application/json" id="traduction">{_json(donnees)}</script>
<script>{SCRIPT}</script>
</head>
<body>
<p>Cette page a changé d'adresse : <a href="{escape(cible)}">ouvrir la nouvelle page</a>.</p>
</body>
</html>
"""
