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

# Construit site/ (la passerelle recopie les pages que les anciens générateurs viennent de réécrire à la racine),
# commit tout, pull --rebase, push puis attend la publication par GitHub Action
sync message="Mise à jour des plans":
    python3 site.py
    git add -A
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

# Variante A (proposition 9 V2 A figée) : modèle 3D (FreeCAD) et rendus (Blender) → cuisine-3d/*.jpg
rendu-3d echantillons="256":
    python3 3d/textures.py
    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd 3d/cuisine_a.py
    /Applications/Blender.app/Contents/MacOS/Blender -b --python 3d/rendu.py -- {{echantillons}}
    mkdir -p cuisine-3d
    for f in 3d/sortie/rendu-*.png; do sips -s format jpeg -s formatOptions 85 "$f" --out "cuisine-3d/$(basename "$f" .png).jpg" >/dev/null; done

# Rendus 3D de la bibliothèque du salon (4 systèmes) → salon-3d/
rendu-salon echantillons="256":
    /Applications/Blender.app/Contents/MacOS/Blender -b --python 3d/salon_biblio.py -- {{echantillons}}
    mkdir -p salon-3d
    for f in 3d/sortie/salon-biblio-*.png; do sips -s format jpeg -s formatOptions 85 "$f" --out "salon-3d/$(basename "$f" .png).jpg" >/dev/null; done

# Cuisine V13 : régénère cuisine-v13.html, la version imprimable et le modèle FreeCAD depuis pieces/cuisine/modele.py (source unique)
v13:
    python3 3d/v13/plan.py
    just cuisine-amenagement-cad

# Fige la version courante de la cuisine V13 (bouton de comparaison + archive/cuisine-v13.x.html)
v13-figer:
    python3 3d/v13/plan.py --figer

# Entrée : reconstruit les pages des deux variantes (site/entree/amenagement/) depuis pieces/entree/
entree:
    python3 site.py entree/amenagement

# Modèle des deux recettes de rendu d'un autre document (déclaration CACHE_RENDU dans son document.py) :
#   <piece>-<document>-rendu echantillons="64" *vues : pour chaque variante de
#     `rendu_cache variantes <piece>/<document>` (`-` : sans variante), cams=$(rendu_cache liste <piece>/<document>
#     <variante> echantillons vues), rien si vide ; effacer les anciennes sorties de ces caméras ; un seul Blender par
#     variante ; copier vers site/<piece>/<document>/rendus/<variante>-<caméra>.jpg (+ <variante>-<caméra>-masque.png
#     s'il y a un masque ; sans variante : <caméra>.jpg, <caméra>-masque.png) ; rendu_cache noter … $cams ; enfin
#     python3 site.py <piece>/<document>.
#   <piece>-<document>-apercu *vues : même boucle, 16 échantillons, sortie dans cache/apercu/, ni cache ni copie
#     dans site/. (rendu_cache = python3 -m commun.rendu_cache ; entree-rendu et entree-apercu en sont l'exemple.)

# Entrée : rendus 3D (Blender) des deux variantes → site/entree/amenagement/rendus/<variante>-<caméra>.jpg + masques India,
# puis la page. Ne rend que les caméras dont l'empreinte a changé (cache/empreintes.json, commun/rendu_cache.py) ; avec des
# noms de caméras (just entree-rendu 64 banc), rend celles-là. Un seul lancement de Blender par variante.
entree-rendu echantillons="64" *vues:
    #!/usr/bin/env bash
    set -euo pipefail
    dest=site/entree/amenagement/rendus
    sortie="${ENTREE_SORTIE:-3d/sortie}"   # le dossier où rendu.py écrit
    mkdir -p "$dest"
    variantes=$(python3 -m commun.rendu_cache variantes entree/amenagement)   # affectation : set -e arrête sur une erreur
    for v in $variantes; do
      cams=$(python3 -m commun.rendu_cache liste entree/amenagement "$v" {{echantillons}} {{vues}})
      if [ -z "$cams" ]; then echo "$v : rien à rendre"; continue; fi
      echo "$v : $cams"
      for c in $cams; do rm -f "$sortie/entree-$v-$c.png" "$sortie/entree-$v-$c-masque.png"; done   # aucun reste d'un ancien rendu à copier
      ENTREE_VARIANTE="$v" "${BLENDER:-/opt/homebrew/bin/blender}" -b --python-exit-code 1 --python pieces/entree/amenagement/rendu.py -- {{echantillons}} $cams
      for c in $cams; do
        sips -s format jpeg -s formatOptions 85 "$sortie/entree-$v-$c.png" --out "$dest/$v-$c.jpg" >/dev/null
        cp "$sortie/entree-$v-$c-masque.png" "$dest/$v-$c-masque.png"
      done
      python3 -m commun.rendu_cache noter entree/amenagement "$v" {{echantillons}} $cams
    done
    python3 site.py entree/amenagement

