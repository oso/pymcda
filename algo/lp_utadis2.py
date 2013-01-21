from __future__ import division
import bisect
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
from mcda.types import point, segment, piecewise_linear
from mcda.types import category_value, categories_values
from mcda.types import criteria_functions, criterion_function
from mcda.types import criteria_values, criterion_value
from mcda.types import categories_values, categories_values, interval
from tools.generate_random import generate_random_criteria_values
from tools.generate_random import generate_random_criteria_functions

verbose = False

try:
    solver = os.environ['SOLVER']
except:
    solver = 'cplex'

if solver == 'glpk':
    import pymprog
#elif solver == 'scip':
#    from zibopt import scip
elif solver == 'cplex':
    import cplex
else:
    raise NameError('Invalid solver selected')

class lp_utadis(object):

    def __init__(self, cat, gi_worst, gi_best):
        self.cat = { cat: i+1 \
                     for i, cat in enumerate(cat.get_ordered_categories()) }
        self.gi_worst = gi_worst
        self.gi_best = gi_best

        if solver == 'cplex':
            self.lp = cplex.Cplex()
            if verbose is False:
                self.lp.set_log_stream(None)
                self.lp.set_results_stream(None)
        elif solver == 'glpk':
            self.lp = pymprog.model('lp_utadis')
            self.lp.verb = verbose

    def __compute_abscissa(self, pt):
        self.points = {}
        for ap in pt:
            for cid, v in ap.performances.items():
                if cid not in self.points:
                    self.points[cid] = [self.gi_worst.performances[cid],
                                        self.gi_best.performances[cid]]

                if v not in self.points[cid]:
                    self.points[cid].append(v)

        for points in self.points.values():
            points.sort()

    def add_variables_cplex(self, aids, pt):
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

        for cid, points in self.points.items():
            nseg = len(points) - 1
            self.lp.variables.add(names = ['w_' + cid + "_%d" % (i + 1)
                                           for i in range(nseg)],
                                  lb = [0 for i in range(nseg)],
                                  ub = [1 for i in range(nseg)])


        ncat = len(self.cat)
        self.lp.variables.add(names = ["u_%d" % i for i in range(1, ncat)],
                              lb = [0 for i in range(ncat-1)],
                              ub = [1 for i in range(ncat-1)])

    def compute_constraint(self, aa, ap):
        d_coefs = {}
        for cid in ap.performances.keys():
            i = self.points[cid].index(ap.performances[cid])
            w_coefs = [1] * i + [0] * (len(self.points[cid]) - 1 - i)
            d_coefs[cid] = w_coefs

        return d_coefs

    def encode_constraint_cplex(self, aa, ap):
        constraints = self.lp.linear_constraints
        d_coefs = self.compute_constraint(aa, ap)

        cat_nr = self.cat[aa.category_id]

        l_vars = ['w_' + cid + '_%d' % (j + 1) for cid in d_coefs.keys()
                  for j in range(len(d_coefs[cid]))]
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
        self.add_variables_cplex(aas.keys(), pt)

        # sum ((sum w_it) + k * w_it+1) - u_k + x_j - x'_j <= -d1
        # sum ((sum w_it) + k * w_it+1) - u_k - y_j + y'_j >= d2
        for aa in aas:
            self.encode_constraint_cplex(aa, pt[aa.id])

        # sum (sum w_it) = 1
        constraints = self.lp.linear_constraints
        w = []
        for cid, values in self.points.items():
            w += ['w_' + cid + "_%d" % (i + 1)
                  for i in range(len(values) - 1)]

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
        self.x = self.lp.var(xrange(len(aids)), 'x', bounds = (0, 1))
        self.y = self.lp.var(xrange(len(aids)), 'y', bounds = (0, 1))
        self.xp = self.lp.var(xrange(len(aids)), 'xp', bounds = (0, 1))
        self.yp = self.lp.var(xrange(len(aids)), 'yp', bounds = (0, 1))

        self.w = {}
        for cid, points in self.points.items():
            self.w[cid] = self.lp.var(xrange(len(points) - 1), 'w_' + cid,
                                      bounds = (0, 1))

        ncat = len(self.cat)
        self.u = self.lp.var(xrange(len(self.cat) - 1), 'u',
                             bounds = (0, 1))

    def encode_constraints_glpk(self, aas, pt):
        self.add_variables_glpk(aas)

        # sum ((sum w_it) + k * w_it+1) - u_k + x_j <= -d1
        # sum ((sum w_it) + k * w_it+1) - u_k - y_j >= d2
        for i, aa in enumerate(aas):
            d_coefs = self.compute_constraint(aa, pt[aa.id])

            cat_nr = self.cat[aa.category_id]

            if cat_nr < len(self.cat):
                self.lp.st(sum(d_coefs[cid][j] * self.w[cid][j] \
                           for cid, points in self.points.items() \
                           for j in range(len(points) - 1)) \
                           + self.x[i] - self.xp[i] - self.u[cat_nr - 1] \
                           == -0.00001)

            if cat_nr > 1:
                self.lp.st(sum(d_coefs[cid][j] * self.w[cid][j] \
                           for cid, points in self.points.items() \
                           for j in range(len(points) - 1)) \
                           - self.y[i] + self.yp[i] - self.u[cat_nr - 2] \
                           == 0.00001)

        # sum (sum w_it) = 1
        self.lp.st(sum(self.w[cid][i] \
                   for cid, points in self.points.items() \
                   for i in range(len(points) - 1)) == 1)

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

        cfs = criteria_functions()
        cvs = criteria_values()
        for cid, points in self.points.items():
            cv = criterion_value(cid, 1)
            cvs.append(cv)

            p1 = point(self.points[cid][0], 0)

            ui = 0
            f = piecewise_linear([])
            for i in range(len(points) - 1):
                uivar = 'w_' + cid + "_%d" % (i + 1)
                ui += self.w[cid][i].primal
                p2 = point(self.points[cid][i + 1], ui)

                s = segment(p1, p2)

                f.append(s)

                p1 = p2

            s.ph_in = True
            cf = criterion_function(cid, f)
            cfs.append(cf)

        cat = {v: k for k, v in self.cat.items()}
        catv = categories_values()
        ui_a = 0
        for i in range(0, len(cat) - 1):
            ui_b = self.u[i].primal
            catv.append(category_value(cat[i + 1], interval(ui_a, ui_b)))
            ui_a = ui_b

        catv.append(category_value(cat[i + 2], interval(ui_a, 1)))

        return obj, cvs, cfs, catv

    def solve_cplex(self, aa, pt):
        self.lp.solve()

        status = self.lp.solution.get_status()
        if status == self.lp.solution.status.infeasible:
            raise RuntimeError("Solver status: %s" % status)

        obj = self.lp.solution.get_objective_value()

        cfs = criteria_functions()
        cvs = criteria_values()
        for cid, points in self.points.items():
            cv = criterion_value(cid, 1)
            cvs.append(cv)

            p1 = point(self.points[cid][0], 0)

            ui = 0
            f = piecewise_linear([])
            for i in range(len(points) - 1):
                uivar = 'w_' + cid + "_%d" % (i + 1)
                ui += self.lp.solution.get_values(uivar)
                p2 = point(self.points[cid][i + 1], ui)

                s = segment(p1, p2)
                f.append(s)

                p1 = p2

            s.ph_in = True
            cf = criterion_function(cid, f)
            cfs.append(cf)

        cat = {v: k for k, v in self.cat.items()}
        catv = categories_values()
        ui_a = 0
        for i in range(1, len(cat)):
            ui_b = self.lp.solution.get_values("u_%d" % i)
            catv.append(category_value(cat[i], interval(ui_a, ui_b)))
            ui_a = ui_b

        catv.append(category_value(cat[i + 1], interval(ui_a, 1)))

        return obj, cvs, cfs, catv

    def solve(self, aa, pt):
        self.__compute_abscissa(pt)

        if solver == 'cplex':
            self.encode_constraints_cplex(aa, pt)
            self.add_objective_cplex(aa)
            solution = self.solve_cplex(aa, pt)
        elif solver == 'glpk':
            self.encode_constraints_glpk(aa, pt)
            self.add_objective_glpk(aa)
            solution = self.solve_glpk(aa, pt)

        return solution

