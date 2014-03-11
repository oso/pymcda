from __future__ import division
import math
from copy import deepcopy
from itertools import product
from pymcda.types import AlternativeAssignment, AlternativesAssignments
from pymcda.types import Criteria, CriteriaValues, PerformanceTable
from pymcda.types import CategoriesProfiles
from pymcda.types import McdaObject
from pymcda.types import marshal, unmarshal
from xml.etree import ElementTree

def eq(a, b, eps=10e-10):
    return abs(a-b) <= eps

class ElectreTri(McdaObject):

    def __init__(self, criteria = None, cv = None, bpt = None, lbda = None,
                 categories_profiles = None, veto = None, indifference = None,
                 preference = None, id = None):
        self.criteria = criteria
        self.cv = cv
        self.bpt = bpt
        self.lbda = lbda
        self.categories_profiles = categories_profiles
        self.veto = veto
        self.preference = preference
        self.indifference = indifference
        self.id = id

    @property
    def categories_profiles(self):
        return self.cprofiles

    @categories_profiles.setter
    def categories_profiles(self, categories_profiles):
        self.cprofiles = categories_profiles
        if self.cprofiles:
            self.categories = categories_profiles.get_ordered_categories()
            self.profiles = categories_profiles.get_ordered_profiles()

    def __check_input_params(self):
        if self.criteria is None:
            raise KeyError('No criteria specified')
        if self.cv is None:
            raise KeyError('No criteria values specified')
        if self.bpt is None:
            raise KeyError('No profiles performances specified')
        if self.lbda is None:
            raise KeyError('No cut threshold specified')
        if self.categories is None:
            raise KeyError('No categories defined')
        if self.profiles is None:
            raise KeyError('No profiles defined')

    def get_threshold_by_profile(self, c, threshold_id, profile):
        if threshold_id == 'q':
            thresholds = self.indifference
        elif threshold_id == 'p':
            thresholds = self.preference
        elif threshold_id == 'v':
            thresholds = self.veto

        if thresholds is None:
            return self._get_threshold_by_profile(c, threshold_id,
                                                  profile)

        return thresholds[profile].performances[c.id]

    def _get_threshold_by_profile(self, c, threshold_id, profile):
        profile_rank = self.profiles.index(profile) + 1

        if c.thresholds is None:
            return None

        threshid = "%s%s" % (threshold_id, profile_rank)
        if threshid in c.thresholds:
            return c.thresholds[threshid].values.value
        elif threshold_id in c.thresholds:
            return c.thresholds[threshold_id].values.value
        else:
            return None

    def __partial_concordance(self, x, y, c, profile):
        # compute g_j(b) - g_j(a)
        diff = (y.performances[c.id]-x.performances[c.id])*c.direction

        # compute c_j(a, b)
        p = self.get_threshold_by_profile(c, 'p', profile)
        q = self.get_threshold_by_profile(c, 'q', profile)
        if q is None:
            q = 0
        if p is None:
            p = q

        if diff > p:
            return 0
        elif diff <= q:
            return 1
        else:
            num = float(p-diff)
            den = float(p-q)
            return num/den

    def __concordance(self, x, y, profile):
        wsum = 0
        pjcj = 0
        for c in self.criteria:
            if c.disabled == 1:
                continue

            cj = self.__partial_concordance(x, y, c, profile)

            cval = self.cv[c.id]
            weight = cval.value
            wcj = float(weight)*cj

            pjcj += wcj
            wsum += weight

        return pjcj/wsum

    def __partial_discordance(self, x, y, c, profile):
        # compute g_j(b) - g_j(a)
        diff = (y.performances[c.id]-x.performances[c.id])*c.direction

        # compute d_j(a,b)
        p = self.get_threshold_by_profile(c, 'p', profile)
        v = self.get_threshold_by_profile(c, 'v', profile)
        if v is None:
            return 0
        elif diff >= v:
            return 1
        elif p is None or diff <= p:
            return 0
        else:
            num = float(v-diff)
            den = float(v-p)
            return num/den

    def credibility(self, x, y, profile):
        self.__check_input_params()
        concordance = self.__concordance(x, y, profile)

        sigma = concordance
        for c in self.criteria:
            if c.disabled == 1:
                continue

            dj = self.__partial_discordance(x, y, c, profile)
            if dj > concordance:
                num = float(1-dj)
                den = float(1-concordance)
                sigma = sigma*num/den

        return sigma

    def __outrank(self, action_perfs, criteria, profile, lbda):
        s_ab = self.credibility(action_perfs, profile, profile.id)
        s_ba = self.credibility(profile, action_perfs, profile.id)

        if eq(s_ab, lbda) or s_ab > lbda:
            if s_ba >= lbda:
                return "I"
            else:
                return "S"
        else:
            if s_ba >= lbda:
                return "-"
            else:
                return "R"

    def pessimist(self, pt):
        self.__check_input_params()
        profiles = self.profiles[:]
        profiles.reverse()
        assignments = AlternativesAssignments([])
        for action_perfs in pt:
            cat_rank = len(profiles)
            for i, profile in enumerate(profiles):
                s_ab = self.credibility(action_perfs, self.bpt[profile],
                                        profile)
                if not eq(s_ab, self.lbda) and s_ab < self.lbda:
                    cat_rank -= 1

            cat_id = self.categories[cat_rank]
            id = action_perfs.id
            alt_affect = AlternativeAssignment(id, cat_id)
            assignments.append(alt_affect)

        return assignments

    def optimist(self, pt):
        self.__check_input_params()
        profiles = self.profiles
        assignments = AlternativesAssignments([])
        for action_perfs in pt:
            cat_rank = 0
            for i, profile in enumerate(profiles):
                outr = self.__outrank(action_perfs, self.criteria,
                                      self.bpt[profile], self.lbda)
                if outr != "-":
                    cat_rank += 1

            cat_id = self.categories[cat_rank]
            id = action_perfs.id
            alt_affect = AlternativeAssignment(id, cat_id)
            assignments.append(alt_affect)

        return assignments

    PESSIMIST = 0
    OPTIMIST = 1
    def get_assignments(self, pt, procedure = PESSIMIST):
        if procedure == ElectreTri.OPTIMIST:
            return self.optimist(pt)
        else:
            return self.pessimist(pt)

    def auck(self, aa, pt, k):
        profile = self.profiles[k-1]
        lower_cat = self.categories[:k]
        upper_cat = self.categories[k:]

        lower_aa, upper_aa = {}, {}
        for a in aa:
            cred = self.credibility(pt[a.id], self.bpt[profile], profile)
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
        for k in range(1, len(self.profiles) + 1):
            auck_sum += self.auck(aa, pt, k)

        return auck_sum / len(self.profiles)

    def to_xmcda(self):
        root = ElementTree.Element('ElectreTri')

        if self.id is not None:
            root.set('id', self.id)

        for obj in ['criteria', 'cv', 'bpt', 'categories_profiles']:
            xmcda = getattr(self, obj).to_xmcda()
            root.append(xmcda)

        mparams = ElementTree.SubElement(root, 'methodParameters')
        param = ElementTree.SubElement(mparams, 'parameter')
        value = ElementTree.SubElement(param, 'value')
        lbda = marshal(self.lbda)
        value.append(lbda)

        return root

    def from_xmcda(self, xmcda):
        if xmcda.tag != 'ElectreTri':
            raise TypeError('ElectreTri::invalid tag')

        self.id = xmcda.get('id')
        value = xmcda.find('.//methodParameters/parameter/value')
        self.lbda = unmarshal(value.getchildren()[0])

        criteria = xmcda.find('.//criteria')
        setattr(self, 'criteria', Criteria().from_xmcda(criteria))
        cv = xmcda.find('.//criteriaValues')
        setattr(self, 'cv', CriteriaValues().from_xmcda(cv))
        bpt = xmcda.find('.//performanceTable')
        setattr(self, 'bpt', PerformanceTable().from_xmcda(bpt))
        categories_profiles = xmcda.find('.//categoriesProfiles')
        setattr(self, 'categories_profiles',
                CategoriesProfiles().from_xmcda(categories_profiles))

        return self

