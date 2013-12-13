from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../../")
from itertools import product
import random
from pymcda.types import AlternativeAssignment, AlternativesAssignments

class MetaMRSortProfiles4():

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
        w = self.model.cv[cid].value
        lbda = self.model.lbda
        direction = self.model.criteria[cid].direction
        delta = 0.00001 * direction

        h_above = {}
        num = total = 0
        alts, perfs = self.pt_sorted.get_middle(cid,
                                                perf_profile, perf_above,
                                                True, True)

        for i, a in enumerate(alts):
            if (perfs[i] + delta) * direction > perf_above * direction:
                continue

            conc = ct[a]
            aa_ori = self.aa_ori._d[a].category_id
            aa = self.aa._d[a].category_id
            diff = conc - w
            if aa_ori == cat_a:
                if aa == cat_a and diff < lbda:
                    # --
                    total += 5
                elif aa == cat_b:
                    # -
                    total += 1
            elif aa_ori == cat_b and aa == cat_a:
                if diff >= lbda:
                    # +
                    num += 0.5
                    total += 1
                    h_above[perfs[i] + delta] = num / total
                else:
                    # ++
                    num += 2
                    total += 1
                    h_above[perfs[i] + delta] = num / total
#            elif self.aa_ori(a) < self.aa(a) and \
            elif aa_ori != aa and \
                 self.cat[aa] < self.cat[cat_a] and \
                 self.cat[aa_ori] < self.cat[cat_a]:
                num += 0.1
                total += 1
                h_above[perfs[i] + delta] = num / total

        return h_above

    def compute_below_histogram(self, cid, perf_profile, perf_below,
                                cat_b, cat_a, ct):
        w = self.model.cv[cid].value
        lbda = self.model.lbda

        h_below = {}
        num = total = 0
        alts, perfs = self.pt_sorted.get_middle(cid,
                                                perf_profile, perf_below,
                                                True, True)

        for i, a in enumerate(alts):
            conc = ct[a]
            aa_ori = self.aa_ori._d[a].category_id
            aa = self.aa._d[a].category_id
            diff = conc + w
            if aa_ori == cat_a and aa == cat_b:
                if diff >= lbda:
                    # ++
                    num += 2
                    total += 1
                    h_below[perfs[i]] = num / total
                else:
                    # +
                    num += 0.5
                    total += 1
                    h_below[perfs[i]] = num / total
            elif aa_ori == cat_b:
                if aa == cat_b and diff >= lbda:
                    # --
                    total += 5
                elif aa == cat_a:
                    # -
                    total += 1
