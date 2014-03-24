import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
from pymcda.types import *
from pymcda.generate import generate_criteria
from pymcda.generate import generate_categories
from pymcda.generate import generate_categories_profiles
from pymcda.electre_tri import MRSort
from pymcda.learning.mip_mrsort_veto import MipMRSortVC
from pymcda.learning.mip_mrsort import MipMRSort

# Model parameters

## Weights
c = generate_criteria(5)
w1 = CriterionValue('c1', 0.2)
w2 = CriterionValue('c2', 0.2)
w3 = CriterionValue('c3', 0.2)
w4 = CriterionValue('c4', 0.2)
w5 = CriterionValue('c5', 0.2)
w = CriteriaValues([w1, w2, w3, w4, w5])

## Profiles and categories
b1 = AlternativePerformances('b1', {'c1': 10, 'c2': 10, 'c3': 10, 'c4': 10, 'c5': 10})
bpt = PerformanceTable([b1])

cat = generate_categories(2)
cps = generate_categories_profiles(cat)

## Veto thresholds
vb1 = AlternativePerformances('b1', {'c1': 2, 'c2': 2, 'c3': 2, 'c4': 2, 'c5': 2}, 'b1')
v = PerformanceTable([vb1])
vw = w.copy()

model = MRSort(c, w, bpt, 0.6, cps, v, vw, 0.4)

# Altenatives
a1 = AlternativePerformances('a1',   {'c1':  9, 'c2':  9, 'c3':  9, 'c4':  9, 'c5': 11})
a2 = AlternativePerformances('a2',   {'c1':  9, 'c2':  9, 'c3':  9, 'c4': 11, 'c5':  9})
a3 = AlternativePerformances('a3',   {'c1':  9, 'c2':  9, 'c3':  9, 'c4': 11, 'c5': 11})
a4 = AlternativePerformances('a4',   {'c1':  9, 'c2':  9, 'c3': 11, 'c4':  9, 'c5':  9})
a5 = AlternativePerformances('a5',   {'c1':  9, 'c2':  9, 'c3': 11, 'c4':  9, 'c5': 11})
a6 = AlternativePerformances('a6',   {'c1':  9, 'c2':  9, 'c3': 11, 'c4': 11, 'c5':  9})
a7 = AlternativePerformances('a7',   {'c1':  9, 'c2':  9, 'c3': 11, 'c4': 11, 'c5': 11})
a8 = AlternativePerformances('a8',   {'c1':  9, 'c2': 11, 'c3':  9, 'c4':  9, 'c5':  9})
a9 = AlternativePerformances('a9',   {'c1':  9, 'c2': 11, 'c3':  9, 'c4':  9, 'c5': 11})
a10 = AlternativePerformances('a10', {'c1':  9, 'c2': 11, 'c3':  9, 'c4': 11, 'c5':  9})
a11 = AlternativePerformances('a11', {'c1':  9, 'c2': 11, 'c3':  9, 'c4': 11, 'c5': 11})
a12 = AlternativePerformances('a12', {'c1':  9, 'c2': 11, 'c3': 11, 'c4':  9, 'c5':  9})
a13 = AlternativePerformances('a13', {'c1':  9, 'c2': 11, 'c3': 11, 'c4':  9, 'c5': 11})
a14 = AlternativePerformances('a14', {'c1':  9, 'c2': 11, 'c3': 11, 'c4': 11, 'c5':  9})
a15 = AlternativePerformances('a15', {'c1':  9, 'c2': 11, 'c3': 11, 'c4': 11, 'c5': 11})
a16 = AlternativePerformances('a16', {'c1': 11, 'c2':  9, 'c3':  9, 'c4':  9, 'c5':  9})
a17 = AlternativePerformances('a17', {'c1': 11, 'c2':  9, 'c3':  9, 'c4':  9, 'c5': 11})
a18 = AlternativePerformances('a18', {'c1': 11, 'c2':  9, 'c3':  9, 'c4': 11, 'c5':  9})
a19 = AlternativePerformances('a19', {'c1': 11, 'c2':  9, 'c3':  9, 'c4': 11, 'c5': 11})
a20 = AlternativePerformances('a20', {'c1': 11, 'c2':  9, 'c3': 11, 'c4':  9, 'c5':  9})
a21 = AlternativePerformances('a21', {'c1': 11, 'c2':  9, 'c3': 11, 'c4':  9, 'c5': 11})
a22 = AlternativePerformances('a22', {'c1': 11, 'c2':  9, 'c3': 11, 'c4': 11, 'c5':  9})
a23 = AlternativePerformances('a23', {'c1': 11, 'c2':  9, 'c3': 11, 'c4': 11, 'c5': 11})
a24 = AlternativePerformances('a24', {'c1': 11, 'c2': 11, 'c3':  9, 'c4':  9, 'c5':  9})
a25 = AlternativePerformances('a25', {'c1': 11, 'c2': 11, 'c3':  9, 'c4':  9, 'c5': 11})
a26 = AlternativePerformances('a26', {'c1': 11, 'c2': 11, 'c3':  9, 'c4': 11, 'c5':  9})
a27 = AlternativePerformances('a27', {'c1': 11, 'c2': 11, 'c3':  9, 'c4': 11, 'c5': 11})
a28 = AlternativePerformances('a28', {'c1': 11, 'c2': 11, 'c3': 11, 'c4':  9, 'c5':  9})
a29 = AlternativePerformances('a29', {'c1': 11, 'c2': 11, 'c3': 11, 'c4':  9, 'c5': 11})
a30 = AlternativePerformances('a30', {'c1': 11, 'c2': 11, 'c3': 11, 'c4': 11, 'c5':  9})

