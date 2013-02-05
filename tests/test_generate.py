import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
from pymcda.generate import *
import unittest

class tests_generate(unittest.TestCase):

    def test001_generate_alternative(self):
        a = generate_alternatives(100)
        self.assertEqual(len(a), 100)

    def test002_generate_criteria(self):
        c = generate_criteria(10)
        self.assertEqual(len(c), 10)

    def test003_generate_performance_table(self):
        a = generate_alternatives(100)
        c = generate_criteria(10)
        pt = generate_random_performance_table(a, c)

        self.assertEqual(len(pt), 100)
        self.assertEqual(len(pt['a1'].performances), 10)

    def test004_generate_performance_table_randomness(self):
        a = generate_alternatives(100)
        c = generate_criteria(10)
        pt = generate_random_performance_table(a, c, 0)
        pt2 = generate_random_performance_table(a, c, 0)
        pt3 = generate_random_performance_table(a, c)

        self.assertEqual(pt, pt2)
        self.assertNotEqual(pt, pt3)

    def test005_generate_random_criteria_weights(self):
        c = generate_criteria(10)
        cw = generate_random_criteria_weights(c)

        self.assertEqual(len(cw), 10)

    def test006_generate_random_criteria_weights_randomness(self):
        c = generate_criteria(10)
        cw = generate_random_criteria_weights(c, 0)
        cw2 = generate_random_criteria_weights(c, 0)
        cw3 = generate_random_criteria_weights(c)

        self.assertEqual(cw, cw2)
        self.assertNotEqual(cw, cw3)

    def test007_generate_random_criteria_values(self):
        c = generate_criteria(10)
        cv = generate_random_criteria_weights(c)

        self.assertEqual(len(cv), 10)

    def test008_generate_random_criteria_values_randomness(self):
        c = generate_criteria(10)
        cv = generate_random_criteria_weights(c, 0)
        cv2 = generate_random_criteria_weights(c, 0)
        cv3 = generate_random_criteria_weights(c)

        self.assertEqual(cv, cv2)
        self.assertNotEqual(cv, cv3)

    def test009_generate_categories(self):
        c = generate_categories(10)
        self.assertEqual(len(c), 10)

    def test010_generate_random_electre_tri_bm_model(self):
        m = generate_random_electre_tri_bm_model(10, 5, 0)

        self.assertEqual(len(m.criteria), 10)
        self.assertEqual(len(m.categories), 5)

    def test011_generate_random_electre_tri_bm_model(self):
        m = generate_random_electre_tri_bm_model(10, 5, 0)
        m2 = generate_random_electre_tri_bm_model(10, 5, 0)
        m3 = generate_random_electre_tri_bm_model(10, 5)

        self.assertEqual(m, m2)
        self.assertNotEqual(m2, m3)

test_classes = [tests_generate]

if __name__ == "__main__":
    suite = []
    for tclass in test_classes:
        suite.append(unittest.TestLoader().loadTestsFromTestCase(tclass))
    alltests = unittest.TestSuite(suite)
    unittest.TextTestRunner(verbosity=2).run(alltests)
