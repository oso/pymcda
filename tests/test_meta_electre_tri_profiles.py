from __future__ import division
import sys
sys.path.insert(0, "..")
import unittest
import time
import random
from itertools import product

from mcda.electre_tri import electre_tri
from tools.meta_electre_tri_profiles import meta_electre_tri_profiles
from tools.meta_electre_tri_profiles import compute_fitness
from tools.utils import get_pc_of_wrong_assignment
from tools.sorted import sorted_performance_table
from tools.generate_random import generate_random_alternatives
from tools.generate_random import generate_random_criteria
from tools.generate_random import generate_random_criteria_values
from tools.generate_random import generate_random_performance_table
from tools.generate_random import generate_random_categories
from tools.generate_random import generate_random_categories_profiles
from tools.utils import normalize_criteria_weights

seeds = [ 123, 456, 789, 12, 345, 678, 901, 234, 567, 890 ]

class metaheuristic_profiles_tests(unittest.TestCase):

    def run_metaheuristic(self, na, nc, ncat, seed, nloop, nmodel):
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

        pt_sorted = sorted_performance_table(pt)

        for j in range(nmodel):
            model.profiles = generate_random_categories_profiles(b, c)
            meta = meta_electre_tri_profiles(model, pt_sorted, cat, aa)
            for k in range(nloop):
                aa2 = model.pessimist(pt)
                f = compute_fitness(aa, aa2)
                fitness.append(f)
                if f == 1:
                    break

                meta.optimize(aa2, f)

            f = compute_fitness(aa, aa2)
            fitness.append(f)

        return fitness

    def run_one_set_of_tests(self, n_alts, n_crit, n_cat, nloop, nmodel):
        fitness = { nc: { na: { ncat: { seed: [ 1 for i in range(nloop+1) ]
                                        for seed in seeds }
                                for ncat in n_cat }
                          for na in n_alts }
                    for nc in n_crit }

        print('\nna\tnc\tncat\tseed\tnloops\tnloopsu\tnmodels\tf_end')
        for na, nc, ncat, seed in product(n_alts, n_crit, n_cat, seeds):
            f = self.run_metaheuristic(na, nc, ncat, seed, nloop, nmodel)
            fitness[nc][na][ncat][seed][0:len(f)] = f
            print("%d\t%d\t%d\t%d\t%d\t%d\t%d\t%-6.5f" % (na, nc, ncat, seed,
                  nloop, len(f)-1, nmodel, f[-1]))

        print('Summary')
        print('=======')
        print("nseeds: %d" % len(seeds))
        print('na\tnc\tncat\tnseeds\tloop\tnmodels\tf_avg\tf_min\tf_max')
        for na, nc, ncat, loop in product(n_alts, n_crit, n_cat,
                                          range(nloop)):
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

    def test001_small_test(self):
        n_alts = [ 10000 ]
        n_crit = [ 5, 7, 10 ]
        n_cat = [ 2 ]
        nloop = 1000
        nmodel = 1

        self.run_one_set_of_tests(n_alts, n_crit, n_cat, nloop, nmodel)


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(metaheuristic_profiles_tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
