from __future__ import division
import sys
sys.path.insert(0, "..")
import unittest
import time
import random
from itertools import product

from mcda.electre_tri import electre_tri
from tools.meta_electre_tri_global import heuristic_profiles
from tools.utils import get_best_alternative_performances
from tools.utils import get_worst_alternative_performances
from tools.utils import get_pc_of_wrong_assignment
from tools.generate_random import generate_random_alternatives
from tools.generate_random import generate_random_criteria
from tools.generate_random import generate_random_criteria_values
from tools.generate_random import generate_random_performance_table
from tools.generate_random import generate_random_categories
from tools.generate_random import generate_random_categories_profiles
from tools.utils import normalize_criteria_weights

seeds = [ 123, 456, 789, 12, 345, 678, 901, 234, 567, 890 ]
seeds = [ 901 ]

class heuristic_profiles_tests(unittest.TestCase):

    def run_heuristic(self, na, nc, ncat, seed, nloop, nmodel):
        fitness = []

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

#        model.profiles.display()

        b0 = get_worst_alternative_performances(pt, c)
        bp = get_best_alternative_performances(pt, c)

        for j in range(nmodel):
            model.profiles = generate_random_categories_profiles(b, c)
            heur = heuristic_profiles(model, a, c, pt, aa, b0, bp)
            for k in range(nloop):
                aa2 = model.pessimist(pt)
                wrong = get_pc_of_wrong_assignment(aa, aa2)
                fitness.append(1-wrong)
                if wrong == 0:
                    break
                heur.optimize(aa2)
#                model.profiles.display(header=None)

            aa_learned = model.pessimist(pt)

        total = len(a)
        nok = 0
        for alt in a:
            if aa(alt.id) != aa_learned(alt.id):
                nok += 1

        return fitness

    def test001_two_categories(self):
        n_alts = [ 500 ]
        n_crit = [ 3, 5, 10 ]
        n_cat = [ 2, 3, 4, 5 ]
        nloop = 1000
        nmodel = 1

        fitness = { nc: { na: { ncat: { seed: [ 1 for i in range(nloop) ]
                                        for seed in seeds }
                                for ncat in n_cat }
                          for na in n_alts }
                    for nc in n_crit }

        print('\nna\tnc\tncat\tseed\tnloop\tnmodels\tf_end')
        for na, nc, ncat, seed in product(n_alts, n_crit, n_cat, seeds):
            f = self.run_heuristic(na, nc, ncat, seed, nloop, nmodel)
            fitness[nc][na][ncat][seed][0:len(f)] = f
            print("%d\t%d\t%d\t%d\t%d\t%d\t%-6.5f" % (na, nc, ncat, seed,
                  nloop, nmodel, f[-1]))

        print('Summary (two categories)')
        print('========================')
        print("nseeds: %d" % len(seeds))
        print('na\tnc\tncat\tnseeds\tloop\tnmodels\tf_avg\tf_min\tf_max')
        for nc, na, loop in product(n_crit, n_alts, range(nloop)):
            favg = fmax = 0
            fmin = 1
            for seed in fitness[nc][na][ncat]:
                f = fitness[nc][na][ncat][seed]
                favg += f[loop]
                if f[loop] < fmin:
                    fmin = f[loop]
                if f[loop] > fmax:
                    fmax = f[loop]
            favg /= len(seeds)
            print("%d\t%d\t%d\t%d\t%d\t%d\t%-6.5f\t%-6.5f\t%-6.5f" % (na,
                  nc, ncat, len(seeds), loop, nmodel, favg, fmin, fmax))


#    def test002_three_categories(self):
#        self.variable_number_alternatives_and_criteria(3)
#
#    def test003_four_categories(self):
#        self.variable_number_alternatives_and_criteria(4)

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(heuristic_profiles_tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
