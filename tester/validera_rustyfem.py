# Kör 15 oberoende modeller i KTHBYGG och installerad RustyFEM.
# Inga ändringar görs i RustyFEM-projektet. Alla körfiler sparas här i repot.
import argparse
import json
import subprocess
from pathlib import Path
import numpy as np
from kthbygg.ram import Ram

ROOT = Path(__file__).resolve().parents[1]


def rak():
    return Ram(EI=40000, EA=200000).nod(1, 0, 0).nod(2, 4, 0).stång(1, 1, 2)


def fall():
    cases = []
    def add(name, r, thermal=False):
        cases.append((name, r, thermal))
    add("01_konsol_punktlast", rak().stöd(1, "fast").punktlast(2, 12))
    add("02_konsol_moment", rak().stöd(1, "fast").moment(2, 8))
    r = Ram(EI=40000, EA=200000).nod(1, 0, 0).nod(2, 2, 0).nod(3, 4, 0)
    r.stång(1, 1, 2).stång(2, 2, 3).stöd(1, "led").stöd(3, "rull").punktlast(2, 12)
    add("03_fritt_upplagd", r)
    add("04_fast_fast_jamn_last", rak().stöd(1, "fast").stöd(2, "fast").utbredd_last(1, 6))
    add("05_konsol_triangellast", rak().stöd(1, "fast").utbredd_last(1, 0, 9))
    r = Ram(EI=40000, EA=200000).nod(1, 0, 0).nod(2, 4, 0).nod(3, 8, 0)
    r.stång(1, 1, 2).stång(2, 2, 3).stöd(1, "led").stöd(2, "rull").stöd(3, "rull")
    r.utbredd_last(1, 6).utbredd_last(2, 3)
    add("06_kontinuerlig_tva_fack", r)
    r = Ram(EI=40000, EA=200000).nod(1, 0, 0).nod(2, 2, 0).nod(3, 4, 0)
    r.stång(1, 1, 2).stång(2, 2, 3, EI=15000, EA=80000).stöd(1, "fast").punktlast(3, 12, 8)
    add("07_olika_EI_EA", r)
    r = Ram(EI=40000, EA=200000).nod(1, 0, 0).nod(2, 0, 4)
    r.stång(1, 1, 2).stöd(1, "fast").nodlast(2, Fx=12, Fy=-8)
    add("08_pelare", r)
    r = Ram(EI=40000, EA=200000).nod(1, 0, 0).nod(2, 3, 4)
    r.stång(1, 1, 2).stöd(1, "fast").punktlast(2, 12, 7).moment(2, 5)
    add("09_sned_konsol", r)
    r = Ram(EI=40000, EA=200000)
    for i, xy in enumerate([(0, 0), (0, 3), (4, 4), (4, 0)], 1):
        r.nod(i, *xy)
    r.stång(1, 1, 2).stång(2, 2, 3, EI=60000, EA=300000).stång(3, 3, 4)
    r.stöd(1, "fast").stöd(4, "led").punktlast(2, 10, 8).punktlast(3, 15)
    add("10_portal_snett_tak", r)
    add("11_translationsfjadrar", rak().stöd(1, "fast").fjäderstöd(2, kx=50000, ky=1000).punktlast(2, 12, 8))
    add("12_rotationsfjader", rak().stöd(1, "led").fjäderstöd(1, kr=20000).punktlast(2, 12))
    add("13_fri_varmeutvidgning", rak().stöd(1, "fast").temperatur(1, 30), True)
    add("14_fastlast_uppvarmning", rak().stöd(1, "fast").stöd(2, "fast").temperatur(1, 30), True)
    r = Ram(EI=40000, EA=200000).nod(1, 0, 0).nod(2, 0, 3).nod(3, 4, 3)
    r.stång(1, 1, 2).stång(2, 2, 3).stöd(1, "fast")
    r.utbredd_last(1, 4).utbredd_last(2, 6).punktlast(3, 8, 5)
    add("15_L_ram_lokala_laster", r)
    return cases


