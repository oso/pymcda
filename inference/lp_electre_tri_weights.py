from __future__ import division
import os
import sys
sys.path.insert(0, "..")
from mcda.types import criterion_value, criteria_values

verbose = False

try:
    solver = os.environ['SOLVER']
except:
    solver = 'cplex'

if solver == 'glpk':
    import pymprog
elif solver == 'scip':
    from zibopt import scip
elif solver == 'cplex':
    import cplex
else:
    raise NameError('Invalid solver selected')

class lp_electre_tri_weights():

    def __init__(self, model, pt, aa_ori, cps, delta=0.0001):
        self.model = model
        self.categories = cps.get_ordered_categories()
        self.profiles = cps.get_ordered_profiles()
        self.delta = delta
        self.cat_ranks = { c: i+1 for i, c in enumerate(self.categories) }
        self.pt = { a.alternative_id: a.performances \
                    for a in pt }
        self.aa_ori = aa_ori
        self.update_linear_program()

    def update_linear_program(self):
        self.compute_constraints(self.aa_ori, self.model.bpt)

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
            self.add_variables_cplex()
            self.add_constraints_cplex()
            self.add_objective_cplex()

    def compute_constraints(self, aa, bpt):
        m = len(self.pt)
        n = len(self.model.criteria)

        aa = { a.alternative_id: self.cat_ranks[a.category_id] \
               for a in aa }
        bpt = { a.alternative_id: a.performances \
                for a in bpt }

        self.c_xi = dict()
        self.c_yi = dict()
        self.a_c_xi = dict()
        self.a_c_yi = dict()
        for a_id in self.pt.keys():
            a_perfs = self.pt[a_id]
            cat_rank = aa[a_id]

            if cat_rank > 1:
                lower_profile = self.profiles[cat_rank-2]
                b_perfs = bpt[lower_profile]

                dj = str()
                for c in self.model.criteria:
                    if a_perfs[c.id] >= b_perfs[c.id]:
                        dj += '1'
                    else:
                        dj += '0'

                # Del old constraint
                if a_id in self.a_c_xi:
                    old = self.a_c_xi[a_id]
                    if self.c_xi[old] == 1:
                        del self.c_xi[old]
                    else:
                        self.c_xi[old] -= 1

                # Save constraint
                self.a_c_xi[a_id] = dj

                # Add new constraint
                if not dj in self.c_xi:
                    self.c_xi[dj] = 1
                else:
                    self.c_xi[dj] += 1

            if cat_rank < len(self.categories):
                upper_profile = self.profiles[cat_rank-1]
                b_perfs = bpt[upper_profile]

                dj = str()
                for c in self.model.criteria:
                    if a_perfs[c.id] >= b_perfs[c.id]:
                        dj += '1'
                    else:
                        dj += '0'

                # Del old constraint
                if a_id in self.a_c_yi:
                    old = self.a_c_yi[a_id]
                    if self.c_yi[old] == 1:
                        del self.c_yi[old]
                    else:
                        self.c_yi[old] -= 1

                # Save constraint
                self.a_c_yi[a_id] = dj

                # Add new constraint
                if not dj in self.c_yi:
                    self.c_yi[dj] = 1
                else:
                    self.c_yi[dj] += 1

    def add_variables_cplex(self):
        self.lp.variables.add(names=['w'+c.id for c in self.model.criteria],
                              lb=[0 for c in self.model.criteria],
                              ub=[1 for c in self.model.criteria])
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

    def add_constraints_cplex(self):
        constraints = self.lp.linear_constraints
        w_vars = ['w'+c.id for c in self.model.criteria]
        for dj in self.c_xi:
            coef = map(float, list(dj))

            # sum(w_j(a_i,b_h-1) - x_i + x'_i = lbda
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

            # sum(w_j(a_i,b_h) + y_i - y'_i = lbda - delta
            constraints.add(names=['csup'+dj],
                            lin_expr =
                                [
                                 [w_vars + ['y'+dj, 'yp'+dj, 'lambda'],
                                  coef + [1.0, -1.0, -1.0]],
                                ],
                            senses = ["E"],
                            rhs = [-self.delta],
                           )

        # sum w_j = 1
        constraints.add(names=['wsum'],
                        lin_expr = [[w_vars,
                                    [1.0 for i in range(len(w_vars))]],
                                   ],
                        senses = ["E"],
                        rhs = [1]
                        )

    def add_objective_cplex(self):
        self.lp.objective.set_sense(self.lp.objective.sense.minimize)
        for dj, coef in self.c_xi.iteritems():
            self.lp.objective.set_linear('xp'+dj, coef)
        for dj, coef in self.c_yi.iteritems():
            self.lp.objective.set_linear('yp'+dj, coef)

    def solve_cplex(self):
        self.lp.solve()

        obj = self.lp.solution.get_objective_value()

        cvs = criteria_values()
        for c in self.model.criteria:
            cv = criterion_value()
            cv.id = c.id
            cv.value = self.lp.solution.get_values('w'+c.id)
            cvs.append(cv)

        self.model.cv = cvs
        self.model.lbda = self.lp.solution.get_values("lambda")

        return obj

    def add_variables_scip(self):
        m1 = len(self.c_xi)
        m2 = len(self.c_yi)

        self.w = dict((c.id, {}) for c in self.model.criteria)
        for c in self.model.criteria:
            self.w[c.id] = self.lp.variable(lower=0, upper=1)

        if m1 > 0:
            self.x = dict((dj, {}) for dj in self.c_xi)
            self.xp = dict((dj, {}) for dj in self.c_xi)
            for dj in self.c_xi:
                self.x[dj] = self.lp.variable(lower=0, upper=1)
                self.xp[dj] = self.lp.variable(lower=0, upper=1)

        if m1 > 0:
            self.y = dict((dj, {}) for dj in self.c_yi)
            self.yp = dict((dj, {}) for dj in self.c_yi)
            for dj in self.c_yi:
                self.y[dj] = self.lp.variable(lower=0, upper=1)
                self.yp[dj] = self.lp.variable(lower=0, upper=1)

        self.lbda = self.lp.variable(lower=0.5, upper=1)

    def add_constraints_scip(self):
        n = len(self.model.criteria)

        for i, dj in enumerate(self.c_xi):
            coef = list(map(float, list(dj)))

            # sum(w_j(a_i,b_h-1) - x_i + x'_i = lbda
            self.lp += sum(coef[j]*self.w[c.id] \
                           for j, c in enumerate(self.model.criteria)) \
                           - self.x[dj] + self.xp[dj] == self.lbda

        for i, dj in enumerate(self.c_yi):
            coef = list(map(float, list(dj)))

            # sum(w_j(a_i,b_h) + y_i - y'_i = lbda - delta
            self.lp += sum(coef[j]*self.w[c.id] \
                           for j, c in enumerate(self.model.criteria)) \
                           + self.y[dj] - self.yp[dj] == self.lbda \
                                                         - self.delta

        # sum w_j = 1
        self.lp += sum(self.w[c.id] for c in self.model.criteria) == 1

    def add_objective_scip(self):
        self.obj = sum([self.xp[dj]*coef \
                       for dj, coef in self.c_xi.items()]) \
                   + sum([self.yp[dj]*coef \
                         for dj, coef in self.c_yi.items()])

    def solve_scip(self):
        solution = self.lp.minimize(objective=self.obj)
        if solution is None:
            raise RuntimeError("No solution found")

        obj = solution.objective

        cvs = criteria_values()
        for c in self.model.criteria:
            cv = criterion_value()
            cv.id = c.id
            cv.value = solution[self.w[c.id]]
            cvs.append(cv)

        self.model.cv = cvs
        self.model.lbda = solution[self.lbda]

        return obj

    def add_variables_glpk(self):
        m1 = len(self.c_xi)
        m2 = len(self.c_yi)
        n = len(self.model.criteria)

        self.w = self.lp.var(xrange(n), 'w', bounds=(0, 1))
        self.lbda = self.lp.var(name='lambda', bounds=(0.5, 1))
        if m1 > 0:
            self.x = self.lp.var(xrange(m1), 'x', bounds=(0, 1))
            self.xp = self.lp.var(xrange(m1), 'xp', bounds=(0, 1))
        if m2 > 0:
            self.y = self.lp.var(xrange(m2), 'y', bounds=(0, 1))
            self.yp = self.lp.var(xrange(m2), 'yp', bounds=(0, 1))

    def add_constraints_glpk(self):
        n = len(self.model.criteria)

        for i, dj in enumerate(self.c_xi):
            coef = map(float, list(dj))

            # sum(w_j(a_i,b_h-1) - x_i + x'_i = lbda
            self.lp.st(sum(coef[j]*self.w[j] for j in range(n)) \
                       - self.x[i] + self.xp[i] == self.lbda)

        for i, dj in enumerate(self.c_yi):
            coef = map(float, list(dj))

            # sum(w_j(a_i,b_h) + y_i - y'_i = lbda - delta
            self.lp.st(sum(coef[j]*self.w[j] for j in range(n)) \
                       + self.y[i] - self.yp[i] == self.lbda - self.delta)

        # sum w_j = 1
        self.lp.st(sum(self.w[j] for j in range(n)) == 1)

    def add_objective_glpk(self):
        m = len(self.pt)
        self.lp.min(sum([k*self.xp[i]
                         for i, k in enumerate(self.c_xi.values())])
                    + sum([k*self.yp[i]
                          for i, k in enumerate(self.c_yi.values())]))

    def solve_glpk(self):
        self.lp.solve()

        status = self.lp.status()
        if status != 'opt':
            raise RuntimeError("Solver status: %s" % self.lp.status())

        #print(self.lp.reportKKT())
        obj = self.lp.vobj()

        cvs = criteria_values()
        for j, c in enumerate(self.model.criteria):
            cv = criterion_value()
            cv.id = c.id
            cv.value = float(self.w[j].primal)
            cvs.append(cv)

        self.model.cv = cvs
        self.model.lbda = float(self.lbda.primal)

        return obj

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
    from tools.generate_random import generate_random_profiles
    from tools.generate_random import generate_random_categories_profiles
    from tools.utils import normalize_criteria_weights
    from tools.utils import add_errors_in_affectations
    from tools.utils import display_affectations_and_pt
    from tools.utils import get_possible_coallitions
    from mcda.electre_tri import electre_tri
    from mcda.types import alternatives_affectations, performance_table

    print("Solver used: %s" % solver)
    # Original Electre Tri model
    a = generate_random_alternatives(15000)
    c = generate_random_criteria(10)
    cv = generate_random_criteria_values(c, 890)
    normalize_criteria_weights(cv)
    pt = generate_random_performance_table(a, c)

    cat = generate_random_categories(5)
    cps = generate_random_categories_profiles(cat)
    b = cps.get_ordered_profiles()
    bpt = generate_random_profiles(b, c)

    lbda = random.uniform(0.5, 1)
