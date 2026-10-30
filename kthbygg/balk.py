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

_TITLAR = {"N": "N(x)", "V": "V(x)", "M": "M(x)", "w": "w(x)"}


def _diagramfaktor(storhet, langdenhet):
    if storhet != "w":
        return 1.
    enheter = {"m": 1000., "cm": 10., "mm": 1.}
    if langdenhet not in enheter:
        raise ValueError("För w i mm måste langdenhet vara m, cm eller mm")
    return enheter[langdenhet]


def _axeltitel(storhet, kraftenhet, langdenhet):
    enheter = {"N": kraftenhet, "V": kraftenhet, "M": kraftenhet + langdenhet, "w": "mm"}
    titel = _TITLAR[storhet]
    return f"{titel} [{enheter[storhet]}]" if storhet in enheter else titel


# Fasta färger: normalkraft grön, tvärkraft blå, moment röd, nedböjning grå
_FÄRGER = {"N": "#2ca02c", "V": "#1f77b4", "M": "#d62728", "w": "#7f7f7f"}

# Diagram som streckas med lodräta linjer
_STRECKADE = ("N", "V", "M")


def _rgba(hexfärg, alfa):
    r, g, b = (int(hexfärg[i:i + 2], 16) for i in (1, 3, 5))
    return f"rgba({r}, {g}, {b}, {alfa})"


def _mörkare(hexfärg, faktor=0.65):
    r, g, b = (int(int(hexfärg[i:i + 2], 16) * faktor) for i in (1, 3, 5))
    return f"#{r:02x}{g:02x}{b:02x}"


def _sluten_kontur(x, y):
    # Diagrammets kontur, stängd ner till nollinjen i båda ändar
    return np.concatenate([[x[0]], x, [x[-1]]]), np.concatenate([[0.0], y, [0.0]])


def _lös_böjning_precist(element, fjädrar, dof_w, dof_θ, f, fria):
    # Korta element kan ge katastrofal subtraktion även efter diagonalskalning.
    # Bygg därför om styvheten med hög precision, inte från den avrundade K.
    import mpmath as mp

    with mp.workdps(80):
        K = mp.matrix(len(f))
        last = mp.matrix([float(v) for v in f])
        matriser = []
        for el in element:
            L, EI = mp.mpf(float(el["Le"])), mp.mpf(float(el["EI"]))
            ke = EI / L**3 * mp.matrix([
                [12, 6*L, -12, 6*L],
                [6*L, 4*L**2, -6*L, 2*L**2],
                [-12, -6*L, 12, -6*L],
                [6*L, 2*L**2, -6*L, 4*L**2]])
            matriser.append(ke)
            for a, i in enumerate(el["dofs"]):
                for b, j in enumerate(el["dofs"]):
                    K[i, j] += ke[a, b]
        for i, (_, ky, kr) in fjädrar.items():
            K[dof_w[i], dof_w[i]] += float(ky)
            K[dof_θ[i], dof_θ[i]] += float(kr)
        A = mp.matrix([[K[i, j] for j in fria] for i in fria])
        lösning = mp.lu_solve(A, mp.matrix([last[i] for i in fria]))
        d = mp.matrix(len(f), 1)
        for i, värde in zip(fria, lösning):
            d[i] = värde
        R = K*d - last
        krafter = []
        for el, ke in zip(element, matriser):
            de = mp.matrix([d[i] for i in el["dofs"]])
            fe = mp.matrix([float(v) for v in el["fe"]])
            krafter.append(np.array([float(v) for v in ke*de - fe]))
        return np.array([float(v) for v in d]), np.array([float(v) for v in R]), krafter


