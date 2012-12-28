from __future__ import division
import sys
sys.path.insert(0, "..")
from itertools import product
import math
import random
from mcda.types import alternative_affectation, alternatives_affectations

def get_wrong_assignments(aa, aa_learned):
    l = list()
    for a in aa:
        aid = a.alternative_id
        if aa(aid) != aa_learned(aid):
            l.append(aid)
    return l

def compute_fitness(aa, aa_learned):
    ok = total = 0
    for a in aa:
        aid = a.alternative_id
        if aa(aid) == aa_learned(aid):
            ok += 1
        total += 1
    return ok/total

class meta_electre_tri_profiles():

    def __init__(self, model, pt_sorted, aa_ori):
        self.na = len(aa_ori)
        self.nc = len(model.criteria)
        self.model = model
        self.nprofiles = len(model.profiles)
        self.pt_sorted = pt_sorted
        self.aa_ori = aa_ori
        self.cat = self.categories_rank(self.model.categories)
        self.cat_ranked = self.model.categories
        self.aa_by_cat = self.sort_alternative_by_category(aa_ori)
        self.b0 = pt_sorted.get_worst_ap()
        self.bp = pt_sorted.get_best_ap()
        self.build_concordance_table(aa_ori.keys(), self.model.bpt)
        self.build_assignments_table()

    def categories_rank(self, cat):
        return { cat: i + 1 for i, cat in enumerate(self.model.categories) }

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

    def compute_above_histogram(self, cid, profile, above,
                                cat_b, cat_a, ct):
        w = self.model.cv[cid].value
        lbda = self.model.lbda

        h_above = {}
        num = total = 0
        alts, perfs = self.pt_sorted.get_middle(cid,
                                                profile.performances[cid],
                                                above.performances[cid],
                                                True, True)

        for i, a in enumerate(alts):
            conc = ct[a]
            diff = conc - w
            if self.aa_ori(a) == cat_a:
                if self.aa(a) == cat_a and diff < lbda:
                        # --
                        total += 5
                elif self.aa(a) == cat_b and diff < lbda:
                        # -
                        total += 1
            elif self.aa_ori(a) == cat_b and self.aa(a) == cat_a:
                if diff >= lbda:
                    # +
                    num += 0.5
                    total += 1
                    h_above[perfs[i] + 0.00001] = num / total
                else:
                    # ++
                    num += 2
                    total += 1
                    h_above[perfs[i] + 0.00001] = num / total
            elif self.aa_ori(a) != self.aa(a) and \
                 self.cat[self.aa_ori(a)] < self.cat[cat_a]:
                num += 0.1
                total += 1
                h_above[perfs[i] + 0.00001] = num / total

        return h_above

    def compute_below_histogram(self, cid, profile, below,
                                cat_b, cat_a, ct):
        w = self.model.cv[cid].value
        lbda = self.model.lbda

        h_below = {}
        num = total = 0
        alts, perfs = self.pt_sorted.get_middle(cid,
                                                below.performances[cid],
                                                profile.performances[cid],
                                                True, True)
        alts.reverse()
        perfs.reverse()
        for i, a in enumerate(alts):
            conc = ct[a]
            diff = conc + w
            if self.aa_ori(a) == cat_a and self.aa(a) == cat_b:
                if diff >= lbda:
                    # ++
                    num += 2
                    total += 1
                    h_below[perfs[i] - 0.00001] = num / total
                else:
                    # +
                    num += 0.5
                    total += 1
                    h_below[perfs[i] - 0.00001] = num / total
            elif self.aa_ori(a) == cat_b:
                if self.aa(a) == cat_b and diff >= lbda:
                    # --
                    total += 5
                elif self.aa(a) == cat_a and diff >= lbda:
                    # -
                    total += 1
            elif self.aa_ori(a) != self.aa(a) and \
                 self.cat[self.aa_ori(a)] > self.cat[cat_b]:
                num += 0.1
                total += 1
                h_below[perfs[i] - 0.00001] = num / total

        return h_below

    def histogram_get_max(self, h, current):
        key = None
        val = 0
        diff = 0
        for k, v in h.items():
            if v >= val:
                tmp = abs(current - k)
                if tmp >= diff:
                    key = k
                    val = v
                    diff = tmp
        return key

    def print_histo(self, h):
        val = h.keys()
        val.sort()
        for i in val:
            print i,':', h[i]

    def get_alternative_assignment(self, aid):
        for profile in reversed(self.model.profiles):
            if self.ct[profile][aid] >= self.model.lbda:
                return self.model.categories_profiles[profile].value.upper

        return self.model.categories_profiles[profile].value.lower

    def build_assignments_table(self):
        self.aa = alternatives_affectations()
        for a in self.aa_ori.keys():
            cat = self.get_alternative_assignment(a)
            self.aa.append(alternative_affectation(a, cat))

    def build_concordance_table(self, aids, profiles):
        self.ct = { profile.alternative_id: dict() for profile in profiles }
        for aid, profile in product(aids, profiles):
            ap = self.pt_sorted[aid]
            conc = self.model.concordance(ap, profile)
            self.ct[profile.alternative_id][aid] = conc

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
            self.aa[a].category_id = self.get_alternative_assignment(a)

    def optimize_profile(self, profile, below, above, cat_b, cat_a):
        criteria = self.model.criteria
        p_perfs = profile.performances

        moved = False
        max_val = 0

        cids = self.model.criteria.keys()
        random.shuffle(cids)

        for cid in cids:
            ct = self.ct[profile.alternative_id]

            h_below = self.compute_below_histogram(cid, profile,
                                                   below, cat_b,
                                                   cat_a, ct)
            h_above = self.compute_above_histogram(cid, profile,
                                                   above, cat_b,
                                                   cat_a, ct)
            h = h_below
            h.update(h_above)

            if not h:
                continue

            i = self.histogram_get_max(h, p_perfs[cid])

            r = random.uniform(0, 1)

            if r <= h[i]:
                self.update_tables(profile.alternative_id, cid,
                                   p_perfs[cid], i)
                p_perfs[cid] = i
                moved = True
            elif moved is False and h[i] > max_val:
                max_val = h[i]
                max_cid = cid
                max_move = i

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

