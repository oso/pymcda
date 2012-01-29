import sys
sys.path.insert(0, "..")
import pymprog
from mcda.types import criterion_value, criteria_values

class lp_elecre_tri_weights():

    # Input params:
    #   - a: learning alternatives
    #   - c: criteria
    #   - cvals: criteria values
    #   - aa: alternative affectations
    #   - pt : alternative performance table
    #   - cat: categories
    #   - b: ordered categories profiles
    #   - bpt: profiles performance
    def __init__(self, a, c, cv, aa, pt, cat, b, bpt):
        self.alternatives = a
        self.criteria = c
        self.criteria_vals = cv
        self.alternative_affectations = aa
        self.pt = pt
        self.categories = cat
        self.profiles = b
        self.bpt = bpt
        self.epsilon = 0
        self.lp = pymprog.model('lp_elecre_tri_weights')
        self.lp.solvopt(verbosity=2)
        self.generate_constraints()
        self.add_objective()

    def generate_constraints(self):
        m = len(self.alternatives)
        n = len(self.criteria)

        # Initialize variables
        self.w = self.lp.var(xrange(n), 'w', bounds=(0, 1))
        self.x = self.lp.var(xrange(m), 'x')
        self.y = self.lp.var(xrange(m), 'y')
        self.lbda = self.lp.var(bounds=(0.5, 1))
        self.alpha = self.lp.var()

        for i, a in enumerate(self.alternatives):
            a_perfs = self.pt(a.id)
            cat_rank = self.alternative_affectations(a.id)
#            print cat_id
#            cat = self.categories(cat_id)

            # sum(w_j(a_i,b_h-1) - x_i = lbda
            if cat_rank > 1:
                lower_profile = self.profiles[cat_rank-2]
                b_perfs = self.bpt(lower_profile.id)

                j_outrank = []
                for j, c in enumerate(self.criteria):
                    c_id = c.id
                    if a_perfs(c_id) >= b_perfs(c_id):
                        j_outrank.append(j)

                self.lp.st(sum(self.w[j] for j in j_outrank) - self.x[i] \
                           == self.lbda)

            # sum(w_j(a_i,b_h) + y_i = lbda
            if cat_rank < len(self.categories):
                upper_profile = self.profiles[cat_rank-1]
                b_perfs = self.bpt(upper_profile.id)

                j_outrank = []
                for j, c in enumerate(self.criteria):
                    c_id = c.id
                    if a_perfs(c_id) >= b_perfs(c_id):
                        j_outrank.append(j)

                self.lp.st(sum(self.w[j] for j in j_outrank) + self.y[i] \
                           == self.lbda)

            # alpha <= x_i
            # alpha <= y_i
            self.lp.st(self.x[i] >= self.alpha)
            self.lp.st(self.y[i] >= self.alpha)

        # sum w_j = 1
        self.lp.st(sum(self.w[j] for j in range(n)) == 1)

    def add_objective(self):
        m = len(self.alternatives)

        self.lp.max(self.alpha \
                    + self.epsilon*sum([self.x[i] + self.y[i] \
                    for i in range(m)]))

    def solve(self):
        self.lp.solve()

        print(self.lp.reportKKT())
        obj = self.lp.vobj()

        cvs = criteria_values()
        for j, c in enumerate(self.criteria):
            cv = criterion_value()
            cv.criterion_id = c.id
            cv.value = float(self.w[j].primal)
            cvs.append(cv)

        lbda = float(self.lbda.primal)

        return obj, cvs, lbda

if __name__ == "__main__":
    from tools.generate_random import generate_random_alternatives
    from tools.generate_random import generate_random_criteria
    from tools.generate_random import generate_random_criteria_values
    from tools.generate_random import generate_random_performance_table
    from tools.generate_random import generate_random_categories
    from tools.generate_random import generate_random_categories_profiles
    from tools.utils import normalize_criteria_weights
    from mcda.electre_tri import electre_tri

    # Original Electre Tri model
    a = generate_random_alternatives(1000)
    c = generate_random_criteria(5)
    cv = generate_random_criteria_values(c, 4567)
    normalize_criteria_weights(cv)
    pt = generate_random_performance_table(a, c, 1234)

    b = generate_random_alternatives(2, 'b')
    bpt = generate_random_categories_profiles(b, c, 2345)
    print bpt
    cat = generate_random_categories(3)

    lbda = 0.75

    model = electre_tri(c, cv, bpt, lbda)
    aa = model.pessimist(pt)

    print(cv)
    print(lbda)
    #print(aa)

    lp_weights = lp_elecre_tri_weights(a, c, cv, aa, pt, cat, b, bpt)
    obj, cv_learned, lbda_learned = lp_weights.solve()
    model.cv = cv_learned
    model.lbda = lbda_learned
    aa_learned = model.pessimist(pt)

    print(cv_learned)
    print(lbda_learned)
    #print(aa_learned)

    total = len(a)
    nok = 0
    for alt in a:
        if aa(alt) <> aa_learned(alt):
            print("Pessimits affectation of %s mismatch (%d <> %d)" %
                  (str(key), affectations(key),
                  expected_affectations(key)))
            nok += 1

    print("Good affectations: %3g %%" % (float(total-nok)/total*100))
    print("Bad affectations : %3g %%" % (float(nok)/total*100))
