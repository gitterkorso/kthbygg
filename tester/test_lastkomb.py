import unittest
import contextlib
import io

from kthbygg import Lastkomb as L


# Bildens andra tabell. Trafik, vind och temperatur har två alternativ var.
G_ALTERNATIV = [
    dict(namn="Egentyngd", effekt=[30, 20], gamma_sup=1.35, gamma_inf=1, xi=.89),
    dict(namn="Sättning", effekt=[10, -5], gamma_sup=1.2, gamma_inf=0, xi=1),
]
Q_ALTERNATIV = [
    dict(namn="Trafik 1", effekt=[25, 10], gamma=1.35, psi_0=.4, grupp="trafik"),
    dict(namn="Trafik 2", effekt=[15, 12], gamma=1.35, psi_0=.4, grupp="trafik"),
    dict(namn="Vind 1", effekt=[5, 2], gamma=1.5, psi_0=.3, grupp="vind"),
    dict(namn="Vind 2", effekt=[-5, -2], gamma=1.5, psi_0=.3, grupp="vind"),
    dict(namn="Temperatur 1", effekt=[-3, 2], gamma=1.5, psi_0=.6, grupp="temperatur"),
    dict(namn="Temperatur 2", effekt=[3, -2], gamma=1.5, psi_0=.6, grupp="temperatur"),
]


