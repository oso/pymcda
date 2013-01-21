import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
from mcda.generate import generate_criteria
from mcda.generate import generate_random_criteria_weights
from mcda.generate import generate_random_criteria_values

n = 10000

c = generate_criteria(3)
cw = generate_random_criteria_weights(c)

cids = c.keys()

f = open('data/random_1.txt', 'wb')

for i in range(n):
    cw = generate_random_criteria_weights(c)
    for cid in cids:
        f.write(str(cw[cid].value) + "\t")
    f.write("\n")

f.close()

f = open('data/random_2.txt', 'wb')

for i in range(n):
    cw = generate_random_criteria_values(c)
    cw.normalize()
    for cid in cids:
        f.write(str(cw[cid].value) + "\t")
    f.write("\n")

f.close()
