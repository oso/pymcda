import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
import random
from pymcda.electre_tri import ElectreTri, MRSort
from pymcda.generate import generate_alternatives, generate_criteria
from pymcda.generate import generate_random_mrsort_model
from pymcda.generate import generate_random_performance_table
from pymcda.generate import generate_categories
from pymcda.generate import generate_categories_profiles
from pymcda.types import CriteriaSet
from pymcda.types import CriterionValue, CriteriaValues
from pymcda.types import AlternativePerformances, PerformanceTable
from pymcda.types import AlternativeAssignment, AlternativesAssignments
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
        self.assertEqual(ok, 1, "One or more alternatives were wrongly "
                         "assigned")

    def test002_test_pessimist_ticino(self):
        """ Ticino - Pessimist """
        from datasets.ticino import c, cv, ptb, lbda, pt, aap, cps
        etri = ElectreTri(c, cv, ptb, lbda, cps).pessimist(pt)
        ok = compare_assignments(etri, aap)
        self.assertEqual(ok, 1, "One or more alternatives were wrongly "
                         "assigned")


    def test003_test_optimist_loulouka(self):
        """ Loulouka - Optimist """
        from datasets.loulouka import c, cv, ptb, lbda, pt, aao, cps
        etri = ElectreTri(c, cv, ptb, lbda, cps).optimist(pt)
        ok = compare_assignments(etri, aao)
        self.assertEqual(ok, 1, "One or more alternatives were wrongly "
                         "assigned")

    def test004_test_optimist_ticino(self):
        """ Ticino - Optimist """
        from datasets.ticino import c, cv, ptb, lbda, pt, aao, cps
        etri = ElectreTri(c, cv, ptb, lbda, cps).optimist(pt)
        ok = compare_assignments(etri, aao)
        self.assertEqual(ok, 1, "One or more alternatives were wrongly "
                         "assigned")

class tests_electre_tri_new_threshold(unittest.TestCase):

    def test001_test_pessimist_loulouka(self):
        """ Loulouka - Pessimist """
        from datasets.loulouka import c, cv, ptb, lbda, pt, aap, cps, v2, q2, p2
        etri = ElectreTri(c, cv, ptb, lbda, cps, v2, q2, p2).pessimist(pt)
        ok = compare_assignments(etri, aap)
        self.assertEqual(ok, 1, "One or more alternatives were wrongly "
                         "assigned")

    def test002_test_pessimist_ticino(self):
        """ Ticino - Pessimist """
        from datasets.ticino import c, cv, ptb, lbda, pt, aap, cps, v2, q2, p2
        etri = ElectreTri(c, cv, ptb, lbda, cps, v2, q2, p2).pessimist(pt)
        ok = compare_assignments(etri, aap)
        self.assertEqual(ok, 1, "One or more alternatives were wrongly "
                         "assigned")


    def test003_test_optimist_loulouka(self):
        """ Loulouka - Optimist """
        from datasets.loulouka import c, cv, ptb, lbda, pt, aao, cps, v2, q2, p2
        etri = ElectreTri(c, cv, ptb, lbda, cps).optimist(pt)
        ok = compare_assignments(etri, aao)
        self.assertEqual(ok, 1, "One or more alternatives were wrongly "
                         "assigned")

    def test004_test_optimist_ticino(self):
        """ Ticino - Optimist """
        from datasets.ticino import c, cv, ptb, lbda, pt, aao, cps, v2, q2, p2
        etri = ElectreTri(c, cv, ptb, lbda, cps, v2, q2, p2).optimist(pt)
        ok = compare_assignments(etri, aao)
        self.assertEqual(ok, 1, "One or more alternatives were wrongly "
                         "assigned")

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

            if aa.category_id == 'cat2':
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

        bp1 = AlternativePerformances('b1', {'c1': 0.75, 'c2': 0.75,
                                             'c3': 0.75, 'c4': 0.75})
        bp2 = AlternativePerformances('b2', {'c1': 0.25, 'c2': 0.25,
                                             'c3': 0.25, 'c4': 0.25})
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

            if aa.category_id == 'cat3':
                self.assertLess(w1, lbda)
                self.assertLess(w2, lbda)
            elif aa.category_id == 'cat2':
                self.assertLess(w1, lbda)
                self.assertGreaterEqual(w2, lbda)
            else:
                self.assertGreaterEqual(w1, lbda)
                self.assertGreaterEqual(w2, lbda)

    def test003(self):
        random.seed(0)
        crits = generate_criteria(5)
        model = generate_random_mrsort_model(len(crits), 2)

        alts = generate_alternatives(1000)
        pt = generate_random_performance_table(alts, crits)
        aa = model.get_assignments(pt)

        aa = model.get_assignments(pt)

        self.assertEqual(len(aa.get_alternatives_in_categories(['cat1'])), 65)
        self.assertEqual(len(aa.get_alternatives_in_categories(['cat2'])), 935)

    def test003(self):
        random.seed(1)
        crits = generate_criteria(5)
        model = generate_random_mrsort_model(len(crits), 4)

        alts = generate_alternatives(1000)
        pt = generate_random_performance_table(alts, crits)
        aa = model.get_assignments(pt)

        aa = model.get_assignments(pt)

        self.assertEqual(len(aa.get_alternatives_in_categories(['cat1'])), 123)
        self.assertEqual(len(aa.get_alternatives_in_categories(['cat2'])), 146)
        self.assertEqual(len(aa.get_alternatives_in_categories(['cat3'])), 287)
        self.assertEqual(len(aa.get_alternatives_in_categories(['cat4'])), 444)

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

