from __future__ import division
import errno
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../../")
import random
import math
from itertools import product
from multiprocessing import Pool, Process, Queue
from threading import Thread

from pymcda.electre_tri import MRSort
from pymcda.types import AlternativeAssignment, AlternativesAssignments
from pymcda.types import PerformanceTable
from pymcda.learning.heur_mrsort_init_veto_profiles import HeurMRSortInitVetoProfiles
from pymcda.learning.lp_mrsort_veto_weights import LpMRSortVetoWeights
from pymcda.learning.heur_mrsort_veto_profiles4 import MetaMRSortVetoProfiles4
from pymcda.utils import compute_ca
from pymcda.pt_sorted import SortedPerformanceTable
from pymcda.generate import generate_random_mrsort_model
from pymcda.generate import generate_alternatives
from pymcda.generate import generate_categories_profiles
from pymcda.generate import generate_random_profiles

def queue_get_retry(queue):
    while True:
        try:
            return queue.get()
        except IOError, e:
            if e.errno == errno.EINTR:
                continue
            else:
                raise

class MetaMRSortVCPop3():

    def __init__(self, nmodels, model, pt_sorted, aa_ori,
                 heur_init_profiles = HeurMRSortInitVetoProfiles,
                 lp_veto_weights = LpMRSortVetoWeights,
                 heur_veto_profiles= MetaMRSortVetoProfiles4,
                 seed = 0):
        self.nmodels = nmodels
        self.model = model
        self.categories = model.categories_profiles.to_categories()
        self.pt_sorted = pt_sorted
        self.aa_ori = aa_ori

        self.heur_init_profiles = heur_init_profiles
        self.lp_veto_weights = lp_veto_weights
        self.heur_veto_profiles = heur_veto_profiles

        self.metas = list()
        for i in range(self.nmodels):
            meta = self.init_one_meta(i + seed)
            self.metas.append(meta)

    def init_one_meta(self, seed):
        cps = generate_categories_profiles(self.categories)
        model = self.model.copy()
        meta = MetaMRSortCV3(model, self.pt_sorted, self.aa_ori,
                             self.heur_init_profiles,
                             self.lp_veto_weights,
                             self.heur_veto_profiles)
        random.seed(seed)
        meta.random_state = random.getstate()
        meta.auc = meta.model.auc(self.aa_ori, self.pt_sorted.pt)
        return meta

    def sort_models(self):
        metas_sorted = sorted(self.metas, key = lambda (k): k.ca,
                              reverse = True)
        return metas_sorted

    def reinit_worst_models(self):
        metas_sorted = self.sort_models()
        nmeta_to_reinit = int(math.ceil(self.nmodels / 2))
        for meta in metas_sorted[nmeta_to_reinit:]:
            meta.init_profiles()

    def _process_optimize(self, meta, nmeta):
        random.setstate(meta.random_state)
        ca = meta.optimize(nmeta)
        meta.queue.put([ca, meta.model.veto, meta.model.veto_weights,
                        meta.model.veto_lbda, random.getstate()])

    def optimize(self, nmeta):
        self.reinit_worst_models()

        for meta in self.metas:
            meta.queue = Queue()
            meta.p = Process(target = self._process_optimize,
                             args = (meta, nmeta))
            meta.p.start()

        for meta in self.metas:
            output = queue_get_retry(meta.queue)

            meta.ca = output[0]
            meta.model.veto = output[1]
            meta.model.veto_weights = output[2]
            meta.model.veto_lbda = output[3]
            meta.random_state = output[4]
            meta.auc = meta.model.auc(self.aa_ori, self.pt_sorted.pt)

        self.models = {meta.model: meta.ca for meta in self.metas}

        metas_sorted = self.sort_models()

        return metas_sorted[0].model, metas_sorted[0].ca

class MetaMRSortVCPop3AUC(MetaMRSortVCPop3):

    def sort_models(self):
        metas_sorted = sorted(self.metas, key = lambda (k): k.auc,
                              reverse = True)
        return metas_sorted

