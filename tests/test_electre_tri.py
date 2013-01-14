import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
from mcda.electre_tri import electre_tri
import unittest

def compare_assignments(assignments, expected_assignments):
        ok = 1
        for aa in expected_assignments:
            key = aa.alternative_id
            if expected_assignments(key) != assignments(key):
                print("Pessimits assignment of %s mismatch (%s <> %s)" %
                      (str(key), assignments(key),
                       expected_assignments(key)))
                ok=0

        return ok

class electre_tri_tests(unittest.TestCase):

    def test001_test_pessimist_loulouka(self):
        """ Loulouka - Pessimist """
        from data_loulouka import c, cv, ptb, lbda, pt, aap, cps
        etri = electre_tri(c, cv, ptb, lbda, cps).pessimist(pt)
        ok = compare_assignments(etri, aap)
        self.assertEqual(ok, 1, "One or more alternatives were wrongly \
                         assigned")

    def test002_test_pessimist_ticino(self):
        """ Ticino - Pessimist """
        from data_ticino import c, cv, ptb, lbda, pt, aap, cps
        etri = electre_tri(c, cv, ptb, lbda, cps).pessimist(pt)
        ok = compare_assignments(etri, aap)
        self.assertEqual(ok, 1, "One or more alternatives were wrongly \
                         assigned")


    def test003_test_optimist_loulouka(self):
        """ Loulouka - Optimist """
        from data_loulouka import c, cv, ptb, lbda, pt, aao, cps
        etri = electre_tri(c, cv, ptb, lbda, cps).optimist(pt)
        ok = compare_assignments(etri, aao)
        self.assertEqual(ok, 1, "One or more alternatives were wrongly \
                         assigned")

    def test004_test_optimist_ticino(self):
        """ Ticino - Optimist """
        from data_ticino import c, cv, ptb, lbda, pt, aao, cps
        etri = electre_tri(c, cv, ptb, lbda, cps).optimist(pt)
        ok = compare_assignments(etri, aao)
        self.assertEqual(ok, 1, "One or more alternatives were wrongly \
                         assigned")

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(electre_tri_tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
