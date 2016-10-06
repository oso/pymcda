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
from pymcda.learning.lp_mrsort_weights import LpMRSortWeightsPositive
from pymcda.learning.lp_mrsort_veto_weights import LpMRSortVetoWeights
from pymcda.learning.heur_mrsort_profiles5 import MetaMRSortProfiles5
from pymcda.learning.heur_mrsort_veto_profiles5 import MetaMRSortVetoProfiles5
from pymcda.utils import compute_ca
from pymcda.pt_sorted import SortedPerformanceTable
from pymcda.generate import generate_random_mrsort_model
from pymcda.generate import generate_random_mrsort_model_with_coalition_veto
from pymcda.generate import generate_random_veto_profiles
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

class MetaMRSortVCPop4():

    def __init__(self, nmodels, criteria, categories, pt_sorted, aa_ori,
                 lp_weights = LpMRSortWeightsPositive,
                 heur_profiles = MetaMRSortProfiles5,
                 lp_veto_weights = LpMRSortVetoWeights,
                 heur_veto_profiles= MetaMRSortVetoProfiles5,
                 seed = 0):
        self.nmodels = nmodels
        self.criteria = criteria
        self.categories = categories
        self.pt_sorted = pt_sorted
        self.aa_ori = aa_ori

        self.lp_weights = lp_weights
        self.heur_profiles = heur_profiles
        self.lp_veto_weights = lp_veto_weights
        self.heur_veto_profiles = heur_veto_profiles

        self.metas = list()
        for i in range(self.nmodels):
            meta = self.init_one_meta(i + seed)
            self.metas.append(meta)

    def init_one_meta(self, seed):
        cps = generate_categories_profiles(self.categories)
        model = MRSort(self.criteria, None, None, None, cps)
        model.id = 'model_%d' % seed
        meta = MetaMRSortCV4(model, self.pt_sorted, self.aa_ori,
                             self.lp_weights,
                             self.heur_profiles,
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
        meta.queue.put([ca, meta.model.bpt, meta.model.cv, meta.model.lbda,
                        meta.model.vpt, meta.model.veto_weights,
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
            meta.model.bpt = output[1]
            meta.model.cv = output[2]
            meta.model.lbda = output[3]
            meta.model.vpt = output[4]
            meta.model.veto_weights = output[5]
            meta.model.veto_lbda = output[6]
            meta.random_state = output[7]
            meta.auc = meta.model.auc(self.aa_ori, self.pt_sorted.pt)

        self.models = {meta.model: meta.ca for meta in self.metas}

        metas_sorted = self.sort_models()

        return metas_sorted[0].model, metas_sorted[0].ca

class MetaMRSortCV4():

    def __init__(self, model, pt_sorted, aa_ori,
                 lp_weights = LpMRSortVetoWeights,
                 heur_profiles = MetaMRSortProfiles5,
                 lp_veto_weights = LpMRSortVetoWeights,
                 heur_veto_profiles = MetaMRSortVetoProfiles5):
        self.model = model
        self.pt_sorted = pt_sorted
        self.aa_ori = aa_ori

        self.lp_weights = lp_weights
        self.heur_profiles = heur_profiles
        self.lp_veto_weights = lp_veto_weights
        self.heur_veto_profiles = heur_veto_profiles

        self.init_profiles()

        self.lp = self.lp_weights(self.model, self.pt_sorted.pt, self.aa_ori)
        self.lp.solve()
        self.meta = self.heur_profiles(self.model, self.pt_sorted, self.aa_ori)

        self.ca = self.meta.good / self.meta.na

    def init_profiles(self):
        bpt = generate_random_profiles(self.model.profiles,
                                       self.model.criteria)
        self.model.bpt = bpt
        self.model.vpt = None

    def init_veto_profiles(self):
        worst = self.pt_sorted.pt.get_worst(self.model.criteria)
        vpt = generate_random_veto_profiles(self.model, worst)
        self.model.vpt = vpt

    def optimize(self, nmeta):
        self.lp.update_linear_program()
        self.lp.solve()
        self.meta.rebuild_tables()

        best_ca = self.meta.good / self.meta.na
        best_bpt = self.model.bpt.copy()

        for i in range(nmeta):
            ca = self.meta.optimize()
            if ca > best_ca:
                best_ca = ca
                best_bpt = self.model.bpt.copy()

            if ca == 1:
                break

        self.model.bpt = best_bpt

        if self.model.vpt is None:
            self.init_veto_profiles()
            best_vpt = None
        else:
            best_vpt = self.model.vpt.copy()

        self.vlp = self.lp_veto_weights(self.model, self.pt_sorted.pt, self.aa_ori)
        self.vlp.solve()

        self.vmeta = self.heur_veto_profiles(self.model, self.pt_sorted,
                                                 self.aa_ori)

#        self.vlp.update_linear_program()
#        self.vlp.solve()
        self.vmeta.rebuild_tables()

        best_ca = self.vmeta.good / self.vmeta.na

        for i in range(nmeta):
            ca = self.vmeta.optimize()
            if ca > best_ca:
                best_ca = ca
                best_vpt = self.model.vpt.copy()

            if ca == 1:
                break

        self.model.vpt = best_vpt

        return best_ca


if __name__ == "__main__":
    import time
    import random
    from pymcda.generate import generate_alternatives
    from pymcda.generate import generate_random_performance_table
    from pymcda.generate import generate_random_criteria_weights
    from pymcda.generate import generate_random_mrsort_model_with_coalition_veto
    from pymcda.utils import compute_winning_and_loosing_coalitions
    from pymcda.utils import compute_confusion_matrix, print_confusion_matrix
    from pymcda.types import AlternativePerformances
    from pymcda.ui.graphic import display_electre_tri_models

    # Generate a random ELECTRE TRI BM model
    model = generate_random_mrsort_model_with_coalition_veto(7, 2, 5,
                                                             veto_weights = True)
#    model = generate_random_mrsort_model(7, 2, 1)
    worst = AlternativePerformances("worst",
                                     {c.id: 0 for c in model.criteria})
    best = AlternativePerformances("best",
                                    {c.id: 1 for c in model.criteria})

    # Generate a set of alternatives
    a = generate_alternatives(1000)
    pt = generate_random_performance_table(a, model.criteria)
    aa = model.get_assignments(pt)

    nmeta = 20
    nloops = 10

    print('Original model')
    print('==============')
    cids = model.criteria.keys()
    model.bpt.display(criterion_ids = cids)
    model.cv.display(criterion_ids = cids)
    print("lambda\t%.7s" % model.lbda)
    if model.vpt is not None:
        model.vpt.display(criterion_ids = cids)
    if model.veto_weights is not None:
        model.veto_weights.display(criterion_ids = cids)
        print("veto_lambda\t%.7s" % model.veto_lbda)

    ncriteria = len(model.criteria)
    ncategories = len(model.categories)
    pt_sorted = SortedPerformanceTable(pt)

    t1 = time.time()

    categories = model.categories_profiles.to_categories()
    meta = MetaMRSortVCPop4(10, model.criteria, categories, pt_sorted, aa)
    for i in range(nloops):
        model2, ca = meta.optimize(nmeta)
        print("%d: ca: %f" % (i, ca))
        if ca == 1:
            break

    t2 = time.time()
    print("Computation time: %g secs" % (t2-t1))

    print('Learned model')
    print('=============')
    model2.bpt.display(criterion_ids = cids)
    model2.cv.display(criterion_ids = cids)
    print("lambda\t%.7s" % model2.lbda)
    if model2.vpt is not None:
        model2.vpt.display(criterion_ids = cids)
    if model2.veto_weights is not None:
        model2.veto_weights.display(criterion_ids = cids)
        print("veto_lambda\t%.7s" % model2.veto_lbda)

    aa_learned = model2.get_assignments(pt)

    total = len(a)
    nok = 0
    anok = []
    for alt in a:
        if aa(alt.id) <> aa_learned(alt.id):
            anok.append(alt)
            nok += 1

    print("Good assignments: %g %%" % (float(total-nok)/total*100))
    print("Bad assignments : %g %%" % (float(nok)/total*100))

    matrix = compute_confusion_matrix(aa, aa_learned, model.categories)
    print_confusion_matrix(matrix, model.categories)

    model.id = "original"
    model2.id = "learned"
    display_electre_tri_models([model, model2],
                               [worst, worst], [best, best],
                               [[ap for ap in model.vpt],
                                [ap for ap in model2.vpt]])
