from __future__ import division
import sys
sys.path.insert(0, "..")
import math
import random
from itertools import product
from mcda.types import alternative_assignment, alternatives_assignments

class meta_electre_tri_profiles():

    def __init__(self, model, pt_sorted, aa_ori):
        self.na = len(aa_ori)
        self.model = model
        self.nprofiles = len(model.profiles)
        self.pt_sorted = pt_sorted
        self.aa_ori = aa_ori
        self.cat = self.categories_rank(self.model.categories)
        self.cat_ranked = self.model.categories
        self.aa_by_cat = self.sort_alternative_by_category(aa_ori)
        self.b0 = pt_sorted.get_worst_ap()
        self.bp = pt_sorted.get_best_ap()
        self.compute_interval_ratios(3)
        self.build_concordance_table()
        self.build_assignments_table()

    def categories_rank(self, cat):
        return { cat: i + 1 for i, cat in enumerate(self.model.categories) }

    def compute_interval_ratios(self, n):
        self.nintervals = n
        intervals = []
        for i in range(n-1):
            intervals += [ math.exp(i+1) ]
        s = sum(intervals)
        self.interval_ratios = [ i/s for i in intervals ] + [ 0.9 ]

    def update_intervals(self, fitness):
        if fitness > 0.99:
            self.compute_interval_ratios(8)
        elif fitness > 0.95:
            self.compute_interval_ratios(6)
        elif fitness > 0.9:
            self.compute_interval_ratios(5)
        else:
            self.compute_interval_ratios(4)

    def rank_categories(self, cat):
        c_rank = { c.id: c.rank for c in cat }
        return sorted([ cat for (cat, rank) in c_rank.items() ])

    def sort_alternative_by_category(self, aa):
        aa_by_cat = {}
        for a in aa:
            aid = a.alternative_id
            cat = self.cat[a.category_id]
            if cat in aa_by_cat:
                aa_by_cat[cat].append(aid)
            else:
                aa_by_cat[cat] = [ aid ]
        return aa_by_cat

    def get_alternative_assignment(self, aid):
        for profile in reversed(self.model.profiles):
            if self.ct[profile][aid] >= self.model.lbda:
                return self.model.categories_profiles[profile].value.upper

        return self.model.categories_profiles[profile].value.lower

    def build_assignments_table(self):
        self.good = 0
        self.aa = alternatives_assignments()
        for aa in self.aa_ori.values():
            aid = aa.alternative_id
            cat = self.get_alternative_assignment(aid)
            self.aa.append(alternative_assignment(aid, cat))

            cat_ori = aa.category_id
            if cat == cat_ori:
                self.good += 1

    def build_concordance_table(self):
        self.ct = { bp.alternative_id: dict() for bp in self.model.bpt }
        for aid, bp in product(self.aa_ori.keys(), self.model.bpt):
            ap = self.pt_sorted[aid]
            conc = self.model.concordance(ap, bp)
            self.ct[bp.alternative_id][aid] = conc

    def rebuild_tables(self):
        self.build_concordance_table()
        self.build_assignments_table()

    def update_tables(self, profile, cid, old, new):
        if old > new:
            down, up = True, False
            w = self.model.cv[cid].value
        else:
            down, up = False, True
            w = -self.model.cv[cid].value

        alts, perfs = self.pt_sorted.get_middle(cid, old, new,
                                                up, down)

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

    def compute_above_histogram(self, cid, profile, above, cat_b, cat_a):
        h_above = {}
        size = above - profile
        intervals = [ profile + self.interval_ratios[i]*size \
                      for i in range(self.nintervals) ]
        intervals = [ profile ] + intervals
        ok = nok = 0
        for i in range(self.nintervals):
            alts = self.pt_sorted.get_middle(cid, intervals[i],
                                             intervals[i+1])[0]
            for a in alts:
                if self.aa(a) == cat_b and self.aa_ori(a) == cat_a:
                    ok += 1
                elif self.aa(a) == cat_a:
                    if self.aa_ori(a) == cat_a:
                        ok += 1
                    elif self.aa_ori(a) == cat_b:
                        nok += 1

            if (ok + nok) > 0:
                h_above[intervals[i+1]] = nok / (ok + nok)
            else:
                h_above[intervals[i+1]] = 0

        return h_above

    def compute_below_histogram(self, cid, profile, below, cat_b, cat_a):
        h_below = {}
        size = profile - below
        intervals = [ profile - self.interval_ratios[i]*size \
                      for i in range(self.nintervals) ]
        intervals = [ profile ] + intervals
        ok = nok = 0
        for i in range(self.nintervals):
            alts = self.pt_sorted.get_middle(cid, intervals[i+1],
                                             intervals[i])[0]
            for a in alts:
                if self.aa(a) == cat_a and self.aa_ori(a) == cat_b:
                    ok += 1
                elif self.aa(a) == cat_b:
                    if self.aa_ori(a) == cat_b:
                        ok += 1
                    elif self.aa_ori(a) == cat_a:
                        nok += 1

            if (ok + nok) > 0:
                h_below[intervals[i+1]] = nok / (ok + nok)
            else:
                h_below[intervals[i+1]] = 0

        return h_below

    def optimize_profile(self, profile, below, above, cat_b, cat_a):
        criteria = self.model.criteria
        p_perfs = profile.performances
        a_perfs = above.performances
        b_perfs = below.performances

        moved = False
        max_val = 0

        for c in self.model.criteria:
            cid = c.id
            h_below = self.compute_below_histogram(cid, p_perfs[cid],
                                                   b_perfs[cid], cat_b,
                                                   cat_a)
            h_above = self.compute_above_histogram(cid, p_perfs[cid],
                                                   a_perfs[cid], cat_b,
                                                   cat_a)

            i_b = max(h_below, key=h_below.get)
            i_a = max(h_above, key=h_above.get)
            r = random.random()

            if h_below[i_b] > h_above[i_a]:
                size = (p_perfs[cid] - b_perfs[cid])
                if r < h_below[i_b]:
                    self.update_tables(profile.alternative_id, cid,
                                       p_perfs[cid], i_b)

                    p_perfs[cid] = i_b
                    moved = True
                elif moved is False and h_below[i_b] > max_val:
                    max_val = h_below[i_b]
                    max_cid = cid
                    max_move = i_b
            elif h_below[i_b] < h_above[i_a]:
                size = (a_perfs[cid] - p_perfs[cid])
                if r < h_above[i_a]:
                    self.update_tables(profile.alternative_id, cid,
                                       p_perfs[cid], i_a)
                    p_perfs[cid] = i_a
                    moved = True
                elif moved is False and h_above[i_a] > max_val:
                    max_val = h_above[i_a]
                    max_cid = cid
                    max_move = i_a
            elif r > 0.5:
                size = (p_perfs[cid] - b_perfs[cid])
                r2 = random.random()
                if r2 < h_below[i_b]:
                    self.update_tables(profile.alternative_id, cid,
                                       p_perfs[cid], i_b)
                    p_perfs[cid] = i_b
                    moved = True
                elif moved is False and h_below[i_b] > max_val:
                    max_val = h_below[i_b]
                    max_cid = cid
                    max_move = i_b
            elif r < 0.5:
                size = (a_perfs[cid] - p_perfs[cid])
                r2 = random.random()
                if r2 < h_above[i_a]:
                    self.update_tables(profile.alternative_id, cid,
                                       p_perfs[cid], i_a)
                    p_perfs[cid] = i_a
                    moved = True
                elif moved is False and h_above[i_a] > max_val:
                    max_val = h_above[i_a]
                    max_cid = cid
                    max_move = i_a

        if moved is False and max_val > 0:
            self.update_tables(profile.alternative_id, max_cid,
                               p_perfs[max_cid], max_move)
            p_perfs[max_cid] = max_move

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
            self.update_intervals(self.good / self.na)
            self.optimize_profile(pperfs, below, above, cat_b, cat_a)

        return self.good / self.na

