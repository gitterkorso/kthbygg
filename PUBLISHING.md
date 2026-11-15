# Publicera KTHbygg

Paketnamnet på PyPI och importnamnet är `kthbygg`. Versionen anges på ett ställe:
`project.version` i `pyproject.toml`. PyPI-versioner kan inte skrivas över.

## Lokal kontroll

Kör i en ren checkout och en ny virtuell miljö. Gamla `build/`, `dist/` och
`*.egg-info/` kan innehålla inaktuella filnamn (särskilt svenska tecken), så
återanvänd dem inte vid en release. Kör därefter i repots rot:

```bash
python -m pip install build twine
python -m build
python -m twine check --strict dist/*
python -m pip install dist/kthbygg-0.1.0-py3-none-any.whl
python -m pip check
python -I scripts/check_installed.py
python -I -m unittest discover -s tester -p 'test_*.py' -v
```

Byt filnamnets version när du släpper en ny version. `python -m build` bygger
först ett källarkiv (sdist), därefter en wheel från det arkivet. Testet körs
med `-I` så att en lokal källmapp inte döljer en trasig installation.

Kontrollera även extraberoendena:

```bash
python -m pip install "dist/kthbygg-0.1.0-py3-none-any.whl[interaktiv]"
python -I scripts/check_installed.py --interaktiv
```

## PyPI och GitHub

Skapa en pending publisher på <https://pypi.org/manage/account/publishing/>:

| Fält | Värde |
|---|---|
| PyPI Project Name | `kthbygg` |
| Owner | `gitterkorso` |
| Repository name | `kthbygg` |
| Workflow name | `publish.yml` |
| Environment name | `pypi` |

Skapa motsvarande GitHub-miljö `pypi`. Publicering använder PyPI Trusted
Publishing och behöver ingen sparad API-nyckel. GitHub Actions måste vara
tillgängligt för repot; ändra inga betalningsgränser för att köra flödet.

Granska och committa ändringarna, uppdatera versionen och pusha en matchande
tagg, exempelvis `v0.1.0`. Workflow-filen `.github/workflows/publish.yml`
bygger arkiven, kontrollerar metadata och testar den installerade wheelen
med Python 3.10 och 3.14 före publicering. En manuell workflow-körning på
en branch gör bara bygg- och installationskontrollerna. De testade paketfilerna
sparas som GitHub-releasebilagor innan ett separat jobb publicerar dem på PyPI.
Det kräver ingen lagring i GitHub Actions artifact-kvoten. Om PyPI-steget
behöver köras om, välj **Re-run failed jobs** så att befintlig release återanvänds.

PyPI gör paketfilerna, inklusive bibliotekets källkod och metadata, offentliga.
Detta gäller även om GitHub-repot är privat. Notebookfiler och
valideringsresultat ingår inte i distributionen.

Efter publicering, verifiera från en ny virtuell miljö:

```bash
python -m pip install --index-url https://pypi.org/simple kthbygg
python -I -c "import kthbygg; print(kthbygg.__file__)"
```

Dokumentation: <https://docs.pypi.org/trusted-publishers/>.
