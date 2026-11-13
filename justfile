set shell := ["bash", "-euo", "pipefail", "-c"]

repo := "vfalduto/plans"
site := "https://vfalduto.github.io/plans/"

# Liste les commandes
default:
    @just --list

# Commit tout, pull --rebase, push puis attend le redéploiement GitHub Pages
sync message="Mise à jour des plans":
    git add -A
    git diff --cached --quiet || git commit -m "{{message}}"
    git pull --rebase --quiet
    git push --quiet
    @just pages-wait

# Attend la fin du build GitHub Pages pour le dernier commit
pages-wait:
    #!/usr/bin/env bash
    set -euo pipefail
    sha=$(git rev-parse HEAD)
    echo "Déploiement GitHub Pages de ${sha:0:7}…"
    for _ in $(seq 1 60); do
      read -r status commit < <(gh api repos/{{repo}}/pages/builds/latest --jq '"\(.status) \(.commit)"')
      if [ "$commit" = "$sha" ] && [ "$status" = built ]; then echo "En ligne : {{site}}"; exit 0; fi
      if [ "$commit" = "$sha" ] && [ "$status" = errored ]; then echo "Échec du build Pages" >&2; exit 1; fi
      sleep 5
    done
    echo "Délai dépassé, vérifier : https://github.com/{{repo}}/actions" >&2
    exit 1

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

# Cuisine V13 : régénère cuisine-v13.html, la version imprimable et le modèle FreeCAD depuis 3d/v13/modele.py (source unique)
v13:
    python3 3d/v13/plan.py
    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd 3d/v13/cad.py

# Cuisine V13 : rendus 3D (Blender) depuis le modèle FreeCAD → cuisine-v13-3d/*.jpg, puis regénère la page
# (toutes les vues par défaut, ou seulement celles données : just v13-rendu 64 entree iso ; 64 échantillons ≈ 256 une fois débruité)
v13-rendu echantillons="64" *vues:
    /Applications/Blender.app/Contents/MacOS/Blender -b --python 3d/v13/rendu.py -- {{echantillons}} {{vues}}
    mkdir -p cuisine-v13-3d
    for v in {{ if vues == "" { "iso iso_no entree fenetre banquette cellier dos_cellier iso_nuit" } else { vues } }}; do f="3d/sortie/v13-rendu-$v.png"; [ -f "$f" ] && sips -s format jpeg -s formatOptions 85 "$f" --out "cuisine-v13-3d/$v.jpg" >/dev/null || true; done
    python3 3d/v13/plan.py

# Cuisine V13 : vidéo du tour à 360° en vue iso, mannequin au centre — aperçu EEVEE 960 × 540 pour valider l'animation
# → 3d/sortie/v13-video-apercu-360.mp4
v13-video-apercu:
    /Applications/Blender.app/Contents/MacOS/Blender -b --python 3d/v13/video.py -- apercu

# Cuisine V13 : la même vidéo en définitif (Cycles, 1920 × 1080) → 3d/sortie/v13-video-360.mp4
v13-video echantillons="64":
    /Applications/Blender.app/Contents/MacOS/Blender -b --python 3d/v13/video.py -- {{echantillons}}

# Cuisine V13 : maquette 3D tournante de la page cuisine-v13-maquette.html (three.js) → cuisine-v13-maquette/modele.js
v13-maquette:
    /Applications/Blender.app/Contents/MacOS/Blender -b --python 3d/v13/maquette.py

# Cuisine V13 : aperçu rapide (16 échantillons, demi-résolution) → 3d/sortie/v13-apercu-<vue>.png, page non touchée
v13-apercu *vues:
    /Applications/Blender.app/Contents/MacOS/Blender -b --python 3d/v13/rendu.py -- 16 apercu {{vues}}
    @ls 3d/sortie/v13-apercu-*.png

# Fige la version courante de la cuisine V13 (bouton de comparaison + archive/cuisine-v13.x.html)
v13-figer:
    python3 3d/v13/plan.py --figer

# Salon V4 : régénère salon-v4.html et les pages des meubles (étagères, enfilade) depuis 3d/salon/modele.py
# Entrée : régénère entree-amenagement.html (plan, coupes, vues 3D) depuis 3d/entree/modele.py
entree:
    python3 3d/entree/plan.py

# Entrée : rendus 3D (Blender) des deux variantes → site/entree/amenagement/rendus/<variante>-<caméra>.jpg + masques India,
# puis la page. Ne rend que les caméras dont l'empreinte a changé (cache/empreintes.json, commun/rendu_cache.py) ; avec des
# noms de caméras (just entree-rendu 64 banc), rend celles-là. Un seul lancement de Blender par variante.
entree-rendu echantillons="64" *vues:
    #!/usr/bin/env bash
    set -euo pipefail
    dest=site/entree/amenagement/rendus
    mkdir -p "$dest"
    for v in principale victor; do
      cams=$(python3 -m commun.rendu_cache liste "$v" {{echantillons}} {{vues}})
      if [ -z "$cams" ]; then echo "$v : rien à rendre"; continue; fi
      echo "$v : $cams"
      for c in $cams; do rm -f "3d/sortie/entree-$v-$c.png" "3d/sortie/entree-$v-$c-masque.png"; done   # aucun reste d'un ancien rendu à copier
      ENTREE_VARIANTE="$v" "${BLENDER:-/opt/homebrew/bin/blender}" -b --python-exit-code 1 --python pieces/entree/amenagement/rendu.py -- {{echantillons}} $cams
      for c in $cams; do
        sips -s format jpeg -s formatOptions 85 "3d/sortie/entree-$v-$c.png" --out "$dest/$v-$c.jpg" >/dev/null
        cp "3d/sortie/entree-$v-$c-masque.png" "$dest/$v-$c-masque.png"
      done
      python3 -m commun.rendu_cache noter "$v" {{echantillons}} $cams
    done
    python3 site.py entree/amenagement

# Entrée : aperçu rapide (16 échantillons, 800 × 600) des deux variantes → cache/apercu/entree-<variante>-<caméra>.png, sans
# cache ni copie dans site/ ; ouvre les images
entree-apercu *vues:
    #!/usr/bin/env bash
    set -euo pipefail
    mkdir -p cache/apercu
    for v in principale victor; do
      ENTREE_VARIANTE="$v" ENTREE_APERCU=1 ENTREE_SORTIE="$PWD/cache/apercu" "${BLENDER:-/opt/homebrew/bin/blender}" -b --python-exit-code 1 --python pieces/entree/amenagement/rendu.py -- 16 {{vues}}
    done
    images=$(ls cache/apercu/entree-*.png | grep -v -- '-masque.png')
    open $images

# Entrée, version Victor : régénère entree-amenagement-victor.html depuis 3d/entree/victor.py
entree-victor:
    python3 3d/entree/plan_victor.py

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
