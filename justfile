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

# Cuisine V13 : aperçu rapide (16 échantillons, demi-résolution) → 3d/sortie/v13-apercu-<vue>.png, page non touchée
v13-apercu *vues:
    /Applications/Blender.app/Contents/MacOS/Blender -b --python 3d/v13/rendu.py -- 16 apercu {{vues}}
    @ls 3d/sortie/v13-apercu-*.png

# Fige la version courante de la cuisine V13 (bouton de comparaison + archive/cuisine-v13.x.html)
v13-figer:
    python3 3d/v13/plan.py --figer

# Salon V4 : régénère salon-v4.html depuis 3d/salon/modele.py (source unique)
salon:
    python3 3d/salon/plan.py

# Salon V4 : rendus 3D (Blender) depuis 3d/salon/modele.py → salon-v4-3d/*.jpg, puis regénère la page
salon-rendu echantillons="64" *vues:
    /Applications/Blender.app/Contents/MacOS/Blender -b --python 3d/salon/rendu.py -- {{echantillons}} {{vues}}
    mkdir -p salon-v4-3d
    for f in 3d/sortie/salon-v4-rendu-*.png; do sips -s format jpeg -s formatOptions 85 "$f" --out "salon-v4-3d/$(basename "$f" .png | sed 's/salon-v4-rendu-//').jpg" >/dev/null; done
    python3 3d/salon/plan.py

# Fige la version courante du salon (bouton de comparaison + archive/salon-v4.x.html)
salon-figer:
    python3 3d/salon/plan.py --figer

# Recherches Leboncoin : serveur local des pages achats/ (boutons ★ / ✕), voir .claude/skills/lbc/SKILL.md
achats port="8765":
    uv run .claude/skills/lbc/achats.py servir --port {{port}}

# Recherches Leboncoin : tests (sans réseau)
achats-tests:
    cd .claude/skills/lbc && uv run -q --no-project --with pytest --with lbc==1.1.7 pytest -q tests
