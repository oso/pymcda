from __future__ import division
import sys
sys.path.insert(0, "..")
import random
from itertools import product

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

    def compute_histograms(self, model, aa, current, above, below):
        above_intervals = {}
        below_intervals = {}
        for c in model.criteria:
            below_interval = (current[c.id]-below[c.id])/self.n_intervals
            above_interval = (above[c.id]-current[c.id])/self.n_intervals

            below_intervals[c.id] = [ current[c.id] - i*below_interval
                                      for i in range(1, self.n_intervals) ]
            above_intervals[c.id] = [ current[c.id] + i*above_interval
                                      for i in range(1, self.n_intervals) ]

        histo_l = { c.id: [ 0 for i in range(self.n_intervals)]
                       for c in model.criteria }
        histo_r = { c.id: [ 0 for i in range(self.n_intervals)]
                       for c in model.criteria }
        for ap, c in product(self.pt, model.criteria):
            aperf = ap.performances[c.id]
            pperf = current[c.id]
            histo_l_c = histo_l[c.id]
            histo_r_c = histo_r[c.id]

            if aperf > above[c.id]:
                print 'above', aperf, above[c.id]
                continue
            if aperf < below[c.id]:
                print 'below', aperf, below[c.id]
                continue

            af = aa(ap.alternative_id)
            af_ori = self.aa(ap.alternative_id)

            rank = self.categories(af).rank
            rank_ori = self.categories(af_ori).rank

            if aperf > pperf:
                i = 0
                if rank < rank_ori: # Profile too low
                    histo_r_c[i] += 1
                    while i < len(above_intervals[c.id]):
                        if aperf < above_intervals[c.id][i]:
                            break;
                        i += 1
                        histo_r_c[i] += 1
                elif rank == rank_ori:
                    histo_r_c[i] -= 1
                    while i < len(above_intervals[c.id]):
                        if aperf < above_intervals[c.id][i]:
                            break;
                        i += 1
                        histo_r_c[i] -= 1

            elif aperf < pperf:
                i = 0
                if rank > rank_ori: #Profile too high
                    histo_l_c[i] += 1
                    while i < len(below_intervals[c.id]):
                        if aperf > below_intervals[c.id][i]:
                            break;
                        i += 1
                        histo_l_c[i] += 1
                elif rank == rank_ori:
                    histo_l_c[i] -= 1
                    while i < len(below_intervals[c.id]):
                        if aperf > below_intervals[c.id][i]:
                            break;
                        i += 1
                        histo_l_c[i] -= 1

        return histo_l, histo_r

    def update_one_profile(self, model, aa, p_id):
        current = model.profiles[p_id].performances

        if p_id == 0:
            below = self.b0.performances
        else:
            below = model.profiles[p_id-1].performances

        if p_id == len(model.profiles)-1:
            above = self.bp.performances
        else:
            above = model.profiles[p_id+1].performances

        histo_l, histo_r = self.compute_histograms(model, aa, current,
                                                   above, below)

        print histo_l, histo_r

        for c in self.criteria:
            m = min(histo_l[c.id])
            if m < 0:
                histo_l[c.id] = [i+abs(m) for i in histo_l[c.id]]
            m = min(histo_r[c.id])
            if m < 0:
                histo_r[c.id] = [i+abs(m) for i in histo_r[c.id]]

            sum_r = sum(histo_l[c.id])
            sum_l = sum(histo_r[c.id])
            if sum_l > sum_r:
                interval = (current[c.id]-below[c.id])/self.n_intervals
                r = random.randint(0, sum_l)
                for i in range(self.n_intervals):
                    histo_l[c.id][i]
            elif sum_l < sum_r:
                interval = (above[c.id]-current[c.id])/self.n_intervals
                r = random.randint(0, sum_r)
                print r
            else:
                pass

        print histo_l, histo_r

#        for c_id, h in histograms.iteritems():
#            m = max(h)
#            if m > 0:
#                i = h.index(m)
#                print "*", m, i
#                if i == 0:
#                    current[c_id] = below[c_id]
#                elif i == 2*self.n_intervals-1:
#                    current[c_id] = above[c_id]
#                elif i < self.n_intervals:
#                    current[c_id] = below_intervals[c_id][i-1]
#                else:
#                    i -= self.n_intervals
#                    current[c_id] = above_intervals[c_id][i-1]

#            print ap.alternative_id, c.id

#        interval = (current-below)/self.n_intervals
#        below_intervals = [ below + i*interval
#                            for i in range(1, self.n_intervals) ]
#        below_intervals.insert(0, 

    def update_profiles(self, model, aa):
        c_perfs = {c.id:list() for c in model.criteria}
        for i, p in enumerate(model.profiles):
            perfs = p.performances
            for c in model.criteria:
                c_perfs[c.id].append(perfs[c.id])
        for c in model.criteria:
            c_perfs[c.id].insert(0, self.b0.performances[c.id])
            c_perfs[c.id].append(self.bp.performances[c.id])

        for i in range(len(model.profiles)):
            self.update_one_profile(model, aa, i);

    def compute_fitness(self, model, aa):
#        # Constructs the intervals
#        for c in model.criteria:
#            perfs = c_perfs[c.id]
#            for h in range(1, len(model.profiles)+1):
#                perf_profile = perfs[h];
#                perf_profile_inf = perfs[h-1]
#                perf_profile_sup = perfs[h+1]
#                print perf_profile
#                print perf_profile_inf
#                print perf_profile_sup
#                c_perfs_interval_min[h][c.id] = []
#                c_perfs_interval_plus[h][c.id] = []

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

            self.update_profiles(model, aa)

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
    a = generate_random_alternatives(100)
    c = generate_random_criteria(5)
    cv = generate_random_criteria_values(c, 4567)
    normalize_criteria_weights(cv)
    pt = generate_random_performance_table(a, c, 1234)

    b = generate_random_alternatives(1, 'b')
    bpt = generate_random_categories_profiles(b, c, 2345)
    cat = generate_random_categories(2)

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
    m = meta_global.solve(10, 100, 5)
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
