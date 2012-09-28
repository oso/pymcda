import sys
sys.path.insert(0, "..")
from mcda.types import *
import unittest

class tests_segment(unittest.TestCase):

    def test001(self):
        p1 = point(0, 0)
        p2 = point(5, 5)
        s = segment(p1, p2)
        self.assertEqual(s.y(2), 2)

    def test002(self):
        p1 = point(0, 0)
        p2 = point(5, 5)
        s = segment(p1, p2)
        self.assertRaises(ValueError, s.y, -1)

    def test003(self):
        p1 = point(0, 0)
        p2 = point(5, 5)
        s = segment(p1, p2)
        self.assertRaises(ValueError, s.y, 6)

    def test004(self):
        p1 = point(0, 0)
        p2 = point(5, 5)
        s = segment(p1, p2)
        self.assertEquals(s.y(0), 0)

    def test005(self):
        p1 = point(0, 0)
        p2 = point(5, 5)
        s = segment(p1, p2, False)
        self.assertRaises(ValueError, s.y, 0)

    def test006(self):
        p1 = point(0, 0)
        p2 = point(5, 5)
        s = segment(p1, p2)
        self.assertRaises(ValueError, s.y, 5)

    def test007(self):
        p1 = point(0, 0)
        p2 = point(5, 5)
        s = segment(p1, p2, True, True)
        self.assertEquals(s.y(5), 5)

class tests_piecewise_linear(unittest.TestCase):

    def test001(self):
        p1 = point(0, 0)
        p2 = point(1, 1)
        s1 = segment(p1, p2)

        p3 = point(1, 5)
        p4 = point(5, 9)
        s2 = segment(p3, p4)

        plf = piecewise_linear([s1, s2])
        self.assertEquals(plf.y(3), 7)

    def test002(self):
        p1 = point(0, 0)
        p2 = point(1, 1)
        s1 = segment(p1, p2)

        p3 = point(1, 5)
        p4 = point(5, 9)
        s2 = segment(p3, p4)

        plf = piecewise_linear([s1, s2])
        self.assertEquals(plf.y(0.5), 0.5)

    def test003(self):
        p1 = point(0, 0)
        p2 = point(1, 1)
        s1 = segment(p1, p2)

        p3 = point(1, 5)
        p4 = point(5, 9)
        s2 = segment(p3, p4)

        plf = piecewise_linear([s1, s2])
        self.assertEquals(plf.y(0), 0)

    def test004(self):
        p1 = point(0, 0)
        p2 = point(1, 1)
        s1 = segment(p1, p2)

        p3 = point(1, 5)
        p4 = point(5, 9)
        s2 = segment(p3, p4)

        plf = piecewise_linear([s1, s2])
        self.assertEquals(plf.y(1), 5)

    def test005(self):
        p1 = point(0, 0)
        p2 = point(1, 1)
        s1 = segment(p1, p2)

        p3 = point(1, 5)
        p4 = point(5, 9)
        s2 = segment(p3, p4)

        plf = piecewise_linear([s1, s2])
        self.assertEquals(plf.y(0), 0)

    def test006(self):
        p1 = point(0, 0)
        p2 = point(1, 1)
        s1 = segment(p1, p2)

        p3 = point(1, 5)
        p4 = point(5, 9)
        s2 = segment(p3, p4)

        plf = piecewise_linear([s1, s2])
        self.assertRaises(ValueError, plf.y, 5)

    def test007(self):
        p1 = point(0, 0)
        p2 = point(1, 1)
        s1 = segment(p1, p2)

        p3 = point(3, 7)
        p4 = point(5, 9)
        s2 = segment(p3, p4)

        plf = piecewise_linear([s1, s2])
        self.assertRaises(ValueError, plf.y, 2)

    def test008(self):
        p1 = point(0, 0)
        p2 = point(1, 1)
        s1 = segment(p1, p2)

        p3 = point(3, 7)
        p4 = point(5, 9)
        s2 = segment(p3, p4)

        plf = piecewise_linear([s1, s2])
        self.assertRaises(ValueError, plf.y, 1)

if __name__ == "__main__":
    suite = []
    suite.append(unittest.TestLoader().loadTestsFromTestCase(tests_segment))
    suite.append(unittest.TestLoader().loadTestsFromTestCase(tests_piecewise_linear))
    alltests = unittest.TestSuite(suite)
    unittest.TextTestRunner(verbosity=2).run(alltests)
