from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
from pymcda.types import AlternativeAssignment
from pymcda.types import AlternativesAssignments

class flowsort():

    POSITIVE_FLOW = 0x01
    NEGATIVE_FLOW = 0x02

    def __init__(self, criteria, crit_weights, cat_profiles, prof_pt,
                 pref_functions):
        self.criteria = criteria
        self.crit_weights = crit_weights
        self.cat_profiles = cat_profiles
        self.prof_pt = prof_pt
        self.pref_functions = pref_functions

    def pi(self, x, y):
        p = 0
        for c in self.crit_weights:
            val = self.pref_functions[c.id].y(x.performances[c.id])
            p += val * c.value

        return p

    def flow(self, x, ri, mask = POSITIVE_FLOW | NEGATIVE_FLOW):
        f = 0
        for y in ri:
            if mask & self.POSITIVE_FLOW:
                f += self.pi(x, y)
            if mask & self.NEGATIVE_FLOW:
                f -= self.pi(y, x)

        if not mask & self.POSITIVE_FLOW:
            f = -f

        return f / (len(ri) - 1)

    def get_assignment(self, ap):
        ri = self.prof_pt.copy()
        ri.append(ap)

        phi_ap = self.flow(ap, ri)
        profiles = self.cat_profiles.get_ordered_profiles()
        categories = self.cat_profiles.get_ordered_categories()
        for i, profile in enumerate(profiles):
            if self.flow(self.prof_pt[profile], ri) > phi_ap:
                return AlternativeAssignment(ap.id, categories[i])

        return AlternativeAssignment(ap.id, categories[i + 1])

    def get_assignments(self, pt):
        aas = AlternativesAssignments([])
        for ap in pt:
            aas.append(self.get_assignment(ap))

        return aas

if __name__ == "__main__":
    import random
    from pymcda.generate import generate_criteria
    from pymcda.generate import generate_random_criteria_weights
    from pymcda.generate import generate_categories
    from pymcda.generate import generate_categories_profiles
    from pymcda.generate import generate_alternatives
    from pymcda.generate import generate_random_performance_table
    from pymcda.generate import generate_random_profiles
    from pymcda.generate import generate_random_plinear_preference_function

    random.seed(123)

    criteria = generate_criteria(5)
    crit_weights = generate_random_criteria_weights(criteria)
    categories = generate_categories(5)
    cat_profiles = generate_categories_profiles(categories)

    a = generate_alternatives(100)
    pt = generate_random_performance_table(a, criteria)
    ap_best = pt.get_best(criteria)
    ap_worst = pt.get_worst(criteria)

    b = cat_profiles.get_ordered_profiles()
    bpt = generate_random_profiles(b, criteria)
    pf = generate_random_plinear_preference_function(criteria, ap_worst,
                                                     ap_best)
    print(crit_weights)
    print(categories)
    print(cat_profiles)
    print(bpt)
    print(pf)

    model = flowsort(criteria, crit_weights, cat_profiles, bpt, pf)
    print(model.get_assignments(pt))