# Entrée : aperçu rapide (16 échantillons, 800 × 600) des deux variantes → cache/apercu/entree-<variante>-<caméra>.png, sans
# cache ni copie dans site/ ; ouvre les images
entree-apercu *vues:
    #!/usr/bin/env bash
    set -euo pipefail
    mkdir -p cache/apercu
    variantes=$(python3 -m commun.rendu_cache variantes entree/amenagement)   # affectation : set -e arrête sur une erreur
    for v in $variantes; do
      ENTREE_VARIANTE="$v" ENTREE_APERCU=1 ENTREE_SORTIE="$PWD/cache/apercu" "${BLENDER:-/opt/homebrew/bin/blender}" -b --python-exit-code 1 --python pieces/entree/amenagement/rendu.py -- 16 {{vues}}
    done
    images=$(ls cache/apercu/entree-*.png | grep -v -- '-masque.png')
    open $images

# Cuisine, aménagement : modèle FreeCAD depuis pieces/cuisine/modele.py → cache/cuisine/cuisine-v13.FCStd et .glb
# (CUISINE_SORTIE=<dossier> pour un autre), l'entrée des rendus
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

# Cuisine, aménagement : rendus 3D (FreeCAD puis Blender) → site/cuisine/amenagement/rendus/<caméra>.jpg, puis la page.
# Ne rend que les caméras dont l'empreinte a changé (cache/empreintes.json, commun/rendu_cache.py) ; avec des noms de
# caméras (just cuisine-amenagement-rendu 64 entree iso_so), rend celles-là. Le glb est refait, puis un seul Blender.
cuisine-amenagement-rendu echantillons="64" *vues:
    #!/usr/bin/env bash
    set -euo pipefail
    dest=site/cuisine/amenagement/rendus
    export CUISINE_SORTIE="${CUISINE_SORTIE:-$PWD/cache/cuisine}"   # le dossier où cad.py et rendu.py écrivent
    cams=$(python3 -m commun.rendu_cache liste cuisine/amenagement - {{echantillons}} {{vues}})   # sans variante : -
    if [ -z "$cams" ]; then echo "cuisine/amenagement : rien à rendre"; exit 0; fi
    echo "cuisine/amenagement : $cams"
    for c in $cams; do rm -f "$CUISINE_SORTIE/cuisine-$c.png"; done   # aucun reste d'un ancien rendu à copier
    just cuisine-amenagement-cad
    "${BLENDER:-/opt/homebrew/bin/blender}" -b --python-exit-code 1 --python pieces/cuisine/amenagement/rendu.py -- {{echantillons}} $cams
    mkdir -p "$dest"
    for c in $cams; do
      nom="$c"   # sans variante : rendus/<caméra>.jpg
      sips -s format jpeg -s formatOptions 85 "$CUISINE_SORTIE/cuisine-$c.png" --out "$dest/$nom.jpg" >/dev/null
    done
    python3 -m commun.rendu_cache noter cuisine/amenagement - {{echantillons}} $cams
    python3 site.py cuisine/amenagement

