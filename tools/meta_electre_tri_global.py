from __future__ import division
import sys
sys.path.insert(0, "..")
import random
from mcda.electre_tri import electre_tri
from mcda.types import alternative_affectation, alternatives_affectations
from tools.lp_electre_tri_weights import lp_elecre_tri_weights
from tools.generate_random import generate_random_categories_profiles
from tools.generate_random import generate_random_alternatives
from tools.utils import get_worst_alternative_performances
from tools.utils import get_best_alternative_performances

class meta_electre_tri_global():

    # Input params:
    #   - a: learning alternatives
    #   - c: criteria
    #   - cvals: criteria values
    #   - aa: alternative affectations
    #   - pt : alternative performance table
    #   - cat: categories
    def __init__(self, a, c, cvals, aa, pt, cat):
        self.alternatives = a
        self.criteria = c
        self.criteria_vals = cvals
        self.aa = aa
        self.pt = pt
        self.categories = cat
        self.b0 = get_worst_alternative_performances(pt, c)
        self.bp = get_best_alternative_performances(pt, c)
        self.n_intervals = 3

    def compute_fitness(self, model, aa):
        c_perfs = {c.id:list() for c in model.criteria}
        for i, p in enumerate(model.profiles):
            perfs = p.performances
            for c in model.criteria:
                c_perfs[c.id].append(perfs[c.id])
        for c in model.criteria:
            c_perfs[c.id].insert(0, self.b0.performances[c.id])
            c_perfs[c.id].append(self.bp.performances[c.id])

        # Constructs the intervals
        for c in model.criteria:
            perfs = c_perfs[c.id]
            for h in range(1, len(model.profiles)+1):
                perf_profile = perfs[h];
                perf_profile_inf = perfs[h-1]
                perf_profile_sup = perfs[h+1]
                print perf_profile
                print perf_profile_inf
                print perf_profile_sup
#                c_perfs_interval_min[h][c.id] = []
#                c_perfs_interval_plus[h][c.id] = []
        raise

        total = len(self.alternatives)
        nok = 0
        for a in self.alternatives:
            af = aa(a.id)
            ok = 0
            if af == self.aa(a.id):
                ok = 1
                nok += 1

            perfs = self.pt(a.id)
            for c in model.criteria:
                for i in range(len(model.profiles)):
                    pass

        return nok/total

    def init_one(self):
        model = electre_tri()
        model.criteria = self.criteria
        model.categories = self.categories

        nprofiles = len(self.categories)-1
        self.b = generate_random_alternatives(nprofiles, 'b') # FIXME
        bpt = generate_random_categories_profiles(b, self.criteria)
        model.profiles = bpt
        return model

    def initialization(self, n):
        models = []
        for i in range(n):
            model = self.init_one()
            models.append(model)

        return models

    def loop_one(self, k):
        models_fitness = {}
        for model in self.models:
            lpw = lp_elecre_tri_weights(self.alternatives, self.criteria,
                                        self.criteria_vals, self.aa,
                                        self.pt, self.categories, self.b,
                                        model.profiles)
            sol = lpw.solve()

            #print("Objective value: %d" % sol[0])

            model.cv = sol[1]
            model.lbda = sol[2]

            aa = model.pessimist(self.pt)
            fitness = self.compute_fitness(model, aa)
            models_fitness[model] = fitness

        return models_fitness

    # Input params:
    #   - n: number of loop to do
    #   - m: number of model to generate
    #   - k: k worst criteria to exchange
    def solve(self, n, m, k):
        self.models = self.initialization(m)
        for i in range(n):
            models_fitness = self.loop_one(k)
            m = max(models_fitness, key = lambda a: models_fitness.get(a))
            print(models_fitness[m]),
        print('')

        return m

if __name__ == "__main__":
    import time
    from tools.generate_random import generate_random_alternatives
    from tools.generate_random import generate_random_criteria
    from tools.generate_random import generate_random_criteria_values
    from tools.generate_random import generate_random_performance_table
    from tools.generate_random import generate_random_categories
    from tools.generate_random import generate_random_categories_profiles
    from tools.utils import normalize_criteria_weights
    from tools.utils import display_affectations_and_pt
    from mcda.electre_tri import electre_tri

    # Original Electre Tri model
    a = generate_random_alternatives(10)
    c = generate_random_criteria(5)
    cv = generate_random_criteria_values(c, 4567)
    normalize_criteria_weights(cv)
    pt = generate_random_performance_table(a, c, 1234)

    b = generate_random_alternatives(2, 'b')
    bpt = generate_random_categories_profiles(b, c, 2345)
    cat = generate_random_categories(3)

    lbda = 0.75

    model = electre_tri(c, cv, bpt, lbda, cat)
    aa = model.pessimist(pt)

    print('Original model')
    print('==============')
    cids = c.get_ids()
    bpt.display(criterion_ids=cids)
    cv.display(criterion_ids=cids)
    print("lambda\t%.7s" % lbda)
    #print(aa)

    meta_global = meta_electre_tri_global(a, c, cv, aa, pt, cat)

    t1 = time.time()
    m = meta_global.solve(100, 10, 5)
    t2 = time.time()
    print("Computation time: %g secs" % (t2-t1))

    aa_learned = m.pessimist(pt)

    print('Learned model')
    print('=============')
    m.profiles.display(criterion_ids=cids)
    m.cv.display(criterion_ids=cids)
    print("lambda\t%.7s" % m.lbda)
    #print(aa_learned)

    total = len(a)
    nok = 0
    for alt in a:
        if aa(alt.id) <> aa_learned(alt.id):
            print("Pessimits affectation of %s mismatch (%s <> %s)" %
                  (str(alt.id), aa(alt.id), aa_learned(alt.id)))
            nok += 1

    print("Good affectations: %3g %%" % (float(total-nok)/total*100))
    print("Bad affectations : %3g %%" % (float(nok)/total*100))

    print("Alternatives and affectations")
    display_affectations_and_pt(a, c, [aa, aa_learned], [pt])
