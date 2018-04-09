from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
import random
from itertools import combinations
from pymcda.choquet import capacities_to_mobius, mobius_truncate
from pymcda.electre_tri import MRSort
from pymcda.uta import AVFSort
from pymcda.rmp import RMP
from pymcda.types import Alternative, Alternatives
from pymcda.types import AlternativePerformances, PerformanceTable
from pymcda.types import Criterion, Criteria
from pymcda.types import CriterionValue, CriteriaValues
from pymcda.types import CriterionFunction, CriteriaFunctions
from pymcda.types import Category, Categories
from pymcda.types import CategoryProfile, CategoriesProfiles, Limits
from pymcda.types import PiecewiseLinear, Point, Segment
from pymcda.types import CategoryValue, CategoriesValues, Interval
from pymcda.types import CriteriaSet

VETO_ABS = 1
VETO_PROP = 2

def generate_random_mobius_indices(criteria, additivity = None,
                                   seed = None, k = 3):
    cvs = generate_random_capacities(criteria, seed, k)
    mobius = capacities_to_mobius(criteria, cvs)

    if additivity is not None:
        mobius_truncate(mobius, additivity)
        mobius.normalize_sum_to_unity()

    return mobius

def generate_random_capacities(criteria, seed = None, k = 3):
    if seed is not None:
        random.seed(seed)

    n = len(criteria)
    r = [round(random.random(), k) for i in range(2 ** n - 2)] + [1.0]
    r.sort()

    j = 0
    cvs = CriteriaValues()
    for i in range(1, n + 1):
        combis = [c for c in combinations(criteria.keys(), i)]
        random.shuffle(combis)
        for combi in combis:
            if i == 1:
                cid = combi[0]
            else:
                cid = CriteriaSet(combi)

            cv = CriterionValue(cid, r[j])
            cvs.append(cv)

            j += 1

    return cvs

def generate_alternatives(number, prefix = 'a', names = None):
    alts = Alternatives()
    for i in range(number):
        aid = names[i] if names is not None else "%s%d" % (prefix, i+1)
        a = Alternative(aid)
        alts.append(a)

    return alts

def generate_criteria(number, prefix = 'c', random_direction = False,
                      names = None):
    crits = Criteria()
    for i in range(number):
        cid = names[i] if names is not None else "%s%d" % (prefix, i+1)
        c = Criterion(cid)
        if random_direction is True:
            c.direction = random.choice([-1, 1])
        crits.append(c)

    return crits

def generate_random_criteria_weights(crits, seed = None, k = 3):
    if seed is not None:
        random.seed(seed)

    weights = [ random.random() for i in range(len(crits) - 1) ]
    weights.sort()

    cvals = CriteriaValues()
    for i, c in enumerate(crits):
        cval = CriterionValue()
        cval.id = c.id
        if i == 0:
            cval.value = round(weights[i], k)
        elif i == len(crits) - 1:
            cval.value = round(1 - weights[i - 1], k)
        else:
            cval.value = round(weights[i] - weights[i - 1], k)

        cvals.append(cval)

    return cvals

def generate_random_criteria_values(crits, seed = None, k = 3,
                                    type = 'float', vmin = 0, vmax = 1):
    if seed is not None:
        random.seed(seed)

    cvals = CriteriaValues()
    for c in crits:
        cval = CriterionValue()
        cval.id = c.id
        if type == 'integer':
            cval.value = random.randint(vmin, vmax)
        else:
            cval.value = round(random.uniform(vmin, vmax), k)

        cvals.append(cval)

    return cvals

def generate_random_performance_table(alts, crits, seed = None, k = 3,
                                      worst = None, best = None):
    if seed is not None:
        random.seed(seed)

    pt = PerformanceTable()
    for a in alts:
        perfs = {}
        for c in crits:
            if worst is None or best is None:
                rdom = round(random.random(), k)
            else:
                rdom = round(random.uniform(worst.performances[c.id],
                                            best.performances[c.id]), k)

            perfs[c.id] = rdom

        ap = AlternativePerformances(a.id, perfs)
        pt.append(ap)

    return pt

def generate_categories(number, prefix = 'cat', names = None):
    cats = Categories()
    for i in reversed(range(number)):
        cid = names[i] if names is not None else "%s%d" % (prefix, i+1)
        c = Category(cid, rank = i + 1)
        cats.append(c)

    return cats

def generate_random_profiles(alts, crits, seed = None, k = 3,
                             worst = None, best = None):
    if seed is not None:
        random.seed(seed)

    if worst is None:
        worst = generate_worst_ap(crits)
    if best is None:
        best = generate_best_ap(crits)

    crit_random = {}
    n = len(alts)
    pt = PerformanceTable()
    for c in crits:
        rdom = []
        for i in range(n):
            minp = worst.performances[c.id]
            maxp = best.performances[c.id]
            if minp > maxp:
                minp, maxp = maxp, minp

            rdom.append(round(random.uniform(minp, maxp), k))

        if c.direction == -1:
            rdom.sort(reverse = True)
        else:
            rdom.sort()

        crit_random[c.id] = rdom

    for i, a in enumerate(alts):
        perfs = {}
        for c in crits:
            perfs[c.id] = crit_random[c.id][i]
        ap = AlternativePerformances(a, perfs)
        pt.append(ap)

    return pt

