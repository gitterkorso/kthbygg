# Linjärelastiska 2D-ramar med Euler–Bernoulli-element och små deformationer.
# Globala krafter: Fx åt höger, Fy uppåt, M moturs.
# Lokal x går från startnod till slutnod, lokal y är 90 grader moturs från x.
import numpy as np

from .balk import Balk, Resultat, _STÖDTYPER


def _tal(*värden):
    a = np.asarray(värden, dtype=float)
    if not np.all(np.isfinite(a)):
        raise ValueError("Alla värden måste vara ändliga")
    return a


def _lös(K, f, låsta):
    d = np.zeros(len(f))
    fria = np.array([i for i in range(len(f)) if i not in låsta], dtype=int)
    if len(fria):
        A = K[np.ix_(fria, fria)]
        diagonal = np.diag(A)
        if np.any(diagonal <= 0):
            raise ValueError("Ramen är en mekanism. Kontrollera stöd och anslutningar.")
        skala = np.sqrt(diagonal)
        A = A / skala[:, None] / skala[None, :]
        if np.linalg.eigvalsh(A)[0] <= 1e-12:
            raise ValueError("Ramen är instabil eller numeriskt nära en mekanism")
        d[fria] = np.linalg.solve(A, f[fria] / skala) / skala
    return d


def _ram_granser(ax):
    # Ge även raka pelare och balkar en läsbar rityta med lika längdskala.
    ax.relim()
    ax.autoscale_view()
    grans = np.array([ax.dataLim.min, ax.dataLim.max])
    if not np.all(np.isfinite(grans)):
        return
    mitt = grans.mean(axis=0)
    spann = grans[1] - grans[0]
    storst = max(spann.max(), 1e-6)
    bredd = np.maximum(spann, .6*storst) + .6*storst
    ax.set_xlim(mitt[0]-bredd[0]/2, mitt[0]+bredd[0]/2, auto=True)
    ax.set_ylim(mitt[1]-bredd[1]/2, mitt[1]+bredd[1]/2, auto=True)


