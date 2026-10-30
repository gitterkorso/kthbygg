import contextlib
import io
import unittest

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from kthbygg.balk import Balk
from kthbygg.ram import Ram


class BalkRamRegressionTest(unittest.TestCase):
    def tearDown(self):
        plt.close("all")

    def test_close_zero_loads(self):
        b = Balk(4, EI=40000).stöd(0, "fast").punktlast(4, 12)
        b.punktlast(2, 0).punktlast(2.0000004, 0)
        r = b.lös()
        self.assertAlmostEqual(r.w(4), 12*4**3/(3*40000))
        self.assertAlmostEqual(r.reaktioner[0]["M"], 48)

    def test_close_nonzero_loads(self):
        for unit in (1, 1000):
            for gap in (1e-4, 4e-7):
                with self.subTest(unit=unit, gap=gap):
                    L, EI = 4*unit, 40000*unit**2
                    loads = [(L, 12), (2*unit, 3), ((2+gap)*unit, 5)]
                    b = Balk(L, EI=EI).stöd(0, "fast")
                    for x, P in loads:
                        b.punktlast(x, P)
                    r = b.lös()
                    expected = sum(P*a*a*(3*L-a)/(6*EI) for a, P in loads)
                    self.assertAlmostEqual(r.w(L)/expected, 1, places=7)
                    self.assertAlmostEqual(r.reaktioner[0]["V"], 20, places=6)
                    self.assertAlmostEqual(r.M(0)/sum(-P*x for x, P in loads), 1, places=7)
                    self.assertAlmostEqual(r.V((2+gap/2)*unit), 17, places=6)

    def test_mechanisms_still_rejected(self):
        for b in (Balk(4).stöd(0, "led"),
                  Balk(4).stöd(0, "led").led(2).stöd(4, "rull"),
                  Balk(4).stöd(0, "fast").led(2)):
            with self.assertRaisesRegex(ValueError, "mekanism"):
                b.lös()

    def test_total_indeterminacy(self):
        for left, right, expected in (("led", "rull", 0), ("led", "led", 1),
                                      ("fast", "rull", 1), ("fast", "fast", 3)):
            r = Balk(4).stöd(0, left).stöd(4, right).lös()
            self.assertEqual(r.grad, expected)
        r = Balk(4).stöd(0, "led").stöd(4, "led").lös()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            r.skriv()
        self.assertIn("1 gång statiskt obestämd", output.getvalue())
        r = Balk(4).stöd(0, "fast").fjäderstöd(4, kx=10).lös()
        self.assertEqual(r.grad, 1)

    def test_element_deformation(self):
        ram = Ram(EI=40000, EA=200000).nod(1, 0, 0).nod(2, 0, 4)
        ram.stång(1, 1, 2).stöd(1, "fast").nodlast(2, Fx=12, Fy=10)
        r = ram.lös().elementresultat(1)
        fig = r.rita_deformerad(skala=1)
        line = next(line for line in fig.axes[0].lines if line.get_linestyle() == "--")
        # Elementbilden använder lokala koordinater och längden 900 ritningsenheter.
        np.testing.assert_allclose([line.get_xdata()[-1], line.get_ydata()[-1]],
                                   [(4+10*4/200000)*225, -12*4**3/(3*40000)*225])

    def test_deformation_units(self):
        ram = Ram(EI=40000, EA=200000).nod(1, 0, 0).nod(2, 4, 0)
        ram.stång(1, 1, 2).stöd(1, "fast").nodlast(2, F=10, vinkel=-30)
        for fig in (ram.rita_modell(deformerad=True, langdenhet="mm", kraftenhet="N"),
                    ram.lös().rita_deformerad(langdenhet="mm", kraftenhet="N")):
            self.assertEqual(fig.axes[0].get_xlabel(), "x [mm]")
            self.assertEqual(fig.axes[0].get_ylabel(), "y [mm]")
            self.assertTrue(any("N" in text.get_text() for text in fig.axes[0].texts))


if __name__ == "__main__":
    unittest.main()