if __name__ == "__main__":
    from tools.generate_random import generate_random_alternatives
    from tools.generate_random import generate_random_criteria
    from tools.generate_random import generate_random_criteria_values
    from tools.generate_random import generate_random_performance_table
    from tools.generate_random import generate_random_categories
    from tools.generate_random import generate_random_profiles
    from tools.generate_random import generate_random_categories_profiles
    from tools.utils import normalize_criteria_weights
    from tools.utils import display_affectations_and_pt
    from tools.utils import get_number_of_possible_coallitions
    from tools.sorted import sorted_performance_table
    from mcda.electre_tri import electre_tri_bm
    from mcda.types import alternative_performances
    from mcda.types import performance_table
    from ui.graphic import display_electre_tri_models

    a = generate_random_alternatives(1000)
    c = generate_random_criteria(10)
    cv = generate_random_criteria_values(c, 92)
    normalize_criteria_weights(cv)
    worst = alternative_performances("worst", {crit.id: 0 for crit in c})
    best = alternative_performances("best", {crit.id: 1 for crit in c})
    pt = generate_random_performance_table(a, c)

    cat = generate_random_categories(3)
    cps = generate_random_categories_profiles(cat)
    b = cps.get_ordered_profiles()
    bpt = generate_random_profiles(b, c)

#    lbda = 0.75
    lbda = random.uniform(0.5, 1)

    model = electre_tri_bm(c, cv, bpt, lbda, cps)
    aa = model.pessimist(pt)

    print('Original model')
    print('==============')
    cids = c.keys()
    bpt.display(criterion_ids=cids)
    cv.display(criterion_ids=cids)
    print("lambda: %.7s" % lbda)
    print("number of possible coallitions: %d" %
          get_number_of_possible_coallitions(cv, lbda))

    bpt2 = generate_random_profiles(b, c)
    model2 = electre_tri_bm(c, cv, bpt2, lbda, cps)
    print('Original random profiles')
    print('========================')
    bpt2.display(criterion_ids=cids)

    pt_sorted = sorted_performance_table(pt)
    meta = meta_electre_tri_profiles(model2, pt_sorted, aa)

    for i in range(1, 501):
        f = compute_fitness(aa, meta.aa)
        print('%d: fitness: %g' % (i, f))
        bpt2.display(criterion_ids=cids)
        if f == 1:
            break

        meta.optimize()

    print('Learned model')
    print('=============')
    print("Number of iterations: %d" % i)
    bpt2.display(criterion_ids=cids)
    cv.display(criterion_ids=cids)
    print("lambda: %.7s" % lbda)

    total = len(a)
    nok = 0
    anok = []
    for alt in a:
        if aa(alt.id) != meta.aa(alt.id):
            anok.append(alt)
            nok += 1

    print("Good affectations: %3g %%" % (float(total-nok)/total*100))
    print("Bad affectations : %3g %%" % (float(nok)/total*100))

    if len(anok) > 0:
        print("Alternatives wrongly assigned:")
        display_affectations_and_pt(anok, c, [aa, meta.aa], [pt])

    aps = [ pt["%s" % aid] for aid in anok ]
    display_electre_tri_models([model, model2],
                               [worst, worst], [best, best])
