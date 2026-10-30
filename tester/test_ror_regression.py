import contextlib
import io
import math
import unittest
from unittest.mock import patch

from kthbygg import KKR, VKR


class RorRegressionTest(unittest.TestCase):
    def test_ellipse_circle_limit(self):
        for module in (KKR, VKR):
            with self.subTest(module=module.__name__):
                circle = module.cirkel(168.3, 8, print_output=False)
                ellipse = module.ellips(168.3, 168.3, 8, print_output=False)
                for ei, ci in ((0, 2), (1, 4), (2, 4), (5, 6), (6, 6),
                               (7, 7), (8, 7), (11, 1), (12, 3)):
                    self.assertAlmostEqual(ellipse[ei], circle[ci])
                # Ellipsens tunnväggiga torsionsformel är approximativ.
                self.assertAlmostEqual(ellipse[9] / circle[8], 1, delta=.01)

    def test_ellipse_axes_and_perimeter(self):
        for module in (KKR, VKR):
            with self.subTest(module=module.__name__):
                h, b, t = 200, 100, 5
                result = module.ellips(h, b, t, print_output=False)
                iy = math.pi * (b*h**3 - (b-2*t)*(h-2*t)**3) / 64
                iz = math.pi * (h*b**3 - (h-2*t)*(b-2*t)**3) / 64
                self.assertAlmostEqual(result[5], iy / (h/2))
                self.assertAlmostEqual(result[6], iz / (b/2))
                # Oberoende numerisk integration av ellipsens ytteromkrets.
                n = 20000
                perimeter = sum(math.hypot(h/2*math.sin((i+.5)*2*math.pi/n),
                                          b/2*math.cos((i+.5)*2*math.pi/n))
                                for i in range(n)) * 2*math.pi/n
                self.assertAlmostEqual(result[11]*1000/perimeter, 1, delta=.001)
                swapped = module.ellips(b, h, t, print_output=False)
                self.assertAlmostEqual(result[5], swapped[6])
                self.assertAlmostEqual(result[9], swapped[9])

    def test_invalid_geometry(self):
        for module in (KKR, VKR):
            for function, args in ((module.cirkel, (100, 60)),
                                   (module.RHS, (20, 20, 6)),
                                   (module.ellips, (100, 10, 5))):
                with self.subTest(function=function.__name__, args=args):
                    with self.assertRaises(ValueError):
                        function(*args, print_output=False)
            for function, valid in ((module.cirkel, (100, 5)),
                                    (module.RHS, (200, 100, 5)),
                                    (module.ellips, (200, 100, 5))):
                for index in range(len(valid)):
                    for bad in (0, -1, math.nan, math.inf):
                        args = list(valid)
                        args[index] = bad
                        with self.assertRaises(ValueError):
                            function(*args, print_output=False)

    def test_rhs_output_modes(self):
        for module in (KKR, VKR):
            for mode, expected in ((True, True), ("print", True), (False, False)):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    module.RHS(200, 100, 5, print_output=mode)
                self.assertEqual(bool(output.getvalue()), expected)
            with patch.object(module, "display") as display:
                module.RHS(200, 100, 5, print_output="display")
                self.assertTrue(display.call_args_list[0].args[0].data.startswith(
                    module.__name__.split(".")[-1]))


if __name__ == "__main__":
    unittest.main()
