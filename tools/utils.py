import random
from mcda.types import alternative_performances

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
    wa = alternative_performances('w', {})

    for c in crits:
        if c.direction == 1:
            val = get_min_alternative_performance(pt, c)
        else:
            val = get_max_alternative_performance(pt, c)

        wa.performances[c.id] = val

    return wa

def get_best_alternative_performances(pt, crits):
    ba = alternative_performances('b', {})

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

def add_errors_in_affectations(alternatives_affectations, category_ids,
                               errors_pc):
    n = int(len(alternatives_affectations)*errors_pc)
    aa = random.sample(alternatives_affectations, n)

    for a in aa:
        new_cat = cat = None
        while new_cat == cat:
            cat = a.category_id
            newcat = random.sample(category_ids, 1)[0]
            a.category_id = newcat

def display_affectations_and_pt(alternatives, criteria,
                                alternatives_affectations,
                                performance_table):

    for i, aas in enumerate(alternatives_affectations):
        print("\taa%d" % i),
    print('\t|'),
    for i, c in enumerate(criteria):
        print("\t%-6s" % c.id),
    print('')

    for a in alternatives:
        print("%6s" % a.id),
        for aas in alternatives_affectations:
            print("\t%-6s" % aas(a.id)),
        print('\t|'),

        for c in criteria:
            for pt in performance_table:
                print("\t%-6.3f" % pt(a.id, c.id)),
        print('')
