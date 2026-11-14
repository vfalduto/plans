import os
import subprocess
import sys
from tests.outils import RACINE

ESSAIS = ("niv_1.py", "niv_2.py", "niv_3.py", "niv_4.py", "niv_commun.py", "niv_comparatif.py", "niveaux.py",
          "var_pivot.py", "var_tiroirs.py", "var_arceaux.py", "var_comparatif.py", "variantes.py", "test_v4.py")
ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}


def test_essais_ranges():
    for nom in ESSAIS:
        assert (RACINE / "explorations" / nom).is_file(), nom
        assert not (RACINE / "3d" / "sdb" / nom).exists(), nom


def test_essais_tournent_sans_ecrire_a_la_racine():
    avant = sorted(p.name for p in RACINE.glob("*.html"))
    for script, sortie in (("niveaux.py", "sdb-meuble-niveaux.html"), ("variantes.py", "sdb-meuble-variantes.html")):
        r = subprocess.run([sys.executable, f"explorations/{script}", "--strict"], cwd=RACINE, env=ENV,
                           capture_output=True, text=True, timeout=180)
        assert r.returncode == 0, r.stderr[-2000:]
        assert (RACINE / "cache" / "explorations" / sortie).is_file()
    assert sorted(p.name for p in RACINE.glob("*.html")) == avant


def test_test_v4_passe():
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "explorations/test_v4.py"],
                       cwd=RACINE, env=ENV, capture_output=True, text=True, timeout=180)
    assert r.returncode == 0, r.stdout[-3000:]
