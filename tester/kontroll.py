# Hjälpfunktioner för test-notebooks i KTHbygg.
#
# Varje kontroll jämför bibliotekets resultat med ett referensvärde som är
# framräknat för hand eller hämtat ur tabell. Kontroller märkta känt_fel=True
# är fel som ännu inte är rättade i biblioteket: de får misslyckas utan att
# notebooken stoppar, men sammanfattning() säger till när de börjar gå igenom.

import contextlib
import io
import math
import re

_resultat = []


def nollställ():
    _resultat.clear()


def _spara(namn, ok, känt_fel, detalj):
    _resultat.append((namn, ok, känt_fel))
    if ok:
        tecken = "✔"
    elif känt_fel:
        tecken = "✘ känt fel"
    else:
        tecken = "✘ FEL"
    print(f"{tecken:12} {namn}: {detalj}")


def kolla(namn, beräkning, förväntat, rel=1e-3, känt_fel=False):
    """Kör beräkning() och jämför med förväntat (relativ tolerans rel)."""
    try:
        värde = beräkning()
    except Exception as e:
        _spara(namn, False, känt_fel, f"{type(e).__name__}: {e}")
        return None
    if isinstance(förväntat, (int, float)) and isinstance(värde, (int, float)):
        ok = math.isclose(värde, förväntat, rel_tol=rel, abs_tol=1e-12)
        detalj = f"fick {värde:.6g}, väntat {förväntat:.6g}"
    else:
        ok = värde == förväntat
        detalj = f"fick {värde!r}, väntat {förväntat!r}"
    _spara(namn, ok, känt_fel, detalj)
    return värde


def kolla_fel(namn, beräkning, feltyp=ValueError, känt_fel=False):
    """Kontrollera att beräkning() avbryts med ett tydligt fel av typen feltyp."""
    try:
        värde = beräkning()
    except feltyp as e:
        _spara(namn, True, känt_fel, f"{type(e).__name__}: {e}")
        return
    except Exception as e:
        _spara(namn, False, känt_fel, f"väntat {feltyp.__name__}, fick {type(e).__name__}: {e}")
        return
    _spara(namn, False, känt_fel, f"väntat {feltyp.__name__}, fick värdet {värde!r}")


def utskrift(funktion, *args, **kwargs):
    """Kör funktionen och returnera det den skriver ut."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        funktion(*args, **kwargs)
    return buf.getvalue()


def klass(funktion, *args, **kwargs):
    """Tvärsnittsklassen (1-4) som en tvk-funktion skriver ut."""
    träff = re.search(r"Klass (\d)", utskrift(funktion, *args, **kwargs))
    return int(träff.group(1)) if träff else None


def sammanfattning():
    gick = [r for r in _resultat if r[1]]
    nya_fel = [r[0] for r in _resultat if not r[1] and not r[2]]
    kända = [r[0] for r in _resultat if not r[1] and r[2]]
    rättade = [r[0] for r in _resultat if r[1] and r[2]]

    print(f"{len(gick)} av {len(_resultat)} kontroller gick igenom.")
    if kända:
        print(f"\n{len(kända)} kända fel som ännu inte är rättade:")
        for namn in kända:
            print(f"  - {namn}")
    if rättade:
        print("\nDessa var märkta som kända fel men går nu igenom. Ta bort känt_fel=True:")
        for namn in rättade:
            print(f"  - {namn}")
    if nya_fel:
        raise AssertionError(f"{len(nya_fel)} oväntade fel: " + ", ".join(nya_fel))
    print("\nInga oväntade fel.")
