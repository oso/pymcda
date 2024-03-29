from __future__ import division
import os, sys
from itertools import product
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../../")
import cplex

class MipSnr(object):

    def __init__(self, model, pt, aa, pwcs):
        self.model = model
        self.pt = pt
        self.aa = aa
        self.pwcs = pwcs

        self.bigm = 10
        self.epsilon = 0.0001

        self.ap_min = pt.get_min()
        self.ap_max = pt.get_max()
        self.profiles = self.model.categories_profiles.get_ordered_profiles()
        self.categories = self.model.categories_profiles.get_ordered_categories()

        self.lp = cplex.Cplex()
        self.add_variables()
        self.add_constraints()
        self.add_objective()

    def add_variables(self):
        variables = self.lp.variables

        variables.add(names = ["%s_%s" % (bh, j)
                               for j in self.model.criteria.keys()
                               for bh in self.profiles],
                      lb = [self.ap_min.performances[j] - self.epsilon
                            for j in self.model.criteria.keys()
                            for bh in self.profiles],
                      ub = [self.ap_max.performances[j] + self.epsilon
                            for j in self.model.criteria.keys()
                            for bh in self.profiles])
        variables.add(names = ["delta_%s_%s_%s" % (j, a, bh)
                               for j in self.model.criteria.keys()
                               for a in self.aa.keys()
                               for bh in self.profiles],
                      types = [self.lp.variables.type.binary
                               for j in self.model.criteria.keys()
                               for a in self.aa.keys()
                               for bh in self.profiles])
        variables.add(names = ["lambda"], lb = [0], ub = [1])
        variables.add(names = ["w_%s" % j
                               for j in self.model.criteria.keys()],
                      lb = [0 for j in self.model.criteria.keys()])
        variables.add(names = ["omega_%s_%s_%s" % (j, a, bh)
                               for j in self.model.criteria.keys()
                               for a in self.aa.keys()
                               for bh in self.profiles],
                      lb = [0 for j in self.model.criteria.keys()
                              for a in self.aa.keys()
                              for bh in self.profiles])
        variables.add(names = ["y_%s_%s" % (a, cat)
                               for a in self.aa.keys()
                               for cat in self.categories],
                      types = [self.lp.variables.type.binary
                               for a in self.aa.keys()
                               for cat in self.categories])
        variables.add(names = ["e_%s_%s_%s" % (pwc.a, pwc.b, cat)
                               for pwc in self.pwcs
                               for cat in self.categories],
                      types = [self.lp.variables.type.binary
                               for pwc in self.pwcs
                               for cat in self.categories])
        variables.add(names = ["delta2_%s_%s_%s" % (bh, pwc.a, pwc.b)
                               for bh in self.profiles
                               for pwc in self.pwcs])

    def add_constraints(self):
        constraints = self.lp.linear_constraints

        constraints.add(names = ["wsum"],
                        lin_expr =
                            [
                                [["w_%s" % j
                                  for j in self.model.criteria.keys()],
                                 [1 for j in self.model.criteria.keys()]]
                            ],
                        senses = ["E"],
                        rhs = [1]
                       )

        for j, bh, a in product(self.model.criteria.keys(), self.profiles, self.aa.keys()):
            constraints.add(names = ["dsup_%s_%s_%s" % (j, a, bh)],
                            lin_expr =
                                [
                                 [["delta_%s_%s_%s" % (j, a, bh),
                                   "%s_%s" % (bh, j)],
                                  [self.bigm, 1]]
                                ],
                            senses = ["G"],
                            rhs = [self.pt[a][j] + self.epsilon]
                           )

            constraints.add(names = ["dinf_%s_%s_%s" % (j, a, bh)],
                            lin_expr =
                                [
                                 [["delta_%s_%s_%s" % (j, a, bh),
                                   "%s_%s" % (bh, j)],
                                  [self.bigm, 1]]
                                ],
                            senses = ["L"],
                            rhs = [self.pt[a][j] + self.bigm]
                           )

            constraints.add(names = ["wj1_%s_%s_%s" % (j, a, bh)],
                            lin_expr =
                                [
                                 [["delta_%s_%s_%s" % (j, a, bh),
                                   "omega_%s_%s_%s" % (j, a, bh)],
                                  [1, -1]]
                                ],
                            senses = ["G"],
                            rhs = [0]
                           )

            constraints.add(names = ["wj2_%s_%s_%s" % (j, a, bh)],
                            lin_expr =
                                [
                                 [["w_%s" % j,
                                   "omega_%s_%s_%s" % (j, a, bh)],
                                  [1, -1]]
                                ],
                            senses = ["G"],
                            rhs = [0]
                           )

            constraints.add(names = ["wj3_%s_%s_%s" % (j, a, bh)],
                            lin_expr =
                                [
                                 [["omega_%s_%s_%s" % (j, a, bh),
                                   "delta_%s_%s_%s" % (j, a, bh),
                                   "w_%s" % j],
                                  [1, -1, -1]]
                                ],
                            senses = ["G"],
                            rhs = [-1]
                           )

        lower_profile = [None] + self.profiles
        upper_profile = self.profiles + [None]
        categories_lower_profile = dict(zip(self.categories, lower_profile))
        categories_upper_profile = dict(zip(self.categories, upper_profile))
        for cat, a in product(self.categories, self.aa.keys()):
            bh = categories_lower_profile[cat]
            bhup = categories_upper_profile[cat]

            if bhup is not None:
                constraints.add(names = ["yah1_%s_%s" % (a, cat)],
                                lin_expr =
                                    [
                                     [["omega_%s_%s_%s" % (j, a, bhup)
                                       for j in self.model.criteria.keys()] +
                                       ["lambda"] +
                                       ["y_%s_%s" % (a, cat)],
                                      [1 for j in self.model.criteria.keys()]
                                       + [-1, self.bigm]]
                                    ],
                                senses = ["L"],
                                rhs = [self.bigm - self.epsilon]
                               )

            if bh is not None:
                constraints.add(names = ["yah2_%s_%s" % (a, cat)],
                                lin_expr =
                                    [
                                     [["omega_%s_%s_%s" % (j, a, bh)
                                       for j in self.model.criteria.keys()] +
                                       ["lambda"] +
                                       ["y_%s_%s" % (a, cat)],
                                      [-1 for j in self.model.criteria.keys()]
                                       + [1, self.bigm]]
                                    ],
                                senses = ["L"],
                                rhs = [self.bigm]
                               )

        for a in self.aa.keys():
            constraints.add(names = ["yah3_%s" % a],
                            lin_expr =
                                [
                                 [["y_%s_%s" % (a, cat) for cat in self.categories],
                                  [1 for cat in self.categories]]
                                ],
                            senses = ["E"],
                            rhs = [1]
                           )

        for aa in self.aa.values():
            a = aa.id
            ci = self.categories.index(aa.category_id)

            for i in range(ci):
                bh = self.profiles[i]
                constraints.add(names = ["omega_inf_%s_%s" % (a, bh)],
                                lin_expr =
                                    [
                                     [["omega_%s_%s_%s" % (j, a, bh)
                                       for j in self.model.criteria.keys()] +
                                       ["lambda"],
                                      [1 for j in self.model.criteria.keys()]
                                       + [-1]]
                                    ],
                                senses = ["G"],
                                rhs = [0]
                               )

            for i in range(ci, len(self.categories) - 1):
                bh = self.profiles[i]
                constraints.add(names = ["omega_sup_%s_%s" % (a, bh)],
                                lin_expr =
                                    [
                                     [["omega_%s_%s_%s" % (j, a, bh)
                                       for j in self.model.criteria.keys()] +
                                       ["lambda"],
                                      [1 for j in self.model.criteria.keys()]
                                       + [-1]]
                                    ],
                                senses = ["L"],
                                rhs = [-self.epsilon]
                               )

        for pwc in self.pwcs:
            constraints.add(names = ["dom_%s_%s" % (pwc.a, pwc.b)],
                            lin_expr =
                                [
                                 [["y_%s_%s" % (pwc.b, cat)
                                   for cat in self.categories[1:]] +
                                  ["y_%s_%s" % (pwc.a, cat)
                                   for cat in self.categories[1:]],
                                  [i for i in range(2, len(self.categories) + 1)]
                                   + [-i for i in range(2, len(self.categories) + 1)]]
                                ],
                            senses = ["L"],
                            rhs = [0])

            for cat in self.categories:
                bh = categories_lower_profile[cat]
                bhup = categories_upper_profile[cat]
                constraints.add(names = ["eps1_%s_%s_%s" % (pwc.a, pwc.b, cat)],
                                lin_expr =
                                    [
                                     [["e_%s_%s_%s" % (pwc.a, pwc.b, cat),
                                       "y_%s_%s" % (pwc.a, cat)],
                                      [1, -1]]
                                    ],
                                senses = ["L"],
                                rhs = [0])

                constraints.add(names = ["eps2_%s_%s_%s" % (pwc.a, pwc.b, cat)],
                                lin_expr =
                                    [
                                     [["e_%s_%s_%s" % (pwc.a, pwc.b, cat),
                                       "y_%s_%s" % (pwc.b, cat)],
                                      [1, -1]]
                                    ],
                                senses = ["L"],
                                rhs = [0])

                constraints.add(names = ["eps3_%s_%s_%s" % (pwc.a, pwc.b, cat)],
                                lin_expr =
                                    [
                                     [["e_%s_%s_%s" % (pwc.a, pwc.b, cat),
                                       "y_%s_%s" % (pwc.a, cat),
                                       "y_%s_%s" % (pwc.b, cat)],
                                      [-1, 1, 1]]
                                    ],
                                senses = ["L"],
                                rhs = [1])

                if bh is not None:
                    constraints.add(names = ["delta2a_%s_%s_%s" % (bh, pwc.a, pwc.b)],
                                    lin_expr =
                                        [
                                         [["delta2_%s_%s_%s" % (bh, pwc.a, pwc.b)] +
                                          ["omega_%s_%s_%s" % (j, pwc.a, bh)
                                           for j in self.model.criteria.keys()] +
                                          ["omega_%s_%s_%s" % (j, pwc.b, bh)
                                           for j in self.model.criteria.keys()],
                                         [1] +
                                         [-1 for j in self.model.criteria.keys()] +
                                         [1 for j in self.model.criteria.keys()]]
                                        ],
                                    senses = ["E"],
                                    rhs = [0])

                    constraints.add(names = ["delta2b_%s_%s_%s" % (bh, pwc.a, pwc.b)],
                                    lin_expr =
                                        [
                                         [["e_%s_%s_%s" % (pwc.a, pwc.b, cat),
                                           "delta2_%s_%s_%s" % (bh, pwc.a, pwc.b)],
                                          [self.bigm, -1]]
                                        ],
                                    senses = ["L"],
                                    rhs = [self.bigm])

                    if bhup is not None:
                        constraints.add(names = ["delta2c_%s_%s_%s" % (bh, pwc.a, pwc.b)],
                                        lin_expr =
                                            [
                                             [["e_%s_%s_%s" % (pwc.a, pwc.b, cat),
                                               "delta2_%s_%s_%s" % (bh, pwc.a, pwc.b),
                                               "delta2_%s_%s_%s" % (bhup, pwc.a, pwc.b)],
                                              [self.bigm, -0.5 * self.bigm, -1]]
                                            ],
                                        senses = ["L"],
                                        rhs = [self.bigm])
                else:
                    constraints.add(names = ["delta2d_%s_%s_%s" % (bhup, pwc.a, pwc.b)],
                                    lin_expr =
                                        [
                                         [["e_%s_%s_%s" % (pwc.a, pwc.b, cat),
                                           "delta2_%s_%s_%s" % (bhup, pwc.a, pwc.b)],
                                          [self.bigm, -1]]
                                        ],
                                    senses = ["L"],
                                    rhs = [self.bigm])


    def add_objective(self):
        return

    def solve(self):
        self.lp.solve()
