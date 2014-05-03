from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../../")
from pymcda.types import CriterionValue, CriteriaValues
from itertools import combinations

verbose = False

class LpMRSortMobius():

    def __init__(self, model, pt, aa_ori, delta = 0.0001):
        self.model = model
        self.pt = pt
        self.aa_ori = aa_ori
        self.delta = delta

        self.categories = model.categories
        self.cat_index = {c: i for i, c in enumerate(self.categories)}
        self.profiles = model.categories_profiles.get_ordered_profiles()

        cids = self.model.criteria.keys()
        self.mindices = [c for c in cids] + \
                        [c for c in combinations(cids, 2)]

        self.update_linear_program()

    def update_linear_program(self):
        self.compute_constraints()

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

    def criteria_in_favor(self, ap1, ap2):
        criteria_list = []

        for c in self.model.criteria:
            diff = ap2.performances[c.id] - ap1.performances[c.id]
            diff *= c.direction
            if diff <= 0:
                criteria_list.append(c.id)

        return criteria_list

    def alternative_constraint(self, ap, bp):
        criteria_combi = self.criteria_in_favor(ap, bp)
        criteria_combi += [c for c in combinations(criteria_combi, 2)]

        return [1 if m in criteria_combi else 0 for m in self.mindices]

    def compute_constraints(self):
        self.lower_constraint = {}
        self.upper_constraint = {}

        for aa in self.aa_ori:
            aid = aa.id
            ap = self.pt[aid]
            index = self.cat_index[aa.category_id]
            upper_profile, lower_profile = None, None

            if index < len(self.cat_index) - 1:
                upper_profile = self.profiles[index]
                bp = self.model.bpt[upper_profile]
                v = self.alternative_constraint(ap, bp)
                self.upper_constraint[aid] = v

            if index > 0:
                lower_profile = self.profiles[index - 1]
                bp = self.model.bpt[lower_profile]
                v = self.alternative_constraint(ap, bp)
                self.lower_constraint[aid] = v

    def add_variables_cplex(self):
        mindices = self.mindices
        self.lp.variables.add(names=['m_%d' % i
                                     for i in range(len(mindices))],
                              lb = [-1 for i in mindices],
                              ub = [1 for i in mindices])
        self.lp.variables.add(names=['x' + i
                                     for i in self.lower_constraint],
                              lb = [0 for i in self.lower_constraint],
                              ub = [1 for i in self.lower_constraint])
        self.lp.variables.add(names=['xp' + i
                                     for i in self.lower_constraint],
                              lb = [0 for i in self.lower_constraint],
                              ub = [1 for i in self.lower_constraint])
        self.lp.variables.add(names=['y' + i
                                     for i in self.upper_constraint],
                              lb = [0 for i in self.upper_constraint],
                              ub = [1 for i in self.upper_constraint])
        self.lp.variables.add(names=['yp' + i
                                     for i in self.upper_constraint],
                              lb = [0 for i in self.upper_constraint],
                              ub = [1 for i in self.upper_constraint])
        self.lp.variables.add(names=['lambda'], lb = [0.5], ub = [1])

    def add_constraints_cplex(self):
        constraints = self.lp.linear_constraints
        m = ['m_%d' % i for i in range(len(self.mindices))]

        for lc, v in self.lower_constraint.items():
            # sum(m_j(a_i,b_h-1) - x_i + x'_i = lbda
            constraints.add(names = ['lc' + lc],
                            lin_expr =
                                [
                                 [m + ['x' + lc, 'xp' + lc, 'lambda'],
                                  v + [-1.0, 1.0, -1.0]],
                                ],
                            senses = ["E"],
                            rhs = [0],
                           )

        for uc, v in self.upper_constraint.items():
            # sum(m_j(a_i,b_h) + y_i - y'_i = lbda - delta
            constraints.add(names = ['uc' + uc],
                            lin_expr =
                                [
                                 [m + ['y' + uc, 'yp' + uc, 'lambda'],
                                  v + [1.0, -1.0, -1.0]],
                                ],
                            senses = ["E"],
                            rhs = [-self.delta],
                           )

        # sum m_j = 1
        constraints.add(names = ['msum'],
                        lin_expr = [[m, [1.0] * len(m)]],
                        senses = ["E"],
                        rhs = [1]
                       )

        # capa monotonicity
        mindices_map = dict(zip(self.mindices, m))
        for c in self.model.criteria.keys():
            constraints.add(names = ["u_%s" % c],
                            lin_expr = [[[mindices_map[c]], [1]]],
                            senses = ["G"],
                            rhs = [0],
                           )

        for c in combinations(self.model.criteria.keys(), 2):
            mc = mindices_map[c]
            m0 = mindices_map[c[0]]
            m1 = mindices_map[c[1]]

            constraints.add(names = ["u_%s%s_%s" % (c[0], c[1], c[0])],
                            lin_expr =
                                [
                                 [[mc, m0], [1, -1]],
                                ],
                            senses = ["G"],
                            rhs = [0],
                           )

            constraints.add(names = ["u_%s%s_%s" % (c[0], c[1], c[1])],
                            lin_expr =
                                [
                                 [[mc, m1], [1, -1]],
                                ],
                            senses = ["G"],
                            rhs = [0],
                           )

    def add_objective_cplex(self):
        self.lp.objective.set_sense(self.lp.objective.sense.minimize)
        for lc in self.lower_constraint:
            self.lp.objective.set_linear('xp' + lc, 1)

        for uc in self.upper_constraint:
            self.lp.objective.set_linear('yp' + uc, 1)

    def solve_cplex(self):
        self.lp.solve()
        obj = self.lp.solution.get_objective_value()

        cvs = CriteriaValues()
        m = ['m_%d' % i for i in range(len(self.mindices))]
        mindices_map = dict(zip(self.mindices, m))
        for m, vname in mindices_map.items():
            cv = CriterionValue()
            cv.id = m
            cv.value = self.lp.solution.get_values(vname)
            cvs.append(cv)

        self.model.cvs = cvs
        self.model.lbda = self.lp.solution.get_values("lambda")

        return obj

    def solve(self):
        return self.solve_function()
