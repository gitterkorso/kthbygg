# Kör från projektroten: .venv/Scripts/python.exe exempel/ritstilar.py
# Skapar SVG, PNG och en lokal förhandsvisning i samma mapp som skriptet.
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from kthbygg.balk import Balk


def main():
    ut = Path(__file__).resolve().parent
    balk = Balk(12, EI=40000)
    balk.stöd(0, "led").stöd(12, "rull")
    balk.utbredd_last(8, 0, 6).punktlast(9, 24)

    konsol = Balk(6, EI=40000)
    konsol.stöd(0, "fast").utbredd_last(0, 0, 3, q2=6)
    konsol.moment(6, 12).punktlast(6, 0, H=15)

    triangel = Balk(6, EI=40000)
    triangel.stöd(0, "led").stöd(6, "rull").utbredd_last(6, q2=0)

    fig, axes = plt.subplots(3, 1, figsize=(12, 13.2), layout="constrained")
    balk.rita_modell(ax=axes[0], titel="01 / Fritt upplagd balk")
    konsol.rita_modell(ax=axes[1], titel="02 / Konsol med varierande last och moment")
    triangel.rita_modell(ax=axes[2], titel="03 / Fritt upplagd balk med triangulär last")
    fig.savefig(ut / "ritstil_teknisk.svg", facecolor="white")
    fig.savefig(ut / "ritstil_teknisk.png", dpi=130, facecolor="white")
    plt.close(fig)
    html = (
        '<!doctype html><html lang="sv"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>KTHbygg – Teknisk balkritning</title>'
        '<style>body{max-width:1100px;margin:40px auto;padding:0 24px;'
        'font:16px/1.5 system-ui;color:#20252b}img{width:100%;height:auto}</style>'
        '<h1>Teknisk balkritning</h1>'
        '<p><a href="ritstil_teknisk.svg" download>Hämta SVG</a></p>'
        '<img src="ritstil_teknisk.svg" alt="Tekniska ritningar av balkar med laster och stöd">'
        '<p>Enheter: m, kN och kNm. Symbolstorlek och pilhöjd är grafiska.</p></html>'
    )
    (ut / "ritstilar.html").write_text(html, encoding="utf-8")
    print(ut / "ritstil_teknisk.svg")


if __name__ == "__main__":
    main()
