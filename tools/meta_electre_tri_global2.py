from __future__ import division
import sys
sys.path.insert(0, "..")
import random
import logging
from itertools import product

from mcda.electre_tri import electre_tri
from mcda.types import alternative_affectation, alternatives_affectations
from mcda.types import performance_table
from tools.sorted import sorted_performance_table
from tools.lp_electre_tri_weights import lp_electre_tri_weights
from tools.meta_electre_tri_profiles import meta_electre_tri_profiles
from tools.meta_electre_tri_profiles import compute_fitness
from tools.generate_random import generate_random_profiles
from tools.generate_random import generate_random_alternatives
from tools.generate_random import generate_random_criteria_values

logger = logging.getLogger('meta')
hdlr = logging.StreamHandler()
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

def info(*args):
    logger.info(','.join(map(str, args)))

def debug(*args):
    logger.debug(','.join(map(str, args)))

class meta_electre_tri_global():

    def __init__(self, a, c, cps, pt, aa):
        self.alternatives = a
        self.criteria = c
        self.categories_profiles = cps
        self.pt = pt
        self.pt_dict = {ap.alternative_id: ap for ap in self.pt}
        self.pt_sorted = sorted_performance_table(pt)
        self.aa = aa
        self.model = self.init_random_model()
        self.lp = lp_electre_tri_weights(self.model, self.pt, self.aa, cat)
        self.meta = meta_electre_tri_profiles(self.model, self.pt_sorted,
                                              cat, aa)

    def init_random_model(self):
        model = electre_tri()
        model.criteria = self.criteria
        model.categories_profiles = self.categories_profiles

        nprofiles = len(self.categories_profiles)
        self.b = generate_random_alternatives(nprofiles, 'b') # FIXME
        bpt = generate_random_profiles(self.b, self.criteria)
        model.profiles = bpt
        model.cv = generate_random_criteria_values(self.criteria)
        model.lbda = random.uniform(0.5, 1)

        return model

    def __optimize(self):
        aa = self.model.pessimist(self.pt)

        print 'fitness:', compute_fitness(aa, self.aa)
        print 'optimizing profiles...'
        old_profiles = self.model.profiles.copy()
        self.meta.optimize(aa)

        self.model.profiles.display()
        aa = self.model.pessimist(self.pt)
        print 'fitness:', compute_fitness(aa, self.aa)

        a = list()
        for i, profile in enumerate(self.model.profiles):
            for c in self.criteria:
                old = old_profiles[i].performances[c.id]
                new = self.model.profiles[i].performances[c.id]

                l = self.pt_sorted.get_middle(c.id, old, new)
                a.extend(x for x in l if x not in a)

        print 'optimizing weights...'
        self.lp.update_linear_program(a)
        obj = self.lp.solve()
        aa = self.model.pessimist(self.pt)
        print 'lambda:', self.model.lbda, 'w:', self.model.cv
        print 'fitness:', compute_fitness(aa, self.aa)

    def optimize(self, n=5000):
        for i in range(n):
            self.__optimize()

        return self.model

if __name__ == "__main__":
    import time
    from tools.generate_random import generate_random_alternatives
    from tools.generate_random import generate_random_criteria
    from tools.generate_random import generate_random_criteria_values
    from tools.generate_random import generate_random_performance_table
    from tools.generate_random import generate_random_categories
    from tools.generate_random import generate_random_profiles
    from tools.generate_random import generate_random_categories_profiles
    from tools.utils import normalize_criteria_weights
    from tools.utils import display_affectations_and_pt
    from mcda.electre_tri import electre_tri

    # Original Electre Tri model
    a = generate_random_alternatives(5000)
    c = generate_random_criteria(5)
    cv = generate_random_criteria_values(c, 4567)
    normalize_criteria_weights(cv)
    pt = generate_random_performance_table(a, c, 1234)

    b = generate_random_alternatives(2, 'b')
    bpt = generate_random_profiles(b, c, 2345)
    cat = generate_random_categories(3)
    cps = generate_random_categories_profiles(cat)

    lbda = 0.75

    model = electre_tri(c, cv, bpt, lbda, cps)
    aa = model.pessimist(pt)

    print('Original model')
    print('==============')
    cids = c.get_ids()
    bpt.display(criterion_ids=cids)
    cv.display(criterion_ids=cids)
    print("lambda\t%.7s" % lbda)
    #print(aa)

    meta = meta_electre_tri_global(a, c, cat, pt, aa)

    t1 = time.time()
    m = meta.optimize()
    t2 = time.time()
    print("Computation time: %g secs" % (t2-t1))

    aa_learned = m.pessimist(pt)

    print('Learned model')
    print('=============')
    model.profiles.display(criterion_ids=cids)
    m.profiles.display(header=False, criterion_ids=cids, append='_learned')
    model.cv.display(criterion_ids=cids, name='w')
    m.cv.display(header=False, criterion_ids=cids, name='w_learned')
    print("lambda\t%.7s" % m.lbda)
    #print(aa_learned)

    total = len(a)
    nok = 0
    anok = []
    for alt in a:
        if aa(alt.id) <> aa_learned(alt.id):
            anok.append(alt)
            nok += 1

    print("Good affectations: %g %%" % (float(total-nok)/total*100))
    print("Bad affectations : %g %%" % (float(nok)/total*100))

    if len(anok) > 0:
        print("Alternatives and affectations")
        display_affectations_and_pt(anok, c, [aa, aa_learned], [pt])
