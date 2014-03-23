from __future__ import division
from __future__ import print_function
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
import math
import random
from itertools import product

from pymcda.generate import generate_random_mrsort_model_with_coalition_veto
from pymcda.generate import generate_random_mrsort_model_with_binary_veto
from pymcda.generate import generate_alternatives
from pymcda.generate import generate_random_performance_table

BINARY_VETO = 1
COALITIONS_VETO = 2

veto_function = 2 # 1 = absolute veto; 2 = prop veto
veto_type = COALITIONS_VETO
veto_weights = True

def count_veto(seed, na, nc, ncat, veto_param):
    # Generate a random ELECTRE TRI BM model
    if veto_type == COALITIONS_VETO:
        model = generate_random_mrsort_model_with_coalition_veto(nc, ncat,
                                            seed,
                                            veto_weights = True,
                                            veto_func = veto_function,
                                            veto_param = veto_param)
    elif veto_type == BINARY_VETO:
        model = generate_random_mrsort_model_with_binary_veto(nc, ncat,
                                            seed,
                                            veto_func = veto_function,
                                            veto_param = veto_param)

    # Generate a set of alternatives
    a = generate_alternatives(na)
    pt = generate_random_performance_table(a, model.criteria)
    aa = model.pessimist(pt)

    return sum([model.count_veto_pessimist(ap) for ap in pt])

if __name__ == "__main__":
#    nas = range(10, 101, 10)
    nas = [ 100 ]
    ncs = [ 5 ]
    ncats = [ 2, 3, 4, 5 ]
    veto_params = [ .1, .2, .3, .4, .5, .6, .7, .8, .9, 1 ]
    nseeds = 10

    nv_avgs = {}
    nv_stds = {}
    print("na\tnc\tncat\tvparam\tnv_avg\tnv_std\tnv_min\tnv_max")
    for nc, ncat, na, veto_param in product(ncs, ncats, nas, veto_params):
        nv = []
        for i in range(nseeds):
            nv.append(count_veto(i, na, nc, ncat, veto_param))
        nv_avg = sum(nv) / nseeds
        nv_std = math.sqrt(sum((map(lambda x: (x - nv_avg)**2, nv))) / nseeds)
        nv_min, nv_max = min(nv), max(nv)

        nv_avgs[na,nc,ncat] = nv_avg
        nv_stds[na,nc,ncat] = nv_std
        print("%d\t%d\t%d\t%g\t%g\t%2g\t%d\t%d" % (na, nc, ncat, veto_param,
                                                  nv_avg, nv_std, nv_min,
                                                  nv_max))

    for nc, na, veto_param in product(ncs, nas, veto_params):
        print("%d & %d & %d" % (nc, na, veto_param), end = '')
        for ncat in ncats:
            print(" & $%.2f \pm %.2f$" % (nv_avgs[na,nc,ncat],
                                        nv_stds[na,nc,ncat]), end = '')
        print("\\\\")