class test_xmcda(unittest.TestCase):

    def test001(self):
        model = generate_random_mrsort_model(5, 3)
        mxmcda = model.to_xmcda()
        model2 = MRSort().from_xmcda(mxmcda)
        self.assertEqual(model, model2)

class tests_mrsort_vc(unittest.TestCase):

    def test001(self):
        c = generate_criteria(5)
        w1 = CriterionValue('c1', 0.2)
        w2 = CriterionValue('c2', 0.2)
        w3 = CriterionValue('c3', 0.2)
        w4 = CriterionValue('c4', 0.2)
        w5 = CriterionValue('c5', 0.2)
        w = CriteriaValues([w1, w2, w3, w4, w5])

        b1 = AlternativePerformances('b1', {'c1': 10, 'c2': 10, 'c3': 10, 'c4': 10, 'c5': 10})
        bpt = PerformanceTable([b1])

        cat = generate_categories(2)
        cps = generate_categories_profiles(cat)

        vb1 = AlternativePerformances('b1', {'c1': 2, 'c2': 2, 'c3': 2, 'c4': 2, 'c5': 2}, 'b1')
        v = PerformanceTable([vb1])
        vw = w.copy()

        a1 = AlternativePerformances('a1',   {'c1':  9, 'c2':  9, 'c3':  9, 'c4':  9, 'c5': 11})
        a2 = AlternativePerformances('a2',   {'c1':  9, 'c2':  9, 'c3':  9, 'c4': 11, 'c5':  9})
        a3 = AlternativePerformances('a3',   {'c1':  9, 'c2':  9, 'c3':  9, 'c4': 11, 'c5': 11})
        a4 = AlternativePerformances('a4',   {'c1':  9, 'c2':  9, 'c3': 11, 'c4':  9, 'c5':  9})
        a5 = AlternativePerformances('a5',   {'c1':  9, 'c2':  9, 'c3': 11, 'c4':  9, 'c5': 11})
        a6 = AlternativePerformances('a6',   {'c1':  9, 'c2':  9, 'c3': 11, 'c4': 11, 'c5':  9})
        a7 = AlternativePerformances('a7',   {'c1':  9, 'c2':  9, 'c3': 11, 'c4': 11, 'c5': 11})
        a8 = AlternativePerformances('a8',   {'c1':  9, 'c2': 11, 'c3':  9, 'c4':  9, 'c5':  9})
        a9 = AlternativePerformances('a9',   {'c1':  9, 'c2': 11, 'c3':  9, 'c4':  9, 'c5': 11})
        a10 = AlternativePerformances('a10', {'c1':  9, 'c2': 11, 'c3':  9, 'c4': 11, 'c5':  9})
        a11 = AlternativePerformances('a11', {'c1':  9, 'c2': 11, 'c3':  9, 'c4': 11, 'c5': 11})
        a12 = AlternativePerformances('a12', {'c1':  9, 'c2': 11, 'c3': 11, 'c4':  9, 'c5':  9})
        a13 = AlternativePerformances('a13', {'c1':  9, 'c2': 11, 'c3': 11, 'c4':  9, 'c5': 11})
        a14 = AlternativePerformances('a14', {'c1':  9, 'c2': 11, 'c3': 11, 'c4': 11, 'c5':  9})
        a15 = AlternativePerformances('a15', {'c1':  9, 'c2': 11, 'c3': 11, 'c4': 11, 'c5': 11})
        a16 = AlternativePerformances('a16', {'c1': 11, 'c2':  9, 'c3':  9, 'c4':  9, 'c5':  9})
        a17 = AlternativePerformances('a17', {'c1': 11, 'c2':  9, 'c3':  9, 'c4':  9, 'c5': 11})
        a18 = AlternativePerformances('a18', {'c1': 11, 'c2':  9, 'c3':  9, 'c4': 11, 'c5':  9})
        a19 = AlternativePerformances('a19', {'c1': 11, 'c2':  9, 'c3':  9, 'c4': 11, 'c5': 11})
        a20 = AlternativePerformances('a20', {'c1': 11, 'c2':  9, 'c3': 11, 'c4':  9, 'c5':  9})
        a21 = AlternativePerformances('a21', {'c1': 11, 'c2':  9, 'c3': 11, 'c4':  9, 'c5': 11})
        a22 = AlternativePerformances('a22', {'c1': 11, 'c2':  9, 'c3': 11, 'c4': 11, 'c5':  9})
        a23 = AlternativePerformances('a23', {'c1': 11, 'c2':  9, 'c3': 11, 'c4': 11, 'c5': 11})
        a24 = AlternativePerformances('a24', {'c1': 11, 'c2': 11, 'c3':  9, 'c4':  9, 'c5':  9})
        a25 = AlternativePerformances('a25', {'c1': 11, 'c2': 11, 'c3':  9, 'c4':  9, 'c5': 11})
        a26 = AlternativePerformances('a26', {'c1': 11, 'c2': 11, 'c3':  9, 'c4': 11, 'c5':  9})
        a27 = AlternativePerformances('a27', {'c1': 11, 'c2': 11, 'c3':  9, 'c4': 11, 'c5': 11})
        a28 = AlternativePerformances('a28', {'c1': 11, 'c2': 11, 'c3': 11, 'c4':  9, 'c5':  9})
        a29 = AlternativePerformances('a29', {'c1': 11, 'c2': 11, 'c3': 11, 'c4':  9, 'c5': 11})
        a30 = AlternativePerformances('a30', {'c1': 11, 'c2': 11, 'c3': 11, 'c4': 11, 'c5':  9})
        a31 = AlternativePerformances('a31', {'c1': 11, 'c2': 11, 'c3': 11, 'c4': 11, 'c5':  7})
        a32 = AlternativePerformances('a32', {'c1': 11, 'c2': 11, 'c3': 11, 'c4':  7, 'c5': 11})
        a33 = AlternativePerformances('a33', {'c1': 11, 'c2': 11, 'c3':  7, 'c4': 11, 'c5': 11})
        a34 = AlternativePerformances('a34', {'c1': 11, 'c2':  7, 'c3': 11, 'c4': 11, 'c5': 11})
        a35 = AlternativePerformances('a35', {'c1':  7, 'c2': 11, 'c3': 11, 'c4': 11, 'c5': 11})
        a36 = AlternativePerformances('a36', {'c1': 11, 'c2': 11, 'c3': 11, 'c4':  7, 'c5':  7})
        a37 = AlternativePerformances('a37', {'c1': 11, 'c2': 11, 'c3':  7, 'c4': 11, 'c5':  7})
        a38 = AlternativePerformances('a38', {'c1': 11, 'c2':  7, 'c3': 11, 'c4': 11, 'c5':  7})
        a39 = AlternativePerformances('a39', {'c1':  7, 'c2': 11, 'c3': 11, 'c4': 11, 'c5':  7})
        a40 = AlternativePerformances('a40', {'c1': 11, 'c2': 11, 'c3':  7, 'c4':  7, 'c5': 11})
        a41 = AlternativePerformances('a41', {'c1': 11, 'c2':  7, 'c3': 11, 'c4':  7, 'c5': 11})
        a42 = AlternativePerformances('a42', {'c1':  7, 'c2': 11, 'c3': 11, 'c4':  7, 'c5': 11})
        a43 = AlternativePerformances('a43', {'c1': 11, 'c2':  7, 'c3':  7, 'c4': 11, 'c5': 11})
        a44 = AlternativePerformances('a44', {'c1':  7, 'c2': 11, 'c3':  7, 'c4': 11, 'c5': 11})
        a45 = AlternativePerformances('a45', {'c1':  7, 'c2':  7, 'c3': 11, 'c4': 11, 'c5': 11})
        pt = PerformanceTable([eval("a%d" % i) for i in range(1, 46)])

        ap1 = AlternativeAssignment('a1', 'cat2')
        ap2 = AlternativeAssignment('a2', 'cat2')
        ap3 = AlternativeAssignment('a3', 'cat2')
        ap4 = AlternativeAssignment('a4', 'cat2')
        ap5 = AlternativeAssignment('a5', 'cat2')
        ap6 = AlternativeAssignment('a6', 'cat2')
        ap7 = AlternativeAssignment('a7', 'cat1')
        ap8 = AlternativeAssignment('a8', 'cat2')
        ap9 = AlternativeAssignment('a9', 'cat2')
        ap10 = AlternativeAssignment('a10', 'cat2')
        ap11 = AlternativeAssignment('a11', 'cat1')
        ap12 = AlternativeAssignment('a12', 'cat2')
        ap13 = AlternativeAssignment('a13', 'cat1')
        ap14 = AlternativeAssignment('a14', 'cat1')
        ap15 = AlternativeAssignment('a15', 'cat1')
        ap16 = AlternativeAssignment('a16', 'cat2')
        ap17 = AlternativeAssignment('a17', 'cat2')
        ap18 = AlternativeAssignment('a18', 'cat2')
        ap19 = AlternativeAssignment('a19', 'cat1')
        ap20 = AlternativeAssignment('a20', 'cat2')
        ap21 = AlternativeAssignment('a21', 'cat1')
        ap22 = AlternativeAssignment('a22', 'cat1')
        ap23 = AlternativeAssignment('a23', 'cat1')
        ap24 = AlternativeAssignment('a24', 'cat2')
        ap25 = AlternativeAssignment('a25', 'cat1')
        ap26 = AlternativeAssignment('a26', 'cat1')
        ap27 = AlternativeAssignment('a27', 'cat1')
        ap28 = AlternativeAssignment('a28', 'cat1')
        ap29 = AlternativeAssignment('a29', 'cat1')
        ap30 = AlternativeAssignment('a30', 'cat1')
        ap31 = AlternativeAssignment('a31', 'cat1')
        ap32 = AlternativeAssignment('a32', 'cat1')
        ap33 = AlternativeAssignment('a33', 'cat1')
        ap34 = AlternativeAssignment('a34', 'cat1')
        ap35 = AlternativeAssignment('a35', 'cat1')
        ap36 = AlternativeAssignment('a36', 'cat2')
        ap37 = AlternativeAssignment('a37', 'cat2')
        ap38 = AlternativeAssignment('a38', 'cat2')
        ap39 = AlternativeAssignment('a39', 'cat2')
        ap40 = AlternativeAssignment('a40', 'cat2')
        ap41 = AlternativeAssignment('a41', 'cat2')
        ap42 = AlternativeAssignment('a42', 'cat2')
        ap43 = AlternativeAssignment('a43', 'cat2')
        ap44 = AlternativeAssignment('a44', 'cat2')
        ap45 = AlternativeAssignment('a45', 'cat2')
        aa = AlternativesAssignments([eval("ap%d" % i) for i in range(1, 46)])

        model = MRSort(c, w, bpt, 0.6, cps, v, vw, 0.4)
        aa2 = model.pessimist(pt)
        ok = compare_assignments(aa, aa2)
        self.assertEqual(ok, 1, "One or more alternatives were wrongly "
                         "assigned")

