from __future__ import division
import bisect

from pymcda.types import AlternativeValue, AlternativesValues
from pymcda.types import AlternativeAssignment
from pymcda.types import AlternativesAssignments
from itertools import product

class Uta(object):

    def __init__(self, criteria = None, cvs = None, cfs = None):
        self.criteria = criteria
        self.cvs = cvs
        self.cfs = cfs

    def marginal_utility(self, cid, aps):
        gi = aps(cid)
        cf = self.cfs[cid]
        return cf.function.y(gi)

    def global_utility(self, ap):
        u = 0
        for c in self.cvs:
            w = c.value
            ui = self.marginal_utility(c.id, ap)
            u += w * ui

        av = AlternativeValue(ap.id, u)

        return av

    def global_utilities(self, pt):
        au = AlternativesValues()

        for ap in pt:
            av = self.global_utility(ap)
            au[av.id] = av

        return au

    def set_equal_weights(self):
        self.cvs.normalize()
        self.cfs.multiply_y(self.cvs)
        for cv in self.cvs:
            cv.value = 1

class AVFSort(Uta):

    def __init__(self, criteria = None, cvs = None, cfs = None,
                 cat_values = None):
        super(AVFSort, self).__init__(criteria, cvs, cfs)
        self.cat_values = cat_values
        upper = cat_values.get_upper_limits()
        self.cat_limits = sorted(upper.iteritems(),
                                 key = lambda (k, v): (v, k))
        self.limits = [ cat_limit[1] for cat_limit in self.cat_limits ]

    @property
    def categories(self):
        return self.cat_values.to_categories()

    def get_assignment(self, ap):
        av = self.global_utility(ap)
        i = bisect.bisect_left(self.limits, av.value)
        if i == len(self.limits):
            cat = self.cat_limits[-1][0]
        else:
            cat = self.cat_limits[i][0]
        return AlternativeAssignment(ap.id, cat)

    def get_assignments(self, pt):
        assignments = AlternativesAssignments([])
        for ap in pt:
            assignments.append(self.get_assignment(ap))
        return assignments

    def auck(self, aa, pt, k):
        categories = self.cat_values.get_ordered_categories()
        lower_cat = categories[:k]
        upper_cat = categories[k:]

        lower_aa, upper_aa = {}, {}
        for a in aa:
            cred = self.global_utility(pt[a.id]).value
            if a.category_id in lower_cat:
                lower_aa[a.id] = cred
            else:
                upper_aa[a.id] = cred

        nlower, nupper = len(lower_aa), len(upper_aa)

        score = 0
        for a_up, a_low in product(upper_aa.keys(), lower_aa.keys()):
            a_up_cred, a_low_cred = upper_aa[a_up], lower_aa[a_low]
            if a_up_cred > a_low_cred:
                score += 1
            elif a_up_cred == a_low_cred:
                score += 0.5

        return score / (nlower * nupper)

    def auc(self, aa, pt):
        auck_sum = 0
        for k in range(1, len(self.cat_limits)):
            auck_sum += self.auck(aa, pt, k)

        return auck_sum / (len(self.cat_limits) - 1)
