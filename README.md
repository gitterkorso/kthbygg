# KTHbygg

KTHbygg är ett Python-bibliotek för dimensionering av bärverk enligt Eurokod. Det är gjort för handberäkningar i Jupyter: funktionerna följer standardens formler steg för steg, och flera av dem kan skriva ut uträkningen med LaTeX.

> **Under utveckling.** Formlerna är inte fullständigt verifierade mot standarden. Kontrollera alltid resultaten innan du använder dem.

## Innehåll

| Modul | Innehåll | Standard |
|---|---|---|
| `balk` | Raka balkar, statiskt bestämda och obestämda: reaktioner, N, V, M och nedböjning | |
| `tvk` | Tvärsnittsklassning: inre och utstående delar, vinklar, rör | EN 1993-1-1 tabell 5.2 |
| `böjknäckning` | Eulers knäcklast, slankhet, χ, C_m och interaktionsfaktorer | EN 1993-1-1 6.3.1, bilaga A |
| `böjvridknäckning` | C_my, C_mz, C_mLT och interaktionsfaktorer med vippning | EN 1993-1-1 6.3.3, bilaga A |
| `vippning` | Vippningskurvor och χ_LT | EN 1993-1-1 6.3.2 |
| `skjuvbuckling` | η, k_τ, χ_w, flänsbidrag och skjuvbärförmåga | EN 1993-1-5 kap. 5 |
| `KKR`, `VKR` | Tvärsnittsdata för kall- och varmformade rör | EN 10219-2, EN 10210-2 |
| `tvärsnitt` | Tvärsnittsstorheter, bl.a. för I-profiler | |
| `svetsförband` | Svetsförband, β_w | EN 1993-1-8 |
| `trä` | k_mod, γ_M, knäckning och bärförmåga för trä | EN 1995-1-1 |
| `snö` | Formfaktorer för snölast | EN 1991-1-3 |
| `lastkomb` | Lastkombinationer | EN 1990 |
| `display`, `print` | Formatering och LaTeX-utskrift av beräkningar | |
| `tools`, `nyttig` | Hjälpfunktioner | |

## Installation

Kräver Python 3.10 eller senare.

```bash
git clone https://github.com/gitterkorso/kthbygg.git
cd kthbygg
python -m pip install -e .
```

## Exempel

```python
import kthbygg as kb

N_cr = kb.böjknäckning.Euler_Ncr(L=5000, E=210000, I=4.97e6, fall=1)
λ = kb.böjknäckning.λ_z(fyd=355, A=2850, N_z_cr=N_cr)
Φ = kb.böjknäckning.Φ_z(α=0.34, λ_z=λ)
χ = kb.böjknäckning.χ_z(Φ, λ)
print(f"χ_z = {χ:.3f}")
```

### Balkberäkning

`balk` räknar med förskjutningsmetoden och fungerar för både statiskt bestämda och obestämda balkar. Stöd kan vara `"fast"` (inspänning), `"led"` (fixlager) eller `"rull"` (rullager), och inre leder läggs till med `led(x)`.

```python
from kthbygg.balk import Balk

b = Balk(L=12, EI=40e3)          # t.ex. kN, m och kNm²
b.stöd(0, "led").stöd(6, "rull").stöd(12, "rull")
b.utbredd_last(10)               # q = 10 kN/m över hela balken
b.punktlast(9, 25)               # 25 kN nedåt vid x = 9
r = b.lös()

r.skriv()                        # reaktioner, statisk obestämdhet, max/min
r.M(6), r.V(3), r.w(2.5)         # snittkrafter och nedböjning i valfri punkt
r.rita(dragen_sida=True)         # diagram för V, M och w
```

Laster är positiva nedåt och punktmoment positiva moturs. M är positivt när underkanten är dragen och w är positiv nedåt.

Fler exempel finns i notebooken [GuideKTHBYGG.ipynb](GuideKTHBYGG.ipynb).

## Tester

Mappen [tester](tester) innehåller en notebook per område. Varje notebook jämför bibliotekets resultat med handräknade värden och tabellvärden. Öppna en notebook i VS Code, välj kerneln `.venv` och kör **Run All**.

Kontroller märkta *känt fel* visar fel som ännu inte är rättade. Sista cellen stoppar bara om ett nytt, okänt fel dyker upp.

Alla notebooks kan också köras på en gång:

```bash
python -m pip install nbclient
python tester/kor_alla.py
```

## Licens

MIT, se [LICENSE](LICENSE).
