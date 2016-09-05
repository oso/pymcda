from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../../")
from itertools import product
import random
from pymcda.types import AlternativeAssignment, AlternativesAssignments

def eq(a, b, eps=10e-10):
    return abs(a-b) <= eps

class MetaMRSortVetoProfiles4():

    def __init__(self, model, pt_sorted, aa_ori):
        self.na = len(aa_ori)
        self.nc = len(model.criteria)
        self.model = model
        self.nprofiles = len(model.profiles)
        self.pt_sorted = pt_sorted
        self.aa_ori = aa_ori
        self.cat = self.categories_rank()
        self.cat_ranked = self.model.categories
        self.aa_by_cat = self.sort_alternative_by_category(aa_ori)
        self.b0 = pt_sorted.pt.get_worst(model.criteria)
        self.bp = pt_sorted.pt.get_best(model.criteria)
        self.build_concordance_table()
        self.build_assignments_table()

    def categories_rank(self):
        return { cat: i + 1 for i, cat in enumerate(self.model.categories) }

    def sort_alternative_by_category(self, aa):
        aa_by_cat = {}
        for a in aa:
            aid = a.id
            cat = self.cat[a.category_id]
            if cat in aa_by_cat:
                aa_by_cat[cat].append(aid)
            else:
                aa_by_cat[cat] = [ aid ]
        return aa_by_cat

    def compute_above_histogram(self, cid, perf_profile, perf_above,
                                cat_b, cat_a, ct):
        w = self.model.veto_weights[cid].value
        lbda = self.model.veto_lbda
        direction = self.model.criteria[cid].direction
        delta = 0.00001 * direction

        h_above = {}
        num = total = 0
        alts, perfs = self.pt_sorted.get_middle(cid,
                                                perf_profile, perf_above,
                                                True, True)

        for i, a in enumerate(alts):
            if a not in self.aa_ori:
                continue

            if (perfs[i] + delta) * direction > perf_above * direction:
                continue

            conc = ct[a]
            aa_ori = self.aa_ori._d[a].category_id
            aa = self.aa._d[a].category_id
            diff = conc + w
            if aa_ori == cat_a:
                if aa == cat_a and diff >= lbda:
                    # --
                    total += 5
                elif aa == cat_b:
                    # -
                    total += 1
            elif aa_ori == cat_b and aa == cat_a:
                if diff < lbda:
                    # +
                    num += 0.5
                    total += 1
                    h_above[perfs[i]] = num / total
                else:
                    # ++
                    num += 2
                    total += 1
                    h_above[perfs[i]] = num / total
#            elif self.aa_ori(a) < self.aa(a) and \
            elif aa_ori != aa and \
                 self.cat[aa] > self.cat[cat_a] and \
                 self.cat[aa_ori] > self.cat[cat_a]:
                num += 0.1
                total += 1
                h_above[perfs[i] + delta] = num / total

        return h_above

    def compute_below_histogram(self, cid, perf_profile, perf_below,
                                cat_b, cat_a, ct):
        w = self.model.cv[cid].value
        lbda = self.model.lbda
        direction = self.model.criteria[cid].direction
        delta = 0.00001 * direction

        h_below = {}
        num = total = 0
        alts, perfs = self.pt_sorted.get_middle(cid,
                                                perf_profile, perf_below,
                                                True, True)

        for i, a in enumerate(alts):
            if a not in self.aa_ori:
                continue

            conc = ct[a]
            aa_ori = self.aa_ori._d[a].category_id
            aa = self.aa._d[a].category_id
            diff = conc - w
            if aa_ori == cat_a and aa == cat_b:
                if diff < lbda:
                    # ++
                    num += 2
                    total += 1
                    h_below[perfs[i] - delta] = num / total
                else:
                    # +
                    num += 0.5
                    total += 1
                    h_below[perfs[i] - delta] = num / total
            elif aa_ori == cat_b:
                if aa == cat_b and diff < lbda:
                    # --
                    total += 5
                elif aa == cat_a:
                    # -
                    total += 1
#            elif self.aa_ori(a) > self.aa(a) and \
            elif aa_ori != aa and \
                 self.cat[aa] < self.cat[cat_b] and \
                 self.cat[aa_ori] < self.cat[cat_b]:
                num += 0.1
                total += 1
                h_below[perfs[i]] = num / total

        return h_below

    def histogram_choose(self, h, current):
        key = random.choice(h.keys())
        val = h[key]
        diff = abs(current - key)
        for k, v in h.items():
            if v >= val:
                tmp = abs(current - k)
                if tmp > diff:
                    key = k
                    val = v
                    diff = tmp
        return key

    def build_assignments_table(self):
        self.aa = self.model.get_assignments(self.pt_sorted.pt)
        self.good = 0
        for aa in self.aa_ori.values():
            cat_ori = aa.category_id
            if self.aa[aa.id].category_id == cat_ori:
                self.good += 1

    def build_concordance_table(self):
        self.ct = { bp.id: dict() for bp in self.model.vpt }
        for aid, bp in product(self.aa_ori.keys(), self.model.bpt):
            ap = self.pt_sorted[aid]
            conc = 1 - self.model.concordance(ap, bp)
            self.ct[bp.id][aid] = conc

    def update_tables(self, profile, cid, old, new):
        self.build_concordance_table()
        self.build_assignments_table()

    def rebuild_tables(self):
        self.build_concordance_table()
        self.build_assignments_table()

    def optimize_profile(self, profile, below, above, cat_b, cat_a):
        cids = self.model.criteria.keys()
        random.shuffle(cids)

        for cid in cids:
            ct = self.ct[profile.id]

            perf_profile = profile.performances[cid]
            perf_above = above.performances[cid]
            perf_below = below.performances[cid]

            h_below = self.compute_below_histogram(cid, perf_profile,
                                                   perf_below, cat_b,
                                                   cat_a, ct)
            h_above = self.compute_above_histogram(cid, perf_profile,
                                                   perf_above, cat_b,
                                                   cat_a, ct)
            h = h_below
            h.update(h_above)

            if not h:
                continue

            i = self.histogram_choose(h, perf_profile)

            r = random.uniform(0, 1)

            if r <= h[i]:
                profile.performances[cid] = i
                newveto = above - profile
                self.model.veto[profile.id].performances = newveto.performances
                self.update_tables(profile.id, cid, perf_profile, i)

            return profile

    def get_below_and_above_profiles(self, i):
        profiles = self.model.profiles
        bpt = self.model.bpt

        if i == 0:
            below = self.b0
        else:
            vpt = self.model.vpt
            below = vpt[profiles[i-1]]

        above = bpt[profiles[i]]

        return below, above

    def optimize(self):
        profiles = self.model.profiles
        for i, profile in enumerate(profiles):
            pperfs = self.model.vpt[profile]
            below, above = self.get_below_and_above_profiles(i)
            cat_b, cat_a = self.cat_ranked[i], self.cat_ranked[i+1]
            self.optimize_profile(pperfs, below, above, cat_b, cat_a)

        return self.good / self.na

