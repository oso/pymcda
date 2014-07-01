import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
from pymcda.types import *
from pymcda.generate import generate_criteria
from pymcda.generate import generate_categories
from pymcda.generate import generate_categories_profiles
from pymcda.electre_tri import MRSort
from pymcda.learning.mip_mrsort_weights import MipMRSortWeights
from pymcda.learning.mip_mrsort_mobius import MipMRSortMobius
from pymcda.utils import print_pt_and_assignments
from coalition_additive_weights import generate_binary_performance_table_and_assignments
from coalition_additive_weights import fmins

## Weights
c = generate_criteria(4)
w1 = CriterionValue('c1', 0.2)
w2 = CriterionValue('c2', 0.2)
w3 = CriterionValue('c3', 0.2)
w4 = CriterionValue('c4', 0.2)
w = CriteriaValues([w1, w2, w3, w4])

## Profiles and categories
bp1 = AlternativePerformances('b1',
                              {'c1': 0.5, 'c2': 0.5, 'c3': 0.5, 'c4': 0.5})
bpt = PerformanceTable([bp1])
cat = generate_categories(2, names = ['bad', 'good'])
cps = generate_categories_profiles(cat)

## Model
model = MRSort(c, w, bpt, 0.6, cps)

results = {}
for i, fmin in enumerate(fmins):
    result = {}
    print("\n%d. Fmin: %s" % (i + 1, ', '.join("%s" % f for f in fmin)))
    pt, aa = generate_binary_performance_table_and_assignments(c, cat, fmin)
    a = Alternatives([Alternative(a.id) for a in aa])
    print_pt_and_assignments(a, c, [aa], pt)

    model = MRSort(c, None, bpt, None, cps)
    mip = MipMRSortWeights(model, pt, aa)
    obj = mip.solve()
    aa2 = model.pessimist(pt)
    print("MipMRSortWeights: Objective: %d (/%d)" % (obj, len(aa)))
    print(model.cv)
    print("lambda: %s" % model.lbda)
    result['obj_weights'] = obj

    mip = MipMRSortMobius(model, pt, aa)
    obj = mip.solve()
    aa3 = model.pessimist(pt)
    print("MipMRSortMobius:  Objective: %d (/%d)" % (obj, len(aa)))
    print(model.cv)
    print("lambda: %s" % model.lbda)
    result['obj_capa'] = obj

    a = Alternatives([Alternative(a.id) \
                      for a in aa
                      if a.category_id != aa2[a.id].category_id]
                      or a.category_id != aa3[a.id].category_id)
    print_pt_and_assignments(a, c, [aa, aa2, aa3], pt)

    results[i] = result

maxlen = max([len(', '.join("%s" % f for f in fmin)) for fmin in fmins])
print("\n%*s obj_weights obj_capa" % (maxlen, "Fmin"))
for i, result in results.items():
    print("%*s %*s %*s" % (maxlen, ', '.join("%s" % f for f in fmins[i]),
                           len('obj_weights'), result['obj_weights'],
                           len('obj_capa'), result['obj_capa']))
