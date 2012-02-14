import sys
sys.path.insert(0, "..")
import unittest
import time
import random
from itertools import product

from mcda.electre_tri import electre_tri
from tools.lp_electre_tri_weights import lp_electre_tri_weights
from tools.generate_random import generate_random_alternatives
from tools.generate_random import generate_random_criteria
from tools.generate_random import generate_random_criteria_values
from tools.generate_random import generate_random_performance_table
from tools.generate_random import generate_random_categories
from tools.generate_random import generate_random_categories_profiles

seeds = [ 1234 ]

class lp_electre_tri_weights_tests(unittest.TestCase):

    def test001_variable_number_alternatives(self):
        n_alts = [ i*10 for i in range(10) ]
        n_crit = [ i for i in range(2,7) ]
        objective = { nc: {na: dict() for na in n_alts} for nc in n_crit }
        print objective[6]
        raise
        for nc, na, seed in product(n_crit, n_alts, seeds):
            random.seed(seed)
            a = generate_random_alternatives(na)
            c = generate_random_criteria(nc)
            pt = generate_random_performance_table(a, c)
            cv = generate_random_criteria_values(c)
            b = generate_random_alternatives(2, 'b')
            bpt = generate_random_categories_profiles(b, c, 2345)
            cat = generate_random_categories(3)
            lbda = random.uniform(0.5, 1)

            model = electre_tri(c, cv, bpt, lbda, cat)
            aa = model.pessimist(pt)

            lp_weights = lp_electre_tri_weights(a, c, cv, aa, pt, cat,
                                                b, bpt, 0.0001, 0.0001)
            obj, cv_learned, lbda_learned = lp_weights.solve()

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(lp_electre_tri_weights_tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
