from __future__ import division
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
from tools.utils import normalize_criteria_weights

seeds = [ 123, 456, 789, 12, 345, 678, 901, 234, 567, 890 ]

class lp_electre_tri_weights_tests(unittest.TestCase):

    def variable_number_alternatives_and_criteria(self, ncat):
        n_alts = [ i*1000 for i in range(1, 11) ]
        n_crit = [ i for i in range(2,21) ]

        print('\nnc\tna\tseed\tobj\terrors\ttime')

        objectives = { nc: {na: dict() for na in n_alts} for nc in n_crit }
        times = { nc: {na: dict() for na in n_alts} for nc in n_crit }
        errors = { nc: {na: dict() for na in n_alts} for nc in n_crit }
        for nc, na, seed in product(n_crit, n_alts, seeds):
            a = generate_random_alternatives(na)
            c = generate_random_criteria(nc)
            cv = generate_random_criteria_values(c, seed)
            normalize_criteria_weights(cv)
            pt = generate_random_performance_table(a, c)

            b = generate_random_alternatives(ncat-1, 'b')
            bpt = generate_random_categories_profiles(b, c)
            cat = generate_random_categories(ncat)

            lbda = random.uniform(0.5, 1)

            model = electre_tri(c, cv, bpt, lbda, cat)
            aa = model.pessimist(pt)

            t1 = time.time()
            lp_weights = lp_electre_tri_weights(a, c, cv, aa, pt, cat,
                                                b, bpt, 0.0001, 0.0001)
            obj, cv_learned, lbda_learned = lp_weights.solve()
            t2 = time.time()

            objectives[nc][na][seed] = obj
            times[nc][na][seed] = t2-t1

            model.cv = cv_learned
            model.lbda = lbda_learned
            aa_learned = model.pessimist(pt)

            total = len(a)
            nok = 0
            for alt in a:
                if aa(alt.id) != aa_learned(alt.id):
                    nok += 1

            errors[nc][na][seed] = nok/total

            print("%d\t%d\t%s\t%-6.5f\t%-6.5f\t%-6.5f" % (nc, na, seed,
                  obj, nok/total, t2-t1))


        print('Summary')
        print('========')
        print("nseeds: %d" % len(seeds))
        print('nc\tna\tobj\terrors\ttime')
        for nc, na in product(n_crit, n_alts):
            obj = sum(objectives[nc][na].values())/len(seeds)
            tim = sum(times[nc][na].values())/len(seeds)
            err = sum(errors[nc][na].values())/len(seeds)
            print("%d\t%d\t%-6.5f\t%-6.5f\t%-6.5f" % (nc, na, obj, err,
                  tim))

    def test001_two_categories(self):
        self.variable_number_alternatives_and_criteria(2)

    def test002_three_categories(self):
        self.variable_number_alternatives_and_criteria(3)

    def test003_four_categories(self):
        self.variable_number_alternatives_and_criteria(4)

    def test004_five_categories(self):
        self.variable_number_alternatives_and_criteria(5)

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(lp_electre_tri_weights_tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
