from __future__ import division
import os, sys
from itertools import product
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../../")
from pymcda.types import CriterionValue, CriteriaValues
from pymcda.types import AlternativePerformances, PerformanceTable
from pymcda.types import PairwiseRelations, PairwiseRelation

verbose = False

class MipJNCSR():

    def __init__(self, model, pt, aa, pwcs, epsilon = 0.0001):
        self.pt = pt
        self.aa = aa
        self.pwcs = pwcs
        self.model = model
        self.criteria = model.criteria.get_active()
        self.cps = model.categories_profiles

        self.epsilon = epsilon

        self.__alternatives = set(self.aa.keys()) | set(self.pwcs.get_alternatives())
        self.__profiles = self.cps.get_ordered_profiles()
        self.__categories = self.cps.get_ordered_categories()

        self.pt.update_direction(model.criteria)

        if self.model.bpt is not None:
            self.model.bpt.update_direction(model.criteria)

            tmp_pt = self.pt.copy()
            for bp in self.model.bpt:
                tmp_pt.append(bp)

            self.ap_min = tmp_pt.get_min()
            self.ap_max = tmp_pt.get_max()
            self.ap_range = tmp_pt.get_range()
        else:
            self.ap_min = self.pt.get_min()
            self.ap_max = self.pt.get_max()
            self.ap_range = self.pt.get_range()

        for c in self.criteria:
            self.ap_min.performances[c.id] -= self.epsilon
            self.ap_max.performances[c.id] += self.epsilon
            self.ap_range.performances[c.id] += 2 * self.epsilon * 100

        solver = os.getenv('SOLVER', 'cplex')
        if solver == 'cplex':
            import cplex
            solver_max_threads = int(os.getenv('SOLVER_MAX_THREADS', 0))
            self.lp = cplex.Cplex()
            self.lp.parameters.threads.set(solver_max_threads)
            self.add_variables_cplex()
            self.add_constraints_cplex()
            self.add_objective_cplex()
            self.solve_function = self.solve_cplex
            if verbose is False:
                self.lp.set_log_stream(None)
                self.lp.set_results_stream(None)
#                self.lp.set_warning_stream(None)
#                self.lp.set_error_stream(None)
        else:
            raise NameError('Invalid solver selected')

        self.pt.update_direction(model.criteria)
        if self.model.bpt is not None:
            self.model.bpt.update_direction(model.criteria)

    def add_variables_cplex(self):
        # w_i
        self.lp.variables.add(names = ["w_" + c.id for c in self.criteria],
                              lb = [0 for c in self.criteria],
                              ub = [1 for c in self.criteria])

        # lambda
        self.lp.variables.add(names = ["lambda"], lb = [0.5], ub = [1])

        # b_i^h
        self.lp.variables.add(names = ["b_%s^%s" % (c.id, h)
                                       for h in self.__profiles
                                       for c in self.criteria],
                              lb = [self.ap_min.performances[c.id]
                                    for h in self.__profiles
                                    for c in self.criteria],
                              ub = [self.ap_max.performances[c.id] + self.epsilon
                                    for h in self.__profiles
                                    for c in self.criteria])

        # delta_i(x,b^h)
        self.lp.variables.add(names = ["delta_%s(%s,%s)" % (c.id, a, bh)
                                       for c in self.criteria
                                       for a in self.__alternatives
                                       for bh in self.__profiles],
                              types = [self.lp.variables.type.binary
                                       for c in self.criteria
                                       for a in self.__alternatives
                                       for bh in self.__profiles])

        # w_i(x,b^h)
        self.lp.variables.add(names = ["w_%s(%s,%s)" % (c.id, a, bh)
                                       for c in self.criteria
                                       for a in self.__alternatives
                                       for bh in self.__profiles],
                              lb = [0 for c in self.criteria
                                      for a in self.__alternatives
                                      for bh in self.__profiles],
                              ub = [1 for c in self.criteria
                                      for a in self.__alternatives
                                      for bh in self.__profiles])

        # y_{x,h}
        self.lp.variables.add(names = ["y_{%s,%s}" % (a, h)
                                       for a in self.__alternatives
                                       for h in self.__categories],
                              types = [self.lp.variables.type.binary
                                       for a in self.__alternatives
                                       for h in self.__categories])

    def add_dominance_constraint_cplex(self):
        constraints = self.lp.linear_constraints

        profiles = self.cps.get_ordered_profiles()
        for h, c in product(range(len(profiles) - 1), self.criteria):
            # g_j(b_h) <= g_j(b_{h+1})
            constraints.add(names= ["dominance"],
                            lin_expr =
                                [
                                 [["b_%s^%s" % (c.id, profiles[h]),
                                   "b_%s^%s" % (c.id, profiles[h + 1])],
                                  [1, -1]],
                                ],
                            senses = ["L"],
                            rhs = [0]
                           )

    def add_weights_constraint_cplex(self):
        constraints = self.lp.linear_constraints

        # sum w_j = 1
        constraints.add(names = ["wsum"],
                        lin_expr =
                            [
                             [["w_%s" % c.id for c in self.criteria],
                              [1 for c in self.criteria]],
                            ],
                        senses = ["E"],
                        rhs = [1]
                        )

    def add_assignment_constraints_cplex(self):
        constraints = self.lp.linear_constraints

        for a, c, h in product(self.__alternatives, self.criteria, self.__profiles):
            bigm = self.ap_range.performances[c.id]

            # M \delta_i(x,b^h) + b_i^h >= x_i + \epsilon
            constraints.add(names = ["d_1_%s_%s_%s" % (a, c.id, h)],
                            lin_expr =
                                [
                                 [["delta_%s(%s,%s)" % (c.id, a, h),
                                   "b_%s^%s" % (c.id,h)],
                                  [bigm, 1]]
                                ],
                            senses = ["G"],
                            rhs = [self.pt[a].performances[c.id] + self.epsilon])

            # M \delta_i(x,b^h) + b_i^h <= x_i + M
            constraints.add(names = ["d_2_%s_%s_%s" % (a, c.id, h)],
                            lin_expr =
                                [
                                 [["delta_%s(%s,%s)" % (c.id, a, h),
                                   "b_%s^%s" % (c.id,h)],
                                  [bigm, 1]]
                                ],
                            senses = ["L"],
                            rhs = [self.pt[a].performances[c.id] + bigm])

            # \delta_i(x, b^h) - w_i(x, b^h) >= 0
            constraints.add(names = ["w_1_%s_%s_%s" % (a, c.id, h)],
                            lin_expr =
                                [
                                 [["delta_%s(%s,%s)" % (c.id, a, h),
                                   "w_%s(%s,%s)" % (c.id, a, h)],
                                  [1, -1]]
                                ],
                            senses = ["G"],
                            rhs = [0])

            # w_i - w_i(x, b^h) >= 0
            constraints.add(names = ["w_2_%s_%s_%s" % (a, c.id, h)],
                            lin_expr =
                                [
                                 [["w_%s" % c.id,
                                   "w_%s(%s,%s)" % (c.id, a, h)],
                                  [1, -1]]
                                ],
                            senses = ["G"],
                            rhs = [0])

            # w_i(x, b^h) - \delta_i(x, b^h) - w_i >= - 1
            constraints.add(names = ["w_3_%s_%s_%s" % (a, c.id, h)],
                            lin_expr =
                                [
                                 [["w_%s(%s,%s)" % (c.id, a, h),
                                   "delta_%s(%s,%s)" % (c.id, a, h),
                                   "w_%s" % c.id],
                                  [1, -1, -1]]
                                ],
                            senses = ["G"],
                            rhs = [-1])