def generate_categories_profiles(cats, prefix='b'):
    cat_ids = cats.get_ordered_categories()
    cps = CategoriesProfiles()
    for i in range(len(cats)-1):
        l = Limits(cat_ids[i], cat_ids[i+1])
        cp = CategoryProfile("%s%d" % (prefix, len(cats) - i - 1), l)
        cps.append(cp)
    return cps

def generate_random_piecewise_linear(gi_min = 0, gi_max = 1, n_segments = 3,
                                     ui_min = 0, ui_max = 1, k = 3):
    d = ui_max - ui_min
    r = [ ui_min + d * round(random.random(), k)
          for i in range(n_segments - 1) ]
    r.append(ui_min)
    r.append(ui_max)
    r.sort()

    interval = (gi_max - gi_min) / n_segments

    f = PiecewiseLinear([])
    for i in range(n_segments):
        a = Point(round(gi_min + i * interval, k), r[i])
        b = Point(round(gi_min + (i + 1) * interval, k), r[i + 1])
        s = Segment("s%d" % (i + 1), a, b)

        f.append(s)

    s.p1_in = True
    s.p2_in = True

    return f

def generate_random_criteria_functions(crits, gi_min = 0, gi_max = 1,
                                       nseg_min = 1, nseg_max = 5,
                                       ui_min = 0, ui_max = 1):
    cfs = CriteriaFunctions()
    for crit in crits:
        ns = random.randint(nseg_min, nseg_max)
        if crit.direction == 1:
            _gi_min, _gi_max = gi_min, gi_max
        else:
            _gi_min, _gi_max = gi_max, gi_min

        f = generate_random_piecewise_linear(_gi_min, _gi_max, ns, ui_min,
                                             ui_max)
        cf = CriterionFunction(crit.id, f)
        cfs.append(cf)

    return cfs

def generate_random_plinear_preference_function(crits, ap_worst, ap_best):
    cfs = CriteriaFunctions()
    for crit in crits:
        worst = ap_worst.performances[crit.id]
        best = ap_best.performances[crit.id]
        if crit.direction == -1:
            worst, best = best, worst

        r = sorted([random.uniform(worst, best) for i in range(2)])

        a = Point(float("-inf"), 0)
        b = Point(r[0],0)
        c = Point(r[1],1)
        d = Point(float("inf"), 1)
        f = PiecewiseLinear([Segment('s1', a, b),
                             Segment('s2', b, c),
                             Segment('s3', c, d)])

        cf = CriterionFunction(crit.id, f)
        cfs.append(cf)

    return cfs

def generate_random_categories_values(cats, k = 3):
    ncats = len(cats)
    r = [round(random.random(), k) for i in range(ncats - 1)]
    r.sort()

    v0 = 0
    catvs = CategoriesValues()
    for i, cat in enumerate(cats.get_ordered_categories()):
        if i == ncats - 1:
            v1 = 1
        else:
            v1 = r[i]
        catv = CategoryValue(cat, Interval(v0, v1))
        catvs.append(catv)
        v0 = v1

    return catvs

def generate_worst_ap(crits, value = 0):
    return AlternativePerformances("worst", {c.id: value
                                             if c.direction == 1 else 1
                                             for c in crits})

def generate_best_ap(crits, value = 1):
    return AlternativePerformances("best", {c.id: value
                                             if c.direction == 1 else 0
                                             for c in crits})

def generate_random_mrsort_model(ncrit, ncat, seed = None, k = 3,
                                 worst = None, best = None,
                                 random_direction = False):
    if seed is not None:
        random.seed(int(seed))

    c = generate_criteria(ncrit, random_direction = random_direction)

    if worst is None:
        worst = generate_worst_ap(c)
    if best is None:
        best = generate_best_ap(c)

    cv = generate_random_criteria_weights(c, None, k)
    cat = generate_categories(ncat)
    cps = generate_categories_profiles(cat)
    b = cps.get_ordered_profiles()
    bpt = generate_random_profiles(b, c, None, k, worst, best)
    lbda = round(random.uniform(0.5, 1), k)

    return MRSort(c, cv, bpt, lbda, cps)

