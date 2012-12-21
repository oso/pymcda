from __future__ import division
import random
from itertools import chain, combinations
from mcda.types import alternative_performances
from mcda.types import alternatives_affectations

def get_max_alternative_performance(pt, crit):
    val = None
    for ap in pt:
        perf = ap(crit.id)
        if val == None or perf > val:
            val = perf

    return val

def get_min_alternative_performance(pt, crit):
    val = None
    for ap in pt:
        perf = ap(crit.id)
        if val == None or perf < val:
            val = perf

    return val

def get_worst_alternative_performances(pt, crits):
    wa = alternative_performances('worst', {})

    for c in crits:
        if c.direction == 1:
            val = get_min_alternative_performance(pt, c)
        else:
            val = get_max_alternative_performance(pt, c)

        wa.performances[c.id] = val

    return wa

def get_best_alternative_performances(pt, crits):
    ba = alternative_performances('best', {})

    for c in crits:
        if c.direction == 1:
            val = get_max_alternative_performance(pt, c)
        else:
            val = get_min_alternative_performance(pt, c)

        ba.performances[c.id] = val

    return ba

def get_ordered_profile_ids(categories, categories_profiles):
    cat_rank = {}
    for c in categories:
        cat_rank[c.id] = c.rank

    profiles = {}
    for cp in categories_profiles:
        upper_category_id = cp.value.upper
        lower_category_id = cp.value.lower
        if upper_category_id:
            upper_category_rank = cat_rank[upper_category_id]
            profiles[upper_category_rank] = cp.alternative_id
        if lower_category_id:
            lower_category_rank = cat_rank[lower_category_id]
            profiles[lower_category_id-1] = cp.alternative_id

    profiles_rank = profiles.keys()
    profiles_rank.sort()

    profile_ids = []
    for pr in profiles_ranks:
        profile_ids.append(profiles[pr])

    return profile_ids

def normalize_criteria_weights(criteria_values):
    total = float()
    for cv in criteria_values:
        total += cv.value

    for cv in criteria_values:
        cv.value /= total

def add_errors_in_affectations(aa, category_ids, errors_pc):
    n = int(len(aa)*errors_pc)
    aa_erroned = random.sample(aa, n)

    l = alternatives_affectations([])
    for a in aa_erroned:
        cat = a.category_id
        new_cat = a.category_id
        while new_cat == cat:
            new_cat = random.sample(category_ids, 1)[0]
        a.category_id = new_cat
        l.append(a)

    return l

def display_affectations_and_pt(alternatives, criteria, aas, pts):

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

def compute_ac(aa, aa2, alist=None):
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

def get_categories_upper_limits(categories_values):
    d = {}
    for cv in categories_values:
        d[cv.id] = cv.value.upper
    return d

def get_categories_lower_limits(categories_values):
    d = {}
    for cv in categories_values:
        d[cv.id] = cv.value.lower
    return d

def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

def get_possible_coallitions(weights, lbda):
    l = []
    for coallition in powerset(weights.keys()):
        w = [ weights[cid].value for cid in coallition ]
        if sum(w) >= lbda:
            l.append(coallition)
    return l

def get_number_of_possible_coallitions(weights, lbda):
    return len(get_possible_coallitions(weights, lbda))
