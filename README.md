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

`resultat.grad` och `resultat.skriv()` anger den totala statiska obestämdheten,
inklusive axialstöd: två fixlager ger grad 1 och två inspänningar ger grad 3.
Nollaster skapar inga extra beräkningsnoder. För tätt placerade verksamma
laster används högre precision när den vanliga styvhetslösningen är illa konditionerad.

```python
from kthbygg.balk import Balk

b = Balk(L=12, EI=40e3)          # t.ex. kN, m och kNm²
b.stöd(0, "led").stöd(6, "rull").stöd(12, "rull")
b.utbredd_last(10)               # q = 10 kN/m över hela balken
b.punktlast(9, 25)               # 25 kN nedåt vid x = 9
r = b.lös()

r.skriv()                        # reaktioner, statisk obestämdhet, max/min
r.M(6), r.V(3), r.w(2.5)         # snittkrafter och nedböjning i valfri punkt
r.rita(dragen_sida=True)         # balken och diagram för N, V, M och w
r.rita("VM")                     # bara valda diagram, eller r.rita_M() osv.
r.rita_interaktiv()              # håll muspekaren över diagrammen för att se värden
```

`rita()` skriver ut värdena vid ändar, språng, knäckar och extrempunkter. Diagrammen har fasta färger: N grön, V blå, M röd och w grå, och laster ritas ljusblå. `rita_interaktiv()` använder plotly och visar N, V, M och w för samma x när du håller muspekaren över diagrammen. plotly installeras med:

```bash
python -m pip install "kthbygg[interaktiv]"
```

Laster är positiva nedåt och punktmoment positiva moturs. M är positivt när underkanten är dragen och w är positiv nedåt.

Fler exempel finns i notebooken [GuideKTHBYGG.ipynb](GuideKTHBYGG.ipynb).

### Teknisk balkritning

`Balk.rita_modell()` ritar balk, laster, stöd och mått i teknisk stil utan att lösa modellen.

```python
fig = b.rita_modell(langdenhet="m", kraftenhet="kN")
fig.savefig("balk.svg", bbox_inches="tight")
```

Enhetstexterna är etiketter och konverterar inte indata. Ange exempelvis
`langdenhet="mm", kraftenhet="N"` för modeller med dessa enheter.
`matt=False` döljer måtten. Befintlig `Resultat.rita()` och de interaktiva diagrammen fungerar som tidigare.

Kör `python exempel/ritstilar.py` och öppna `exempel/ritstilar.html` för
exempel med fritt upplagd balk, konsol och triangulär last.
Exemplet skapar `ritstil_teknisk.svg` och en PNG-förhandsvisning.

Snittkraftsdiagrammens y-axlar visar `N(x) [kN]`, `V(x) [kN]` och `M(x) [kNm]`.
Använd `kraftenhet="N", langdenhet="mm"` i `rita()` eller `rita_interaktiv()`
för andra indataenheter. Detta ändrar enbart etiketterna, inte beräkningsvärdena.

Färgläge för modellritningen: `b.rita_modell(färgat=True)` ger blå laster
och röda längdmått. Anpassa rött med exempelvis `måttfärg="#d62728"`.

Spara modellritningar och Matplotlib-diagram direkt på skrivbordet:

```python
fig = b.rita_modell(färgat=True)
fig.spara("konsol.svg")
fig.spara("konsol.pdf")
```

`fig.spara("konsol")` använder SVG. Utan argument blir namnet `balk.svg`.
Metoden returnerar sökvägen och skriver över en befintlig fil med samma namn.
Skrivbordet är på datorn där Python körs; på en fjärrserver är det serverns skrivbord.

## Varierande styvhet, fjäderstöd och temperatur

```python
from kthbygg.balk import Balk

b = Balk(6, EI=40000, EA=200000)
b.stöd(0, "fast")
b.sektion(3, 6, EI=20000, EA=100000)
b.fjäderstöd(6, ky=1000, kx=50000, kr=200)
b.temperatur(30, alfa=12e-6)
b.temperatur(gradient=50, alfa=12e-6, x1=3, x2=6)
b.punktlast(6, P=12)
r = b.lös()
print(r.förskjutningar)
r.rita()
```

