from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../../")
import bisect
from pymcda.types import Point, Segment, PiecewiseLinear
from pymcda.types import CategoryValue, CategoriesValues
from pymcda.types import CriteriaFunctions, CriterionFunction
from pymcda.types import CriteriaValues, CriterionValue
from pymcda.types import CategoriesValues, CategoriesValues, Interval
from pymcda.generate import generate_random_criteria_values
from pymcda.generate import generate_random_criteria_functions

verbose = False

class LpAVFSort(object):

    def __init__(self, c, cs, cat, gi_worst, gi_best):
        self.criteria = c
        self.cs = cs
        self.cat = { cat: i+1 \
                     for i, cat in enumerate(cat.get_ordered_categories()) }
        self.gi_worst = gi_worst
        self.gi_best = gi_best
        self.__compute_abscissa()

        solver = os.getenv('SOLVER', 'cplex')
        if solver == 'cplex':
            import cplex
            solver_max_threads = int(os.getenv('SOLVER_MAX_THREADS', 0))
            self.lp = cplex.Cplex()
            self.lp.parameters.threads.set(solver_max_threads)
            self.encode_constraints = self.encode_constraints_cplex
            self.add_objective = self.add_objective_cplex
            self.solve_function = self.solve_cplex
            if verbose is False:
                self.lp.set_log_stream(None)
                self.lp.set_results_stream(None)
        elif solver == 'glpk':
            import pymprog
            self.lp = pymprog.model('lp_avfsort')
            self.lp.verb = verbose
            self.encode_constraints = self.encode_constraints_glpk
            self.add_objective = self.add_objective_glpk
            self.solve_function = self.solve_glpk
        else:
            raise NameError('Invalid solver selected')

    def __compute_abscissa(self):
        self.points = {}
        for cs in self.cs:
            best = self.gi_best.performances[cs.id]
            worst = self.gi_worst.performances[cs.id]
            diff = best - worst

            self.points[cs.id] = [ worst ]
            for i in range(1, cs.value):
                self.points[cs.id].append(worst + i / cs.value * diff)
            self.points[cs.id].append(best)

    def __get_left_points(self, cid, x):
        left = bisect.bisect_right(sorted(self.points[cid]), x) - 1
        if self.criteria[cid].direction == -1:
            left = len(self.points[cid]) - 2 - left

        if left == len(self.points[cid]) - 1:
            left -= 1
        elif left == -1:
            left += 1

        return left

    def add_variables_cplex(self, aids):
        self.lp.variables.add(names = ['x_' + aid for aid in aids],
                              lb = [0 for aid in aids],
                              ub = [1 for aid in aids])
        self.lp.variables.add(names = ['y_' + aid for aid in aids],
                              lb = [0 for aid in aids],
                              ub = [1 for aid in aids])
        self.lp.variables.add(names = ['xp_' + aid for aid in aids],
                              lb = [0 for aid in aids],
                              ub = [1 for aid in aids])
        self.lp.variables.add(names = ['yp_' + aid for aid in aids],
                              lb = [0 for aid in aids],
                              ub = [1 for aid in aids])

        for cs in self.cs:
            cid = cs.id
            nseg = cs.value
            self.lp.variables.add(names = ['w_' + cid + "_%d" % (i+1)
                                           for i in range(nseg)],
                                  lb = [0 for i in range(nseg)],
                                  ub = [1 for i in range(nseg)])


        ncat = len(self.cat)
        self.lp.variables.add(names = ["u_%d" % i for i in range(1, ncat)],
                              lb = [0 for i in range(ncat-1)],
                              ub = [1 for i in range(ncat-1)])

    def compute_constraint(self, aa, ap):
        d_coefs = {}
        for cs in self.cs:
            perf = ap.performances[cs.id]
            left = self.__get_left_points(cs.id, perf)

            if self.criteria[cs.id].direction == 1:
                d = self.points[cs.id][left + 1] - self.points[cs.id][left]
                k = (perf - self.points[cs.id][left]) / d
            else:
                d = self.points[cs.id][left] - self.points[cs.id][left + 1]
                k = (self.points[cs.id][left] - perf) / d

            if k > 1 or k < 0:
                raise

            w_coefs = [1] * left + [k] + [0] * (cs.value - left - 1)

            d_coefs[cs.id] = w_coefs

        return d_coefs

    def encode_constraint_cplex(self, aa, ap):
        constraints = self.lp.linear_constraints
        d_coefs = self.compute_constraint(aa, ap)

        cat_nr = self.cat[aa.category_id]

        l_vars = ['w_' + cid + '_%d' % j for cid in d_coefs.keys()
                  for j in range(1, self.cs[cid].value + 1)]
        l_coefs = [j for i in d_coefs.values() for j in i]

        if cat_nr < len(self.cat):
            constraints.add(names = ['csup' + aa.id],
                            lin_expr =
                                [[
                                 l_vars +
                                  ["u_%d" % cat_nr,
                                   'x_' + aa.id,
                                   'xp_' + aa.id],
                                 l_coefs + [-1.0, 1.0, -1.0],
                                ]],
                            senses = ["E"],
                            rhs = [-0.00001],
                           )

        if cat_nr > 1:
            constraints.add(names = ['cinf' + aa.id],
                            lin_expr =
                                [[
                                 l_vars +
                                  ["u_%d" % (cat_nr - 1),
                                   'y_' + aa.id,
                                   'yp_' + aa.id],
                                 l_coefs + [-1.0, -1.0, 1.0],
                                ]],
                            senses = ["E"],
                            rhs = [0.00001],
                           )

    def encode_constraints_cplex(self, aas, pt):
        self.add_variables_cplex(aas.keys())

        # sum ((sum w_it) + k * w_it+1) - u_k + x_j - x'_j <= -d1
        # sum ((sum w_it) + k * w_it+1) - u_k - y_j + y'_j >= d2
        for aa in aas:
            self.encode_constraint_cplex(aa, pt[aa.id])

        # sum (sum w_it) = 1
        constraints = self.lp.linear_constraints
        w = []
        for cs in self.cs:
            w += ['w_' + cs.id + "_%d" % (i + 1) for i in range(cs.value)]

        constraints.add(names = ['csum'],
                        lin_expr = [[w, [1] * len(w)]],
                        senses = ["E"],
                        rhs = [1],
                       )

        # u_k - u_k-1 >= s
        ncat = len(self.cat)
        for i in range(2, ncat):
            constraints.add(names = ["umin_%d_%d" % (i, i-1)],
                            lin_expr = [[
                                         ["u_%d" % i, "u_%d" % (i-1)],
                                         [1, -1],
                                       ]],
                            senses = ["G"],
                            rhs = [0.00001],
                           )

    def add_objective_cplex(self, aa):
        self.lp.objective.set_sense(self.lp.objective.sense.minimize)
        for aa in aa.keys():
            self.lp.objective.set_linear('xp_' + aa, 1)
            self.lp.objective.set_linear('yp_' + aa, 1)

    def add_variables_glpk(self, aids):
        self.x = self.lp.var(xrange(len(aids)), 'x', bounds=(0, 1))
        self.y = self.lp.var(xrange(len(aids)), 'y', bounds=(0, 1))
        self.xp = self.lp.var(xrange(len(aids)), 'xp', bounds=(0, 1))
        self.yp = self.lp.var(xrange(len(aids)), 'yp', bounds=(0, 1))

        self.w = {}
        for cs in self.cs:
            cid = cs.id
            self.w[cs.id] = self.lp.var(xrange(cs.value), 'w_' + cid,
                                        bounds=(0, 1))
            w_vars = ['w_' + cs.id + "_%d" % i
                      for i in range(1, cs.value+1)]

        ncat = len(self.cat)
        self.u = self.lp.var(xrange(len(self.cat) - 1), 'u', bounds=(0, 1))

    def encode_constraints_glpk(self, aas, pt):
        self.add_variables_glpk(aas)

        # sum ((sum w_it) + k * w_it+1) - u_k + x_j <= -d1
        # sum ((sum w_it) + k * w_it+1) - u_k - y_j >= d2
        for i, aa in enumerate(aas):
            d_coefs = self.compute_constraint(aa, pt[aa.id])

            cat_nr = self.cat[aa.category_id]

            if cat_nr < len(self.cat):
                self.lp.st(sum(d_coefs[cs.id][j] * self.w[cs.id][j] \
                           for cs in self.cs for j in range(cs.value)) \
                           + self.x[i] - self.xp[i] - self.u[cat_nr - 1] \
                           == -0.00001)

            if cat_nr > 1:
                self.lp.st(sum(d_coefs[cs.id][j] * self.w[cs.id][j] \
                           for cs in self.cs for j in range(cs.value)) \
                           - self.y[i] + self.yp[i] - self.u[cat_nr - 2] \
                           == 0.00001)

        # sum (sum w_it) = 1
        self.lp.st(sum(self.w[cs.id][i] for cs in self.cs \
                   for i in range(cs.value)) == 1)

        # u_k - u_k-1 >= s
        ncat = len(self.cat)
        for i in range(1, ncat - 1):
            self.lp.st(self.u[i] - self.u[i - 1] >= 0.00001)

    def add_objective_glpk(self, aa):
        self.lp.min(sum(self.xp[i] for i in range(len(self.xp)))
                    + sum(self.yp[i] for i in range(len(self.yp))))

    def solve_glpk(self, aa, pt):
        self.lp.solve()

        status = self.lp.status()
        if status != 'opt':
            raise RuntimeError("Solver status: %s" % self.lp.status())

        obj = self.lp.vobj()

        cfs = CriteriaFunctions()
        cvs = CriteriaValues()
        for cs in self.cs:
            cv = CriterionValue(cs.id, 1)
            cvs.append(cv)

            nseg = cs.value
            x_points = range(nseg)

            p1 = Point(self.points[cs.id][0], 0)

            ui = 0
            f = PiecewiseLinear([])
            for i in x_points:
                uivar = 'w_' + cs.id + "_%d" % (i + 1)
                ui += self.w[cs.id][i].primal

                x = self.points[cs.id][i + 1]

                p2 = Point(x, ui)

                s = Segment("s%d" % (i + 1), p1, p2)
                f.append(s)

                p1 = p2

            s.p1_in = True
            s.p2_in = True
            cf = CriterionFunction(cs.id, f)
            cfs.append(cf)

        cat = {v: k for k, v in self.cat.items()}
        catv = CategoriesValues()
        ui_a = 0
        for i in range(0, len(cat) - 1):
            ui_b = self.u[i].primal
            catv.append(CategoryValue(cat[i + 1], Interval(ui_a, ui_b)))
            ui_a = ui_b

        catv.append(CategoryValue(cat[i + 2], Interval(ui_a, 1)))

        return obj, cvs, cfs, catv

    def solve_cplex(self, aa, pt):
        self.lp.solve()

        status = self.lp.solution.get_status()
        if status == self.lp.solution.status.infeasible:
            raise RuntimeError("Solver status: %s" % status)

        obj = self.lp.solution.get_objective_value()

        cfs = CriteriaFunctions()
        cvs = CriteriaValues()
        for cs in self.cs:
            cv = CriterionValue(cs.id, 1)
            cvs.append(cv)

            nseg = cs.value
            x_points = range(nseg)

            p1 = Point(self.points[cs.id][0], 0)

            ui = 0
            f = PiecewiseLinear([])
            for i in x_points:
                uivar = 'w_' + cs.id + "_%d" % (i + 1)
                ui += self.lp.solution.get_values(uivar)

                x = self.points[cs.id][i + 1]

                p2 = Point(x, ui)

                s = Segment("s%d" % (i + 1), p1, p2)
                f.append(s)

                p1 = p2

            s.p1_in = True
            s.p2_in = True
            cf = CriterionFunction(cs.id, f)
            cfs.append(cf)

        cat = {v: k for k, v in self.cat.items()}
        catv = CategoriesValues()
        ui_a = 0
        for i in range(1, len(cat)):
            ui_b = self.lp.solution.get_values("u_%d" % i)
            catv.append(CategoryValue(cat[i], Interval(ui_a, ui_b)))
            ui_a = ui_b

        catv.append(CategoryValue(cat[i + 1], Interval(ui_a, 1)))

        return obj, cvs, cfs, catv

    def solve(self, aa, pt):
        self.encode_constraints(aa, pt)
        self.add_objective(aa)
        return self.solve_function(aa, pt)

