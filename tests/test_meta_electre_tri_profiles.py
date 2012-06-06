from __future__ import division
import sys
sys.path.insert(0, "..")
import unittest
import time
import random
from itertools import product

from mcda.types import alternatives_affectations, performance_table
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
                          nerrors=0, nlearn=1.0):
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

        # Reinitialize the model with bad profiles
        model.bpt = generate_random_profiles(b, c)

        # Select the alternatives used to learn the weights
        a_learn = random.sample(a, int(nlearn*len(a)))
        aa_learn = alternatives_affectations([ aa[alt.id]
                                               for alt in a_learn ])
        pt_learn = performance_table([ pt[alt.id] for alt in a_learn ])

        # Add errors
        aa_err = aa_learn.copy()
        aa_erroned = add_errors_in_affectations(aa_err, cat.get_ids(),
                                                nerrors)

        # Sort the performance table
        pt_sorted = sorted_performance_table(pt_learn)

        t1 = time.time()

        # Run the algorithm
        meta = meta_electre_tri_profiles(model, pt_sorted, cat, aa_err)

        best_f = 0
        best_bpt = model.bpt.copy()
        for k in range(nloop):
            aa2 = model.pessimist(pt)
            f = compute_ac(aa_err, aa2)
            fitness.append(f)
            if f >= best_f:
                best_f = f
                best_bpt = model.bpt.copy()

            if f == 1:
                break

            meta.optimize(aa2, f)

        aa2 = model.pessimist(pt)

        f = compute_ac(aa_err, aa2)
        fitness.append(f)
        if f >= best_f:
            best_f = f
            best_bpt = model.bpt.copy()

        t = time.time() - t1

        model.bpt = best_bpt
        aa2 = model.pessimist(pt)

        nok = nok_erroned = 0
        for alt in a:
            if aa(alt.id) != aa2(alt.id):
                nok += 1
                if alt.id in aa_erroned:
                    nok_erroned += 1

        total = len(a)
        ac = float(total-nok) / total

        erroned_bad = nok_erroned/total

        return t, fitness, ac, erroned_bad

    def run_one_set_of_tests(self, n_alts, n_crit, n_cat, nloop, nmodel,
                             nerrors, nlearn=1.0):
        fitness = { nc: { na: { ncat: { seed: [ 1 for i in range(nloop+1) ]
                                        for seed in seeds }
                                for ncat in n_cat }
                          for na in n_alts }
                    for nc in n_crit }

        print('\nna\tnc\tncat\tseed\tnloop\tnloopu\tnlearn\tnerrors' \
              '\tf_end\tf_best\tac\terr_bad\ttime')
        for na, nc, ncat, seed in product(n_alts, n_crit, n_cat, seeds):
            t, f, ac, eb = self.run_metaheuristic(na, nc, ncat, seed, nloop,
                                                  nlearn, nerrors, nlearn)
            fitness[nc][na][ncat][seed][0:len(f)] = f
            print("%d\t%d\t%d\t%d\t%d\t%d\t%d\t%g\t%-6.5f\t%-6.5f\t%-6.5f" \
                  "\t%-6.5f\t%-6.5f" \
                  % (na, nc, ncat, seed, nloop, len(f)-1, nlearn, nerrors,
                  f[-1], max(f), ac, eb, t))

        print('Summary')
        print('=======')
        print("nseeds: %d" % len(seeds))
        print('na\tnc\tncat\tnseeds\tloop\tnlearn\tf_avg\tf_min\tf_max')
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
                  nc, ncat, len(seeds), loop, nlearn, favg, fmin, fmax))

    def test001_no_errors(self):
        n_alts = [ 10000 ]
        n_crit = [ 5, 7, 10 ]
        n_cat = [ 2, 3 ]
        nloop = 1000
        nmodel = 1
        nerrors = 0

        self.run_one_set_of_tests(n_alts, n_crit, n_cat, nloop, nmodel, nerrors)

    def test002__10pc_errors(self):
        n_alts = [ 10000 ]
        n_crit = [ 5, 7, 10 ]
        n_cat = [ 2, 3 ]
        nloop = 1000
        nmodel = 1
        nerrors = 0.1

        self.run_one_set_of_tests(n_alts, n_crit, n_cat, nloop, nmodel, nerrors)

    def test003_pc_alternatives(self):
        n_alts = [ 10000 ]
        n_crit = [ 5, 7, 10 ]
        n_cat = [ 2, 3 ]
        nloop = 1000
        nmodel = 1
        nerrors = 0

        self.run_one_set_of_tests(n_alts, n_crit, n_cat, nloop, nmodel, nerrors, 1)
        self.run_one_set_of_tests(n_alts, n_crit, n_cat, nloop, nmodel, nerrors, 0.9)
        self.run_one_set_of_tests(n_alts, n_crit, n_cat, nloop, nmodel, nerrors, 0.8)
        self.run_one_set_of_tests(n_alts, n_crit, n_cat, nloop, nmodel, nerrors, 0.7)
        self.run_one_set_of_tests(n_alts, n_crit, n_cat, nloop, nmodel, nerrors, 0.6)
        self.run_one_set_of_tests(n_alts, n_crit, n_cat, nloop, nmodel, nerrors, 0.5)
        self.run_one_set_of_tests(n_alts, n_crit, n_cat, nloop, nmodel, nerrors, 0.4)
        self.run_one_set_of_tests(n_alts, n_crit, n_cat, nloop, nmodel, nerrors, 0.3)
        self.run_one_set_of_tests(n_alts, n_crit, n_cat, nloop, nmodel, nerrors, 0.2)
        self.run_one_set_of_tests(n_alts, n_crit, n_cat, nloop, nmodel, nerrors, 0.1)

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(metaheuristic_profiles_tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