#        print(self.lp.solution.get_values('e_%s_%s_%s' % ("c", "d", "cat2")))
        print(self.lp.solution.get_values('e_%s_%s_%s' % ("a", "b", "cat1")))
        print(self.lp.solution.get_values('e_%s_%s_%s' % ("b", "c", "cat1")))
        print(self.lp.solution.get_values('e_%s_%s_%s' % ("c", "d", "cat1")))
        print(self.lp.solution.get_values('e_%s_%s_%s' % ("d", "e", "cat1")))
        print(self.lp.solution.get_values('e_%s_%s_%s' % ("e", "f", "cat1")))
        print(self.lp.solution.get_values('e_%s_%s_%s' % ("a", "b", "cat2")))
        print(self.lp.solution.get_values('e_%s_%s_%s' % ("b", "c", "cat2")))
        print(self.lp.solution.get_values('e_%s_%s_%s' % ("c", "d", "cat2")))
        print(self.lp.solution.get_values('e_%s_%s_%s' % ("d", "e", "cat2")))
        print(self.lp.solution.get_values('e_%s_%s_%s' % ("e", "f", "cat2")))
        print(self.lp.solution.get_values('e_%s_%s_%s' % ("a", "b", "cat3")))
        print(self.lp.solution.get_values('e_%s_%s_%s' % ("b", "c", "cat3")))
        print(self.lp.solution.get_values('e_%s_%s_%s' % ("c", "d", "cat3")))
        print(self.lp.solution.get_values('e_%s_%s_%s' % ("d", "e", "cat3")))
        print(self.lp.solution.get_values('e_%s_%s_%s' % ("e", "f", "cat3")))

        status = self.lp.solution.get_status()
        if status != self.lp.solution.status.MIP_optimal:
            raise RuntimeError("Solver status: %s" % status)

        cvs = CriteriaValues()
        for j in self.model.criteria.keys():
            cv = CriterionValue()
            cv.id = j
            cv.value = self.lp.solution.get_values('w_' + j)
            cvs.append(cv)
        self.model.cv = cvs

        self.model.lbda = round(self.lp.solution.get_values("lambda"), 5)

        pt = PerformanceTable()
        for bh in self.profiles:
            ap = AlternativePerformances(bh)
            for j in self.model.criteria.keys():
                perf = self.lp.solution.get_values("%s_%s" % (bh, j))
                ap.performances[j] = round(perf, 5)
            pt.append(ap)
        self.model.bpt = pt

