from __future__ import division
import sys
import pickle
sys.path.insert(0, "..")
from mcda.types import criterion_value, criteria_values

solver = 'cplex'
verbose = False

if solver == 'glpk':
    import pymprog
elif solver == 'scip':
    from zibopt import scip
elif solver == 'cplex':
    import cplex
else:
    raise NameError('Invalid solver selected')

class lp_electre_tri_weights():

    # Input params:
    #   - a: learning alternatives
    #   - c: criteria
    #   - cvals: criteria values
    #   - aa: alternative affectations
    #   - pt : alternative performance table
    #   - cat: categories
    #   - b: ordered categories profiles
    #   - bpt: profiles performance
    def __init__(self, a, c, cv, aa, pt, cat, b, bpt, delta=0.0001):
        self.alternatives = a
        self.criteria = c
        self.criteria_vals = cv
        self.alternative_affectations = aa
        self.pt = pt
        self.categories = cat
        self.profiles = b
        self.bpt = bpt
        self.delta = delta
        if solver == 'glpk':
            self.lp = pymprog.model('lp_elecre_tri_weights')
            self.lp.verb=verbose
            self.add_variables_glpk()
            self.add_constraints_glpk()
            self.add_objective_glpk()
        elif solver == 'scip':
            self.lp = scip.solver(quiet=not verbose)
            self.add_variables_scip()
            self.add_constraints_scip()
            self.add_objective_scip()
        elif solver == 'cplex':
            self.lp = cplex.Cplex()
            if verbose is False:
                self.lp.set_log_stream(None)
                self.lp.set_results_stream(None)
