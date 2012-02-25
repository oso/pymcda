from __future__ import division
import sys
sys.path.insert(0, "..")
import random
import logging
from itertools import product

from mcda.electre_tri import electre_tri
from mcda.types import alternative_affectation, alternatives_affectations
from tools.lp_electre_tri_weights import lp_electre_tri_weights
from tools.generate_random import generate_random_categories_profiles
from tools.generate_random import generate_random_alternatives
from tools.utils import get_worst_alternative_performances
from tools.utils import get_best_alternative_performances

logger = logging.getLogger('meta')
hdlr = logging.StreamHandler()
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

def info(*args):
    logger.info(','.join(map(str, args)))

def debug(*args):
    logger.debug(','.join(map(str, args)))

class heuristic_profiles():

    def __init__(self, model, a, c, pt, aa, b0, bp):
        self.m = model
        self.alternatives = a
        self.criteria = c
        self.pt = pt
        self.aa = aa
        self.b0 = b0
        self.bp = bp

        self.n_intervals = 5

    def compute_histograms(self, aa, current, above, below):
        above_intervals = {}
        below_intervals = {}

        for c in self.m.criteria:
            below_size = current[c.id]-below[c.id]
            above_size = above[c.id]-current[c.id]

            below_intervals[c.id] = [ current[c.id] -
                                      self.intervals_size[i]*below_size
                                      for i in range(self.n_intervals-1) ]
            above_intervals[c.id] = [ current[c.id] +
                                      self.intervals_size[i]*above_size
                                      for i in range(self.n_intervals-1) ]

        debug('current', current)
        debug('below', below_intervals)
        debug('above', above_intervals)

        h_good_l = { c.id: [ 0 for i in range(self.n_intervals)]
                     for c in self.m.criteria }
        h_good_r = { c.id: [ 0 for i in range(self.n_intervals)]
                     for c in self.m.criteria }
        h_bad_l = { c.id: [ 0 for i in range(self.n_intervals)]
                    for c in self.m.criteria }
        h_bad_r = { c.id: [ 0 for i in range(self.n_intervals)]
                    for c in self.m.criteria }
        for ap, c in product(self.pt, self.m.criteria):
            aperf = ap.performances[c.id]
            pperf = current[c.id]
            h_bad_l_c = h_bad_l[c.id]
            h_bad_r_c = h_bad_r[c.id]
            h_good_l_c = h_good_l[c.id]
            h_good_r_c = h_good_r[c.id]

            if aperf > above[c.id]:
                continue
            if aperf < below[c.id]:
                continue

            af = aa(ap.alternative_id)
            af_ori = self.aa(ap.alternative_id)

            rank = self.m.categories(af).rank
            rank_ori = self.m.categories(af_ori).rank

            if aperf > pperf:
                i = len(above_intervals[c.id])
                if rank > rank_ori: # Profile too low
                    h_bad_r_c[i] += 1
                    while i > 0:
                        i -= 1
                        if aperf > above_intervals[c.id][i]:
                            break
                        h_bad_r_c[i] += 1
                elif rank == rank_ori:
                    h_good_r_c[i] += 1
                    while i > 0:
                        i -= 1
                        if aperf >  above_intervals[c.id][i]:
                            break
                        h_good_r_c[i] += 1

            elif aperf < pperf:
                i = len(below_intervals[c.id])
                if rank < rank_ori: #Profile too high
                    h_bad_l_c[i] += 1
                    while i > 0:
                        i -= 1
                        if aperf < below_intervals[c.id][i]:
                            break
                        h_bad_l_c[i] += 1
                elif rank == rank_ori:
                    h_good_l_c[i] += 1
                    while i > 0:
                        i -= 1
                        if aperf < below_intervals[c.id][i]:
                            break
                        h_good_l_c[i] += 1

        return h_bad_l, h_bad_r, h_good_l, h_good_r

    def compute_histo_proba(self, h_bad, h_good):
        histo = []
        for x, y in zip(h_bad, h_good):
            if x+y > 0:
                histo.append(x / (x + y))
            else:
                histo.append(0)
        return histo

    def update_one_profile(self, aa, p_id):
        current = self.m.profiles[p_id].performances

        if p_id == 0:
            below = self.b0.performances
        else:
            below = self.m.profiles[p_id-1].performances

        if p_id == len(self.m.profiles)-1:
            above = self.bp.performances
        else:
            above = self.m.profiles[p_id+1].performances

        histograms = self.compute_histograms(aa, current, above, below)
        h_bad_l, h_bad_r, h_good_l, h_good_r = histograms

        debug(current, h_bad_l, h_bad_r)
        debug(current, h_good_l, h_good_r)

        for c in self.criteria:
            h_bad_l_c = h_bad_l[c.id]
            h_bad_r_c = h_bad_r[c.id]
            h_good_l_c = h_good_l[c.id]
            h_good_r_c = h_good_r[c.id]

            if sum(h_bad_l_c) > sum(h_bad_r_c):
                histo_l = self.compute_histo_proba(h_bad_l_c, h_good_l_c)
                ml = max(histo_l)
                if random.random() > ml:
                    continue
                i = histo_l.index(ml)
                below_size = current[c.id]-below[c.id]
                current[c.id] -= self.intervals_size[i]*below_size
            elif sum(h_bad_l_c) < sum(h_bad_r_c):
                histo_r = self.compute_histo_proba(h_bad_r_c, h_good_r_c)
                mr = max(histo_r)
                if random.random() > mr:
                    continue
                i = histo_r.index(mr)
                above_size = above[c.id]-current[c.id]
                current[c.id] += self.intervals_size[i]*above_size
            else:
                histo_l = self.compute_histo_proba(h_bad_l_c, h_good_l_c)
                histo_r = self.compute_histo_proba(h_bad_r_c, h_good_r_c)
                ml = max(histo_l)
                mr = max(histo_r)

                rdom = random.random()
                if ml > mr and rdom < ml:
                    i = histo_l.index(ml)
                    below_size = current[c.id]-below[c.id]
                    current[c.id] -= self.intervals_size[i]*below_size
                elif ml < mr and rdom < mr:
                    i = histo_r.index(mr)
                    above_size = above[c.id]-current[c.id]
                    current[c.id] += self.intervals_size[i]*above_size
                elif mr == ml and rdom < 0.5:
                    rdom = random.random()
                    if random.random() > ml:
                        continue
                    i = histo_l.index(ml)
                    below_size = current[c.id]-below[c.id]
                    current[c.id] -= self.intervals_size[i]*below_size
                elif mr == ml and rdom > 0.5:
                    if random.random() > mr:
                        continue
                    i = histo_r.index(mr)
                    above_size = above[c.id]-current[c.id]
                    current[c.id] += self.intervals_size[i]*above_size

    def optimize(self, aa):
        k = random.randint(1,10)
        isize = [ k ** i for i in range(self.n_intervals) ]
        self.intervals_size = [ i/sum(isize) for i in isize ]

        c_perfs = {c.id:list() for c in self.m.criteria}
        for i, p in enumerate(self.m.profiles):
            perfs = p.performances
            for c in self.m.criteria:
                c_perfs[c.id].append(perfs[c.id])
        for c in self.m.criteria:
            c_perfs[c.id].insert(0, self.b0.performances[c.id])
            c_perfs[c.id].append(self.bp.performances[c.id])

        for i in range(len(self.m.profiles)):
            self.update_one_profile(aa, i);

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

    def compute_fitness(self, model, aa):
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

    def loop_one(self):
        models_fitness = {}
        for model in self.models:
            lpw = lp_electre_tri_weights(self.alternatives, self.criteria,
                                         self.criteria_vals, self.aa,
                                         self.pt, self.categories, self.b,
                                         model.profiles)
            sol = lpw.solve()

            #print("Objective value: %d" % sol[0])

            model.cv = cv
            model.lbda = lbda

            aa = model.pessimist(self.pt)
            fitness = self.compute_fitness(model, aa)
            models_fitness[model] = fitness
            if fitness == 1:
                return models_fitness

            heuristic = heuristic_profiles(model, self.alternatives,
                                           self.criteria, self.pt, self.aa,
                                           self.b0, self.bp)
            heuristic.optimize(aa)

        return models_fitness

    # Input params:
    #   - n: number of loop to do
    #   - m: number of model to generate
    def solve(self, n, m):
        self.models = self.initialization(m)
        for i in range(n):
            models_fitness = self.loop_one()
            m = max(models_fitness, key = lambda a: models_fitness.get(a))
            info("Iteration %d: best fitness = %f" % (i, models_fitness[m]))
            if models_fitness[m] == 1:
                break;
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
    a = generate_random_alternatives(1000)
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
    m = meta_global.solve(100, 1)
    t2 = time.time()
    print("Computation time: %g secs" % (t2-t1))

    aa_learned = m.pessimist(pt)

    print('Learned model')
    print('=============')
    model.profiles.display(criterion_ids=cids)
    m.profiles.display(header=False, criterion_ids=cids, append='_learned')
    model.cv.display(criterion_ids=cids, name='w')
    m.cv.display(header=False, criterion_ids=cids, name='w_learned')
    print("lambda\t%.7s" % m.lbda)
    #print(aa_learned)

    total = len(a)
    nok = 0
    anok = []
    for alt in a:
        if aa(alt.id) <> aa_learned(alt.id):
            anok.append(alt)
#            print("Pessimits affectation of %s mismatch (%s <> %s)" %
#                  (str(alt.id), aa(alt.id), aa_learned(alt.id)))
            nok += 1

    print("Good affectations: %3g %%" % (float(total-nok)/total*100))
    print("Bad affectations : %3g %%" % (float(nok)/total*100))

    if len(anok) > 0:
        print("Alternatives and affectations")
        display_affectations_and_pt(anok, c, [aa, aa_learned], [pt])
