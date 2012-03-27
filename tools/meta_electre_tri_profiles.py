from __future__ import division
import sys
sys.path.insert(0, "..")
from tools.utils import get_worst_alternative_performances
from tools.utils import get_best_alternative_performances

class meta_electre_tri_profiles():

    def __init__(self, model, pt_sorted, cat, aa_ori):
        self.model = model
        self.nprofiles = len(model.profiles)
        self.pt_sorted = pt_sorted
        self.aa_ori = aa_ori
        self.cat = cat
        self.aa_by_cat = self.sort_alternative_by_category(aa_ori)
        self.b0 = get_worst_alternative_performances(pt, model.criteria)
        self.bp = get_best_alternative_performances(pt, model.criteria)

    def sort_alternative_by_category(self, aa):
        aa_by_cat = {}
        for a in aa:
            aid = a.alternative_id
            cat = self.cat(a.category_id).rank
            if cat in aa_by_cat:
                aa_by_cat[cat].append(aid)
            else:
                aa_by_cat[cat] = [ aid ]
        return aa_by_cat

    def compute_histogram(self, profile, below, above):
        pass

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
            self.compute_histogram(profile, below, above)

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
