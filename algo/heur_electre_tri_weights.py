from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
from collections import defaultdict
from tools.generate_random import generate_random_electre_tri_bm_model
from tools.generate_random import generate_random_performance_table
from tools.generate_random import generate_random_alternatives
from tools.utils import get_possible_coallitions
from tools.utils import compute_degree_of_extremality
from tools.utils import get_number_of_possible_coallitions
from tools.utils import display_coallitions
from ui.graphic import display_electre_tri_models

class heur_electre_tri_weights():

    def __init__(self, c, cats, pt, aa):
        self.c = c
        self.cats = cats
        self.pt = pt
        self.aa = aa
        self.extrem = compute_degree_of_extremality(pt)
        self.sorted_extrem = sorted(self.extrem.items(),
                                    key = lambda (k,v): v,
                                    reverse = True)
        self.worst = pt.get_worst(c)
        self.best = pt.get_best(c)
        self.mean = pt.get_mean()

    def identify_coallition(self, ap, aa):
        winning = []
        loosing = []
        for c in self.c:
            diff = ap.performances[c.id] - self.mean.performances[c.id]
            diff *= c.direction

            if aa.category_id == self.cats[-1]:
                if diff > 0:
                    winning.append(c.id)
                else:
                    loosing.append(c.id)

            if aa.category_id == self.cats[0]:
                if diff < 0:
                    winning.append(c.id)
                else:
                    loosing.append(c.id)

        return tuple(winning), tuple(loosing)

    def run(self, n):
        coallitions = {}
        for i in range(n):
            aid = self.sorted_extrem[i][0]
            winning, loosing = self.identify_coallition(pt[aid], aa[aid])
            if winning not in coallitions:
                coallitions[winning] = self.sorted_extrem[i][1]
            else:
                coallitions[winning] += self.sorted_extrem[i][1]

            if loosing not in coallitions:
                coallitions[loosing] = -self.sorted_extrem[i][1]
            else:
                coallitions[loosing] -= self.sorted_extrem[i][1]

        coallitions = sorted(coallitions.items(), key = lambda (k, v): v,
                             reverse = True)
        return coallitions

    def cut(self, coal_proba, k = 0):
        coallitions = []
        for c in coal_proba:
            if c[1] > k:
                coallitions.append(c[0])

        return coallitions

if __name__ == "__main__":
    m = generate_random_electre_tri_bm_model(5, 2, 123789)
    print m.lbda

    coal = get_possible_coallitions(m.cv, m.lbda)
    print("Number of winning coallitions: %d" % len(coal))
    print("List of coallitions:")
    display_coallitions(coal)

    a = generate_random_alternatives(10000)
    pt = generate_random_performance_table(a, m.criteria)

    display_electre_tri_models([m], [pt.get_worst(m.criteria)],
                               [pt.get_best(m.criteria)])
    aa = m.pessimist(pt)

    heur = heur_electre_tri_weights(m.criteria, m.categories, pt, aa)
    coal_proba = heur.run(100)
    print("List of coallitions found:")
    coal2 = heur.cut(coal_proba, 0)
    display_coallitions(coal2)

    print("List of coallitions not identified:")
    display_coallitions(list((set(coal) ^ set(coal2)) & set(coal)))
    print("List of coallitions added:")
    display_coallitions(list((set(coal) ^ set(coal2)) & set(coal2)))