class Balk:
    def __init__(self, L, EI=None, EA=None):
        if not np.isfinite(L) or L <= 0:
            raise ValueError(f"Balklängden måste vara positiv (du angav L = {L})")
        self.L = float(L)
        self.EI_angivet = EI is not None
        self.EI = float(EI) if EI is not None else 1.0
        self.EA = float(EA) if EA is not None else 1.0
        if not np.all(np.isfinite([self.EI, self.EA])) or min(self.EI, self.EA) <= 0:
            raise ValueError("EI och EA måste vara positiva och ändliga")
        self._stöd = {}
        self._leder = []
        self._punktlaster = []
        self._vinkellaster = {}
        self._punktmoment = []
        self._utbredda = []
        self._delar = []
        self._temperaturer = []
        self._fjädrar = {}

    def sektion(self, x1, x2, *, EI=None, EA=None):
        # Styvhet inom intervallet; överlappande definitioner avvisas.
        x1, x2 = self._x(x1, "Delens början"), self._x(x2, "Delens slut")
        if x2 <= x1 or any(x1 < b and x2 > a for a, b, _, _ in self._delar):
            raise ValueError("Delar måste ha positiv längd och får inte överlappa")
        ei, ea = self.EI if EI is None else float(EI), self.EA if EA is None else float(EA)
        if not np.all(np.isfinite([ei, ea])) or min(ei, ea) <= 0:
            raise ValueError("EI och EA måste vara positiva och ändliga")
        self._delar.append((x1, x2, ei, ea))
        return self

    def fjäderstöd(self, x, *, kx=0, ky=0, kr=0):
        x = self._x(x, "Fjädern")
        k = np.array([kx, ky, kr], dtype=float)
        if not np.all(np.isfinite(k)) or np.any(k < 0) or not np.any(k > 0):
            raise ValueError("Fjäderstyvheter ska vara ändliga och icke-negativa, minst en positiv")
        self._fjädrar[x] = self._fjädrar.get(x, np.zeros(3)) + k
        return self

    def temperatur(self, delta_T=0, *, alfa=12e-6, gradient=0, x1=0, x2=None):
        # gradient = (T_undersida - T_översida) / höjd, i grader per längdenhet.
        x1, x2 = self._x(x1, "Temperaturens början"), self._x(self.L if x2 is None else x2, "Temperaturens slut")
        if x2 <= x1 or not np.all(np.isfinite([delta_T, alfa, gradient])):
            raise ValueError("Temperaturlast kräver positiv längd och ändliga värden")
        self._temperaturer.append((x1, x2, alfa * delta_T, alfa * gradient))
        return self

    # Modellritning utan att först behöva lösa balken.
    def rita_modell(self, stil="teknisk", *, deformerad=False, skala=None, **kwargs):
        if deformerad:
            return self.lös().rita_deformerad(skala=skala, stil=stil, **kwargs)
        from .balkstil import rita_modell
        return rita_modell(self, stil, **kwargs)

    def _x(self, x, vad):
        x = float(x)
        if not np.isfinite(x) or not 0 <= x <= self.L:
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

    def punktlast(self, x, P=0.0, H=0.0, *, F=None, vinkel=0):
        """Punktlast P (positiv nedåt) och valfri horisontell last H (positiv åt höger)."""
        x = self._x(x, "Punktlasten")
        P, H = float(P), float(H)
        if not np.all(np.isfinite([P, H])):
            raise ValueError("Punktlastens P och H måste vara ändliga")
        if F is not None:
            if P or H or not np.all(np.isfinite([F, vinkel])) or F < 0:
                raise ValueError("Ange F >= 0 och en ändlig vinkel, utan P/H")
            alfa = np.deg2rad(vinkel)
            H, P = F*np.cos(alfa), -F*np.sin(alfa)
            self._vinkellaster[len(self._punktlaster)] = (float(F), float(vinkel))
        self._punktlaster.append((x, float(P), float(H)))
        return self

    def moment(self, x, M0):
        """Punktmoment M0, positivt moturs."""
        M0 = float(M0)
        if not np.isfinite(M0):
            raise ValueError("Punktmomentet M0 måste vara ändligt")
        self._punktmoment.append((self._x(x, "Punktmomentet"), M0))
        return self

    def utbredd_last(self, q, x1=0.0, x2=None, q2=None):
        """Utbredd last q (positiv nedåt) från x1 till x2.

        Anges q2 varierar lasten linjärt från q vid x1 till q2 vid x2."""
        x1 = self._x(x1, "Lastens början")
        x2 = self._x(self.L if x2 is None else x2, "Lastens slut")
        if x2 <= x1:
            raise ValueError(f"Den utbredda lasten måste ha x1 < x2 (du angav x1 = {x1}, x2 = {x2})")
        q, q2 = float(q), float(q if q2 is None else q2)
        if not np.all(np.isfinite([q, q2])):
            raise ValueError("Lastintensiteterna q och q2 måste vara ändliga")
        self._utbredda.append((x1, x2, q, q2))
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
        if not self._stöd and not self._fjädrar:
            raise ValueError("Balken saknar stöd")
        tol = 1e-9 * self.L

        # Noder i alla punkter där något händer
        punkter = {0.0, self.L, *self._stöd, *self._leder}
        punkter.update(self._fjädrar)
        for a, b, _, _ in self._delar + self._temperaturer:
            punkter.update([a, b])
        punkter |= {x for x, P, H in self._punktlaster if P or H}
        punkter |= {x for x, M in self._punktmoment if M}
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
        fjädrar = {}
        for x, fjäder in self._fjädrar.items():
            i = nod(x)
            fjädrar[i] = fjädrar.get(i, np.zeros(3)) + fjäder
        leder = {nod(x) for x in self._leder}
        for i in leder:
            if i in fjädrar and fjädrar[i][2]:
                raise ValueError("Rotationsfjäder i inre led kräver en angiven sida och stöds inte")
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
            EI, EA = self.EI, self.EA
            for a, b, ei, ea in self._delar:
                if a <= x0 + tol and noder[e + 1] <= b + tol:
                    EI, EA = ei, ea
            eps, kappa = np.zeros(2)
            for a, b, ep, kap in self._temperaturer:
                if a <= x0 + tol and noder[e + 1] <= b + tol:
                    eps += ep
                    kappa += kap
            dofs = [dof_w[e], dof_θh[e], dof_w[e + 1], dof_θv[e + 1]]
            ke = EI / Le**3 * np.array([
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
            fe += np.array([0, -EI * kappa, 0, EI * kappa])
            K[np.ix_(dofs, dofs)] += ke
            f[dofs] += fe
            element.append({"x0": x0, "Le": Le, "dofs": dofs, "ke": ke, "fe": fe, "p1": p1, "p2": p2})
            element[-1].update(EI=EI, EA=EA, eps=eps)

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

        for i, (_, ky, kr) in fjädrar.items():
            K[dof_w[i], dof_w[i]] += ky
            K[dof_θv[i], dof_θv[i]] += kr
        # Mekanismer bestäms av stöd och leder, oberoende av elementstyvheterna.
        # En rörelse utan böjenergi är styckvis linjär med lutningssprång i lederna.
        led_x = noder[sorted(leder)] / self.L
        villkor = []
        for i, x in enumerate(noder / self.L):
            mask = stöd_vid.get(i, (False, False, False))
            fj = fjädrar.get(i, np.zeros(3))
            if mask[1] or fj[1] > 0:
                villkor.append([1., x, *np.maximum(x - led_x, 0.)])
            if mask[2] or fj[2] > 0:
                villkor.append([0., 1., *(x > led_x).astype(float)])
        if not villkor or np.linalg.matrix_rank(np.asarray(villkor)) < 2 + len(leder):
            raise ValueError("Balken är en mekanism och kan inte bära lasten. Kontrollera stöd och leder.")
        Kff = K[np.ix_(fria, fria)]
        d = np.zeros(ndof)
        hög_precision = False
        if fria:
            skala = np.sqrt(np.diag(Kff))
            A = Kff / skala[:, None] / skala[None, :]
            hög_precision = np.linalg.cond(A) > 1e10
            if not hög_precision:
                d[fria] = np.linalg.solve(A, f[fria] / skala) / skala
        if hög_precision:
            d, R, ändkrafter = _lös_böjning_precist(element, fjädrar, dof_w, dof_θv, f, fria)
        else:
            R = K @ d - f

        for e, el in enumerate(element):
            F = ändkrafter[e] if hög_precision else el["ke"] @ d[el["dofs"]] - el["fe"]
            el["d"] = d[el["dofs"]]
            el["Fv1"], el["Fθ1"] = F[0], F[1]

        # Axialkraft löses separat, den är frikopplad från böjningen för en rak balk
        H_nod = np.zeros(n)
        for x, _, H in self._punktlaster:
            H_nod[nod(x)] += H
        u_låsta = [i for i, (u_låst, _, _) in stöd_vid.items() if u_låst]
        for e, el in enumerate(element):
            H_nod[e:e + 2] += el["EA"] * el["eps"] * np.array([-1, 1])
        u = np.zeros(n)
        R_u = np.zeros(n)
        if u_låsta or any(k[0] > 0 for k in fjädrar.values()):
            Ka = np.zeros((n, n))
            for e in range(n - 1):
                ka = element[e]["EA"] / element[e]["Le"]
                Ka[np.ix_([e, e + 1], [e, e + 1])] += ka * np.array([[1, -1], [-1, 1]])
            for i, (kx, _, _) in fjädrar.items():
                Ka[i, i] += kx
            u_fria = [i for i in range(n) if i not in u_låsta]
            if u_fria:
                u[u_fria] = np.linalg.solve(Ka[np.ix_(u_fria, u_fria)], H_nod[u_fria])
            R_u = Ka @ u - H_nod
        elif any(H != 0 for _, _, H in self._punktlaster):
            raise ValueError("Balken har horisontell last men inget stöd som tar horisontell kraft. "
                             "Använd 'led' eller 'fast' för minst ett stöd.")
        else:
            for e, el in enumerate(element):
                u[e + 1] = u[e] + el["eps"] * el["Le"]
        for e, el in enumerate(element):
            el["u"] = u[e:e + 2].copy()
            el["N"] = el["EA"] * ((u[e + 1] - u[e]) / el["Le"] - el["eps"])

        reaktioner = {}
        for i in sorted(stöd_vid):
            u_låst, w_låst, θ_låst = stöd_vid[i]
            reaktioner[float(noder[i])] = {
                "V": R[dof_w[i]] if w_låst else 0.0,
                "H": R_u[i] if u_låst else 0.0,
                "M": R[dof_θv[i]] if θ_låst else 0.0,
            }

        for i, (kx, ky, kr) in fjädrar.items():
            r = reaktioner.setdefault(float(noder[i]), {"V": 0., "H": 0., "M": 0.})
            r["H"] -= kx * u[i]
            r["V"] -= ky * d[dof_w[i]]
            r["M"] -= kr * d[dof_θv[i]]
        # Statiskt obestämd grad för böjning: låsta w och θ minus jämviktsekvationer och leder
        grad = len(låsta) - 2 - len(leder)
        grad += sum(int(ky > 0 and dof_w[i] not in låsta) + int(kr > 0 and dof_θv[i] not in låsta)
                    for i, (_, ky, kr) in fjädrar.items())
        # Axial jämvikt ger en ekvation; ytterligare axialstöd är redundanta.
        axialstöd = len(u_låsta) + sum(kx > 0 and i not in u_låsta
                                      for i, (kx, _, _) in fjädrar.items())
        grad += max(0, axialstöd - 1)
        resultat = Resultat(self, element, reaktioner, grad)
        resultat.förskjutningar = {float(x): {"u": u[i], "w": -d[dof_w[i]], "rotation": d[dof_θv[i]]} for i, x in enumerate(noder)}
        return resultat


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
        EI = el.get("EI", self.balk.EI)
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

    def _rita_deformation(self, ax, skala):
        from .deformation import rita_kurvor
        kurvor = []
        for el in self._element:
            x = np.linspace(0, el["Le"], 201)
            u0, u1 = el["u"]
            u = u0 + (u1-u0)*x/el["Le"]
            v = -self._värde(el, x, "w")
            bas = np.column_stack((el["x0"] + x, np.zeros_like(x)))
            kurvor.append((bas, np.column_stack((u, v))))
        return rita_kurvor(ax, kurvor, skala, self.balk.L, faktor=900/self.balk.L)

    def rita_deformerad(self, skala=None, *, stil="teknisk", ax=None, **kwargs):
        fig = self.balk.rita_modell(stil=stil, ax=ax, **kwargs)
        self._rita_deformation(fig.axes[0] if ax is None else ax, skala)
        return fig

    def rita(self, storheter=("N", "V", "M", "w"), dragen_sida=True, visa_balk=True, värden=True,
             *, kraftenhet="kN", langdenhet="m", färgat=False,
             måttfärg="#d62728", matt=True, deformerad=False, skala=None):
        """Rita balken och diagram för N, V, M och w.

        storheter    vilka diagram som ritas och i vilken ordning, t.ex. "NVM", "M"
                     eller ("V", "M"). Standard är alla fyra.
        dragen_sida  ritar positivt moment nedåt, alltså på den dragna sidan (standard: True).
        visa_balk    ritar balken överst med Balk.rita_modell().
        värden       skriver ut värdena i noderna och i extrempunkterna."""
        import matplotlib.pyplot as plt

        if isinstance(storheter, str):
            storheter = tuple(storheter)
        if not storheter:
            raise ValueError("Välj minst ett diagram: N, V, M eller w")
        okända = [s for s in storheter if s not in _TITLAR]
        if okända:
            raise ValueError(f"Okända diagram {okända}, välj bland N, V, M och w")

        if deformerad and not visa_balk:
            raise ValueError("deformerad=True kräver visa_balk=True")

        rader = len(storheter) + (1 if visa_balk else 0)
        # Modellritningen använder normaliserade koordinater; bara resultatens
        # axlar delar x-skala med varandra.
        fig, axlar = plt.subplots(rader, 1, squeeze=False,
                                  figsize=(8, 1.9 * len(storheter) + (3.3 if visa_balk else 0.8)),
                                  gridspec_kw={"height_ratios": ([1.6] if visa_balk else []) + [1]*len(storheter)})
        axlar = list(axlar[:, 0])
        modellax = None
        if visa_balk:
            modellax = axlar.pop(0)
            self.balk.rita_modell(ax=modellax, kraftenhet=kraftenhet,
                                 langdenhet=langdenhet, färgat=färgat,
                                 måttfärg=måttfärg, matt=matt)
            if deformerad:
                self._rita_deformation(modellax, skala)
        for ax, storhet in zip(axlar, storheter):
            if ax is not axlar[0]:
                ax.sharex(axlar[0])
            self._rita_diagram(ax, storhet, dragen_sida, värden, kraftenhet, langdenhet)
            if ax is not axlar[-1]:
                ax.tick_params(labelbottom=False)
        if modellax is not None:
            # Samma balkändar i modell och resultat, trots olika koordinatsystem.
            axlar[0].set_xlim(*(x*self.balk.L/900 for x in modellax.get_xlim()))
        axlar[-1].set_xlabel(f"x [{langdenhet}]")
        fig.tight_layout()
        if modellax is not None:
            position = modellax.get_position()
            for ax in axlar:
                ruta = ax.get_position()
                ax.set_position([position.x0, ruta.y0, position.width, ruta.height])
        from .balkstil import _forbered_visning
        return _forbered_visning(fig)

    def rita_N(self, **kwargs):
        """Rita normalkraftsdiagrammet. Tar samma argument som rita()."""
        return self.rita("N", **kwargs)

    def rita_V(self, **kwargs):
        """Rita tvärkraftsdiagrammet. Tar samma argument som rita()."""
        return self.rita("V", **kwargs)

    def rita_M(self, **kwargs):
        """Rita momentdiagrammet. Tar samma argument som rita()."""
        return self.rita("M", **kwargs)

    def rita_w(self, **kwargs):
        """Rita nedböjningen. Tar samma argument som rita()."""
        return self.rita("w", **kwargs)

    def rita_interaktiv(self, storheter=("N", "V", "M", "w"), dragen_sida=True, värden=True,
                        *, kraftenhet="kN", langdenhet="m"):
        """Interaktiva diagram med plotly. Håll muspekaren över diagrammen för att se
        N, V, M och w i samma x. Kräver plotly: python -m pip install plotly

        Argumenten fungerar som i rita(). Returnerar en plotly-figur; i Jupyter visas
        den om den står sist i cellen, annars med fig.show()."""
        try:
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
        except ImportError:
            raise ImportError("Interaktiva diagram kräver plotly. Installera med: python -m pip install plotly") from None

        if isinstance(storheter, str):
            storheter = tuple(storheter)
        if not storheter:
            raise ValueError("Välj minst ett diagram: N, V, M eller w")
        okända = [s for s in storheter if s not in _TITLAR]
        if okända:
            raise ValueError(f"Okända diagram {okända}, välj bland N, V, M och w")

        n = len(storheter)
        fig = make_subplots(rows=n, cols=1, shared_xaxes=True, vertical_spacing=0.06 / max(n - 1, 1) * 2)
        for rad, storhet in enumerate(storheter, start=1):
            x, y = self.kurva(storhet)
            faktor = _diagramfaktor(storhet, langdenhet)
            referens = np.max(np.abs(y)) or 1.0
            y = y * faktor
            nedåt = storhet == "w" or (storhet == "M" and dragen_sida)
            noll = self._är_noll(y)
            if noll:
                y = np.zeros_like(y)
                fig.add_annotation(text=f"{storhet} = 0 längs hela balken", showarrow=False,
                                   font={"color": "gray"}, xref="paper", x=0.5,
                                   yref=f"y{'' if rad == 1 else rad} domain", y=0.75)
                fig.update_yaxes(range=[-1, 1], tickvals=[0], row=rad, col=1)
            enhet = {"N": kraftenhet, "V": kraftenhet,
                     "M": kraftenhet + langdenhet, "w": "mm"}[storhet]
            # Skriv x i själva rutan också: äldre notebook-renderare kan ignorera
            # unifiedhovertitle även när Python-paketet stöder egenskapen.
            xrad = f"x = %{{x:.3f}} [{langdenhet}]<br>" if rad == 1 else ""
            kantfärg = _mörkare(_FÄRGER[storhet])
            fig.add_trace(go.Scatter(
                x=x, y=y, mode="lines", fill="tozeroy", name=storhet,
                line={"color": kantfärg, "width": 2.5}, fillcolor=_rgba(_FÄRGER[storhet], 0.25),
                hovertemplate=xrad + f"{storhet} = %{{y:.4g}} [{enhet}]<extra></extra>",
            ), row=rad, col=1)
            if storhet in _STRECKADE and not noll:
                # Snittkraftsdiagrammen streckas med lodräta linjer
                xs, ys = self._streckning(storhet)
                fig.add_trace(go.Scatter(
                    x=np.repeat(xs, 3), y=np.column_stack([np.zeros_like(ys), ys, np.full_like(ys, np.nan)]).ravel(),
                    mode="lines", line={"color": _FÄRGER[storhet], "width": 1},
                    hoverinfo="skip", showlegend=False, name=f"{storhet} streckning",
                ), row=rad, col=1)
            if not noll:
                # Lodräta kantsträck i ändarna, så att diagrammet är slutet mot nollinjen
                fig.add_trace(go.Scatter(
                    x=[x[0], x[0], None, x[-1], x[-1]], y=[0, y[0], None, y[-1], 0],
                    mode="lines", line={"color": kantfärg, "width": 2.5},
                    hoverinfo="skip", showlegend=False, name=f"{storhet} kant",
                ), row=rad, col=1)
            if värden and not noll:
                etiketter = self._etikettpunkter(storhet, referens)
                if etiketter:
                    ex, ey, eha = zip(*etiketter)
                    ey = np.asarray(ey) * faktor
                    sida = {"left": " right", "right": " left", "center": " center"}
                    fig.add_trace(go.Scatter(
                        x=ex, y=ey, mode="markers+text", text=[f"{v:.3g}" for v in ey],
                        textposition=[("top" if (v >= 0) != nedåt else "bottom") + sida[h] for v, h in zip(ey, eha)],
                        marker={"size": 5, "color": _FÄRGER[storhet]}, textfont={"size": 10},
                        cliponaxis=False, hoverinfo="skip", showlegend=False,
                    ), row=rad, col=1)
            fig.add_shape(type="line", x0=0, x1=self.balk.L, y0=0, y1=0,
                          line={"color": "black", "width": 2}, layer="above", row=rad, col=1)
            fig.update_yaxes(title_text=_axeltitel(storhet, kraftenhet, langdenhet), zeroline=True, zerolinecolor="black",
                             row=rad, col=1)
            if nedåt:
                fig.update_yaxes(autorange="reversed", row=rad, col=1)

        # Alla kurvor läggs på den nedersta x-axeln, så att en enda hover-ruta visar
        # värdena från samtliga diagram i samma x
        fig.update_traces(xaxis=f"x{n}" if n > 1 else "x")
        fig.update_xaxes(showspikes=True, spikemode="across", spikesnap="cursor",
                         spikethickness=1, spikedash="dot", spikecolor="gray", hoverformat=".3f",
                         unifiedhovertitle={"text": f"x = %{{x:.3f}} [{langdenhet}]"})
        fig.update_xaxes(title_text=f"x [{langdenhet}]", row=n, col=1)
        fig.update_layout(hovermode="x unified", hoversubplots="axis", showlegend=False, height=200 * n + 80,
                          margin={"l": 70, "r": 20, "t": 30, "b": 50}, template="plotly_white")
        return fig

    def _rita_diagram(self, ax, storhet, dragen_sida, värden, kraftenhet, langdenhet):
        x, y = self.kurva(storhet)
        faktor = _diagramfaktor(storhet, langdenhet)
        referens = np.max(np.abs(y)) or 1.0
        y = y * faktor
        ax.axhline(0, color="black", linewidth=0.8)
        ax.plot([0, self.balk.L], [0, 0], color="black", linewidth=1.5,
                solid_capstyle="butt", zorder=4)
        ax.set_ylabel(_axeltitel(storhet, kraftenhet, langdenhet))
        ax.grid(True, alpha=0.3)
        if self._är_noll(y):
            ax.text(0.5, 0.72, f"{storhet} = 0 längs hela balken", transform=ax.transAxes,
                    ha="center", va="center", color="gray")
            ax.set_ylim(-1, 1)
            ax.set_yticks([0])
            return
        ax.fill_between(x, y, alpha=0.25, color=_FÄRGER[storhet], linewidth=0)
        if storhet in _STRECKADE:
            # Snittkraftsdiagrammen streckas med lodräta linjer
            xs, ys = self._streckning(storhet)
            ax.vlines(xs, 0, ys, color=_FÄRGER[storhet], linewidth=0.8)
        ax.plot(*_sluten_kontur(x, y), color=_mörkare(_FÄRGER[storhet]), linewidth=2,
                solid_capstyle="butt", solid_joinstyle="miter")
        ax.margins(y=0.3)
        nedåt = storhet == "w" or (storhet == "M" and dragen_sida)
        if nedåt:
            ax.invert_yaxis()
        if not värden:
            return

        for xi, yi, ha in self._etikettpunkter(storhet, referens):
            yi *= faktor
            uppåt = (yi >= 0) != nedåt
            ax.annotate(f"{yi:.3g}", (xi, yi), textcoords="offset points",
                        xytext=(0, 4 if uppåt else -11), ha=ha, fontsize=8)

    def _streckning(self, storhet, antal=30):
        # Jämnt fördelade lodräta streck mellan kurvan och nollinjen, ändarna utelämnas
        # eftersom kantsträcken redan ritar dem
        xs = np.linspace(0, self.balk.L, antal + 1)[1:-1]
        return xs, self._i_punkt(xs, storhet, "höger")

    def _är_noll(self, y):
        # Avrundningsrester från lösningen räknas som noll
        return np.max(np.abs(y)) < 1e-9

    def _etikettpunkter(self, storhet, skala):
        # Värden som är värda att skriva ut: balkens ändar, språng (båda sidor),
        # knäckar, extrempunkter i noder och extrempunkter inuti element
        el_lista = self._element
        punkter = []

        def lägg_till(x, y, ha):
            if abs(y) > 1e-6 * skala:
                punkter.append((float(x), float(y), ha))

        for e, el in enumerate(el_lista):
            p = self._polynom(el, storhet)
            dp = p.deriv()
            Le = el["Le"]
            for ξ in self._kritiska_punkter(el, storhet)[1:-1]:
                lägg_till(el["x0"] + ξ, p(ξ), "center")
            if e == 0:
                lägg_till(el["x0"], p(0.0), "left")
            if e == len(el_lista) - 1:
                lägg_till(el["x0"] + Le, p(Le), "right")
                continue
            nästa = el_lista[e + 1]
            p2 = self._polynom(nästa, storhet)
            x_nod = nästa["x0"]
            y_v, y_h = p(Le), p2(0.0)
            d_v, d_h = dp(Le), p2.deriv()(0.0)
            d_skala = max(abs(d_v), abs(d_h), 1e-300)
            if abs(y_v - y_h) > 1e-6 * skala:
                lägg_till(x_nod, y_v, "right")
                lägg_till(x_nod, y_h, "left")
            elif abs(d_v - d_h) > 1e-6 * d_skala or d_v * d_h < 0:
                lägg_till(x_nod, y_v, "center")

        # Etiketter som ligger nära varandra skjuts isär åt var sitt håll
        punkter.sort(key=lambda p: p[0])
        for i in range(len(punkter) - 1):
            (x1, y1, ha1), (x2, y2, ha2) = punkter[i], punkter[i + 1]
            if 0 < x2 - x1 < 0.06 * self.balk.L:
                punkter[i] = (x1, y1, "right")
                punkter[i + 1] = (x2, y2, "left")
        return punkter
