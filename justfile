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

# Rendus 3D de la bibliothèque du salon (3 systèmes) → salon-3d/
rendu-salon echantillons="256":
    /Applications/Blender.app/Contents/MacOS/Blender -b --python 3d/salon_biblio.py -- {{echantillons}}
    mkdir -p salon-3d
    for f in 3d/sortie/salon-biblio-*.png; do sips -s format jpeg -s formatOptions 85 "$f" --out "salon-3d/$(basename "$f" .png).jpg" >/dev/null; done

# Cuisine V11 : régénère cuisine-v11.html et le modèle FreeCAD depuis 3d/v11/modele.py (source unique)
v11:
    python3 3d/v11/plan.py
    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd 3d/v11/cad.py

# Cuisine V11 : rendus 3D (Blender) depuis le modèle FreeCAD → cuisine-v11-3d/*.jpg, puis regénère la page
v11-rendu echantillons="256":
    /Applications/Blender.app/Contents/MacOS/Blender -b --python 3d/v11/rendu.py -- {{echantillons}}
    mkdir -p cuisine-v11-3d
    for v in iso iso_no entree fenetre banquette cellier dos_cellier iso_nuit; do sips -s format jpeg -s formatOptions 85 "3d/sortie/v11-rendu-$v.png" --out "cuisine-v11-3d/$v.jpg" >/dev/null; done
    python3 3d/v11/plan.py

# Fige la version courante de la cuisine V11 (bouton de comparaison + archive/cuisine-v11.x.html)
v11-figer:
    python3 3d/v11/plan.py --figer

# Recopie la proposition 9 V2 A (table carrée) depuis cuisine-plan.html dans les versions figées de la V11
v11-figer-p9:
    python3 3d/v11/figer_p9.py
    python3 3d/v11/plan.py
