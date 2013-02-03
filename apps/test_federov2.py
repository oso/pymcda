import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
import pprint
import matplotlib.pyplot as plt
from pymcda.types import alternative, alternatives
from pymcda.types import criterion, criteria
from pymcda.types import alternative_performances, performance_table
from pymcda.generate import generate_alternatives
from pymcda.generate import generate_criteria
from pymcda.generate import generate_random_performance_table
from tools.federov import generate_init_plan, federov

def plot(pt, p_pt):
    xs = []
    ys = []
    x = []
    y = []
    for ap in pt:
        xi = ap('c1')
        yi = ap('c2')
        if ap in p_pt:
            xs.append(xi)
            ys.append(yi)
        else:
            x.append(xi)
            y.append(yi)
    
    plt.plot(x, y, 'bo')
    plt.plot(xs, ys, 'ro')
    plt.show()

# Alternatives
a = generate_alternatives(100)

# Criteria
c = generate_criteria(2)
#c.append(criterion('c3', weight=1))

# Alternative performances
pt = generate_random_performance_table(a, c)
for ap in pt:
    ap.performances['c3'] = 1

# Initial plan
p0_a, p0_pt = generate_init_plan(a, pt, 10)

print "Initial plan"
pprint.pprint(p0_a)
pprint.pprint(p0_pt)
plot(pt, p0_pt)

p_a, p_pt = federov(a, c, pt, 10, p0_a, p0_pt)
print "Optimal set"
pprint.pprint(p_a)
pprint.pprint(p_pt)

plot(pt, p_pt)
