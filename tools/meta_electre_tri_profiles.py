from __future__ import division
import sys
sys.path.insert(0, "..")
import math
from tools.utils import get_worst_alternative_performances
from tools.utils import get_best_alternative_performances

class meta_electre_tri_profiles():

    def __init__(self, model, pt_sorted, cat, aa_ori):
        self.model = model
        self.nprofiles = len(model.profiles)
        self.pt_sorted = pt_sorted
        self.aa_ori = aa_ori
        self.cat = self.categories_to_rank(cat)
        self.aa_by_cat = self.sort_alternative_by_category(aa_ori)
        self.b0 = get_worst_alternative_performances(pt, model.criteria)
        self.bp = get_best_alternative_performances(pt, model.criteria)
        self.nintervals = 3
        self.interval_ratios = self.compute_interval_ratios(self.nintervals)

    def compute_interval_ratios(self, n):
        intervals = []
        for i in range(n):
            intervals += [ math.exp((i+1)) ]
        s = sum(intervals)
        return [ i/s for i in intervals ]

    def categories_to_rank(self, cat):
        return { c.id: c.rank for c in cat }

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

    def compute_above_histogram(self, c, p_num, profile, below, above):
        h_above_ok = {}
        h_above_nok = {}
        size = above-profile
        intervals = [ profile + self.interval_ratios[i]*size \
                      for i in range(self.nintervals) ]
        intervals = [ profile ] + intervals + [ above ]
        ok = nok = 0
        for i in range(self.nintervals):
            alts = self.pt_sorted.get_middle(c.id, intervals[i],
                                            intervals[i+1])
            for a in alts:
                if p_num+1 == self.cat[self.aa_ori(a)]:
                    ok += 1
                else:
                    nok += 1

            h_above_ok[i] = ok
            h_above_nok[i] = nok

        return h_above_ok, h_above_nok

    def compute_below_histogram(self, c, p_num, profile, below, above):
        h_below_ok = {}
        h_below_nok = {}
        size = profile-below
        intervals = [ profile - self.interval_ratios[i]*size \
                      for i in range(self.nintervals) ]
        intervals = [ profile ] + intervals + [ below ]
        ok = nok = 0
        for i in range(self.nintervals):
            alts = self.pt_sorted.get_middle(c.id, intervals[i+1],
                                            intervals[i])
            for a in alts:
                if p_num+1 == self.cat[self.aa_ori(a)]:
                    ok += 1
                else:
                    nok += 1

            h_below_ok[i] = ok
            h_below_nok[i] = nok

        return h_below_ok, h_below_nok

    def compute_histograms(self, p_num, profile, below, above):
        criteria = self.model.criteria
        p_perfs = profile.performances
        a_perfs = above.performances
        b_perfs = below.performances
        for c in criteria:
            b_ok, b_nok = self.compute_below_histogram(c, p_num,
                                p_perfs[c.id], b_perfs[c.id], a_perfs[c.id])
            a_ok, a_nok = self.compute_above_histogram(c, p_num,
                                p_perfs[c.id], b_perfs[c.id], a_perfs[c.id])

            print a_ok, b_ok

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
            self.compute_histograms(i+1, profile, below, above)

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


    a = generate_random_alternatives(1000)
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

    pt_sorted = sorted_performance_table(pt)
    meta = meta_electre_tri_profiles(model, pt_sorted, cat, aa)
    meta.optimize(aa)
