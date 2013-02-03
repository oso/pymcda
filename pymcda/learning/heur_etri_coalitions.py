from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../../")
from collections import defaultdict
from pymcda.generate import generate_random_electre_tri_bm_model
from pymcda.generate import generate_random_performance_table
from pymcda.generate import generate_alternatives
from pymcda.utils import compute_winning_coalitions
from pymcda.utils import compute_degree_of_extremality
from pymcda.utils import compute_number_of_winning_coalitions
from pymcda.utils import display_coalitions
from pymcda.ui.graphic import display_electre_tri_models

class heur_etri_coalitions():

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

    def identify_coalition(self, ap, aa):
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

    def compute_coalitions_probabilities(self, n):
        coalitions = {}
        for i in range(n):
            aid = self.sorted_extrem[i][0]
            winning, loosing = self.identify_coalition(self.pt[aid],
                                                       self.aa[aid])
            if winning not in coalitions:
                coalitions[winning] = self.sorted_extrem[i][1]
            else:
                coalitions[winning] += self.sorted_extrem[i][1]

            if loosing not in coalitions:
                coalitions[loosing] = -self.sorted_extrem[i][1]
            else:
                coalitions[loosing] -= self.sorted_extrem[i][1]

        coalitions = sorted(coalitions.items(), key = lambda (k, v): v,
                             reverse = True)
        return coalitions

    def find_coalitions(self, n, k = 0):
        coal_proba = self.compute_coalitions_probabilities(n)
        coalitions = []
        for c in coal_proba:
            if c[1] > k:
                coalitions.append(c[0])

        return coalitions

if __name__ == "__main__":
    m = generate_random_electre_tri_bm_model(5, 2, 123)

    coal = compute_winning_coalitions(m.cv, m.lbda)
    print("Number of winning coalitions: %d" % len(coal))
    print("List of coalitions:")
    display_coalitions(coal)

    a = generate_alternatives(1000)
    pt = generate_random_performance_table(a, m.criteria)

    aa = m.pessimist(pt)

    heur = heur_etri_coalitions(m.criteria, m.categories, pt, aa)
    aids = [aid[0] for aid in heur.sorted_extrem ]
    display_electre_tri_models([m], [pt.get_worst(m.criteria)],
                               [pt.get_best(m.criteria)],
                               [[pt[aid] for aid in aids[:100]]])

    coal2 = heur.find_coalitions(100)
    print("List of coalitions found:")
    display_coalitions(coal2)

    coal_ni = list((set(coal) ^ set(coal2)) & set(coal))
    print("List of coalitions not identified (%d):" % len(coal_ni))
    display_coalitions(coal_ni)

    coal_add = list((set(coal) ^ set(coal2)) & set(coal2))
    print("List of coalitions added (%s):" % len(coal_add))
    display_coalitions(coal_add)
