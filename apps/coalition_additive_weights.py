from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
from pymcda.types import CriteriaSet
from pymcda.types import PerformanceTable, AlternativePerformances
from pymcda.types import AlternativeAssignment, AlternativesAssignments
from pymcda.utils import powerset

fmin1 = [CriteriaSet('c1', 'c2'), CriteriaSet('c1', 'c3'),
         CriteriaSet('c2', 'c4'), CriteriaSet('c3', 'c4')]
gmax1 = [CriteriaSet('c2', 'c3'), CriteriaSet('c1', 'c4')]

fmin2 = [CriteriaSet('c1', 'c2'), CriteriaSet('c1', 'c3'),
         CriteriaSet('c2', 'c4')]
gmax2 = [CriteriaSet('c2', 'c3'), CriteriaSet('c1', 'c4'),
         CriteriaSet('c3', 'c4')]

fmin3 = [CriteriaSet('c1', 'c2'), CriteriaSet('c1', 'c3'),
         CriteriaSet('c3', 'c4')]
gmax3 = [CriteriaSet('c2', 'c3'), CriteriaSet('c1', 'c4'),
         CriteriaSet('c2', 'c4')]

fmin4 = [CriteriaSet('c1', 'c2'), CriteriaSet('c2', 'c3'),
         CriteriaSet('c1', 'c4'), CriteriaSet('c3', 'c4')]
gmax4 = [CriteriaSet('c1', 'c3'), CriteriaSet('c2', 'c4')]

fmin5 = [CriteriaSet('c1', 'c2'), CriteriaSet('c2', 'c3'),
         CriteriaSet('c1', 'c4')]
gmax5 = [CriteriaSet('c1', 'c3'), CriteriaSet('c2', 'c4'),
         CriteriaSet('c3', 'c4')]

fmin6 = [CriteriaSet('c1', 'c2'), CriteriaSet('c2', 'c3'),
         CriteriaSet('c3', 'c4')]
gmax6 = [CriteriaSet('c1', 'c3'), CriteriaSet('c1', 'c4'),
         CriteriaSet('c2', 'c4')]

fmin7 = [CriteriaSet('c1', 'c2'), CriteriaSet('c1', 'c4'),
         CriteriaSet('c3', 'c4')]
gmax7 = [CriteriaSet('c1', 'c3'), CriteriaSet('c2', 'c3'),
         CriteriaSet('c2', 'c4')]

fmin8 = [CriteriaSet('c1', 'c2'), CriteriaSet('c2', 'c4'),
         CriteriaSet('c3', 'c4')]
gmax8 = [CriteriaSet('c1', 'c3'), CriteriaSet('c2', 'c3'),
         CriteriaSet('c1', 'c4')]

fmin9 = [CriteriaSet('c1', 'c2'), CriteriaSet('c3', 'c4')]
gmax9 = [CriteriaSet('c1', 'c3'), CriteriaSet('c2', 'c3'),
         CriteriaSet('c1', 'c4'), CriteriaSet('c2', 'c4')]

fmin10 = [CriteriaSet('c1', 'c3'), CriteriaSet('c2', 'c3'),
          CriteriaSet('c1', 'c4'), CriteriaSet('c2', 'c4')]
gmax10 = [CriteriaSet('c1', 'c2'), CriteriaSet('c3', 'c4')]

fmin11 = [CriteriaSet('c1', 'c3'), CriteriaSet('c2', 'c3'),
          CriteriaSet('c1', 'c4')]
gmax11 = [CriteriaSet('c1', 'c2'), CriteriaSet('c2', 'c4'),
          CriteriaSet('c3', 'c4')]

fmin12 = [CriteriaSet('c1', 'c3'), CriteriaSet('c2', 'c3'),
          CriteriaSet('c2', 'c4')]
gmax12 = [CriteriaSet('c1', 'c2'), CriteriaSet('c1', 'c4'),
          CriteriaSet('c3', 'c4')]

fmin13 = [CriteriaSet('c1', 'c3'), CriteriaSet('c1', 'c4'),
          CriteriaSet('c2', 'c4')]
gmax13 = [CriteriaSet('c1', 'c2'), CriteriaSet('c2', 'c3'),
          CriteriaSet('c3', 'c4')]

fmin14 = [CriteriaSet('c1', 'c3'), CriteriaSet('c2', 'c4'),
          CriteriaSet('c3', 'c4')]
gmax14 = [CriteriaSet('c1', 'c2'), CriteriaSet('c2', 'c3'),
          CriteriaSet('c1', 'c4')]

fmin15 = [CriteriaSet('c1', 'c3'), CriteriaSet('c2', 'c4')]
gmax15 = [CriteriaSet('c1', 'c2'), CriteriaSet('c2', 'c3'),
          CriteriaSet('c1', 'c4'), CriteriaSet('c3', 'c4')]

fmin16 = [CriteriaSet('c2', 'c3'), CriteriaSet('c1', 'c4'),
          CriteriaSet('c2', 'c4')]
gmax16 = [CriteriaSet('c1', 'c2'), CriteriaSet('c1', 'c3'),
          CriteriaSet('c3', 'c4')]

fmin17 = [CriteriaSet('c2', 'c3'), CriteriaSet('c1', 'c4'),
          CriteriaSet('c3', 'c4')]
gmax17 = [CriteriaSet('c1', 'c2'), CriteriaSet('c1', 'c3'),
          CriteriaSet('c2', 'c4')]

fmin18 = [CriteriaSet('c2', 'c3'), CriteriaSet('c1', 'c4')]
gmax18 = [CriteriaSet('c1', 'c2'), CriteriaSet('c1', 'c3'),
          CriteriaSet('c2', 'c4'), CriteriaSet('c3', 'c4')]
fmins = [fmin1, fmin2, fmin3, fmin4, fmin5, fmin6, fmin7, fmin8, fmin9,
         fmin10, fmin11, fmin12, fmin13, fmin14, fmin15, fmin16, fmin17,
         fmin18]

def generate_binary_performance_table_and_assignments(criteria,
                                                      categories, fmins):
    cids = list(criteria.keys())
    cats = categories.get_ordered_categories()
    aa = AlternativesAssignments()
    pt = PerformanceTable()
    i = 1
    for coalition in powerset(cids):
        if set(coalition) == set({}) or set(coalition) == set(cids):
            continue

        aid = "a%d" % i
        ap = AlternativePerformances(aid, {c: 1 if c in coalition else 0
                                           for c in cids})
        pt.append(ap)

        cat = cats[0]
        for fmin in fmins:
            if fmin.issubset(set(coalition)) is True:
                cat = cats[1]
                break

        aa.append(AlternativeAssignment(aid, cat))

        i += 1

    return pt, aa

if __name__ == "__main__":
    from pymcda.generate import generate_criteria
    from pymcda.generate import generate_categories

    criteria = generate_criteria(4)
    categories = generate_categories(2)
    pt, aa =  generate_binary_performance_table_and_assignments(criteria,
                                                                categories,
                                                                fmin1)
    print(pt)
    print(aa)
