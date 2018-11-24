#!/usr/bin/env python2

import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../../")

from itertools import combinations

from pymcda.types import AlternativePerformances
from pymcda.types import CriteriaValues, CriterionValue
from pymcda.types import CriteriaSet
from pymcda.types import PerformanceTable

from pymcda.choquet import capacities_to_mobius

from pymcda.utils import powerset

import pycryptosat

class SatRMP():

    epsilon = 0.001

    def __init__(self, model, pt, pw_comparisons):
        self.model = model
        self.criteria = model.criteria
        self.pt = pt
        self.pw_comparisons = pw_comparisons

        self.x = pt.get_unique_values()
        for k, v in self.x.items():
            v.sort()

        self.criteria_combinations = []
        for i in range(0, len(self.criteria) + 1):
            for c in combinations(self.criteria.keys(), i):
                clist = list(c)
                clist.sort()
                self.criteria_combinations.append(tuple(clist))

        self.clauses = []
        self.__update_sat()

    def print_clause(self, clause):
        var_map = {v: '_'.join(tuple(map(str, k))) for k, v in self.variables.items()}
        sign = lambda a: '' if a > 0 else '-' if a < 0 else 0
        txt = map(lambda x: sign(x) + str(var_map[abs(x)]), clause)
        txt = " V ".join(txt)
        print(txt)

    def print_clauses(self):
        for clause in self.clauses:
            self.print_clause(clause)

    def number_of_clauses(self):
        return len(self.clauses)

    def print_clause_with_solution(self, clause, solution):
        var_map = {v: '_'.join(tuple(map(str, k))) for k, v in self.variables.items()}
        sign = lambda a: '' if a > 0 else '-' if a < 0 else 0
        txt = map(lambda x: sign(x) + str(var_map[abs(x)]), clause)
        txt = " V ".join(txt)

        sol = lambda a: solution[a] if a > 0 else not solution[-a]
        txt2 = map(lambda x: str(sol(x)), clause)
        txt2 = " V ".join(txt2)
        print(txt + ': ' + str(txt2))

    def print_clauses_with_solution(self, solution):
        for clause in self.clauses:
            self.print_clause_with_solution(clause, solution)

    def add_clause(self, clause):
        self.clauses.append(clause)
        self.solver.add_clause(clause)

    def __add_variable(self, name):
        self.nvariables += 1
        self.variables[name] = self.nvariables

    def __create_variables(self):
        self.variables = {}
        self.nvariables = 0

        # x_{i,h,k}
        for c in self.criteria:
            for h in self.model.profiles:
                xi = self.x[c.id]
                for i in range(len(xi)):
                    self.__add_variable(('x', c.id, h, xi[i]))

        # y_{A,B}
        for combi in self.criteria_combinations:
            for combi2 in self.criteria_combinations:
                self.__add_variable(('y', combi, combi2))

        # z_{j,h}
        for pwc in self.pw_comparisons:
            for h in self.model.profiles:
                self.__add_variable(('z', pwc.id, h))

        # z'_{j,h}
        for pwc in self.pw_comparisons:
            for h in self.model.profiles:
                self.__add_variable(('zp', pwc.id, h))

        # s_{j,h}
        for pwc in self.pw_comparisons:
            for h in self.model.profiles:
                self.__add_variable(('s', pwc.id, h))

        # d_{h,h'}
        for h in self.model.profiles:
            for h2 in self.model.profiles:
                if h == h2:
                    continue

                self.__add_variable(('d', h, h2))

    def __update_constraints(self):
        # Add phi_scales
        for c in self.criteria:
            for h in self.model.profiles:
                xi = self.x[c.id]
                for i in range(len(xi) - 1):
                    v1 = self.variables[('x', c.id, h, xi[i])]
                    v2 = self.variables[('x', c.id, h, xi[i + 1])]
                    self.add_clause([-v1, v2])

        # Add phi profiles_1
        for h in self.model.profiles:
            for h2 in self.model.profiles:
                if h == h2:
                    continue

                for c in self.criteria:
                    for k in self.x[c.id]:
                        v1 = self.variables[('x', c.id, h2, k)]
                        v2 = self.variables[('x', c.id, h, k)]
                        v3 = self.variables[('d', h, h2)]
                        self.add_clause([v1, -v2, -v3])

        # Add phi profiles_2
        for i in range(len(self.model.profiles) - 1):
            for j in range(i + 1, len(self.model.profiles)):
                h = self.model.profiles[i]
                h2 = self.model.profiles[j]
                v1 = self.variables[('d', h, h2)]
                v2 = self.variables[('d', h2, h)]
                self.add_clause([v1, v2])

        # Add phi pareto
        for combi in self.criteria_combinations:
            for combi2 in self.criteria_combinations:
                if not set(combi).issubset(set(combi2)):
                    continue

                v1 = self.variables[('y', combi2, combi)]
                self.add_clause([v1])

        # Add phi completeness
        for combi in self.criteria_combinations:
            for combi2 in self.criteria_combinations:
                v1 = self.variables[('y', combi, combi2)]
                v2 = self.variables[('y', combi2, combi)]
                self.add_clause([v1, v2])

        # Add phi transitivity
        for combi in self.criteria_combinations:
            for combi2 in self.criteria_combinations:
                for combi3 in self.criteria_combinations:
                    v1 = self.variables[('y', combi, combi2)]
                    v2 = self.variables[('y', combi2, combi3)]
                    v3 = self.variables[('y', combi, combi3)]
                    self.add_clause([-v1, -v2, v3])

        # Add phi outranking 1
        for a in self.criteria_combinations:
            for b in self.criteria_combinations:
                for h in self.model.profiles:
                    for j in self.pw_comparisons:
                        clause = []
                        for i in self.criteria:
                            if i.id in a:
                                continue

                            ap = self.pt[j.a].performances
                            v = self.variables[('x', i.id, h, ap[i.id])]
                            clause.append(v)

                        for i in self.criteria:
                            if i.id not in b:
                                continue

                            ap = self.pt[j.b].performances
                            v = self.variables[('x', i.id, h, ap[i.id])]
                            clause.append(-v)

                        v = self.variables[('y', a, b)]
                        clause.append(v)

                        v = self.variables[('z', j.id, h)]
                        clause.append(-v)

                        self.add_clause(clause)

        # Add phi outranking 2
        for a in self.criteria_combinations:
            for b in self.criteria_combinations:
                for h in self.model.profiles:
                    for j in self.pw_comparisons:
                        clause = []
                        for i in self.criteria:
                            if i.id in a:
                                continue

                            ap = self.pt[j.b].performances
                            v = self.variables[('x', i.id, h, ap[i.id])]
                            clause.append(v)

                        for i in self.criteria:
                            if i.id not in b:
                                continue

                            ap = self.pt[j.a].performances
                            v = self.variables[('x', i.id, h, ap[i.id])]
                            clause.append(-v)

                        v = self.variables[('y', a, b)]
                        clause.append(v)

                        v = self.variables['zp', j.id, h]
                        clause.append(-v)

                        self.add_clause(clause)

        # Add phi outranking 3
        for a in self.criteria_combinations:
            for b in self.criteria_combinations:
                for h in self.model.profiles:
                    for j in self.pw_comparisons:
                        clause = []
                        for i in self.criteria:
                            ap = self.pt[j.a].performances
                            v = self.variables[('x', i.id, h, ap[i.id])]
                            if i.id in a:
                                clause.append(-v)
                            else:
                                clause.append(v)


                        for i in self.criteria:
                            ap = self.pt[j.b].performances
                            v = self.variables[('x', i.id, h, ap[i.id])]
                            if i.id in b:
                                clause.append(-v)
                            else:
                                clause.append(v)

                        v = self.variables[('y', b, a)]
                        clause.append(-v)

                        v = self.variables['zp', j.id, h]
                        clause.append(v)

                        self.add_clause(clause)

        # Add phi preference
        for pwc in self.pw_comparisons:
            if pwc.relation == pwc.INDIFFERENT:
                for h in self.model.profiles:
                    v = self.variables['s', pwc.id, h]
                    self.add_clause([-v])
            else:
                clause = []
                for h in self.model.profiles:
                    v = self.variables['s', pwc.id, h]
                    clause.append(v)
                self.add_clause(clause)

        # Add phi lexicography
        for pwc in self.pw_comparisons:
            for i in range(len(self.model.profiles)):
                for j in range(i, len(self.model.profiles)):
                    v1 = self.variables[('z', pwc.id, self.model.profiles[i])]
                    v2 = self.variables[('s', pwc.id, self.model.profiles[j])]
                    self.add_clause([v1, -v2])

        # Add phi lexicography 2
        for pwc in self.pw_comparisons:
            for i in range(len(self.model.profiles) - 1):
                for j in range(i + 1, len(self.model.profiles)):
                    v1 = self.variables[('zp', pwc.id, self.model.profiles[i])]
                    v2 = self.variables[('s', pwc.id, self.model.profiles[j])]
                    self.add_clause([v1, -v2])

        # Add phi lexicography 3
        for pwc in self.pw_comparisons:
            for h in self.model.profiles:
                v1 = self.variables[('zp', pwc.id, h)]
                v2 = self.variables[('s', pwc.id, h)]
                self.add_clause([-v1, -v2])

    def __update_sat(self):
        self.solver = pycryptosat.Solver(threads=1)
        self.__create_variables()
        self.__update_constraints()

    def __parse_profile_order(self, solution):
        l = [self.model.profiles[0]]
        for profile in self.model.profiles[1:]:
            for fixed in l:
                v = self.variables[('d', profile, fixed)]
                if solution[v] is False:
                    l = [profile] + l
                    break

            if profile not in l:
                l += [profile]

        return l

    def __parse_profiles(self, solution):
        bpt = PerformanceTable()
        for profile in self.model.profiles:
            bp = AlternativePerformances(profile, {})
            for c in self.criteria:
                xi = sorted(self.x[c.id])
                bp.performances[c.id] = xi[-1] + self.epsilon * c.direction
                for xij in xi:
                    var = self.variables[('x', c.id, profile, xij)]
                    val = solution[var]
                    if val is True:
                        bp.performances[c.id] = xij
                        break
            bpt.append(bp)
        return bpt

    def __parse_coalitions(self, solution):
        coalitions = dict()
        for combi in self.criteria_combinations:
            coalitions[combi] = dict()
            for combi2 in self.criteria_combinations:
                var = self.variables[('y', combi, combi2)]
                val = solution[var]
                coalitions[combi][combi2] = val

        return coalitions

    def __parse_solution(self, solution):