#    lbda = 0.75
    errors = 0.2
    delta = 0.0001
    nlearn = 1.00

    model = electre_tri(c, cv, bpt, lbda, cps)
    aa = model.pessimist(pt)

    a_learn = random.sample(a, int(nlearn*len(a)))
    aa_learn = alternatives_affectations([ aa[alt.id] for alt in a_learn ])
    pt_learn = performance_table([ pt[alt.id] for alt in a_learn ])

    aa_err = aa_learn.copy()
    aa_erroned = add_errors_in_affectations(aa_err, cat.keys(), errors)

    print('Original model')
    print('==============')
    print("Number of alternatives: %d" % len(a))
    print("Number of learning alternatives: %d" % len(aa_learn))
    print("Errors in alternatives affectations: %g%%" % (errors*100))
    cids = c.keys()
    bpt.display(criterion_ids = cids, alternative_ids = b)
    cv.display(criterion_ids = cids)
    print("lambda\t%.7s" % lbda)
    print("delta: %g" % delta)
    #print(aa)

    model2 = model.copy()
    t1 = time.time()
    lp_weights = lp_electre_tri_weights(model2, pt_learn, aa_err, cps,
                                        delta)
    t2 = time.time()
    obj = lp_weights.solve()
    t3 = time.time()

    aa_learned = model2.pessimist(pt)

    print('Learned model')
    print('=============')
    print("Total computation time: %g secs" % (t3-t1))
    print("Constraints encoding time: %g secs" % (t2-t1))
    print("Solving time: %g secs" % (t3-t2))
    print("Objective: %s" % obj)
    cv.display(criterion_ids=cids, name='w')
    model2.cv.display(header=False, criterion_ids=cids, name='w_learned')
    print("lambda\t%.7s" % lbda)
    print("lambda_learned\t%.7s" % model2.lbda)
    #print(aa_learned)

    total = len(a)
    nok = nok_erroned = 0
    anok = []
    a_assign = {alt.alternative_id: alt.category_id for alt in aa}
    a_assign2 = {alt.alternative_id: alt.category_id for alt in aa_learned}
    for alt in a:
        if a_assign[alt.id] != a_assign2[alt.id]:
            anok.append(alt)
            nok += 1
            if alt.id in aa_erroned:
                nok_erroned += 1

    print("Good affectations          : %3g %%" \
          % (float(total-nok)/total*100))
    print("Bad affectations           : %3g %%" \
          % (float(nok)/total*100))
    if aa_erroned:
        print("Bad in erroned affectations: %3g %%" \
              % (float(nok_erroned)/total*100))

    if len(anok) > 0:
        print("Alternatives wrongly assigned:")
        display_affectations_and_pt(anok, c, [aa, aa_learned], [pt])

    coal1 = get_possible_coallitions(model.cv, model.lbda)
    coal2 = get_possible_coallitions(model2.cv, model2.lbda)
    coali = list(set(coal1) & set(coal2))
    coal1e = list(set(coal1) ^ set(coali))
    coal2e = list(set(coal2) ^ set(coali))

    print("Number of coallitions original: %d"
          % len(coal1))
    print("Number of coallitions learned: %d"
          % len(coal2))
    print("Number of common coallitions: %d"
          % len(coali))
    print("Coallitions in original and not in learned: %s"
          % '; '.join(map(str, coal1e)))
    print("Coallitions in learned and not in original: %s"
          % '; '.join(map(str, coal2e)))