class tests_mrsort_choquet(unittest.TestCase):

    def test001(self):
        c = generate_criteria(3)
        cat = generate_categories(3)
        cps = generate_categories_profiles(cat)

        bp1 = AlternativePerformances('b1', {'c1': 0.75, 'c2': 0.75, 'c3': 0.75})
        bp2 = AlternativePerformances('b2', {'c1': 0.25, 'c2': 0.25, 'c3': 0.25})
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

        ap1 = AlternativePerformances('a1',
                                      {'c1': 0.3, 'c2': 0.3, 'c3': 0.3})
        ap2 = AlternativePerformances('a2',
                                      {'c1': 0.8, 'c2': 0.8, 'c3': 0.8})
        ap3 = AlternativePerformances('a3',
                                      {'c1': 0.3, 'c2': 0.3, 'c3': 0.1})
        ap4 = AlternativePerformances('a4',
                                      {'c1': 0.3, 'c2': 0.1, 'c3': 0.3})
        ap5 = AlternativePerformances('a5',
                                      {'c1': 0.1, 'c2': 0.3, 'c3': 0.3})
        ap6 = AlternativePerformances('a6',
                                      {'c1': 0.8, 'c2': 0.8, 'c3': 0.1})
        ap7 = AlternativePerformances('a7',
                                      {'c1': 0.8, 'c2': 0.1, 'c3': 0.8})
        ap8 = AlternativePerformances('a8',
                                      {'c1': 0.1, 'c2': 0.8, 'c3': 0.8})
        pt = PerformanceTable([ap1, ap2, ap3, ap4, ap5, ap6, ap7, ap8])

        aa = model.get_assignments(pt)

        self.assertEqual(aa['a1'].category_id, "cat2")
        self.assertEqual(aa['a2'].category_id, "cat1")
        self.assertEqual(aa['a3'].category_id, "cat3")
        self.assertEqual(aa['a4'].category_id, "cat2")
        self.assertEqual(aa['a5'].category_id, "cat2")
        self.assertEqual(aa['a6'].category_id, "cat3")
        self.assertEqual(aa['a7'].category_id, "cat1")
        self.assertEqual(aa['a8'].category_id, "cat1")

test_classes = [tests_electre_tri, tests_electre_tri_new_threshold,
                tests_mrsort, test_indicator, test_xmcda,
                tests_mrsort_vc, tests_mrsort_choquet]

if __name__ == "__main__":
    suite = []
    for tclass in test_classes:
        suite.append(unittest.TestLoader().loadTestsFromTestCase(tclass))
    alltests = unittest.TestSuite(suite)
    unittest.TextTestRunner(verbosity=2).run(alltests)
