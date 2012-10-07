import sys
sys.path.insert(0, "..")
import random
from mcda.types import alternative, alternatives
from mcda.types import alternative_performances, performance_table
from mcda.types import criterion, criteria
from mcda.types import criterion_value, criteria_values
from mcda.types import category, categories
from mcda.types import category_profile, categories_profiles, limits
from mcda.types import piecewise_linear, point, segment

def generate_random_alternatives(number, prefix='a'):
    alts = alternatives()
    for i in range(number):
        a = alternative()
        a.id = "%s%d" % (prefix, i+1)
        alts.append(a)

    return alts

def generate_random_criteria(number, prefix='c'):
    crits = criteria()
    for i in range(number):
        c = criterion("%s%d" % (prefix, i+1))
        crits.append(c)

    return crits

def generate_random_criteria_values(crits, seed=None, k=3):
    if seed is not None:
        random.seed(seed)

    cvals = criteria_values()
    for c in crits:
        cval = criterion_value()
        cval.id = c.id
        cval.value = round(random.random(), k)
        cvals.append(cval)

    return cvals

def generate_random_performance_table(alts, crits, seed=None):
    if seed is not None:
        random.seed(seed)

    pt = performance_table()
    for a in alts:
        perfs = {}
        for c in crits:
            perfs[c.id] = round(random.random(), 3)
        ap = alternative_performances(a.id, perfs)
        pt.append(ap)

    return pt

def generate_random_categories(number, prefix='cat'):
    cats = categories()
    for i in range(number):
        c = category()
        c.id = "%s%d" % (prefix, i+1)
        c.rank = i+1
        cats.append(c)

    return cats

def generate_random_profiles(alts, crits, seed=None, k=3):
    if seed is not None:
        random.seed(seed)

    crit_random = {}
    n = len(alts)
    pt = performance_table()
    for c in crits:
        rdom = []
        for i in range(n):
            rdom.append(round(random.random(), k))
        rdom.sort()

        crit_random[c.id] = rdom

    for i, a in enumerate(alts):
        perfs = {}
        for c in crits:
            perfs[c.id] = crit_random[c.id][i]
        ap = alternative_performances(a, perfs)
        pt.append(ap)

    return pt

def generate_random_categories_profiles(cats, prefix='b'):
    cat_ids = cats.get_ordered_categories()
    cps = categories_profiles()
    for i in range(len(cats)-1):
        l = limits(cat_ids[i], cat_ids[i+1])
        cp = category_profile("%s%d" % (prefix, i+1), l)
        cps.append(cp)
    return cps

def generate_random_piecewise_linear(gi_min, gi_max, n_segments,
                                     ui_min = 0, ui_max = 1):
    d = ui_max - ui_min
    r = [ ui_min + d * random.random() for i in range(n_segments - 1) ]
    r.append(ui_min)
    r.append(ui_max)
    r.sort()

    interval = (gi_max - gi_min) / n_segments

    f = piecewise_linear([])
    for i in range(n_segments):
        a = point(gi_min + i * interval, r[i])
        b = point(gi_min + (i + 1) * interval, r[i + 1])
        s = segment(a, b)

        f.append(s)

    return f

if __name__ == "__main__":
    alts = generate_random_alternatives(10)
    print(alts)
    crits = generate_random_criteria(5)
    print(crits)
    cv = generate_random_criteria_values(crits)
    print(cv)
    pt = generate_random_performance_table(alts, crits)
    print(pt)
    bpt = generate_random_profiles(alts, crits)
    print(bpt)
    cats = generate_random_categories(3)
    print(cats)
    cps = generate_random_categories_profiles(cats)
    print(cps)
    pl = generate_random_piecewise_linear(0, 5, 3)
    print(pl)
