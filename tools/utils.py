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
