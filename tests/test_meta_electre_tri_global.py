from __future__ import division
import sys
sys.path.insert(0, "..")
import unittest
import time
import random
from itertools import product

from mcda.electre_tri import electre_tri
from inference.meta_electre_tri_global import heuristic_profiles
from inference.meta_electre_tri_global import meta_electre_tri_global
from tools.utils import get_best_alternative_performances
from tools.utils import get_worst_alternative_performances
from tools.utils import compute_ac
from tools.generate_random import generate_random_alternatives
from tools.generate_random import generate_random_criteria
from tools.generate_random import generate_random_criteria_values
from tools.generate_random import generate_random_performance_table
from tools.generate_random import generate_random_categories
from tools.generate_random import generate_random_profiles
from tools.generate_random import generate_random_categories_profiles
from tools.utils import normalize_criteria_weights

seeds = [ 123, 456, 789, 12, 345, 678, 901, 234, 567, 890 ]

class heuristic_profiles_tests(unittest.TestCase):

    def run_heuristic(self, na, nc, ncat, seed, nloop, nmodel):
        fitness = []

        a = generate_random_alternatives(na)
        c = generate_random_criteria(nc)
        cv = generate_random_criteria_values(c, seed)
        normalize_criteria_weights(cv)
        pt = generate_random_performance_table(a, c)

        b = generate_random_alternatives(ncat-1, 'b')
        bpt = generate_random_profiles(b, c)
        cat = generate_random_categories(ncat)
        cps = generate_random_categories_profiles(cat)

        lbda = random.uniform(0.5, 1)

        model = electre_tri(c, cv, bpt, lbda, cps)
        aa = model.pessimist(pt)

#        model.bpt.display()

        b0 = get_worst_alternative_performances(pt, c)
        bp = get_best_alternative_performances(pt, c)

        for j in range(nmodel):
            model.bpt = generate_random_profiles(b, c)
            heur = heuristic_profiles(model, a, c, pt, aa, b0, bp)
            for k in range(nloop):
                aa2 = model.pessimist(pt)
                wrong = 1 - compute_ac(aa, aa2)
                fitness.append(1-wrong)
                if wrong == 0:
                    break
                heur.optimize(aa2)
#                model.bpt.display(header=None)

            aa_learned = model.pessimist(pt)

        total = len(a)
        nok = 0
        for alt in a:
            if aa(alt.id) != aa_learned(alt.id):
                nok += 1

        return fitness

    def run_one_set_of_tests(self, n_alts, n_crit, n_cat, nloop, nmodel):
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

#    def test001_small_test(self):
#        n_alts = [ 500 ]
#        n_crit = [ 5 ]
#        n_cat = [ 2 ]
#        nloop = 100
#        nmodel = 1
#
#        self.run_one_set_of_tests(n_alts, n_crit, n_cat, nloop, nmodel)
#
#    def test002_variable_crit_and_cat(self):
#        n_alts = [ 500 ]
#        n_crit = [ 3, 5, 10 ]
#        n_cat = [ 2, 3, 4, 5 ]
#        nloop = 1000
#        nmodel = 1
#
#        self.run_one_set_of_tests(n_alts, n_crit, n_cat, nloop, nmodel)

    def test003_variable_alternatives(self):
        #n_alts = [ 100, 500, 1000 ]
        n_alts = [ 5000 ]
        n_crit = [ 5 ]
        n_cat = [ 3 ]
        nloop = 1000
        nmodel = 1

        self.run_one_set_of_tests(n_alts, n_crit, n_cat, nloop, nmodel)

