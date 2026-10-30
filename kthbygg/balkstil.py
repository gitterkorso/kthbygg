# Teknisk modellritning. Alla symboler ritas i samma koordinatsystem
# med lika skala i x och y, oberoende av balkens valda längdenhet.
from dataclasses import dataclass, replace

import numpy as np

from .figur import _lagg_till_spara


@dataclass(frozen=True)
class Ritstil:
    namn: str
    beskrivning: str
    balk: str
    last: str
    sekundar: str
    balkbredd: float
    pil: str
    fyllda_stod: bool = False
    konturbalk: bool = False
    snedstreck: bool = False
    font: str = "DejaVu Sans"


STILAR = {
    "teknisk": Ritstil("Teknisk", "Svart tusch · slutna pilspetsar · tydlig linjehierarki",
                       "#20252b", "#20252b", "#737b85", 3.2, "-|>"),

}


def _rita_vinkelkraft(ax, xy, F, vinkel, color, kraftenhet):
    if not F:
        return
    alfa = np.deg2rad(vinkel)
    riktning = np.array([np.cos(alfa), np.sin(alfa)])
    start = -55*riktning
    ax.annotate("", xy, xytext=tuple(start), textcoords="offset points",
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.6,
                                mutation_scale=13, shrinkA=0, shrinkB=0), zorder=7)
    normal = np.array([-riktning[1], riktning[0]])
    if normal[1] < 0:
        normal = -normal
    ax.annotate(f"F = {F:g} {kraftenhet}", xy,
                xytext=tuple(start*.6+14*normal), textcoords="offset points",
                ha="center", va="center", fontsize=9, color=color)


def _rita_inspanning(ax, transform, color):
    # Gemensam symbol: lokal x pekar ut från konstruktionen in i stödet.
    from matplotlib.patches import Rectangle

    klipp = Rectangle((0, -38), 30, 76, transform=transform)
    for y in range(-26, 37, 10):
        streck, = ax.plot([0, 14], [y, y-10], color=color, lw=.85,
                          solid_capstyle="round", transform=transform)
        streck.set_clip_path(klipp)
    ax.plot([0, 0], [-38, 38], color=color, lw=2, zorder=4,
            solid_capstyle="butt", transform=transform)


def _forbered_visning(fig):
    import matplotlib.pyplot as plt

    _lagg_till_spara(fig)

    if "inline" in plt.get_backend().lower():
        from matplotlib_inline.backend_inline import set_matplotlib_formats

        set_matplotlib_formats("svg")
        # Hantera både explicit display och Jupyters automatiska visning.
        # Stäng först när figuren har visats, så att plt.show() också fungerar.
        def visa_en_gang():
            from IPython.display import display

            del fig._ipython_display_
            try:
                display(fig)
            finally:
                fig._ipython_display_ = visa_en_gang
                plt.close(fig)

        fig._ipython_display_ = visa_en_gang
    return fig


