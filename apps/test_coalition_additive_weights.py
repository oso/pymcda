import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
import bz2
from pymcda.types import *
from pymcda.generate import generate_criteria
from pymcda.generate import generate_categories
from pymcda.generate import generate_categories_profiles
from pymcda.electre_tri import MRSort
from pymcda.learning.mip_mrsort_weights import MipMRSortWeights
from pymcda.learning.mip_mrsort_mobius import MipMRSortMobius
from pymcda.utils import print_pt_and_assignments
from coalition_additive_weights import generate_binary_performance_table_and_assignments

f = bz2.BZ2File(sys.argv[1])

tree = ElementTree.parse(f)
root = tree.getroot()

xmcda_criteria = root.find(".//criteria")
criteria = Criteria().from_xmcda(xmcda_criteria)

xmcda_csets = root.findall(".//criteriaSets")
f.close()

## Weights
w = CriteriaValues()
for c in criteria:
    w.append(CriterionValue(c.id, 0.2))

## Profiles and categories
bp1 = AlternativePerformances('b1', {c.id: 0.5 for c in criteria})
bpt = PerformanceTable([bp1])
cat = generate_categories(2, names = ['good', 'bad'])
cps = generate_categories_profiles(cat)

## Model
model = MRSort(c, w, bpt, 0.6, cps)

fmins = []
results = {}
for i, xmcda in enumerate(xmcda_csets):
    result = {}
    fmin = CriteriaSets().from_xmcda(xmcda)
    fmins.append(fmin)
    print("\n%d. Fmin: %s" % (i + 1, ', '.join("%s" % f for f in fmin)))
    pt, aa = generate_binary_performance_table_and_assignments(criteria, cat,
                                                               fmin)
    aa.id = 'aa'
    a = Alternatives([Alternative(a.id) for a in aa])

    model = MRSort(criteria, None, bpt, None, cps)
    mip = MipMRSortWeights(model, pt, aa)
    obj = mip.solve()
    aa2 = model.pessimist(pt)
    aa2.id = 'aa_add'
    print("MipMRSortWeights: Objective: %d (/%d)" % (obj, len(aa)))
    anok = [a.id for a in aa if a.category_id != aa2[a.id].category_id]
    print("Alternative not restored: %s" % ','.join("%s" % a for a in anok))
    print(model.cv)
    print("lambda: %s" % model.lbda)
    result['obj_weights'] = obj

    mip = MipMRSortMobius(model, pt, aa)
    obj = mip.solve()
    aa3 = model.pessimist(pt)
    aa3.id = 'aa_capa'
    print("MipMRSortMobius:  Objective: %d (/%d)" % (obj, len(aa)))
    anok = [a.id for a in aa if a.category_id != aa3[a.id].category_id]
    print("Alternative not restored: %s" % ','.join("%s" % a for a in anok))
    print(model.cv)
    print("lambda: %s" % model.lbda)
    result['obj_capa'] = obj

    a = Alternatives([Alternative(a.id) for a in aa])
    print_pt_and_assignments(a, criteria, [aa, aa2, aa3], pt)

    results[i] = result

maxlen = max([len(', '.join("%s" % f for f in fmin)) for fmin in fmins])
print("\n%*s obj_weights obj_capa" % (maxlen, "Fmin"))
for i, result in results.items():
    print("%*s %*s %*s" % (maxlen, ', '.join("%s" % f for f in fmins[i]),
                           len('obj_weights'), result['obj_weights'],
                           len('obj_capa'), result['obj_capa']))