`sektion(x1, x2, EI=..., EA=...)` ändrar styvheten inom intervallet.
Utanför gäller balkens grundvärden. Intervall får inte överlappa.
`fjäderstöd` anger fjädrar mot mark: `kx`, `ky` i kraft/längd och `kr` i
moment/radian. Upprepade fjädrar på samma plats adderas. Reaktionerna
inkluderar fjäderkrafterna. En rotationsfjäder precis i en inre led stöds inte.

`temperatur(delta_T, alfa=..., gradient=..., x1=..., x2=...)` anger
temperaturändring relativt det spänningsfria tillståndet. `alfa` anges per grad.
`gradient = (T_undersida - T_översida) / höjd` i grader per längdenhet:
10 graders skillnad över 0,2 m ger `gradient=50` när modellen använder meter.
Temperaturlaster adderas. De ger fri töjning `alfa*delta_T` och fri krökning
`alfa*gradient`; inspänning kan därför ge krafter även utan mekanisk last.
`förskjutningar[x]` innehåller `u` åt höger, `w` nedåt och `rotation` moturs.

## 2D-ramar

```python
from kthbygg.ram import Ram

ram = Ram(EI=40000, EA=200000)
ram.nod("A", 0, 0).nod("B", 0, 3).nod("C", 4, 4).nod("D", 4, 0)
ram.stång("AB", "A", "B")
ram.stång("BC", "B", "C", EI=60000, EA=300000)
ram.stång("CD", "C", "D")
ram.stöd("A", "fast").stöd("D", "led")
ram.fjäderstöd("B", kx=1000)
ram.nodlast("B", Fx=8, Fy=-10, M=0)
ram.utbredd_last("BC", q=6, q2=9)
ram.temperatur("BC", delta_T=30, alfa=12e-6)

r = ram.lös()
print(r.reaktioner)
print(r.förskjutningar)
print(r.M("BC", 2))
ram.rita_modell()
r.rita("M")
r.rita_deformerad(skala=100)
```

Noder ansluts med namn, inte genom att enbart ha samma koordinater.
Elementen har styva knutpunkter. Punktlaster och stöd sätts i noder;
dela en stång vid en mellanliggande last eller ett styvhetsbyte.
`stöd(nod, ux=True, uy=False, rotation=False)` låser valda globala frihetsgrader.
`"rull"` låser global y. `"led"` låser båda translationerna men frigör
nodrotationen mot mark; det skapar inte en inre led mellan anslutande stänger.

`nodlast` använder global Fx åt höger, Fy uppåt och M moturs.
`punktlast(nod, P=..., H=...)` har P nedåt, som `Balk`.
Utbredd last verkar i negativ **lokal y**, per faktisk stånglängd.
Lokal x går från startnod till slutnod; lokal y är vriden 90 grader moturs.
Positiv temperaturgradient betyder varmare på negativ lokal y-sida.
EI och EA måste anges explicit för ramen eller för varje stång.

Resultatets `N`, `V`, `M`, `w` tar elementnamn och lokal x-koordinat.
`w` är positiv mot negativ lokal y och inkluderar nodförskjutningarna.
`förskjutningar` innehåller globala `ux`, `uy`, `rotation`.
`ändkrafter` är lokala nodändkrafter med komponenterna Fx1, Fy1, M1, Fx2, Fy2, M2.
För separata elementdiagram används `r.elementresultat("BC").rita(visa_balk=False)`.
Ramdiagrammens höjd skalas automatiskt; `skala=` väljer diagramhöjd per resultatenhet.

Båda lösarna använder direkt styvhetsmetod, linjärelastiska
Euler–Bernoulli-element och små deformationer. Ramklassen stöder ännu inte
inre leder, sneda stödaxlar, stödsättningar, skjuvdeformation, knäckning,
andra ordningen, plasticitet eller 3D. Modellritningarna är schematiska.

### Verifiering

```shell
python -m unittest tester.test_ram_solver -v
python -m tester.validera_rustyfem --exe "C:/sökväg/till/rustyfem.exe"
```

15 jämförelsefall och resultaten finns i [validation/rustyfem/rapport.md](validation/rustyfem/rapport.md).
Rapporten beskriver jämförda storheter, toleranser och begränsningar.
Avkylning gav konvergensfel i RustyFEM i två extra diagnostiska fall;
temperaturgradient stöds inte där. Dessa räknas inte som godkända jämförelser
och verifieras i stället analytiskt i KTHBYGG.
