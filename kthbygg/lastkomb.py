
# Säkerhetsklass
def γ_d(säkerhetsklass):
    if isinstance(säkerhetsklass, (bool, np.bool_)) or not np.isscalar(säkerhetsklass):
        raise ValueError("säkerhetsklass ska vara 1, 2 eller 3.")
    if säkerhetsklass == 1:
        val = 0.83
    elif säkerhetsklass == 2:
        val = 0.91
    elif säkerhetsklass == 3:
        val = 1.0
    else:
        raise ValueError("säkerhetsklass ska vara 1, 2 eller 3.")
    return val


import numpy as np


# Enumerera 6.10a/b med samhörande lasteffekter (t.ex. [M, N]).
# G: effekt, gamma_sup, gamma_inf, xi. Q: effekt, gamma, psi_0, grupp.
# Samma grupp betyder alternativa laster; None betyder oberoende last.
# Faktorer anges uttryckligen av anroparen. Ingen extra gamma_d appliceras.
def lastkomb_610_fall(G, Q, *, variabel_i_610a=True):
    from itertools import product

    if not isinstance(variabel_i_610a, (bool, np.bool_)):
        raise ValueError("variabel_i_610a ska vara True eller False.")
    g, q = list(G), list(Q)
    if not g:
        raise ValueError("Ange minst en permanent last.")
    effekter = [_värden(last["effekt"], "effekt") for last in g + q]
    if not effekter[0].size or any(e.shape != effekter[0].shape for e in effekter):
        raise ValueError("Alla effektvektorer ska ha samma positiva längd.")

    def faktor(last, namn, maxvärde=None):
        v = _skalär(last[namn], namn)
        if v < 0 or (maxvärde is not None and v > maxvärde):
            raise ValueError(f"Ogiltig faktor: {namn}.")
        return v

    gs = [faktor(last, "gamma_sup") for last in g]
    gi = [faktor(last, "gamma_inf") for last in g]
    xi = [faktor(last, "xi", 1) for last in g]
    if any(a > b for a, b in zip(gi, gs)):
        raise ValueError("gamma_inf får inte överstiga gamma_sup.")
    gq = [faktor(last, "gamma") for last in q]
    psi = [faktor(last, "psi_0", 1) for last in q]
    grupper = {}
    for i, last in enumerate(q):
        grupp = last.get("grupp")
        nyckel = ("oberoende", i) if grupp is None else ("grupp", grupp)
        grupper.setdefault(nyckel, [None]).append(i)
    matris = np.stack(effekter)
    resultat = []
    for val in product(*grupper.values()):
        aktiva = [i for i in val if i is not None]
        for ekvation in ("6.10a", "6.10b"):
            huvudlaster = aktiva if ekvation == "6.10b" and aktiva else [None]
            for huvud in huvudlaster:
                alternativ = [sorted(set((lo, hi if ekvation == "6.10a" else x * hi)))
                              for lo, hi, x in zip(gi, gs, xi)]
                for gf in product(*alternativ):
                    qf = np.zeros(len(q))
                    if ekvation == "6.10b" or variabel_i_610a:
                        for i in aktiva:
                            qf[i] = gq[i] * (1 if i == huvud else psi[i])
                    faktorer = np.r_[gf, qf]
                    effekt = faktorer @ matris
                    if not np.all(np.isfinite(effekt)):
                        raise ValueError("Lastkombinationen ger ett icke-ändligt resultat.")
                    resultat.append(dict(kombination=ekvation, huvudlast=huvud,
                                         faktorer=faktorer.tolist(), effekt=effekt.tolist()))
    return resultat


def _värden(värden, namn):
    try:
        a = np.atleast_1d(np.asarray(värden, dtype=float))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{namn} ska innehålla ändliga tal.") from exc
    if a.ndim != 1 or not np.all(np.isfinite(a)):
        raise ValueError(f"{namn} ska vara ett tal eller en lista av ändliga tal.")
    return a