#                self.lp.set_warning_stream(None)
#                self.lp.set_error_stream(None)
#            self.add_variables_cplex()
#            self.add_constraints_cplex()
#            self.add_objective_cplex()
            self.compute_constraints()
            self.add_variables_cplex2()
            self.add_constraints_cplex2()
            self.add_objective_cplex2()

    def compute_constraints(self):
        m = len(self.alternatives)
        n = len(self.criteria)

        cat_ranks = { c.id: c.rank for c in self.categories }
        assignments = { a.alternative_id: cat_ranks[a.category_id] \
                       for a in self.alternative_affectations }

        self.c_xi = dict()
        self.c_yi = dict()
        for a in self.alternatives:
            a_perfs = self.pt(a.id)
            cat_rank = assignments[a.id]

            if cat_rank > 1:
                lower_profile = self.profiles[cat_rank-2]
                b_perfs = self.bpt(lower_profile.id)

                dj = str()
                for c in self.criteria:
                    if a_perfs(c.id) >= b_perfs(c.id):
                        dj += '1'
                    else:
                        dj += '0'

                if self.c_xi.has_key(dj) is False:
                    self.c_xi[dj] = 1
                else:
                    self.c_xi[dj] += 1

            if cat_rank < len(self.categories):
                upper_profile = self.profiles[cat_rank-1]
                b_perfs = self.bpt(upper_profile.id)

                dj = str()
                for c in self.criteria:
                    if a_perfs(c.id) >= b_perfs(c.id):
                        dj += '1'
                    else:
                        dj += '0'

                if self.c_yi.has_key(dj) is False:
                    self.c_yi[dj] = 1
                else:
                    self.c_yi[dj] += 1

    def add_variables_cplex2(self):
        self.lp.variables.add(names=['w'+c.id for c in self.criteria],
                              lb=[0 for c in self.criteria],
                              ub=[1 for c in self.criteria])
        self.lp.variables.add(names=['x'+dj for dj in self.c_xi],
                              lb = [0 for dj in self.c_xi],
                              ub = [1 for dj in self.c_xi])
        self.lp.variables.add(names=['y'+dj for dj in self.c_yi],
                              lb = [0 for dj in self.c_yi],
                              ub = [1 for dj in self.c_yi])
        self.lp.variables.add(names=['xp'+dj for dj in self.c_xi],
                              lb = [0 for dj in self.c_xi],
                              ub = [1 for dj in self.c_xi])
        self.lp.variables.add(names=['yp'+dj for dj in self.c_yi],
                              lb = [0 for dj in self.c_yi],
                              ub = [1 for dj in self.c_yi])
        self.lp.variables.add(names=['lambda'], lb = [0.5], ub = [1])

    def add_constraints_cplex2(self):
        constraints = self.lp.linear_constraints
        w_vars = ['w'+c.id for c in self.criteria]
        for dj in self.c_xi:
            coef = map(float, list(dj))
            constraints.add(names=['cinf'+dj],
                            lin_expr =
                                [
                                 [w_vars + ['x'+dj, 'xp'+dj, 'lambda'],
                                  coef + [-1.0, 1.0, -1.0]],
                                ],
                            senses = ["E"],
                            rhs = [0],
                           )

        for dj in self.c_yi:
            coef = map(float, list(dj))
            constraints.add(names=['csup'+dj],
                            lin_expr =
                                [
                                 [w_vars + ['y'+dj, 'yp'+dj, 'lambda'],
                                  coef + [1.0, -1.0, -1.0]],
                                ],
                            senses = ["E"],
                            rhs = [-self.delta],
                           )

        constraints.add(names=['wsum'],
                        lin_expr = [[w_vars,
                                    [1.0 for i in range(len(w_vars))]],
                                   ],
                        senses = ["E"],
                        rhs = [1]
                        )

    def add_objective_cplex2(self):
        self.lp.objective.set_sense(self.lp.objective.sense.minimize)
        for dj, coef in self.c_xi.iteritems():
            self.lp.objective.set_linear('xp'+dj, coef)
        for dj, coef in self.c_yi.iteritems():
            self.lp.objective.set_linear('yp'+dj, coef)

    def add_variables_cplex(self):
        self.lp.variables.add(names=['w'+c.id for c in self.criteria],
                              lb=[0 for c in self.criteria],
                              ub=[1 for c in self.criteria])
        self.lp.variables.add(names=['x'+a.id for a in self.alternatives],
                              lb=[0 for a in self.alternatives],
                              ub=[1 for a in self.alternatives])
        self.lp.variables.add(names=['y'+a.id for a in self.alternatives],
                              lb=[0 for a in self.alternatives],
                              ub=[1 for a in self.alternatives])
        self.lp.variables.add(names=['xp'+a.id for a in self.alternatives],
                              lb=[0 for a in self.alternatives],
                              ub=[1 for a in self.alternatives])
        self.lp.variables.add(names=['yp'+a.id for a in self.alternatives],
                              lb=[0 for a in self.alternatives],
                              ub=[1 for a in self.alternatives])
        self.lp.variables.add(names=['lambda'], lb = [0.5], ub = [1])

    def add_constraints_cplex(self):
        m = len(self.alternatives)
        n = len(self.criteria)
        constraints = self.lp.linear_constraints

        m = 0
        for a in self.alternatives:
            a_perfs = self.pt(a.id)
            cat_id = self.alternative_affectations(a.id)
            cat_rank = self.categories(cat_id).rank

            # sum(w_j(a_i,b_h-1) - x_i + x'_i = lbda
            if cat_rank > 1:
                lower_profile = self.profiles[cat_rank-2]
                b_perfs = self.bpt(lower_profile.id)

                constraints.add(names=['cinf'+a.id])
                for c in self.criteria:
                    if a_perfs(c.id) >= b_perfs(c.id):
                        k = 1
                    else:
                        k = 0
                    constraints.set_coefficients('cinf'+a.id, 'w'+c.id, k)

                constraints.set_coefficients('cinf'+a.id, 'x'+a.id, -1)
                constraints.set_coefficients('cinf'+a.id, 'xp'+a.id, 1)
                constraints.set_coefficients('cinf'+a.id, 'lambda', -1)
                constraints.set_rhs('cinf'+a.id, 0)
                constraints.set_senses('cinf'+a.id, 'E')
            else:
                constraints.add(names=['nil'+a.id])
                constraints.set_coefficients('nil'+a.id, 'x'+a.id, 1)
                constraints.set_coefficients('nil'+a.id, 'xp'+a.id, 1)
                constraints.set_rhs('nil'+a.id, 0)
                constraints.set_senses('nil'+a.id, 'E')

            # sum(w_j(a_i,b_h) + y_i - y'_i = lbda - delta
            if cat_rank < len(self.categories):
                upper_profile = self.profiles[cat_rank-1]
                b_perfs = self.bpt(upper_profile.id)

                constraints.add(names=['csup'+a.id])
                for c in self.criteria:
                    if a_perfs(c.id) >= b_perfs(c.id):
                        k = 1
                    else:
                        k = 0
                    constraints.set_coefficients('csup'+a.id, 'w'+c.id, k)

                constraints.set_coefficients('csup'+a.id, 'y'+a.id, 1)
                constraints.set_coefficients('csup'+a.id, 'yp'+a.id, -1)
                constraints.set_coefficients('csup'+a.id, 'lambda', -1)
                constraints.set_rhs('csup'+a.id, -self.delta)
                constraints.set_senses('csup'+a.id, 'E')
            else:
                constraints.add(names=['nil'+a.id])
                constraints.set_coefficients('nil'+a.id, 'y'+a.id, 1)
                constraints.set_coefficients('nil'+a.id, 'yp'+a.id, 1)
                constraints.set_rhs('nil'+a.id, 0)
                constraints.set_senses('nil'+a.id, 'E')

        # sum w_j = 1
        constraints.add(names=['wsum'])
        for c in self.criteria:
            constraints.set_coefficients('wsum', 'w'+c.id, 1)
        constraints.set_rhs('wsum', 1)
        constraints.set_senses('wsum', 'E')

    def add_objective_cplex(self):
        self.lp.objective.set_sense(self.lp.objective.sense.minimize)
        for a in self.alternatives:
            self.lp.objective.set_linear('xp'+a.id, 1)
            self.lp.objective.set_linear('yp'+a.id, 1)

    def solve_cplex(self):
        self.lp.solve()

        obj = self.lp.solution.get_objective_value()

        cvs = criteria_values()
        for c in self.criteria:
            cv = criterion_value()
            cv.criterion_id = c.id
            cv.value = self.lp.solution.get_values('w'+c.id)
            cvs.append(cv)

        lbda = self.lp.solution.get_values("lambda")

        return obj, cvs, lbda

    def add_variables_scip(self):
        self.w = dict((j.id, {}) for j in self.criteria)
        for j in self.criteria:
            self.w[j.id] = self.lp.variable(lower=0, upper=1)

        self.x = dict((i.id, {}) for i in self.alternatives)
        self.y = dict((i.id, {}) for i in self.alternatives)
        self.xp = dict((i.id, {}) for i in self.alternatives)
        self.yp = dict((i.id, {}) for i in self.alternatives)
        for i in self.alternatives:
            self.x[i.id] = self.lp.variable(lower=0, upper=1)
            self.y[i.id] = self.lp.variable(lower=0, upper=1)
            self.xp[i.id] = self.lp.variable(lower=0, upper=1)
            self.yp[i.id] = self.lp.variable(lower=0, upper=1)

        self.lbda = self.lp.variable(lower=0.5, upper=1)

    def add_constraints_scip(self):
        for a in self.alternatives:
            a_perfs = self.pt(a.id)
            cat_id = self.alternative_affectations(a.id)
            cat_rank = self.categories(cat_id).rank

            # sum(w_j(a_i,b_h-1) - x_i + x'_i = lbda
            if cat_rank > 1:
                lower_profile = self.profiles[cat_rank-2]
                b_perfs = self.bpt(lower_profile.id)

                c_outrank = []
                for c in self.criteria:
                    if a_perfs(c.id) >= b_perfs(c.id):
                        c_outrank.append(c)

                self.lp += sum(self.w[c.id] for c in c_outrank) \
                               - self.x[a.id] + self.xp[a.id] == self.lbda
            else:
                self.lp += self.x[a.id] == 0
                self.lp += self.xp[a.id] == 0

            # sum(w_j(a_i,b_h) + y_i - y'_i = lbda - delta
            if cat_rank < len(self.categories):
                upper_profile = self.profiles[cat_rank-1]
                b_perfs = self.bpt(upper_profile.id)

                c_outrank = []
                for c in self.criteria:
                    if a_perfs(c.id) >= b_perfs(c.id):
                        c_outrank.append(c)

                self.lp += sum(self.w[c.id] for c in c_outrank) \
                               + self.y[a.id] - self.yp[a.id] == self.lbda \
                               - self.delta
            else:
                self.lp += self.y[a.id] == 0
                self.lp += self.yp[a.id] == 0

        # sum w_j = 1
        self.lp += sum(self.w[c.id] for c in self.criteria) == 1

    def add_objective_scip(self):
        m = len(self.alternatives)
        n = len(self.criteria)

        self.obj = sum([self.xp[i.id] for i in self.alternatives]) \
                   + sum([self.yp[i.id] for i in self.alternatives])

    def solve_scip(self):
        solution = self.lp.minimize(objective=self.obj)
        if solution is None:
            raise RuntimeError("No solution found")

        obj = solution.objective

        cvs = criteria_values()
        for c in self.criteria:
            cv = criterion_value()
            cv.criterion_id = c.id
            cv.value = solution[self.w[c.id]]
            cvs.append(cv)

        lbda = solution[self.lbda]

        return obj, cvs, lbda

    def add_variables_glpk(self):
        m = len(self.alternatives)
        n = len(self.criteria)

        # Initialize variables
        self.w = self.lp.var(xrange(n), 'w', bounds=(0, 1))
        self.x = self.lp.var(xrange(m), 'x', bounds=(0, 1))
        self.y = self.lp.var(xrange(m), 'y', bounds=(0, 1))
        self.xp = self.lp.var(xrange(m), 'xp', bounds=(0, 1))
        self.yp = self.lp.var(xrange(m), 'yp', bounds=(0, 1))
        self.lbda = self.lp.var(name='lambda', bounds=(0.5, 1))

    def add_constraints_glpk(self):
        n = len(self.criteria)

        for i, a in enumerate(self.alternatives):
            a_perfs = self.pt(a.id)
            cat_id = self.alternative_affectations(a.id)
            cat_rank = self.categories(cat_id).rank

            # sum(w_j(a_i,b_h-1) - x_i + x'_i = lbda
            if cat_rank > 1:
                lower_profile = self.profiles[cat_rank-2]
                b_perfs = self.bpt(lower_profile.id)

                j_outrank = []
                for j, c in enumerate(self.criteria):
                    c_id = c.id
                    if a_perfs(c_id) >= b_perfs(c_id):
                        j_outrank.append(j)

                self.lp.st(sum(self.w[j] for j in j_outrank) - self.x[i] \
                           + self.xp[i] == self.lbda)
            else:
                self.lp.st(self.x[i] == 0)
                self.lp.st(self.xp[i] == 0)

            # sum(w_j(a_i,b_h) + y_i - y'_i = lbda - delta
            if cat_rank < len(self.categories):
                upper_profile = self.profiles[cat_rank-1]
                b_perfs = self.bpt(upper_profile.id)

                j_outrank = []
                for j, c in enumerate(self.criteria):
                    c_id = c.id
                    if a_perfs(c_id) >= b_perfs(c_id):
                        j_outrank.append(j)

                self.lp.st(sum(self.w[j] for j in j_outrank) + self.y[i] \
                           - self.yp[i] == self.lbda - self.delta)
            else:
                self.lp.st(self.y[i] == 0)
                self.lp.st(self.yp[i] == 0)

        # sum w_j = 1
        self.lp.st(sum(self.w[j] for j in range(n)) == 1)

    def add_objective_glpk(self):
        m = len(self.alternatives)

        self.lp.min(sum([self.xp[i] for i in range(m)])   \
                    + sum([self.yp[i] for i in range(m)]))

    def solve_glpk(self):
        self.lp.solve()

        status = self.lp.status()
        if status != 'opt':
            raise RuntimeError("Solver status: %s" % self.lp.status())

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

    def solve(self):
        if solver == 'glpk':
            sol = self.solve_glpk()
        elif solver == 'scip':
            sol = self.solve_scip()
        elif solver == 'cplex':
            sol = self.solve_cplex()
        else:
            raise NameError('Invalid solver selected')

        return sol

