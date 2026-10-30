import unittest
import numpy as np
from kthbygg.balk import Balk
from kthbygg.ram import Ram


class SolverTest(unittest.TestCase):
    def test_cantilever_rotation(self):
        for angle in (0, .5, np.pi/2, 2.4):
            c, s = np.cos(angle), np.sin(angle)
            r = Ram(EI=40000, EA=200000).nod(1, 0, 0).nod(2, 4*c, 4*s)
            r.stång(1, 1, 2).stöd(1, "fast").nodlast(2, Fx=12*s, Fy=-12*c)
            out = r.lös()
            tip = out.förskjutningar[2]
            self.assertAlmostEqual(-s*tip["ux"]+c*tip["uy"], -12*4**3/(3*40000))
            self.assertAlmostEqual(out.M(1, 0), -48)

    def test_thermal(self):
        for fixed in (False, True):
            b = Balk(4, EI=40000, EA=200000).stöd(0, "fast")
            if fixed:
                b.stöd(4, "fast")
            b.temperatur(30)
            r = b.lös()
            self.assertAlmostEqual(r.N(2), -72 if fixed else 0)
            self.assertAlmostEqual(r.förskjutningar[4]["u"], 0 if fixed else .00144)

    def test_gradient(self):
        b = Balk(4, EI=40000, EA=200000).stöd(0, "fast").temperatur(gradient=50)
        r = b.lös()
        self.assertAlmostEqual(r.w(4), -12e-6*50*4**2/2)
        self.assertAlmostEqual(r.M(2), 0)

    def test_stepped_stiffness(self):
        b = Balk(4, EI=40000, EA=200000).stöd(0, "fast")
        b.sektion(2, 4, EI=20000, EA=100000).punktlast(4, 12, H=10)
        r = b.lös()
        self.assertAlmostEqual(r.w(4), 12*((64-8)/40000+8/20000)/3)
        self.assertAlmostEqual(r.förskjutningar[4]["u"], 10*(2/200000+2/100000))

    def test_spring(self):
        b = Balk(4, EI=40000).stöd(0, "fast").fjäderstöd(4, ky=1000).punktlast(4, 12)
        r = b.lös()
        self.assertAlmostEqual(r.w(4), 12/(3*40000/4**3+1000))
        self.assertAlmostEqual(sum(v["V"] for v in r.reaktioner.values()), 12)

    def test_ram_thermal_and_spring(self):
        r = Ram(EI=40000, EA=200000).nod(1, 0, 0).nod(2, 4, 0)
        r.stång(1, 1, 2).stöd(1, "fast").fjäderstöd(2, kx=50000)
        r.temperatur(1, 30, gradient=50)
        out = r.lös()
        self.assertAlmostEqual(out.förskjutningar[2]["ux"], .00072)
        self.assertAlmostEqual(out.N(1, 2), -36)
        self.assertAlmostEqual(out.w(1, 4), -.0048)

    def test_instability(self):
        r = Ram(EI=40000, EA=200000).nod(1, 0, 0).nod(2, 4, 0).stång(1, 1, 2)
        with self.assertRaises(ValueError):
            r.lös()

    def test_cooling_spring(self):
        for temperature in (-25, 30):
            r = Ram(EI=40000, EA=200000).nod(1, 0, 0).nod(2, 4, 0).stång(1, 1, 2)
            r.stöd(1, "fast").fjäderstöd(2, kx=50000).temperatur(1, temperature)
            out = r.lös()
            u = 12e-6*temperature*4/2
            self.assertAlmostEqual(out.förskjutningar[2]["ux"], u)
            self.assertAlmostEqual(out.N(1, 2), -50000*u)
            self.assertAlmostEqual(out.reaktioner[2]["H"], -50000*u)

    def test_balk_ram_combined(self):
        b = Balk(4, EI=40000, EA=200000).stöd(0, "fast").stöd(4, "rull")
        b.sektion(2, 4, EI=20000, EA=100000).temperatur(30, gradient=50)
        b.fjäderstöd(2, ky=1000, kx=5000, kr=200).utbredd_last(2, q2=8).punktlast(2, 4, 8)
        rr = Ram(EI=40000, EA=200000).nod(1, 0, 0).nod(2, 2, 0).nod(3, 4, 0)
        rr.stång(1, 1, 2).stång(2, 2, 3, EI=20000, EA=100000).stöd(1, "fast").stöd(3, "rull")
        rr.temperatur(1, 30, gradient=50).temperatur(2, 30, gradient=50)
        rr.fjäderstöd(2, ky=1000, kx=5000, kr=200).utbredd_last(1, 2, 5).utbredd_last(2, 5, 8).punktlast(2, 4, 8)
        br, r = b.lös(), rr.lös()
        for node, x in ((1, 0), (2, 2), (3, 4)):
            self.assertAlmostEqual(br.förskjutningar[x]["u"], r.förskjutningar[node]["ux"])
            self.assertAlmostEqual(br.förskjutningar[x]["w"], -r.förskjutningar[node]["uy"])
            for key in ("H", "V", "M"):
                self.assertAlmostEqual(br.reaktioner[x][key], r.reaktioner[node][key])
        for element, offset in ((1, 0), (2, 2)):
            for x in (.3, 1., 1.9):
                for name in ("N", "V", "M", "w"):
                    self.assertAlmostEqual(getattr(br, name)(offset+x), getattr(r, name)(element, x))

    def test_distributed_and_hinge_regression(self):
        b = Balk(4, EI=40000).stöd(0, "led").stöd(4, "rull").utbredd_last(6)
        r = b.lös()
        self.assertAlmostEqual(r.M(2), 12)
        self.assertAlmostEqual(r.w(2), 5*6*4**4/(384*40000))
        b = Balk(6, EI=40000).stöd(0, "fast").stöd(6, "rull").led(3).punktlast(4, 12)
        self.assertAlmostEqual(b.lös().M(3), 0)


if __name__ == "__main__":
    unittest.main()
