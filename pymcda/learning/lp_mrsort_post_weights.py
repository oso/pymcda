from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../../")
from itertools import product
from pymcda.types import CriterionValue, CriteriaValues
from pymcda.utils import powerset
from pymcda.utils import compute_winning_and_loosing_coalitions
from pymcda.utils import compute_minimal_winning_coalitions
from pymcda.utils import compute_maximal_loosing_coalitions

verbose = False

class LpMRSortPostWeights(object):

    def __init__(self, cvs, lbda, wsum = 100):
        self.cvs = cvs
        self.lbda = lbda
        self.epsilon = 1
        self.wsum = wsum

        self.solver = os.getenv('SOLVER', 'cplex')
        if self.solver == 'cplex':
            import cplex
            solver_max_threads = int(os.getenv('SOLVER_MAX_THREADS', 0))
            self.lp = cplex.Cplex()
            self.lp.parameters.threads.set(solver_max_threads)
            if verbose is False:
                self.lp.set_log_stream(None)
                self.lp.set_results_stream(None)
        else:
            raise NameError('Invalid solver selected')

    def __add_variables_cplex(self):
        self.lp.variables.add(names=["w_%s" % c.id for c in self.cvs],
                              lb=[0 for c in self.cvs],
                              ub=[int(self.wsum / 2 + 1) for c in self.cvs],
                              types=[self.lp.variables.type.integer
                                     for c in self.cvs])
        self.lp.variables.add(names=["x_%s" % fmin for fmin in self.fmins],
                              lb=[0 for fmin in self.fmins])
        self.lp.variables.add(names=["y_%s" % gmax for gmax in self.gmaxs],
                              lb=[0 for gmax in self.gmaxs])
        self.lp.variables.add(names=["alpha"], lb=[0])
        self.lp.variables.add(names=['lambda'],
                              lb = [0], ub = [self.wsum],
                              types=[self.lp.variables.type.integer])

    def __add_constraints_cplex(self):
        constraints = self.lp.linear_constraints

        # sum(wi) = 1
        constraints.add(names = ["wsum"],
                        lin_expr =
                            [
                             [["w_%s" % cv.id for cv in self.cvs],
                              [1] * len(self.cvs)],
                            ],
                        senses = ["E"],
                        rhs = [self.wsum],
                       )

        # fmins
        for fmin in self.fmins:
            wvars = ["w_%s" % cv.id for cv in self.cvs.get_subset(fmin)]
            constraints.add(names = ["fmin_%s" % fmin],
                            lin_expr =
                                [
                                 [wvars + ["lambda"] + ["x_%s" % fmin],
                                  [1] * len(wvars) + [-1] + [-1]],
                                ],
                            senses = ["G"],
                            rhs = [0],
                           )

        # gmaxs
        for gmax in self.gmaxs:
            wvars = ["w_%s" % cv.id for cv in self.cvs.get_subset(gmax)]
            constraints.add(names = ["gmax_%s" % gmax],
                            lin_expr =
                                [
                                 [wvars + ["lambda"] + ["y_%s" % gmax],
                                  [1] * len(wvars) + [-1] + [1]],
                                ],
                            senses = ["L"],
                            rhs = [-self.epsilon],
                           )

        # alpha
        for fmin in self.fmins:
            constraints.add(names = ["alpha_%s" % fmin],
                            lin_expr =
                                [
                                 [["alpha"] + ["x_%s" % fmin],
                                  [1, -1]],
                                ],
                            senses = ["L"],
                            rhs = [0],
                           )

        for gmax in self.gmaxs:
            constraints.add(names = ["alpha_%s" % fmin],
                            lin_expr =
                                [
                                 [["alpha"] + ["y_%s" % gmax],
                                  [1, -1]],
                                ],
                            senses = ["L"],
                            rhs = [0],
                           )

    def __add_objective_cplex(self):
        self.lp.objective.set_sense(self.lp.objective.sense.maximize)
        self.lp.objective.set_linear("alpha", 1)

    def solve_cplex(self):
        self.__add_variables_cplex()
        self.__add_constraints_cplex()
        self.__add_objective_cplex()

        self.lp.solve()

        status = self.lp.solution.get_status()
        if status != self.lp.solution.status.MIP_optimal:
            raise RuntimeError("Solver status: %s" % status)

        obj = self.lp.solution.get_objective_value()

        cvs2 = CriteriaValues()
        for cv in self.cvs:
            cv2 = CriterionValue(cv.id)
            cv2.value = int(self.lp.solution.get_values("w_%s" % cv.id))
            cvs2.append(cv2)

        lbda2 = int(self.lp.solution.get_values("lambda"))

        return obj, cvs2, lbda2

    def solve(self):
        self.fmins, self.gmaxs = \
            compute_winning_and_loosing_coalitions(self.cvs,
                                                   self.lbda)
#        self.fmins = compute_minimal_winning_coalitions(self.fmins)
#        self.gmaxs = compute_maximal_loosing_coalitions(self.gmaxs)

        if self.solver == 'cplex':
            obj, cvs2, lbda2 = self.solve_cplex()

        self.fmins2, self.gmaxs2 = \
            compute_winning_and_loosing_coalitions(cvs2,
                                                   lbda2)

        if self.fmins2 != self.fmins:
            raise RuntimeError("fmins")
        if self.gmaxs2 != self.gmaxs:
            raise RuntimeError("gmaxs")

        return obj, cvs2, lbda2

if __name__ == "__main__":
    import random
    from pymcda.generate import generate_random_criteria_weights
    from pymcda.generate import generate_criteria

    random.seed(3)

    c = generate_criteria(3)
    cvs = generate_random_criteria_weights(c)
#    lbda = round(random.uniform(0.5, 1), 3)
    lbda = 0.5

    suf, insuf = compute_winning_and_loosing_coalitions(cvs, lbda)

    print(c)
    print(cvs)
    print("lbda: %f" % lbda)

    lp = LpMRSortPostWeights(cvs, lbda, 100)
    obj, cvs2, lbda2 = lp.solve()

    print("objective: %f" % obj)
    print(cvs2)
    print("lbda2: %f" % lbda2)

    suf2, insuf2 = compute_winning_and_loosing_coalitions(cvs2, lbda2)

    for coa in suf ^ suf2:
        print(coa)