class metaheuristic_tests(unittest.TestCase):

    def run_metaheuristic(self, na, nc, ncat, seed, nloop, nloop2, nmodel):
        a = generate_random_alternatives(na)
        c = generate_random_criteria(nc)
        cv = generate_random_criteria_values(c, seed)
        normalize_criteria_weights(cv)
        pt = generate_random_performance_table(a, c)

        b = generate_random_alternatives(ncat-1, 'b')
        bpt = generate_random_profiles(b, c)
        cat = generate_random_categories(ncat)
        cps = generate_random_categories_profiles(cat)

        lbda = random.uniform(0.5, 1)

        model = electre_tri(c, cv, bpt, lbda, cps)
        aa = model.pessimist(pt)

        t1 = time.time()
        meta = meta_electre_tri_global(a, c, cv, aa, pt, cps, cat)
        model_learned = meta.solve(nmodel, nloop, nloop2)
        t2 = time.time()

        aa_learned = model_learned.pessimist(pt)
        total = len(a)
        nok = 0
        for alt in a:
            if aa(alt.id) != aa_learned(alt.id):
                nok += 1

        fitness = (total-nok)/total
        t = t2-t1

        return fitness, t

    def run_one_set_of_tests(self, n_alts, n_crit, n_cat, nloop, nloop2,
                             nmodel):
        fitness = { nc: { na: { ncat: { seed: 0 for seed in seeds }
                                for ncat in n_cat }
                          for na in n_alts }
                    for nc in n_crit }
        times = { nc: { na: { ncat: { seed: 0 for seed in seeds }
                                for ncat in n_cat }
                          for na in n_alts }
                    for nc in n_crit }

        print('\nna\tnc\tncat\tseed\tnloop\tnloop2\tnmodels\tf_end')
        for na, nc, ncat, seed in product(n_alts, n_crit, n_cat, seeds):
            f, t = self.run_metaheuristic(na, nc, ncat, seed, nloop, nloop2,
                                          nmodel)
            fitness[nc][na][ncat][seed] = f
            times[nc][na][ncat][seed] = t
            print("%d\t%d\t%d\t%d\t%d\t%d\t%d\t%-6.5f" % (na, nc, ncat,
                  seed, nloop, nloop2, nmodel, f))

        print('Summary')
        print('=======')
        print("nseeds: %d" % len(seeds))
        print('na\tnc\tncat\tnseeds\tnloop\tnloop2\tnmodels\t' \
              'f_avg\tf_min\tf_max\tt_avg\tt_min\tt_max')
        for na, nc, ncat in product(n_alts, n_crit, n_cat):
            f_avg = sum(fitness[nc][na][ncat].values())/len(seeds)
            f_min = min(fitness[nc][na][ncat].values())
            f_max = max(fitness[nc][na][ncat].values())
            t_avg = sum(times[nc][na][ncat].values())/len(seeds)
            t_min = min(times[nc][na][ncat].values())
            t_max = max(times[nc][na][ncat].values())
            print("%d\t%d\t%d\t%d\t%d\t%d\t%d\t%-6.5f\t%-6.5f\t%-6.5f" \
                  "\t%-6.5f\t%-6.5f\t%-6.5f" % (na, nc, ncat, len(seeds),
                  nloop, nloop2, nmodel,
                  f_avg, f_min, f_max, t_avg, t_min, t_max))

    def test001_small_test(self):
        n_alts = [ 25, 50, 75, 100, 125, 150 ]
        n_crit = [ 3, 5, 10 ]
        n_cat = [ 3 ]
        nloop = 10
        nloop2 = 50
        nmodel = 5

        self.run_one_set_of_tests(n_alts, n_crit, n_cat, nloop, nloop2,
                                  nmodel)

    def test002_big_test(self):
        n_alts = [ 100, 200, 300, 400, 500 ]
        n_crit = [ 3, 5, 10 ]
        n_cat = [ 3 ]
        nloop = 10
        nloop2 = 100
        nmodel = 10

        self.run_one_set_of_tests(n_alts, n_crit, n_cat, nloop, nloop2,
                                  nmodel)

if __name__ == "__main__":
    loader = unittest.TestLoader()
#    suite = loader.loadTestsFromTestCase(heuristic_profiles_tests)
    suite = loader.loadTestsFromTestCase(metaheuristic_tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