a31 = AlternativePerformances('a31', {'c1': 11, 'c2': 11, 'c3': 11, 'c4': 11, 'c5':  7})
a32 = AlternativePerformances('a32', {'c1': 11, 'c2': 11, 'c3': 11, 'c4':  7, 'c5': 11})
a33 = AlternativePerformances('a33', {'c1': 11, 'c2': 11, 'c3':  7, 'c4': 11, 'c5': 11})
a34 = AlternativePerformances('a34', {'c1': 11, 'c2':  7, 'c3': 11, 'c4': 11, 'c5': 11})
a35 = AlternativePerformances('a35', {'c1':  7, 'c2': 11, 'c3': 11, 'c4': 11, 'c5': 11})

a36 = AlternativePerformances('a36', {'c1': 11, 'c2': 11, 'c3': 11, 'c4':  7, 'c5':  7})
a37 = AlternativePerformances('a37', {'c1': 11, 'c2': 11, 'c3':  7, 'c4': 11, 'c5':  7})
a38 = AlternativePerformances('a38', {'c1': 11, 'c2':  7, 'c3': 11, 'c4': 11, 'c5':  7})
a39 = AlternativePerformances('a39', {'c1':  7, 'c2': 11, 'c3': 11, 'c4': 11, 'c5':  7})

a40 = AlternativePerformances('a40', {'c1': 11, 'c2': 11, 'c3':  7, 'c4':  7, 'c5': 11})
a41 = AlternativePerformances('a41', {'c1': 11, 'c2':  7, 'c3': 11, 'c4':  7, 'c5': 11})
a42 = AlternativePerformances('a42', {'c1':  7, 'c2': 11, 'c3': 11, 'c4':  7, 'c5': 11})

a43 = AlternativePerformances('a43', {'c1': 11, 'c2':  7, 'c3':  7, 'c4': 11, 'c5': 11})
a44 = AlternativePerformances('a44', {'c1':  7, 'c2': 11, 'c3':  7, 'c4': 11, 'c5': 11})

a45 = AlternativePerformances('a45', {'c1':  7, 'c2':  7, 'c3': 11, 'c4': 11, 'c5': 11})

pt = PerformanceTable([eval("a%d" % i) for i in range(1, 46)])
aa = model.pessimist(pt)
print(aa)

nveto = [model.count_veto_pessimist(eval("a%d" % i)) for i in range(1, 46)]
print("Number of veto effects: %d" % sum(nveto))

model2 = MRSort(c, None, None, None, cps, None, None, None)
#model2.veto_lbda = model.veto_lbda
#model2.veto_weights = model.veto_weights

mip = MipMRSortVC(model2, pt, aa)
#mip = MipMRSort(model2, pt, aa)
mip.solve()

print(model2.cv)
print(model2.bpt)
print(model2.lbda)
print(model2.veto)
print(model2.veto_lbda)
print(model2.veto_weights)

aa2 = model2.pessimist(pt)
for a in aa2:
    if aa[a.id].category_id != a.category_id:
        print(a, aa[a.id])
