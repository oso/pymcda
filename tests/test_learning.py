from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
from pymcda.generate import generate_random_electre_tri_bm_model
from pymcda.generate import generate_alternatives
from pymcda.generate import generate_random_performance_table
from pymcda.generate import generate_random_profiles
from pymcda.learning.lp_etri_weights import lp_etri_weights
from pymcda.learning.meta_etri_profiles3 import meta_etri_profiles3
from pymcda.learning.meta_etri_profiles4 import meta_etri_profiles4
from pymcda.learning.mip_etri_global import mip_etri_global
from pymcda.learning.heur_etri_profiles import HeurEtriProfiles
from pymcda.pt_sorted import SortedPerformanceTable
from pymcda.utils import compute_ca
from pymcda.utils import add_errors_in_assignments
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

        pt_sorted = SortedPerformanceTable(pt)

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

        pt_sorted = SortedPerformanceTable(pt)

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

class tests_mip_etri_global(unittest.TestCase):

    def one_test(self, seed, na, nc, ncat, pcerrors):
        model = generate_random_electre_tri_bm_model(nc, ncat, seed)
        a = generate_alternatives(na)
        pt = generate_random_performance_table(a, model.criteria)

        aa = model.pessimist(pt)
        aa_err = aa.copy()
        add_errors_in_assignments(aa_err, model.categories, pcerrors / 100)

        model2 = model.copy()
        bids = model2.categories_profiles.get_ordered_profiles()
        model2.bpt = generate_random_profiles(bids, model.criteria)

        mip = mip_etri_global(model2, pt, aa_err)
        obj = mip.solve()

        aa2 = model2.pessimist(pt)

        ca = compute_ca(aa, aa2)
        ca2 = compute_ca(aa_err, aa2)

        self.assertEqual(ca2, obj / len(a))
        self.assertLessEqual(pcerrors / 100, ca2)

    def test001(self):
        self.one_test(0, 20, 5, 3, 0)

    def test002(self):
        self.one_test(1, 20, 5, 3, 0)

    def test003(self):
        self.one_test(2, 20, 5, 3, 0)

    def test004(self):
        self.one_test(3, 20, 5, 3, 0)

    def test005(self):
        self.one_test(4, 20, 5, 3, 50)

    def test006(self):
        self.one_test(5, 20, 5, 3, 50)

    def test007(self):
        self.one_test(6, 20, 5, 3, 50)

    def test008(self):
        self.one_test(7, 20, 5, 3, 50)

class tests_heur_etri_profiles(unittest.TestCase):

    def one_test(self, seed, na, nc, ncat, ca_expected):
        model = generate_random_electre_tri_bm_model(nc, ncat, seed)
        a = generate_alternatives(na)
        pt = generate_random_performance_table(a, model.criteria)

        aa = model.pessimist(pt)

        pt_sorted = SortedPerformanceTable(pt)
        heur = HeurEtriProfiles(model, pt_sorted, aa)
        heur.solve()

        aa2 = model.pessimist(pt)

        ca = compute_ca(aa, aa2)

        self.assertEqual(ca, ca_expected)

    def test001(self):
        self.one_test(0, 1000, 10, 3, 0.999)

    def test002(self):
        self.one_test(1, 1000, 10, 3, 0.736)

    def test003(self):
        self.one_test(2, 1000, 10, 3, 0.608)

    def test004(self):
        self.one_test(3, 1000, 10, 3, 0.987)

test_classes = [tests_lp_etri_weights, tests_meta_etri_profiles,
                tests_meta_etri_profiles4, tests_mip_etri_global,
                tests_heur_etri_profiles]

if __name__ == "__main__":
    suite = []
    for tclass in test_classes:
        suite.append(unittest.TestLoader().loadTestsFromTestCase(tclass))
    alltests = unittest.TestSuite(suite)
    unittest.TextTestRunner(verbosity=2).run(alltests)
