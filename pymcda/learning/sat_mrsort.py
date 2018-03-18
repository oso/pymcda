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

class SatMRSort():

    def __init__(self, model, performance_table, assignments):
        self.model = model
        self.criteria = model.criteria
        self.categories = model.categories
        self.categories_profiles = model.categories_profiles
        self.performance_table = performance_table
        self.assignments = assignments

        self.__update_sat()

    def __add_variable(self, name):
        self.nvariables += 1
        self.variables[name] = self.nvariables

    def __create_variables(self):
        self.variables = {}
        self.nvariables = 0

        # z_{i,h,k}
        self.x = pt.get_unique_values()
        for c in self.criteria:
            for cp in self.categories_profiles:
                xi = self.x[c.id]
                for i in range(len(xi)):
                    self.__add_variable((c.id, cp.id, xi[i]))

        # y_{C}
        for i in range(0, len(self.criteria) + 1):
            for c in combinations(self.criteria.keys(), i):
                clist = list(c)
                clist.sort()
                self.__add_variable(tuple(clist))

    def __update_constraints(self):
        # Add clause 1
        for c in self.criteria:
            for cp in self.categories_profiles:
                xi = self.x[c.id]
                xi.sort()
                for i in range(len(xi) - 1):
                    v1 = self.variables[(c.id, cp.id, xi[i])]
                    v2 = self.variables[(c.id, cp.id, xi[i + 1])]
                    self.solver.add_clause([-v1, v2])

        # Add clause 2
        profiles = self.categories_profiles.get_ordered_profiles()
        for c in self.criteria:
            xi = self.x[c.id]
            for xij in xi:
                for i in range(len(profiles) - 1):
                    v1 = self.variables[(c.id, profile[i], xij)]
                    v2 = self.variables[(c.id, profile[i + 1], xij)]
                    self.solver.add_clause([v1, -v2])

        # Add clause 3
        for i in range(len(self.criteria), -1, -1):
            coalitions = combinations(self.criteria.keys(), i)
            for coalition in coalitions:
                coalition = tuple(sorted(list(coalition)))
                for j in range(i - 1, -1, -1):
                    coalitions2 = combinations(list(coalition), j)
                    for coalition2 in coalitions2:
                        coalition2 = tuple(sorted(list(coalition2)))
                        v1 = self.variables[coalition]
                        v2 = self.variables[coalition2]
                        self.solver.add_clause([v1, -v2])

        # Add clause 4
        for i in range(len(self.criteria) + 1):
            for coalition in combinations(self.criteria.keys(), i):
                coainv = tuple(sorted(list(set(self.criteria.keys()) ^ set(coalition))))
                v2 = self.variables[coainv]
                for cp in self.categories_profiles:
                    cat = cp.value.upper
                    aids = self.assignments.get_alternatives_in_category(cat)
                    for a in aids:
                        perfs = self.performance_table[a].performances
                        v1 = [self.variables[(c, cp.id, perfs[c])]
                              for c in coalition]
                        v1.append(v2)
                        self.solver.add_clause(v1)

        # Add clause 5
        for i in range(len(self.criteria) + 1):
            for coalition in combinations(self.criteria.keys(), i):
                coalition = tuple(sorted(list(coalition)))
                v2 = -self.variables[coalition]
                for cp in self.categories_profiles:
                    cat = cp.value.lower
                    aids = self.assignments.get_alternatives_in_category(cat)
                    for a in aids:
                        perfs = self.performance_table[a].performances
                        v1 = [-self.variables[(c, cp.id, perfs[c])]
                              for c in coalition]
                        v1.append(v2)
                        self.solver.add_clause(v1)

    def __update_sat(self):
        self.solver = pycryptosat.Solver()
        self.__create_variables()
        self.__update_constraints()

    def __parse_solution(self, solution):
        # Get capacities
        cv = CriteriaValues()
        for c in self.criteria.keys():
            var = self.variables[(c,)]
            val = 1 if solution[var] is True else 0
            cval = CriterionValue(c, val)
            cv.append(cval)

        for i in range(2, len(self.criteria) + 1):
            for coalition in combinations(self.criteria.keys(), i):
                coalition = tuple(sorted(list(coalition)))
                var = self.variables[coalition]
                val = 1 if solution[var] is True else 0
                cval = CriterionValue(CriteriaSet(coalition), 1)
                cv.append(cval)

        cv = capacities_to_mobius(self.criteria, cv)
        self.model.cv = cv
        self.model.lbda = 1

        # Get profiles
        bpt = PerformanceTable()
        for cp in self.categories_profiles:
            bp = AlternativePerformances(cp.id, {})
            for c in self.criteria:
                xi = sorted(self.x[c.id])
                for xij in xi:
                    var = self.variables[c.id, cp.id, xij]
                    val = solution[var]
                    if val is True:
                        bp.performances[c.id] = xij
            bpt.append(bp)
        self.model.bpt = bpt

    def solve(self):
        sat, solution = self.solver.solve()
        if sat is False:
            return False

        self.__parse_solution(solution)

        return True

if __name__ == "__main__":
    from pymcda.utils import print_pt_and_assignments
    from pymcda.generate import generate_random_mrsort_model
    from pymcda.generate import generate_alternatives
    from pymcda.generate import generate_criteria
    from pymcda.generate import generate_categories
    from pymcda.generate import generate_categories_profiles
    from pymcda.generate import generate_random_performance_table
    from pymcda.electre_tri import MRSort

    # Define the MR-Sort model
    ncriteria = 3
    ncategories = 2

    c = generate_criteria(ncriteria)
    cv = CriteriaValues(CriterionValue(crit.id, float(1) / ncriteria) for crit in c)
    cat = generate_categories(ncategories)
    cps = generate_categories_profiles(cat)
    b1 = AlternativePerformances('b1', {crit.id: 5 for crit in c})
    bpt = PerformanceTable([b1])
    lbda = 0.6
    model = MRSort(c, cv, bpt, lbda, cps)

    # Define the alternatives
    a = generate_alternatives(8)
    a1 = AlternativePerformances('a1', {'c1': 1, 'c2': 1, 'c3': 1})
    a2 = AlternativePerformances('a2', {'c1': 9, 'c2': 1, 'c3': 1})
    a3 = AlternativePerformances('a3', {'c1': 1, 'c2': 9, 'c3': 1})
    a4 = AlternativePerformances('a4', {'c1': 1, 'c2': 1, 'c3': 9})
    a5 = AlternativePerformances('a5', {'c1': 9, 'c2': 9, 'c3': 9})
    a6 = AlternativePerformances('a6', {'c1': 9, 'c2': 9, 'c3': 1})
    a7 = AlternativePerformances('a7', {'c1': 1, 'c2': 9, 'c3': 9})
    a8 = AlternativePerformances('a8', {'c1': 9, 'c2': 1, 'c3': 9})
    pt = PerformanceTable([a1, a2, a3, a4, a5, a6, a7, a8])

    aa = model.pessimist(pt)

    ## random model
    #model = generate_random_mrsort_model(ncriteria, ncategories, 123)
    #a = generate_alternatives(1000)
    #pt = generate_random_performance_table(a, model.criteria)
    #aa = model.pessimist(pt)

    # Learn the parameters
    sat = SatMRSort(model, pt, aa)
    aa2 = model.pessimist(pt)

    # Check that all the alternatives are correctly assigned
    alist = []
    for alt in a:
        if aa(alt.id) != aa2(alt.id):
            alist.append(alt.id)

    if len(alist) == 0:
        print("All the alternatives are correcly assigned")
    else:
       print_pt_and_assignments(alist, None, [aa, aa2], pt)