# Cuisine, aménagement : aperçu rapide (16 échantillons, 800 × 600) → cache/apercu/cuisine-<caméra>.png, sans cache ni
# copie dans site/ (glb de cache/cuisine, refait s'il est plus ancien que le modèle)
cuisine-amenagement-apercu *vues: _cuisine-amenagement-glb
    #!/usr/bin/env bash
    set -euo pipefail
    mkdir -p cache/apercu
    cp "${CUISINE_SORTIE:-$PWD/cache/cuisine}/cuisine-v13.glb" cache/apercu/cuisine-v13.glb
    CUISINE_APERCU=1 CUISINE_SORTIE="$PWD/cache/apercu" "${BLENDER:-/opt/homebrew/bin/blender}" -b --python-exit-code 1 --python pieces/cuisine/amenagement/rendu.py -- 16 {{vues}}
    ls cache/apercu/cuisine-*.png

# Cuisine, aménagement : maquette 3D tournante (three.js) → site/cuisine/amenagement/maquette-3d/modele.js
# (CUISINE_MAQUETTE=<fichier> pour un autre)
cuisine-amenagement-maquette: _cuisine-amenagement-glb
    "${BLENDER:-/opt/homebrew/bin/blender}" -b --python-exit-code 1 --python pieces/cuisine/amenagement/maquette.py

# Cuisine, aménagement : vidéo du tour à 360° en vue iso, mannequin au centre — aperçu EEVEE 960 × 540 pour valider
# l'animation → cache/cuisine/cuisine-video-apercu-360.mp4
cuisine-amenagement-video-apercu: _cuisine-amenagement-glb
    "${BLENDER:-/opt/homebrew/bin/blender}" -b --python-exit-code 1 --python pieces/cuisine/amenagement/video.py -- apercu

# Cuisine, aménagement : la même vidéo en définitif (Cycles, 1920 × 1080) → cache/cuisine/cuisine-video-360.mp4
cuisine-amenagement-video echantillons="64": _cuisine-amenagement-glb
    "${BLENDER:-/opt/homebrew/bin/blender}" -b --python-exit-code 1 --python pieces/cuisine/amenagement/video.py -- {{echantillons}}

# Salon V4 : régénère salon-v4.html et les pages des meubles (étagères, enfilade) depuis 3d/salon/modele.py
salon:
    python3 3d/salon/plan.py
    python3 3d/salon/etageres.py
    python3 3d/salon/enfilade.py

# Salon V4 : rendus 3D (Blender) depuis 3d/salon/modele.py → salon-v4-3d/*.jpg, puis regénère la page
salon-rendu echantillons="64" *vues:
    /Applications/Blender.app/Contents/MacOS/Blender -b --python 3d/salon/rendu.py -- {{echantillons}} {{vues}}
    mkdir -p salon-v4-3d
    for f in 3d/sortie/salon-v4-rendu-*.png; do sips -s format jpeg -s formatOptions 85 "$f" --out "salon-v4-3d/$(basename "$f" .png | sed 's/salon-v4-rendu-//').jpg" >/dev/null; done
    python3 3d/salon/plan.py

# Salon : rendus 3D des meubles à fabriquer (étagères, enfilade) → salon-meubles-3d/*.jpg, puis regénère leurs pages
salon-meubles-rendu echantillons="128" *vues:
    /Applications/Blender.app/Contents/MacOS/Blender -b --python 3d/salon/rendu_meubles.py -- {{echantillons}} {{vues}}
    mkdir -p salon-meubles-3d
    for f in 3d/sortie/salon-meuble-*.png; do sips -s format jpeg -s formatOptions 85 "$f" --out "salon-meubles-3d/$(basename "$f" .png | sed 's/salon-meuble-//').jpg" >/dev/null; done
    python3 3d/salon/etageres.py
    python3 3d/salon/enfilade.py

# Fige la version courante du salon (bouton de comparaison + archive/salon-v4.x.html)
salon-figer:
    python3 3d/salon/plan.py --figer

# Meuble linge SDB : régénère sdb-meuble-bas.html (bas.py), sdb-meuble-haut.html (haut.py) et sdb-meuble-achats.html (achats.py), depuis 3d/sdb/modele.py, puis le modèle FreeCAD
sdb:
    python3 3d/sdb/bas.py
    python3 3d/sdb/haut.py
    python3 3d/sdb/achats.py
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
