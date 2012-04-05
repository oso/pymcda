from __future__ import division
import sys
sys.path.insert(0, "..")
import math
import random
from tools.utils import get_worst_alternative_performances
from tools.utils import get_best_alternative_performances

def compute_fitness(aa, aa_learned):
    ok = total = 0
    for a in aa:
        aid = a.alternative_id
        if aa(aid) == aa_learned(aid):
            ok += 1
        total += 1

    return ok/total

class meta_electre_tri_profiles():

    def __init__(self, model, pt_sorted, cat, aa_ori):
        self.model = model
        self.nprofiles = len(model.profiles)
        self.pt_sorted = pt_sorted
        self.aa_ori = aa_ori
        self.cat = self.categories_rank(cat)
        self.cat_ranked = self.rank_categories(cat)
        self.aa_by_cat = self.sort_alternative_by_category(aa_ori)
        self.b0 = get_worst_alternative_performances(pt, model.criteria)
        self.bp = get_best_alternative_performances(pt, model.criteria)
        self.nintervals = 4
        self.interval_ratios = self.compute_interval_ratios(self.nintervals)

    def compute_interval_ratios(self, n):
        intervals = []
        for i in range(n):
            intervals += [ math.exp((i+1)) ]
        s = sum(intervals)
        return [ i/s for i in intervals ]

    def categories_rank(self, cat):
        return { c.id: c.rank for c in cat }

    def rank_categories(self, cat):
        c_rank = { c.id: c.rank for c in cat }
        return sorted([ cat for (cat, rank) in c_rank.items() ])

    def sort_alternative_by_category(self, aa):
        aa_by_cat = {}
        for a in aa:
            aid = a.alternative_id
            cat = self.cat[a.category_id]
            if cat in aa_by_cat:
                aa_by_cat[cat].append(aid)
            else:
                aa_by_cat[cat] = [ aid ]
        return aa_by_cat

    def compute_above_histogram(self, aa, cid, profile, above, cat_b, cat_a):
        h_above = {}
        size = above - profile
        intervals = [ profile + self.interval_ratios[i]*size \
                      for i in range(self.nintervals) ]
        intervals = [ profile ] + intervals + [ above ]
        ok = nok = 0
        for i in range(self.nintervals):
            alts = self.pt_sorted.get_middle(cid, intervals[i],
                                             intervals[i+1])
            for a in alts:
                if aa(a) == self.aa_ori(a) and self.aa_ori(a) == cat_a:
                    ok += 1
                elif aa(a) != self.aa_ori(a) and self.aa_ori(a) == cat_b:
                    nok += 1

            if (ok + nok) > 0:
                h_above[i] = nok / (ok + nok)
            else:
                h_above[i] = 0

        return h_above

    def compute_below_histogram(self, aa, cid, profile, below, cat_b, cat_a):
        h_below = {}
        size = profile - below
        intervals = [ profile - self.interval_ratios[i]*size \
                      for i in range(self.nintervals) ]
        intervals = [ profile ] + intervals + [ below ]
        ok = nok = 0
        for i in range(self.nintervals):
            alts = self.pt_sorted.get_middle(cid, intervals[i+1],
                                             intervals[i])
            for a in alts:
                if aa(a) == self.aa_ori(a) and self.aa_ori(a) == cat_b:
                    ok += 1
                elif aa(a) != self.aa_ori(a) and self.aa_ori(a) == cat_a:
                    nok += 1

            if (ok + nok) > 0:
                h_below[i] = nok / (ok + nok)
            else:
                h_below[i] = 0

        return h_below

    def compute_histograms(self, aa, profile, below, above, cat_b, cat_a):
        criteria = self.model.criteria
        p_perfs = profile.performances
        a_perfs = above.performances
        b_perfs = below.performances

        for c in self.model.criteria:
            cid = c.id
            h_below = self.compute_below_histogram(aa, cid, p_perfs[cid],
                                                   b_perfs[cid], cat_b,
                                                   cat_a)
            h_above = self.compute_above_histogram(aa, cid, p_perfs[cid],
                                                   a_perfs[cid], cat_b,
                                                   cat_a)

            i_b = max(h_below, key=h_below.get)
            i_a = max(h_above, key=h_above.get)
            r = random.random()/2

            if h_below[i_b] > h_above[i_a]:
                if r < h_below[i_b]:
                    size = (p_perfs[cid] - b_perfs[cid])
                    p_perfs[cid] = p_perfs[cid] \
                                    - self.interval_ratios[i_b] * size
            elif h_below[i_b] < h_above[i_a]:
                if r < h_above[i_a]:
                    size = (a_perfs[cid] - p_perfs[cid])
                    p_perfs[cid] = p_perfs[cid] \
                                    + self.interval_ratios[i_a] * size
            elif r > 0.5:
                r2 = random.random()
                if r2 < h_below[i_b]:
                    size = (p_perfs[cid] - b_perfs[cid])
                    p_perfs[cid] = p_perfs[cid] \
                                    - self.interval_ratios[i_b] * size
            elif r < 0.5:
                r2 = random.random()
                if r2 < h_above[i_a]:
                    size = (a_perfs[cid] - p_perfs[cid])
                    p_perfs[cid] = p_perfs[cid] \
                                    + self.interval_ratios[i_a] * size

    def get_below_and_above_profiles(self, i):
        profiles = self.model.profiles

        if i == 0:
            below = self.b0
        else:
            below = profiles[i-1]

        if i == self.nprofiles-1:
            above = self.bp
        else:
            above = profiles[i+1]

        return below, above

    def optimize(self, aa):
        profiles = self.model.profiles
        for i, profile in enumerate(profiles):
            below, above = self.get_below_and_above_profiles(i)
            cat_b, cat_a = self.cat_ranked[i], self.cat_ranked[i+1]
            self.compute_histograms(aa, profile, below, above, cat_b, cat_a)

if __name__ == "__main__":
    from tools.generate_random import generate_random_alternatives
    from tools.generate_random import generate_random_criteria
    from tools.generate_random import generate_random_criteria_values
    from tools.generate_random import generate_random_performance_table
    from tools.generate_random import generate_random_categories
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

    bpt2 = generate_random_categories_profiles(b, c, 0123)
    model2 = electre_tri(c, cv, bpt2, lbda, cat)
    print('Original random profiles')
    print('========================')
    bpt2.display(criterion_ids=cids)

    pt_sorted = sorted_performance_table(pt)
    meta = meta_electre_tri_profiles(model2, pt_sorted, cat, aa)
    meta.optimize(aa)

    for i in range(500):
        aa2 = model2.pessimist(pt)
        bpt2.display(criterion_ids=cids)
        f = compute_fitness(aa, aa2)
        print 'fitness', f
        if f == 1:
            break
        meta.optimize(aa2)
