# Kör alla test-notebooks i den här mappen utan att öppna dem.
# Kräver nbclient:  python -m pip install nbclient
#
#   python tester/kor_alla.py            kör och skriv ut resultatet
#   python tester/kor_alla.py --spara    spara också resultaten i notebooks

import pathlib
import sys

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

MAPP = pathlib.Path(__file__).parent
spara = "--spara" in sys.argv

misslyckade = []
for fil in sorted(MAPP.glob("test_*.ipynb")):
    nb = nbformat.read(fil, as_version=4)
    try:
        NotebookClient(nb, timeout=120, resources={"metadata": {"path": str(MAPP)}}).execute()
        status = "OK"
    except CellExecutionError as e:
        status = "FEL"
        misslyckade.append(fil.name)
    print(f"\n=== {fil.name}: {status} ===")
    sista = nb.cells[-1]
    for ut in sista.get("outputs", []):
        print(ut.get("text") or ut.get("evalue", ""))
    if spara:
        nbformat.write(nb, fil)

if misslyckade:
    sys.exit(f"\nOväntade fel i: {', '.join(misslyckade)}")
print("\nAlla notebooks kördes utan oväntade fel.")
