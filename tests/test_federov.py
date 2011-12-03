import sys
sys.path.insert(0, "..")
import pprint
from mcda.types import alternative, alternatives
from mcda.types import criterion, criteria
from mcda.types import alternative_performances, performance_table
from tools.federov import federov

# Alternatives
a1 = alternative('a1')
a2 = alternative('a2')
a3 = alternative('a3')
a4 = alternative('a4')
a5 = alternative('a5')
a6 = alternative('a6')
a7 = alternative('a7')
a8 = alternative('a8')
a9 = alternative('a9')
a10 = alternative('a10')
a11 = alternative('a11')
a12 = alternative('a12')
a13 = alternative('a13')
a14 = alternative('a14')
a15 = alternative('a15')
a16 = alternative('a16')
a17 = alternative('a17')
a18 = alternative('a18')
a19 = alternative('a19')
a20 = alternative('a20')
a21 = alternative('a21')
a22 = alternative('a22')
a23 = alternative('a23')
a24 = alternative('a24')
a = alternatives([a1, a2, a3, a4, a5, a6, a7, a8,
                  a9, a10, a11, a12, a13, a14, a15, a16,
                  a17, a18, a19, a20, a21, a22, a23, a24])

# Criteria
c1 = criterion('c1', weight=1)
c2 = criterion('c2', weight=1)
c3 = criterion('c3', weight=1)
c = criteria([c1, c2, c3])

# Alternative performances
ap1 = alternative_performances('a1', {'c1': 1, 'c2': 1.2, 'c3': 5.5})
ap2 = alternative_performances('a2', {'c1': 1, 'c2': 1.2, 'c3': 5.1})
ap3 = alternative_performances('a3', {'c1': 1, 'c2': 1.2, 'c3': 4.9})
ap4 = alternative_performances('a4', {'c1': 1, 'c2': 1.2, 'c3': 4.7})
ap5 = alternative_performances('a5', {'c1': 1, 'c2': 1.2, 'c3': 4.3})
ap6 = alternative_performances('a6', {'c1': 1, 'c2': 1.8, 'c3': 5.5})
ap7 = alternative_performances('a7', {'c1': 1, 'c2': 1.8, 'c3': 5.1})
ap8 = alternative_performances('a8', {'c1': 1, 'c2': 1.8, 'c3': 4.7})
ap9 = alternative_performances('a9', {'c1': 1, 'c2': 1.8, 'c3': 4.3})
ap10 = alternative_performances('a10', {'c1': 1, 'c2': 1.8, 'c3': 3.9})
ap11 = alternative_performances('a11', {'c1': 1, 'c2': 1.6, 'c3': 4.1})
ap12 = alternative_performances('a12', {'c1': 1, 'c2': 2.4, 'c3': 5.5})
ap13 = alternative_performances('a13', {'c1': 1, 'c2': 2.4, 'c3': 5.1})
ap14 = alternative_performances('a14', {'c1': 1, 'c2': 2.4, 'c3': 4.7})
ap15 = alternative_performances('a15', {'c1': 1, 'c2': 2.4, 'c3': 4.3})
ap16 = alternative_performances('a16', {'c1': 1, 'c2': 2.4, 'c3': 3.9})
ap17 = alternative_performances('a17', {'c1': 1, 'c2': 2.7, 'c3': 3.9})
ap18 = alternative_performances('a18', {'c1': 1, 'c2': 3.0, 'c3': 5.1})
ap19 = alternative_performances('a19', {'c1': 1, 'c2': 3.0, 'c3': 4.7})
ap20 = alternative_performances('a20', {'c1': 1, 'c2': 3.0, 'c3': 4.3})
ap21 = alternative_performances('a21', {'c1': 1, 'c2': 3.0, 'c3': 3.9})
ap22 = alternative_performances('a22', {'c1': 1, 'c2': 3.6, 'c3': 4.7})
ap23 = alternative_performances('a23', {'c1': 1, 'c2': 3.6, 'c3': 4.3})
ap24 = alternative_performances('a24', {'c1': 1, 'c2': 3.6, 'c3': 3.9})
pt = performance_table([ap1, ap2, ap3, ap4, ap5, ap6, ap7, ap8,
                        ap9, ap10, ap11, ap12, ap13, ap14, ap15, ap16,
                        ap17, ap18, ap19, ap20, ap21, ap22, ap23, ap24])

print "Performance table"
pprint.pprint(pt)

p0_a = [a1, a11, a24, a18]
p0_pt = [ap1, ap11, ap24, ap18]

print "Initial plan"
pprint.pprint(p0_a)
pprint.pprint(p0_pt)

p_a, p_pt = federov(a, c, pt, 4, p0_a, p0_pt)
print "Optimal set"
pprint.pprint(p_a)
pprint.pprint(p_pt)
