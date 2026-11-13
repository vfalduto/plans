#!/usr/bin/env bash
# Lance un script de vérification dans le navigateur, sur le site d'essai :
#
#   tests/navigateur/lancer.sh tests/navigateur/navigation.js
#
# 1. construit le site d'essai (tests/fixtures/essai/construire.py) dans cache/essai-site/ ;
# 2. le sert sur 127.0.0.1:$PORT ;
# 3. ouvre la session playwright-cli $SESSION, va à la racine du site, puis exécute le script ;
# 4. ferme la session et arrête le serveur, même en cas d'échec ;
# 5. sort en erreur si le script n'a pas renvoyé "ok": true.
#
# Le script est une fonction `async page => {…}`. Il part de la racine du site d'essai (BASE = l'origine de
# page.url()) et renvoie {ok, echecs: […], erreurs: […]}, où erreurs regroupe les erreurs de console et de page.
#
# PORT (8811) et SESSION (refonte-essai) se changent par l'environnement, pour lancer plusieurs vérifications à la
# fois. Seule la session $SESSION est fermée : jamais close-all ni kill-all.
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "usage : $0 <script.js>" >&2
  exit 2
fi
racine="$(cd "$(dirname "$0")/../.." && pwd)"
script="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
port="${PORT:-8811}"
session="${SESSION:-refonte-essai}"
site="http://127.0.0.1:$port/"

python3 "$racine/tests/fixtures/essai/construire.py"

if curl -s -o /dev/null "$site"; then
  echo "lancer.sh : le port $port est déjà pris (PORT=… pour en choisir un autre)" >&2
  exit 2
fi
python3 -m http.server "$port" --bind 127.0.0.1 --directory "$racine/cache/essai-site" \
  >"$racine/cache/essai-serveur-$port.log" 2>&1 &
serveur=$!
fermer() {
  playwright-cli -s="$session" close >/dev/null 2>&1 || true
  kill "$serveur" 2>/dev/null || true
}
trap fermer EXIT
for _ in $(seq 50); do
  curl -s -o /dev/null "$site" && break
  if ! kill -0 "$serveur" 2>/dev/null; then
    echo "lancer.sh : le serveur ne démarre pas, voir cache/essai-serveur-$port.log" >&2
    exit 2
  fi
  sleep 0.1
done

playwright-cli -s="$session" close >/dev/null 2>&1 || true   # reste d'un lancement interrompu
playwright-cli -s="$session" open about:blank >/dev/null
playwright-cli -s="$session" goto "$site" >/dev/null
code=0
sortie="$(playwright-cli -s="$session" --raw run-code --filename="$script")" || code=$?
echo "$sortie"
[ "$code" -eq 0 ] || exit 1
python3 -c 'import json, sys; sys.exit(0 if json.loads(sys.argv[1]).get("ok") is True else 1)' "$sortie" 2>/dev/null