#        categories_cvs = {}
#        for h, cat in enumerate(self.model.categories):
#            cvs = CriteriaValues()
#            for j in self.model.criteria.keys():
#                cv = CriterionValue()
#                cv.id = j
#                cv.value = self.lp.solution.get_values("omega_%s_%" % (j, self.profiles[h]))
#                cvs.append(cv)
#            categories_cvs[cat] = cvs
#        self.model.categories_profiles = categories_cvs


if __name__ == "__main__":
    from pymcda.types import CriteriaValues, CriterionValue
    from pymcda.types import AlternativePerformances
    from pymcda.types import PerformanceTable
    from pymcda.types import Criterion, Criteria
    from pymcda.types import CategoryProfile, CategoriesProfiles
    from pymcda.types import Limits
    from pymcda.types import PairwiseRelations
    from pymcda.snr import SortAndRank

    ap1 = AlternativePerformances("a", {"c1": 7, "c2": 7, "c3": 7})
    ap2 = AlternativePerformances("b", {"c1": 8, "c2": 4, "c3": 8})
    ap3 = AlternativePerformances("c", {"c1": 8, "c2": 5, "c3": 4})
    ap4 = AlternativePerformances("d", {"c1": 4, "c2": 4, "c3": 9})
    ap5 = AlternativePerformances("e", {"c1": 5, "c2": 2, "c3": 1})
    ap6 = AlternativePerformances("f", {"c1": 1, "c2": 2, "c3": 6})
    pt = PerformanceTable([ap1, ap2, ap3, ap4, ap5, ap6])

    c1 = Criterion("c1")
    c2 = Criterion("c2")
    c3 = Criterion("c3")
    criteria = Criteria([c1, c2, c3])

    bp1 = AlternativePerformances("b1", {"c1": 3, "c2": 3, "c3": 3})
    bp2 = AlternativePerformances("b2", {"c1": 6, "c2": 6, "c3": 6})
    bpt = PerformanceTable([bp1, bp2])

    cv1 = CriterionValue("c1", 1)
    cv2 = CriterionValue("c2", 1)
    cv3 = CriterionValue("c3", 1)
    cvs = CriteriaValues([cv1, cv2, cv3])

    lbda = 2

    cpb1 = CategoryProfile("b1", Limits("cat1", "cat2"))
    cpb2 = CategoryProfile("b2", Limits("cat2", "cat3"))
    cpbs = CategoriesProfiles([cpb1, cpb2])

    cvs1 = CriteriaValues([CriterionValue("c1", 1),
                           CriterionValue("c2", 1),
                           CriterionValue("c3", 1)])
    cvs2 = CriteriaValues([CriterionValue("c1", 1),
                           CriterionValue("c2", 1),
                           CriterionValue("c3", 1)])
    cvs3 = CriteriaValues([CriterionValue("c1", 1),
                           CriterionValue("c2", 1),
                           CriterionValue("c3", 1)])
