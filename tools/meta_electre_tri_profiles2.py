from __future__ import division
import sys
sys.path.insert(0, "..")
import math
import random

from mcda.types import performance_table
from tools.sorted import sorted_performance_table

def get_wrong_assignment(aa, aa_learned):
    l = list()
    for a in aa:
        aid = a.alternative_id
        if aa(aid) != aa_learned(aid):
            l.append(aid)
    return l

def compute_fitness(aa, aa_learned):
    ok = total = 0
    for a in aa:
        aid = a.alternative_id
        if aa(aid) == aa_learned(aid):
            ok += 1
        total += 1
    return ok/total

class meta_greedy_electre_tri_profiles():

    def __init__(self, model, pt, aa_ori):
        self.model = model
        self.nprofiles = len(model.profiles)
        self.pt = pt
        self.pt_dict = { ap.alternative_id: ap for ap in pt}
        self.pt_sorted = sorted_performance_table(pt)
        self.nalternatives = len(self.pt)
        self.aa_ori = aa_ori
        self.b0 = self.pt_sorted.get_worst_ap()
        self.bp = self.pt_sorted.get_best_ap()
        self.intervals = self.compute_intervals()

    def compute_intervals(self):
        intervals = {}
        for c in self.model.criteria:
            cid = c.id
            interval = self.bp.performances[cid] - self.b0.performances[cid]
            intervals[cid] = float(interval) / (len(self.model.categories))
        return intervals

    def compute_models_fitness(self, models):
        mf = {}
        for m in models:
            a = m.pessimist(self.pt)
            f = compute_fitness(a, self.aa_ori)
            mf[m] = f

        return mf

    def generate_random_models(self, n, aa, fitness):
        models = [ self.model.copy() for i in range(n) ]
        models_alternatives = { m: list() for m in models }
        models_aa = { m: aa.copy() for m in models }
        models_fitness = { m: fitness for m in models }

        for i in range(len(self.model.profiles)):
            below, above = self.get_below_and_above_profiles(i)
            for c in self.model.criteria:
                interval = (1 - fitness) * self.intervals[c.id]
                for m in models:
                    r = random.randint(-10, 10)
                    p = m.bpt[self.model.profiles[i]].performances

                    old = p[c.id]
                    p[c.id] += interval * (r/10)
                    if p[c.id] < below.performances[c.id]:
                        p[c.id] = below.performances[c.id]
                    if p[c.id] > above.performances[c.id]:
                        p[c.id] = above.performances[c.id]

                    aids = self.pt_sorted.get_middle(c.id, old, p[c.id])[0]
                    models_alternatives[m].extend(aids)

        for m in models:
            aids = list(set(models_alternatives[m]))
            pt_aids = performance_table([ self.pt_dict[aid]
                                          for aid in aids ])
            aa_aids = m.pessimist(pt_aids)
            models_aa[m].update(aa_aids)

            l = len(aids)
            ok = 0
            for aid in aids:
                if aa(aid) != aa_aids(aid):
                    if self.aa_ori(aid) == aa_aids(aid):
                        ok += 1
                    else:
                        ok -= 1

            models_fitness[m] += (ok / self.nalternatives)

        return models_fitness, models_aa

    def get_below_and_above_profiles(self, i):
        profiles = self.model.profiles
        bpt = self.model.bpt

        if i == 0:
            below = self.b0
        else:
            below = bpt[profiles[i-1]]

        if i == self.nprofiles-1:
            above = self.bp
        else:
            above = bpt[profiles[i+1]]

        return below, above

    def optimize(self, aa, f, n):
        f = compute_fitness(self.aa_ori, aa)
        models_fitness, models_aa = self.generate_random_models(n, aa, f)
        m = max(models_fitness, key = lambda a: models_fitness.get(a))
        self.model.bpt = m.bpt
        return models_aa[m], models_fitness[m]

if __name__ == "__main__":
    from tools.generate_random import generate_random_alternatives
    from tools.generate_random import generate_random_criteria
    from tools.generate_random import generate_random_criteria_values
    from tools.generate_random import generate_random_performance_table
    from tools.generate_random import generate_random_categories
    from tools.generate_random import generate_random_profiles
    from tools.generate_random import generate_random_categories_profiles
    from tools.utils import normalize_criteria_weights
    from tools.utils import display_affectations_and_pt
    from tools.sorted import sorted_performance_table
    from mcda.electre_tri import electre_tri

    a = generate_random_alternatives(10000)

    c = generate_random_criteria(5)
    cv = generate_random_criteria_values(c, 4567)
    normalize_criteria_weights(cv)
    pt = generate_random_performance_table(a, c, 1234)

    b = generate_random_alternatives(1, 'b')
    bpt = generate_random_profiles(b, c, 2345)
    cat = generate_random_categories(2)
    cps = generate_random_categories_profiles(cat)

    lbda = 0.75

    model = electre_tri(c, cv, bpt, lbda, cps)
    aa = model.pessimist(pt)

    print('Original model')
    print('==============')
    cids = c.get_ids()
    bpt.display(criterion_ids=cids)
    cv.display(criterion_ids=cids)
    print("lambda: %.7s" % lbda)

    bpt2 = generate_random_profiles(b, c, 0123)
    model2 = electre_tri(c, cv, bpt2, lbda, cps)
    print('Original random profiles')
    print('========================')
    bpt2.display(criterion_ids=cids)

    pt_sorted = sorted_performance_table(pt)
    meta = meta_greedy_electre_tri_profiles(model2, pt, aa)

    aa2 = model2.pessimist(pt)
    f = compute_fitness(aa, aa2)
    for i in range(1, 501):
        print('%d: fitness: %g' % (i, f))
        model2.bpt.display(criterion_ids=cids)
        if f == 1:
            break

        aa2, f = meta.optimize(aa2, f, 20)

    print('Learned model')
    print('=============')
    print("Number of iterations: %d" % i)
    bpt2.display(criterion_ids=cids)
    cv.display(criterion_ids=cids)
    print("lambda: %.7s" % lbda)

    total = len(a)
    nok = 0
    anok = []
    for alt in a:
        if aa(alt.id) != aa2(alt.id):
            anok.append(alt)
            nok += 1

    print("Good affectations: %3g %%" % (float(total-nok)/total*100))
    print("Bad affectations : %3g %%" % (float(nok)/total*100))

    if len(anok) > 0:
        print("Alternatives wrongly assigned:")
        display_affectations_and_pt(anok, c, [aa, aa2], [pt])
