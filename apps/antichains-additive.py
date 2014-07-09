import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
import cplex
import math
import sys
import bz2
from itertools import product
from xml.etree import ElementTree
from pymcda.types import Criteria, CriteriaSets, CriteriaSet
from pymcda.utils import powerset

def cplex_lbda_minmax(cids, fmins, gmaxs, epsilon = 0.00001):
    lp = cplex.Cplex()
    lp.set_log_stream(None)
    lp.set_results_stream(None)

    lp.variables.add(names = ["w%s" % cid for cid in cids],
                     lb = [0 for c in cids],
                     ub = [1 for c in cids])
    lp.variables.add(names = ["lambda"], lb = [0], ub = [1 + epsilon])

    lp.linear_constraints.add(names = ["fmin%s" % i
                                       for i in range(len(fmins))],
                              lin_expr =
                                [
                                 [["w%s" % cid for cid in cids] + ["lambda"],
                                  [1 if cid in fmin else 0 for cid in cids]
                                  + [-1]
                                 ] for fmin in fmins
                                ],
                              senses = ["G" for fmin in fmins],
                              rhs = [0 for fmin in fmins])

    lp.linear_constraints.add(names = ["gmax%s" % i
                                       for i in range(len(gmaxs))],
                              lin_expr =
                                [
                                 [["w%s" % cid for cid in cids] + ["lambda"],
                                  [1 if cid in gmax else 0 for cid in cids]
                                  + [-1]
                                 ] for gmax in gmaxs
                                ],
                              senses = ["L" for gmax in gmaxs],
                              rhs = [-epsilon for gmax in gmaxs])

    lp.linear_constraints.add(names = ["wsum"],
                              lin_expr = [
                                          [["w%s" % cid for cid in cids],
                                           [1.0] * len(cids)],
                                         ],
                              senses = ["E"],
                              rhs = [1]
                             )

    lp.objective.set_linear("lambda", 1)

    lp.objective.set_sense(lp.objective.sense.minimize)
    lp.solve()
    lbdamin = lp.solution.get_objective_value()

    lp.objective.set_sense(lp.objective.sense.maximize)
    lp.solve()
    lbdamax = lp.solution.get_objective_value()

    return lbdamin, lbdamax

def compute_gmax(pset, fmins):
    gmaxs = pset.copy()
    for s, fmin in product(gmaxs, fmins):
        if fmin.issubset(s):
            gmaxs.discard(s)

    for s, s2 in product(gmaxs, gmaxs):
        if s == s2:
            continue
        elif s2.issubset(s):
            gmaxs.discard(s2)

    return gmaxs

if __name__ == "__main__":
    f = bz2.BZ2File(sys.argv[1])

    tree = ElementTree.parse(f)
    root = tree.getroot()

    xmcda_criteria = root.find(".//criteria")
    c = Criteria().from_xmcda(xmcda_criteria)
    print(c)
    cids = c.keys()

    c_pset = CriteriaSets(set(CriteriaSet(*i) for i in powerset(c.keys())))

    xmcda_csets = root.findall(".//criteriaSets")

    i = 0
    for xmcda in xmcda_csets:
        fmins = CriteriaSets().from_xmcda(xmcda)
        gmaxs = compute_gmax(c_pset, fmins)
        lbdamin, lbdamax = cplex_lbda_minmax(cids, fmins, gmaxs)
        if lbdamin > lbdamax:
            i += 1
            print(i, fmins, lbdamin, lbdamax)