def generate_random_mrsort_choquet_model(ncrit, ncat, additivity = None,
                                         seed = None, k = 3,
                                         worst = None, best = None,
                                         random_direction = False):
    if seed is not None:
        random.seed(int(seed))

    c = generate_criteria(ncrit, random_direction = random_direction)

    if worst is None:
        worst = generate_worst_ap(c)
    if best is None:
        best = generate_best_ap(c)

    cv = generate_random_mobius_indices(c, additivity, None, k)
    cat = generate_categories(ncat)
    cps = generate_categories_profiles(cat)
    b = cps.get_ordered_profiles()
    bpt = generate_random_profiles(b, c, None, k, worst, best)
    lbda = round(random.uniform(0.5, 1), k)

    return MRSort(c, cv, bpt, lbda, cps)

def generate_random_avfsort_model(ncrit, ncat, nseg_min, nseg_max,
                                  seed = None, k = 3,
                                  random_direction = False):
    if seed is not None:
        random.seed(seed)

    c = generate_criteria(ncrit, random_direction = random_direction)
    cv = generate_random_criteria_weights(c, None, k)
    cat = generate_categories(ncat)

    cfs = generate_random_criteria_functions(c, nseg_min = nseg_min,
                                             nseg_max = nseg_max)
    catv = generate_random_categories_values(cat)

    return AVFSort(c, cv, cfs, catv)

def generate_random_veto_profiles(model, worst = None, k = 3):
    if worst is None:
        worst = generate_worst_ap(model.criteria)

    vpt = PerformanceTable()
    for bid in model.profiles:
        ap = AlternativePerformances(bid, {})
        for c in model.criteria:
            a = model.bpt[bid].performances[c.id]
            b = worst.performances[c.id]
            ap.performances[c.id] = round(random.uniform(a, b), k)
        vpt.append(ap)
        worst = ap

    return vpt

def generate_random_mrsort_model_with_binary_veto(ncrit, ncat, seed = None,
                                                  k = 3, worst = None,
                                                  best = None,
                                                  random_direction = False):
    model = generate_random_mrsort_model(ncrit, ncat, seed, k, worst, best,
                                         random_direction)
    if worst is None:
        worst = generate_worst_ap(model.criteria)
    if best is None:
        best = generate_best_ap(model.criteria)

    model.vpt = generate_random_veto_profiles(model, worst = None)
    return model

def generate_random_mrsort_model_with_coalition_veto(ncrit, ncat,
                                                     seed = None,
                                                     k = 3, worst = None,
                                                     best = None,
                                                     random_direction = False,
                                                     veto_weights = False):
    model = generate_random_mrsort_model_with_binary_veto(ncrit, ncat, seed,
                                                          k, worst, best,
                                                          random_direction)
    if veto_weights is True:
        model.veto_weights = generate_random_criteria_weights(model.criteria,
                                                              None, k)
        model.veto_lbda = random.uniform(0, 1 - model.lbda)
    else:
        model.veto_weights = model.cv.copy()
        model.veto_lbda = random.uniform(0, 0.5)

    return model

def generate_random_mrsort_model_with_coalition_veto2(ncrit, ncat,
                                                      seed = None, k = 3):

    criteria = generate_criteria(ncrit)
    worst = generate_worst_ap(criteria, 0.3)
    best = generate_best_ap(criteria, 0.7)
    model = generate_random_mrsort_model(ncrit, ncat, seed, k, worst, best)
    model.lbda = random.uniform(0.4, 0.7)
    model.vpt = model.bpt.copy() / 2
    model.veto_weights = generate_random_criteria_weights(model.criteria,
                                                          None, k)
    model.veto_lbda = random.uniform(0, 1 - model.lbda)

    return model

def generate_random_rmp_model(ncrit, nprofiles, seed = None):
    if seed:
        random.seed(seed)

    c = generate_criteria(ncrit)
    cvs = generate_random_criteria_weights(c)
    b = ["b%d" % (i + 1) for i in range(nprofiles)]
    bpt = generate_random_profiles(b, c)

    return RMP(c, cvs, b, bpt)

if __name__ == "__main__":
    alts = generate_alternatives(10)
    print(alts)
    crits = generate_criteria(5)
    print(crits)
    cv = generate_random_criteria_values(crits)
    print(cv)
    pt = generate_random_performance_table(alts, crits)
    print(pt)
    bpt = generate_random_profiles(alts.keys(), crits)
    print(bpt)
    cats = generate_categories(3)
    print(cats)
    cps = generate_categories_profiles(cats)
    print(cps)
    pl = generate_random_piecewise_linear(0, 5, 3)
    print(pl)
    catv = generate_random_categories_values(cats)
    print(catv)
    cw = generate_random_criteria_weights(crits)
    print(cw)
    model = generate_random_mrsort_model(10, 3)
    print(model)
    model = generate_random_avfsort_model(10, 3, 3, 3)
    print(model)
    model = generate_random_mrsort_model_with_binary_veto(10, 3)
    print(model)
    model = generate_random_mrsort_model_with_coalition_veto(10, 3)
    print(model)
    model = generate_random_mrsort_model_with_coalition_veto2(10, 3)
    print(model)
    model = generate_random_rmp_model(10, 2)
    print(model)
