from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
from pymcda.types import *
from pymcda.generate import *
from pymcda.utils import *
import unittest

class tests_utils(unittest.TestCase):

    def generate_random_assignments(self, na, ncat):
        category_ids = ['cat%d' % (i + 1) for i in range(ncat)]
        aa = AlternativesAssignments([])
        for i in range(na):
            cat = random.sample(category_ids, 1)[0]
            af = AlternativeAssignment('a%d' % (i + 1), cat)
            aa.append(af)

        return aa

    def test001(self):
        aa = self.generate_random_assignments(1000, 3)
        aa_err = aa.copy()
        category_ids = ['cat%d' % (i + 1) for i in range(3)]
        add_errors_in_assignments(aa_err, category_ids, 0.2)
        ca = compute_ca(aa, aa_err)
        self.assertEqual(ca, 0.8)

    def test002(self):
        aa = self.generate_random_assignments(1000, 3)
        aa_err = aa.copy()
        category_ids = ['cat%d' % (i + 1) for i in range(3)]
        err = add_errors_in_assignments_proba(aa_err, category_ids, 0.2)
        ca = compute_ca(aa, aa_err)
        self.assertEqual(ca, (len(aa) - len(err)) / len(aa))
        self.assertLess(ca, 0.9)
        self.assertGreater(ca, 0.7)

test_classes = [tests_utils]

if __name__ == "__main__":
    suite = []
    for tclass in test_classes:
        suite.append(unittest.TestLoader().loadTestsFromTestCase(tclass))
    alltests = unittest.TestSuite(suite)
    unittest.TextTestRunner(verbosity=2).run(alltests)
