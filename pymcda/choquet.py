import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
from itertools import combinations
from pymcda.types import CriteriaSet
from pymcda.types import CriterionValue, CriteriaValues

def capacities_to_mobius(criteria, capacities):
    cvs = CriteriaValues()
    n = len(criteria)
    for i in range(1, n + 1):
        for combi in [c for c in combinations(criteria.keys(), i)]:
            cid = combi[0] if (i == 1) else CriteriaSet(combi)
            m = capacities[cid].value
            for j in range(1, i):
                for combi2 in [c for c in combinations(combi, j)]:
                    cidj = combi2[0] if (j == 1) else CriteriaSet(combi2)
                    m -= cvs[cidj].value

            cv = CriterionValue(cid, m)
            cvs.append(cv)

    return cvs

def mobius_to_capacities(criteria, mobius):
    cvs = CriteriaValues()
    n = len(criteria)
    for i in range(1, n + 1):
        for combi in [c for c in combinations(criteria.keys(), i)]:
            cid = combi[0] if (i == 1) else CriteriaSet(combi)
            v = 0
            for j in range(1, i + 1):
                for combi2 in [c for c in combinations(combi, j)]:
                    cidj = combi2[0] if (j == 1) else CriteriaSet(combi2)
                    if cidj in mobius:
                        v += mobius[cidj].value

            cv = CriterionValue(cid, v)
            cvs.append(cv)

    return cvs

def mobius_truncate(mobius, k):
    if k < 1:
        raise ValueError("Invalid cut value (%d)" % k)

    for m in mobius:
        if isinstance(m.id, CriteriaSet) and len(m.id) > k:
            mobius.remove(m.id)

def capacities_are_monotone(criteria, capacities):
    n = len(criteria)
    for i in range(2, n + 1):
        for combi in [c for c in combinations(criteria.keys(), i)]:
            cid = CriteriaSet(combi)
            for combi2 in [c for c in combinations(combi, i - 1)]:
                cidj = combi2[0] if (i == 2) else CriteriaSet(combi2)
                if capacities[cidj].value > capacities[cid].value:
                    return False

    return True
