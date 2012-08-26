from __future__ import division
import sys
sys.path.insert(0, "..")
import unittest
import time
import random
from itertools import product

from mcda.types import alternatives_affectations, performance_table
from mcda.electre_tri import electre_tri
from inference.lp_electre_tri_weights import lp_electre_tri_weights
from tools.generate_random import generate_random_alternatives
from tools.generate_random import generate_random_criteria
from tools.generate_random import generate_random_criteria_values
from tools.generate_random import generate_random_performance_table
from tools.generate_random import generate_random_categories
from tools.generate_random import generate_random_profiles
from tools.generate_random import generate_random_categories_profiles
from tools.utils import compute_ac
from tools.utils import normalize_criteria_weights
from tools.utils import add_errors_in_affectations

seeds = [ 123, 456, 789, 12, 345, 678, 901, 234, 567, 890 ]

def variable_number_alternatives_and_criteria(ncat, er = 0, na_gen = 10000):
    n_alts = [ i*1000 for i in range(1, 11) ]
    n_crit = [ 5, 7, 10]

    print('\nnc\tna\tncat\tna_gen\terr\tseed\tobj\terrors\terr_bad\tca'
          '\tt_total\tt_const\tt_solve')

    objectives = { nc: {na: dict() for na in n_alts} for nc in n_crit }
    times_total = { nc: {na: dict() for na in n_alts} for nc in n_crit }
    times_const = { nc: {na: dict() for na in n_alts} for nc in n_crit }
    times_solve = { nc: {na: dict() for na in n_alts} for nc in n_crit }
    errors = { nc: {na: dict() for na in n_alts} for nc in n_crit }
    errors_min = { nc: {na: dict() for na in n_alts} for nc in n_crit }
    errors_max = { nc: {na: dict() for na in n_alts} for nc in n_crit }
    errors_erroned = { nc: {na: dict() for na in n_alts} for nc in n_crit }
    cas = { nc: {na: dict() for na in n_alts} for nc in n_crit }
    for nc, na, seed in product(n_crit, n_alts, seeds):
        # Generate a random ELECTRE TRI model and assignment examples
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
        model2 = model.copy()
        aa = model.pessimist(pt)

        # Add errors in assignment examples
        aa_err = aa.copy()
        aa_erroned = add_errors_in_affectations(aa_err, cat.get_ids(), er)

        # Run linear program
        t1 = time.time()
        lp_weights = lp_electre_tri_weights(model2, pt, aa_err, cps,
                                            0.0001)
        t2 = time.time()
        obj = lp_weights.solve()
        t3 = time.time()

        objectives[nc][na][seed] = obj
        times_total[nc][na][seed] = t3-t1
        times_const[nc][na][seed] = t2-t1
        times_solve[nc][na][seed] = t3-t2

        # Compute new assignment and classification accuracy
        aa2 = model2.pessimist(pt)
        nok = nok_erroned = 0
        for alt in a:
            if aa(alt.id) != aa2(alt.id):
                nok += 1
                if alt.id in aa_erroned:
                    nok_erroned += 1

        total = len(a)

        e = nok/total
        e_err = nok_erroned / total
        errors[nc][na][seed] = nok / total
        errors_erroned[nc][na][seed] = e_err

        # Perform the generalization
        a_gen = generate_random_alternatives(na_gen)
        pt_gen = generate_random_performance_table(a_gen, c)
        aa = model.pessimist(pt_gen)
        aa2 = model2.pessimist(pt_gen)
        ca = compute_ac(aa, aa2)
        cas[nc][na][seed] = ca

        print("%d\t%d\t%d\t%d\t%-6.4f\t%s\t%-6.4f\t%-6.5f\t%-6.5f"
              "\t%-6.5f\t%-6.5f\t%-6.5f\t%-6.5f" % (nc, na, ncat, na_gen,
              er, seed, obj, e, e_err, ca, t3-t1, t2-t1, t3-t2))

    print('Summary')
    print('========')
    print("nseeds: %d" % len(seeds))
    print('nc\tna\tncat\tna_gen\terr\tobj\terr_avg\terr_min\terr_max' \
          '\terr_bad\tca\tca_min\tca_max\tt_total\tt_cons\tt_solve')
    for nc, na in product(n_crit, n_alts):
        obj = sum(objectives[nc][na].values()) / len(seeds)
        tim_tot = sum(times_total[nc][na].values()) / len(seeds)
        tim_con = sum(times_const[nc][na].values()) / len(seeds)
        tim_sol = sum(times_solve[nc][na].values()) / len(seeds)
        err = sum(errors[nc][na].values()) / len(seeds)
        err_min = min(errors[nc][na].values())
        err_max = max(errors[nc][na].values())
        err_erroned = sum(errors_erroned[nc][na].values()) / len(seeds)
        ca = sum(cas[nc][na].values()) / len(seeds)
        ca_min = min(cas[nc][na].values())
        ca_max = max(cas[nc][na].values())
        print("%d\t%d\t%d\t%d\t%-6.5f\t%-6.4f\t%-6.5f\t%-6.5f\t%-6.5f"
              "\t%-6.5f\t%-6.5f\t%-6.5f\t%-6.5f\t%-6.5f\t%-6.5f\t%-6.5f" \
              % (nc, na, ncat, na_gen, er, obj, err, err_min, err_max,
              err_erroned, ca, ca_min, ca_max, tim_tot, tim_con, tim_sol))

class tests_lp_electre_tri_weights(unittest.TestCase):

    def test001_two_categories(self):
        variable_number_alternatives_and_criteria(2)

    def test002_three_categories(self):
        variable_number_alternatives_and_criteria(3)

    def test003_four_categories(self):
        variable_number_alternatives_and_criteria(4)

    def test004_five_categories(self):
        variable_number_alternatives_and_criteria(5)

class tests_lp_electre_tri_weights_with_errors(unittest.TestCase):

    def test001_two_categories_errors_10pc(self):
        variable_number_alternatives_and_criteria(2, 0.1)

    def test002_two_categories_errors_20pc(self):
        variable_number_alternatives_and_criteria(2, 0.2)

    def test003_two_categories_errors_30pc(self):
        variable_number_alternatives_and_criteria(2, 0.3)

    def test004_two_categories_errors_40pc(self):
        variable_number_alternatives_and_criteria(2, 0.4)

    def test005_three_categories_errors_10pc(self):
        variable_number_alternatives_and_criteria(3, 0.1)

    def test006_three_categories_errors_20pc(self):
        variable_number_alternatives_and_criteria(3, 0.2)

    def test007_three_categories_errors_30pc(self):
        variable_number_alternatives_and_criteria(3, 0.3)

    def test008_three_categories_errors_40pc(self):
        variable_number_alternatives_and_criteria(3, 0.4)

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite1 = loader.loadTestsFromTestCase(tests_lp_electre_tri_weights)
    suite2 = loader.loadTestsFromTestCase(tests_lp_electre_tri_weights_with_errors)
    alltests = unittest.TestSuite([suite1, suite2])
    unittest.TextTestRunner(verbosity=2).run(alltests)
