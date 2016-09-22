from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../../")
from pymcda.types import CriterionValue, CriteriaValues

verbose = False

class LpMRSortVetoWeights():

    def __init__(self, model, pt, aa_ori, aa, delta=0.0001):
        self.model = model
        self.categories = model.categories_profiles.get_ordered_categories()
        self.profiles = model.categories_profiles.get_ordered_profiles()
        self.delta = delta
        self.cat_ranks = { c: i+1 for i, c in enumerate(self.categories) }
        self.pt = { a.id: a.performances for a in pt }
        self.aa_ori = aa_ori
        self.aa = aa
        self.update_linear_program()

    def update_linear_program(self):
        self.compute_constraints(self.aa_ori, self.aa, self.model.vpt)

        solver = os.getenv('SOLVER', 'cplex')
        if solver == 'cplex':
            import cplex
            solver_max_threads = int(os.getenv('SOLVER_MAX_THREADS', 0))
            self.lp = cplex.Cplex()
            self.lp.parameters.threads.set(solver_max_threads)
            if verbose is False:
                self.lp.set_log_stream(None)
                self.lp.set_results_stream(None)
#                self.lp.set_warning_stream(None)
#                self.lp.set_error_stream(None)
            self.add_variables_cplex()
            self.add_constraints_cplex()
            self.add_objective_cplex()
            self.solve_function = self.solve_cplex
        else:
            raise NameError('Invalid solver selected')


    def compute_constraints(self, aa_ori, aa, bpt):
        aa_ori = { a.id: self.cat_ranks[a.category_id] for a in aa_ori }
        aa = { a.id: self.cat_ranks[a.category_id] for a in aa }
        bpt = { a.id: a.performances for a in bpt }

        self.c_xi = dict()
        self.c_yi = dict()
        self.a_c_xi = dict()
        self.a_c_yi = dict()
        for a_id in aa_ori.keys():
            ap = self.pt[a_id]
            cat_rank = aa_ori[a_id]
            cat_rank2 = aa[a_id]

            if cat_rank > 1:
                lower_profile = self.profiles[cat_rank-2]
                bp = bpt[lower_profile]

                dj = str()
                for c in self.model.criteria:
                    if ap[c.id] * c.direction <= bp[c.id] * c.direction:
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

            if cat_rank < len(self.categories) and cat_rank < cat_rank2:
                upper_profile = self.profiles[cat_rank-1]
                bp = bpt[upper_profile]

                dj = str()
                for c in self.model.criteria:
                    if ap[c.id] * c.direction <= bp[c.id] * c.direction:
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
        self.lp.variables.add(names=['lambda'], lb = [0], ub = [1])

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
                                  coef + [1.0, -1.0, -1.0]],
                                ],
                            senses = ["E"],
                            rhs = [-self.delta],
                           )

        for dj in self.c_yi:
            coef = map(float, list(dj))

            # sum(w_j(a_i,b_h) + y_i - y'_i = lbda - delta
            constraints.add(names=['csup'+dj],
                            lin_expr =
                                [
                                 [w_vars + ['y'+dj, 'yp'+dj, 'lambda'],
                                  coef + [-1.0, 1.0, -1.0]],
                                ],
                            senses = ["E"],
                            rhs = [0],
                           )

        # sum w_j = 1
        constraints.add(names=['wsum'],
                        lin_expr = [[w_vars,
                                    [1.0] * len(w_vars)],
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

        status = self.lp.solution.get_status()
        if status != self.lp.solution.status.optimal:
            raise RuntimeError("Solver status: %s" % status)

        obj = self.lp.solution.get_objective_value()

        cvs = CriteriaValues()
        for c in self.model.criteria:
            cv = CriterionValue()
            cv.id = c.id
            cv.value = self.lp.solution.get_values('w'+c.id)
            cvs.append(cv)

        self.model.veto_weights = cvs
        self.model.veto_lbda = self.lp.solution.get_values("lambda")

        return obj

    def solve(self):
        return self.solve_function()

if __name__ == "__main__":
    import time
    import random
    from pymcda.generate import generate_alternatives
    from pymcda.generate import generate_random_performance_table
    from pymcda.generate import generate_random_mrsort_model
    from pymcda.generate import generate_random_mrsort_model_with_coalition_veto
    from pymcda.generate import generate_criteria
    from pymcda.generate import generate_categories
    from pymcda.generate import generate_categories_profiles
    from pymcda.utils import add_errors_in_assignments
    from pymcda.utils import print_pt_and_assignments
    from pymcda.utils import compute_winning_and_loosing_coalitions
    from pymcda.types import AlternativesAssignments, PerformanceTable
    from pymcda.types import AlternativePerformances
    from pymcda.types import CriteriaValues, CriterionValue
    from pymcda.electre_tri import MRSort

    # MR-Sort model
    model = generate_random_mrsort_model_with_coalition_veto(5, 3, 4)

    # Generate random alternatives
    a = generate_alternatives(15000)
    pt = generate_random_performance_table(a, model.criteria)

    errors = 0.0
    delta = 0.0001
    nlearn = 1.00

    # Assign the alternative with the model
    aa = model.pessimist(pt)

    a_learn = random.sample(a, int(nlearn*len(a)))
    aa_learn = AlternativesAssignments([ aa[alt.id] for alt in a_learn ])
    pt_learn = PerformanceTable([ pt[alt.id] for alt in a_learn ])

    aa_err = aa_learn.copy()
    aa_erroned = add_errors_in_assignments(aa_err, model.categories, errors)

    print('Original model')
    print('==============')
    print("Number of alternatives: %d" % len(a))
    print("Number of learning alternatives: %d" % len(aa_learn))
    print("Errors in alternatives assignments: %g%%" % (errors*100))
    cids = model.criteria.keys()
    model.bpt.display(criterion_ids = cids)
    model.cv.display(criterion_ids = cids)
    print("lambda\t%.7s" % model.lbda)
    print("delta: %g" % delta)
    #print(aa)

    vpt = model.vpt
    model2 = model.copy()
    model2.vpt = None
    model2.veto_weights = None
    model2.veto_lbda = None

    aa2 = model2.pessimist(pt)

    model2.vpt = vpt

    t1 = time.time()
    lp_weights = LpMRSortVetoWeights(model2, pt_learn, aa_err, aa2, delta)
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
    model2.cv.display(criterion_ids=cids)
    print("lambda\t%.7s" % model2.lbda)
    model2.veto_weights.display(criterion_ids=cids)
    print("veto_lambda\t%.7s" % model2.veto_lbda)
    print(model2.veto)
    #print(aa_learned)

    total = len(a)
    nok = nok_erroned = 0
    anok = []
    a_assign = {alt.id: alt.category_id for alt in aa}
    a_assign2 = {alt.id: alt.category_id for alt in aa_learned}
    for alt in a:
        if a_assign[alt.id] != a_assign2[alt.id]:
            anok.append(alt.id)
            nok += 1
            if alt.id in aa_erroned:
                nok_erroned += 1

    print("Good assignments          : %3g %%" \
          % (float(total-nok)/total*100))
    print("Bad assignments           : %3g %%" \
          % (float(nok)/total*100))
    if aa_erroned:
        print("Bad in erroned assignments: %3g %%" \
              % (float(nok_erroned)/total*100))

    if len(anok) > 0:
        print("Alternatives wrongly assigned:")
        print_pt_and_assignments(anok, model.criteria.keys(),
                                 [aa, aa_learned], pt)

    win1, loose1 = compute_winning_and_loosing_coalitions(model.cv,
                                                          model.lbda)
    win2, loose2 = compute_winning_and_loosing_coalitions(model2.cv,
                                                          model2.lbda)
    coali = list(set(win1) & set(win2))
    coal1e = list(set(win1) ^ set(coali))
    coal2e = list(set(win2) ^ set(coali))

    print("Number of coalitions original: %d"
          % len(win1))
    print("Number of coalitions learned: %d"
          % len(win2))
    print("Number of common coalitions: %d"
          % len(coali))
    print("Coalitions in original and not in learned: %s"
          % '; '.join(map(str, coal1e)))
    print("Coalitions in learned and not in original: %s"
          % '; '.join(map(str, coal2e)))
