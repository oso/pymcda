from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../../")
from pymcda.types import CriterionValue, CriteriaValues

verbose = False

class MipMRSortWeights():

    def __init__(self, model, pt, aa, epsilon = 0.0001):
        self.pt = pt
        self.aa = aa
        self.model = model
        self.criteria = model.criteria.get_active()
        self.epsilon = epsilon

        self.profiles = model.categories_profiles.get_ordered_profiles()
        self.categories = model.categories_profiles.get_ordered_categories()
        self.cat_ranks = {c: i for i, c in enumerate(self.categories)}

        self.pt.update_direction(model.criteria)

        solver = os.getenv('SOLVER', 'cplex')
        if solver == 'cplex':
            import cplex
            self.lp = cplex.Cplex()
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

    def add_variables_cplex(self):
        a1 = self.aa.get_alternatives_in_categories(self.categories[1:])
        a2 = self.aa.get_alternatives_in_categories(self.categories[:-1])

        self.lp.variables.add(names = ["w_" + c.id for c in self.criteria],
                              lb = [0 for c in self.criteria],
                              ub = [1 for c in self.criteria])
        self.lp.variables.add(names = ["lambda"], lb = [0], ub = [1])
        self.lp.variables.add(names = ["x_%s" % a for a in a1],
                              lb = [0 for a in a1],
                              ub = [1 for a in a1])
        self.lp.variables.add(names = ["y_%s" % a for a in a2],
                              lb = [0 for a in a2],
                              ub = [1 for a in a2])
        self.lp.variables.add(names = ["gamma_%s" % a.id for a in self.aa],
                              types = [self.lp.variables.type.binary
                                       for a in self.aa])

    def get_winning_coalition(self, ap, bp):
        aperfs = ap.performances
        bperfs = bp.performances
        return {c.id: 1 if aperfs[c.id] >= bperfs[c.id] else 0
                for c in self.criteria}

    def add_constraints_cplex(self):
        constraints = self.lp.linear_constraints
        rankmax = len(self.cat_ranks)
        for a in self.aa:
            rank = self.cat_ranks[a.category_id]
            lp = self.profiles[rank - 1] if rank > 0 else None
            up = self.profiles[rank] if rank < (rankmax - 1) else None
            if lp is not None:
                coalitions = self.get_winning_coalition(self.pt[a.id],
                                                        self.model.bpt[lp])
                keys = ["w_%s" % coa for coa in coalitions.keys()]
                values = list(coalitions.values())
                constraints.add(names = ["cx_%s" % a.id],
                                lin_expr =
                                    [
                                     [keys + ["x_%s" % a.id] + ["lambda"],
                                      values + [1, -1]],
                                    ],
                                senses = ["G"],
                                rhs = [0]
                               )

                constraints.add(names = ["cxgamma_%s" % a.id],
                                lin_expr =
                                    [
                                     [["x_%s" % a.id] + ["gamma_%s" % a.id],
                                      [1, 1]]
                                    ],
                                senses = ["L"],
                                rhs = [1]
                               )

            if up is not None:
                coalitions = self.get_winning_coalition(self.pt[a.id],
                                                        self.model.bpt[up])
                keys = ["w_%s" % coa for coa in coalitions.keys()]
                values = list(coalitions.values())
                constraints.add(names = ["cy_%s" % a.id],
                                lin_expr =
                                    [
                                     [keys + ["y_%s" % a.id] + ["lambda"],
                                      values + [-1, -1]],
                                    ],
                                senses = ["L"],
                                rhs = [-self.epsilon]
                               )

                constraints.add(names = ["cygamma_%s" % a.id],
                                lin_expr =
                                    [
                                     [["y_%s" % a.id] + ["gamma_%s" % a.id],
                                      [1, 1]]
                                    ],
                                senses = ["L"],
                                rhs = [1]
                               )

        constraints.add(names = ["wsum"],
                 lin_expr =
                     [
                      [["w_%s" % c.id for c in self.criteria],
                       [1 for c in self.criteria]],
                     ],
                 senses = ["E"],
                 rhs = [1]
                 )

    def add_objective_cplex(self):
        self.lp.objective.set_sense(self.lp.objective.sense.maximize)
        self.lp.objective.set_linear([("gamma_%s" % aid, 1)
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
            cv.value = self.lp.solution.get_values('w_' + c.id)
            cvs.append(cv)

        self.model.cv = cvs

        self.model.lbda = self.lp.solution.get_values("lambda")

        return obj

    def solve(self):
        return self.solve_function()

if __name__ == "__main__":
    from pymcda.generate import generate_random_mrsort_model
    from pymcda.generate import generate_alternatives
    from pymcda.generate import generate_random_performance_table
    from pymcda.utils import print_pt_and_assignments
    from pymcda.ui.graphic import display_electre_tri_models

    seed = 12
    ncrit = 8
    ncat = 3

    # Generate a random ELECTRE TRI BM model
    model = generate_random_mrsort_model(ncrit, ncat, seed)

    # Display model parameters
    print('Original model')
    print('==============')
    cids = model.criteria.keys()
    cids.sort()
    print(model.bpt)
    print(model.cv)
    print("lambda: %.7s" % model.lbda)

    # Generate a set of alternatives
    a = generate_alternatives(1000)
    pt = generate_random_performance_table(a, model.criteria)

    worst = pt.get_worst(model.criteria)
    best = pt.get_best(model.criteria)

    # Assign the alternatives
    aa = model.pessimist(pt)

    # Run the MIP
    model2 = model.copy()
    model2.cv = None
    model2.bpt = model.bpt
    model2.lbda = None

    mip = MipMRSortWeights(model2, pt, aa)
    mip.solve()

    # Display learned model parameters
    print('Learned model')
    print('=============')
    print(model2.bpt)
    print(model2.cv)
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
        print_pt_and_assignments(anok.keys(), model.criteria.keys(),
                                 [aa, aa2], pt)

#    # Display models
#    display_electre_tri_models([model, model2],
#                               [worst, worst], [best, best])
