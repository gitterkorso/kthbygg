import numpy as np


def automatisk_skala(kurvor):
    # Utgå från hela geometrin, inte längden på ett godtyckligt FE-element.
    punkter = np.concatenate([bas for bas, _ in kurvor])
    storlek = float(np.linalg.norm(np.ptp(punkter, axis=0)))
    maximum = max(float(np.max(np.linalg.norm(delta, axis=1))) for _, delta in kurvor)
    if storlek == 0 or maximum <= 1e-12 * storlek:
        return 1.

    # Fyra procent ger en synlig men måttlig förskjutning i modellbilden.
    skala = .04 * storlek / maximum
    # Begränsa även den lokala förändringen. En kort del får inte vikas ihop
    # bara för att resten av modellen är lång. Detta är oberoende av mesh.
    for bas, delta in kurvor:
        ds = np.linalg.norm(np.diff(bas, axis=0), axis=1)
        dd = np.linalg.norm(np.diff(delta, axis=0), axis=1)
        giltiga = ds > 0
        lutning = np.max(dd[giltiga] / ds[giltiga], initial=0.)
        if lutning > 0:
            skala = min(skala, .2 / lutning)

    # Avrunda nedåt till en lättläst faktor, även när formen måste förminskas.
    tiopotens = 10. ** np.floor(np.log10(skala))
    steg = np.array([1., 1.25, 1.5, 2., 2.5, 3., 4., 5., 6., 8., 10.])
    return float(steg[steg <= skala / tiopotens + 1e-12][-1] * tiopotens)


def rita_kurvor(ax, kurvor, skala, langd, faktor=1):
    # Samma förstoring för alla element och båda förskjutningskomponenterna.
    if skala is None:
        skala = automatisk_skala(kurvor)
    skala = float(skala)
    if not np.isfinite(skala) or skala <= 0:
        raise ValueError("skala måste vara positiv och ändlig")
    # Behåll modellens ursprungliga utseende och lägg deformationen ovanpå.
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    geometri = np.concatenate([bas for bas, _ in kurvor])
    pad = .025 * np.linalg.norm(np.ptp(geometri, axis=0)) * faktor
    for i, (bas, delta) in enumerate(kurvor):
        xy = faktor * (bas + skala * delta)
        ax.plot(*xy.T, color="black", linestyle="--", lw=1.8, zorder=6,
                label=f"Deformerad, ×{skala:.4g}" if i == 0 else None)
        xmin, xmax = min(xmin, xy[:, 0].min()-pad), max(xmax, xy[:, 0].max()+pad)
        ymin, ymax = min(ymin, xy[:, 1].min()-pad), max(ymax, xy[:, 1].max()+pad)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_aspect("equal", adjustable="box")
    ax.legend(loc="lower right", bbox_to_anchor=(1, 1.02), fontsize=9,
              borderaxespad=0)
    return skala
