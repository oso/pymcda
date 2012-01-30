import sys
sys.path.insert(0, "..")
import random
from mcda.electre_tri import electre_tri
from mcda.types import alternative_affectation, alternatives_affectations
from tools.lp_electre_tri_weights import lp_elecre_tri_weights
from tools.generate_random import generate_random_categories_profiles
from tools.generate_random import generate_random_alternatives

class meta_electre_tri_global():

    # Input params:
    #   - a: learning alternatives
    #   - c: criteria
    #   - cvals: criteria values
    #   - aa: alternative affectations
    #   - pt : alternative performance table
    #   - cat: categories
    def __init__(self, a, c, cvals, aa, pt, cat):
        self.alternatives = a
        self.criteria = c
        self.criteria_vals = cvals
        self.aa = aa
        self.pt = pt
        self.categories = cat

    def init_one(self):
        model = electre_tri()
        model.criteria = self.criteria
        model.categories = self.categories

        nprofiles = len(self.categories)-1
        self.b = generate_random_alternatives(nprofiles, 'b') # FIXME
        bpt = generate_random_categories_profiles(b, self.criteria)
        model.profiles = bpt
        return model

    def initialization(self, n):
        models = []
        for i in range(n):
            model = self.init_one()
            models.append(model)

        return models

    def compute_fitness(self, aa):
        #print(aa)
        total = len(self.alternatives)
        ok = float(0)
        for alt in self.alternatives:
            if self.aa(alt.id) == aa(alt.id):
                ok += 1

        return ok/total

    def compute_dictatorial_affectations(self, model):
        nprofiles = len(model.profiles)
        ncategories = nprofiles+1
        ptb = model.profiles
        profiles = self.b[:]
        profiles.reverse()

        criteria_fitness = {}
        for criterion in model.criteria:
            aa = alternatives_affectations()
            for alt in self.alternatives:
                i = ncategories
                for profile in profiles:
                    gj_b = ptb(profile.id, criterion.id)
                    gj_a = self.pt(alt.id, criterion.id)
                    if gj_a >= gj_b:
                        break;
                    i -= 1
                af = alternative_affectation(alt.id, i)
                aa.append(af)

            fitness = self.compute_fitness(aa)
            criteria_fitness[criterion.id] = fitness

        return criteria_fitness

    def find_k_worst_criteria(self, criteria_fitness, k):
        #print criteria_fitness
        c_ids = criteria_fitness.keys()
        c_ids.sort(key = criteria_fitness.__getitem__)
        #print c_ids
        return c_ids[0:k]

    def update_profile(self, model, c_ids):
        profiles = self.b
        k = len(c_ids)
        pt_a = model.profiles
        models_b = random.sample(self.models, k)
        for model_b in models_b:
            pt_b = model_b.profiles

            for c_id in c_ids:
                new_perfs = []
                for profile in profiles:
                    new_perfs.append(random.random())

                new_perfs.sort()
                for i, profile in enumerate(profiles):
                    a_p = pt_a(profile.id)
                    a_p.performances[c_id] = new_perfs[i]

## Invert with another model
#                for profile in profiles:
#                    a_p = pt_a(profile.id)
#                    b_p = pt_b(profile.id)
#                    a_p_c = a_p.performances[c_id]
#                    b_p_c = b_p.performances[c_id]
#                    #print a_p, b_p, c_id
#                    a_p.performances[c_id] = b_p_c
#                    b_p.performances[c_id] = a_p_c
#                    #print a_p, b_p

    def loop_one(self, k):
        models_fitness = {}
        for model in self.models:
            criteria_fitness = self.compute_dictatorial_affectations(model)
            c_id = self.find_k_worst_criteria(criteria_fitness, k)

            self.update_profile(model, c_id)

            lpw = lp_elecre_tri_weights(self.alternatives, self.criteria,
                                        self.criteria_vals, self.aa,
                                        self.pt, self.categories, self.b,
                                        model.profiles)
            sol = lpw.solve()

            #print("Objective value: %d" % sol[0])

            model.cv = sol[1]
            #print model.cv
            model.lbda = sol[2]

            aa = model.pessimist(self.pt)
            fitness = self.compute_fitness(aa)
            models_fitness[model] = fitness
            if fitness == 1:
                break

        return models_fitness

    # Input params:
    #   - n: number of loop to do
    #   - m: number of model to generate
    #   - k: k worst criteria to exchange
    def solve(self, n, m, k):
        self.models = self.initialization(m)
        for i in range(n):
            models_fitness = self.loop_one(k)
            m = max(models_fitness, key = lambda a: models_fitness.get(a))
            print(models_fitness[m])

        return m

if __name__ == "__main__":
    import time
    from tools.generate_random import generate_random_alternatives
    from tools.generate_random import generate_random_criteria
    from tools.generate_random import generate_random_criteria_values
    from tools.generate_random import generate_random_performance_table
    from tools.generate_random import generate_random_categories
    from tools.generate_random import generate_random_categories_profiles
    from tools.utils import normalize_criteria_weights
    from mcda.electre_tri import electre_tri

    # Original Electre Tri model
    a = generate_random_alternatives(100)
    c = generate_random_criteria(5)
    cv = generate_random_criteria_values(c, 4567)
    normalize_criteria_weights(cv)
    pt = generate_random_performance_table(a, c, 1234)

    b = generate_random_alternatives(2, 'b')
    bpt = generate_random_categories_profiles(b, c, 2345)
    cat = generate_random_categories(3)

    lbda = 0.75

    model = electre_tri(c, cv, bpt, lbda, cat)
    aa = model.pessimist(pt)

    print('Original model')
    print('==============')
    cids = c.get_ids()
    bpt.display(criterion_ids=cids)
    cv.display(criterion_ids=cids)
    print("lambda\t%.7s" % lbda)
    #print(aa)

    meta_global = meta_electre_tri_global(a, c, cv, aa, pt, cat)

    t1 = time.time()
    m = meta_global.solve(100, 10, 2)
    t2 = time.time()
    print("Computation time: %g secs" % (t2-t1))

    aa_learned = m.pessimist(pt)

    print('Learned model')
    print('=============')
    m.profiles.display(criterion_ids=cids)
    m.cv.display(criterion_ids=cids)
    print("lambda\t%.7s" % m.lbda)
    #print(aa_learned)

    total = len(a)
    nok = 0
    for alt in a:
        if aa(alt.id) <> aa_learned(alt.id):
            print("Pessimits affectation of %s mismatch (%s <> %s)" %
                  (str(alt.id), aa(alt.id), aa_learned(alt.id)))
            nok += 1

    print("Good affectations: %3g %%" % (float(total-nok)/total*100))
    print("Bad affectations : %3g %%" % (float(nok)/total*100))
