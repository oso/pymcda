import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
from pymcda.electre_tri import electre_tri
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

class electre_tri_tests(unittest.TestCase):

    def test001_test_pessimist_loulouka(self):
        """ Loulouka - Pessimist """
        from datasets.loulouka import c, cv, ptb, lbda, pt, aap, cps
        etri = electre_tri(c, cv, ptb, lbda, cps).pessimist(pt)
        ok = compare_assignments(etri, aap)
        self.assertEqual(ok, 1, "One or more alternatives were wrongly \
                         assigned")

    def test002_test_pessimist_ticino(self):
        """ Ticino - Pessimist """
        from datasets.ticino import c, cv, ptb, lbda, pt, aap, cps
        etri = electre_tri(c, cv, ptb, lbda, cps).pessimist(pt)
        ok = compare_assignments(etri, aap)
        self.assertEqual(ok, 1, "One or more alternatives were wrongly \
                         assigned")


    def test003_test_optimist_loulouka(self):
        """ Loulouka - Optimist """
        from datasets.loulouka import c, cv, ptb, lbda, pt, aao, cps
        etri = electre_tri(c, cv, ptb, lbda, cps).optimist(pt)
        ok = compare_assignments(etri, aao)
        self.assertEqual(ok, 1, "One or more alternatives were wrongly \
                         assigned")

    def test004_test_optimist_ticino(self):
        """ Ticino - Optimist """
        from datasets.ticino import c, cv, ptb, lbda, pt, aao, cps
        etri = electre_tri(c, cv, ptb, lbda, cps).optimist(pt)
        ok = compare_assignments(etri, aao)
        self.assertEqual(ok, 1, "One or more alternatives were wrongly \
                         assigned")

test_classes = [electre_tri_tests]

if __name__ == "__main__":
    suite = []
    for tclass in test_classes:
        suite.append(unittest.TestLoader().loadTestsFromTestCase(tclass))
    alltests = unittest.TestSuite(suite)
    unittest.TextTestRunner(verbosity=2).run(alltests)
