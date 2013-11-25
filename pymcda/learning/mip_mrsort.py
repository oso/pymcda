from __future__ import division
import os, sys
from itertools import product
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../../")
from pymcda.types import CriterionValue, CriteriaValues
from pymcda.types import AlternativePerformances, PerformanceTable

verbose = False

try:
    solver = os.environ['SOLVER']
except:
    solver = 'cplex'

if solver == 'cplex':
    import cplex
elif solver == 'glpk':
    import pymprog
else:
    raise NameError('Invalid solver selected')

class MipMRSort():

    def __init__(self, model, pt, aa, epsilon = 0.0001):
        self.pt = pt
        self.aa = aa
        self.model = model
        self.criteria = model.criteria.get_active()
        self.cps = model.categories_profiles

        self.epsilon = epsilon

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

        if solver == 'glpk':
            self.lp = pymprog.model('lp_elecre_tri_weights')
            self.lp.verb = verbose
            self.add_variables_glpk()
            self.add_constraints_glpk()
            self.add_extra_constraints_glpk()
            self.add_objective_glpk()
        elif solver == 'cplex':
            self.lp = cplex.Cplex()
            self.add_variables_cplex()
            self.add_constraints_cplex()
            self.add_extra_constraints_cplex()
            self.add_objective_cplex()
            if verbose is False:
                self.lp.set_log_stream(None)
                self.lp.set_results_stream(None)