#        for a in self.__alternatives:
#            bigm = 2
#            worst_cat = self.__categories[0]
#            best_cat = self.__categories[-1]
#
#            # - \lambda + M y_{x, h = p} <= M - \epsilon
#            constraints.add(names = ["ysupmax(%s)" % a],
#                            lin_expr =
#                                [
#                                 [["lambda", "y_{%s,%s}" % (a, best_cat)],
#                                  [-1, bigm]]
#                                ],
#                            senses = ["L"],
#                            rhs = [bigm - self.epsilon])
#
#            # - \lambda - M y_{x, h = 0} >= M - 1
#            constraints.add(names = ["yinfmax(%s)" % a],
#                            lin_expr =
#                                [
#                                 [["lambda", "y_{%s,%s}" % (a, worst_cat)],
#                                  [-1, -bigm]]
#                                ],
#                            senses = ["G"],
#                            rhs = [bigm - 1])

        for a, h in product(self.__alternatives, self.__profiles):
            bigm = 2
            i = self.__profiles.index(h)
            lcat = self.__categories[i]
            ucat = self.__categories[i + 1]

            # \sum_{i \in [n]} w_i(x,b^h) - \lambda + M y_{x,h} <= M - \epsilon
            constraints.add(names = ["ysup_(%s,%s)" % (a, h)],
                            lin_expr =
                                [
                                 [["w_%s(%s,%s)" % (c.id, a, h) for c in self.criteria]
                                    + ["lambda", "y_{%s,%s}" % (a, lcat)],
                                  [1 for c in self.criteria] + [-1, bigm]
                                 ]
                                ],
                            senses = ["L"],
                            rhs = [bigm - self.epsilon])

            # \sum_{i \in [n]} w_j(x, b^{h-1}) - \lambda - M y_{x,h} >= -M
            constraints.add(names = ["yinf_(%s,%s)" % (a, h)],
                            lin_expr =
                                [
                                 [["w_%s(%s,%s)" % (c.id, a, h) for c in self.criteria]
                                    + ["lambda", "y_{%s,%s}" % (a, ucat)],
                                  [1 for c in self.criteria] + [-1, -bigm]
                                 ]
                                ],
                            senses = ["G"],
                            rhs = [-bigm])


        # \sum_{h \in {1, ..., p} y_{x,h} = 1
        for a in self.__alternatives:
            constraints.add(names = ["sum(y_{%s})" % a],
                            lin_expr =
                                [
                                 [["y_{%s,%s}" % (a, h) for h in self.__categories],
                                  [1 for h in self.__categories]]
                                ],
                            senses = ["E"],
                            rhs = [1])

        # assignment examples
        for aa in self.aa:
            constraints.add(names = ["y_{%s,%s}=1" % (aa.id, aa.category_id)],
                            lin_expr =
                                [
                                 [["y_{%s,%s}" % (aa.id, aa.category_id)],
                                  [1]]
                                ],
                            senses = "E",
                            rhs = [1])

    def add_constraints_cplex(self):
        constraints = self.lp.linear_constraints

        self.add_dominance_constraint_cplex()
        self.add_weights_constraint_cplex()
        self.add_assignment_constraints_cplex()

    def add_objective_cplex(self):
        self.lp.objective.set_sense(self.lp.objective.sense.maximize)
        self.lp.objective.set_linear([("y_{%s,%s}" % (aa.id, aa.category_id), 1)
                                      for aa in self.aa])

    def solve_cplex(self):
        self.lp.solve()

        status = self.lp.solution.get_status()
        if status != self.lp.solution.status.MIP_optimal:
            raise RuntimeError("Solver status: %s" % status)

        obj = self.lp.solution.get_objective_value()

        cvs = CriteriaValues()
        for c in self.criteria:
            cv = CriterionValue()
            cv.id = c.id
            cv.value = self.lp.solution.get_values('w_' + c.id)
            cvs.append(cv)

        self.model.cv = cvs

        self.model.lbda = self.lp.solution.get_values("lambda")

        pt = PerformanceTable()
        for p in self.__profiles:
            ap = AlternativePerformances(p)
            for c in self.criteria:
                perf = self.lp.solution.get_values("b_%s^%s" % (c.id, p))
                ap.performances[c.id] = round(perf, 5)
            pt.append(ap)

        self.model.bpt = pt
        self.model.bpt.update_direction(self.model.criteria)

        return obj

    def solve(self):
        return self.solve_function()

