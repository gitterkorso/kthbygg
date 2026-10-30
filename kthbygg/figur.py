# Gemensamma verktyg för Matplotlib-figurer från kthbygg.
import os
import sys
from pathlib import Path
from types import MethodType


def _skrivbord():
    if sys.platform == "win32":
        import winreg

        # Windows kan ha flyttat skrivbordet till exempelvis OneDrive.
        nyckel = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, nyckel) as key:
                plats, _ = winreg.QueryValueEx(key, "Desktop")
            return Path(os.path.expandvars(plats))
        except OSError:
            pass
    elif sys.platform.startswith("linux"):
        config = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
        fil = config / "user-dirs.dirs"
        if fil.is_file():
            for rad in fil.read_text(encoding="utf-8").splitlines():
                if rad.startswith("XDG_DESKTOP_DIR="):
                    plats = rad.split("=", 1)[1].strip().strip('"')
                    return Path(os.path.expandvars(plats))
    return Path.home() / "Desktop"


def _spara(self, filnamn="balk.svg", **kwargs):
    namn = os.fspath(filnamn)
    if not namn or namn in (".", "..") or any(tecken in namn for tecken in ("/", "\\", ":")):
        raise ValueError("Ange bara ett filnamn, till exempel 'konsol.svg'. Filen sparas på skrivbordet.")
    fil = Path(namn)
    if not fil.suffix:
        fil = fil.with_suffix(".svg")
    if "format" in kwargs:
        raise ValueError("Välj format med filändelsen, till exempel .svg eller .pdf.")
    skrivbord = _skrivbord()
    if not skrivbord.is_dir():
        raise FileNotFoundError(f"Hittar inte skrivbordsmappen: {skrivbord}")
    sökväg = skrivbord / fil
    kwargs.setdefault("bbox_inches", "tight")
    self.savefig(sökväg, **kwargs)
    return sökväg


def _lagg_till_spara(fig):
    fig.spara = MethodType(_spara, fig)
    return fig
