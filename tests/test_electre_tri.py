import sys
sys.path.insert(0, "..")
from mcda.electre_tri import electre_tri
import unittest

class electre_tri_tests(unittest.TestCase):

    def test001_test_pessimist_loulouka(self):
        """ Loulouka - Pessimist """

        from data_loulouka import c, cv, ptb, lbda, pt, aap
        etri = electre_tri(c, cv, ptb, lbda)
        affectations = etri.pessimist(pt)
        ok = 1
        for aa in aap:
            key = aa.alternative_id
            if aap(key) <> affectations(key):
                print("Pessimits affectation of %s mismatch (%d <> %d)" %
                      (str(key), aap(key), affectations(key)))
                ok=0
        self.assertEqual(ok, 1, "One or more affectations were wrongly \
                         assigned")

    def test002_test_pessimist_ticino(self):
        """ Ticino - Pessimist """

        from data_ticino import c, cv, ptb, lbda, pt, aap
        etri = electre_tri(c, cv, ptb, lbda)
        affectations = etri.pessimist(pt)
        ok = 1
        for aa in aap:
            key = aa.alternative_id
            if aap(key) <> affectations(key):
                print("Pessimits affectation of %s mismatch (%d <> %d)" %
                      (str(key), aap(key), affectations(key)))
                ok=0
        self.assertEqual(ok, 1, "One or more affectations were wrongly \
                         assigned")

    def test003_test_optimist_loulouka(self):
        """ Loulouka - Optimist """

        from data_loulouka import c, cv, ptb, lbda, pt, aao
        etri = electre_tri(c, cv, ptb, lbda)
        affectations = etri.optimist(pt)
        ok = 1
        for aa in aao:
            key = aa.alternative_id
            if aao(key) <> affectations(key):
                print("Pessimits affectation of %s mismatch (%d <> %d)" %
                      (str(key), aao(key), affectations(key)))
                ok=0
        self.assertEqual(ok, 1, "One or more affectations were wrongly \
                         assigned")

    def test004_test_optimist_ticino(self):
        """ Ticino - Optimist """

        from data_ticino import c, cv, ptb, lbda, pt, aao
        etri = electre_tri(c, cv, ptb, lbda)
        affectations = etri.optimist(pt)
        ok = 1
        for aa in aao:
            key = aa.alternative_id
            if aao(key) <> affectations(key):
                print("Pessimits affectation of %s mismatch (%d <> %d)" %
                      (str(key), aao(key), affectations(key)))
                ok=0
        self.assertEqual(ok, 1, "One or more affectations were wrongly \
                         assigned")

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(electre_tri_tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