def _placera_nodnamn(ax, etiketter):
    # Jämför textens verkliga storlek med linjer, pilar och övriga texter.
    from matplotlib.transforms import Bbox

    ax.figure.canvas.draw()
    renderer = ax.figure.canvas.get_renderer()
    marginal = renderer.points_to_pixels(3)
    hinder = [linje.get_transform().transform_path(linje.get_path()) for linje in ax.lines]
    for patch in ax.patches:
        hinder.append(patch.get_transform().transform_path(patch.get_path()))
    textrutor = []
    for text in ax.texts:
        if text in etiketter:
            continue
        if text.get_text():
            textrutor.append(text.get_window_extent(renderer))
        pil = getattr(text, "arrow_patch", None)
        if pil is not None:
            hinder.append(pil.get_transform().transform_path(pil.get_path()))
    riktningar = [(1, 1), (-1, 1), (1, -1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]
    for text in etiketter:
        basta = None
        for avstand in (14, 22, 32, 44):
            for dx, dy in riktningar:
                position = avstand * np.array([dx, dy]) / np.hypot(dx, dy)
                text.set_position(position)
                ruta = text.get_window_extent(renderer)
                fri = Bbox.from_extents(ruta.x0-marginal, ruta.y0-marginal,
                                        ruta.x1+marginal, ruta.y1+marginal)
                krockar = sum(path.intersects_bbox(fri, filled=False) for path in hinder)
                krockar += sum(fri.overlaps(annan) for annan in textrutor)
                poang = 1000*krockar + avstand
                if not ax.bbox.contains(fri.x0, fri.y0) or not ax.bbox.contains(fri.x1, fri.y1):
                    poang += 1000
                if basta is None or poang < basta[0]:
                    basta = (poang, position)
            if basta[0] < 1000:
                break
        text.set_position(basta[1])
        textrutor.append(text.get_window_extent(renderer))


class Ram:
    def __init__(self, *, EI=None, EA=None):
        self.EI, self.EA = EI, EA
        self.noder = {}
        self.element = {}
        self._stöd = {}
        self._fjädrar = {}
        self._laster = {}
        self._vinkellaster = {}

    def nod(self, namn, x, y):
        if namn in self.noder:
            raise ValueError(f"Noden {namn!r} finns redan")
        self.noder[namn] = _tal(x, y)
        return self

    def _nod(self, namn):
        if namn not in self.noder:
            raise ValueError(f"Okänd nod: {namn!r}")

    def stång(self, namn, start, slut, *, EI=None, EA=None):
        self._nod(start)
        self._nod(slut)
        if namn in self.element:
            raise ValueError(f"Elementet {namn!r} finns redan")
        ei, ea = self.EI if EI is None else EI, self.EA if EA is None else EA
        if ei is None or ea is None:
            raise ValueError("Ange både EI och EA för ramen eller elementet")
        ei, ea = _tal(ei, ea)
        if min(ei, ea) <= 0 or np.linalg.norm(self.noder[slut] - self.noder[start]) == 0:
            raise ValueError("EI, EA och elementlängden måste vara positiva")
        self.element[namn] = dict(start=start, slut=slut, EI=ei, EA=ea,
                                  q1=0., q2=0., eps=0., kappa=0.)
        return self

    def stöd(self, nod, typ=None, *, ux=False, uy=False, rotation=False):
        self._nod(nod)
        if typ is not None:
            if typ.lower() not in _STÖDTYPER:
                raise ValueError("Välj fast, led eller rull, eller ange ux/uy/rotation")
            if any((ux, uy, rotation)):
                raise ValueError("Ange stödtyp eller individuella låsningar, inte båda")
            ux, uy, rotation = _STÖDTYPER[typ.lower()]
        if not any((ux, uy, rotation)):
            raise ValueError("Minst en frihetsgrad måste låsas")
        tidigare = self._stöd.get(nod, (False, False, False))
        self._stöd[nod] = tuple(a or bool(b) for a, b in zip(tidigare, (ux, uy, rotation)))
        return self

    def fjäderstöd(self, nod, *, kx=0, ky=0, kr=0):
        self._nod(nod)
        k = _tal(kx, ky, kr)
        if np.any(k < 0) or not np.any(k > 0):
            raise ValueError("Fjäderstyvheter måste vara icke-negativa, minst en positiv")
        self._fjädrar[nod] = self._fjädrar.get(nod, np.zeros(3)) + k
        return self

    def nodlast(self, nod, *, Fx=0, Fy=0, M=0, F=None, vinkel=0):
        self._nod(nod)
        _tal(Fx, Fy, M)
        if F is not None:
            _tal(F, vinkel)
            if Fx or Fy or F < 0:
                raise ValueError("Ange F >= 0 och vinkel utan Fx/Fy")
            alfa = np.deg2rad(vinkel)
            Fx, Fy = F*np.cos(alfa), F*np.sin(alfa)
            self._vinkellaster.setdefault(nod, []).append((float(F), float(vinkel)))
        self._laster[nod] = self._laster.get(nod, np.zeros(3)) + _tal(Fx, Fy, M)
        return self

    def punktlast(self, nod, P=0, H=0, *, F=None, vinkel=0):
        return self.nodlast(nod, Fx=H, Fy=-P, F=F, vinkel=vinkel)

    def moment(self, nod, M0):
        return self.nodlast(nod, M=M0)

    def _element(self, namn):
        if namn not in self.element:
            raise ValueError(f"Okänt element: {namn!r}")
        return self.element[namn]

    def utbredd_last(self, element, q, q2=None):
        # Positiv q verkar i negativ lokal y-riktning, per faktisk stånglängd.
        el = self._element(element)
        q1, q2 = _tal(q, q if q2 is None else q2)
        el["q1"] += q1
        el["q2"] += q2
        return self

    def temperatur(self, element, delta_T=0, *, alfa=12e-6, gradient=0):
        # gradient = (T på negativ lokal y-sida - T på positiv lokal y-sida) / höjd.
        el = self._element(element)
        delta_T, alfa, gradient = _tal(delta_T, alfa, gradient)
        el["eps"] += alfa * delta_T
        el["kappa"] += alfa * gradient
        return self

    def lös(self):
        if not self.element:
            raise ValueError("Ramen saknar element")
        index = {namn: i for i, namn in enumerate(self.noder)}
        K = np.zeros((3 * len(index), 3 * len(index)))
        f = np.zeros(len(K))
        elementdata = {}
        for namn, el in self.element.items():
            vektor = self.noder[el["slut"]] - self.noder[el["start"]]
            L = np.linalg.norm(vektor)
            c, s = vektor / L
            rot = np.array([[c, s, 0], [-s, c, 0], [0, 0, 1.]])
            T = np.zeros((6, 6))
            T[:3, :3] = T[3:, 3:] = rot
            EI, EA = el["EI"], el["EA"]
            k = np.zeros((6, 6))
            böj = [1, 2, 4, 5]
            k[np.ix_(böj, böj)] = EI / L**3 * np.array([
                [12, 6*L, -12, 6*L], [6*L, 4*L**2, -6*L, 2*L**2],
                [-12, -6*L, 12, -6*L], [6*L, 2*L**2, -6*L, 4*L**2]])
            k[np.ix_([0, 3], [0, 3])] = EA / L * np.array([[1, -1], [-1, 1]])
            p1, p2 = -el["q1"], -el["q2"]
            fe = np.array([-EA*el["eps"], L*(7*p1+3*p2)/20,
                           L**2*(3*p1+2*p2)/60 - EI*el["kappa"],
                           EA*el["eps"], L*(3*p1+7*p2)/20,
                           -L**2*(2*p1+3*p2)/60 + EI*el["kappa"]])
            i, j = index[el["start"]], index[el["slut"]]
            dofs = np.array([3*i, 3*i+1, 3*i+2, 3*j, 3*j+1, 3*j+2])
            K[np.ix_(dofs, dofs)] += T.T @ k @ T
            f[dofs] += T.T @ fe
            elementdata[namn] = dict(T=T, k=k, fe=fe, dofs=dofs, L=L, el=el.copy())
        for nod, last in self._laster.items():
            i = 3 * index[nod]
            f[i:i+3] += last
        fjäder = np.zeros(len(K))
        for nod, styvhet in self._fjädrar.items():
            i = 3 * index[nod]
            fjäder[i:i+3] += styvhet
        låsta = {3*index[nod]+j for nod, mask in self._stöd.items() for j, låst in enumerate(mask) if låst}
        d = _lös(K + np.diag(fjäder), f, låsta)
        # K innehåller bara stångstyvheter: residualen ger samtliga stödreaktioner.
        R = K @ d - f
        return RamResultat(self, index, elementdata, d, R)

    def rita_modell(self, *, ax=None, titel=None, deformerad=False, skala=None,
                    langdenhet="m", kraftenhet="kN"):
        if deformerad:
            return self.lös().rita_deformerad(skala=skala, ax=ax, titel=titel,
                                              langdenhet=langdenhet, kraftenhet=kraftenhet)
        import matplotlib.pyplot as plt
        if ax is None:
            _, ax = plt.subplots(figsize=(8, 6))
        from matplotlib.patches import FancyArrowPatch
        punkter = np.array(list(self.noder.values()))
        spann = max(np.ptp(punkter, axis=0)) if len(punkter) else 1.
        lasthojd = .12 * (spann or 1.)
        qmax = max((abs(el[k]) for el in self.element.values() for k in ("q1", "q2")), default=1.) or 1.
        for nummer, (namn, el) in enumerate(self.element.items(), start=1):
            a, b = self.noder[el["start"]], self.noder[el["slut"]]
            ax.plot(*np.array([a, b]).T, color="black", lw=1.5, solid_capstyle="butt", gid="ursprungsgeometri")
            etikett = [str(nummer)]
            if el["q1"] or el["q2"]:
                q1, q2 = el["q1"], el["q2"]
                tangent = (b-a) / np.linalg.norm(b-a)
                normal = np.array([-tangent[1], tangent[0]])
                t = np.linspace(0, 1, max(3, int(18*np.linalg.norm(b-a)/(spann or 1.))+1))
                if q1*q2 < 0:
                    t = np.sort(np.append(t, -q1/(q2-q1)))
                q = q1 + (q2-q1)*t
                bas = a + t[:, None]*(b-a)
                topp = bas + (lasthojd*np.abs(q)/qmax)[:, None]*normal
                kontur = np.vstack([a, topp, b])
                ax.plot(*kontur.T, color="tab:blue", lw=1.1,
                        solid_capstyle="butt", solid_joinstyle="miter", zorder=5)
                for fot, ovre, last in zip(bas, topp, q):
                    if abs(last) < qmax*.04:
                        continue
                    start, slut = (ovre, fot) if last > 0 else (fot, ovre)
                    ax.add_patch(FancyArrowPatch(start, slut, arrowstyle="-|>",
                                 mutation_scale=min(9, 45*abs(last)/qmax),
                                 lw=1.1, color="tab:blue", shrinkA=0, shrinkB=0,
                                 capstyle="butt", joinstyle="miter", zorder=4))
                index = 0 if abs(q1) >= abs(q2) else -1
                plats = (topp[0]+topp[-1])/2 if q1 == q2 else topp[index]
                ax.annotate(f"q = {max(abs(q1), abs(q2)):g} {kraftenhet}/{langdenhet}",
                            plats, xytext=tuple(15*normal), textcoords="offset points",
                            ha="center", va="center", fontsize=9, color="tab:blue")
                # Stångnumret placeras på andra sidan om stången från lasten.
                ax.annotate(str(nummer), (a+b)/2, xytext=tuple(-12*normal),
                            textcoords="offset points", ha="center", va="center", fontsize=9)
                etikett = []
            if el["eps"] or el["kappa"]:
                etikett.append(f"εT={el['eps']:g}, κT={el['kappa']:g}")
            ax.annotate("\n".join(etikett), (a+b)/2, xytext=(5, 5), textcoords="offset points", fontsize=9)
        nodetiketter = []
        for nummer, (namn, xy) in enumerate(self.noder.items(), start=1):
            ax.plot(*xy, "ko", ms=3)
            # Fortsätt med AA, AB, ... efter Z.
            bokstav = ""
            while nummer:
                nummer, rest = divmod(nummer - 1, 26)
                bokstav = chr(65 + rest) + bokstav
            nodetiketter.append(ax.annotate(bokstav, xy, xytext=(10, 10),
                                            textcoords="offset points", ha="center", va="center"))
            if namn in self._stöd:
                mask = self._stöd[namn]
                if all(mask):
                    from matplotlib.transforms import Affine2D, ScaledTranslation
                    from .balkstil import _rita_inspanning, STILAR

                    # Vänd stödet bort från den anslutande stången.
                    anslutningar = [
                        self.noder[el["slut"] if el["start"] == namn else el["start"]] - xy
                        for el in self.element.values() if namn in (el["start"], el["slut"])
                    ]
                    inat = sum((v / np.linalg.norm(v) for v in anslutningar), np.zeros(2))
                    if np.linalg.norm(inat) < 1e-12:
                        inat = anslutningar[0] if anslutningar else np.array([0., 1.])
                    vinkel = np.arctan2(-inat[1], -inat[0])
                    # Symbolstorlek i punkter, oberoende av ramens mått och zoom.
                    transform = (Affine2D().scale(.65 / 72).rotate(vinkel)
                                 + ax.figure.dpi_scale_trans
                                 + ScaledTranslation(*xy, ax.transData))
                    _rita_inspanning(ax, transform, STILAR["teknisk"].balk)
                else:
                    ax.plot(*xy, marker="^", ms=10, mfc="white", mec="black")
            if namn in self._fjädrar:
                etikett = ", ".join(f"{k}={v:g}" for k, v in zip(("kx", "ky", "kr"), self._fjädrar[namn]) if v)
                ax.annotate("fjäder " + etikett, xy,
                            xytext=(8, -28), textcoords="offset points", fontsize=8)
            if namn in self._laster:
                fx, fy, moment = self._laster[namn]
                from .balkstil import _rita_vinkelkraft
                for F, vinkel in self._vinkellaster.get(namn, []):
                    _rita_vinkelkraft(ax, xy, F, vinkel, "tab:blue", kraftenhet)
                    fx -= F*np.cos(np.deg2rad(vinkel))
                    fy -= F*np.sin(np.deg2rad(vinkel))
                if abs(fx) < 1e-12:
                    fx = 0.
                if abs(fy) < 1e-12:
                    fy = 0.
                for komponent, kraft, riktning in (("Fx", fx, (1, 0)), ("Fy", fy, (0, 1))):
                    if not kraft:
                        continue
                    # Pilspetsen ligger vid noden; längden anges i bildpunkter.
                    dx, dy = -48 * np.sign(kraft) * np.array(riktning)
                    ax.annotate("", xy, xytext=(dx, dy), textcoords="offset points",
                                arrowprops=dict(arrowstyle="-|>", color="tab:blue",
                                                lw=1.6, mutation_scale=13,
                                                shrinkA=0, shrinkB=0),
                                zorder=7)
                    ax.annotate(f"{komponent}={kraft:g}", xy,
                                xytext=(dx/2 + (9 if dy else 0), dy/2 + (9 if dx else 0)),
                                textcoords="offset points", fontsize=8, color="tab:blue",
                                ha="left" if dy else "center", va="center")
                if moment:
                    ax.annotate(f"M={moment:g}", xy, ha="center",
                                xytext=(0, 20), textcoords="offset points", fontsize=8,
                                color="tab:blue")
        ax.set_aspect("equal", adjustable="box")
        _ram_granser(ax)
        ax.set(xlabel=f"x [{langdenhet}]", ylabel=f"y [{langdenhet}]", title=titel or "Rammodell")
        ax.grid(alpha=.2)
        _placera_nodnamn(ax, nodetiketter)
        from .balkstil import _forbered_visning
        return _forbered_visning(ax.figure)


class RamResultat:
    def __init__(self, ram, index, elementdata, d, R):
        self.ram = ram
        self.förskjutningar = {n: dict(zip(("ux", "uy", "rotation"), d[3*i:3*i+3])) for n, i in index.items()}
        self.reaktioner = {n: dict(zip(("H", "V", "M"), R[3*i:3*i+3]))
                          for n, i in index.items() if n in ram._stöd or n in ram._fjädrar}
        self.ändkrafter = {}
        self._resultat = {}
        self._data = elementdata
        for namn, data in elementdata.items():
            el, L = data["el"], data["L"]
            dl = data["T"] @ d[data["dofs"]]
            F = data["k"] @ dl - data["fe"]
            # Lokala nodändkrafter (inte samma tecken som snittkrafter på båda sidor).
            self.ändkrafter[namn] = dict(zip(("Fx1", "Fy1", "M1", "Fx2", "Fy2", "M2"), F))
            balk = Balk(L, EI=el["EI"], EA=el["EA"])
            e = dict(x0=0., Le=L, EI=el["EI"], d=dl[[1, 2, 4, 5]], u=dl[[0, 3]].copy(),
                     N=-F[0], Fv1=F[1], Fθ1=F[2], p1=-el["q1"], p2=-el["q2"])
            self._resultat[namn] = Resultat(balk, [e], {}, 0)
            data["dl"] = dl

    def elementresultat(self, element):
        if element not in self._resultat:
            raise ValueError(f"Okänt element: {element!r}")
        return self._resultat[element]

    def N(self, element, x):
        return self.elementresultat(element).N(x)

    def V(self, element, x):
        return self.elementresultat(element).V(x)

    def M(self, element, x):
        return self.elementresultat(element).M(x)

    def w(self, element, x):
        # Positiv mot negativ lokal y; inkluderar nodernas förskjutningar.
        return self.elementresultat(element).w(x)

    def rita(self, storhet="M", *, skala=None, ax=None, dragen_sida=True,
             värden=True, kraftenhet="kN", langdenhet="m"):
        if storhet not in ("N", "V", "M", "w"):
            raise ValueError("Välj N, V, M eller w")
        from matplotlib.collections import LineCollection
        from .balk import _FÄRGER, _STRECKADE, _mörkare, _diagramfaktor, _axeltitel

        fig = self.ram.rita_modell(ax=ax, titel=_axeltitel(storhet, kraftenhet, langdenhet),
                                   kraftenhet=kraftenhet, langdenhet=langdenhet)
        ax = fig.axes[0] if ax is None else ax
        kurvor = {n: r.kurva(storhet) for n, r in self._resultat.items()}
        maxvärde = max(np.max(np.abs(y)) for x, y in kurvor.values())
        längd = max(d["L"] for d in self._data.values())
        if skala is None:
            skala = .2 * längd / maxvärde if maxvärde > 1e-12 else 1.
        for namn, (x, y) in kurvor.items():
            data = self._data[namn]
            a = self.ram.noder[data["el"]["start"]]
            riktning = data["T"][0, :2]
            normal = data["T"][1, :2]
            bas = a + x[:, None] * riktning
            sida = -1 if storhet == "w" or (storhet == "M" and dragen_sida) else 1
            kurva = bas + sida * skala * y[:, None] * normal
            resultat = self._resultat[namn]
            if resultat._är_noll(y):
                continue
            kontur = np.vstack([bas[0], kurva, bas[-1]])
            ax.fill(*kontur.T, color=_FÄRGER[storhet], alpha=.25, linewidth=0)
            if storhet in _STRECKADE:
                xs, ys = resultat._streckning(storhet)
                fot = a + xs[:, None]*riktning
                spets = fot + sida*skala*ys[:, None]*normal
                ax.add_collection(LineCollection(np.stack([fot, spets], axis=1),
                                  colors=_FÄRGER[storhet], linewidths=.8, capstyle="butt"))
            ax.plot(*kontur.T, color=_mörkare(_FÄRGER[storhet]), lw=2,
                    solid_capstyle="butt", solid_joinstyle="miter")
            ax.plot(*np.array([bas[0], bas[-1]]).T, color="black", lw=1.5,
                    solid_capstyle="butt", zorder=4)
            if värden:
                for xi, yi, ha in resultat._etikettpunkter(storhet, maxvärde or 1.):
                    punkt = a + xi*riktning + sida*skala*yi*normal
                    offset = 9*sida*np.sign(yi)*normal
                    ax.annotate(f"{yi*_diagramfaktor(storhet, langdenhet):.3g}", punkt,
                                xytext=tuple(offset), textcoords="offset points",
                                ha="center", va="center", fontsize=8)
        ax.set(xlabel=f"x [{langdenhet}]", ylabel=f"y [{langdenhet}]")
        _ram_granser(ax)
        nodtexter = [t for t in ax.texts if t.get_text().isalpha() and t.get_text().isupper()]
        _placera_nodnamn(ax, nodtexter)
        return fig

    def rita_deformerad(self, skala=None, *, ax=None, titel=None,
                        langdenhet="m", kraftenhet="kN"):
        fig = self.ram.rita_modell(ax=ax, titel=titel or "Deformerad ram",
                                  langdenhet=langdenhet, kraftenhet=kraftenhet)
        ax = fig.axes[0] if ax is None else ax
        kurvor = []
        for namn, data in self._data.items():
            x = np.linspace(0, data["L"], 101)
            dl = data["dl"]
            u = dl[0] + (dl[3] - dl[0]) * x / data["L"]
            v = -self.w(namn, x)
            a = self.ram.noder[data["el"]["start"]]
            bas = a + x[:, None]*data["T"][0, :2]
            delta = u[:, None]*data["T"][0, :2] + v[:, None]*data["T"][1, :2]
            kurvor.append((bas, delta))
        from .deformation import rita_kurvor
        rita_kurvor(ax, kurvor, skala, max(d["L"] for d in self._data.values()))
        _ram_granser(ax)
        return fig
