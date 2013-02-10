import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
import pprint
import matplotlib.pyplot as plt
from pymcda.types import Alternative, Alternatives
from pymcda.types import Criterion, Criteria
from pymcda.types import AlternativePerformances, PerformanceTable
from tools.federov import generate_init_plan, federov

def plot(pt, p_pt):
    xs = []
    ys = []
    x = []
    y = []
    for ap in pt:
        xi = ap('c2')
        yi = ap('c3')
        if ap in p_pt:
            xs.append(xi)
            ys.append(yi)
        else:
            x.append(xi)
            y.append(yi)

    plt.title('T=a+b1*x1+b2*x2+b12*x1*x2')
    plt.plot(x, y, 'bo')
    plt.plot(xs, ys, 'ro')
    plt.axis([0.6, 4.2, 3.5, 5.9])
    plt.show()

# Alternatives
a1 = Alternative('a1')
a2 = Alternative('a2')
a3 = Alternative('a3')
a4 = Alternative('a4')
a5 = Alternative('a5')
a6 = Alternative('a6')
a7 = Alternative('a7')
a8 = Alternative('a8')
a9 = Alternative('a9')
a10 = Alternative('a10')
a11 = Alternative('a11')
a12 = Alternative('a12')
a13 = Alternative('a13')
a14 = Alternative('a14')
a15 = Alternative('a15')
a16 = Alternative('a16')
a17 = Alternative('a17')
a18 = Alternative('a18')
a19 = Alternative('a19')
a20 = Alternative('a20')
a21 = Alternative('a21')
a22 = Alternative('a22')
a23 = Alternative('a23')
a24 = Alternative('a24')
a = Alternatives([a1, a2, a3, a4, a5, a6, a7, a8,
                  a9, a10, a11, a12, a13, a14, a15, a16,
                  a17, a18, a19, a20, a21, a22, a23, a24])

# Criteria
c1 = Criterion('c1', weight=1)
c2 = Criterion('c2', weight=1)
c3 = Criterion('c3', weight=1)
c = Criteria([c1, c2, c3])

# Alternative performances
ap1 = AlternativePerformances('a1', {'c1': 1, 'c2': 1.2, 'c3': 5.5})
ap2 = AlternativePerformances('a2', {'c1': 1, 'c2': 1.2, 'c3': 5.1})
ap3 = AlternativePerformances('a3', {'c1': 1, 'c2': 1.2, 'c3': 4.9})
ap4 = AlternativePerformances('a4', {'c1': 1, 'c2': 1.2, 'c3': 4.7})
ap5 = AlternativePerformances('a5', {'c1': 1, 'c2': 1.2, 'c3': 4.3})
ap6 = AlternativePerformances('a6', {'c1': 1, 'c2': 1.8, 'c3': 5.5})
ap7 = AlternativePerformances('a7', {'c1': 1, 'c2': 1.8, 'c3': 5.1})
ap8 = AlternativePerformances('a8', {'c1': 1, 'c2': 1.8, 'c3': 4.7})
ap9 = AlternativePerformances('a9', {'c1': 1, 'c2': 1.8, 'c3': 4.3})
ap10 = AlternativePerformances('a10', {'c1': 1, 'c2': 1.8, 'c3': 3.9})
ap11 = AlternativePerformances('a11', {'c1': 1, 'c2': 1.5, 'c3': 4.1})
ap12 = AlternativePerformances('a12', {'c1': 1, 'c2': 2.4, 'c3': 5.5})
ap13 = AlternativePerformances('a13', {'c1': 1, 'c2': 2.4, 'c3': 5.1})
ap14 = AlternativePerformances('a14', {'c1': 1, 'c2': 2.4, 'c3': 4.7})
ap15 = AlternativePerformances('a15', {'c1': 1, 'c2': 2.4, 'c3': 4.3})
ap16 = AlternativePerformances('a16', {'c1': 1, 'c2': 2.4, 'c3': 3.9})
ap17 = AlternativePerformances('a17', {'c1': 1, 'c2': 2.7, 'c3': 3.9})
ap18 = AlternativePerformances('a18', {'c1': 1, 'c2': 3.0, 'c3': 5.1})
ap19 = AlternativePerformances('a19', {'c1': 1, 'c2': 3.0, 'c3': 4.7})
ap20 = AlternativePerformances('a20', {'c1': 1, 'c2': 3.0, 'c3': 4.3})
ap21 = AlternativePerformances('a21', {'c1': 1, 'c2': 3.0, 'c3': 3.9})
ap22 = AlternativePerformances('a22', {'c1': 1, 'c2': 3.6, 'c3': 4.7})
ap23 = AlternativePerformances('a23', {'c1': 1, 'c2': 3.6, 'c3': 4.3})
ap24 = AlternativePerformances('a24', {'c1': 1, 'c2': 3.6, 'c3': 3.9})
pt = PerformanceTable([ap1, ap2, ap3, ap4, ap5, ap6, ap7, ap8,
                        ap9, ap10, ap11, ap12, ap13, ap14, ap15, ap16,
                        ap17, ap18, ap19, ap20, ap21, ap22, ap23, ap24])

print "Performance table"
pprint.pprint(pt)

print "Initial plan"
p0_a, p0_pt = generate_init_plan(a, pt, 4)
pprint.pprint(p0_a)
pprint.pprint(p0_pt)
plot(pt, p0_pt)

p_a, p_pt = federov(a, c, pt, 4, p0_a, p0_pt)
print "Optimal set"
pprint.pprint(p_a)
pprint.pprint(p_pt)
plot(pt, p_pt)