if __name__ == "__main__":
    import time
    import random
    from tools.generate_random import generate_random_alternatives
    from tools.generate_random import generate_random_criteria
    from tools.generate_random import generate_random_criteria_values
    from tools.generate_random import generate_random_performance_table
    from tools.generate_random import generate_random_categories
    from tools.generate_random import generate_random_categories_profiles
    from tools.utils import normalize_criteria_weights
    from tools.utils import add_errors_in_affectations
    from tools.utils import display_affectations_and_pt
    from mcda.electre_tri import electre_tri

    print("Solver used: %s" % solver)
    # Original Electre Tri model
    a = generate_random_alternatives(5000)
    c = generate_random_criteria(5)
    cv = generate_random_criteria_values(c, 890)
    normalize_criteria_weights(cv)
    pt = generate_random_performance_table(a, c)

    b = generate_random_alternatives(1, 'b')
    bpt = generate_random_categories_profiles(b, c)
    cat = generate_random_categories(2)

    lbda = random.uniform(0.5, 1)
#    lbda = 0.75
    errors = 0.0
    delta = 0.0001

    model = electre_tri(c, cv, bpt, lbda, cat)
    aa = model.pessimist(pt)
    add_errors_in_affectations(aa, cat.get_ids(), errors)

    print('Original model')
    print('==============')
    print("Number of alternatives: %d" % len(a))
    print("Errors in alternatives affectations: %g%%" % (errors*100))
    cids = c.get_ids()
    bpt.display(criterion_ids=cids)
    cv.display(criterion_ids=cids)
    print("lambda\t%.7s" % lbda)
    print("delta: %g" % delta)
    #print(aa)

    lp_weights = lp_electre_tri_weights(a, c, cv, aa, pt, cat, b, bpt,
                                        delta)

    t1 = time.time()
    obj, cv_learned, lbda_learned = lp_weights.solve()
    t2 = time.time()

    model.cv = cv_learned
    model.lbda = lbda_learned
    aa_learned = model.pessimist(pt)

    print('Learned model')
    print('=============')
    print("Computation time: %g secs" % (t2-t1))
    print("Objective: %s" % obj)
    cv.display(criterion_ids=cids, name='w')
    cv_learned.display(header=False, criterion_ids=cids, name='w_learned')
    print("lambda\t%.7s" % lbda)
    print("lambda_learned\t%.7s" % lbda_learned)
    #print(aa_learned)

    total = len(a)
    nok = 0
    anok = []
    for alt in a:
        if aa(alt.id) != aa_learned(alt.id):
            anok.append(alt)
#            print("Pessimistic affectation of %s mismatch (%s <> %s)" %
#                  (str(alt.id), aa(alt.id), aa_learned(alt.id)))
            nok += 1

    print("Good affectations: %3g %%" % (float(total-nok)/total*100))
    print("Bad affectations : %3g %%" % (float(nok)/total*100))

    if len(anok) > 0:
        print("Alternatives wrongly assigned:")
        display_affectations_and_pt(anok, c, [aa, aa_learned], [pt])
