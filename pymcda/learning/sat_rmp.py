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
        for (clause, w) in self.clauses:
            self.print_clause(clause)

    def number_of_clauses(self):
        return len(self.clauses)

    def number_of_variables(self):
        return len(self.variables)

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
        for (clause, w) in self.clauses:
            self.print_clause_with_solution(clause, solution)

    def add_clause(self, clause, weight = 1000):
        self.clauses.append((clause, weight))

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

                if len(set(combi)) != len(set(combi2)) - 1:
                    continue

                v1 = self.variables[('y', combi2, combi)]
                self.add_clause([v1])

        # Add phi completeness
        for combi in self.criteria_combinations:
            for combi2 in self.criteria_combinations:
                if len(set(combi)) != len(set(combi2)) - 1:
                    continue

                v1 = self.variables[('y', combi, combi2)]
                v2 = self.variables[('y', combi2, combi)]
                self.add_clause([v1, v2])

        # Add phi transitivity
        for combi in self.criteria_combinations:
            for combi2 in self.criteria_combinations:
                for combi3 in self.criteria_combinations:
                    if set(combi).issubset(set(combi2)):
                        continue

                    if set(combi2).issubset(set(combi3)):
                        continue

                    if set(combi3).issubset(set(combi)):
                        continue

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
                self.add_clause(clause, 1)

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

    def solve_sat(self):
        for (clause, w) in self.clauses:
            self.solver.add_clause(clause)

        sat, solution = self.solver.solve()
        if sat is False:
            return False

        #self.print_clauses_with_solution(solution)
        #print(solution[0], len(solution))
        self.__parse_solution(solution)

        return True

    def __clauses_to_dimacs(self, f):
        f.write("p wcnf %d %d\n" % (self.number_of_variables(),
                                    self.number_of_clauses()))
        for (clause, w) in self.clauses:
            f.write(str(w) + " " + " ".join(map(str, clause)) + " 0\n")


    def solve_maxsat(self):
        import tempfile
        import subprocess
        f = tempfile.NamedTemporaryFile(delete = False)
        self.__clauses_to_dimacs(f)
        f.flush()
        output = subprocess.check_output(["maxhs", f.name])
        output = output.decode("ascii",errors="ignore")

        for line in output.splitlines():
            if line.startswith("v "):
                solution = line[2:]
                break
        f.close()

        solution = [None] + [True if int(sol) >= 0 else False
                    for sol in solution.split(" ")]
        self.__parse_solution(solution)
        return True

    def solve(self, maxsat = False):
        if maxsat is True:
            return self.solve_maxsat()

        return self.solve_sat()

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
    ncriteria = 5
    nprofiles = 1
    npairs = 30
    nbinversions = 5

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
    while i != npairs:
        x = Alternative("x%d" % (i + 1))
        y = Alternative("y%d" % (i + 1))
        apx = generate_random_alternative_performances(x, c)
        apy = generate_random_alternative_performances(y, c)
        pwc = model.compare(apx, apy)
        if pwc.relation == pwc.INDIFFERENT:
            continue
        if apx.dominates(apy, c) or apy.dominates(apx, c):
            continue

        if i < nbinversions:
            print(pwc)
            if pwc.relation == pwc.PREFERRED:
                pwc.relation = pwc.WEAKER
            else:
                pwc.relation = pwc.PREFERRED
            print(pwc)

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
        solution = satrmp.solve(True)
        if solution is False:
            print("Warning: no MaxSAT solution")
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
    print("Number of variables: %d" % satrmp.number_of_variables())
    print("Number of clauses: %d" % satrmp.number_of_clauses())
