from __future__ import division
import sys
sys.path.insert(0, "..")

class meta_electre_tri_profiles():

    def __init__(self, model, pt_sorted, aa_ori):
        self.model = model
        self.pt_sorted = pt_sorted
        self.aa_ori = aa_ori

    def optimize(self, aa):
        for a in aa:
            print a
        pass

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


    a = generate_random_alternatives(500)
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
    meta = meta_electre_tri_profiles(model, pt_sorted, aa)
    meta.optimize(aa)
