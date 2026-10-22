import sympy as smp
from IPython.display import display, Math
import re

# -------------------------------------------------
# Hjälpfunktion: enhet i kursiv + exponenter
# -------------------------------------------------
def _format_unit(unit):
    if "^" in unit:
        base, exp = unit.split("^", 1)
        return rf"\textit{{{base}}}^{{{exp}}}"
    else:
        return rf"\textit{{{unit}}}"

# -------------------------------------------------
# Intern visningsfunktion
# -------------------------------------------------
from sympy.parsing.sympy_parser import parse_expr

def _show(name, value, unit, expr=None, decimals=2):
    unit_ltx = _format_unit(unit)

    if isinstance(name, str):
        name_ltx = name.replace("_", "_{") + "}" if "_" in name else name
    else:
        name_ltx = smp.latex(name)

    if expr is not None:
        expr_str = expr.replace("math.pi", "smp.pi")

        tokens = set(re.findall(r"[a-zA-Z_]\w*", expr_str))
        known = set(dir(smp)) | {"smp", "pi", "math"}
        var_names = [t for t in tokens if t not in known]

        local_dict = {v: smp.Symbol(v) for v in var_names}
        local_dict["smp"] = smp

        expr_sym = parse_expr(expr_str, local_dict=local_dict, evaluate=False)

        for var in var_names:
            if var in globals():
                expr_sym = expr_sym.subs(local_dict[var], globals()[var])

        expr_ltx = smp.latex(expr_sym)
        val_ltx = f"{float(value):.{decimals}f}"

        display(Math(rf"{name_ltx} = {expr_ltx} = {val_ltx}\,{unit_ltx}"))
    else:
        val_ltx = f"{float(value):.{decimals}f}"
        display(Math(rf"{name_ltx} = {val_ltx}\,{unit_ltx}"))
# -------------------------------------------------
# Längd
# -------------------------------------------------
def mm(value, name, expr=None, decimals=2):
    _show(name, value, "mm", expr, decimals)

def cm(value, name, expr=None, decimals=2):
    _show(name, value/10, "cm", expr, decimals)

def m(value, name, expr=None, decimals=3):
    _show(name, value/1000, "m", expr, decimals)

# -------------------------------------------------
# Area
# -------------------------------------------------
def mm2(value, name, expr=None, decimals=2):
    _show(name, value, "mm^2", expr, decimals)

def cm2(value, name, expr=None, decimals=2):
    _show(name, value/100, "cm^2", expr, decimals)

def m2(value, name, expr=None, decimals=4):
    _show(name, value/1e6, "m^2", expr, decimals)

# -------------------------------------------------
# Volym
# -------------------------------------------------
def mm3(value, name, expr=None, decimals=2):
    _show(name, value, "mm^3", expr, decimals)

def cm3(value, name, expr=None, decimals=2):
    _show(name, value/1000, "cm^3", expr, decimals)

def m3(value, name, expr=None, decimals=4):
    _show(name, value/1e9, "m^3", expr, decimals)

# -------------------------------------------------
# Moment / kraft
# -------------------------------------------------
def Nmm(value, name, expr=None, decimals=2):
    _show(name, value, "Nmm", expr, decimals)

def Nm(value, name, expr=None, decimals=2):
    _show(name, value/1e3, "Nm", expr, decimals)

def kNm(value, name, expr=None, decimals=2):
    _show(name, value/1e6, "kNm", expr, decimals)

def MNm(value, name, expr=None, decimals=3):
    _show(name, value/1e9, "MNm", expr, decimals)

def kN(value, name, expr=None, decimals=2):
    _show(name, value/1000, "kN", expr, decimals)

def N(value, name, expr=None, decimals=2):
    _show(name, value, "N", expr, decimals)

# -------------------------------------------------
# Spänning / modul
# -------------------------------------------------
def Pa(value, name, expr=None, decimals=2):
    _show(name, value, "Pa", expr, decimals)

def MPa(value, name, expr=None, decimals=2):
    _show(name, value, "MPa", expr, decimals)

def GPa(value, name, expr=None, decimals=2):
    _show(name, value/1000, "GPa", expr, decimals)

# -------------------------------------------------
# Sektionsmoduler / ytmoment / warping
# -------------------------------------------------
def mm3(value, name, expr=None, decimals=2):
    _show(name, value, "mm^3", expr, decimals)

def mm4(value, name, expr=None, decimals=2):
    _show(name, value, "mm^4", expr, decimals)

def cm4(value, name, expr=None, decimals=2):
    _show(name, value/10000, "cm^4", expr, decimals)

def mm6(value, name, expr=None, decimals=2):
    _show(name, value, "mm^6", expr, decimals)

def cm6(value, name, expr=None, decimals=2):
    _show(name, value/1000000, "cm^6", expr, decimals)

def mm8(value, name, expr=None, decimals=2):
    _show(name, value, "mm^8", expr, decimals)

# Generella dimensionslösa storheter
def generic(value, name, expr=None, decimals=3):
    _show(name, value, "", expr, decimals)

# -------------------------------------------------
# Angles
# -------------------------------------------------

def Degrees(value, name, expr=None, decimals=2):
    _show(name, value, "Degrees", expr, decimals)

def Radians(value, name, expr=None, decimals=2):
    _show(name, value, "Radians", expr, decimals)

# -------------------------------------------------
# Utnyttjandegrad
# -------------------------------------------------

def Utnyttjande(value1, value2, name="Utnyttjandegrad", expr=None, decimals=2):
    _show(name, value1 / value2, "", expr, decimals)


# HTML checkar

from IPython.display import display, HTML

def check_box(value1,
              value2,
              label1="Value 1",
              label2="Value 2",
              title="Kontroll",
              operator=">=",
              decimals=2):

    # ---- jämförelse ----
    ops = {
        ">=": value1 >= value2,
        "<=": value1 <= value2,
        ">":  value1 >  value2,
        "<":  value1 <  value2,
        "==": value1 == value2
    }

    if operator not in ops:
        raise ValueError("Operator måste vara >=, <=, >, < eller ==")

    ok = ops[operator]
    ratio = value2/value1 if value1 != 0 else float("inf")

    # ---- styling ----
    color = "#2ecc71" if ok else "#e74c3c"
    symbol = "✔" if ok else "✘"
    status = "OK" if ok else "EJ OK"

    html = f"""
    <div style="
        font-family:Segoe UI,Arial;
        width:320px;
        border-radius:12px;
        overflow:hidden;
        box-shadow:0 2px 8px rgba(0,0,0,0.15);
        border:1px solid #ddd;
        background:white;">

        <div style="
            background:{color};
            color:white;
            font-size:22px;
            font-weight:bold;
            padding:10px;
            text-align:center;">
            {symbol} {title} — {status}
        </div>

        <div style="padding:16px;font-size:16px;color:#222;">
            <b>{label1}</b> = {value1:.{decimals}f}<br>
            <b>{label2}</b> = {value2:.{decimals}f}<br><br>

            <b>Jämförelse:</b> {label1} {operator} {label2}<br><br>

            <b>Utnyttjandegrad:</b><br>
            <span style="font-size:20px;font-weight:bold;">
            {ratio:.2%}
            </span>
        </div>
    </div>
    """

    display(HTML(html))