if __name__ == "__main__":
    from mcda.types import criteria_values, criterion_value
    from mcda.types import alternative_performances
    from mcda.types import criteria_functions, criterion_function
    from mcda.types import category_value, categories_values
    from mcda.types import interval
    from mcda.uta import utadis
    from tools.utils import normalize_criteria_weights
    from tools.utils import compute_ca
    from tools.generate_random import generate_alternatives
    from tools.generate_random import generate_random_categories
    from tools.generate_random import generate_criteria
    from tools.generate_random import generate_random_criteria_values
    from tools.generate_random import generate_random_performance_table
    from tools.generate_random import generate_random_criteria_functions
    from tools.generate_random import generate_random_categories_values
    from tools.utils import add_errors_in_assignments
    from tools.utils import display_assignments_and_pt

    # Generate an utadis model
    c = generate_criteria(2)
    cv = generate_random_criteria_values(c, seed = 6)
    normalize_criteria_weights(cv)
    cat = generate_random_categories(3)

    cfs = generate_random_criteria_functions(c, nseg_min = 3, nseg_max = 3)
    catv = generate_random_categories_values(cat)

    u = utadis(c, cv, cfs, catv)

    # Generate random alternative and compute assignments
    a = generate_alternatives(10)
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
    gi_worst = alternative_performances('worst', {crit.id: 0 for crit in c})
    gi_best = alternative_performances('best', {crit.id: 1 for crit in c})

    lp = lp_utadis(cat, gi_worst, gi_best)
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

    u2 = utadis(c, cvs, cfs, catv)
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
        display_assignments_and_pt(anok, c, [aa, aa2], [pt])
