from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
import random
from pymcda.electre_tri import ElectreTriBM
from pymcda.uta import AVFSort
from pymcda.types import Alternative, Alternatives
from pymcda.types import AlternativePerformances, PerformanceTable
from pymcda.types import Criterion, Criteria
from pymcda.types import CriterionValue, CriteriaValues
from pymcda.types import CriterionFunction, CriteriaFunctions
from pymcda.types import Category, Categories
from pymcda.types import CategoryProfile, CategoriesProfiles, Limits
from pymcda.types import PiecewiseLinear, Point, Segment
from pymcda.types import CategoryValue, CategoriesValues, Interval

def generate_alternatives(number, prefix='a'):
    alts = Alternatives()
    for i in range(number):
        a = Alternative()
        a.id = "%s%d" % (prefix, i+1)
        alts.append(a)

    return alts

def generate_criteria(number, prefix='c', random_direction = False):
    crits = Criteria()
    for i in range(number):
        c = Criterion("%s%d" % (prefix, i+1))
        if random_direction is True:
            c.direction = random.choice([-1, 1])
        crits.append(c)

    return crits

def generate_random_criteria_weights(crits, seed = None, k = 3):
    if seed is not None:
        random.seed(seed)

    weights = [ round(random.random(), k) for i in range(len(crits) - 1) ]
    weights.sort()

    cvals = CriteriaValues()
    for i, c in enumerate(crits):
        cval = CriterionValue()
        cval.id = c.id
        if i == 0:
            cval.value = weights[i]
        elif i == len(crits) - 1:
            cval.value = 1 - weights[i - 1]
        else:
            cval.value = weights[i] - weights[i - 1]

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

def generate_categories(number, prefix='cat'):
    cats = Categories()
    for i in range(number):
        c = Category()
        c.id = "%s%d" % (prefix, i+1)
        c.rank = i+1
        cats.append(c)

    return cats

def generate_random_profiles(alts, crits, seed = None, k = 3,
                             worst = None, best = None):
    if seed is not None:
        random.seed(seed)

    crit_random = {}
    n = len(alts)
    pt = PerformanceTable()
    for c in crits:
        rdom = []
        for i in range(n):
            if worst is None or best is None:
                rdom.append(round(random.random(), k))
            else:
                rdom.append(round(random.uniform(worst.performances[c.id],
                                                 best.performances[c.id]),
                                  k))

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
        cp = CategoryProfile("%s%d" % (prefix, i+1), l)
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
        a = Point(gi_min + i * interval, r[i])
        b = Point(gi_min + (i + 1) * interval, r[i + 1])
        s = Segment(a, b)

        f.append(s)

    s.ph_in = True

    return f

def generate_random_criteria_functions(crits, gi_min = 0, gi_max = 1,
                                       nseg_min = 1, nseg_max = 5,
                                       ui_min = 0, ui_max = 1):
    cfs = CriteriaFunctions()
    for crit in crits:
        ns = random.randint(nseg_min, nseg_max)
        f = generate_random_piecewise_linear(gi_min, gi_max, ns, ui_min,
                                             ui_max)
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

def generate_random_mrsort_model(ncrit, ncat, seed = None, k = 3,
                                 worst = None, best = None,
                                 random_direction = False):
    if seed is not None:
        random.seed(int(seed))

    c = generate_criteria(ncrit, random_direction = random_direction)
    cv = generate_random_criteria_weights(c, None, k)
    cat = generate_categories(ncat)
    cps = generate_categories_profiles(cat)
    b = cps.get_ordered_profiles()
    bpt = generate_random_profiles(b, c, None, k, worst, best)
    lbda = random.uniform(0.5, 1)

    return ElectreTriBM(c, cv, bpt, lbda, cps)

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

if __name__ == "__main__":
    alts = generate_alternatives(10)
    print(alts)
    crits = generate_criteria(5)
    print(crits)
    cv = generate_random_criteria_values(crits)
    print(cv)
    pt = generate_random_performance_table(alts, crits)
    print(pt)
    bpt = generate_random_profiles(alts, crits)
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
