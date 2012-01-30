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
        self.epsilon = 0.0000
        self.delta = 0.0001
        self.lp = pymprog.model('lp_elecre_tri_weights')
        #self.lp.verb=True
        self.generate_constraints()
        self.add_objective()

    def generate_constraints(self):
        m = len(self.alternatives)
        n = len(self.criteria)

        # Initialize variables
        self.w = self.lp.var(xrange(n), 'w', bounds=(0, 1))
        self.x = self.lp.var(xrange(m), 'x', bounds=(-1, 1))
        self.y = self.lp.var(xrange(m), 'y', bounds=(-1, 1))
        self.lbda = self.lp.var(name='lambda', bounds=(0.5, 1))
        self.alpha = self.lp.var(name='alpha', bounds=(-1, 1))

        for i, a in enumerate(self.alternatives):
            a_perfs = self.pt(a.id)
            cat_id = self.alternative_affectations(a.id)
            cat_rank = self.categories(cat_id).rank

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
                           == self.lbda - self.delta)

            # alpha <= x_i
            # alpha <= y_i
            self.lp.st(self.x[i] >= self.alpha)
            self.lp.st(self.y[i] >= self.alpha)

        for j in range(n):
            self.lp.st(self.w[j] <= 0.5)

        # sum w_j = 1
        self.lp.st(sum(self.w[j] for j in range(n)) == 1)

    def add_objective(self):
        m = len(self.alternatives)

        self.lp.max(self.alpha \
                    + self.epsilon*sum([self.x[i] for i in range(m)])   \
                    + self.epsilon*sum([self.y[i] for i in range(m)]))

    def solve(self):
        self.lp.solve()

        status = self.lp.status()
        if status != 'opt':
            print("Solver status: %s" % self.lp.status())
            #FIXME: raise error

        #print(self.lp.reportKKT())
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
    import time
    from tools.generate_random import generate_random_alternatives
    from tools.generate_random import generate_random_criteria
    from tools.generate_random import generate_random_criteria_values
    from tools.generate_random import generate_random_performance_table
    from tools.generate_random import generate_random_categories
    from tools.generate_random import generate_random_categories_profiles
    from tools.utils import normalize_criteria_weights
    from tools.utils import add_errors_in_affectations
    from mcda.electre_tri import electre_tri

    # Original Electre Tri model
    a = generate_random_alternatives(2000)
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
    add_errors_in_affectations(aa, cat.get_ids(), 0.000)

    print('Original model')
    print('==============')
    cids = c.get_ids()
    bpt.display(criterion_ids=cids)
    cv.display(criterion_ids=cids)
    print("lambda\t%.7s" % lbda)
    #print(aa)

    lp_weights = lp_elecre_tri_weights(a, c, cv, aa, pt, cat, b, bpt)

    t1 = time.time()
    obj, cv_learned, lbda_learned = lp_weights.solve()
    t2 = time.time()
    print("Computation time: %g secs" % (t2-t1))
    print("Objective: %s" % obj)

    model.cv = cv_learned
    model.lbda = lbda_learned
    aa_learned = model.pessimist(pt)

    print('Learned model')
    print('=============')
    cv.display(criterion_ids=cids, name='w')
    cv_learned.display(header=False, criterion_ids=cids, name='w_learned')
    print("lambda\t%.7s" % lbda_learned)
    #print(aa_learned)

    total = len(a)
    nok = 0
    for alt in a:
        if aa(alt.id) <> aa_learned(alt.id):
            print("Pessimistic affectation of %s mismatch (%s <> %s)" %
                  (str(alt.id), aa(alt.id), aa_learned(alt.id)))
            nok += 1

    print("Good affectations: %3g %%" % (float(total-nok)/total*100))
    print("Bad affectations : %3g %%" % (float(nok)/total*100))