#    cvs1 = CriteriaValues([CriterionValue("c1", 40),
#                           CriterionValue("c2", 25),
#                           CriterionValue("c3", 35)])
#    cvs2 = CriteriaValues([CriterionValue("c1", 35),
#                           CriterionValue("c2", 40),
#                           CriterionValue("c3", 25)])
#    cvs3 = CriteriaValues([CriterionValue("c1", 25),
#                           CriterionValue("c2", 35),
#                           CriterionValue("c3", 40)])
    categories_cvs = {"cat1": cvs1, "cat2": cvs2, "cat3": cvs3}

    snr = SortAndRank(criteria, cvs, bpt, lbda, cpbs, categories_cvs)
    print(snr.cv)

    pwc1 = snr.compare(ap1, ap2)
    pwc2 = snr.compare(ap2, ap3)
    pwc3 = snr.compare(ap3, ap4)
    pwc4 = snr.compare(ap4, ap5)
    pwc5 = snr.compare(ap5, ap6)
    pwcs = PairwiseRelations([pwc1, pwc2, pwc3, pwc4, pwc5])
    print(pwcs)

    print(pt)
    print(bpt)
    aa = snr.get_assignments(pt)
    print(aa)

    mip = MipSnr(snr, pt, aa, pwcs)
    mip.solve()

    print(snr.bpt)
    print(snr.cv)
    print(snr.lbda)
    print(pt)
    aa = snr.get_assignments(pt)
    pwc1 = snr.compare(ap1, ap2)
    pwc2 = snr.compare(ap2, ap3)
    pwc3 = snr.compare(ap3, ap4)
    pwc4 = snr.compare(ap4, ap5)
    pwc5 = snr.compare(ap5, ap6)
    pwcs = PairwiseRelations([pwc1, pwc2, pwc3, pwc4, pwc5])
    print(pwcs)
    print(aa)
