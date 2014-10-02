from __future__ import division
import os, sys
from itertools import product
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../../")
from pymcda.types import CriterionValue, CriteriaValues
from pymcda.types import AlternativePerformances, PerformanceTable
from pymcda.types import CriteriaSet
from itertools import combinations
from pymcda.utils import powerset

verbose = False

class MipCMRSort():

    def __init__(self, model, pt, aa, epsilon = 0.0001):
        self.pt = pt
        self.aa = aa
        self.model = model
        self.criteria = model.criteria.get_active()
        self.cps = model.categories_profiles

        self.epsilon = epsilon

        self.__profiles = self.cps.get_ordered_profiles()
        self.__categories = self.cps.get_ordered_categories()

        cids = self.criteria.keys()
        self.m2indices = [frozenset(c) for c in combinations(cids, 2)]

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
        self.lp.variables.add(names = ["alphainf_%s_%s" % (a, c)
                                       for a in a1
                                       for c in self.m2indices],
                              lb = [0 for a in a1 for c in self.m2indices],
                              ub = [1 for a in a1 for c in self.m2indices])
        self.lp.variables.add(names = ["alphasup_%s_%s" % (a, c)
                                       for a in a2
                                       for c in self.m2indices],
                              lb = [0 for a in a2 for c in self.m2indices],
                              ub = [1 for a in a2 for c in self.m2indices])
        self.lp.variables.add(names = ["betainf_%s_%s" % (a, c)
                                       for a in a1
                                       for c in self.m2indices],
                              lb = [0 for a in a1 for c in self.m2indices],
                              ub = [1 for a in a1 for c in self.m2indices])
        self.lp.variables.add(names = ["betasup_%s_%s" % (a, c)
                                       for a in a2
                                       for c in self.m2indices],
                              lb = [0 for a in a2 for c in self.m2indices],
                              ub = [1 for a in a2 for c in self.m2indices])
        self.lp.variables.add(names = ["Dinf_%s_%s" % (a, c)
                                       for a in a1
                                       for c in self.m2indices],
                              types = [self.lp.variables.type.binary
                                       for a in a1
                                       for c in self.m2indices])
        self.lp.variables.add(names = ["Dsup_%s_%s" % (a, c)
                                       for a in a2
                                       for c in self.m2indices],
                              types = [self.lp.variables.type.binary
                                       for a in a2
                                       for c in self.m2indices])

        self.lp.variables.add(names = ["m_%s" % c.id for c in self.criteria],
                              lb = [0 for c in self.criteria],
                              ub = [1 for c in self.criteria])
        self.lp.variables.add(names = ["m2p_%s" % c for c in self.m2indices],
                              lb = [0 for c in self.m2indices],
                              ub = [1 for c in self.m2indices])
        self.lp.variables.add(names = ["m2n_%s" % c for c in self.m2indices],
                              lb = [0 for c in self.m2indices],
                              ub = [1 for c in self.m2indices])

        self.lp.variables.add(names = ["g_%s_%s" % (profile, c.id)
                                       for profile in self.__profiles
                                       for c in self.criteria],
                              lb = [self.ap_min.performances[c.id]
                                    for profile in self.__profiles
                                    for c in self.criteria],
                              ub = [self.ap_max.performances[c.id] + self.epsilon
                                    for profile in self.__profiles
                                    for c in self.criteria])

        self.lp.variables.add(names = ["a_" + a for a in self.aa.keys()],
                              types = [self.lp.variables.type.binary
                                       for a in self.aa.keys()])

        self.lp.variables.add(names = ["lambda"], lb = [0.5], ub = [1])

    def __add_lower_constraints_cplex(self, aa):
        constraints = self.lp.linear_constraints
        i = self.__categories.index(aa.category_id)
        b = self.__profiles[i - 1]

        # sum cinf_j(a_i, b_{h-1}) + ...  >= lambda - 2 (1 - alpha_i)
        constraints.add(names = ["gamma_inf_%s" % (aa.id)],
                        lin_expr =
                            [
                             [["cinf_%s_%s" % (aa.id, c.id)
                               for c in self.criteria] + \
                              ["alphainf_%s_%s" % (aa.id, m2)
                               for m2 in self.m2indices] + \
                              ["betainf_%s_%s" % (aa.id, m2)
                               for m2 in self.m2indices] + \
                              ["lambda"] + ["a_%s" % aa.id],
                              [1 for c in self.criteria] + \
                              [1 for m2 in self.m2indices] + \
                              [-1 for m2 in self.m2indices] + \
                              [-1] + [-2]],
                            ],
                        senses = ["G"],
                        rhs = [-2]
                       )

        for c in self.criteria:
            bigm = self.ap_range.performances[c.id]

            # cinf_j(a_i, b_{h-1}) <= m_j
            constraints.add(names = ["c_cinf_%s_%s" % (aa.id, c.id)],
                            lin_expr =
                                [
                                 [["cinf_%s_%s" % (aa.id, c.id),
                                   "m_" + c.id],
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

            # cinf_j(a_i, b_{h-1}) >= dinf_{i,j} - 1 + m_j
            constraints.add(names = ["c_cinf3_%s_%s" % (aa.id, c.id)],
                            lin_expr =
                                [
                                 [["cinf_%s_%s" % (aa.id, c.id),
                                   "dinf_%s_%s" % (aa.id, c.id),
                                   "m_" + c.id],
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

        for m2 in self.m2indices:
            c1, c2 = m2

            # dinf_{a,j} + dinf_{a,k} >= 2Dinf_{a,j,k}
            constraints.add(names = ["D_Dinf_%s_%s" % (aa.id, m2)],
                            lin_expr =
                                [
                                 [["dinf_%s_%s" % (aa.id, c1),
                                   "dinf_%s_%s" % (aa.id, c2),
                                   "Dinf_%s_%s" % (aa.id, m2)],
                                  [1, 1, -2]],
                                ],
                            senses = ["G"],
                            rhs = [0]
                           )

            # dinf_{a,j} + dinf_{a,k} <= Dinf_{a,j,k} + 1
            constraints.add(names = ["D2_Dinf_%s_%s" % (aa.id, m2)],
                            lin_expr =
                                [
                                 [["dinf_%s_%s" % (aa.id, c1),
                                   "dinf_%s_%s" % (aa.id, c2),
                                   "Dinf_%s_%s" % (aa.id, m2)],
                                  [1, 1, -1]],
                                ],
                            senses = ["L"],
                            rhs = [1]
                           )

            # alpha_{a,j,k} <= Dinf_{a,j,k}
            constraints.add(names = ["D3_Dinf_%s_%s" % (aa.id, m2)],
                            lin_expr =
                                [
                                 [["alphainf_%s_%s" % (aa.id, m2),
                                   "Dinf_%s_%s" % (aa.id, m2)],
                                  [1, -1]],
                                ],
                            senses = ["L"],
                            rhs = [0]
                           )

            # beta_{a,j,k} <= Dinf_{a,j,k}
            constraints.add(names = ["D4_Dinf_%s_%s" % (aa.id, m2)],
                            lin_expr =
                                [
                                 [["betainf_%s_%s" % (aa.id, m2),
                                   "Dinf_%s_%s" % (aa.id, m2)],
                                  [1, -1]],
                                ],
                            senses = ["L"],
                            rhs = [0]
                           )

            # alpha_{a,j,k} <= m2p_{j,k}
            constraints.add(names = ["D5_Dinf_%s_%s" % (aa.id, m2)],
                            lin_expr =
                                [
                                 [["alphainf_%s_%s" % (aa.id, m2),
                                   "m2p_%s" % m2],
                                  [1, -1]],
                                ],
                            senses = ["L"],
                            rhs = [0]
                           )

            # beta_{a,j,k} <= m2n_{j,k}
            constraints.add(names = ["D6_Dinf_%s_%s" % (aa.id, m2)],
                            lin_expr =
                                [
                                 [["betainf_%s_%s" % (aa.id, m2),
                                   "m2n_%s" % m2],
                                  [1, -1]],
                                ],
                            senses = ["L"],
                            rhs = [0]
                           )

            # alpha_{a,j,k} - Dinf_{a,j,k} - m2p_{j,k} >= -1
            constraints.add(names = ["D7_Dinf_%s_%s" % (aa.id, m2)],
                            lin_expr =
                                [
                                 [["alphainf_%s_%s" % (aa.id, m2),
                                   "Dinf_%s_%s" % (aa.id, m2),
                                   "m2p_%s" % m2],
                                  [1, -1, -1]],
                                ],
                            senses = ["G"],
                            rhs = [-1]
                           )

            # beta_{a,j,k} - Dinf_{a,j,k} - m2n_{j,k} >= -1
            constraints.add(names = ["D8_Dinf_%s_%s" % (aa.id, m2)],
                            lin_expr =
                                [
                                 [["betainf_%s_%s" % (aa.id, m2),
                                   "Dinf_%s_%s" % (aa.id, m2),
                                   "m2n_%s" % m2],
                                  [1, -1, -1]],
                                ],
                            senses = ["G"],
                            rhs = [-1]
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
                              ["alphasup_%s_%s" % (aa.id, m2)
                               for m2 in self.m2indices] + \
                              ["betasup_%s_%s" % (aa.id, m2)
                               for m2 in self.m2indices] + \
                              ["lambda"] + ["a_%s" % aa.id],
                              [1 for c in self.criteria] + \
                              [1 for m2 in self.m2indices] + \
                              [-1 for m2 in self.m2indices] + \
                              [-1] + [2]],
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
                                   "m_" + c.id],
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
                                   "m_" + c.id],
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

        for m2 in self.m2indices:
            c1, c2 = m2

            # dsup_{a,j} + dsup_{a,k} >= 2Dsup_{a,j,k}
            constraints.add(names = ["D_Dsup_%s_%s" % (aa.id, m2)],
                            lin_expr =
                                [
                                 [["dsup_%s_%s" % (aa.id, c1),
                                   "dsup_%s_%s" % (aa.id, c2),
                                   "Dsup_%s_%s" % (aa.id, m2)],
                                  [1, 1, -2]],
                                ],
                            senses = ["G"],
                            rhs = [0]
                           )

            # dsup_{a,j} + dsup_{a,k} <= Dsup_{a,j,k} + 1
            constraints.add(names = ["D2_Dsup_%s_%s" % (aa.id, m2)],
                            lin_expr =
                                [
                                 [["dsup_%s_%s" % (aa.id, c1),
                                   "dsup_%s_%s" % (aa.id, c2),
                                   "Dsup_%s_%s" % (aa.id, m2)],
                                  [1, 1, -1]],
                                ],
                            senses = ["L"],
                            rhs = [1]
                           )

            # alpha_{a,j,k} <= Dinf_{a,j,k}
            constraints.add(names = ["D3_Dsup_%s_%s" % (aa.id, m2)],
                            lin_expr =
                                [
                                 [["alphasup_%s_%s" % (aa.id, m2),
                                   "Dsup_%s_%s" % (aa.id, m2)],
                                  [1, -1]],
                                ],
                            senses = ["L"],
                            rhs = [0]
                           )

            # beta_{a,j,k} <= Dinf_{a,j,k}
            constraints.add(names = ["D4_Dsup_%s_%s" % (aa.id, m2)],
                            lin_expr =
                                [
                                 [["betasup_%s_%s" % (aa.id, m2),
                                   "Dsup_%s_%s" % (aa.id, m2)],
                                  [1, -1]],
                                ],
                            senses = ["L"],
                            rhs = [0]
                           )

            # alpha_{a,j,k} <= m2p_{j,k}
            constraints.add(names = ["D5_Dsup_%s_%s" % (aa.id, m2)],
                            lin_expr =
                                [
                                 [["alphasup_%s_%s" % (aa.id, m2),
                                   "m2p_%s" % m2],
                                  [1, -1]],
                                ],
                            senses = ["L"],
                            rhs = [0]
                           )

            # beta_{a,j,k} <= m2n_{j,k}
            constraints.add(names = ["D6_Dsup_%s_%s" % (aa.id, m2)],
                            lin_expr =
                                [
                                 [["betasup_%s_%s" % (aa.id, m2),
                                   "m2n_%s" % m2],
                                  [1, -1]],
                                ],
                            senses = ["L"],
                            rhs = [0]
                           )

            # alpha_{a,j,k} - Dinf_{a,j,k} - m2p_{j,k} >= -1
            constraints.add(names = ["D7_Dsup_%s_%s" % (aa.id, m2)],
                            lin_expr =
                                [
                                 [["alphasup_%s_%s" % (aa.id, m2),
                                   "Dsup_%s_%s" % (aa.id, m2),
                                   "m2p_%s" % m2],
                                  [1, -1, -1]],
                                ],
                            senses = ["G"],
                            rhs = [-1]
                           )

            # beta_{a,j,k} - Dinf_{a,j,k} - m2n_{j,k} >= -1
            constraints.add(names = ["D8_Dsup_%s_%s" % (aa.id, m2)],
                            lin_expr =
                                [
                                 [["betasup_%s_%s" % (aa.id, m2),
                                   "Dsup_%s_%s" % (aa.id, m2),
                                   "m2n_%s" % m2],
                                  [1, -1, -1]],
                                ],
                            senses = ["G"],
                            rhs = [-1]
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
        constraints.add(names = ["wsum"],
                        lin_expr =
                            [
                             [["m_%s" % c.id for c in self.criteria] +
                              ["m2p_%s" % m2 for m2 in self.m2indices] +
                              ["m2n_%s" % m2 for m2 in self.m2indices],
                              [1 for c in self.criteria] +
                              [1 for m2 in self.m2indices] +
                              [-1 for m2 in self.m2indices]],
                            ],
                        senses = ["E"],
                        rhs = [1]
                        )

        # w_j + sum_{k \in J} m_{j,k} >= 0
        criteria = set(self.model.criteria.keys())
        for c in self.criteria:
            for c2 in (set(self.criteria.keys()) ^ set([c.id])):
                m2 = frozenset([c.id, c2])
                constraints.add(names = ["u_%s_%s" % (c.id, c2)],
                                lin_expr = [
                                            [["m_%s" % c.id] +
                                             ["m2p_%s" % m2] +
                                             ["m2n_%s" % m2] ,
                                             [1, 1, -1]]
                                           ],
                                senses = ["G"],
                                rhs = [0],
                               )

    def add_objective_cplex(self):
        self.lp.objective.set_sense(self.lp.objective.sense.maximize)
        self.lp.objective.set_linear([("a_%s" % aid, 1)
                                      for aid in self.aa.keys()])

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
            cv.value = self.lp.solution.get_values('m_' + c.id)
            cvs.append(cv)

        for c in self.m2indices:
            cv = CriterionValue()
            cv.id = CriteriaSet(c)
            cv.value = self.lp.solution.get_values("m2p_%s" % c)
            cv.value -= self.lp.solution.get_values("m2n_%s" % c)
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

    def solve(self):
        return self.solve_function()

if __name__ == "__main__":
    from pymcda.electre_tri import MRSort
    from pymcda.generate import generate_alternatives
    from pymcda.generate import generate_categories
    from pymcda.generate import generate_categories_profiles
    from pymcda.generate import generate_random_performance_table
    from pymcda.generate import generate_criteria
    from pymcda.types import AlternativeAssignment
    from pymcda.types import AlternativesAssignments
    from pymcda.utils import print_pt_and_assignments
    from pymcda.ui.graphic import display_electre_tri_models

    cat = generate_categories(2)
    cps = generate_categories_profiles(cat)
    c = generate_criteria(4)

    # Generate assignment incompatible with an MR-Sort model
    ap1 = AlternativePerformances('a1', {'c1': 1, 'c2': 1, 'c3': 0, 'c4': 0})
    ap2 = AlternativePerformances('a2', {'c1': 0, 'c2': 0, 'c3': 1, 'c4': 1})
    ap3 = AlternativePerformances('a3', {'c1': 1, 'c2': 0, 'c3': 1, 'c4': 0})
    ap4 = AlternativePerformances('a4', {'c1': 1, 'c2': 0, 'c3': 0, 'c4': 1})
    ap5 = AlternativePerformances('a5', {'c1': 0, 'c2': 1, 'c3': 1, 'c4': 0})
    ap6 = AlternativePerformances('a6', {'c1': 0, 'c2': 1, 'c3': 0, 'c4': 1})
    pt = PerformanceTable([ap1, ap2, ap3, ap4, ap5, ap6])

    aa1 = AlternativeAssignment('a1', 'cat1')
    aa2 = AlternativeAssignment('a2', 'cat1')
    aa3 = AlternativeAssignment('a3', 'cat2')
    aa4 = AlternativeAssignment('a4', 'cat2')
    aa5 = AlternativeAssignment('a5', 'cat2')
    aa6 = AlternativeAssignment('a6', 'cat2')
    aa = AlternativesAssignments([aa1, aa2, aa3, aa4, aa5, aa6])
    print_pt_and_assignments(aa, c, [aa], pt)

    model = MRSort(c, None, None, None, cps)

    worst = pt.get_worst(model.criteria)
    best = pt.get_best(model.criteria)

    # Run the MIP
    mip = MipCMRSort(model, pt, aa)
    mip.solve()

    # Display learned model parameters
    print('Learned model')
    print('=============')
    model.bpt.display()
    model.cv.display()
    print("lambda: %.7s" % model.lbda)

    # Compute assignment with the learned model
    aa2 = model.pessimist(pt)

    # Compute CA
    total = len(aa)
    nok = 0
    anok = []
    for alt in aa:
        if aa(alt.id) != aa2(alt.id):
            anok.append(alt)
            nok += 1

    print("Good assignments: %3g %%" % (float(total-nok)/total*100))
    print("Bad assignments : %3g %%" % (float(nok)/total*100))

    if len(anok) > 0:
        print("Alternatives wrongly assigned:")
        print_pt_and_assignments(anok, model.criteria, [aa, aa2], pt)

    # Display models
    display_electre_tri_models([model], [worst], [best])
