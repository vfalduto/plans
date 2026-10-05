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

# Regénère le modèle 3D (FreeCAD) et les rendus (Blender), puis les copie en JPG pour cuisine-3d.html
rendu-3d echantillons="256":
    python3 3d/textures.py
    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd 3d/cuisine_a.py
    /Applications/Blender.app/Contents/MacOS/Blender -b --python 3d/rendu.py -- {{echantillons}}
    mkdir -p cuisine-3d
    for f in 3d/sortie/rendu-*.png; do sips -s format jpeg -s formatOptions 85 "$f" --out "cuisine-3d/$(basename "$f" .png).jpg" >/dev/null; done

# Rendus 3D de la bibliothèque du salon (3 systèmes) → salon-3d/
rendu-salon echantillons="256":
    /Applications/Blender.app/Contents/MacOS/Blender -b --python 3d/salon_biblio.py -- {{echantillons}}
    mkdir -p salon-3d
    for f in 3d/sortie/salon-biblio-*.png; do sips -s format jpeg -s formatOptions 85 "$f" --out "salon-3d/$(basename "$f" .png).jpg" >/dev/null; done
