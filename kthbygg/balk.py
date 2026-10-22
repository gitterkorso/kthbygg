# Balkberäkning med förskjutningsmetoden (Euler-Bernoulli-balk).
#
# Fungerar för både statiskt bestämda och statiskt obestämda raka balkar med
# inspänningar, fixlager, rullager och inre leder. Ger stödreaktioner och
# snittkrafterna N(x), V(x), M(x) samt nedböjningen w(x) längs balken.
# Snittkrafterna räknas exakt inom varje element, inte approximativt.
#
# Teckenregler
#   x       längs balken, från vänster ände (x = 0) till höger ände (x = L)
#   P, q    vertikala laster, positiva nedåt
#   H       horisontell punktlast, positiv åt höger
#   M0      punktmoment, positivt moturs
#   Reaktioner: V positiv uppåt, H positiv åt höger, M positivt moturs
#   N(x)    normalkraft, positiv som drag
#   V(x)    tvärkraft = summan av vertikala krafter till vänster om snittet,
#           positiv uppåt, så att dM/dx = V
#   M(x)    böjmoment, positivt när underkanten är dragen
#   w(x)    nedböjning, positiv nedåt
#
# Enheterna väljer du själv men de måste vara konsekventa, t.ex. kN, m och kNm²
# eller N, mm och Nmm². Med konstant EI beror reaktioner och snittkrafter inte
# på EI, men nedböjningen gör det.
#
# Exempel: kontinuerlig balk över två fack
#   b = Balk(L=12, EI=40e3)
#   b.stöd(0, "led"); b.stöd(6, "rull"); b.stöd(12, "rull")
#   b.utbredd_last(10)
#   r = b.lös()
#   r.skriv()
#   r.rita()

import numpy as np

# Låsta frihetsgrader (u, w, θ) för varje stödtyp
_STÖDTYPER = {
    "fast": (True, True, True),
    "inspänd": (True, True, True),
    "inspänning": (True, True, True),
    "led": (True, True, False),
    "fixlager": (True, True, False),
    "rull": (False, True, False),
    "rullager": (False, True, False),
}