#                self.lp.set_warning_stream(None)
#                self.lp.set_error_stream(None)

        self.pt.update_direction(model.criteria)
        if self.model.bpt is not None:
            self.model.bpt.update_direction(model.criteria)

    def add_variables_glpk(self):
        n = len(self.criteria)
        m = len(self.aa)
        ncat = len(self.__categories)
        a1 = self.aa.get_alternatives_in_categories(self.__categories[1:])
        a2 = self.aa.get_alternatives_in_categories(self.__categories[:-1])

        self.a = {}
        for a in self.aa:
            self.a[a.id] = self.lp.var(name = "a_%s" % a.id, kind = bool)

        self.w = {}
        for c in self.criteria:
            self.w[c.id] = self.lp.var(name = "w_%s" % c.id, bounds = (0, 1))

        self.lbda = self.lp.var(name = 'lambda', bounds = (0.5, 1))

        self.g = {p: {} for p in self.__profiles}
        for p, c in product(self.__profiles, self.criteria):
            self.g[p][c.id] = self.lp.var(name = "g_%s_%s" % (p, c.id),
                                          bounds = (self.ap_min.performances[c.id],
                                                    self.ap_max.performances[c.id]))

        self.cinf = {a: {} for a in a1}
        self.dinf = {a: {} for a in a1}
        for a, c in product(a1, self.criteria):
            self.cinf[a][c.id] = self.lp.var(name = "cinf_%s_%s" % (a, c.id),
                                             bounds = (0, 1))
            self.dinf[a][c.id] = self.lp.var(name = "dinf_%s_%s" % (a, c.id),
                                             kind = bool)

        self.csup = {a: {} for a in a2}
        self.dsup = {a: {} for a in a2}
        for a, c in product(a2, self.criteria):
            self.csup[a][c.id] = self.lp.var(name = "csup_%s_%s" % (a, c.id),
                                             bounds = (0, 1))
            self.dsup[a][c.id] = self.lp.var(name = "dsup_%s_%s" % (a, c.id),
                                             kind = bool)

    def add_variables_cplex(self):
        self.lp.variables.add(names = ["a_" + a for a in self.aa.keys()],
                              types = [self.lp.variables.type.binary
                                       for a in self.aa.keys()])
        self.lp.variables.add(names = ["lambda"], lb = [0.5], ub = [1])
        self.lp.variables.add(names = ["w_" + c.id for c in self.criteria],
                              lb = [0 for c in self.criteria],
                              ub = [1 for c in self.criteria])
        self.lp.variables.add(names = ["g_%s_%s" % (profile, c.id)
                                       for profile in self.__profiles
                                       for c in self.criteria],
                              lb = [self.ap_min.performances[c.id]
                                    for profile in self.__profiles
                                    for c in self.criteria],
                              ub = [self.ap_max.performances[c.id] + self.epsilon
                                    for profile in self.__profiles
                                    for c in self.criteria])

        a1 = self.aa.get_alternatives_in_categories(self.__categories[1:])
        a2 = self.aa.get_alternatives_in_categories(self.__categories[:-1])
        self.lp.variables.add(names = ["cinf_%s_%s" % (a, c.id)
                                       for a in a1
                                       for c in self.criteria],
                              lb = [0 for a in a1 for c in self.criteria],
                              ub = [1 for a in a1 for c in self.criteria])
        self.lp.variables.add(names = ["csup_%s_%s" % (a, c.id)
                                       for a in a2
                                       for c in self.criteria],
                              lb = [0 for a in a2 for c in self.criteria],
                              ub = [1 for a in a2 for c in self.criteria])
        self.lp.variables.add(names = ["dinf_%s_%s" % (a, c.id)
                                       for a in a1
                                       for c in self.criteria],
                              types = [self.lp.variables.type.binary
                                       for a in a1
                                       for c in self.criteria])
        self.lp.variables.add(names = ["dsup_%s_%s" % (a, c.id)
                                       for a in a2
                                       for c in self.criteria],
                              types = [self.lp.variables.type.binary
                                       for a in a2
                                       for c in self.criteria])

    def __add_lower_constraints_glpk(self, aa):
        i = self.__categories.index(aa.category_id)
        b = self.__profiles[i - 1]

        # sum cinf_j(a_i, b_{h-1}) >= lambda - 2 (1 - alpha_i)
        self.lp.st(sum(self.cinf[aa.id].values()) \
                   >= self.lbda - 2 + 2 * self.a[aa.id])

        for c in self.criteria:
            bigm = self.ap_range.performances[c.id]

            # cinf_j(a_i, b_{h-1}) <= w_j
            self.lp.st(self.cinf[aa.id][c.id] <= self.w[c.id])

            # cinf_j(a_i, b_{h-1}) <= dinf_{i,j}
            self.lp.st(self.cinf[aa.id][c.id] <= self.dinf[aa.id][c.id])

            # cinf_j(a_i, b_{h-1}) >= dinf_{i,j} - 1 + w_j
            self.lp.st(self.cinf[aa.id][c.id] >= self.dinf[aa.id][c.id] - 1
                                                 + self.w[c.id])

            # M dinf_(i,j) > a_{i,j} - b_{h-1,j}
            self.lp.st(bigm * self.dinf[aa.id][c.id] >= \
                                        self.pt[aa.id].performances[c.id] \
                                        - self.g[b][c.id] + self.epsilon)

            # M dinf_(i,j) <= a_{i,j} - b_{h-1,j} + M
            self.lp.st(bigm * self.dinf[aa.id][c.id] <= \
                                        self.pt[aa.id].performances[c.id] \
                                        - self.g[b][c.id] + bigm)

    def __add_upper_constraints_glpk(self, aa):
        i = self.__categories.index(aa.category_id)
        b = self.__profiles[i]

        # sum csup_j(a_i, b_{h-1}) < lambda + 2 (1 - alpha_i)
        self.lp.st(sum(self.csup[aa.id].values()) \
                   <= self.lbda + 2 - 2 * self.a[aa.id] - self.epsilon)

        for c in self.criteria:
            bigm = self.ap_range.performances[c.id]

            # csup_j(a_i, b_h) <= w_j
            self.lp.st(self.csup[aa.id][c.id] <= self.w[c.id])

            # csup_j(a_i, b_h) <= dsup_{i,j}
            self.lp.st(self.csup[aa.id][c.id] <= self.dsup[aa.id][c.id])

            # csup_j(a_i, b_{h-1}) >= dsup_{i,j} - 1 + w_j
            self.lp.st(self.csup[aa.id][c.id] >= self.dsup[aa.id][c.id] - 1
                                                 + self.w[c.id])

            # M dsup_(i,j) > a_{i,j} - b_{h,j}
            self.lp.st(bigm * self.dsup[aa.id][c.id] >= \
                                        self.pt[aa.id].performances[c.id] \
                                        - self.g[b][c.id] + self.epsilon)

            # M dsup_(i,j) <= a_{i,j} - b_{h,j} + M
            self.lp.st(bigm * self.dsup[aa.id][c.id] <= \
                                        self.pt[aa.id].performances[c.id] \
                                        - self.g[b][c.id] + bigm)

    def add_constraints_glpk(self):
        self.add_lower_constraints = self.__add_lower_constraints_glpk
        self.add_upper_constraints = self.__add_upper_constraints_glpk
        self.add_alternatives_constraints()

        profiles = self.cps.get_ordered_profiles()
        for h, c in product(range(len(profiles) - 1), self.criteria):
            # g_j(b_h) <= g_j(b_{h+1})
            self.lp.st(self.g[profiles[h]][c.id] <= \
                                            self.g[profiles[h + 1]][c.id])

        # sum w_j = 1
        if self.model.cv is None:
            self.lp.st(sum(self.w.values()) == 1)

    def add_extra_constraints_glpk(self):
        if self.model.lbda is not None:
            self.lp.st(self.lbda == self.model.lbda)

        if self.model.cv is not None:
            for c in self.criteria:
                self.lp.st(self.w[c.id] == self.model.cv[c.id].value)

        if self.model.bpt is not None:
            for bp, c in product(self.model.bpt, self.model.criteria):
                self.lp.st(self.g[bp.id][c.id] == bp.performances[c.id])

    def __add_lower_constraints_cplex(self, aa):
        constraints = self.lp.linear_constraints
        i = self.__categories.index(aa.category_id)
        b = self.__profiles[i - 1]

        # sum cinf_j(a_i, b_{h-1}) >= lambda - 2 (1 - alpha_i)
        constraints.add(names = ["gamma_inf_%s" % (aa.id)],
                        lin_expr =
                            [
                             [["cinf_%s_%s" % (aa.id, c.id)
                               for c in self.criteria] + \
                              ["lambda"] + ["a_%s" % aa.id],
                              [1 for c in self.criteria] + [-1] + [-2]],
                            ],
                        senses = ["G"],
                        rhs = [-2]
                       )

        for c in self.criteria:
            bigm = self.ap_range.performances[c.id]

            # cinf_j(a_i, b_{h-1}) <= w_j
            constraints.add(names = ["c_cinf_%s_%s" % (aa.id, c.id)],
                            lin_expr =
                                [
                                 [["cinf_%s_%s" % (aa.id, c.id),
                                   "w_" + c.id],
                                  [1, -1]],
                                ],
                            senses = ["L"],
                            rhs = [0]
                           )

            # cinf_j(a_i, b_{h-1}) <= dinf_{i,j}
            constraints.add(names = ["c_cinf2_%s_%s" % (aa.id, c.id)],
                            lin_expr =
                                [
                                 [["cinf_%s_%s" % (aa.id, c.id),
                                   "dinf_%s_%s" % (aa.id, c.id)],
                                  [1, -1]],
                                ],
                            senses = ["L"],
                            rhs = [0]
                           )

            # cinf_j(a_i, b_{h-1}) >= dinf_{i,j} - 1 + w_j
            constraints.add(names = ["c_cinf3_%s_%s" % (aa.id, c.id)],
                            lin_expr =
                                [
                                 [["cinf_%s_%s" % (aa.id, c.id),
                                   "dinf_%s_%s" % (aa.id, c.id),
                                   "w_" + c.id],
                                  [1, -1, -1]],
                                ],
                            senses = ["G"],
                            rhs = [-1]
                           )

            # M dinf_(i,j) > a_{i,j} - b_{h-1,j}
            constraints.add(names = ["d_dinf_%s_%s" % (aa.id, c.id)],
                            lin_expr =
                                [
                                 [["dinf_%s_%s" % (aa.id, c.id),
                                   "g_%s_%s" % (b, c.id)],
                                  [bigm, 1]],
                                ],
                            senses = ["G"],
                            rhs = [self.pt[aa.id].performances[c.id] +
                                   self.epsilon]
                           )

            # M dinf_(i,j) <= a_{i,j} - b_{h-1,j} + M
            constraints.add(names = ["d_dinf_%s_%s" % (aa.id, c.id)],
                            lin_expr =
                                [
                                 [["dinf_%s_%s" % (aa.id, c.id),
                                   "g_%s_%s" % (b, c.id)],
                                  [bigm, 1]],
                                ],
                            senses = ["L"],
                            rhs = [self.pt[aa.id].performances[c.id] + bigm]
                           )

    def __add_upper_constraints_cplex(self, aa):
        constraints = self.lp.linear_constraints
        i = self.__categories.index(aa.category_id)
        b = self.__profiles[i]

        # sum csup_j(a_i, b_{h-1}) < lambda + 2 (1 - alpha_i)
        constraints.add(names = ["gamma_sup_%s" % (aa.id)],
                        lin_expr =
                            [
                             [["csup_%s_%s" % (aa.id, c.id)
                               for c in self.criteria] + \
                              ["lambda"] + ["a_%s" % aa.id],
                              [1 for c in self.criteria] + [-1] + [2]],
                            ],
                        senses = ["L"],
                        rhs = [2 - self.epsilon]
                       )

        for c in self.criteria:
            bigm = self.ap_range.performances[c.id]

            # csup_j(a_i, b_h) <= w_j
            constraints.add(names = ["c_csup_%s_%s" % (aa.id, c.id)],
                            lin_expr =
                                [
                                 [["csup_%s_%s" % (aa.id, c.id),
                                   "w_" + c.id],
                                  [1, -1]],
                                ],
                            senses = ["L"],
                            rhs = [0]
                           )

            # csup_j(a_i, b_h) <= dsup_{i,j}
            constraints.add(names = ["c_csup2_%s_%s" % (aa.id, c.id)],
                            lin_expr =
                                [
                                 [["csup_%s_%s" % (aa.id, c.id),
                                   "dsup_%s_%s" % (aa.id, c.id)],
                                  [1, -1]],
                                ],
                            senses = ["L"],
                            rhs = [0]
                           )

            # csup_j(a_i, b_{h-1}) >= dsup_{i,j} - 1 + w_j
            constraints.add(names = ["c_csup3_%s_%s" % (aa.id, c.id)],
                            lin_expr =
                                [
                                 [["csup_%s_%s" % (aa.id, c.id),
                                   "dsup_%s_%s" % (aa.id, c.id),
                                   "w_" + c.id],
                                  [1, -1, -1]],
                                ],
                            senses = ["G"],
                            rhs = [-1]
                           )

            # M dsup_(i,j) > a_{i,j} - b_{h,j}
            constraints.add(names = ["d_dsup_%s_%s" % (aa.id, c.id)],
                            lin_expr =
                                [
                                 [["dsup_%s_%s" % (aa.id, c.id),
                                   "g_%s_%s" % (b, c.id)],
                                  [bigm, 1]],
                                ],
                            senses = ["G"],
                            rhs = [self.pt[aa.id].performances[c.id] +
                                   self.epsilon]
                           )

            # M dsup_(i,j) <= a_{i,j} - b_{h,j} + M
            constraints.add(names = ["d_dsup_%s_%s" % (aa.id, c.id)],
                            lin_expr =
                                [
                                 [["dsup_%s_%s" % (aa.id, c.id),
                                   "g_%s_%s" % (b, c.id)],
                                  [bigm, 1]],
                                ],
                            senses = ["L"],
                            rhs = [self.pt[aa.id].performances[c.id] + bigm]
                           )

    def add_alternatives_constraints(self):
        lower_cat = self.__categories[0]
        upper_cat = self.__categories[-1]

        for aa in self.aa:
            cat = aa.category_id

            if cat != lower_cat:
                self.add_lower_constraints(aa)

            if cat != upper_cat:
                self.add_upper_constraints(aa)

    def add_constraints_cplex(self):
        constraints = self.lp.linear_constraints

        self.add_lower_constraints = self.__add_lower_constraints_cplex
        self.add_upper_constraints = self.__add_upper_constraints_cplex
        self.add_alternatives_constraints()

        profiles = self.cps.get_ordered_profiles()
        for h, c in product(range(len(profiles) - 1), self.criteria):
            # g_j(b_h) <= g_j(b_{h+1})
            constraints.add(names= ["dominance"],
                            lin_expr =
                                [
                                 [["g_%s_%s" % (profiles[h], c.id),
                                   "g_%s_%s" % (profiles[h + 1], c.id)],
                                  [1, -1]],
                                ],
                            senses = ["L"],
                            rhs = [0]
                           )

        # sum w_j = 1
        if self.model.cv is None:
            constraints.add(names = ["wsum"],
                            lin_expr =
                                [
                                 [["w_%s" % c.id for c in self.criteria],
                                  [1 for c in self.criteria]],
                                ],
                            senses = ["E"],
                            rhs = [1]
                            )

    def add_extra_constraints_cplex(self):
        constraints = self.lp.linear_constraints

        if self.model.lbda is not None:
            constraints.add(names = ["lambda"],
                            lin_expr =
                                [
                                 [["lambda"],
                                  [1]]
                                 ],
                            senses = ["E"],
                            rhs = [self.model.lbda]
                           )

        if self.model.cv is not None:
            for c in self.criteria:
                constraints.add(names = ["w_%s" % c.id],
                                lin_expr =
                                    [
                                     [["w_%s" % c.id],
                                      [1]]
                                     ],
                                senses = ["E"],
                                rhs = [self.model.cv[c.id].value]
                               )

        if self.model.bpt is not None:
            for bp, c in product(self.model.bpt, self.model.criteria):
                constraints.add(names = ["g_%s_%s" % (bp.id, c.id)],
                                lin_expr =
                                    [
                                     [["g_%s_%s" % (bp.id, c.id)],
                                      [1]]
                                     ],
                                senses = ["E"],
                                rhs = [bp.performances[c.id]]
                               )

    def add_objective_glpk(self):
        self.lp.max(sum(self.a.values()))

    def add_objective_cplex(self):
        self.lp.objective.set_sense(self.lp.objective.sense.maximize)
        self.lp.objective.set_linear([("a_%s" % aid, 1)
                                      for aid in self.aa.keys()])

    def solve_cplex(self):
        self.lp.solve()

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
                perf = self.lp.solution.get_values("g_%s_%s" % (p, c.id))
                ap.performances[c.id] = round(perf, 5)
            pt.append(ap)

        self.model.bpt = pt
        self.model.bpt.update_direction(self.model.criteria)

        return obj

    def solve_glpk(self):
        self.lp.solvopt(method='exact', integer='advanced')
        self.lp.solve()

        status = self.lp.status()
        if status != 'opt':
            raise RuntimeError("Solver status: %s" % self.lp.status())

        #print(self.lp.reportKKT())
        obj = self.lp.vobj()

        cvs = CriteriaValues()
        for c in self.criteria:
            cv = CriterionValue()
            cv.id = c.id
            cv.value = float(self.w[c.id].primal)
            cvs.append(cv)

        self.model.cv = cvs
        self.model.lbda = self.lbda.primal

        pt = PerformanceTable()
        for p in self.__profiles:
            ap = AlternativePerformances(p)
            for c in self.criteria:
                perf = self.g[p][c.id].primal
                ap.performances[c.id] = round(perf, 5)
            pt.append(ap)

        self.model.bpt = pt
        self.model.bpt.update_direction(self.model.criteria)

        return obj

    def solve(self):
        if solver == 'glpk':
            return self.solve_glpk()
        elif solver == 'cplex':
            return self.solve_cplex()

if __name__ == "__main__":
    from pymcda.generate import generate_random_mrsort_model
    from pymcda.generate import generate_alternatives
    from pymcda.generate import generate_random_performance_table
    from pymcda.utils import display_assignments_and_pt
    from pymcda.ui.graphic import display_electre_tri_models

    seed = 12
    ncrit = 5
    ncat = 3

    # Generate a random ELECTRE TRI BM model
    model = generate_random_mrsort_model(ncrit, ncat, seed)

    # Display model parameters
    print('Original model')
    print('==============')
    cids = model.criteria.keys()
    cids.sort()
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

    # Run the MIP
    model2 = model.copy()
    model2.cv = model.cv
    model2.bpt = None
    model2.lbda = model.lbda

    mip = MipMRSort(model2, pt, aa)
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

    if len(anok) > 0:
        print("Alternatives wrongly assigned:")
        display_assignments_and_pt(anok, model.criteria, [aa, aa2],
                                   [pt])

    # Display models
    display_electre_tri_models([model, model2],
                               [worst, worst], [best, best])