class MetaMRSortCV3():

    def __init__(self, model, pt_sorted, aa_ori,
                 heur_init_profiles = HeurMRSortInitVetoProfiles,
                 lp_weights = LpMRSortVetoWeights,
                 heur_profiles = MetaMRSortVetoProfiles4):
        self.model = model
        self.pt_sorted = pt_sorted
        self.aa_ori = aa_ori

        self.heur_init_profiles = heur_init_profiles
        self.lp_weights = lp_weights
        self.heur_profiles = heur_profiles

        self.ca = 0

        self.init_profiles()
        self.lp = self.lp_weights(self.model, pt_sorted.pt, self.aa_ori)

        # Because MetaMRSortProfiles4 needs weights in initialization
        self.lp.solve()

        self.meta = self.heur_profiles(self.model, pt_sorted, self.aa_ori)

    def init_profiles(self):
#        heur = self.heur_init_profiles(self.model, self.pt_sorted, self.aa_ori)
#        heur.solve()
        cats = self.model.categories_profiles.to_categories()
        vpt = generate_random_profiles(self.model.profiles,
                                       self.model.criteria, None, 3,
                                       self.pt_sorted.pt.get_worst(self.model.criteria),
                                       self.model.bpt['b1'])
        self.model.veto = PerformanceTable([self.model.bpt['b1'] - vpt['b1']])

    def optimize(self, nmeta):
        self.lp.update_linear_program()
        obj = self.lp.solve()

        self.meta.update_tables()
        ca = self.meta.good / self.meta.na

        best_veto = self.model.veto.copy()
        best_ca = ca

        for i in range(nmeta):
            ca = self.meta.optimize()
            if ca > best_ca:
                best_ca = ca
                best_veto = self.model.veto.copy()

            if ca == 1:
                break

        self.model.veto = best_veto
        self.ca = best_ca
        return best_ca


if __name__ == "__main__":
    import time
    import random
    from pymcda.generate import generate_alternatives
    from pymcda.generate import generate_random_performance_table
    from pymcda.generate import generate_random_criteria_weights
    from pymcda.utils import compute_winning_and_loosing_coalitions
    from pymcda.types import AlternativePerformances
    from pymcda.ui.graphic import display_electre_tri_models

    # Generate a random ELECTRE TRI BM model
    model = generate_random_mrsort_model(5, 2, 1)
    worst = AlternativePerformances("worst",
                                     {c.id: 0 for c in model.criteria})
    best = AlternativePerformances("best",
                                    {c.id: 1 for c in model.criteria})

    # Add veto
    vpt = generate_random_profiles(model.profiles, model.criteria, None, 3,
                                   worst, model.bpt['b1'])
    model.veto = PerformanceTable([model.bpt['b1'] - vpt['b1']])
    model.veto_weights = generate_random_criteria_weights(model.criteria)
    model.veto_lbda = random.random()

    # Generate a set of alternatives
    a = generate_alternatives(1000)
    pt = generate_random_performance_table(a, model.criteria)
    aa = model.pessimist(pt)

    nmeta = 20
    nloops = 10

    print('Original model')
    print('==============')
    cids = model.criteria.keys()
    model.bpt.display(criterion_ids = cids)
    model.cv.display(criterion_ids = cids)
    print("lambda\t%.7s" % model.lbda)
    model.veto.display(criterion_ids = cids)
    model.veto_weights.display(criterion_ids = cids)
    print("veto_lambda\t%.7s" % model.veto_lbda)

    ncriteria = len(model.criteria)
    ncategories = len(model.categories)
    pt_sorted = SortedPerformanceTable(pt)

    model2 = model.copy()
    model2.veto = None
    model2.veto_weights = None
    model2.veto_lambda = None
    aa2 = model2.pessimist(pt)
    print(compute_ca(aa, aa2))

    t1 = time.time()

    meta = MetaMRSortVCPop3(10, model2,
                            pt_sorted, aa)
    for i in range(nloops):
        model2, ca = meta.optimize(nmeta)
        print("%d: ca: %f" % (i, ca))

    t2 = time.time()
    print("Computation time: %g secs" % (t2-t1))

    print('Learned model')
    print('=============')
    model2.bpt.display(criterion_ids = cids)
    model2.cv.display(criterion_ids = cids)
    print("lambda\t%.7s" % model2.lbda)
    model2.veto.display(criterion_ids = cids)
    model2.veto_weights.display(criterion_ids = cids)
    print("veto_lambda\t%.7s" % model2.veto_lbda)

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

    display_electre_tri_models([model, model2],
                               [worst, worst], [best, best])