def export(r, thermal):
    lines = ["*HEADING", "KTHBYGG independent solver comparison", "*NODE, NSET=ALL"]
    for n, (x, y) in r.noder.items():
        lines.append(f"{n}, {x:.16g}, {y:.16g}")
    for n, el in r.element.items():
        lines += [f"*ELEMENT, TYPE={'B21' if thermal else 'B23'}, ELSET=E{n}", f"{n}, {el['start']}, {el['slut']}"]
        # Rectangle chosen to match both EA and EI, E in kN/m2.
        E = 2e8
        h = np.sqrt(12*el["EI"]/el["EA"])
        b = el["EA"]/E/h
        lines += [f"*MATERIAL, NAME=M{n}", "*ELASTIC", f"{E}, 0.3"]
        if thermal:
            lines += ["*EXPANSION", "1.2e-5"]
        lines += [f"*BEAM SECTION, SECTION=RECT, MATERIAL=M{n}, ELSET=E{n}", f"{b:.16g}, {h:.16g}"]
    eid = max(r.element) + 1
    for n, ks in r._fjädrar.items():
        for dof, k in zip((1, 2, 6), ks):
            if k:
                lines += [f"*ELEMENT, TYPE=SPRING1, ELSET=S{eid}", f"{eid}, {n}",
                          f"*SPRING, ELSET=S{eid}", str(dof), str(k)]
                eid += 1
    lines += ["*BOUNDARY"]
    for n, mask in r._stöd.items():
        for dof, fixed in zip((1, 2, 6), mask):
            if fixed:
                lines.append(f"{n}, {dof}, {dof}, 0")
    if thermal:
        lines += ["*INITIAL CONDITIONS, TYPE=TEMPERATURE", "ALL, 0"]
    lines += ["*STEP", "*STATIC"]
    if r._laster:
        lines += ["*CLOAD"]
        for n, loads in r._laster.items():
            for dof, val in zip((1, 2, 6), loads):
                if val:
                    lines.append(f"{n}, {dof}, {val:.16g}")
    # RustyFEM has uniform DLOAD; use independently integrated nodal loads for
    # the one trapezoidal case, explicitly marked in the report.
    for n, el in r.element.items():
        if el["q1"] == el["q2"]:
            if el["q1"]:
                v = r.noder[el["slut"]]-r.noder[el["start"]]
                c, s = v/np.linalg.norm(v)
                lines += ["*DLOAD", f"{n}, PX, {el['q1']*s:.16g}", f"{n}, PY, {-el['q1']*c:.16g}"]
        else:
            # Gauss integration, independent from the solver's closed formulas.
            a, b = el["start"], el["slut"]
            v = r.noder[b]-r.noder[a]
            L = np.linalg.norm(v)
            c, s = v/L
            fe = np.zeros(4)
            gp, gw = np.polynomial.legendre.leggauss(4)
            for g, w in zip(gp, gw):
                t = (g+1)/2
                N = np.array([1-3*t*t+2*t**3, L*(t-2*t*t+t**3), 3*t*t-2*t**3, L*(-t*t+t**3)])
                fe -= N*(el["q1"]*(1-t)+el["q2"]*t)*w*L/2
            lines += ["*CLOAD"]
            for node, force, moment in ((a, fe[0], fe[1]), (b, fe[2], fe[3])):
                lines += [f"{node}, 1, {-s*force:.16g}", f"{node}, 2, {c*force:.16g}", f"{node}, 6, {moment:.16g}"]
    if thermal:
        temps = {el["eps"]/12e-6 for el in r.element.values()}
        assert len(temps) == 1
        lines += ["*TEMPERATURE", f"ALL, {temps.pop():.16g}"]
    lines += ["*OUTPUT, FIELD", "*NODE OUTPUT", "U, UR, RF, RM", "*ELEMENT OUTPUT", "SF, SM", "*END STEP"]
    return "\n".join(lines)+"\n"


def read_result(path):
    nodes, elements = {}, {}
    for line in path.read_text().splitlines():
        p = line.split(";")
        if p[0] == "N":
            nodes.setdefault(int(p[3]), {}).update({k: float(v) for k, v in (s.split("=") for s in p[4:])})
        if p[0] == "E":
            elements.setdefault((int(p[3]), int(p[4])), {}).update({k: float(v) for k, v in (s.split("=") for s in p[6:])})
    return nodes, elements