class LastkombTest(unittest.TestCase):
    def test_alternative_loads_with_paired_effects(self):
        fall = L.lastkomb_610_fall(G_ALTERNATIV, Q_ALTERNATIV)
        for f in fall:
            g1, g2, t1, t2, w1, w2, h1, h2 = f["faktorer"]
            self.assertEqual(t1 * t2, 0)
            self.assertEqual(w1 * w2, 0)
            self.assertEqual(h1 * h2, 0)
            self.assertAlmostEqual(f["effekt"][0],
                                   30*g1 + 10*g2 + 25*t1 + 15*t2 + 5*w1 - 5*w2 - 3*h1 + 3*h2)
            self.assertAlmostEqual(f["effekt"][1],
                                   20*g1 - 5*g2 + 10*t1 + 12*t2 + 2*w1 - 2*w2 + 2*h1 - 2*h2)
        max_m = max(fall, key=lambda f: f["effekt"][0])
        max_n = max(fall, key=lambda f: f["effekt"][1])
        for actual, expected in zip(max_m["effekt"], [86.745, 30.63]):
            self.assertAlmostEqual(actual, expected)
        for actual, expected in zip(max_n["effekt"], [55.845, 42.93]):
            self.assertAlmostEqual(actual, expected)
        self.assertEqual(max_m["huvudlast"], 0)
        self.assertEqual(max_n["huvudlast"], 1)
        self.assertAlmostEqual(min(f["effekt"][0] for f in fall), 19.8)
        self.assertAlmostEqual(min(f["effekt"][1] for f in fall), 9.2)

    def test_moment_and_normal_force_load_table(self):
        # Self-weight; Q: traffic, wind, thermal. gamma_G=1.35,
        # gamma_Q=1.5, xi=0.89, gamma_d=1. Original 6.10a.
        cases = (
            ("M [kNm]", 150, [225, 10, 35], 373.5,
             [553.725, 361.725, 372.225]),
            ("N [kN]", 100, [55, 2, 70], 231.9,
             [266.55, 219.15, 259.05]),
        )
        for name, g, q, expected_a, expected_b in cases:
            with self.subTest(effect=name):
                r = L.lastkomb(g, q, [.4, .3, .6], variabel_i_610a=True)
                self.assertAlmostEqual(r["6.10a"], expected_a)
                for actual, expected in zip(r["6.10b_alla"], expected_b):
                    self.assertAlmostEqual(actual, expected)
                self.assertEqual(len(r["6.10b_alla"]), 3)
                self.assertEqual(r["kombination"], "6.10b")
                self.assertEqual(r["huvudlast"], 0)
                self.assertAlmostEqual(r["dimensionerande"], expected_b[0])

    def test_classes(self):
        for klass, faktor in ((1, .83), (2, .91), (3, 1.0)):
            self.assertEqual(L.γ_d(klass), faktor)
        for klass in (0, 4, None, True, "2", [1], float("nan")):
            with self.assertRaises(ValueError):
                L.γ_d(klass)

    def test_permanent(self):
        r = L.lastkomb(10)
        self.assertAlmostEqual(r["dimensionerande"], 13.5)
        self.assertEqual(r["kombination"], "6.10a")
        self.assertIsNone(r["huvudlast"])

    def test_leading_loads(self):
        r = L.lastkomb(10, [2, 3], [.7, .5])
        self.assertAlmostEqual(r["6.10a"], 13.5)
        self.assertAlmostEqual(r["6.10b_alla"][0], 17.265)
        self.assertAlmostEqual(r["6.10b_alla"][1], 18.615)
        self.assertEqual(r["huvudlast"], 1)
        self.assertAlmostEqual(r["dimensionerande"], 18.615)

    def test_original_expression(self):
        r = L.lastkomb(5.7, 2, .7, 1, variabel_i_610a=True)
        self.assertAlmostEqual(r["6.10a"], 8.12985)
        self.assertAlmostEqual(r["6.10b"], 8.1742965)

    def test_favourable(self):
        r = L.lastkomb([10, -4], [2, -8], .7, 2)
        self.assertAlmostEqual(r["6.10a"], 8.285)
        self.assertAlmostEqual(r["6.10b"], 9.66365)

    def test_invalid(self):
        for kwargs in ({"G": float("nan")}, {"G": [[1]]},
                       {"G": 1, "Q": [1, 2], "psi_0": [.7, .6, .5]},
                       {"G": 1, "Q": 2}, {"G": 1, "Q": float("inf"), "psi_0": .7},
                       {"G": 1, "Q": 2, "psi_0": 1.1},
                       {"G": 1, "variabel_i_610a": "False"}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                L.lastkomb(**kwargs)

    def test_service_combinations(self):
        # G=10, P=-1, Q=[2,4]. Båda huvudlastfallen räknas för hand.
        r = L.lastkomb(10, [2, 4], [.7, .6], kombination="6.14", P=-1)
        self.assertEqual([f["värde"] for f in r["lastfall"]], [13.4, 14.4])
        self.assertEqual(r["huvudlast"], 1)
        r = L.lastkomb(10, [2, 4], kombination="6.15", P=-1,
                       psi_1=[.5, .2], psi_2=[.3, .1])
        self.assertAlmostEqual(r["lastfall"][0]["värde"], 10.4)
        self.assertAlmostEqual(r["lastfall"][1]["värde"], 10.4)
        r = L.lastkomb(10, [2, 4], kombination="6.16", P=-1, psi_2=[.3, .1])
        self.assertEqual(r["dimensionerande"], 10)
        self.assertIsNone(r["huvudlast"])

    def test_accidental_and_seismic(self):
        for val, expected in (("psi_1", 15.4), ("psi_2", 15)):
            r = L.lastkomb(10, [2, 4], kombination="6.11", P=-1, A_d=5,
                           psi_1=[.5, .2], psi_2=[.3, .1], olycka_huvudlast=val)
            self.assertAlmostEqual(r["dimensionerande"], expected)
        r = L.lastkomb(10, [2, 4], kombination="6.12b", P=-1, A_Ed=-5,
                       psi_2=[.3, .1])
        self.assertEqual(r["dimensionerande"], 5)
        self.assertIsNone(r["huvudlast"])

    def test_new_permanent_and_favourable(self):
        for nummer in ("6.14", "6.15", "6.16"):
            self.assertEqual(L.lastkomb([10, -4], kombination=nummer)["dimensionerande"], 6)
        r = L.lastkomb([10, -4], [-8, 2], kombination="6.16", psi_2=.3)
        self.assertAlmostEqual(r["dimensionerande"], 6.6)

    def test_serviceability_check(self):
        self.assertTrue(L.kontroll_613(10, 10)["uppfyllt"])
        self.assertFalse(L.kontroll_613(11, 10)["uppfyllt"])
        self.assertTrue(L.kontroll_613(0, 0)["uppfyllt"])
        self.assertFalse(L.kontroll_613(1, 0)["uppfyllt"])
        for ed, cd in ((-1, 10), (1, -1), (float("nan"), 1)):
            with self.assertRaises(ValueError):
                L.kontroll_613(ed, cd)

    def test_new_validation(self):
        for kwargs in ({"kombination": "6.13"}, {"kombination": "6.12"},
                       {"kombination": "6.11", "A_d": 1},
                       {"kombination": "6.16", "Q": 2},
                       {"kombination": "6.15", "Q": 2, "psi_1": .5, "psi_2": 1.1},
                       {"kombination": "6.14", "A_d": 3},
                       {"kombination": "6.16", "säkerhetsklass": 1}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                L.lastkomb(10, **kwargs)

    def test_new_formula_output(self):
        for nummer, extra in (("6.11", {"A_d": 5, "olycka_huvudlast": "psi_1"}),
                              ("6.12", {"A_Ed": 5}), ("6.14", {}),
                              ("6.15", {}), ("6.16", {})):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                L.skriv_formler(10, [2, 4], .7, kombination=nummer, psi_1=.5,
                                psi_2=.3, enhet="kN/m", **extra)
            self.assertIn(nummer, output.getvalue())
            self.assertIn("[kN/m]", output.getvalue())
            self.assertIn("Dimensionerande E_d", output.getvalue())


if __name__ == "__main__":
    unittest.main()