class Balk:
    def __init__(self, L, EI=None, EA=None):
        if L <= 0:
            raise ValueError(f"Balklängden måste vara positiv (du angav L = {L})")
        self.L = float(L)
        self.EI_angivet = EI is not None
        self.EI = float(EI) if EI is not None else 1.0
        self.EA = float(EA) if EA is not None else 1.0
        self._stöd = {}
        self._leder = []
        self._punktlaster = []
        self._punktmoment = []
        self._utbredda = []

    def _x(self, x, vad):
        x = float(x)
        if not 0 <= x <= self.L:
            raise ValueError(f"{vad} vid x = {x} ligger utanför balken (0 ≤ x ≤ {self.L})")
        return x

    def stöd(self, x, typ):
        """Lägg till ett stöd: "fast" (inspänning), "led" (fixlager) eller "rull" (rullager)."""
        typ = typ.lower()
        if typ not in _STÖDTYPER:
            raise ValueError(f"Okänd stödtyp '{typ}'. Välj bland: fast, led, rull")
        self._stöd[self._x(x, "Stödet")] = typ
        return self

    def led(self, x):
        """Lägg till en inre led (momentfri förbindelse) vid x."""
        x = self._x(x, "Leden")
        if x == 0 or x == self.L:
            raise ValueError("En inre led måste ligga mellan balkens ändar")
        self._leder.append(x)
        return self

    def punktlast(self, x, P, H=0.0):
        """Punktlast P (positiv nedåt) och valfri horisontell last H (positiv åt höger)."""
        self._punktlaster.append((self._x(x, "Punktlasten"), float(P), float(H)))
        return self

    def moment(self, x, M0):
        """Punktmoment M0, positivt moturs."""
        self._punktmoment.append((self._x(x, "Punktmomentet"), float(M0)))
        return self

    def utbredd_last(self, q, x1=0.0, x2=None, q2=None):
        """Utbredd last q (positiv nedåt) från x1 till x2.

        Anges q2 varierar lasten linjärt från q vid x1 till q2 vid x2."""
        x1 = self._x(x1, "Lastens början")
        x2 = self._x(self.L if x2 is None else x2, "Lastens slut")
        if x2 <= x1:
            raise ValueError(f"Den utbredda lasten måste ha x1 < x2 (du angav x1 = {x1}, x2 = {x2})")
        self._utbredda.append((x1, x2, float(q), float(q if q2 is None else q2)))
        return self

    def _last_på(self, xa, xb, tol):
        # Utbredd last (positiv uppåt) i elementets ändar
        p1 = p2 = 0.0
        for x1, x2, q1, q2 in self._utbredda:
            if x1 <= xa + tol and xb <= x2 + tol:
                lutning = (q2 - q1) / (x2 - x1)
                p1 -= q1 + lutning * (xa - x1)
                p2 -= q1 + lutning * (xb - x1)
        return p1, p2

    def lös(self):
        """Lös balken och returnera ett Resultat."""
        if not self._stöd:
            raise ValueError("Balken saknar stöd")
        tol = 1e-9 * self.L

        # Noder i alla punkter där något händer
        punkter = {0.0, self.L, *self._stöd, *self._leder}
        punkter |= {x for x, _, _ in self._punktlaster}
        punkter |= {x for x, _ in self._punktmoment}
        for x1, x2, _, _ in self._utbredda:
            punkter |= {x1, x2}
        noder = []
        for x in sorted(punkter):
            if not noder or x - noder[-1] > tol:
                noder.append(x)
        noder = np.array(noder)
        n = len(noder)

        def nod(x):
            return int(np.argmin(np.abs(noder - x)))

        stöd_vid = {nod(x): _STÖDTYPER[typ] for x, typ in self._stöd.items()}
        leder = {nod(x) for x in self._leder}
        for i in leder:
            if i in stöd_vid and stöd_vid[i][2]:
                raise ValueError(f"En inre led kan inte ligga i en inspänning (x = {noder[i]})")

        # Frihetsgrader för böjning: w och θ i varje nod, två θ i en led
        dof_w, dof_θv, dof_θh = [], [], []
        k = 0
        for i in range(n):
            dof_w.append(k)
            k += 1
            dof_θv.append(k)
            if i in leder:
                k += 1
            dof_θh.append(k)
            k += 1
        ndof = k

        K = np.zeros((ndof, ndof))
        f = np.zeros(ndof)
        element = []
        for e in range(n - 1):
            x0, Le = noder[e], noder[e + 1] - noder[e]
            dofs = [dof_w[e], dof_θh[e], dof_w[e + 1], dof_θv[e + 1]]
            ke = self.EI / Le**3 * np.array([
                [12, 6 * Le, -12, 6 * Le],
                [6 * Le, 4 * Le**2, -6 * Le, 2 * Le**2],
                [-12, -6 * Le, 12, -6 * Le],
                [6 * Le, 2 * Le**2, -6 * Le, 4 * Le**2],
            ])
            p1, p2 = self._last_på(x0, noder[e + 1], tol)
            # Ekvivalenta nodlaster för linjärt varierande last
            fe = np.array([
                Le * (7 * p1 + 3 * p2) / 20,
                Le**2 * (3 * p1 + 2 * p2) / 60,
                Le * (3 * p1 + 7 * p2) / 20,
                -Le**2 * (2 * p1 + 3 * p2) / 60,
            ])
            K[np.ix_(dofs, dofs)] += ke
            f[dofs] += fe
            element.append({"x0": x0, "Le": Le, "dofs": dofs, "ke": ke, "fe": fe, "p1": p1, "p2": p2})

        for x, P, _ in self._punktlaster:
            f[dof_w[nod(x)]] -= P
        for x, M0 in self._punktmoment:
            i = nod(x)
            if i in leder:
                raise ValueError(f"Ett punktmoment kan inte läggas i en inre led (x = {noder[i]}), "
                                 "lägg det strax till vänster eller höger om leden")
            f[dof_θv[i]] += M0

        låsta = set()
        for i, (_, w_låst, θ_låst) in stöd_vid.items():
            if w_låst:
                låsta.add(dof_w[i])
            if θ_låst:
                låsta.add(dof_θv[i])
        fria = [d for d in range(ndof) if d not in låsta]

        Kff = K[np.ix_(fria, fria)]
        if fria and np.linalg.matrix_rank(Kff) < len(fria):
            raise ValueError("Balken är en mekanism och kan inte bära lasten. Kontrollera stöd och leder.")
        d = np.zeros(ndof)
        if fria:
            d[fria] = np.linalg.solve(Kff, f[fria])
        R = K @ d - f

        for el in element:
            F = el["ke"] @ d[el["dofs"]] - el["fe"]
            el["d"] = d[el["dofs"]]
            el["Fv1"], el["Fθ1"] = F[0], F[1]

        # Axialkraft löses separat, den är frikopplad från böjningen för en rak balk
        H_nod = np.zeros(n)
        for x, _, H in self._punktlaster:
            H_nod[nod(x)] += H
        u_låsta = [i for i, (u_låst, _, _) in stöd_vid.items() if u_låst]
        u = np.zeros(n)
        R_u = np.zeros(n)
        if u_låsta:
            Ka = np.zeros((n, n))
            for e in range(n - 1):
                ka = self.EA / element[e]["Le"]
                Ka[np.ix_([e, e + 1], [e, e + 1])] += ka * np.array([[1, -1], [-1, 1]])
            u_fria = [i for i in range(n) if i not in u_låsta]
            if u_fria:
                u[u_fria] = np.linalg.solve(Ka[np.ix_(u_fria, u_fria)], H_nod[u_fria])
            R_u = Ka @ u - H_nod
        elif np.any(np.abs(H_nod) > 0):
            raise ValueError("Balken har horisontell last men inget stöd som tar horisontell kraft. "
                             "Använd 'led' eller 'fast' för minst ett stöd.")
        for e, el in enumerate(element):
            el["N"] = self.EA / el["Le"] * (u[e + 1] - u[e])

        reaktioner = {}
        for i in sorted(stöd_vid):
            u_låst, w_låst, θ_låst = stöd_vid[i]
            reaktioner[float(noder[i])] = {
                "V": R[dof_w[i]] if w_låst else 0.0,
                "H": R_u[i] if u_låst else 0.0,
                "M": R[dof_θv[i]] if θ_låst else 0.0,
            }

        # Statiskt obestämd grad för böjning: låsta w och θ minus jämviktsekvationer och leder
        grad = len(låsta) - 2 - len(leder)
        return Resultat(self, element, reaktioner, grad)


