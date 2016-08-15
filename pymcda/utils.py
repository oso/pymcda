from __future__ import division
from __future__ import print_function
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
import random
from itertools import chain, combinations, product
from math import factorial, ceil
from pymcda.types import AlternativesAssignments
from collections import OrderedDict

def add_errors_in_assignments(aa, category_ids, errors_pc):
    n = int(len(aa)*errors_pc)
    aa_erroned = random.sample(list(aa), n)

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

def print_pt_and_assignments(alternatives, cids, aas, pt):
    alen = max([len(aid) for aid in alternatives] + [len("alt.")])

    if alternatives is None:
        alternatives = pt.keys()

    if cids is None:
        cids = pt[alternatives[0]].performances.keys()

    aaname, aalen = {}, {}
    for i, aa in enumerate(aas):
        aaname[i] = aid
        if aid is None:
            aaname[i] = "assign%d" % (i + 1)

        aalen[i] = max([len(aa[aid].category_id) for aid in alternatives]
                        + [len(aaname[i])])

    clen = {}
    for cid in cids:
        clen[cid] = max([len(str(pt[aid].performances[cid]))
                          for aid in alternatives] + [len(cid)])

    print(" " * (alen - len("alt.")) + "alt.", end = "")
    for i, aa in enumerate(aas):
        print(" " + " " * (aalen[i] - len(aaname[i])) + aaname[i],
              end = "")
    print(" |", end = "")
    for cid in cids:
        print(" " + " " * (clen[cid] - len(cid)) + cid, end = "")
    print("")

    for aid in alternatives:
        print(" " * (alen - len(aid)) + "%s" % aid, end = "")
        for i, aa in enumerate(aas):
            cat = aa[aid].category_id
            print(" " + " " * (aalen[i] - len(cat)) + cat, end = "")
        print(" |", end = "")
        for cid in  cids:
            perf = str(pt[aid].performances[cid])
            print(" " + " " * (clen[cid] - len(perf)) + "%s" % perf, end = "")
        print("")

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

def compute_number_of_winning_coalitions(weights, lbda):
    winning, loosing = compute_winning_and_loosing_coalitions(weights, lbda)
    return len(winning)

def compute_maximal_number_of_coalitions(n):
    k = int(ceil(n/2))
    v = 0
    for i in range(k, n + 1):
        v += factorial(n) / (factorial(i) * factorial(n-i))
    return int(v)

def compute_winning_and_loosing_coalitions(cvs, lbda):
    sufficient = set()
    insufficient = set()

    c = cvs.keys()
    for coa in powerset(c):
        l = cvs.get_subset(coa)
        diff = sum([cv.value for cv in l]) - lbda
        if abs(diff) < 10e-9 or diff > 0:
#        if diff >= 0:
            sufficient.add(frozenset(coa))
        else:
            insufficient.add(frozenset(coa))

    return sufficient, insufficient

def compute_minimal_winning_coalitions(coalitions):
    fmins = coalitions
    for fmin, fmin2 in product(fmins, fmins):
        if fmin == fmin2:
            continue
        elif fmin2.issuperset(fmin):
            fmins.discard(fmin2)

    return fmins

def compute_maximal_loosing_coalitions(coalitions):
    gmaxs = coalitions
    for gmax, gmax2 in product(gmaxs, gmaxs):
        if gmax == gmax2:
            continue
        elif gmax2.issubset(gmax):
            gmaxs.discard(gmax2)

    return gmaxs

def display_coalitions(coalitions):
    # Converting the list to a set remove duplicates
    crits = list(set([i for c in coalitions for i in c]))
    crits.sort()

    coalitions = list(coalitions)
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

def compute_confusion_matrix(aa, aa2, categories):
    matrix = OrderedDict([((a, b), 0) for a in categories \
                                      for b in categories])

    aids = aa.keys()
    for aid in aids:
        cata, catb = aa[aid].category_id, aa2[aid].category_id
        matrix[(cata, catb)] += 1

    return matrix

def print_confusion_matrix(matrix):
    list_categories = []
    for cata, catb in matrix.keys():
        if cata not in list_categories:
            list_categories.append(cata)
        if catb not in list_categories:
            list_categories.append(catb)

    len_cols = {cat: max([len(cat)] + [len(str(matrix[cat, cat2])) \
                          for cat2 in list_categories]) \
                for cat in list_categories}
    len_cols[0] = max([len(cat) for cat in list_categories])

    string = " " * max([len(cat) + 1 for cat in list_categories])
    for cat in list_categories:
        string += "%s " % cat
    print(string)

    for cat in list_categories:
        string = "%s " % cat + " " * (len_cols[0] - len(cat))
        for catb in list_categories:
            val = str(matrix[cat, catb])
            string += " " * (len_cols[catb] - len(val))
            string += "%s " % val
        print(string)