#            elif self.aa_ori(a) > self.aa(a) and \
            elif aa_ori != aa and \
                 self.cat[aa] > self.cat[cat_b] and \
                 self.cat[aa_ori] > self.cat[cat_b]:
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

    def get_alternative_assignment(self, aid):
        profile = self.model.profiles[0]
        for profile in reversed(self.model.profiles):
            if self.ct[profile][aid] >= self.model.lbda:
                return self.model.categories_profiles[profile].value.upper

        return self.model.categories_profiles[profile].value.lower

    def build_assignments_table(self):
        self.good = 0
        self.aa = AlternativesAssignments()
        for aa in self.aa_ori.values():
            aid = aa.id
            cat = self.get_alternative_assignment(aid)
            self.aa.append(AlternativeAssignment(aid, cat))

            cat_ori = aa.category_id
            if cat == cat_ori:
                self.good += 1

    def build_concordance_table(self):
        self.ct = { bp.id: dict() for bp in self.model.bpt }
        for aid, bp in product(self.aa_ori.keys(), self.model.bpt):
            ap = self.pt_sorted[aid]
            conc = self.model.concordance(ap, bp)
            self.ct[bp.id][aid] = conc

    def rebuild_tables(self):
        self.build_concordance_table()
        self.build_assignments_table()

    def update_tables(self, profile, cid, old, new):
        direction = self.model.criteria[cid].direction
        if old > new:
            if direction == 1:
                down, up = True, False
            else:
                down, up = False, True
            w = self.model.cv[cid].value * direction
        else:
            if direction == 1:
                down, up = False, True
            else:
                down, up = True, False
            w = -self.model.cv[cid].value * direction

        alts, perfs = self.pt_sorted.get_middle(cid, old, new, up, down)

        for a in alts:
            self.ct[profile][a] += w
            old_cat = self.aa[a].category_id
            new_cat = self.get_alternative_assignment(a)
            ori_cat = self.aa_ori[a].category_id

            if old_cat == new_cat:
                continue
            elif old_cat == ori_cat:
                self.good -= 1
            elif new_cat == ori_cat:
                self.good += 1

            self.aa[a].category_id = new_cat

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
                self.update_tables(profile.id, cid, perf_profile, i)
                profile.performances[cid] = i

    def get_below_and_above_profiles(self, i):
        profiles = self.model.profiles
        bpt = self.model.bpt

        if i == 0:
            below = self.b0
        else:
            below = bpt[profiles[i-1]]

        if i == self.nprofiles-1:
            above = self.bp
        else:
            above = bpt[profiles[i+1]]

        return below, above

    def optimize(self):
        profiles = self.model.profiles
        for i, profile in enumerate(profiles):
            pperfs = self.model.bpt[profile]
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
    from pymcda.utils import print_pt_and_assignments
    from pymcda.utils import compute_number_of_winning_coalitions
    from pymcda.pt_sorted import SortedPerformanceTable
    from pymcda.ui.graphic import display_electre_tri_models

    # Generate a random ELECTRE TRI BM model
    model = generate_random_mrsort_model(10, 3, 123)

    # Generate a set of alternatives
    a = generate_alternatives(1000)
    pt = generate_random_performance_table(a, model.criteria)
    aa = model.pessimist(pt)

    worst = pt.get_worst(model.criteria)
    best = pt.get_best(model.criteria)

    print('Original model')
    print('==============')
    cids = model.criteria.keys()
    model.bpt.display(criterion_ids=cids)
    model.cv.display(criterion_ids=cids)
    print("lambda: %.7s" % model.lbda)
    print("number of possible coalitions: %d" %
          compute_number_of_winning_coalitions(model.cv, model.lbda))

    model2 = model.copy()
    model2.bpt = generate_random_profiles(model.profiles, model.criteria)
    print('Original random profiles')
    print('========================')
    model.bpt.display(criterion_ids = cids)

    pt_sorted = SortedPerformanceTable(pt)
    meta = MetaMRSortProfiles4(model2, pt_sorted, aa)

    t1 = time.time()

    i = 0
    for i in range(0, 101):
        f = meta.good / meta.na
        print('%d: fitness: %g' % (i, f))
        model2.bpt.display(criterion_ids=cids)
        if f == 1:
            break

        f = meta.optimize()

    t2 = time.time()

    print('%d: fitness: %g' % (i + 1, f))
    model2.bpt.display(criterion_ids=cids)

    print('Learned model')
    print('=============')
    print("Computing time: %d sec" % (t2 - t1))
    print("Number of iterations: %d" % i)
    model2.bpt.display(criterion_ids = cids)
    model2.cv.display(criterion_ids = cids)
    print("lambda: %.7s" % model.lbda)

    aa2 = model2.pessimist(pt)
    if aa2 != meta.aa:
        print('Error in classification accuracy computation!')

    total = len(a)
    nok = 0
    anok = []
    for alt in a:
        if aa(alt.id) != aa2(alt.id):
            anok.append(alt)
            nok += 1

    print("Good assignments: %3g %%" % (float(total-nok)/total*100))
    print("Bad assignments : %3g %%" % (float(nok)/total*100))

    if len(anok) > 0:
        print("Alternatives wrongly assigned:")
        print_pt_and_assignments(anok, model.criteria, [aa, aa2], pt)

    aps = [ pt["%s" % aid] for aid in anok ]
    display_electre_tri_models([model, model2],
                               [worst, worst], [best, best])
