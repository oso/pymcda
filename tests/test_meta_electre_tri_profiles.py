from __future__ import division
import sys
sys.path.insert(0, "..")
import unittest
import time
import random
from itertools import product

from mcda.electre_tri import electre_tri
from inference.meta_electre_tri_profiles import meta_electre_tri_profiles
from tools.utils import compute_ac
from tools.sorted import sorted_performance_table
from tools.generate_random import generate_random_alternatives
from tools.generate_random import generate_random_criteria
from tools.generate_random import generate_random_criteria_values
from tools.generate_random import generate_random_performance_table
from tools.generate_random import generate_random_categories
from tools.generate_random import generate_random_profiles
from tools.generate_random import generate_random_categories_profiles
from tools.utils import normalize_criteria_weights
from tools.utils import add_errors_in_affectations

seeds = [ 123, 456, 789, 12, 345, 678, 901, 234, 567, 890 ]

class metaheuristic_profiles_tests(unittest.TestCase):

    def run_metaheuristic(self, na, nc, ncat, seed, nloop, nmodel,
                          nerrors=0):
        fitness = []

        a = generate_random_alternatives(na)
        c = generate_random_criteria(nc)
        cv = generate_random_criteria_values(c, seed)
        normalize_criteria_weights(cv)
        pt = generate_random_performance_table(a, c)

        cat = generate_random_categories(ncat)
        cps = generate_random_categories_profiles(cat)
        b = cps.get_ordered_profiles()
        bpt = generate_random_profiles(b, c)

        lbda = random.uniform(0.5, 1)

        model = electre_tri(c, cv, bpt, lbda, cps)
        aa = model.pessimist(pt)
        aa_errors = model.pessimist(pt)

        aa_erroned = add_errors_in_affectations(aa_errors, cat.get_ids(), nerrors)

        pt_sorted = sorted_performance_table(pt)

        t1 = time.time()

        model.bpt = generate_random_profiles(b, c)
        meta = meta_electre_tri_profiles(model, pt_sorted, cat, aa_errors)

        best_f = 0
        best_bpt = model.bpt.copy()
        for k in range(nloop):
            aa2 = model.pessimist(pt)
            f = compute_ac(aa_errors, aa2)
            fitness.append(f)
            if f >= best_f:
                best_f = f
                best_bpt = model.bpt.copy()

            if f == 1:
                break

            meta.optimize(aa2, f)

        aa2 = model.pessimist(pt)

        f = compute_ac(aa_errors, aa2)
        fitness.append(f)

        t = time.time() - t1

        model.bpt = best_bpt
        aa2 = model.pessimist(pt)

        nok = nok_erroned = 0
        for alt in a:
            if aa(alt.id) != aa2[alt.id]:
                nok += 1
                if alt.id in aa_erroned:
                    nok_erroned += 1

        total = len(a)
        er = float(total-nok) / total

        if aa_erroned:
            erroned_bad = nok_erroned/len(aa_erroned)
        else:
            erroned_bad = 0

        return t, fitness, er, erroned_bad

    def run_one_set_of_tests(self, n_alts, n_crit, n_cat, nloop, nmodel,
                             nerrors):
        fitness = { nc: { na: { ncat: { seed: [ 1 for i in range(nloop+1) ]
                                        for seed in seeds }
                                for ncat in n_cat }
                          for na in n_alts }
                    for nc in n_crit }

        print('\nna\tnc\tncat\tseed\tnloop\tnloopu\tnmodels\tnerrors\tf_end\tf_best\terr\terr_bad\ttime')
        for na, nc, ncat, seed in product(n_alts, n_crit, n_cat, seeds):
            t, f, er, eb = self.run_metaheuristic(na, nc, ncat, seed, nloop,
                                                  nmodel, nerrors)
            fitness[nc][na][ncat][seed][0:len(f)] = f
            print("%d\t%d\t%d\t%d\t%d\t%d\t%d\t%g\t%-6.5f\t%-6.5f\t%-6.5f" \
                  "\t%-6.5f\t%-6.5f" \
                  % (na, nc, ncat, seed, nloop, len(f)-1, nmodel, nerrors,
                  f[-1], max(f), er, eb, t))

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

    def test001_two_cat_no_errors(self):
        n_alts = [ 10000 ]
        n_crit = [ 5, 7, 10 ]
        n_cat = [ 2 ]
        nloop = 1000
        nmodel = 1
        nerrors = 0

        self.run_one_set_of_tests(n_alts, n_crit, n_cat, nloop, nmodel, nerrors)

    def test002_two_cat_10pc_errors(self):
        n_alts = [ 10000 ]
        n_crit = [ 5, 7, 10 ]
        n_cat = [ 2 ]
        nloop = 1000
        nmodel = 1
        nerrors = 0.1

        self.run_one_set_of_tests(n_alts, n_crit, n_cat, nloop, nmodel, nerrors)

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(metaheuristic_profiles_tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