if __name__ == "__main__":
    import time
    from pymcda.generate import generate_random_mrsort_model
    from pymcda.generate import generate_alternatives
    from pymcda.generate import generate_random_performance_table
    from pymcda.generate import generate_random_profiles
    from pymcda.generate import generate_criteria
    from pymcda.generate import generate_categories
    from pymcda.generate import generate_categories_profiles
    from pymcda.utils import print_pt_and_assignments
    from pymcda.utils import compute_number_of_winning_coalitions
    from pymcda.pt_sorted import SortedPerformanceTable
    from pymcda.ui.graphic import display_electre_tri_models
    from pymcda.electre_tri import MRSort
    from pymcda.types import CriterionValue, CriteriaValues
    from pymcda.types import AlternativePerformances, PerformanceTable
    from pymcda.types import AlternativeAssignment, AlternativesAssignments

    # Generate a random ELECTRE TRI BM model
    random.seed(127890123456789)
    ncriteria = 5
    model = MRSort()
    model.criteria = generate_criteria(ncriteria)
    model.cv = CriteriaValues([CriterionValue('c%d' % (i + 1), 0.2)
                               for i in range(ncriteria)])
    b1 = AlternativePerformances('b1', {'c%d' % (i + 1): 0.5
                                        for i in range(ncriteria)})
    model.bpt = PerformanceTable([b1])
    cat = generate_categories(2)
    model.categories_profiles = generate_categories_profiles(cat)
    model.lbda = 0.6
    vb1 = AlternativePerformances('b1', {'c%d' % (i + 1): random.uniform(0,0.4)
                                         for i in range(ncriteria)})
    model.veto = PerformanceTable([vb1])
    model.veto_weights = model.cv.copy()
    model.veto_lbda = 0.4

    # Generate a set of alternatives
    a = generate_alternatives(1000)
    pt = generate_random_performance_table(a, model.criteria)
    aa = model.pessimist(pt)

    worst = pt.get_worst(model.criteria)
    best = b1

    print('Original model')
    print('==============')
    cids = model.criteria.keys()
    model.bpt.display(criterion_ids=cids)
    model.cv.display(criterion_ids=cids)
    print("lambda: %.7s" % model.lbda)
    model.vpt.display(criterion_ids=cids)
    model.veto_weights.display(criterion_ids=cids)

    model2 = model.copy()
    vpt = generate_random_profiles(model.profiles, model.criteria, None, 3,
                                   worst, best)
    model2.veto = PerformanceTable([b1 - vpt[b1.id]])
    print('Original random profiles')
    print('========================')
    model2.vpt.display(criterion_ids = cids)

    pt_sorted = SortedPerformanceTable(pt)
    meta = MetaMRSortVetoProfiles4(model2, pt_sorted, aa)

    t1 = time.time()

    i = 0
    for i in range(0, 100):
        f = meta.good / meta.na
        print('%d: fitness: %g' % (i, f))
#        model2.vpt.display(criterion_ids=cids)
        if f == 1:
            break

        f = meta.optimize()

    t2 = time.time()

    print('%d: fitness: %g' % (i + 1, f))
    model2.vpt.display(criterion_ids=cids)

    print('Learned model')
    print('=============')
    print("Computing time: %d sec" % (t2 - t1))
    print("Number of iterations: %d" % i)
    model2.vpt.display(criterion_ids = cids)
    model2.veto_weights.display(criterion_ids = cids)
    print("lambda: %.7s" % model.veto_lbda)

    aa2 = model2.pessimist(pt)
    if aa2 != meta.aa:
        print('Error in classification accuracy computation!')

    total = len(a)
    nok = 0
    anok = []
    for alt in a:
        if aa(alt.id) != aa2(alt.id):
            anok.append(alt.id)
            nok += 1

    print("Good assignments: %3g %%" % (float(total-nok)/total*100))
    print("Bad assignments : %3g %%" % (float(nok)/total*100))

    if len(anok) > 0:
        print("Alternatives wrongly assigned:")
        print_pt_and_assignments(anok, model.criteria.keys(),
                                 [aa, aa2], pt)

    aps = [ pt["%s" % aid] for aid in anok ]
    worst = pt.get_worst(model.criteria)
    best = pt.get_best(model.criteria)
    display_electre_tri_models([model, model2],
                               [worst, worst], [best, best],
                               [[vb1], [vb1]])