if __name__ == "__main__":
    from pymcda.types import CriteriaValues, CriterionValue
    from pymcda.types import AlternativePerformances
    from pymcda.types import CriteriaFunctions, CriterionFunction
    from pymcda.types import CategoryValue, CategoriesValues
    from pymcda.types import Interval
    from pymcda.uta import AVFSort
    from pymcda.utils import compute_ca
    from pymcda.generate import generate_alternatives
    from pymcda.generate import generate_categories
    from pymcda.generate import generate_criteria
    from pymcda.generate import generate_random_criteria_values
    from pymcda.generate import generate_random_performance_table
    from pymcda.generate import generate_random_criteria_functions
    from pymcda.generate import generate_random_categories_values
    from pymcda.utils import add_errors_in_assignments
    from pymcda.utils import print_pt_and_assignments

    # Generate an avfsort model
    c = generate_criteria(7, random_direction = True)
    cv = generate_random_criteria_values(c, seed = 1)
    cv.normalize()
    cat = generate_categories(3)

    cfs = generate_random_criteria_functions(c, nseg_min = 3, nseg_max = 3)
    catv = generate_random_categories_values(cat)

    u = AVFSort(c, cv, cfs, catv)

    # Generate random alternative and compute assignments
    a = generate_alternatives(1000)
    pt = generate_random_performance_table(a, c)
    aa = u.get_assignments(pt)
    aa_err = aa.copy()
    aa_erroned = add_errors_in_assignments(aa_err, cat.keys(), 0.0)

    print('==============')
    print('Original model')
    print('==============')
    print("Number of alternatives: %d" % len(a))
    print('Criteria weights:')
    cv.display()
    print('Criteria functions:')
    cfs.display()
    print('Categories values:')
    catv.display()
    print("Errors in alternatives assignments: %g %%" \
          % (len(aa_erroned) / len(a) * 100))

    # Learn the parameters from assignment examples
    gi_worst = pt.get_worst(c)
    gi_best = pt.get_best(c)

    css = CriteriaValues([])
    for cf in cfs:
        cs = CriterionValue(cf.id, len(cf.function))
        css.append(cs)

    lp = LpAVFSort(c, css, cat, gi_worst, gi_best)
    obj, cvs, cfs, catv = lp.solve(aa_err, pt)

    print('=============')
    print('Learned model')
    print('=============')
    print('Criteria weights:')
    cvs.display()
    print('Criteria functions:')
    cfs.display()
    print('Categories values:')
    catv.display()

    u2 = AVFSort(c, cvs, cfs, catv)
    aa2 = u2.get_assignments(pt)

    total = len(a)
    nok = nok_erroned = 0
    anok = []
    for alt in a:
        if aa(alt.id) != aa2(alt.id):
            anok.append(alt)
            nok += 1
            if alt.id in aa_erroned:
                nok_erroned += 1

    print("Good assignments          : %3g %%" \
          % ((total - nok) / total *100))
    print("Bad assignments           : %3g %%" \
          % ((nok) / total *100))
    if aa_erroned:
        print("Bad in erroned assignments: %3g %%" \
              % (nok_erroned / total * 100))

    if len(anok) > 0:
        print("Alternatives wrongly assigned:")
        print_pt_and_assignments(anok, c, [aa, aa2], pt)
