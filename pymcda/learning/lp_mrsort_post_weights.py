from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../../")
from itertools import product
from pymcda.types import CriterionValue, CriteriaValues
from pymcda.utils import powerset

verbose = False

def compute_sufficient_and_insufficient_coalitions(cvs, lbda):
    sufficient = set()
    insufficient = set()

    c = cvs.keys()
    for coa in powerset(c):
        l = cvs.get_subset(coa)
        if sum([cv.value for cv in l]) >= lbda:
            sufficient.add(frozenset(coa))
        else:
            insufficient.add(frozenset(coa))

    return sufficient, insufficient

def compute_fmins(coalitions):
    fmins = coalitions
    for fmin, fmin2 in product(fmins, fmins):
        if fmin == fmin2:
            continue
        elif fmin2.issuperset(fmin):
            fmins.discard(fmin2)

    return fmins

def compute_gmaxs(coalitions):
    gmaxs = coalitions
    for gmax, gmax2 in product(gmaxs, gmaxs):
        if gmax == gmax2:
            continue
        elif gmax2.issubset(gmax):
            gmaxs.discard(gmax2)

    return gmaxs

class LpMRSortPostWeights(object):

    def __init__(self, cvs, lbda, epsilon = 0.00001):
        self.cvs = cvs
        self.lbda = lbda
        self.epsilon = epsilon

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

    def __compute_fmins(self):
        fmins = self.__sufficient
        for fmin, fmin2 in product(fmins, fmins):
            if fmin == fmin2:
                continue
            elif fmin2.issuperset(fmin):
                fmins.discard(fmin2)

    def __compute_gmaxs(self):
        gmaxs = self.__insufficient
        for gmax, gmax2 in product(gmaxs, gmaxs):
            if gmax == gmax2:
                continue
            elif gmax2.issubset(gmax):
                gmaxs.discard(gmax2)

    def __add_variables_cplex(self):
        self.lp.variables.add(names=["w_%s" % c.id for c in self.cvs],
                              lb=[0 for c in self.cvs],
                              ub=[1 for c in self.cvs])
        self.lp.variables.add(names=["wm_%s" % c.id for c in self.cvs],
                              lb=[0 for c in self.cvs],
                              ub=[1 for c in self.cvs])
        self.lp.variables.add(names=["wp_%s" % c.id for c in self.cvs],
                              lb=[0 for c in self.cvs],
                              ub=[1 for c in self.cvs])
        self.lp.variables.add(names=['lambda'],
                              lb = [0], ub = [1]) #len(self.cvs)])

    def __add_constraints_cplex(self):
        constraints = self.lp.linear_constraints

        for cv in self.cvs:
            # wi = wi+ - wi- + 1/n
            constraints.add(names = ["c_w_%s" % cv.id],
                            lin_expr =
                                [
                                 [["w_%s" % cv.id, "wm_%s" % cv.id,
                                   "wp_%s" % cv.id],
                                  [1, 1, -1]],
                                ],
                            senses = ["E"],
                            rhs = [1 / len(self.cvs)],
                           )

        # sum(wi) = 1
        constraints.add(names = ["wsum"],
                        lin_expr =
                            [
                             [["w_%s" % cv.id for cv in self.cvs],
                              [1.0] * len(self.cvs)],
                            ],
                        senses = ["E"],
                        rhs = [1],
                       )

        # fmins
        for fmin in self.__fmins:
            wvars = ["w_%s" % cv.id for cv in self.cvs.get_subset(fmin)]
            constraints.add(names = ["fmin_%s" % fmin],
                            lin_expr =
                                [
                                 [wvars + ["lambda"],
                                  [1] * len(wvars) + [-1]],
                                ],
                            senses = ["G"],
                            rhs = [self.epsilon],
                           )

        # gmaxs
        for gmax in self.__gmaxs:
            wvars = ["w_%s" % cv.id for cv in self.cvs.get_subset(gmax)]
            constraints.add(names = ["gmax_%s" % gmax],
                            lin_expr =
                                [
                                 [wvars + ["lambda"],
                                  [1] * len(wvars) + [-1]],
                                ],
                            senses = ["L"],
                            rhs = [-self.epsilon],
                           )

    def __add_objective_cplex(self):
        self.lp.objective.set_sense(self.lp.objective.sense.minimize)
        for cv in cvs:
            self.lp.objective.set_linear("wp_%s" % cv.id, 1)
            self.lp.objective.set_linear("wm_%s" % cv.id, 1)

    def solve_cplex(self):
        self.__add_variables_cplex()
        self.__add_constraints_cplex()
        self.__add_objective_cplex()

        self.lp.solve()

        status = self.lp.solution.get_status()
        if status != self.lp.solution.status.optimal:
            raise RuntimeError("Solver status: %s" % status)

        obj = self.lp.solution.get_objective_value()

        cvs2 = CriteriaValues()
        for cv in self.cvs:
            cv2 = CriterionValue(cv.id)
            cv2.value = self.lp.solution.get_values("w_%s" % cv.id)
            cvs2.append(cv2)

        lbda2 = self.lp.solution.get_values("lambda")

        return obj, cvs2, lbda2

    def solve(self):
        self.__fmins, self.__gmaxs = \
            compute_sufficient_and_insufficient_coalitions(self.cvs,
                                                           self.lbda)
#        self.__fmins = compute_fmins(self.__fmins)
#        self.__gmaxs = compute_gmaxs(self.__gmaxs)

        if self.solver == 'cplex':
            return self.solve_cplex()

if __name__ == "__main__":
    import random
    from pymcda.generate import generate_random_criteria_weights
    from pymcda.generate import generate_criteria

    random.seed(1)

    c = generate_criteria(14)
    cvs = generate_random_criteria_weights(c)
    lbda = round(random.uniform(0.5, 1), 3)

    suf, insuf = compute_sufficient_and_insufficient_coalitions(cvs, lbda)

    print(c)
    print(cvs)
    print("lbda: %f" % lbda)

    lp = LpMRSortPostWeights(cvs, lbda)
    obj, cvs2, lbda2 = lp.solve()

    print("objective: %f" % obj)
    print(cvs2)
    print("lbda2: %f" % lbda2)

    suf2, insuf2 = compute_sufficient_and_insufficient_coalitions(cvs2, lbda2)

    for coa in suf ^ suf2:
        print(coa)
