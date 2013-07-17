import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
import random
from pymcda.electre_tri import ElectreTri, MRSort
from pymcda.generate import generate_alternatives, generate_criteria
from pymcda.generate import generate_random_mrsort_model
from pymcda.generate import generate_random_performance_table
from pymcda.generate import generate_categories
from pymcda.generate import generate_categories_profiles
from pymcda.types import CriterionValue, CriteriaValues
from pymcda.types import AlternativePerformances, PerformanceTable
from pymcda.utils import add_errors_in_assignments
import unittest

def compare_assignments(assignments, expected_assignments):
        ok = 1
        for aa in expected_assignments:
            key = aa.id
            if expected_assignments(key) != assignments(key):
                print("Pessimits assignment of %s mismatch (%s <> %s)" %
                      (str(key), assignments(key),
                       expected_assignments(key)))
                ok=0

        return ok

class tests_electre_tri(unittest.TestCase):

    def test001_test_pessimist_loulouka(self):
        """ Loulouka - Pessimist """
        from datasets.loulouka import c, cv, ptb, lbda, pt, aap, cps
        etri = ElectreTri(c, cv, ptb, lbda, cps).pessimist(pt)
        ok = compare_assignments(etri, aap)
        self.assertEqual(ok, 1, "One or more alternatives were wrongly \
                         assigned")

    def test002_test_pessimist_ticino(self):
        """ Ticino - Pessimist """
        from datasets.ticino import c, cv, ptb, lbda, pt, aap, cps
        etri = ElectreTri(c, cv, ptb, lbda, cps).pessimist(pt)
        ok = compare_assignments(etri, aap)
        self.assertEqual(ok, 1, "One or more alternatives were wrongly \
                         assigned")


    def test003_test_optimist_loulouka(self):
        """ Loulouka - Optimist """
        from datasets.loulouka import c, cv, ptb, lbda, pt, aao, cps
        etri = ElectreTri(c, cv, ptb, lbda, cps).optimist(pt)
        ok = compare_assignments(etri, aao)
        self.assertEqual(ok, 1, "One or more alternatives were wrongly \
                         assigned")

    def test004_test_optimist_ticino(self):
        """ Ticino - Optimist """
        from datasets.ticino import c, cv, ptb, lbda, pt, aao, cps
        etri = ElectreTri(c, cv, ptb, lbda, cps).optimist(pt)
        ok = compare_assignments(etri, aao)
        self.assertEqual(ok, 1, "One or more alternatives were wrongly \
                         assigned")

class tests_mrsort(unittest.TestCase):

    def setUp(self):
        if not hasattr(self, 'i'):
            self.i = 0
        else:
            self.i += 1

        random.seed(self.i)

    def test001(self):
        random.seed(1)
        c = generate_criteria(4)

        cv1 = CriterionValue('c1', 0.25)
        cv2 = CriterionValue('c2', 0.25)
        cv3 = CriterionValue('c3', 0.25)
        cv4 = CriterionValue('c4', 0.25)
        cv = CriteriaValues([cv1, cv2, cv3, cv4])

        cat = generate_categories(2)
        cps = generate_categories_profiles(cat)

        bp = AlternativePerformances('b1', {'c1': 0.5, 'c2': 0.5,
                                            'c3': 0.5, 'c4': 0.5})
        bpt = PerformanceTable([bp])
        lbda = 0.5

        etri = MRSort(c, cv, bpt, 0.5, cps)

        a = generate_alternatives(1000)
        pt = generate_random_performance_table(a, c)
        aas = etri.pessimist(pt)

        for aa in aas:
            w = 0
            perfs = pt[aa.id].performances
            for c, val in perfs.items():
                if val >= bp.performances[c]:
                    w += cv[c].value

            if aa.category_id == 'cat1':
                self.assertLess(w, lbda)
            else:
                self.assertGreaterEqual(w, lbda)

    def test002(self):
        random.seed(2)
        c = generate_criteria(4)

        cv1 = CriterionValue('c1', 0.25)
        cv2 = CriterionValue('c2', 0.25)
        cv3 = CriterionValue('c3', 0.25)
        cv4 = CriterionValue('c4', 0.25)
        cv = CriteriaValues([cv1, cv2, cv3, cv4])

        cat = generate_categories(3)
        cps = generate_categories_profiles(cat)

        bp1 = AlternativePerformances('b1', {'c1': 0.25, 'c2': 0.25,
                                             'c3': 0.25, 'c4': 0.25})
        bp2 = AlternativePerformances('b2', {'c1': 0.75, 'c2': 0.75,
                                             'c3': 0.75, 'c4': 0.75})
        bpt = PerformanceTable([bp1, bp2])
        lbda = 0.5

        etri = MRSort(c, cv, bpt, 0.5, cps)

        a = generate_alternatives(1000)
        pt = generate_random_performance_table(a, c)
        aas = etri.pessimist(pt)

        for aa in aas:
            w1 = w2 = 0
            perfs = pt[aa.id].performances
            for c, val in perfs.items():
                if val >= bp1.performances[c]:
                    w1 += cv[c].value
                if val >= bp2.performances[c]:
                    w2 += cv[c].value

            if aa.category_id == 'cat1':
                self.assertLess(w1, lbda)
                self.assertLess(w2, lbda)
            elif aa.category_id == 'cat2':
                self.assertGreaterEqual(w1, lbda)
                self.assertLess(w2, lbda)
            else:
                self.assertGreaterEqual(w1, lbda)
                self.assertGreaterEqual(w2, lbda)

class test_indicator(unittest.TestCase):

    def test001_auck_no_errors(self):
        random.seed(1)
        crits = generate_criteria(5)
        model = generate_random_mrsort_model(len(crits), 2)

        alts = generate_alternatives(1000)
        pt = generate_random_performance_table(alts, crits)
        aa = model.get_assignments(pt)

        auck = model.auck(aa, pt, 1)
        self.assertEqual(auck, 1)

    def test002_auck_all_errors(self):
        random.seed(2)
        crits = generate_criteria(5)
        model = generate_random_mrsort_model(len(crits), 2)

        alts = generate_alternatives(1000)
        pt = generate_random_performance_table(alts, crits)
        aa = model.get_assignments(pt)
        aa_err = add_errors_in_assignments(aa, model.categories, 1)

        auck = model.auck(aa_err, pt, 1)
        self.assertEqual(auck, 0)

    def test003_auc_no_errors(self):
        random.seed(3)
        crits = generate_criteria(5)
        model = generate_random_mrsort_model(len(crits), 3)

        alts = generate_alternatives(1000)
        pt = generate_random_performance_table(alts, crits)
        aa = model.get_assignments(pt)

        auc = model.auc(aa, pt)
        self.assertEqual(auc, 1)

test_classes = [tests_electre_tri, tests_mrsort, test_indicator]

if __name__ == "__main__":
    suite = []
    for tclass in test_classes:
        suite.append(unittest.TestLoader().loadTestsFromTestCase(tclass))
    alltests = unittest.TestSuite(suite)
    unittest.TextTestRunner(verbosity=2).run(alltests)
