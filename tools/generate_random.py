import sys
sys.path.insert(0, "..")
import random
from mcda.types import alternative, alternatives
from mcda.types import alternative_performances, performance_table
from mcda.types import criterion, criteria
from mcda.types import criterion_value, criteria_values

def generate_random_alternatives(number):
    alts = alternatives()
    for i in range(number):
        a = alternative()
        a.id = "a%d" % (i+1)
        alts.append(a)

    return alts

def generate_random_criteria(number, seed=None):
    if seed is not None:
        random.seed(seed)

    crits = criteria()
    for i in range(number):
        c = criterion("c%d" % (i+1))
        crits.append(c)

    return crits

def generate_random_criteria_values(crits, seed=None):
    if seed is not None:
        random.seed(seed)

    cvals = criteria_values()
    for c in crits:
        cval = criterion_value()
        cval.criterion_id = c.id
        cval.value = random.random()
        cvals.append(cval)

    return cvals

def generate_random_performance_table(alts, crits, seed=None):
    if seed is not None:
        random.seed(seed)

    pt = performance_table()
    for a in alts:
        perfs = {}
        for c in crits:
            perfs[c.id] = random.random()
        ap = alternative_performances(a.id, perfs)
        pt.append(ap)

    return pt

if __name__ == "__main__":
    alts = generate_random_alternatives(10)
    print(alts)
    crits = generate_random_criteria(5)
    print(crits)
    cv = generate_random_criteria_values(crits)
    print(cv)
    pt = generate_random_performance_table(alts, crits)
    print(pt)