# STR/GEO utan förspänning, enligt EKS 11 tabell B-3.
# https://www.boverket.se/globalassets/publikationer/dokument/2019/eks-112.pdf
# G och Q: signerade lasteffekter i samma enhet, positivt är ogynnsamt.
# Sök maximum; vänd tecknen för att undersöka motsatt riktning.
# Q ska avse oberoende, samtidigt möjliga laster. psi_0 följer ordningen i Q.
# Ett skalärt psi_0 används för alla Q. Gynnsamma Q utelämnas.
# variabel_i_610a=True ger ursprunglig 6.10a med reducerade variabla laster,
# i stället för EKS 11:s förenkling med endast permanenta laster.
def lastkomb(G, Q=(), psi_0=(), säkerhetsklass=3, *, variabel_i_610a=False,
             kombination="6.10", psi_1=(), psi_2=(), P=0, A_d=None, A_Ed=None,
             olycka_huvudlast=None):
    if kombination != "6.10":
        if säkerhetsklass != 3 or variabel_i_610a:
            raise ValueError("säkerhetsklass och variabel_i_610a används bara för 6.10.")
        return _kombination(kombination, G, Q, psi_0, psi_1, psi_2, P,
                            A_d, A_Ed, olycka_huvudlast)
    if P != 0 or A_d is not None or A_Ed is not None or olycka_huvudlast is not None:
        raise ValueError("P och olycks-/jordbävningsparametrar stöds inte för 6.10.")
    gd = γ_d(säkerhetsklass)
    g = _värden(G, "G")
    q = _värden(Q, "Q")
    psi = _värden(psi_0, "psi_0")
    if not isinstance(variabel_i_610a, (bool, np.bool_)):
        raise ValueError("variabel_i_610a ska vara True eller False.")
    if np.any((psi < 0) | (psi > 1)):
        raise ValueError("psi_0 ska ligga mellan 0 och 1.")
    if psi.size == 1:
        psi = np.full(q.size, psi.item())
    if psi.size != q.size:
        raise ValueError("Ange ett psi_0 för varje variabel last.")
    g_pos = float(np.maximum(g, 0).sum())
    g_neg = float(np.minimum(g, 0).sum())
    q = np.maximum(q, 0)
    samverkande = float(np.dot(psi, q))
    a = gd * 1.35 * g_pos + g_neg
    if variabel_i_610a:
        a += gd * 1.5 * samverkande
    b_g = gd * 0.89 * 1.35 * g_pos + g_neg
    b = [float(b_g + gd * 1.5 * (samverkande + (1 - p) * last))
         for last, p in zip(q, psi)]
    if not b:
        b = [b_g]
    index = int(np.argmax(b))
    b_max = b[index]
    return {
        "6.10a": float(a), "6.10b": b_max, "6.10b_alla": b,
        "dimensionerande": max(float(a), b_max),
        "kombination": "6.10a" if a >= b_max else "6.10b",
        # Nollbaserat index i Q; ingen huvudlast när 6.10a styr.
        "huvudlast": index if b_max > a and q.size else None,
    }


