# KTHbygg

KTHbygg är ett Python-bibliotek för dimensionering av bärverk enligt Eurokod. Det är gjort för handberäkningar i Jupyter: funktionerna följer standardens formler steg för steg, och flera av dem kan skriva ut uträkningen med LaTeX.

> **Under utveckling.** Formlerna är inte fullständigt verifierade mot standarden. Kontrollera alltid resultaten innan du använder dem.

## Innehåll

| Modul | Innehåll | Standard |
|---|---|---|
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

Fler exempel finns i notebooken [GuideKTHBYGG.ipynb](GuideKTHBYGG.ipynb).

## Licens

MIT, se [LICENSE](LICENSE).