#        self.model.profiles = self.__parse_profile_order(solution)
        self.model.bpt = self.__parse_profiles(solution)
        self.model.coalition_relations = self.__parse_coalitions(solution)

    def solve(self):
        sat, solution = self.solver.solve()
        if sat is False:
            return False

        #self.print_clauses_with_solution(solution)
        self.__parse_solution(solution)

        return True

if __name__ == "__main__":
    from pymcda.types import Alternative
    from pymcda.types import PairwiseRelations
    from pymcda.types import PerformanceTable
    from pymcda.generate import generate_alternatives
    from pymcda.generate import generate_criteria
    from pymcda.generate import generate_random_profiles
    from pymcda.generate import generate_random_criteria_values
    from pymcda.generate import generate_random_alternative_performances
    from pymcda.generate import generate_random_performance_table
    from pymcda.rmp import RMP
    import random

    seed = 2
    ncriteria = 4
    nprofiles = 3
    nalternatives = 100

    random.seed(seed)
    c = generate_criteria(ncriteria)
    cv = generate_random_criteria_values(c)
    b = [ "b%d" % i for i in range(1, nprofiles + 1)]
    bpt = generate_random_profiles(b, c)
    random.shuffle(b)
    model = RMP(c, cv, b, bpt)

    i = 0
    pwcs = PairwiseRelations()
    pt = PerformanceTable()
    while i != nalternatives:
        x = Alternative("x%d" % (i + 1))
        y = Alternative("y%d" % (i + 1))
        apx = generate_random_alternative_performances(x, c)
        apy = generate_random_alternative_performances(y, c)
        pwc = model.compare(apx, apy)
        if pwc.relation == pwc.INDIFFERENT:
            continue
        if apx.dominates(apy, c) or apy.dominates(apx, c):
            continue

        pt.append(apx)
        pt.append(apy)
        pwcs.append(pwc)
        i += 1

    pwcs.weaker_to_preferred()

    model2 = RMP(c, None, b, None)

    satrmp = SatRMP(model2, pt, pwcs)
    solution = satrmp.solve()
    if solution is False:
        print("Warning: solution is UNSAT")
        sys.exit(1)

    pwcs2 = PairwiseRelations()
    for pwc in pwcs:
        pwc2 = model2.compare(pt[pwc.a], pt[pwc.b])

        if pwc != pwc2:
            print("%s != %s" % (pwc, pwc2))
            print(pt[pwc.a])
            print(pt[pwc.b])
    print(model.profiles)
    print(model.bpt)
    print(model2.profiles)
    print(model2.bpt)