# Samma indata som lastkomb. Enheten är en etikett, ingen omräkning görs.
# Skriver ut en gång och returnerar None, även i en notebook.
def skriv_formler(G, Q=(), psi_0=(), säkerhetsklass=3, *,
                  variabel_i_610a=False, enhet="", decimaler=3,
                  kombination="6.10", psi_1=(), psi_2=(), P=0, A_d=None,
                  A_Ed=None, olycka_huvudlast=None):
    if isinstance(decimaler, bool) or not isinstance(decimaler, int) or decimaler < 0:
        raise ValueError("decimaler ska vara ett icke-negativt heltal.")
    r = lastkomb(G, Q, psi_0, säkerhetsklass,
                 variabel_i_610a=variabel_i_610a, kombination=kombination,
                 psi_1=psi_1, psi_2=psi_2, P=P, A_d=A_d, A_Ed=A_Ed,
                 olycka_huvudlast=olycka_huvudlast)
    if kombination != "6.10":
        suffix = f" [{enhet}]" if enhet else ""
        rader = [f"{r['kombination']}: {r['formel']}",
                 "Signerade lasteffekter i samma enhet; gynnsamma Q utelämnas vid sökt maximum."]
        for fall in r["lastfall"]:
            namn = f"Q_{fall['huvudlast'] + 1} huvudlast" if fall['huvudlast'] is not None else "utan huvudlast"
            rader.append(f"{namn}: E_d = {' + '.join(fall['termer'])}"
                         f" = {fall['värde']:.{decimaler}f}{suffix}")
        rader.append(f"Dimensionerande E_d = {r['dimensionerande']:.{decimaler}f}{suffix}")
        _skriv_text("\n".join(rader))
        return
    g = _värden(G, "G")
    q = _värden(Q, "Q")
    psi = _värden(psi_0, "psi_0")
    if psi.size == 1:
        psi = np.full(q.size, psi.item())
    gd = γ_d(säkerhetsklass)
    suffix = f" [{enhet}]" if enhet else ""

    def tal(x):
        return f"({x:g})" if x < 0 else f"{x:g}"

    def permanent(reducerad=False):
        faktor = f"{gd:g} · " + ("0.89 · " if reducerad else "") + "1.35"
        return [f"{faktor} · {tal(x)}" if x >= 0 else f"1.00 · {tal(x)}"
                for x in g]

    def variabel(huvudlast=None):
        termer = []
        for i, (x, p) in enumerate(zip(q, psi)):
            if x < 0:
                termer.append(f"0 · {tal(x)}")
            elif i == huvudlast:
                termer.append(f"{gd:g} · 1.5 · {tal(x)}")
            else:
                termer.append(f"{gd:g} · 1.5 · {p:g} · {tal(x)}")
        return termer

    def rad(namn, termer, värde):
        uttryck = " + ".join(termer) or "0"
        return f"{namn} = {uttryck} = {värde:.{decimaler}f}{suffix}"

    rader = [f"Säkerhetsklass {säkerhetsklass}: γ_d = {gd:g}",
             "G+ = ogynnsamma permanenta effekter; G− = gynnsamma permanenta effekter.",
             "Q+ = max(Q, 0); gynnsamma variabla effekter utelämnas.",
             "Alla indata ska ha samma enhet. Q numreras från 1.", "",
             "6.10a: E_d,a = γ_d · 1.35 · ΣG+ + 1.00 · ΣG−"
             + (" + γ_d · 1.5 · Σ(ψ_0,i · Q_i+)" if variabel_i_610a else " (EKS 11)")]
    rader.append(rad("E_d,a", permanent() + (variabel() if variabel_i_610a else []),
                     r["6.10a"]))
    rader.extend(["", "6.10b: E_d,b,j = γ_d · 0.89 · 1.35 · ΣG+ + 1.00 · ΣG−"
                  " + γ_d · 1.5 · (Q_j+ + Σ(i≠j)(ψ_0,i · Q_i+))"])
    for i, värde in enumerate(r["6.10b_alla"]):
        namn = f"E_d,b (Q_{i + 1} huvudlast)" if q.size else "E_d,b (ingen variabel last)"
        rader.append(rad(namn, permanent(True) + variabel(i), värde))
    styrande = r["kombination"]
    if r["huvudlast"] is not None:
        styrande += f", Q_{r['huvudlast'] + 1} huvudlast"
    rader.extend(["", f"E_d = max(E_d,a, E_d,b,j) = {r['dimensionerande']:.{decimaler}f}"
                  f"{suffix} — dimensionerande: {styrande}"])
    _skriv_text("\n".join(rader))


def _skriv_text(text):
    # Äldre Windows-terminaler kan sakna stöd för grekiska tecken.
    import sys
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        text.encode(encoding)
    except UnicodeEncodeError:
        for symbol, ersättning in (("γ", "gamma"), ("ψ", "psi"), ("Σ", "sum"),
                                   ("−", "-"), ("≠", "!="), ("≤", "<="), ("·", "*"), ("—", "-")):
            text = text.replace(symbol, ersättning)
        text = text.encode(encoding, errors="replace").decode(encoding)
    print(text)


def _skalär(x, namn):
    a = _värden(x, namn)
    if a.size != 1 or not np.isscalar(x):
        raise ValueError(f"{namn} ska vara ett ändligt tal.")
    return float(a[0])


def _psi(x, antal, namn):
    a = _värden(x, namn)
    if np.any((a < 0) | (a > 1)):
        raise ValueError(f"{namn} ska ligga mellan 0 och 1.")
    if a.size == 1:
        a = np.full(antal, a.item())
    if a.size != antal:
        raise ValueError(f"Ange {namn} för varje variabel last.")
    return a