if __name__ == "__main__":
    from tools.generate_random import generate_random_electre_tri_bm_model
    from tools.generate_random import generate_random_alternatives
    from tools.generate_random import generate_random_performance_table
    from tools.generate_random import generate_random_profiles
    from tools.utils import normalize_criteria_weights
    from tools.utils import display_affectations_and_pt
    from tools.utils import add_errors_in_affectations
    from tools.utils import compute_ca
    from tools.sorted import sorted_performance_table
    from mcda.types import alternatives_assignments, performance_table
    from mcda.types import alternative_performances
    from mcda.electre_tri import electre_tri_bm
    from ui.graphic import display_electre_tri_models

    # Generate a random ELECTRE TRI BM model
    model = generate_random_electre_tri_bm_model(10, 3, 83)
    worst = alternative_performances("worst",
                                     {c.id: 0 for c in model.criteria})
    best = alternative_performances("best",
                                    {c.id: 1 for c in model.criteria})

    # Generate a set of alternatives
    a = generate_random_alternatives(1000)
    pt = generate_random_performance_table(a, model.criteria)
    aa = model.pessimist(pt)

    errors = 0.0
    nlearn = 1.0

    model2 = model.copy()
    model2.bpt = generate_random_profiles(model.profiles, model.criteria)

    a_learn = random.sample(a, int(nlearn*len(a)))
    aa_learn = alternatives_assignments([ aa[alt.id] for alt in a_learn ])
    pt_learn = performance_table([ pt[alt.id] for alt in a_learn ])

    aa_err = aa_learn.copy()
    aa_erroned = add_errors_in_affectations(aa_err, model.categories,
                                            errors)

    print('Original model')
    print('==============')
    cids = model.criteria.keys()
    model.bpt.display(criterion_ids = cids,
                      alternative_ids = model.profiles)
    model.cv.display(criterion_ids = cids)
    print("lambda: %.7s" % model.lbda)

    print('Original random profiles')
    print('========================')
    model2.bpt.display(criterion_ids = cids,
                       alternative_ids = model2.profiles)

    pt_sorted = sorted_performance_table(pt_learn)
    meta = meta_electre_tri_profiles(model2, pt_sorted, aa_err)

    f = meta.good / meta.na
    best_f = f
    best_bpt = model2.bpt.copy()
    for i in range(0, 501):
        print('%d: fitness: %g' % (i, f))
        model2.bpt.display(criterion_ids = cids,
                           alternative_ids = model2.profiles)
        if f >= best_f:
            best_f = f
            best_bpt = model2.bpt.copy()

        if f == 1:
            break

        f = meta.optimize()

    model2.bpt = best_bpt
    aa2 = model2.pessimist(pt_learn)
    f = compute_ca(aa_err, aa2)

    print('Learned model')
    print('=============')
    print("Number of iterations: %d" % i)
    print("Fitness score: %g %%" % (float(f) * 100))
    model2.bpt.display(criterion_ids = cids,
                       alternative_ids = model2.profiles)
    model2.cv.display(criterion_ids=cids)
    print("lambda: %.7s" % model2.lbda)

    aa2 = model2.pessimist(pt)
    total = len(a)
    nok = nok_erroned = 0
    anok = []
    for alt in a:
        if aa(alt.id) != aa2(alt.id):
            anok.append(alt)
            nok += 1
            if alt.id in aa_erroned:
                nok_erroned += 1

    print("Good affectations          : %3g %%" \
          % (float(total-nok)/total*100))
    print("Bad affectations           : %3g %%" \
          % (float(nok)/total*100))
    if aa_erroned:
        print("Bad in erroned affectations: %3g %%" \
              % (float(nok_erroned)/total*100))

    if len(anok) > 0:
        print("Alternatives wrongly assigned:")
        display_affectations_and_pt(anok, model.criteria, [aa, aa2], [pt])

    display_electre_tri_models([model, model2],
                               [worst, worst], [best, best])
