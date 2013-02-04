import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
from pymcda.generate import generate_random_electre_tri_bm_model
from pymcda.generate import generate_alternatives
from pymcda.generate import generate_random_performance_table
from pymcda.learning.lp_etri_weights import lp_etri_weights
import unittest

class tests_lp_etri_weights(unittest.TestCase):

    def one_test(self, seed, ncrit, ncat, na):
        model = generate_random_electre_tri_bm_model(ncrit, ncat, seed)
        a = generate_alternatives(na)
        pt = generate_random_performance_table(a, model.criteria)

        aa = model.pessimist(pt)

        model2 = model.copy()
        model2.cvs = None

        lp_weights = lp_etri_weights(model2, pt, aa)
        lp_weights.solve()

        aa2 = model2.pessimist(pt)

        self.assertEqual(aa, aa2)

    def test001(self):
        for i in range(10):
            self.one_test(i, 10, 2, 100)

    def test002(self):
        for i in range(10):
            self.one_test(i, 10, 3, 100)

    def test003(self):
        for i in range(10):
            self.one_test(i, 10, 4, 100)

    def test004(self):
        for i in range(10):
            self.one_test(i, 10, 5, 100)

    def test005(self):
        for i in range(10):
            self.one_test(i, 10, 5, 1000)

test_classes = [tests_lp_etri_weights]

if __name__ == "__main__":
    suite = []
    for tclass in test_classes:
        suite.append(unittest.TestLoader().loadTestsFromTestCase(tclass))
    alltests = unittest.TestSuite(suite)
    unittest.TextTestRunner(verbosity=2).run(alltests)
