from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
import math
import random
from itertools import product

from pymcda.generate import generate_random_mrsort_model_with_coalition_veto
from pymcda.generate import generate_alternatives
from pymcda.generate import generate_random_performance_table

def count_veto(seed, na, nc, ncat, veto_interval):
    # Generate a random ELECTRE TRI BM model
    model = generate_random_mrsort_model_with_coalition_veto(nc, ncat, seed,
                                        veto_interval = veto_interval / 100)

    # Generate a set of alternatives
    a = generate_alternatives(na)
    pt = generate_random_performance_table(a, model.criteria)
    aa = model.pessimist(pt)

    return sum([model.count_veto_pessimist(ap) for ap in pt])

if __name__ == "__main__":
    nas = range(10, 101, 10)
    ncs = [ 3, 5, 7, 10 ]
    ncats = [ 2, 3, 4, 5 ]
    veto_intervals = [ 80 ]
    nseeds = 10

    print("na\tnc\tncat\tvinterv\tnv_avg\tnv_std\tnv_min\tnv_max")
    for nc, ncat, na, veto_interval in product(ncs, ncats, nas, veto_intervals):
        nv = []
        for i in range(nseeds):
            nv.append(count_veto(i, na, nc, ncat, veto_interval))
        nv_avg = sum(nv) / nseeds
        nv_std = math.sqrt(sum((map(lambda x: (x - nv_avg)**2, nv))) / nseeds)
        nv_min, nv_max = min(nv), max(nv)
        print("%d\t%d\t%d\t%g\t%g\t%g\t%g\t%g" % (na, nc, ncat, veto_interval,
                                                  nv_avg, nv_std, nv_min,
                                                  nv_max))
