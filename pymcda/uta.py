from __future__ import division
import bisect

from pymcda.types import AlternativeValue, AlternativesValues
from pymcda.types import AlternativeAssignment
from pymcda.types import AlternativesAssignments
from pymcda.types import Criteria, CriteriaValues, CriteriaFunctions
from pymcda.types import CategoriesValues
from pymcda.types import find_xmcda_tag
from itertools import product
from xml.etree import ElementTree

class Uta(object):

    def __init__(self, criteria = None, cvs = None, cfs = None, id = None):
        self.criteria = criteria
        self.cvs = cvs
        self.cfs = cfs
        self.id = id

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

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

    def to_xmcda(self):
        root = ElementTree.Element('UTA')

        if self.id is not None:
            root.set('id', self.id)

        for obj in ['criteria', 'cvs', 'cfs']:
            mcda = getattr(self, obj)
            mcda.id = obj
            xmcda = mcda.to_xmcda()
            root.append(xmcda)

        return root

    def from_cmda(self, xmcda, id = None):
        xmcda = find_xmcda_tag(xmcda, 'UTA', id)

        self.id = xmcda.get('id')
        setattr(self, 'criteria', Criteria().from_xmcda(xmcda, 'criteria'))
        setattr(self, 'cvs', CriteriaValues().from_xmcda(xmcda, 'cvs'))
        setattr(self, 'cfs', CriteriaFunctions().from_xmcda(xmcda, 'cfs'))

        return self

class AVFSort(Uta):

    def __init__(self, criteria = None, cvs = None, cfs = None,
                 cat_values = None):
        super(AVFSort, self).__init__(criteria, cvs, cfs)
        self.cat_values = cat_values

    @property
    def categories(self):
        return self.cat_values.to_categories()

    @property
    def cat_values(self):
        return self.cvalues

    @cat_values.setter
    def cat_values(self, cat_values):
        self.cvalues = cat_values
        if self.cvalues:
            self.ordered_cat = self.cat_values.get_ordered_categories()
            lower = cat_values.get_upper_limits()
            self.limits = sorted(lower.values())

    def get_assignment(self, ap):
        av = self.global_utility(ap)
        i = bisect.bisect_left(self.limits, av.value)
        if i == len(self.limits):
            cat = self.ordered_cat[-1]
        else:
            cat = self.ordered_cat[i]
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
        if nlower == 0 or nupper == 0:
            return 1

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
        for k in range(1, len(self.ordered_cat)):
            auck_sum += self.auck(aa, pt, k)

        return auck_sum / (len(self.ordered_cat) - 1)

    def to_xmcda(self):
        root = ElementTree.Element('AVFSort')

        if self.id is not None:
            root.set('id', self.id)

        for obj in ['criteria', 'cvs', 'cfs', 'cat_values']:
            mcda = getattr(self, obj)
            mcda.id = obj
            xmcda = mcda.to_xmcda()
            root.append(xmcda)

        return root

    def from_xmcda(self, xmcda, id = None):
        xmcda = find_xmcda_tag(xmcda, 'AVFSort', id)

        self.id = xmcda.get('id')
        setattr(self, 'criteria', Criteria().from_xmcda(xmcda, 'criteria'))
        setattr(self, 'cvs', CriteriaValues().from_xmcda(xmcda, 'cvs'))
        setattr(self, 'cfs', CriteriaFunctions().from_xmcda(xmcda, 'cfs'))
        setattr(self, 'cat_values', CategoriesValues().from_xmcda(xmcda, 'cat_values'))

        return self

