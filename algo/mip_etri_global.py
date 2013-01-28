from __future__ import division
import os, sys
from itertools import product
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
from mcda.types import criterion_value, criteria_values
from mcda.types import alternative_performances, performance_table

try:
    solver = os.environ['SOLVER']
except:
    solver = 'cplex'

if solver == 'cplex':
    import cplex
else:
    raise NameError('Invalid solver selected')

class mip_etri_global():

    def __init__(self, pt, aa, model, epsilon = 0.0001):
        self.pt = pt
        self.aa = aa
        self.model = model
        self.criteria = model.criteria
        self.cps = model.categories_profiles

        self.epsilon = epsilon

        self.__profiles = self.cps.get_ordered_profiles()
        self.__categories = self.cps.get_ordered_categories()

        self.lp = cplex.Cplex()
        self.add_variables()
        self.add_constraints()
        self.add_objective()

    def add_variables(self):
        self.ap_min = self.pt.get_min()
        self.ap_max = self.pt.get_max()
        self.ap_range = self.pt.get_range()
        for c in self.criteria:
            self.ap_min.performances[c.id] -= self.epsilon
            self.ap_max.performances[c.id] += self.epsilon
            self.ap_range.performances[c.id] *= 2

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
                              ub = [self.ap_max.performances[c.id]
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

    def __add_alternative_lower_constraints(self, aa):
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

            # dinf_(i,j) > a_{i,j} - b_{h-1,j}
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

            # dinf_(i,j) <= a_{i,j} - b_{h-1,j} + 1
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

    def __add_alternative_upper_constraints(self, aa):
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

            # dinf_(i,j) > a_{i,j} - b_{h,j}
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

            # dinf_(i,j) <= a_{i,j} - b_{h,j} + 1
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
        constraints = self.lp.linear_constraints

        profiles = self.cps.get_ordered_profiles()

        lower_cat = self.__categories[0]
        upper_cat = self.__categories[-1]

        for aa in self.aa:
            cat = aa.category_id

            if cat != lower_cat:
                self.__add_alternative_lower_constraints(aa)

            if cat != upper_cat:
                self.__add_alternative_upper_constraints(aa)

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
                             [["w_%s" % c.id for c in self.criteria],
                              [1 for c in self.criteria]],
                            ],
                        senses = ["E"],
                        rhs = [1]
                        )

    def add_constraints(self):
        constraints = self.lp.linear_constraints

        self.add_alternatives_constraints()

    def add_objective(self):
        self.lp.objective.set_sense(self.lp.objective.sense.maximize)
        self.lp.objective.set_linear([("a_%s" % aid, 1)
                                      for aid in self.aa.keys()])

    def solve(self):
        self.lp.solve()

        obj = self.lp.solution.get_objective_value()

        cvs = criteria_values()
        for c in self.criteria:
            cv = criterion_value()
            cv.id = c.id
            cv.value = self.lp.solution.get_values('w_' + c.id)
            cvs.append(cv)

        self.model.cv = cvs

        self.model.lbda = self.lp.solution.get_values("lambda")

        pt = performance_table()
        for p in self.__profiles:
            ap = alternative_performances(p)
            for c in self.criteria:
                perf = self.lp.solution.get_values("g_%s_%s" % (p, c.id))
                ap.performances[c.id] = round(perf, 5)
            pt.append(ap)

        self.model.bpt = pt
        pt.display()
        print "obj", obj

        return obj

if __name__ == "__main__":
    from mcda.generate import generate_random_electre_tri_bm_model
    from mcda.generate import generate_alternatives
    from mcda.generate import generate_criteria
    from mcda.generate import generate_random_performance_table
    from mcda.utils import compute_ca
    from mcda.utils import display_assignments_and_pt
    from ui.graphic import display_electre_tri_models

    seed = 123
    ncrit = 5
    ncat = 3

    # Generate a random ELECTRE TRI BM model
    criteria = generate_criteria(ncrit)
    worst = alternative_performances("worst",
                                     {c.id: 0 for c in criteria})
    best = alternative_performances("best",
                                    {c.id: 10 for c in criteria})
    model = generate_random_electre_tri_bm_model(ncrit, ncat, seed,
                                                 worst = worst, best = best)

    # Display model parameters
    print('Original model')
    print('==============')
    cids = model.criteria.keys()
    model.bpt.display(criterion_ids = cids)
    model.cv.display(criterion_ids = cids)
    print("lambda: %.7s" % model.lbda)

    # Generate a set of alternatives
    a = generate_alternatives(100)
    pt = generate_random_performance_table(a, model.criteria,
                                           worst = worst, best = best)
    aa = model.pessimist(pt)

    # Run the MIP
    model2 = model.copy()
    model2.cv = None
    model2.bpt = None
    model2.lbda = None

    mip = mip_etri_global(pt, aa, model2)
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