def rita_modell(balk, stil="teknisk", *, ax=None, langdenhet="m", kraftenhet="kN",
                matt=True, titel=None, färgat=False, måttfärg="#d62728"):
    # Returnerar figuren även när en befintlig axel används.
    # Enhetstexterna är etiketter; funktionen räknar inte om indata.
    import matplotlib.pyplot as plt
    from matplotlib.path import Path
    from matplotlib.transforms import Affine2D, ScaledTranslation
    from matplotlib.patches import ArrowStyle, Circle, FancyArrowPatch, Polygon, Rectangle

    if stil not in STILAR:
        raise ValueError(f"Okänd stil {stil!r}. Välj: {', '.join(STILAR)}")
    s = STILAR[stil]
    if färgat:
        s = replace(s, last="#2878b8", sekundar=måttfärg)
    egen_figur = ax is None
    if egen_figur:
        _, ax = plt.subplots(figsize=(11, 4.3))
    fig = ax.figure
    X = lambda x: 900 * x / balk.L
    # Balkens överkant består av en geometrisk nivå och halva linjevikten.
    # Linjevikten anges i punkter så anslutningen håller vid export och zoom.
    balkkant = 4 if s.konturbalk else 0

    def linje(xs, ys, color=None, lw=1, **kw):
        capstyle = kw.pop("solid_capstyle", "butt")
        return ax.plot(xs, ys, color=color or s.balk, lw=lw,
                       solid_capstyle=capstyle, **kw)

    def text(x, y, value, color=None, size=10, **kw):
        va = kw.pop("va", "center")
        return ax.text(x, y, value, color=color or s.balk, fontsize=size,
                       fontfamily=s.font, ha="center", va=va, **kw)

    class Momentspets(ArrowStyle.CurveFilledB):
        # Basen ligger vid bågens slut. Spetsen fortsätter längs tangenten där.
        def transmute(self, path, mutation_size, linewidth):
            bas = path.vertices[-1]
            tangent = bas - path.vertices[-2]
            tangent = tangent / np.linalg.norm(tangent)
            normal = np.array([-tangent[1], tangent[0]])
            spets = bas + self.head_length * mutation_size * tangent
            sida = self.head_width * mutation_size * normal
            huvud = Path([bas+sida, spets, bas-sida, bas+sida],
                         [Path.MOVETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY])
            return [path, huvud], [False, True]

    class Lastpil(FancyArrowPatch):
        # Anpassa vid varje rendering, även efter ändrad figurstorlek eller DPI.
        def __init__(self, start, slut, lutning=0, **kwargs):
            super().__init__(start, slut, **kwargs)
            self.andpunkter = (start, slut)
            self.max_spets = self.get_mutation_scale()
            self.lutning = abs(lutning)

        def draw(self, renderer):
            a, b = self.get_transform().transform(self.andpunkter)
            langd = np.linalg.norm(b-a) / renderer.points_to_pixels(1)
            fri_langd = langd - self.shrinkA - self.shrinkB
            # Reservera utrymme för linjevikten och spetsens bredd mot snedlinjen.
            utrymme = fri_langd - 2*self.get_linewidth()*(1+self.lutning)
            spets = min(self.max_spets, .6*utrymme/(.4+.2*self.lutning))
            if spets < 3:
                return
            self.set_mutation_scale(spets)
            super().draw(renderer)

    def pil(start, slut, liten=False, color=None, start_pa_balk=False, slut_pa_balk=False,
            lutning=0):
        pilklass = Lastpil if liten else FancyArrowPatch
        extra = {"lutning": lutning} if liten else {}
        patch = pilklass(start, slut, arrowstyle=s.pil,
                                    mutation_scale=9 if liten else 13,
                                    linewidth=1.1 if liten else 1.6,
                                    color=color or s.last,
                                    capstyle="butt", joinstyle="miter",
                                    shrinkA=s.balkbredd/2 if start_pa_balk else 0,
                                    shrinkB=s.balkbredd/2 if slut_pa_balk else 0,
                                    zorder=4, **extra)
        ax.add_patch(patch)
        return patch

    stodtransform = ax.transData + ScaledTranslation(
        0, -s.balkbredd / 144, fig.dpi_scale_trans)

    def mark(x, y, bredd=44, forskjutning=0):
        # Samma skraffering som vid fast inspänning, klippt mot stödlinjen.
        klipp = Rectangle((x-bredd/2, y-30), bredd, 30, transform=stodtransform)
        for dx in np.arange(-bredd/2+8+forskjutning, bredd/2-1, 8):
            streck, = linje([x+dx-6, x+dx], [y-9, y], s.balk, .85,
                           solid_capstyle="round", transform=stodtransform)
            streck.set_clip_path(klipp)
        linje([x-bredd/2, x+bredd/2], [y, y], lw=1.1, zorder=3.5, transform=stodtransform)

    # Balk och stöd ligger ovanför måttkedjorna.
    if s.konturbalk:
        ax.add_patch(Rectangle((0, -4), 900, 8, facecolor="#f2f4f5",
                               edgecolor=s.balk, linewidth=s.balkbredd, zorder=3, gid="ursprungsgeometri"))
    else:
        linje([0, 900], [0, 0], lw=s.balkbredd, zorder=3, gid="ursprungsgeometri")
    for x, typ in balk._stöd.items():
        xx = X(x)
        if typ in ("fast", "inspänd", "inspänning"):
            # Skrafferingen vänds utåt vid högeränden.
            riktning = 1 if x == balk.L else -1
            transform = Affine2D().scale(riktning, 1).translate(xx, 0) + ax.transData
            _rita_inspanning(ax, transform, s.balk)
        else:
            # Stödets spets ansluter till balkens synliga underkant.
            # Samma förskjutning på mark och hjul håller stödet sammanhängande.
            rullstod = typ in ("rull", "rullager")
            stodtopp = -balkkant
            stodbas = stodtopp - (14 if rullstod else 22)
            halvbredd = 9 if rullstod else 14
            # Mycket liten grafisk indragning av ändstöden.
            # Beräkningsläge och måttsättning använder fortfarande stödets x.
            indrag = (halvbredd + 3) / 25
            xx = min(max(xx, indrag), 900 - indrag)
            triangel = Polygon([(xx, stodtopp), (xx-halvbredd, stodbas), (xx+halvbredd, stodbas)],
                                 facecolor=s.balk if s.fyllda_stod else "white",
                                 edgecolor=s.balk if rullstod else "none",
                                 linewidth=1.2 if rullstod else 0, zorder=3,
                                 transform=stodtransform)
            ax.add_patch(triangel)
            if not rullstod:
                # Marklinjen är stödets enda bottenlinje; rita bara de två sidorna.
                sidor, = linje([xx-halvbredd, xx, xx+halvbredd],
                              [stodbas, stodtopp, stodbas], lw=1.2, zorder=3,
                              transform=stodtransform)
                sidor.set_clip_path(Rectangle(
                    (xx-halvbredd-10, stodbas), 2*halvbredd+20,
                    stodtopp-stodbas+10, transform=stodtransform))
            if rullstod:
                # Centrumavståndet är två radier: hjulen tangerar varandra.
                # Rita hjulen ovanpå mark och triangel så deras vita insidor är fria.
                hjulradie = 4
                for dx in (-hjulradie, hjulradie):
                    ax.add_patch(Circle((xx+dx, stodbas-hjulradie), hjulradie, facecolor="white",
                                        edgecolor=s.balk, linewidth=1, zorder=4,
                                        transform=stodtransform))
                mark(xx, stodbas-2*hjulradie)
            else:
                # Undvik att skrafferingen fortsätter längs triangelns sida.
                mark(xx, stodbas, forskjutning=2)
    for x in balk._leder:
        ax.add_patch(Circle((X(x), 0), 5, facecolor="white", edgecolor=s.balk,
                            linewidth=1.4, zorder=6))

    # Varje utbredd last får egen rad, så överlappande laster kan urskiljas.
    qmax = max((abs(q) for _, _, q1, q2 in balk._utbredda for q in (q1, q2)), default=1) or 1
    # Hela lastfiguren utgår från balkens synliga överkant, även vid nollast.
    lasttransform = ax.transData + ScaledTranslation(
        0, s.balkbredd / 144, fig.dpi_scale_trans)
    top = 145
    for i, (x1, x2, q1, q2) in enumerate(balk._utbredda):
        if q1 == q2 == 0:
            continue
        bas = balkkant
        xa, xb = X(x1), X(x2)
        # Negativa laster ritas uppåt på samma rad; amplituden är proportionell.
        # Vid teckenbyte delas fyllningen vid nollgenomgången.
        xs = np.linspace(xa, xb, max(2, int((xb-xa)/38)+1))
        qs = np.linspace(q1, q2, len(xs))
        if q1*q2 < 0:
            zero = xa + (xb-xa)*(-q1)/(q2-q1)
            xs = np.sort(np.append(xs, zero))
            qs = q1 + (q2-q1)*(xs-xa)/(xb-xa)
        hojd = bas + 105*i + 79*np.abs(qs)/qmax
        # Rita ändhörnen som en sammanhängande linje med samma bredd som
        # pilskaften. Två separata linjeändar lämnar annars en hackig skarv.
        horn_x = np.r_[xa, xs, xb]
        # Sidokanterna ska nå balken även om en kort ändpil inte kan ritas.
        horn_y = np.r_[bas, hojd, bas]
        konturtransform = lasttransform
        if i == 0 and (q1 == 0 or q2 == 0):
            # Sänk konturen en halv linjebredd så hela strecket försvinner
            # in i balken vid nolländen, inte bara streckets mittlinje.
            konturtransform = lasttransform + ScaledTranslation(
                0, -1.1 / 144, fig.dpi_scale_trans)
        kontur, = linje(horn_x, horn_y, s.last, 1.1, zorder=5,
                        solid_joinstyle="miter", transform=konturtransform)
        # Klipp exakt vid balkens överkant och ändar, även linjens tjocklek.
        kontur.set_clip_path(Rectangle((0, bas), 900, max(hojd)-bas+100,
                                      transform=lasttransform))
        # Klipp mot överkonturen men lämna sidoutrymme för ändpilarnas spetsar.
        klipp = Polygon([(xa-30, bas-100), (xa-30, hojd[0]),
                         *zip(xs, hojd), (xb+30, hojd[-1]), (xb+30, bas-100)],
                        closed=True, transform=lasttransform)
        for xx, q, yy in zip(xs, qs, hojd):
            if abs(q) > qmax*1e-10:
                start, slut = (xx, yy), (xx, bas)
                lastpil = pil(start if q > 0 else slut, slut if q > 0 else start, liten=True,
                    lutning=79*(q2-q1)/(qmax*(xb-xa)))
                lastpil.set_transform(lasttransform)
                lastpil.set_clip_path(klipp)
        label_x = (xa+xb)/2
        label = f"q = {abs(q1):g} {kraftenhet}/{langdenhet}"
        if q1 == 0 or q2 == 0:
            # Triangellast märks bara med maxvärdet vid den högsta änden.
            label_x = xa if abs(q1) > abs(q2) else xb
            label = f"{max(abs(q1), abs(q2)):g} {kraftenhet}/{langdenhet}"
        elif q1 != q2:
            label = f"q = {q1:g} → {q2:g} {kraftenhet}/{langdenhet}"
        text(label_x, max(hojd)+23, label, s.last)
        top = max(top, max(hojd)+65)

    for i, (x, p, h) in enumerate(balk._punktlaster):
        xx = X(x)
        if i in balk._vinkellaster:
            F, vinkel = balk._vinkellaster[i]
            _rita_vinkelkraft(ax, (xx, balkkant), F, vinkel, s.last, kraftenhet)
            continue
        # Höj punktlasten om den delar x med en utbredd last.
        overlap = [j for j, (a, b, _, _) in enumerate(balk._utbredda) if a <= x <= b]
        y = max(118, 130+105*max(overlap)) if overlap else 118
        if p:
            start, slut = (xx, y), (xx, balkkant)
            pil(start if p > 0 else slut, slut if p > 0 else start,
                start_pa_balk=p < 0, slut_pa_balk=p > 0)
            text(xx, y+23, f"P = {abs(p):g} {kraftenhet}", s.last)
            top = max(top, y+60)
        if h:
            # Horisontell last visas på egen nivå för att inte dölja balken.
            y = 51
            start = (xx-83 if h > 0 else xx+83, y)
            # Sammanhängande angreppslinje från balken, förbi pilspetsen.
            linje([xx, xx], [balkkant, y+6], s.last, .9, zorder=3)
            pil(start, (xx, y))
            text((start[0]+xx)/2, y+24, f"H = {abs(h):g} {kraftenhet}", s.last, size=9)

    for x, moment in balk._punktmoment:
        if not moment:
            continue
        # Positivt moment går moturs; pilspetsen följer cirkelns tangent.
        xx, yy, r = X(x), 0, 33
        # Bågen slutar vid spetsens bas; dess tangent bestämmer huvudets vinkel.
        bage = Path.arc(35, 305)
        if moment < 0:
            bage = Path(bage.vertices[::-1], bage.codes.copy())
        bage = bage.transformed(Affine2D().scale(r).translate(xx, yy))
        ax.add_patch(FancyArrowPatch(path=bage,
                                    arrowstyle=Momentspets(), mutation_scale=13,
                                    linewidth=1.5, color=s.last, zorder=5,
                                    capstyle="butt", joinstyle="miter"))
        text(xx, -70, f"M = {abs(moment):g} {kraftenhet}{langdenhet}", s.last, size=9)

    if matt:
        punkter = sorted({0., balk.L, *balk._stöd, *balk._leder,
                          *(x for x, _, _ in balk._punktlaster),
                          *(x for x, _ in balk._punktmoment),
                          *(x for a, b, _, _ in balk._utbredda for x in (a, b))})

        def dimension(a, b, y, total=False):
            xa, xb = X(a), X(b)
            for xx in (xa, xb):
                linje([xx, xx], [y-9, -82 if not total else y+16], s.sekundar, .65)
            if s.snedstreck:
                linje([xa-5, xb+5], [y, y], s.sekundar, .8)
                for xx in (xa, xb):
                    linje([xx-4, xx+4], [y-6, y+6], s.balk, 1.1)
            else:
                ax.add_patch(FancyArrowPatch((xa, y), (xb, y), arrowstyle="<->",
                                            mutation_scale=8, color=s.sekundar,
                                            linewidth=.75, shrinkA=0, shrinkB=0,
                                            capstyle="butt", joinstyle="miter"))
            # Kortare segment får roterad etikett för att undvika textkrockar.
            kort = xb-xa < 62
            label = f"{'L = ' if total else ''}{b-a:g} {langdenhet}"
            text((xa+xb)/2, y-18 if kort else y+13, label, s.sekundar,
                 size=9, rotation=90 if kort else 0, va="top" if kort else "center")

        for a, b in zip(punkter, punkter[1:]):
            dimension(a, b, -116)
        if len(punkter) > 2:
            dimension(0, balk.L, -181, total=True)

    # Nya modellvillkor redovisas explicit så de inte försvinner i modellbilden.
    villkor = []
    for x, k in balk._fjädrar.items():
        villkor.append(f"Fjäder x={x:g}: kx={k[0]:g}, ky={k[1]:g}, kr={k[2]:g}")
    for a, b, ei, ea in balk._delar:
        villkor.append(f"Sektion {a:g}–{b:g}: EI={ei:g}, EA={ea:g}")
    for a, b, eps, kappa in balk._temperaturer:
        villkor.append(f"Temperatur {a:g}–{b:g}: εT={eps:g}, κT={kappa:g}")
    for villkorstext in villkor:
        top += 26
        text(450, top, villkorstext, s.sekundar, size=8)

    ax.set_xlim(-95, 995)
    ax.set_ylim(-220 if matt else -95, top+10)
    ax.set_aspect("equal", adjustable="box")
    ax.set_axis_off()
    if titel:
        ax.set_title(titel, loc="left", fontsize=12, fontweight="bold", color=s.balk, pad=16)
    return _forbered_visning(fig) if egen_figur else _lagg_till_spara(fig)