class MRSort(ElectreTri):

    def __init__(self, criteria = None, cv = None, bpt = None,
                 lbda = None, categories_profiles = None, veto = None,
                 veto_weights = None, veto_lbda = None, id = None):
        super(MRSort, self).__init__(criteria, cv, bpt, lbda,
                                     categories_profiles)
        self.veto = veto
        self.veto_weights = veto_weights
        self.veto_lbda = veto_lbda

    def concordance(self, ap, profile):
        w = wsum = 0
        for c in self.criteria:
            diff = profile.performances[c.id] - ap.performances[c.id]
            diff *= c.direction
            if diff <= 0:
                w += self.cv[c.id].value

            wsum += self.cv[c.id].value

        return w / wsum

    def veto_concordance(self, x, y, profile):
        w = 0
        for c in self.criteria:
            diff = y.performances[c.id] - x.performances[c.id]
            diff *= c.direction
            v = self.get_threshold_by_profile(c, 'v', profile)
            if diff >= v:
                if self.veto_weights is None:
                    return 1
                else:
                    w += self.veto_weights[c.id].value

        return w

    def credibility(self, x, y, profile):
        c = self.concordance(x, y)

        if self.veto is None:
            return c

        vc = self.veto_concordance(x, y, profile)
        if self.veto_lbda and vc >= self.veto_lbda:
            return 0
        elif self.veto_lbda is None and vc >= 0:
            return 0

        return c

    def count_veto_pessimist(self, ap):
        n = 0
        profiles = self.profiles[:]
        profiles.reverse()
        for i, profile in enumerate(profiles):
            c = self.concordance(ap, self.bpt[profile])
            if c < self.lbda:
                continue

            vc = self.veto_concordance(ap, self.bpt[profile], profile)
            if self.veto_lbda and vc >= self.veto_lbda:
                n += 1
            elif self.veto_lbda is None and vc >= 0:
                n += 1

        return n
