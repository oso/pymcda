from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
import random
from itertools import chain, combinations, product
from math import factorial, ceil
from pymcda.types import AlternativesAssignments
from collections import OrderedDict

def add_errors_in_assignments(aa, category_ids, errors_pc):
    n = int(len(aa)*errors_pc)
    aa_erroned = random.sample(aa, n)

    l = AlternativesAssignments([])
    for a in aa_erroned:
        cat = a.category_id
        new_cat = a.category_id
        while new_cat == cat:
            new_cat = random.sample(category_ids, 1)[0]
        a.category_id = new_cat
        l.append(a)

    return l

def add_errors_in_assignments_proba(aa, category_ids, proba):
    l = AlternativesAssignments([])

    for a in aa:
        r = random.random()
        if r <= proba:
            cat = a.category_id
            new_cat = a.category_id
            while new_cat == cat:
                new_cat = random.sample(category_ids, 1)[0]
            a.category_id = new_cat

            l.append(a)

    return l

def display_assignments_and_pt(alternatives, criteria, aas, pts):

    for i, aa in enumerate(aas):
        print("\taa%d" % i),
    print('\t|'),
    for i, c in enumerate(criteria):
        print("%-7s" % c.id),
    print('')

    for a in alternatives:
        print("%6s" % a.id),
        for aa in aas:
            print("\t%-6s" % aa(a.id)),
        print('\t|'),

        for c in criteria:
            for pt in pts:
                perfs = pt(a.id)
                print("%-6.5f" % perfs[c.id]),
        print('')

def compute_ca(aa, aa2, alist=None):
    if alist is None:
        alist = aa.keys()

    total = len(alist)
    ok = 0
    for aid in alist:
        af = aa(aid)
        af2 = aa2(aid)
        if af == af2:
            ok += 1

    return ok / total

def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

def compute_winning_coalitions(weights, lbda):
    l = []
    for coalition in powerset(weights.keys()):
        w = [ weights[cid].value for cid in coalition ]
        if sum(w) >= lbda:
            l.append(coalition)
    return l

def compute_number_of_winning_coalitions(weights, lbda):
    return len(compute_winning_coalitions(weights, lbda))

def compute_maximal_number_of_coalitions(n):
    k = int(ceil(n/2))
    v = 0
    for i in range(k, n + 1):
        v += factorial(n) / (factorial(i) * factorial(n-i))
    return int(v)

def display_coalitions(coalitions):
    # Converting the list to a set remove duplicates
    crits = list(set([i for c in coalitions for i in c]))
    crits.sort()

    coalitions.sort()

    clen = {crit: len(crit) + 1 for crit in crits}

    line = ""
    for crit in crits:
        line += "%s" % crit + " " * (clen[crit] - len(crit))
    print(line)

    for coalition in coalitions:
        line = ""
        for crit in crits:
            if crit in coalition:
                line += "x"
            else:
                line += " "

            line += " " * (clen[crit] - 1)

        print(line)

def compute_degree_of_extremality(pt):
    results = { ap.id: 1 for ap in pt}

    minv = pt.get_min().performances
    maxv = pt.get_max().performances

    cids = next(pt.itervalues()).performances.keys()
    for ap, cid in product(pt, cids):
        down = ap.performances[cid] - minv[cid]
        up = maxv[cid] - ap.performances[cid]

        if down > up:
            results[ap.id] *= down / (maxv[cid] - minv[cid])
        else:
            results[ap.id] *= up / (maxv[cid] - minv[cid])

    return results

def compute_ranking_differences(aa, aa2, categories):
    ncategories = len(categories)
    rank_diff = {i: 0 for i in range(-ncategories + 1, ncategories)}

    cat_rank = { category: i for i, category in enumerate(categories) }
    aids = aa.keys()
    for aid in aids:
        cata, catb = aa[aid].category_id, aa2[aid].category_id
        ranka, rankb = cat_rank[cata], cat_rank[catb]
        rank_diff[rankb - ranka] += 1

    return rank_diff

def compute_ranking_matrix(aa, aa2, categories):
    matrix = OrderedDict([((a, b), 0) for a in categories \
                                      for b in categories])

    aids = aa.keys()
    for aid in aids:
        cata, catb = aa[aid].category_id, aa2[aid].category_id
        matrix[(cata, catb)] += 1

    return matrix
