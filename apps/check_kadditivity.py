from __future__ import division
import cplex
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
from itertools import combinations

from pymcda.types import PairwiseRelations
from pymcda.types import PairwiseRelation
from pymcda.utils import powerset

def read_input_file(path):
    f = open(path, "r")
    lines = f.readlines()

    prev = None
    relations = PairwiseRelations()
    for line in lines:
        l = line.strip().strip("[]").replace(" ", "")
        if len(l) == 0:
            continue

        coalitions = []
        for coa in l.split(","):
            coa = frozenset((coa.split("-")))
            coalitions.append(coa)

        first = coalitions.pop(0)
        for coa in coalitions:
            relations.append(PairwiseRelation(first, coa, PairwiseRelation.INDIFFERENT))

        if prev is None:
            prev = first
            continue

        relations.append(PairwiseRelation(first, prev, PairwiseRelation.PREFERRED))
        prev = first

    return relations

def get_criteria(relations):
    criteria = set()
    for rel in relations:
        if len(rel.a) == 1:
            criteria.add(next(iter(rel.a)))
        if len(rel.b) == 1:
            criteria.add(next(iter(rel.b)))

    return criteria

def get_mobius_indices_from_coalition(coalition, kadditivity):
    mobius = set()
    for k in range(1, kadditivity + 1):
        mobius |=  set([frozenset(c) for c in combinations(coalition, k)])
    return mobius

def check_kadditivity(relations, kadditivity, epsilon = 0.00001, msum = 1000):
    lp = cplex.Cplex()
#    lp.set_log_stream(None)
#    lp.set_results_stream(None)

    criteria = get_criteria(relations)

    # get list of mobius indices
    mi = []
    for k in range(1, kadditivity + 1):
        for c in combinations(criteria, k):
            c = str(sorted(c))
            mi.append(c)

    lp.variables.add(names = mi, lb = [-msum for m in mi],
                                 ub = [msum for m in mi])
    lp.variables.add(names = ["alpha"], lb = [0], ub = [msum])
    lp.variables.add(names = ["delta"], lb = [0], ub = [msum])

    for relation in relations:
        mob_a = get_mobius_indices_from_coalition(relation.a, kadditivity)
        mob_b = get_mobius_indices_from_coalition(relation.b, kadditivity)

        inter = mob_a & mob_b
        mob_a -= inter
        mob_b -= inter

        mob_a = map(sorted, mob_a)
        mob_b = map(sorted, mob_b)
        mob_a = map(str, mob_a)
        mob_b = map(str, mob_b)

        if relation.relation == PairwiseRelation.WEAKER:
            mob_a, mob_b = mob_b, mob_a

        if relation.relation == PairwiseRelation.INDIFFERENT:
            lp.linear_constraints.add(names = ["%s" % relation],
                                      lin_expr = [
                                                  [list(mob_b) + list(mob_a) + ["delta"],
                                                  [1.0] * len(mob_b) + [-1.0] * len(mob_a) + [-1.0]],
                                                 ],
                                      senses = ["L"],
                                      rhs = [0]
                                     )

            lp.linear_constraints.add(names = ["%s_2" % relation],
                                      lin_expr = [
                                                  [list(mob_a) + list(mob_b) + ["delta"],
                                                  [1.0] * len(mob_a) + [-1.0] * len(mob_b) + [-1.0]],
                                                 ],
                                      senses = ["L"],
                                      rhs = [0]
                                     )
        else:
            mob_b.append("alpha")
            lp.linear_constraints.add(names = ["%s" % relation],
                                      lin_expr = [
                                                  [list(mob_a) + list(mob_b),
                                                  [1.0] * len(mob_a) + [-1.0] * len(mob_b)],
                                                 ],
                                      senses = ["G"],
                                      rhs = [0]
                                     )


    lp.linear_constraints.add(names = ["wsum"],
                              lin_expr = [
                                          [mi, [1.0] * len(mi)],
                                         ],
                              senses = ["E"],
                              rhs = [msum]
                             )

    lp.linear_constraints.add(names = ["alpha_delta"],
                              lin_expr = [
                                          [["delta", "alpha"],
                                           [1.0, -1.0]],
                                         ],
                              senses = ["L"],
                              rhs = [0]
                             )

    for k in range(1, kadditivity + 1):
        for ua in combinations(criteria, k):
            ua = frozenset(ua)
            for ub in combinations(ua, k - 1):
                ub = frozenset(ub)

                mob_ua = get_mobius_indices_from_coalition(ua, kadditivity)
                mob_ub = get_mobius_indices_from_coalition(ub, kadditivity)

                inter = mob_ua & mob_ub
                mob_ua -= inter
                mob_ub -= inter

                mob_ua = map(sorted, mob_ua)
                mob_ub = map(sorted, mob_ub)
                mob_ua = map(str, mob_ua)
                mob_ub = map(str, mob_ub)

                lp.linear_constraints.add(names = ["%s_%s" % (mob_ua, mob_ub)],
                                          lin_expr = [
                                                      [list(mob_ua) + list(mob_ub),
                                                      [1.0] * len(mob_ua) + [-1.0] * len(mob_ub)],
                                                     ],
                                          senses = ["G"],
                                          rhs = [0]
                                         )

    lp.objective.set_sense(lp.objective.sense.maximize)
    lp.objective.set_linear("alpha", 1)
    lp.objective.set_linear("delta", -1)

    lp.solve()

    status = lp.solution.get_status()
    if status != lp.solution.status.optimal:
        raise RuntimeError("Solver status: %s" % status)

    obj = lp.solution.get_objective_value()
    print("obj: %s" % obj)
    print("delta: %s" % lp.solution.get_values("delta"))
    print("alpha: %s" % lp.solution.get_values("alpha"))

    for m in mi:
        print("%s: %s" % (m, lp.solution.get_values(m)))

    for pwc in relations:
        mob_a = get_mobius_indices_from_coalition(pwc.a, kadditivity)
        mob_b = get_mobius_indices_from_coalition(pwc.b, kadditivity)

        inter = mob_a & mob_b
        mob_a -= inter
        mob_b -= inter

        mob_a = map(sorted, mob_a)
        mob_b = map(sorted, mob_b)
        mob_a = map(str, mob_a)
        mob_b = map(str, mob_b)

        mob_a = map(lp.solution.get_values, mob_a)
        mob_b = map(lp.solution.get_values, mob_b)

        if pwc.relation == PairwiseRelation.INDIFFERENT:
            print("= %s" % (abs(sum(mob_a) - sum(mob_b)) <= 1e-12))
        elif pwc.relation == PairwiseRelation.WEAKER:
            print("< %s" % (sum(mob_a) < sum(mob_b)))
        elif pwc.relation == PairwiseRelation.PREFERRED:
            print("> %s" % (sum(mob_a) > sum(mob_b)))

    return

if __name__ == "__main__":
    import sys

    relations = read_input_file(sys.argv[1])
    for relation in relations:
        print(relation)

    check_kadditivity(relations, int(sys.argv[2]))
