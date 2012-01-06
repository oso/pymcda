import sys
sys.path.insert(0, "..")
from mcda.electre_tri import electre_tri
import unittest

def compare_affectations(affectations, expected_affectations):
        ok = 1
        for aa in expected_affectations:
            key = aa.alternative_id
            if expected_affectations(key) <> affectations(key):
                print("Pessimits affectation of %s mismatch (%d <> %d)" %
                      (str(key), affectations(key),
                       expected_affectations(key)))
                ok=0

        return ok

class electre_tri_tests(unittest.TestCase):

    def test001_test_pessimist_loulouka(self):
        """ Loulouka - Pessimist """
        from data_loulouka import c, cv, ptb, lbda, pt, aap
        etri = electre_tri(c, cv, ptb, lbda).pessimist(pt)
        ok = compare_affectations(etri, aap)
        self.assertEqual(ok, 1, "One or more affectations were wrongly \
                         assigned")

    def test002_test_pessimist_ticino(self):
        """ Ticino - Pessimist """
        from data_ticino import c, cv, ptb, lbda, pt, aap
        etri = electre_tri(c, cv, ptb, lbda).pessimist(pt)
        ok = compare_affectations(etri, aap)
        self.assertEqual(ok, 1, "One or more affectations were wrongly \
                         assigned")


    def test003_test_optimist_loulouka(self):
        """ Loulouka - Optimist """
        from data_loulouka import c, cv, ptb, lbda, pt, aao
        etri = electre_tri(c, cv, ptb, lbda).optimist(pt)
        ok = compare_affectations(etri, aao)
        self.assertEqual(ok, 1, "One or more affectations were wrongly \
                         assigned")

    def test004_test_optimist_ticino(self):
        """ Ticino - Optimist """
        from data_ticino import c, cv, ptb, lbda, pt, aao
        etri = electre_tri(c, cv, ptb, lbda).optimist(pt)
        ok = compare_affectations(etri, aao)
        self.assertEqual(ok, 1, "One or more affectations were wrongly \
                         assigned")

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(electre_tri_tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
