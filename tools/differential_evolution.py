import sys
sys.path.insert(0, "..")
import random
from mcda.types import criterion_value, criteria_values
from mcda.types import alternatives, alternative
from mcda.types import alternative_performances, performance_table
from tools.generate_random import generate_random_criteria_values
from tools.utils import get_best_alternative_performances
from tools.utils import get_worst_alternative_performances

def mutations_weights(g_weights, best_weights, r_weights, s_weights):
    pass

def mutation(model, best, r, s):
    pass

def mutations(models, best, r, s):
    ba = get_best_alternative_performances(best.pt, best.criteria)
    wa = get_worst_alternative_performances(best.pt, best.criteria)

    new_models = []
    for m in models:
        nm = mutation(model, best, r, s)
        new_models.append(nm)
    return new_models

def crossover(models, cr):
    n = len(models)
    l = random.randint(0, n-1)

    rdom = [ random.random() for i in range(l, n-1) ]
    rdom.sort()

    j = 0
    for i, val in enumerate(rdom):
        if i > 0 and val > cr:
            j = i-1
            break

    return (l, j)

def selection():
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

def compute_models_fitness(models, aa):
    models_fitness = {}
    for m in models:
        p = m.pessimist()
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

    random_model = electre_tri(c, cvals, pt, bpt, lbda)

    return random_model

def initialization(n, c, pt, cats):
    """ Return several ELECTRE TRI models """
    nprofiles = len(cats)-1
    models = []
    for i in range(n):
        model = init_one(c, pt, nprofiles)
        models.append(model)
    return models

def differential_evolution(sample, mc, cr, c, a, aa, pt, cats):
    """ Learn an ELECTRE TRI model """
    models = initialization(sample, c, pt, cats)
    models_fitness = compute_models_fitness(models, aa)

    best_model = get_best_model(models_fitness)
    print(best_model.pessimist())
    [ h_model, s_model ] = get_random_models(models)
    print(h_model, s_model)

    crossover(models, cr)
    mutations(models, best_model, h_model, s_model)

if __name__ == "__main__":
    from tools.generate_random import generate_random_alternatives
    from tools.generate_random import generate_random_criteria
    from tools.generate_random import generate_random_criteria_values
    from tools.generate_random import generate_random_performance_table
    from tools.generate_random import generate_random_categories
    from mcda.electre_tri import electre_tri

    # Create an original arbitrary model
    a = generate_random_alternatives(100)
    c = generate_random_criteria(3)
    cv = generate_random_criteria_values(c, 4567)
    pt = generate_random_performance_table(a, c, 1234)

    b = generate_random_alternatives(2)
    bpt = generate_random_performance_table(b, c, 0123)
    cats = generate_random_categories(3) 

    lbda = 0.6

    model = electre_tri(c, cv, pt, bpt, lbda)
    af = model.pessimist()
    print(af)

    differential_evolution(100, 0.6, 0.6, c, a, af, pt, cats)
