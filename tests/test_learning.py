import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
from pymcda.generate import generate_random_electre_tri_bm_model
from pymcda.generate import generate_alternatives
from pymcda.generate import generate_random_performance_table
from pymcda.generate import generate_random_profiles
from pymcda.learning.lp_etri_weights import lp_etri_weights
from pymcda.learning.meta_etri_profiles3 import meta_etri_profiles3
from pymcda.learning.meta_etri_profiles4 import meta_etri_profiles4
from pymcda.pt_sorted import sorted_performance_table
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

class tests_meta_etri_profiles(unittest.TestCase):

    def one_test(self, seed, na, nc, ncat, max_loop, n):
        model = generate_random_electre_tri_bm_model(nc, ncat, seed)
        a = generate_alternatives(na)
        pt = generate_random_performance_table(a, model.criteria)

        aa = model.pessimist(pt)

        model2 = model.copy()
        bids = model2.categories_profiles.get_ordered_profiles()
        model2.bpt = generate_random_profiles(bids, model.criteria)

        pt_sorted = sorted_performance_table(pt)

        meta = meta_etri_profiles3(model2, pt_sorted, aa)

        for i in range(1, max_loop + 1):
            ca = meta.optimize()
            if ca == 1:
                break

        aa2 = model2.pessimist(pt)

        self.assertEqual(i, n)
        self.assertEqual(aa, aa2)

    def test001(self):
        self.one_test(0, 100, 5, 2, 100, 7)

    def test002(self):
        self.one_test(1, 100, 5, 2, 100, 5)

    def test003(self):
        self.one_test(2, 100, 5, 2, 100, 5)

    def test004(self):
        self.one_test(3, 100, 5, 2, 100, 28)

    def test005(self):
        self.one_test(4, 1000, 5, 2, 100, 51)

    def test006(self):
        self.one_test(5, 1000, 5, 2, 100, 13)

    def test007(self):
        self.one_test(6, 1000, 5, 2, 100, 10)

    def test008(self):
        self.one_test(7, 1000, 5, 2, 100, 42)

class tests_meta_etri_profiles4(unittest.TestCase):

    def one_test(self, seed, na, nc, ncat, max_loop, n):
        model = generate_random_electre_tri_bm_model(nc, ncat, seed)
        a = generate_alternatives(na)
        pt = generate_random_performance_table(a, model.criteria)

        aa = model.pessimist(pt)

        model2 = model.copy()
        bids = model2.categories_profiles.get_ordered_profiles()
        model2.bpt = generate_random_profiles(bids, model.criteria)

        pt_sorted = sorted_performance_table(pt)

        meta = meta_etri_profiles4(model2, pt_sorted, aa)

        for i in range(1, max_loop + 1):
            ca = meta.optimize()
            if ca == 1:
                break

        aa2 = model2.pessimist(pt)

        self.assertEqual(i, n)
        self.assertEqual(aa, aa2)

    def test001(self):
        self.one_test(0, 100, 5, 2, 100, 13)

    def test002(self):
        self.one_test(1, 100, 5, 2, 100, 1)

    def test003(self):
        self.one_test(2, 100, 5, 2, 100, 1)

    def test004(self):
        self.one_test(3, 100, 5, 2, 100, 4)

    def test005(self):
        self.one_test(4, 100, 10, 3, 100, 15)

    def test006(self):
        self.one_test(5, 100, 10, 3, 100, 19)

    def test007(self):
        self.one_test(6, 100, 10, 3, 100, 54)

    def test008(self):
        self.one_test(7, 100, 10, 3, 100, 22)

test_classes = [tests_lp_etri_weights, tests_meta_etri_profiles,
                tests_meta_etri_profiles4]

if __name__ == "__main__":
    suite = []
    for tclass in test_classes:
        suite.append(unittest.TestLoader().loadTestsFromTestCase(tclass))
    alltests = unittest.TestSuite(suite)
    unittest.TextTestRunner(verbosity=2).run(alltests)
