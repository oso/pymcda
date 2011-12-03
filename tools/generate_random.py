import sys
sys.path.insert(0, "..")
import random
from mcda.types import alternative, alternatives
from mcda.types import alternative_performances, performance_table
from mcda.types import criterion, criteria

def generate_random_alternatives(number):
    alts = alternatives()
    for i in range(number):
        a = alternative()
        a.id = "a%d" % i
#        a.name = "a%d" % i
        alts.append(a)

    return alts

def generate_random_criteria(number, seed=1234):
    random.seed(seed)

    crits = criteria()
    for i in range(number):
        c = criterion("c%d" % i)
#        c.name = "c%d" %i
        c.weight = random.randint(0,100)
        crits.append(c)

    return crits

def generate_random_performance_table(alts, crits, seed=5678):
    random.seed(seed)

    pt = performance_table()
    for a in alts:
        perfs = {}
        for c in crits:
            perfs[c.id] = random.random()
#            perfs[c.id] = random.randint(0,100)
        ap = alternative_performances(a.id, perfs)
        pt.append(ap)

    return pt

if __name__ == "__main__":
    alts = generate_random_alternatives(10)
    print alts
    crits = generate_random_criteria(5)
    print crits
    pt = generate_random_performance_table(alts, crits)
    print pt
