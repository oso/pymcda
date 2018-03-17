#!/usr/bin/env python2

import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")

from itertools import combinations

from pymcda.types import PerformanceTable
from pymcda.types import AlternativePerformances
from pymcda.types import AlternativesAssignments
from pymcda.types import CriteriaValues, CriterionValue
from pymcda.types import AlternativePerformances
from pymcda.types import PerformanceTable
from pymcda.types import AlternativeAssignment

from pymcda.generate import generate_random_mrsort_model
from pymcda.generate import generate_alternatives
from pymcda.generate import generate_criteria
from pymcda.generate import generate_categories
from pymcda.generate import generate_categories_profiles
from pymcda.generate import generate_random_performance_table

from pymcda.utils import print_pt_and_assignments
from pymcda.utils import powerset

from pymcda.electre_tri import MRSort

import pycryptosat

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

print_pt_and_assignments([alt.id for alt in a], None, [aa], pt)

# Learn the parameters
class MRSortSAT():

    def __init__(self, criteria, categories, categories_profiles,
                 performance_table, assignments):
        self.criteria = criteria
        self.categories = categories
        self.categories_profiles = categories_profiles
        self.performance_table = performance_table
        self.assignments = assignments

        self.__update_sat()

    def __add_variable(self, name):
        self.nvariables += 1
        self.variables[name] = self.nvariables
        print(self.nvariables, name)

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
                print(coalition, v2)
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

    def __parse_solution(self):
        for c in self.criteria:
            for cp in self.categories_profiles:
                xi = sorted(self.x[c.id])
                for xij in xi:
                    print(xij)

    def solve(self):
        sat, solution = self.solver.solve()
        if sat is False:
            return False

        for i in range(1, len(solution)):
            print(i, solution[i])
        self.__parse_solution()

        return True

sat = MRSortSAT(c, cat, cps, pt, aa)
print(sat.solve())
