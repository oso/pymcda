from __future__ import division
import bisect
import sys
sys.path.insert(0, "..")
from mcda.types import point

import cplex

class lp_utadis(object):

    def __init__(self, cs, c, gi_worst, gi_best):
        self.cs = cs
        self.gi_worst = gi_worst
        self.gi_best = gi_best
        self.__compute_abscissa()

        self.lp = cplex.Cplex()

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

    def __get_points(self, cid, x):
        left = bisect.bisect_left(self.points[cid], x) - 1
        right = bisect.bisect_right(self.points[cid], x)
        return left, right

    def encode_constraint(self, aa, ap):
        for cs in self.cs:
            perf = ap.performances[cs.id]
            left, right = self.__get_points(cs.id, perf)
            d = self.points[cs.id][right] - self.points[cs.id][left]
            k = (perf - self.points[cs.id][left]) / d

    def encode_constraints(self, aas, pt):
        for aa in aas:
            self.encode_constraint(aa, pt[aa.alternative_id])

    def solve(self, aa, pt):
        self.encode_constraints(aa, pt)
        for a in aa:
            print pt[a.alternative_id]
            print a

if __name__ == "__main__":
    from mcda.types import criteria_values, criterion_value
    from mcda.types import alternative_performances
    from mcda.types import criteria_functions, criterion_function
    from mcda.types import category_value, categories_values
    from mcda.types import interval
    from mcda.uta import utadis
    from tools.generate_random import generate_random_alternatives
    from tools.generate_random import generate_random_categories
    from tools.generate_random import generate_random_criteria
    from tools.generate_random import generate_random_criteria_values
    from tools.generate_random import generate_random_performance_table
    from tools.generate_random import generate_random_criteria_functions

    # Generate an utadis model
    c = generate_random_criteria(3)
    cv = generate_random_criteria_values(c, seed = 123)
    cat = generate_random_categories(3)

    cfs = generate_random_criteria_functions(c)

    catv1 = category_value("cat1", interval(0, 0.25))
    catv2 = category_value("cat2", interval(0.25, 0.65))
    catv3 = category_value("cat3", interval(0.65, 1))
    catv = categories_values([catv1, catv2, catv3])

    u = utadis(c, cv, cfs, catv)

    # Generate random alternative and compute assignments
    a = generate_random_alternatives(10)
    pt = generate_random_performance_table(a, c)
    aa = u.get_assignments(pt)

    # Learn the parameters from assignment examples
    gi_worst = alternative_performances('worst',
                                        {'c1': 0, 'c2': 0, 'c3': 0})
    gi_best = alternative_performances('best',
                                       {'c1': 1, 'c2': 1, 'c3': 1})

    css = criteria_values([])
    for cf in cfs:
        cs = criterion_value(cf.id, len(cf.function))
        css.append(cs)

    print(cfs)
    print(gi_worst)
    print(gi_best)
    print(css)

    lp = lp_utadis(css, cat, gi_worst, gi_best)
    lp.solve(aa, pt)
