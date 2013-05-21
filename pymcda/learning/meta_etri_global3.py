from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../../")
import random
from itertools import product
from multiprocessing import Process, Queue
from threading import Thread

from pymcda.electre_tri import ElectreTriBM
from pymcda.types import AlternativeAssignment, AlternativesAssignments
from pymcda.types import PerformanceTable
from pymcda.learning.heur_etri_profiles import HeurEtriProfiles
from pymcda.learning.lp_etri_weights import LpEtriWeights
from pymcda.learning.meta_etri_profiles4 import MetaEtriProfiles4
from pymcda.utils import compute_ca
from pymcda.pt_sorted import SortedPerformanceTable
from pymcda.generate import generate_random_electre_tri_bm_model
from pymcda.generate import generate_alternatives
from pymcda.generate import generate_categories_profiles

class MetaEtriGlobalPop3():

    def __init__(self, nmodels, criteria, categories, pt_sorted, aa_ori):
        self.nmodels = nmodels
        self.models = list()
        self.metas = list()

        for i in range(self.nmodels):
            cps = generate_categories_profiles(categories)
            model = ElectreTriBM(criteria, None, None, None, cps)
            self.models.append(model)
            meta = MetaEtriGlobal3(model, pt_sorted, aa_ori, i)
            self.metas.append(meta)

    def _process_optimize(self, queue, meta, nmeta):
        ca = meta.optimize(nmeta)
        queue.put([ca, meta.model.bpt, meta.model.cv, meta.model.lbda])

    def reinit_worst_models(self):
        meta_ca = [(meta, meta.ca) for meta in self.metas]
        meta_ca = sorted(meta_ca, key = lambda (k,v): (v,k),
                           reverse = True)
        for i in range(int((self.nmodels + 1) / 2), self.nmodels):
            meta_ca[i][0].init_profiles()

    def optimize(self, nmeta):
        self.reinit_worst_models()

        processes = list()
        for meta in self.metas:
            q = Queue()
            p = Process(target = self._process_optimize,
                        args = (q, meta, nmeta))
            processes.append((meta, p, q))

            p.start()

        print 'started'

        for meta, p, q in processes:
            p.join()
            meta.ca, meta.model.bpt, meta.model.cv, meta.model.lbda = q.get()

        print 'joined'

        models_ca = [(meta.model, meta.ca) for meta in self.metas]
        models_ca = sorted(models_ca,
                           key = lambda (k,v): (v,k),
                           reverse = True)

        return models_ca[0][0], models_ca[0][1]

class MetaEtriGlobal3():

    def __init__(self, model, pt_sorted, aa_ori, seed = None):
        if seed is not None:
            random.seed(seed)

        self.model = model
        self.pt_sorted = pt_sorted
        self.aa_ori = aa_ori
        self.ca = 0

        self.init_profiles()
        self.lp = LpEtriWeights(self.model, pt_sorted.pt, self.aa_ori)

        # Because MetaEtriProfiles4 needs weights in initialization
        self.lp.solve()

        self.meta = MetaEtriProfiles4(self.model, pt_sorted, self.aa_ori)

    def init_profiles(self):
        cats = self.model.categories_profiles.to_categories()
        heur = HeurEtriProfiles(self.model, self.pt_sorted, self.aa_ori)
        heur.solve()

    def optimize(self, nmeta):
        self.lp.update_linear_program()
        obj = self.lp.solve()

        self.meta.rebuild_tables()
        ca = self.meta.good / self.meta.na

        best_bpt = self.model.bpt.copy()
        best_ca = ca

        for i in range(nmeta):
            ca = self.meta.optimize()
            if ca > best_ca:
                best_ca = ca
                best_bpt = self.model.bpt.copy()

            if ca == 1:
                break

        self.model.bpt = best_bpt
        self.ca = best_ca
        return best_ca

if __name__ == "__main__":
    import time
    from pymcda.generate import generate_alternatives
    from pymcda.generate import generate_random_performance_table
    from pymcda.utils import display_assignments_and_pt
    from pymcda.utils import compute_winning_coalitions
    from pymcda.types import AlternativePerformances
    from pymcda.ui.graphic import display_electre_tri_models

    # Generate a random ELECTRE TRI BM model
    model = generate_random_electre_tri_bm_model(10, 3, 1)
    worst = AlternativePerformances("worst",
                                     {c.id: 0 for c in model.criteria})
    best = AlternativePerformances("best",
                                    {c.id: 1 for c in model.criteria})

    # Generate a set of alternatives
    a = generate_alternatives(1000)
    pt = generate_random_performance_table(a, model.criteria)
    aa = model.pessimist(pt)

    nmeta = 20
    nloops = 30

    print('Original model')
    print('==============')
    cids = model.criteria.keys()
    model.bpt.display(criterion_ids = cids)
    model.cv.display(criterion_ids = cids)
    print("lambda\t%.7s" % model.lbda)

    ncriteria = len(model.criteria)
    ncategories = len(model.categories)
    pt_sorted = SortedPerformanceTable(pt)

    model2 = generate_random_electre_tri_bm_model(ncriteria, ncategories)

    t1 = time.time()

    meta = MetaEtriGlobalPop3(10, model.criteria,
                              model.categories_profiles.to_categories(),
                              pt_sorted, aa)
    for i in range(nloops):
        model2, ca = meta.optimize(20)
        print ca

    t2 = time.time()
    print("Computation time: %g secs" % (t2-t1))

    print('Learned model')
    print('=============')
    model2.bpt.display(criterion_ids = cids)
    model2.cv.display(criterion_ids = cids)
    print("lambda\t%.7s" % model2.lbda)
    #print(aa_learned)

    aa_learned = model2.pessimist(pt)

    total = len(a)
    nok = 0
    anok = []
    for alt in a:
        if aa(alt.id) <> aa_learned(alt.id):
            anok.append(alt)
            nok += 1

    print("Good assignments: %g %%" % (float(total-nok)/total*100))
    print("Bad assignments : %g %%" % (float(nok)/total*100))

    coal1 = compute_winning_coalitions(model.cv, model.lbda)
    coal2 = compute_winning_coalitions(model2.cv, model2.lbda)
    coali = list(set(coal1) & set(coal2))
    coal1e = list(set(coal1) ^ set(coali))
    coal2e = list(set(coal2) ^ set(coali))

    print("Number of coalitions original: %d"
          % len(coal1))
    print("Number of coalitions learned: %d"
          % len(coal2))
    print("Number of common coalitions: %d"
          % len(coali))
    print("Coallitions in original and not in learned: %s"
          % '; '.join(map(str, coal1e)))
    print("Coallitions in learned and not in original: %s"
          % '; '.join(map(str, coal2e)))

    display_electre_tri_models([model, model2],
                               [worst, worst], [best, best])