# EN 1990:2002+A1, 6.11b, 6.12b och 6.14b–6.16b.
# https://eurocodes.jrc.ec.europa.eu/sites/default/files/2021-12/Balkans_report_online_f.pdf
# Linjär summering av signerade lasteffekter, samma antaganden om Q som i 6.10.
# P är relevant representativ förspänningseffekt; A_d och A_Ed är redan
# dimensionerande effekter. Ingen ytterligare gamma_d eller gamma_Q används.
# Val av psi-värden och olyckans huvudlastfaktor görs av anroparen.
def _kombination(nummer, G, Q, psi_0, psi_1, psi_2, P, A_d, A_Ed, olycka_huvudlast):
    nummer = str(nummer).removesuffix("b")
    if nummer not in ("6.11", "6.12", "6.14", "6.15", "6.16"):
        raise ValueError("Välj 6.10, 6.11, 6.12, 6.14, 6.15 eller 6.16. För 6.13: kontroll_613(E_d, C_d).")
    g = _värden(G, "G")
    q = _värden(Q, "Q")
    p = _skalär(P, "P")
    if A_d is not None and nummer != "6.11":
        raise ValueError("A_d används endast i 6.11.")
    if A_Ed is not None and nummer != "6.12":
        raise ValueError("A_Ed används endast i 6.12.")
    if olycka_huvudlast is not None and nummer != "6.11":
        raise ValueError("olycka_huvudlast används endast i 6.11.")
    extra = 0.0
    huvud = None
    if nummer == "6.14":
        följd = _psi(psi_0, q.size, "psi_0")
        huvud = np.ones(q.size)
        formel = "E_d = ΣG + P + Q_j + Σ(i≠j)(ψ_0,i · Q_i)"
    else:
        följd = _psi(psi_2, q.size, "psi_2")
        if nummer == "6.15":
            huvud = _psi(psi_1, q.size, "psi_1")
            formel = "E_d = ΣG + P + ψ_1,j · Q_j + Σ(i≠j)(ψ_2,i · Q_i)"
        elif nummer == "6.11":
            extra = _skalär(A_d, "A_d")
            if olycka_huvudlast not in ("psi_1", "psi_2"):
                raise ValueError("Välj olycka_huvudlast='psi_1' eller 'psi_2' för 6.11.")
            huvud = _psi(psi_1, q.size, "psi_1") if olycka_huvudlast == "psi_1" else följd.copy()
            symbol = "ψ_1,j" if olycka_huvudlast == "psi_1" else "ψ_2,j"
            formel = f"E_d = ΣG + P + A_d + {symbol} · Q_j + Σ(i≠j)(ψ_2,i · Q_i)"
        elif nummer == "6.12":
            extra = _skalär(A_Ed, "A_Ed")
            formel = "E_d = ΣG + P + A_Ed + Σ(ψ_2,i · Q_i)"
        else:
            formel = "E_d = ΣG + P + Σ(ψ_2,i · Q_i)"

    def tal(x):
        return f"({x:g})" if x < 0 else f"{x:g}"

    grund = float(g.sum()) + p + extra
    bastermer = [tal(x) for x in g] + [tal(p)]
    if nummer in ("6.11", "6.12"):
        bastermer.append(tal(extra))
    fall = []
    for j in (range(q.size) if huvud is not None and q.size else [None]):
        faktorer = följd.copy()
        if j is not None:
            faktorer[j] = huvud[j]
        faktorer[q < 0] = 0
        värde = float(grund + np.dot(faktorer, q))
        if not np.isfinite(värde):
            raise ValueError("Lastkombinationen ger ett icke-ändligt resultat.")
        termer = bastermer + [f"{f:g} · {tal(x)}" for f, x in zip(faktorer, q)]
        fall.append({"huvudlast": j, "värde": värde, "termer": termer})
    styrande = max(fall, key=lambda f: f["värde"])
    return {nummer: styrande["värde"], "dimensionerande": styrande["värde"],
            "kombination": nummer, "huvudlast": styrande["huvudlast"],
            "lastfall": fall, "formel": formel}


# 6.13 kontrollerar en redan beräknad brukbarhetseffekt, t.ex. nedböjning.
# E_d och C_d ska vara icke-negativa och ha samma enhet. Ta vid behov
# absolutbeloppet av en signerad deformation före anropet.
def kontroll_613(E_d, C_d, *, skriv=False, enhet="", decimaler=3):
    ed = _skalär(E_d, "E_d")
    cd = _skalär(C_d, "C_d")
    if ed < 0 or cd < 0:
        raise ValueError("E_d och C_d ska vara icke-negativa.")
    if isinstance(decimaler, bool) or not isinstance(decimaler, int) or decimaler < 0:
        raise ValueError("decimaler ska vara ett icke-negativt heltal.")
    ok = ed <= cd
    kvot = ed / cd if cd else (0.0 if ed == 0 else float("inf"))
    if skriv:
        suffix = f" [{enhet}]" if enhet else ""
        _skriv_text(f"6.13: E_d ≤ C_d\nE_d = {ed:.{decimaler}f}{suffix}, "
                    f"C_d = {cd:.{decimaler}f}{suffix}\n"
                    + ("Kravet är uppfyllt." if ok else "Kravet är inte uppfyllt."))
    return {"E_d": ed, "C_d": cd, "uppfyllt": ok, "utnyttjandegrad": kvot}
