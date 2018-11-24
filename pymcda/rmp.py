from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
from pymcda.types import PairwiseRelations, PairwiseRelation

class RMP(object):

    WEAKER = 0
    INDIFFERENT = 1
    PREFERRED = 2

    def __init__(self, criteria = None, cvs = None, profiles = None,
                 bpt = None, coalition_relations = None):
        self.criteria = criteria
        self.cvs = cvs
        self.profiles = profiles
        self.bpt = bpt
        self.coalition_relations = coalition_relations

    def __criteria_coalition(self, ap1, ap2):
        criteria_set = set()
        for c in self.criteria:
            diff = ap2.performances[c.id] - ap1.performances[c.id]
            diff *= c.direction
            if diff <= 0:
                criteria_set.add(c.id)

        return criteria_set

    def __concordance(self, criteria_set):
        return sum([c.value for c in self.cvs
                    if c.id_issubset(criteria_set) is True])

    def compare_get_profile(self, ap1, ap2):
        for i, profile in enumerate(self.profiles):
            bp = self.bpt[profile]
            c1 = self.__criteria_coalition(ap1, bp)
            c2 = self.__criteria_coalition(ap2, bp)

            if c1 == c2:
                continue

            if self.coalition_relations:
                c1 = tuple(sorted(list(c1)))
                c2 = tuple(sorted(list(c2)))
                if self.coalition_relations[c1][c2] is True:
                    return (PairwiseRelation(ap1.id, ap2.id,
                                             PairwiseRelation.PREFERRED), i)

                if self.coalition_relations[c2][c1] is True:
                    return (PairwiseRelation(ap1.id, ap2.id,
                                             PairwiseRelation.WEAKER), i)

            else:
                c1 = self.__concordance(c1)
                c2 = self.__concordance(c2)

                if c1 > c2:
                    return (PairwiseRelation(ap1.id, ap2.id,
                                             PairwiseRelation.PREFERRED), i)

                if c1 < c2:
                    return (PairwiseRelation(ap1.id, ap2.id,
                                            PairwiseRelation.WEAKER), i)

        return (PairwiseRelation(ap1.id, ap2.id, PairwiseRelation.INDIFFERENT),
                None)

    def compare(self, ap1, ap2):
        return self.compare_get_profile(ap1, ap2)[0]

if __name__ == "__main__":
    import random
    from itertools import combinations

    from generate import generate_criteria, generate_random_criteria_weights
    from generate import generate_random_profiles
    from generate import generate_random_performance_table
    from generate import generate_alternatives
    from generate import generate_random_performance_table

    ncriteria = 5
    nprofiles = 3
    nalternatives = 100

    random.seed(0)
    c = generate_criteria(ncriteria)
    cvs = generate_random_criteria_weights(c)
    b = ["b%d" % (i + 1) for i in range(nprofiles)]
    bpt = generate_random_profiles(b, c)

    a = generate_alternatives(nalternatives)
    pt = generate_random_performance_table(a, c)

    rmp = RMP(c, cvs, b, bpt)
    for a1, a2 in combinations(a.keys(), 2):
        ap1 = pt[a1]
        ap2 = pt[a2]
        rel1 = rmp.compare(ap1, ap2).relation
        rel2 = rmp.compare(ap2, ap1).relation

        if rel1 == rmp.INDIFFERENT and rel2 != rmp.INDIFFERENT:
            print("Error:", ap1, ap2, rel1, rel2)

        if rel1 == rmp.WEAKER and rel2 != rmp.PREFERRED:
            print("Error:", ap1, ap2, rel1, rel2)

        if rel1 == rmp.PREFERRED and rel2 != rmp.WEAKER:
            print("Error:", ap1, ap2, rel1, rel2)
