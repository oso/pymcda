import sys
sys.path.insert(0, "..")
import random
from mcda.types import criterion_value, criteria_values
from tools.generate_random import generate_random_criteria_values

def mutation(model, best, r, s):
    pass

def crossover(model):
    pass

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

def fitness(model):
    pass

def init_one(c):
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

def initialization(n, c):
    """ Return several ELECTRE TRI models """
    for i in range(n):
        init_one(c)

def differential_evolution(c, a, aa):
    """ Learn an ELECTRE TRI model """
    initialization(1, c)

if __name__ == "__main__":
    from tools.generate_random import generate_random_alternatives
    from tools.generate_random import generate_random_criteria
    from tools.generate_random import generate_random_criteria_values
    from tools.generate_random import generate_random_performance_table
    from mcda.electre_tri import electre_tri

    # Create an original arbitrary model
    a = generate_random_alternatives(200)
    c = generate_random_criteria(3)
    cv = generate_random_criteria_values(c, 4567)
    pt = generate_random_performance_table(a, c, 1234)

    b = generate_random_alternatives(1)
    bpt = generate_random_performance_table(b, c, 0123)

    lbda = 0.6

    model = electre_tri(c, cv, pt, bpt, lbda)
    af = model.pessimist()

    # Pick 20 alternatives
    a_dm = a[:20]
    af_dm = af[:20]

    differential_evolution(c, a_dm, af_dm)