class Resultat:
    def __init__(self, balk, element, reaktioner, grad):
        self.balk = balk
        self.reaktioner = reaktioner
        self.grad = grad
        self._element = element
        self._x0 = np.array([el["x0"] for el in element])

    def _hitta(self, x, sida):
        if sida == "höger":
            e = int(np.searchsorted(self._x0, x, side="right")) - 1
        elif sida == "vänster":
            e = int(np.searchsorted(self._x0, x, side="left")) - 1
        else:
            raise ValueError("sida ska vara 'vänster' eller 'höger'")
        return min(max(e, 0), len(self._element) - 1)

    def _polynom(self, el, storhet):
        # Varje storhet är ett polynom i ξ = x - x0 inom elementet
        Le, p1, p2 = el["Le"], el["p1"], el["p2"]
        if storhet == "N":
            return np.polynomial.Polynomial([el["N"]])
        if storhet == "V":
            return np.polynomial.Polynomial([el["Fv1"], p1, (p2 - p1) / (2 * Le)])
        if storhet == "M":
            return np.polynomial.Polynomial([-el["Fθ1"], el["Fv1"], p1 / 2, (p2 - p1) / (6 * Le)])
        if storhet != "w":
            raise ValueError(f"Okänd storhet '{storhet}', välj N, V, M eller w")
        # Nedböjning: Hermite-interpolation av nodförskjutningarna plus lösningen för
        # en fast inspänd balk med elementets last (v uppåt, w = -v)
        EI = self.balk.EI
        v1, θ1, v2, θ2 = el["d"]
        a = (p1 * Le**4 / 24 + (p2 - p1) * Le**4 / 120) / EI
        da = (p1 * Le**3 / 6 + (p2 - p1) * Le**3 / 24) / EI
        c3 = (2 * a / Le - da) / Le**2
        c2 = (-a - c3 * Le**3) / Le**2
        v = np.polynomial.Polynomial([
            v1,
            θ1,
            -3 * v1 / Le**2 - 2 * θ1 / Le + 3 * v2 / Le**2 - θ2 / Le + c2,
            2 * v1 / Le**3 + θ1 / Le**2 - 2 * v2 / Le**3 + θ2 / Le**2 + c3,
            p1 / (24 * EI),
            (p2 - p1) / (120 * Le * EI),
        ])
        return -v

    def _värde(self, el, ξ, storhet):
        return self._polynom(el, storhet)(ξ)

    def _kritiska_punkter(self, el, storhet):
        # Elementets ändar och derivatans nollställen inuti elementet
        rötter = self._polynom(el, storhet).deriv().roots() if storhet != "N" else []
        inre = [r.real for r in rötter if abs(r.imag) < 1e-9 * el["Le"] and 0 < r.real < el["Le"]]
        return np.array([0.0, *inre, el["Le"]])

    def _i_punkt(self, x, storhet, sida):
        x = np.asarray(x, dtype=float)
        if np.any((x < 0) | (x > self.balk.L)):
            raise ValueError(f"x måste ligga mellan 0 och {self.balk.L}")
        ut = []
        for xi in x.ravel():
            el = self._element[self._hitta(xi, sida)]
            ut.append(self._värde(el, xi - el["x0"], storhet))
        ut = np.array(ut)
        return ut.reshape(x.shape) if x.shape else float(ut[0])

    def N(self, x, sida="höger"):
        """Normalkraft i x (positiv som drag)."""
        return self._i_punkt(x, "N", sida)

    def V(self, x, sida="höger"):
        """Tvärkraft i x. Vid en punktlast ger sida="höger" värdet strax till höger."""
        return self._i_punkt(x, "V", sida)

    def M(self, x, sida="höger"):
        """Böjmoment i x (positivt när underkanten är dragen)."""
        return self._i_punkt(x, "M", sida)

    def w(self, x):
        """Nedböjning i x (positiv nedåt)."""
        return self._i_punkt(x, "w", "höger")

    def kurva(self, storhet, punkter_per_element=200):
        """x- och värden längs hela balken. Vid språng finns båda värdena med."""
        xs, ys = [], []
        for el in self._element:
            ξ = np.linspace(0, el["Le"], punkter_per_element)
            ξ = np.unique(np.concatenate([ξ, self._kritiska_punkter(el, storhet)]))
            xs.append(el["x0"] + ξ)
            ys.append(self._värde(el, ξ, storhet))
        return np.concatenate(xs), np.concatenate(ys)

    def extremvärden(self, storhet):
        """(x, största värde) och (x, minsta värde) för N, V, M eller w.

        Värdena är exakta: de tas i elementens ändar och där derivatan är noll."""
        kandidater = []
        for el in self._element:
            ξ = self._kritiska_punkter(el, storhet)
            kandidater += zip(el["x0"] + ξ, self._värde(el, ξ, storhet))
        x_max, y_max = max(kandidater, key=lambda k: k[1])
        x_min, y_min = min(kandidater, key=lambda k: k[1])
        return (float(x_max), float(y_max)), (float(x_min), float(y_min))

    def skriv(self):
        """Skriv ut statisk obestämdhet, reaktioner och extremvärden."""
        if self.grad == 0:
            print("Balken är statiskt bestämd.")
        else:
            print(f"Balken är {self.grad} gång{'er' if self.grad > 1 else ''} statiskt obestämd.")
        print("\nStödreaktioner (V uppåt, H åt höger, M moturs):")
        for x, r in self.reaktioner.items():
            delar = [f"{k} = {v:.4g}" for k, v in r.items() if abs(v) > 1e-9 * (1 + abs(v))]
            print(f"  x = {x:g}: " + (", ".join(delar) if delar else "0"))
        print()
        for storhet, namn in (("N", "Normalkraft"), ("V", "Tvärkraft"), ("M", "Böjmoment"), ("w", "Nedböjning")):
            (x_max, y_max), (x_min, y_min) = self.extremvärden(storhet)
            skala = max(abs(y_max), abs(y_min))
            if storhet == "N" and skala < 1e-12:
                continue
            # Avrundningsrester nära noll skrivs som 0
            y_max, y_min = (0.0 if abs(y) < 1e-9 * skala else y for y in (y_max, y_min))
            print(f"{namn}: max {y_max:.4g} vid x = {x_max:.4g}, min {y_min:.4g} vid x = {x_min:.4g}")
        if not self.balk.EI_angivet:
            print("\nEI är inte angivet, så nedböjningen är räknad med EI = 1.")

    def rita(self, dragen_sida=False):
        """Rita balken, N-, V-, M-diagram och nedböjning.

        Med dragen_sida=True ritas positivt moment nedåt, alltså på den dragna sidan."""
        import matplotlib.pyplot as plt

        x_N, y_N = self.kurva("N")
        med_N = np.max(np.abs(y_N)) > 1e-12
        diagram = ([("N", "N(x)", x_N, y_N)] if med_N else []) + [
            ("V", "V(x)", *self.kurva("V")),
            ("M", "M(x)", *self.kurva("M")),
            ("w", "w(x), nedåt", *self.kurva("w")),
        ]
        fig, axlar = plt.subplots(len(diagram) + 1, 1, sharex=True,
                                  figsize=(8, 1.8 * (len(diagram) + 1) + 1))
        self._rita_balk(axlar[0])
        for ax, (storhet, titel, x, y) in zip(axlar[1:], diagram):
            ax.plot(x, y, color="C0")
            ax.fill_between(x, y, alpha=0.25, color="C0")
            ax.axhline(0, color="black", linewidth=0.8)
            ax.set_ylabel(titel)
            ax.grid(True, alpha=0.3)
            if storhet == "w" or (storhet == "M" and dragen_sida):
                ax.invert_yaxis()
            (x_max, y_max), (x_min, y_min) = self.extremvärden(storhet)
            for xe, ye in ((x_max, y_max), (x_min, y_min)):
                if abs(ye) > 1e-9 * (1 + np.max(np.abs(y))):
                    ax.annotate(f"{ye:.3g}", (xe, ye), textcoords="offset points",
                                xytext=(0, 4), ha="center", fontsize=8)
        axlar[-1].set_xlabel("x")
        fig.tight_layout()
        return fig

    def _rita_balk(self, ax):
        b = self.balk
        ax.plot([0, b.L], [0, 0], color="black", linewidth=3)
        for x, typ in b._stöd.items():
            u, w, θ = _STÖDTYPER[typ]
            if θ:
                ax.plot([x, x], [-0.5, 0.5], color="black", linewidth=4)
            else:
                ax.plot(x, -0.25, marker="^", markersize=12, color="black" if u else "gray")
        for x in b._leder:
            ax.plot(x, 0, marker="o", markersize=8, markerfacecolor="white", color="black")
        for x, P, H in b._punktlaster:
            if P:
                ax.annotate("", (x, 0.05 if P > 0 else -0.05), (x, 0.8 if P > 0 else -0.8),
                            arrowprops={"arrowstyle": "->", "color": "C3"})
        for x1, x2, q1, q2 in b._utbredda:
            q_max = max(abs(q) for _, _, *qs in b._utbredda for q in qs) or 1
            ax.fill_between([x1, x2], [0.1, 0.1], [0.1 + 0.5 * q1 / q_max, 0.1 + 0.5 * q2 / q_max],
                            color="C3", alpha=0.3)
        ax.set_ylim(-1, 1)
        ax.set_yticks([])
        ax.set_title("Balk och laster")
