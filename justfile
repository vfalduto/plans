set shell := ["bash", "-euo", "pipefail", "-c"]

repo := "vfalduto/plans"
site := "https://vfalduto.github.io/plans/"
# FreeCAD en ligne de commande, pour la cuisine (FREECADCMD=<binaire> pour un autre)
cuisine_freecadcmd := env_var_or_default("FREECADCMD", "/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd")

# Liste les commandes
default:
    @just --list

# Construit site/ (toutes les pièces, ou seulement celles données : just site entree/amenagement)
site *args:
    python3 site.py {{args}}

# Construit site/ puis le sert sur http://127.0.0.1:8800/ et l'ouvre
apercu:
    #!/usr/bin/env bash
    set -euo pipefail
    python3 site.py
    ( sleep 1; open http://127.0.0.1:8800/ ) &
    python3 -m http.server 8800 --bind 127.0.0.1 --directory site

# Construit site/, commit site/ et les fichiers suivis modifiés (jamais un fichier non suivi), pull --rebase, push, attend GitHub Pages
sync message="Mise à jour des plans":
    python3 site.py
    git add site/
    git add -u
    git diff --cached --quiet || git commit -m "{{message}}"
    git pull --rebase --quiet
    git push --quiet
    @just pages-wait

# Attend la fin de l'exécution de pages.yml pour le dernier commit
pages-wait:
    #!/usr/bin/env bash
    set -euo pipefail
    sha=$(git rev-parse HEAD)
    echo "Publication GitHub Actions de ${sha:0:7}…"
    id=""
    for _ in $(seq 1 30); do
      id=$(gh run list --repo {{repo}} --workflow pages.yml --commit "$sha" --json databaseId --jq '.[0].databaseId // empty')
      [ -n "$id" ] && break
      sleep 2
    done
    if [ -z "$id" ]; then
      echo "Aucune exécution de pages.yml pour ${sha:0:7} : https://github.com/{{repo}}/actions" >&2
      exit 1
    fi
    gh run watch "$id" --repo {{repo}} --exit-status
    echo "En ligne : {{site}}"

# Porte du cellier : régénère site/cuisine-v13-porte-cellier.html (page figée hors du menu) depuis pieces/cuisine/modele.py
v13-porte:
    python3 3d/v13/porte.py

# Ce qui distingue un document (script, variables, bois du salon, FreeCAD de la cuisine) est dans sa CACHE_RENDU (document.py).
# Un seul Blender à la fois : BLENDER=<REGISTRE>/outils/blender-seul.sh BLENDER_REEL=/opt/homebrew/bin/blender
# Rendus 3D (Blender) d'un document → site/<piece>/<document>/rendus/, puis sa page ; ne rend que les caméras dont l'empreinte a changé, ou celles nommées
rendu page echantillons="64" *vues:
    python3 -m commun.rendu_cache rendre {{page}} {{echantillons}} {{vues}}

# Aperçu rapide d'un document (16 échantillons, 800 × 600) → cache/apercu/, sans cache ni copie dans site/ ; sans caméra nommée, toutes celles du document
rendu-apercu page *vues:
    python3 -m commun.rendu_cache apercu {{page}} {{vues}}

# (CUISINE_SORTIE=<dossier> pour un autre)
# Cuisine, aménagement : modèle FreeCAD depuis pieces/cuisine/modele.py → cache/cuisine/cuisine-v13.FCStd et .glb
cuisine-amenagement-cad:
    #!/usr/bin/env bash
    set -euo pipefail
    sortie="${CUISINE_SORTIE:-$PWD/cache/cuisine}"
    mkdir -p "$sortie"
    rm -f "$sortie/cuisine-v13.glb"
    CUISINE_SORTIE="$sortie" "{{cuisine_freecadcmd}}" pieces/cuisine/amenagement/cad.py
    [ -s "$sortie/cuisine-v13.glb" ] || { echo "cad.py n'a pas écrit $sortie/cuisine-v13.glb" >&2; exit 1; }   # freecadcmd sort en 0 sur une erreur

# Le glb de la cuisine, refait s'il manque ou s'il est plus ancien que le modèle ou que cad.py
_cuisine-amenagement-glb:
    #!/usr/bin/env bash
    set -euo pipefail
    glb="${CUISINE_SORTIE:-$PWD/cache/cuisine}/cuisine-v13.glb"
    if [ ! -f "$glb" ] || [ "$glb" -ot pieces/cuisine/modele.py ] || [ "$glb" -ot pieces/cuisine/amenagement/cad.py ]; then
      just cuisine-amenagement-cad
    fi

# (CUISINE_MAQUETTE=<fichier> pour un autre)
# Cuisine, aménagement : maquette 3D tournante (three.js) → site/cuisine/amenagement/maquette-3d/modele.js
cuisine-amenagement-maquette: _cuisine-amenagement-glb
    "${BLENDER:-/opt/homebrew/bin/blender}" -b --python-exit-code 1 --python pieces/cuisine/amenagement/maquette.py

# Cuisine, aménagement : vidéo du tour à 360° en vue iso, mannequin au centre, aperçu EEVEE 960 × 540 → cache/cuisine/cuisine-video-apercu-360.mp4
cuisine-amenagement-video-apercu: _cuisine-amenagement-glb
    "${BLENDER:-/opt/homebrew/bin/blender}" -b --python-exit-code 1 --python pieces/cuisine/amenagement/video.py -- apercu

# Cuisine, aménagement : la même vidéo en définitif (Cycles, 1920 × 1080) → cache/cuisine/cuisine-video-360.mp4
cuisine-amenagement-video echantillons="64": _cuisine-amenagement-glb
    "${BLENDER:-/opt/homebrew/bin/blender}" -b --python-exit-code 1 --python pieces/cuisine/amenagement/video.py -- {{echantillons}}

# Meuble linge de la salle de bain : modèle FreeCAD (3d/sdb/modele.py, ancien meuble) → 3d/sortie/sdb-meuble-v4.FCStd
sdb-cad:
    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd 3d/sdb/cad.py

# Recherches Leboncoin : serveur local des pages achats/ (boutons ★ / ✕), voir .claude/skills/lbc/SKILL.md
achats port="8765":
    uv run .claude/skills/lbc/achats.py servir --port {{port}}

# Recherches Leboncoin : tests (sans réseau)
achats-tests:
    cd .claude/skills/lbc && uv run -q --no-project --with pytest --with lbc==1.1.7 pytest -q tests

# Tests du site (commun/, site.py)
tests:
    uv run -q --no-project --with pytest pytest -q tests