#    satrmp.print_clauses()
    print("Number of clauses %d" % satrmp.number_of_clauses())

#    a1 = generate_alternatives(nalternatives, "x")
#    pt1 = generate_random_performance_table(a1, c)
#    a2 = generate_alternatives(nalternatives, "y")
#    pt2 = generate_random_performance_table(a2, c)
#
#    pwcs = PairwiseRelations()
#    for i in range(1, len(pt1) + 1):
#        pwc = model.compare(pt1["x%d" % i], pt2["y%d" % i])
#        pwcs.append(pwc)
#
#    pwcs.weaker_to_preferred()
##    pwcs = pwcs.get_preferred()
#    print(len(pwcs))
#
#    pt = PerformanceTable()
#    for ap in pt1:
#        pt.append(ap)
#    for ap in pt2:
#        pt.append(ap)
#
#    model2 = RMP(c, None, b, None)
#    satrmp = SatRMP(model2, pt, pwcs)
#    solution = satrmp.solve()
#    if solution is False:
#        print("Problem is UNSAT!")
#        sys.exit(1);
#
#    pwcs2 = PairwiseRelations()
#    for pwc in pwcs:
#        pwc2 = model2.compare(pt[pwc.a], pt[pwc.b])
#        pwcs2.append(pwc2)
#
#    #print("Performance table")
#    #print(pt)
#
#    #print("Original model")
#    #print(model.profiles)
#    #print(model.bpt)
#    #print(pwcs)
#
#    #print("Learned model")
#    #print(model2.profiles)
#    #print(model2.bpt)
#    #print(pwcs2)
#
#    for pwc, pwc2 in zip(pwcs, pwcs2):
#        if pwc != pwc2:
#            print("%s != %s" % (pwc, pwc2))
#            print(pt[pwc.a])
#            print(pt[pwc.b])
#
#    ncriteria = 2
#
#    c = generate_criteria(ncriteria)
#    cv = CriteriaValues(CriterionValue(crit.id, float(1) / ncriteria) for crit in c)
#    b1 = AlternativePerformances('b1', {crit.id: 9 for crit in c})
#    b2 = AlternativePerformances('b2', {crit.id: 5 for crit in c})
#    bpt = PerformanceTable([b1, b2])
#    model = RMP(c, cv, ["b1", "b2"], bpt)
#
#    # Define the alternatives
#    a = generate_alternatives(8)
#    x1 = AlternativePerformances('x1', {'c1': 9, 'c2': 9, 'c3': 1})
#    y1 = AlternativePerformances('y1', {'c1': 9, 'c2': 5, 'c3': 1})
#
#    x2 = AlternativePerformances('x2', {'c1': 9, 'c2': 9, 'c3': 1})
#    y2 = AlternativePerformances('y2', {'c1': 1, 'c2': 9, 'c3': 1})
#
#    x3 = AlternativePerformances('x3', {'c1': 1, 'c2': 5, 'c3': 1})
#    y3 = AlternativePerformances('y3', {'c1': 5, 'c2': 1, 'c3': 9})
#
#    x4 = AlternativePerformances('x4', {'c1': 1, 'c2': 9, 'c3': 9})
#    y4 = AlternativePerformances('y4', {'c1': 9, 'c2': 1, 'c3': 1})
#
#    x5 = AlternativePerformances('x5', {'c1': 9, 'c2': 9, 'c3': 9})
#    y5 = AlternativePerformances('y5', {'c1': 9, 'c2': 1, 'c3': 1})
#
#    x6 = AlternativePerformances('x6', {'c1': 9, 'c2': 9, 'c3': 9})
#    y6 = AlternativePerformances('y6', {'c1': 9, 'c2': 9, 'c3': 1})
#
#    pt = PerformanceTable([x1, y1, x2, y2, x3, y3, x4, y4, x5, y5, x6, y6])
#
##    x1 = AlternativePerformances('x1', {'c1': 3, 'c2': 9, 'c3': 9})
##    y1 = AlternativePerformances('y1', {'c1': 2, 'c2': 1, 'c3': 1})
##
##    x2 = AlternativePerformances('x2', {'c1': 2, 'c2': 1, 'c3': 1})
##    y2 = AlternativePerformances('y2', {'c1': 1, 'c2': 9, 'c3': 9})
##    pt = PerformanceTable([x1, y1, x2, y2])
#
#    pwcs = PairwiseRelations()
#    for i in range(0, len(pt) / 2 - 3):
#        pwc = model.compare(eval("x%d" % (i + 1)), eval("y%d" % (i + 1)))
#        pwcs.append(pwc)
#
#    satrmp = SatRMP(model, pt, pwcs)
#    solution = satrmp.solve()
#    if solution is False:
#        print("Problem is UNSAT!")
#        sys.exit(1);
#
#    print(pt)
#    print(solution)
#    print(pwcs)
#
#    pwcs2 = PairwiseRelations()
#    for i in range(0, len(pt) / 2):
#        pwc = model.compare(eval("x%d" % (i + 1)), eval("y%d" % (i + 1)))
#        pwcs2.append(pwc)
#
#    print(pwcs2)