def run(exe, out):
    out.mkdir(parents=True, exist_ok=True)
    results = []
    for name, model, thermal in fall():
        inp, res = out/f"{name}.inp", out/f"{name}.res"
        inp.write_text(export(model, thermal), encoding="utf-8")
        cmd = subprocess.run([str(exe), "run", str(inp), "--out", str(res)], capture_output=True, text=True, errors="replace", cwd=out, timeout=60)
        (out/f"{name}.log").write_text(cmd.stdout+cmd.stderr, encoding="utf-8")
        if cmd.returncode or not res.exists():
            results.append(dict(fall=name, status="ERROR", error=cmd.stderr))
            print(name, "ERROR", cmd.stderr[-250:], flush=True)
            continue
        actual = model.lös()
        nodes, elems = read_result(res)
        pairs = {"förskjutning": [], "reaktion": [], "snittkraft": []}
        for n, d in actual.förskjutningar.items():
            for key, rust in (("ux", "U1"), ("uy", "U2"), ("rotation", "UR3")):
                pairs["förskjutning"].append((d[key], nodes[n][rust]))
        for n, reaction in actual.reaktioner.items():
            for j, (key, rust, disp) in enumerate((("H", "RF1", "U1"), ("V", "RF2", "U2"), ("M", "RM3", "UR3"))):
                v = nodes[n].get(rust, 0.)
                # At free spring DOFs RustyFEM RF is the total residual (zero).
                if n in model._fjädrar:
                    v -= model._fjädrar[n][j]*nodes[n][disp]
                pairs["reaktion"].append((reaction[key], v))
        # B23 reports interpolated moments, not exact loaded-element fields.
        # Compare N and M at its three Gauss points only on unloaded elements.
        if not thermal:
            for n, el in model.element.items():
                if el["q1"] or el["q2"]:
                    continue
                L = np.linalg.norm(model.noder[el["slut"]]-model.noder[el["start"]])
                for ip, frac in enumerate((.1127016653792583, .5, .8872983346207417), 1):
                    e = elems[(n, ip)]
                    pairs["snittkraft"] += [(actual.N(n, frac*L), e["SF11"]), (actual.M(n, frac*L), -e["SM1"])]
        errors = {}
        for kind, values in pairs.items():
            if not values:
                continue
            arr = np.array(values)
            maxerr = float(np.max(np.abs(arr[:, 0]-arr[:, 1])))
            ref = float(np.max(np.abs(arr[:, 1])))
            atol = 1e-9 if kind == "förskjutning" else 1e-6
            errors[kind] = dict(max_abs=maxerr, reference_scale=ref, passed=maxerr <= atol+1e-7*ref, count=len(values))
        status = "PASS" if all(e["passed"] for e in errors.values()) else "FAIL"
        results.append(dict(fall=name, status=status, errors=errors, element="B21" if thermal else "B23",
                            load="Gauss-integrerade ekvivalenta nodlaster" if name.startswith("05") else "Native RustyFEM load"))
        print(name, status, errors, flush=True)
    (out/"resultat.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = ["# KTHBYGG mot RustyFEM – 15 jämförelsefall", "", f"Körbar fil: `{exe}`", "",
             "Tolerans per grupp: 1e-7 × största referensvärdet + absolut tolerans (1e-9 för förskjutning/rotation, 1e-6 för krafter/moment). Enheter kN, m, rad.", "",
             "| Fall | Status | Max absolut förskjutnings-/rotationsfel | Max absolut reaktionsfel | Max absolut N/M-fel |", "|---|---|---:|---:|---:|"]
    for r in results:
        vals = [f"{r.get('errors', {}).get(k, {}).get('max_abs', float('nan')):.3g}" for k in ("förskjutning", "reaktion", "snittkraft")]
        lines.append(f"| {r['fall']} | {r['status']} | {' | '.join(vals)} |")
    lines += ["", "B23 används för mekaniska fall. B21 används för jämn temperatur, där skjuvdeformation inte påverkar lösningen. Temperaturerna skickas som *TEMPERATURE och *EXPANSION, inte som ekvivalenta laster.",
              "", "Triangellasten jämförs via oberoende Gauss-integrerade nodlaster. Det fallet verifierar nodlösningen och reaktionerna, inte RustyFEM:s hantering av en inbyggd triangellast.",
              "", "N och M jämförs i tre integrationspunkter per olastat B23-element. Utbrett lastade elements snittkrafter samt temperaturfallens snittkrafter ingår inte i denna jämförelse. RustyFEM B23 rapporterar inte tvärkraft; V kontrolleras separat analytiskt. nan betyder ej jämfört.",
              "", "Temperaturgradient genom balktvärsnitt stöds inte i den installerade RustyFEM-koden. Gradientfallet verifieras därför analytiskt i test_ram_solver.py, inte mot RustyFEM.",
              "", "Extra diagnostik: både avkylning mot axialfjäder och fri avkylning av sned stång gav konvergensfel i RustyFEM (15_avkylning_mot_fjader och 15_avkylning_sned_stang, .inp och .log). Dessa räknas inte som godkända jämförelsefall. Fall 15 i tabellen är istället en L-ram med lokala utbredda laster. Avkylning och temperatur + fjäder verifieras analytiskt i KTHBYGG."]
    (out/"rapport.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    return all(r["status"] == "PASS" for r in results)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--exe", type=Path, default=Path.home()/"Desktop/RustyFEM/target/release/rustyfem.exe")
    p.add_argument("--out", type=Path, default=ROOT/"validation/rustyfem")
    args = p.parse_args()
    raise SystemExit(0 if run(args.exe, args.out.resolve()) else 1)
