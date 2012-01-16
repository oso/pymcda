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

def mutation(mc, g, best, h, s):
    return g + mc*(best-g) + mc*(h-s)

def crossover_weights(cr, mc, g, best, h, s):
    cvals = criteria_values()
    for w in g:
        id = w.criterion_id
        val = w.value
        bval = best(id).value
        hval = h(id).value
        sval = s(id).value

        if random.random() < cr:
            nval = mutation(mc, val, bval, hval, sval)
            if nval < 0:
                nval = random.uniform(0, val)
        else:
            nval = val

        cvals.append(criterion_value(criterion_id=id, value=nval))

    return cvals

def crossover_profiles(cr, mc, crit, g, b, h, s, ba, wa):
    gnew = []
    for i, profile in enumerate(g):
        alt_id = g[i].alternative_id
        perfs = g[i].performances
        bperfs = b[i].performances
        hperfs = h[i].performances
        sperfs = s[i].performances
        gnew_perfs = {}
        for c in crit:
            if random.random() < cr:
                g_cr = mutation(mc, perfs[c.id], bperfs[c.id], hperfs[c.id],
                                sperfs[c.id])
            else:
                g_cr = perfs[c.id]

            if c.direction == 1:
                if g_cr < wa.performances[c.id]:
                    g_cr = random.uniform(wa.performances[c.id],
                                          g[i].performances[c.id])
                elif g_cr > ba.performances[c.id]:
                    g_cr = random.uniform(g[i].performances[c.id],
                                          ba.performances[c.id])
            elif c.direction == -1:
                if g_cr > wa.performances[c.id]:
                    g_cr = random.uniform(g[i].performances[c.id],
                                          wa.performances[c.id])
                elif g_cr < ba.performances[c.id]:
                    g_cr = random.uniform(ba.performances[c.id],
                                          g[i].performances[c.id])

            if i > 0:
                if c.direction == 1 and g_cr < g[i-1].performances[c.id]:
                    g_cr = random.uniform(g[i-1].performances[c.id],
                                          ba.performances[c.id])
                elif c.direction == -1 and g_cr > g[i-1].performances[c.id]:
                    g_cr = random.uniform(ba.performances[c.id],
                                          g[i-1].performances[c.id])

            gnew_perfs[c.id] = g_cr

        gnew.append(alternative_performances(alt_id, gnew_perfs))

    return gnew

def crossover_lambda(cr, mc, g_lbda, best_lbda, h_lbda, s_lbda):
    if random.random() < cr:
        new_lbda = g_lbda + mc*(best_lbda-g_lbda) + mc*(h_lbda-g_lbda)
        new_lbda = mutation(mc, g_lbda, best_lbda,  h_lbda, s_lbda)
        if new_lbda < 0.5:
            new_lbda = random.uniform(0.5, g_lbda)
        elif new_lbda > 1:
            new_lbda = random.uniform(g_lbda, 1)
    else:
        new_lbda = g_lbda

    return new_lbda

def crossover(cr, mc, g, best, h, s, ba, wa):
    # First crossover of the weights
    cvals = crossover_weights(cr, mc, g.cv, best.cv, h.cv, s.cv)
    # Then crossover of the profiles
    profiles = crossover_profiles(cr, mc, g.criteria, g.profiles, \
                                  best.profiles, h.profiles, s.profiles, \
                                  ba, wa)
    # Finally crossover of lambda
    lbda = crossover_lambda(cr, mc, g.lbda, best.lbda, h.lbda, s.lbda)

    return electre_tri(g.criteria, cvals, profiles, lbda)

def crossovers(models, cr, mc, best, ba, wa):
    cross_models = []
    for i, g in enumerate(models):
        [ h, s ] = get_random_models(models)
        gm = crossover(cr, mc, g, best, h, s, ba, wa)
        cross_models.append(gm)
    return cross_models

def selection(models, muted_models, pt, aa):
    nmodels = len(models)

    selected_models = []
    for i in range(nmodels):
        muted_fitness = fitness(muted_models[i], pt, aa)
#        print muted_models[i].profiles
#        print muted_models[i].cv
#        print muted_models[i].lbda
        fit = fitness(models[i], pt, aa)
#        print max(muted_fitness, fit)
        if muted_fitness > fit:
            selected_models.append(muted_models[i])
        else:
            selected_models.append(models[i])

    return selected_models

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

def fitness(model, pt, aa):
    return compute_ca(model.pessimist(pt), aa)

def compute_models_fitness(models, pt, aa):
    models_fitness = {}
    for m in models:
        f = fitness(m, pt, aa)
        models_fitness[m] = f

    return models_fitness

def get_best_model(models_fitness):
    best = None
    for m, f in models_fitness.iteritems():
        if best is None or f > best:
            best = f
            model = m

    return best, model

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

    # Get worst and best possible alternative
    ba = get_best_alternative_performances(pt, c)
    wa = get_worst_alternative_performances(pt, c)

    for i in range(ngen):
        models_fitness = compute_models_fitness(models, pt, aa)
        fit_best, best = get_best_model(models_fitness)
        print("%d: fitness: %g" % (i, fit_best))
        print best
        if fit_best == 1:
            return best

        # Perform the crossover (include mutation)
        cross_models = crossovers(models, cr, mc, best, wa, ba)

        # Perform the selection
        selected_models = selection(cross_models, models, pt, aa)

        models = selected_models

    fit_best, best = get_best_model(models_fitness)
    print("fitness: %g" % fit_best)
    return best

if __name__ == "__main__":
    from tools.generate_random import generate_random_alternatives
    from tools.generate_random import generate_random_criteria
    from tools.generate_random import generate_random_criteria_values
    from tools.generate_random import generate_random_performance_table
    from tools.generate_random import generate_random_categories
    from tools.generate_random import generate_random_categories_profiles
    from mcda.electre_tri import electre_tri

    # Create an original arbitrary model
    a = generate_random_alternatives(100)
    c = generate_random_criteria(5)
    cv = generate_random_criteria_values(c, 4567)
    pt = generate_random_performance_table(a, c, 1234)

    b = generate_random_alternatives(2)
    bpt = generate_random_categories_profiles(b, c, 0123)
    cats = generate_random_categories(3)

    lbda = 0.75

    model = electre_tri(c, cv, bpt, lbda)
    af = model.pessimist(pt)

    de_model = differential_evolution(1000, 100, 0.6, 0.6, c, a, af, pt, cats)
    de_af = de_model.pessimist(pt)

    print(af)
    print(de_af)

    print model.cv
    print de_model.cv