if __name__ == "__main__":
    from pymcda.generate import generate_random_mrsort_model
    from pymcda.generate import generate_alternatives
    from pymcda.generate import generate_random_performance_table
    from pymcda.utils import print_pt_and_assignments
    from pymcda.ui.graphic import display_electre_tri_models
    from itertools import combinations

    seed = 12
    ncrit = 5
    ncat = 3

    # Generate a random ELECTRE TRI BM model
    model = generate_random_mrsort_model(ncrit, ncat, seed)

    # Display model parameters
    print('Original model')
    print('==============')
    cids = sorted(model.criteria.keys())
    model.bpt.display(criterion_ids = cids)
    model.cv.display(criterion_ids = cids)
    print("lambda: %.7s" % model.lbda)

    # Generate a set of alternatives
    a = generate_alternatives(100)
    pt = generate_random_performance_table(a, model.criteria)

    worst = pt.get_worst(model.criteria)
    best = pt.get_best(model.criteria)

    # Assign the alternatives
    aa = model.pessimist(pt)

    # Add pairwise comparisons
    pwcs = PairwiseRelations()
    for pwa in combinations(a.keys(), 2):
        pwc = model.compare(pt[pwa[0]], pt[pwa[1]])
        if pwc.relation == PairwiseRelation.INDIFFERENT:
            continue
        pwcs.append(pwc)

    pwcs.weaker_to_preferred();

    print(f"# pairwise comparisons: {len(pwcs)}")

    # Run the MIP
    model2 = model.copy()
    model2.cv = model.cv
    model2.bpt = None
    model2.lbda = model.lbda

    mip = MipJNCSR(model2, pt, aa, pwcs)
    mip.solve()

    # Display learned model parameters
    print('Learned model')
    print('=============')
    model2.bpt.display(criterion_ids = cids)
    model2.cv.display(criterion_ids = cids)
    print("lambda: %.7s" % model2.lbda)

    # Compute assignment with the learned model
    aa2 = model2.pessimist(pt)

    # Compute CA
    total = len(a)
    nok = 0
    anok = []
    for alt in a:
        if aa(alt.id) != aa2(alt.id):
            anok.append(alt)
            nok += 1

    print("Good assignments: %3g %%" % (float(total-nok)/total*100))
    print("Bad assignments : %3g %%" % (float(nok)/total*100))

#    if len(anok) > 0:
#        print("Alternatives wrongly assigned:")
#        print_pt_and_assignments(anok, model.criteria.keys(),
#                                 [aa, aa2], pt)

    # Display models
    display_electre_tri_models([model, model2],
                               [worst, worst], [best, best])
