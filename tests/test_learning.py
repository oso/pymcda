from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
from pymcda.types import AlternativePerformances, PerformanceTable
from pymcda.types import CriteriaSet
from pymcda.types import CriteriaValues, CriterionValue
from pymcda.uta import AVFSort
from pymcda.electre_tri import MRSort
from pymcda.generate import generate_random_mrsort_model
from pymcda.generate import generate_alternatives
from pymcda.generate import generate_categories
from pymcda.generate import generate_categories_profiles
from pymcda.generate import generate_criteria
from pymcda.generate import generate_random_performance_table
from pymcda.generate import generate_random_profiles
from pymcda.generate import generate_random_avfsort_model
from pymcda.learning.lp_mrsort_weights import LpMRSortWeights
from pymcda.learning.heur_mrsort_profiles3 import MetaMRSortProfiles3
from pymcda.learning.heur_mrsort_profiles4 import MetaMRSortProfiles4
from pymcda.learning.mip_mrsort import MipMRSort
from pymcda.learning.heur_mrsort_init_profiles import HeurMRSortInitProfiles
from pymcda.learning.lp_avfsort import LpAVFSort
from pymcda.learning.lp_mrsort_mobius import LpMRSortMobius
from pymcda.pt_sorted import SortedPerformanceTable
from pymcda.utils import compute_ca
from pymcda.utils import add_errors_in_assignments
import unittest

class tests_lp_mrsort_weights(unittest.TestCase):

    def one_test(self, seed, ncrit, ncat, na):
        model = generate_random_mrsort_model(ncrit, ncat, seed)
        a = generate_alternatives(na)
        pt = generate_random_performance_table(a, model.criteria)

        aa = model.pessimist(pt)

        model2 = model.copy()
        model2.cvs = None

        lp_weights = LpMRSortWeights(model2, pt, aa)
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

    def one_test2(self, seed, ncrit, ncat, na):
        model = generate_random_mrsort_model(ncrit, ncat, seed)
        a = generate_alternatives(na)
        pt = generate_random_performance_table(a, model.criteria)

        aa = model.pessimist(pt)

        model2 = model.copy()
        model2.cvs = None

        lp_weights = LpMRSortWeights(model2, pt, aa)

        bids = model.categories_profiles.get_ordered_profiles()
        bpt = generate_random_profiles(bids, model.criteria)

        model.bpt = model2.bpt = bpt
        aa = model.pessimist(pt)

        lp_weights.aa_ori = aa
        lp_weights.update_linear_program()

        lp_weights.solve()

        aa2 = model2.pessimist(pt)

        self.assertEqual(aa, aa2)

    def test006(self):
        for i in range(10):
            self.one_test2(i, 10, 3, 1000)

    def test007(self):
        for i in range(10):
            self.one_test2(i, 10, 3, 100)

    def test008(self):
        for i in range(10):
            self.one_test2(i, 10, 4, 100)

    def test009(self):
        for i in range(10):
            self.one_test2(i, 10, 5, 100)

    def test010(self):
        for i in range(10):
            self.one_test2(i, 10, 5, 1000)

class tests_heur_mrsort_profiles(unittest.TestCase):

    def one_test(self, seed, na, nc, ncat, max_loop, n):
        model = generate_random_mrsort_model(nc, ncat, seed)
        a = generate_alternatives(na)
        pt = generate_random_performance_table(a, model.criteria)

        aa = model.pessimist(pt)

        model2 = model.copy()
        bids = model2.categories_profiles.get_ordered_profiles()
        model2.bpt = generate_random_profiles(bids, model.criteria)

        pt_sorted = SortedPerformanceTable(pt)

        meta = MetaMRSortProfiles3(model2, pt_sorted, aa)

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

class tests_heur_mrsort_profiles4(unittest.TestCase):

    def one_test(self, seed, na, nc, ncat, max_loop, n):
        model = generate_random_mrsort_model(nc, ncat, seed)
        a = generate_alternatives(na)
        pt = generate_random_performance_table(a, model.criteria)

        aa = model.pessimist(pt)

        model2 = model.copy()
        bids = model2.categories_profiles.get_ordered_profiles()
        model2.bpt = generate_random_profiles(bids, model.criteria)

        pt_sorted = SortedPerformanceTable(pt)

        meta = MetaMRSortProfiles4(model2, pt_sorted, aa)

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
        self.one_test(4, 100, 10, 3, 100, 21)

    def test006(self):
        self.one_test(5, 100, 10, 3, 100, 19)

    def test007(self):
        self.one_test(6, 100, 10, 3, 100, 78)

    def test008(self):
        self.one_test(7, 100, 10, 3, 100, 17)

class tests_mip_mrsort(unittest.TestCase):

    def one_test(self, seed, na, nc, ncat, pcerrors):
        model = generate_random_mrsort_model(nc, ncat, seed)
        a = generate_alternatives(na)
        pt = generate_random_performance_table(a, model.criteria)

        aa = model.pessimist(pt)
        aa_err = aa.copy()
        add_errors_in_assignments(aa_err, model.categories, pcerrors / 100)

        model2 = model.copy()
        model2.bpt = None
        model2.cv = None
        model2.lbda = None

        mip = MipMRSort(model2, pt, aa_err)
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

