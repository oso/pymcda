from __future__ import division
import bisect
import os
import sys
sys.path.insert(0, "..")
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

    def __init__(self, cs, cat, gi_worst, gi_best):
        self.cs = cs
        self.cat = { cat: i+1 \
                     for i, cat in enumerate(cat.get_ordered_categories()) }
        self.gi_worst = gi_worst
        self.gi_best = gi_best
        self.__compute_abscissa()

        if solver == 'cplex':
            self.lp = cplex.Cplex()
        elif solver == 'glpk':
            self.lp = pymprog.model('lp_utadis')
            self.lp.verb = verbose

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
        left = bisect.bisect_right(self.points[cid], x) - 1
        if left == len(self.points[cid]) - 1:
            left -= 1
        return left

    def add_variables_cplex(self, aids):
        self.lp.variables.add(names = ['x_' + aid for aid in aids],
                              lb = [0 for aid in aids],
                              ub = [1 for aid in aids])
        self.lp.variables.add(names = ['y_' + aid for aid in aids],
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
            d = self.points[cs.id][left + 1] - self.points[cs.id][left]
            k = (perf - self.points[cs.id][left]) / d

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
            constraints.add(names = ['csup' + aa.alternative_id],
                            lin_expr =
                                [[
                                 l_vars +
                                  ["u_%d" % cat_nr,
                                   'x_' + aa.alternative_id],
                                 l_coefs + [-1.0, 1.0],
                                ]],
                            senses = ["L"],
                            rhs = [-0.00001],
                           )

        if cat_nr > 1:
            constraints.add(names = ['cinf' + aa.alternative_id],
                            lin_expr =
                                [[
                                 l_vars +
                                  ["u_%d" % (cat_nr - 1),
                                   'y_' + aa.alternative_id],
                                 l_coefs + [-1.0, -1.0],
                                ]],
                            senses = ["G"],
                            rhs = [0.00001],
                           )

    def encode_constraints_cplex(self, aas, pt):
        self.add_variables_cplex(aas.keys())

        # sum ((sum w_it) + k * w_it+1) - u_k + x_j <= -d1
        # sum ((sum w_it) + k * w_it+1) - u_k - y_j >= d2
        for aa in aas:
            self.encode_constraint_cplex(aa, pt[aa.alternative_id])

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
                            rhs = [0.01],
                           )

    def add_objective_cplex(self, aa):
        self.lp.objective.set_sense(self.lp.objective.sense.minimize)
        for aa in aa.keys():
            self.lp.objective.set_linear('x_' + aa, 1)
            self.lp.objective.set_linear('y_' + aa, 1)

    def add_variables_glpk(self, aids):
        self.x = self.lp.var(xrange(len(aids)), 'x', bounds=(0, 1))
        self.y = self.lp.var(xrange(len(aids)), 'y', bounds=(0, 1))

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
            d_coefs = self.compute_constraint(aa, pt[aa.alternative_id])

            cat_nr = self.cat[aa.category_id]

            if cat_nr < len(self.cat):
                self.lp.st(sum(d_coefs[cs.id][j] * self.w[cs.id][j] \
                           for cs in self.cs for j in range(cs.value)) \
                           + self.x[i] - self.u[cat_nr - 1] \
                           <= -0.00001)

            if cat_nr > 1:
                self.lp.st(sum(d_coefs[cs.id][j] * self.w[cs.id][j] \
                           for cs in self.cs for j in range(cs.value)) \
                           - self.y[i] - self.u[cat_nr - 2] \
                           >= 0.00001)

        # sum (sum w_it) = 1
        self.lp.st(sum(self.w[cs.id][i] for cs in self.cs \
                   for i in range(cs.value)) == 1)

        # u_k - u_k-1 >= s
        ncat = len(self.cat)
        for i in range(1, ncat - 1):
            self.lp.st(self.u[i] - self.u[i - 1] >= 0.01)

    def add_objective_glpk(self, aa):
        self.lp.min(sum(self.x[i] for i in range(len(self.x)))
                    + sum(self.y[i] for i in range(len(self.y))))

    def solve_glpk(self, aa, pt):
        self.lp.solve()

        status = self.lp.status()
        if status != 'opt':
            raise RuntimeError("Solver status: %s" % self.lp.status())

        cfs = criteria_functions()
        cvs = criteria_values()
        for cs in self.cs:
            cv = criterion_value(cs.id, 1)
            cvs.append(cv)

            p1 = point(self.points[cs.id][0], 0)

            ui = 0
            f = piecewise_linear([])
            for i in range(cs.value):
                uivar = 'w_' + cs.id + "_%d" % (i + 1)
                ui += self.w[cs.id][i].primal
                p2 = point(self.points[cs.id][i + 1], ui)

                s = segment(p1, p2)

                f.append(s)

                p1 = p2

            s.ph_in = True
            cf = criterion_function(cs.id, f)
            cfs.append(cf)

        cat = {v: k for k, v in self.cat.items()}
        catv = categories_values()
        ui_a = 0
        for i in range(0, len(cat) - 1):
            ui_b = self.u[i].primal
            catv.append(category_value(cat[i + 1], interval(ui_a, ui_b)))
            ui_a = ui_b

        catv.append(category_value(cat[i + 2], interval(ui_a, 1)))

        return cvs, cfs, catv

    def solve_cplex(self, aa, pt):
        self.lp.solve()

        cfs = criteria_functions()
        cvs = criteria_values()
        for cs in self.cs:
            cv = criterion_value(cs.id, 1)
            cvs.append(cv)

            p1 = point(self.points[cs.id][0], 0)

            ui = 0
            f = piecewise_linear([])
            for i in range(cs.value):
                uivar = 'w_' + cs.id + "_%d" % (i + 1)
                ui += self.lp.solution.get_values(uivar)
                p2 = point(self.points[cs.id][i + 1], ui)

                s = segment(p1, p2)
                f.append(s)

                p1 = p2

            s.ph_in = True
            cf = criterion_function(cs.id, f)
            cfs.append(cf)

        cat = {v: k for k, v in self.cat.items()}
        catv = categories_values()
        ui_a = 0
        for i in range(1, len(cat)):
            ui_b = self.lp.solution.get_values("u_%d" % i)
            catv.append(category_value(cat[i], interval(ui_a, ui_b)))
            ui_a = ui_b

        catv.append(category_value(cat[i + 1], interval(ui_a, 1)))

        return cvs, cfs, catv

    def solve(self, aa, pt):
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
    from tools.utils import compute_ac
    from tools.generate_random import generate_random_alternatives
    from tools.generate_random import generate_random_categories
    from tools.generate_random import generate_random_criteria
    from tools.generate_random import generate_random_criteria_values
    from tools.generate_random import generate_random_performance_table
    from tools.generate_random import generate_random_criteria_functions
    from tools.generate_random import generate_random_categories_values
    from tools.utils import display_affectations_and_pt

    # Generate an utadis model
    c = generate_random_criteria(3)
    cv = generate_random_criteria_values(c, seed = 1235)
    normalize_criteria_weights(cv)
    cat = generate_random_categories(3)

    cfs = generate_random_criteria_functions(c)
    catv = generate_random_categories_values(cat)

    u = utadis(c, cv, cfs, catv)

    # Generate random alternative and compute assignments
    a = generate_random_alternatives(1000)
    pt = generate_random_performance_table(a, c)
    aa = u.get_assignments(pt)

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

    # Learn the parameters from assignment examples
    gi_worst = alternative_performances('worst', {crit.id: 0 for crit in c})
    gi_best = alternative_performances('best', {crit.id: 1 for crit in c})

    css = criteria_values([])
    for cf in cfs:
        cs = criterion_value(cf.id, len(cf.function))
        css.append(cs)

    lp = lp_utadis(css, cat, gi_worst, gi_best)
    cvs, cfs, catv = lp.solve(aa, pt)

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
    nok = 0
    anok = []
    for alt in a:
        if aa(alt.id) != aa2(alt.id):
            anok.append(alt)
            nok += 1

    print("Good affectations          : %3g %%" \
          % ((total - nok) / total *100))
    print("Bad affectations           : %3g %%" \
          % ((nok) / total *100))

    if len(anok) > 0:
        print("Alternatives wrongly assigned:")
        display_affectations_and_pt(anok, c, [aa, aa2], [pt])
