from __future__ import division
import sys
sys.path.insert(0, "..")
import math
import random

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
        self.b0 = pt_sorted.get_worst_ap()
        self.bp = pt_sorted.get_best_ap()
        self.compute_interval_ratios(3)

    def compute_interval_ratios(self, n):
        self.nintervals = n
        intervals = []
        for i in range(n-1):
            intervals += [ math.exp(i+1) ]
        s = sum(intervals)
        self.interval_ratios = [ i/s for i in intervals ] + [ 0.9 ]
#        print self.interval_ratios

    def update_intervals(self, fitness):
        if fitness > 0.99:
            self.compute_interval_ratios(7)
        elif fitness > 0.95:
            self.compute_interval_ratios(5)
        elif fitness > 0.9:
            self.compute_interval_ratios(4)
        else:
            self.compute_interval_ratios(3)

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
        intervals = [ profile ] + intervals
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
        intervals = [ profile ] + intervals
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

        moved = False
        max_val = 0

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
            r = random.random()

            if h_below[i_b] > h_above[i_a]:
                size = (p_perfs[cid] - b_perfs[cid])
                if r < h_below[i_b]:
                    p_perfs[cid] = p_perfs[cid] \
                                    - self.interval_ratios[i_b] * size
                    moved = True
                elif moved is False and h_below[i_b] > max_val:
                    max_val = h_below[i_b]
                    max_cid = cid
                    max_move = - self.interval_ratios[i_b] * size
            elif h_below[i_b] < h_above[i_a]:
                size = (a_perfs[cid] - p_perfs[cid])
                if r < h_above[i_a]:
                    p_perfs[cid] = p_perfs[cid] \
                                    + self.interval_ratios[i_a] * size
                    moved = True
                elif moved is False and h_above[i_a] > max_val:
                    max_val = h_above[i_a]
                    max_cid = cid
                    max_move = self.interval_ratios[i_a] * size
            elif r > 0.5:
                size = (p_perfs[cid] - b_perfs[cid])
                r2 = random.random()
                if r2 < h_below[i_b]:
                    p_perfs[cid] = p_perfs[cid] \
                                    - self.interval_ratios[i_b] * size
                    moved = True
                elif moved is False and h_below[i_b] > max_val:
                    max_val = h_below[i_b]
                    max_cid = cid
                    max_move = - self.interval_ratios[i_b] * size
            elif r < 0.5:
                size = (a_perfs[cid] - p_perfs[cid])
                r2 = random.random()
                if r2 < h_above[i_a]:
                    p_perfs[cid] = p_perfs[cid] \
                                    + self.interval_ratios[i_a] * size
                    moved = True
                elif moved is False and h_above[i_a] > max_val:
                    max_val = h_above[i_a]
                    max_cid = cid
                    max_move = self.interval_ratios[i_a] * size

        if moved is False and max_val > 0:
#            print 'move', max_val
            p_perfs[max_cid] = p_perfs[max_cid] + max_move

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

    def optimize(self, aa, fitness):
        profiles = self.model.profiles
        for i, profile in enumerate(profiles):
            below, above = self.get_below_and_above_profiles(i)
            cat_b, cat_a = self.cat_ranked[i], self.cat_ranked[i+1]
            self.update_intervals(fitness)
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

    c = generate_random_criteria(7)
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
    print("lambda: %.7s" % lbda)

    bpt2 = generate_random_categories_profiles(b, c, 0123)
    model2 = electre_tri(c, cv, bpt2, lbda, cat)
    print('Original random profiles')
    print('========================')
    bpt2.display(criterion_ids=cids)

    pt_sorted = sorted_performance_table(pt)
    meta = meta_electre_tri_profiles(model2, pt_sorted, cat, aa)

    for i in range(1, 501):
        aa2 = model2.pessimist(pt)

        f = compute_fitness(aa, aa2)
        print('%d: fitness: %g' % (i, f))
        bpt2.display(criterion_ids=cids)
        if f == 1:
            break

        meta.optimize(aa2, f)

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
