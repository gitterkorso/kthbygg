"""Kontrollera ett installerat paket: python -I scripts/check_installed.py [--interaktiv]."""

import argparse
import importlib
import importlib.metadata
import io
import math
from pathlib import Path
import sysconfig


MODULES = (
    "KKR", "Knutpunkt", "VKR", "balk", "balkstil", "bärförmåga",
    "böjknäckning", "böjvridknäckning", "deformation", "display", "figur",
    "lastkomb", "nyttig", "print", "ram", "sammansatttryckta",
    "skjuvbuckling", "skruvförband", "snö", "svetsförband", "tools",
    "torsion", "trä", "tvk", "tvärsnitt", "vippning",
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interaktiv", action="store_true", help="Testa extra beroenden och Plotly.")
    args = parser.parse_args()

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import kthbygg

    package_file = Path(kthbygg.__file__).resolve()
    install_dirs = [Path(sysconfig.get_path(name)).resolve() for name in ("purelib", "platlib")]
    assert any(package_file.is_relative_to(path) for path in install_dirs), (
        f"Paketet måste komma från site-packages, inte en källmapp: {package_file}"
    )
    dist = importlib.metadata.distribution("kthbygg")
    assert dist.metadata["Name"].lower() == "kthbygg"
    assert dist.version and dist.metadata["Requires-Python"]
    assert Path(dist.locate_file("kthbygg/__init__.py")).resolve() == package_file
    for name in MODULES:
        module = importlib.import_module(f"kthbygg.{name}")
        assert Path(module.__file__).resolve().parent == package_file.parent, name

    # Analytisk referens: konsol med punktlast vid den fria änden.
    from kthbygg.balk import Balk
    result = Balk(4, EI=40000).stöd(0, "fast").punktlast(4, 12).lös()
    assert math.isclose(result.reaktioner[0]["V"], 12, rel_tol=1e-10)
    assert math.isclose(result.reaktioner[0]["M"], 48, rel_tol=1e-10)
    assert math.isclose(result.w(4), 12 * 4**3 / (3 * 40000), rel_tol=1e-10)
    figure = result.rita("VMw")
    try:
        output = io.BytesIO()
        figure.savefig(output, format="png")
        assert output.getvalue().startswith(b"\x89PNG\r\n\x1a\n")
    finally:
        plt.close(figure)

    if args.interaktiv:
        import nbformat
        import plotly.graph_objects as go
        nbformat.validate(nbformat.v4.new_notebook())
        # Metoden returnerar figuren utan att öppna ett fönster.
        interactive = result.rita_interaktiv("VMw")
        assert isinstance(interactive, go.Figure) and len(interactive.data) > 0
        assert interactive.to_json()

    extra = " inklusive interaktiv" if args.interaktiv else ""
    print(f"OK: kthbygg {dist.version}{extra}; import, konsol och ritning från {package_file}")


if __name__ == "__main__":
    main()
