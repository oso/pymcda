import sys
sys.path.insert(0, "..")
import random
from mcda.types import criterion_value, criteria_values
from mcda.types import alternatives, alternative
from mcda.types import alternative_performances, performance_table
from tools.generate_random import generate_random_criteria_values
from tools.utils import get_best_alternative_performances
from tools.utils import get_worst_alternative_performances

def get_crossover_indices(models, cr):
    n = len(models)
    l = random.randint(0, n-1)

    rdom = [ random.random() for i in range(l, n-1) ]
    rdom.sort()

    j = 0
    for i, val in enumerate(rdom):
        if i > 0 and val > cr:
            j = i-1
            break

    return (l, l+j)

def mutation_weights(mc, g, best, h, s):
    cvals = criteria_values()
    for w in g:
        id = w.criterion_id
        val = w.value
        bval = best(id).value
        hval = h(id).value
        sval = s(id).value

        nval = val + mc*(bval-val) + mc*(hval-sval)

        cvals.append(criterion_value(id, nval))

    return cvals

def d_add(a, b):
    return dict( (n, a.get(n, 0)+b.get(n, 0)) for n in set(a)|set(b) )

def d_substract(a, b):
    return dict( (n, a.get(n, 0)-b.get(n, 0)) for n in set(a)|set(b) )

def mutation_profiles(mc, g, b, h, s):
    gnew = []
    for i, profile in enumerate(g):
        alt_id = profile.alternative_id
        diff1 = d_substract(b[i].performances, g[i].performances)
        diff2 = d_substract(h[i].performances, s[i].performances)
        delta = d_add(diff1, diff2)
        mdelta = dict((key, value*mc) for key, value in delta.iteritems())
        gnew_perfs = d_add(g[i].performances, mdelta)

        # Check there are no problem with computed values
        # FIXME: take criteria dir into account and max/min values
        for c, v in gnew_perfs.iteritems():
            if g[i].performances[c] < 0:
                gnew_perfs[c] = random.uniform(0, 1)

            if g[i].performances[c] > 1:
                gnew_perfs[c] = random.uniform(0, 1)

            if i > 0 and v < g[i-1].performances[c]:
                gnew_perfs[c] = random.uniform(g[i-1].performances[c], 1)

        gnew.append(alternative_performances(alt_id, gnew_perfs))

    print g
    print gnew
    return gnew

def mutation(mc, g, best, h, s, ba, wa):
    # First mutation of the weights
    cvals = mutation_weights(mc, g.cv, best.cv, h.cv, s.cv)
    # Then mutation of the profiles
    profiles = mutation_profiles(mc, g.profiles, best.profiles, \
                            h.profiles, s.profiles)
    # Finally mutation of lambda
    g.cv = cvals
    g.profiles = profiles
    return g

def mutations(models, mc, j, l, best, ba, wa):
    muted_models = []
    for i, g in enumerate(models[j:l]):
        [ h, s ] = get_random_models(models)
        gm = mutation(mc, g, best, h, s, ba, wa)
        muted_models.append(gm)
    return muted_models

def selection(models, muted_models):
    pass

def compute_ca(model_af, dm_af):
    """ Compute the ration of alternatives correctly assigned """
    total = len(dm_af)
    ok = float(0)
    for af in dm_af:
        if model_af(af.alternative_id) == af.category_id:
            ok += 1
    return ok/total

def compute_auc_k(model, k):
    """ Compute the probability that an alternative of a group has a higher
    score than an alternative from a worse group """
    pass

def fitness(model, aa):
    return compute_ca(model, aa)

def compute_models_fitness(models, pt, aa):
    models_fitness = {}
    for m in models:
        p = m.pessimist(pt)
        f = fitness(p, aa)
        models_fitness[m] = f

    return models_fitness

def get_best_model(models_fitness):
    best = None
    for m, f in models_fitness.iteritems():
        if best is None or f > best:
            best = f
            model = m
            print(f)

    return model

def get_random_models(models):
    return random.sample(models, 2)

def init_one(c, pt, nprofiles):
    """ Generate a random ELECTRE TRI model"""

    # Initialize lambda value
    lbda = random.uniform(0.6, 0.95)

    # Initialize weights
    cvals = criteria_values()
    for crit in c:
        if crit.disabled == 1:
            continue

        cval = criterion_value()
        cval.criterion_id = crit.id
        cvals.append(cval)

    random_vals = [ 0 , 1 ]
    for cval in range(1, len(cvals)):
        random_vals.append(random.random())

    random_vals.sort()

    for i, cval in enumerate(cvals):
        cval.value = random_vals[i+1]-random_vals[i]

    # Initialize profiles
    b = alternatives()
    bpt = performance_table()
    for i in range(nprofiles):
        id = "b%d" % (i+1)
        b.append(alternative(id))
        bp = alternative_performances(id, {})
        bpt.append(bp)

    worst = get_worst_alternative_performances(pt, c)
    best = get_best_alternative_performances(pt, c)
    for crit in c:
        worst_perf = worst(crit.id)
        best_perf = best(crit.id)
        rval = [ random.uniform(worst_perf, best_perf) \
                    for i in range(nprofiles) ]
        rval.sort()
        for i in range(nprofiles):
            id = "b%d" % (i+1)
            bp = bpt(id)
            bp.performances[crit.id] = rval[i]

    random_model = electre_tri(c, cvals, bpt, lbda)

    return random_model

def initialization(n, c, pt, cats):
    """ Return several ELECTRE TRI models """
    nprofiles = len(cats)-1
    models = []
    for i in range(n):
        model = init_one(c, pt, nprofiles)
        models.append(model)
    return models

def differential_evolution(ngen, pop, mc, cr, c, a, aa, pt, cats):
    """ Learn an ELECTRE TRI model """
    models = initialization(pop, c, pt, cats)
    models_fitness = compute_models_fitness(models, pt, aa)

    # Get worst and best possible alternative
    ba = get_best_alternative_performances(pt, c)
    wa = get_worst_alternative_performances(pt, c)

    for i in range(ngen):
        # First get crossover indices
        l, j = get_crossover_indices(models, cr)

        # Then perform the mutation
        best = get_best_model(models_fitness)
        mutations(models, mc, l, j, best, wa, ba)

if __name__ == "__main__":
    from tools.generate_random import generate_random_alternatives
    from tools.generate_random import generate_random_criteria
    from tools.generate_random import generate_random_criteria_values
    from tools.generate_random import generate_random_performance_table
    from tools.generate_random import generate_random_categories
    from mcda.electre_tri import electre_tri

    # Create an original arbitrary model
    a = generate_random_alternatives(10)
    c = generate_random_criteria(10)
    cv = generate_random_criteria_values(c, 4567)
    pt = generate_random_performance_table(a, c, 1234)

    b = generate_random_alternatives(3)
    bpt = generate_random_performance_table(b, c, 0123)
    cats = generate_random_categories(4)

    lbda = 0.6

    model = electre_tri(c, cv, bpt, lbda)
    af = model.pessimist(pt)
    print(af)

    differential_evolution(1, 100, 0.6, 0.6, c, a, af, pt, cats)
