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
from tools.utils import add_errors_in_affectations

seeds = [ 123, 456, 789, 12, 345, 678, 901, 234, 567, 890 ]

def variable_number_alternatives_and_criteria(ncat, er=0):
    n_alts = [ i*1000 for i in range(1, 11) ]
    n_crit = [ i for i in range(2,21) ]
    n_alts = [ i*1000 for i in range(1, 11) ]
    n_crit = [ 5 ]

    print('\nnc\tna\terr\tseed\tobj\terrors\ttime')

    objectives = { nc: {na: dict() for na in n_alts} for nc in n_crit }
    times = { nc: {na: dict() for na in n_alts} for nc in n_crit }
    errors = { nc: {na: dict() for na in n_alts} for nc in n_crit }
    errors_min = { nc: {na: dict() for na in n_alts} for nc in n_crit }
    errors_max = { nc: {na: dict() for na in n_alts} for nc in n_crit }
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
        aa_errors = model.pessimist(pt)

        add_errors_in_affectations(aa_errors, cat.get_ids(), er)

        t1 = time.time()
        lp_weights = lp_electre_tri_weights(a, c, cv, aa_errors, pt,
                                            cat, b, bpt, 0.0001)
        obj, cv_learned, lbda_learned = lp_weights.solve()
        t2 = time.time()

        objectives[nc][na][seed] = obj
        times[nc][na][seed] = t2-t1

        model.cv = cv_learned
        model.lbda = lbda_learned
        aa_learned = model.pessimist(pt)

        total = len(a)
        nok = 0
        a_assign = { alt.alternative_id: alt.category_id for alt in aa }
        a_assign2 = { alt.alternative_id: alt.category_id
                      for alt in aa_learned}
        for alt in a:
            if a_assign[alt.id] != a_assign2[alt.id]:
                nok += 1

        e = nok/total
        errors[nc][na][seed] = nok/total

        print("%d\t%d\t%d\t%-6.4f\t%s\t%-6.4f\t%-6.5f\t%-6.5f" % (nc, na,
              ncat, er, seed, obj, e, t2-t1))

    print('Summary')
    print('========')
    print("nseeds: %d" % len(seeds))
    print('nc\tna\tncat\terr\tobj\terr_avg\terr_min\terr_max\ttime')
    for nc, na in product(n_crit, n_alts):
        obj = sum(objectives[nc][na].values())/len(seeds)
        tim = sum(times[nc][na].values())/len(seeds)
        err = sum(errors[nc][na].values())/len(seeds)
        err_min = min(errors[nc][na].values())
        err_max = max(errors[nc][na].values())
        print("%d\t%d\t%d\t%-6.5f\t%-6.4f\t%-6.5f\t%-6.5f\t%-6.5f\t%-6.5f"
              % (nc, na, ncat, er, obj, err, err_min, err_max, tim))

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
    suite = loader.loadTestsFromTestCase(tests_lp_electre_tri_weights)
    unittest.TextTestRunner(verbosity=2).run(suite)