class tests_heur_mrsort_init_profiles(unittest.TestCase):

    def one_test(self, seed, na, nc, ncat, ca_expected):
        model = generate_random_mrsort_model(nc, ncat, seed)
        a = generate_alternatives(na)
        pt = generate_random_performance_table(a, model.criteria)

        aa = model.pessimist(pt)

        pt_sorted = SortedPerformanceTable(pt)
        heur = HeurMRSortInitProfiles(model, pt_sorted, aa)
        heur.solve()

        aa2 = model.pessimist(pt)

        ca = compute_ca(aa, aa2)

        self.assertEqual(ca, ca_expected)

    def test001(self):
        self.one_test(0, 1000, 10, 3, 0.999)

    def test002(self):
        self.one_test(1, 1000, 10, 3, 0.723)

    def test003(self):
        self.one_test(2, 1000, 10, 3, 0.607)

    def test004(self):
        self.one_test(3, 1000, 10, 3, 0.986)

class tests_lp_avfsort(unittest.TestCase):

    def one_test(self, seed, na, nc, ncat, ns):
        u = generate_random_avfsort_model(nc, ncat, ns, ns, seed)
        a = generate_alternatives(na)
        pt = generate_random_performance_table(a, u.criteria)

        aa = u.get_assignments(pt)

        css = CriteriaValues([])
        for cf in u.cfs:
            cs = CriterionValue(cf.id, len(cf.function))
            css.append(cs)

        cat = u.cat_values.to_categories()
        lp = LpAVFSort(u.criteria, css, cat, pt.get_worst(u.criteria),
                       pt.get_best(u.criteria))
        obj, cvs, cfs, catv = lp.solve(aa, pt)

        u2 = AVFSort(u.criteria, cvs, cfs, catv)
        aa2 = u2.get_assignments(pt)

        self.assertEqual(aa, aa2)

    def test001(self):
        for i in range(10):
            self.one_test(i, 1000, 10, 3, 1)

    def test002(self):
        for i in range(10):
            self.one_test(i, 1000, 10, 3, 2)

    def test003(self):
        for i in range(10):
            self.one_test(i, 1000, 10, 3, 3)

    def test004(self):
        for i in range(10):
            self.one_test(i, 1000, 10, 3, 4)

    def test005(self):
        for i in range(10):
            self.one_test(i, 1000, 10, 3, 5)

class tests_lp_mrsort_choquet(unittest.TestCase):

    def test001(self):
        c = generate_criteria(3)
        cat = generate_categories(3)
        cps = generate_categories_profiles(cat)

        bp1 = AlternativePerformances('b1',
                                      {'c1': 0.75, 'c2': 0.75, 'c3': 0.75})
        bp2 = AlternativePerformances('b2',
                                      {'c1': 0.25, 'c2': 0.25, 'c3': 0.25})
        bpt = PerformanceTable([bp1, bp2])

        cv1 = CriterionValue('c1', 0.2)
        cv2 = CriterionValue('c2', 0.2)
        cv3 = CriterionValue('c3', 0.2)
        cv12 = CriterionValue(CriteriaSet('c1', 'c2'), -0.1)
        cv23 = CriterionValue(CriteriaSet('c2', 'c3'), 0.2)
        cv13 = CriterionValue(CriteriaSet('c1', 'c3'), 0.3)
        cvs = CriteriaValues([cv1, cv2, cv3, cv12, cv23, cv13])

        lbda = 0.6

        model = MRSort(c, cvs, bpt, lbda, cps)

        ap1 = AlternativePerformances('a1', {'c1': 0.3, 'c2': 0.3, 'c3': 0.3})
        ap2 = AlternativePerformances('a2', {'c1': 0.8, 'c2': 0.8, 'c3': 0.8})
        ap3 = AlternativePerformances('a3', {'c1': 0.3, 'c2': 0.3, 'c3': 0.1})
        ap4 = AlternativePerformances('a4', {'c1': 0.3, 'c2': 0.1, 'c3': 0.3})
        ap5 = AlternativePerformances('a5', {'c1': 0.1, 'c2': 0.3, 'c3': 0.3})
        ap6 = AlternativePerformances('a6', {'c1': 0.8, 'c2': 0.8, 'c3': 0.1})
        ap7 = AlternativePerformances('a7', {'c1': 0.8, 'c2': 0.1, 'c3': 0.8})
        ap8 = AlternativePerformances('a8', {'c1': 0.1, 'c2': 0.8, 'c3': 0.8})
        pt = PerformanceTable([ap1, ap2, ap3, ap4, ap5, ap6, ap7, ap8])

        aa = model.get_assignments(pt)

        model2 = MRSort(c, None, bpt, None, cps)
        lp = LpMRSortMobius(model2, pt, aa)
        obj = lp.solve()

        aa2 = model.get_assignments(pt)

        self.assertEqual(obj, 0)
        self.assertEqual(aa, aa2)


test_classes = [tests_lp_mrsort_weights, tests_heur_mrsort_profiles,
                tests_heur_mrsort_profiles4, tests_mip_mrsort,
                tests_heur_mrsort_init_profiles, tests_lp_avfsort,
                tests_lp_mrsort_choquet]

if __name__ == "__main__":
    suite = []
    for tclass in test_classes:
        suite.append(unittest.TestLoader().loadTestsFromTestCase(tclass))
    alltests = unittest.TestSuite(suite)
    unittest.TextTestRunner(verbosity=2).run(alltests)
