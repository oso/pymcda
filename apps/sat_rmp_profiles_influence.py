from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")

from pymcda.types import Alternative
from pymcda.types import PairwiseRelations
from pymcda.types import PerformanceTable
from pymcda.generate import generate_alternatives
from pymcda.generate import generate_criteria
from pymcda.generate import generate_random_profiles
from pymcda.generate import generate_random_criteria_values
from pymcda.generate import generate_random_alternative_performances
from pymcda.generate import generate_random_performance_table
from pymcda.rmp import RMP
import random
import sys

nseeds = int(sys.argv[1])
ncriteria = int(sys.argv[2])
nprofiles = int(sys.argv[3])
nalternatives = int(sys.argv[4])

#print("#seeds; %d" % nseeds)
#print("#criteria: %d" % ncriteria)
#print("#profiles: %d" % nprofiles)
#print("#alternatives: %d" % nalternatives)

stats = [ 0 ] * nprofiles

for seed in range(nseeds):
    random.seed(2 ** seed + 3 ** nalternatives + 5 ** ncriteria + 7 ** nprofiles)

    c = generate_criteria(ncriteria)
    cv = generate_random_criteria_values(c)
    b = [ "b%d" % i for i in range(1, nprofiles + 1)]
    bpt = generate_random_profiles(b, c)
    random.shuffle(b)
    model = RMP(c, cv, b, bpt)

    i = 0
    pwcs = PairwiseRelations()
    pt = PerformanceTable()
    while i != nalternatives:
        x = Alternative("x%d" % (i + 1))
        y = Alternative("y%d" % (i + 1))
        apx = generate_random_alternative_performances(x, c)
        apy = generate_random_alternative_performances(y, c)
        pwc, profile = model.compare_get_profile(apx, apy)
        if pwc.relation == pwc.INDIFFERENT:
            continue
        if apx.dominates(apy, c) or apy.dominates(apx, c):
            continue

        stats[profile] += 1

        pt.append(apx)
        pt.append(apy)
        pwcs.append(pwc)
        i += 1

    pwcs.weaker_to_preferred()

print([round(stat / nalternatives / nseeds * 100, 2) for stat in stats])
