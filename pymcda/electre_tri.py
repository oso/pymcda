from __future__ import division
import math
from copy import deepcopy
from itertools import product
from pymcda.types import AlternativeAssignment, AlternativesAssignments
from pymcda.types import AlternativePerformances
from pymcda.types import Criteria, CriteriaValues, PerformanceTable
from pymcda.types import CategoriesProfiles
from pymcda.types import McdaObject
from pymcda.types import marshal, unmarshal
from pymcda.types import find_xmcda_tag
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

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

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
            diff = a_up_cred - a_low_cred
            if abs(diff) < 1e-8:
                score += 0.5
            elif diff > 0:
                score += 1

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
            mcda = getattr(self, obj)
            mcda.id = obj
            xmcda = mcda.to_xmcda()
            root.append(xmcda)

        mparams = ElementTree.SubElement(root, 'methodParameters')
        param = ElementTree.SubElement(mparams, 'parameter')
        value = ElementTree.SubElement(param, 'value')
        value.set('id', 'lambda')
        lbda = marshal(self.lbda)
        value.append(lbda)

        return root

    def from_xmcda(self, xmcda, id = None):
        xmcda = find_xmcda_tag(xmcda, 'ElectreTri', id)

        self.id = xmcda.get('id')
        value = xmcda.find(".//methodParameters/parameter/value[@id='lambda']")
        self.lbda = unmarshal(value.getchildren()[0])

        setattr(self, 'criteria', Criteria().from_xmcda(xmcda, 'criteria'))
        setattr(self, 'cv', CriteriaValues().from_xmcda(xmcda, 'cv'))
        setattr(self, 'bpt', PerformanceTable().from_xmcda(xmcda, 'bpt'))
        setattr(self, 'categories_profiles',
                CategoriesProfiles().from_xmcda(xmcda,
                                                'categories_profiles'))

        return self

class MRSort(ElectreTri):

    def __init__(self, criteria = None, cv = None, bpt = None,
                 lbda = None, categories_profiles = None, veto = None,
                 veto_weights = None, veto_lbda = None):
        super(MRSort, self).__init__(criteria, cv, bpt, lbda,
                                     categories_profiles)
        self.veto = veto
        self.veto_weights = veto_weights
        self.veto_lbda = veto_lbda

    @property
    def veto(self):
        if self.vpt is None:
            return None

        veto = PerformanceTable()
        for bp in self.bpt:
            vbp = bp - self.vpt[bp.id]
            veto.append(vbp)
        return veto

    @veto.setter
    def veto(self, veto):
        if veto is None:
            self.vpt = None
            return

        self.vpt = PerformanceTable()
        for bp in self.bpt:
            vbp = bp - veto[bp.id]
            self.vpt.append(vbp)

    def criteria_coalition(self, ap1, ap2):
        criteria_set = set()

        for c in self.criteria:
            diff = ap2.performances[c.id] - ap1.performances[c.id]
            diff *= c.direction
            if diff <= 0:
                criteria_set.add(c.id)

        return criteria_set

    def concordance(self, ap, profile):
        criteria_set = self.criteria_coalition(ap, profile)
        return sum([c.value for c in self.cv
                    if c.id_issubset(criteria_set) is True])

    def coalition_weight(self, criteria_coalition):
        return sum([c.value for c in self.cv
                   if c.id_issubset(criteria_coalition) is True])

    def veto_concordance(self, ap, profile):
        if self.bpt is None:
            return 0

        criteria_set = self.criteria_coalition(profile, ap)
        if self.veto_weights is None:
            if len(criteria_set) > 0:
                return 1
            else:
                return 0

        return sum([c.value for c in self.veto_weights
                    if c.id_issubset(criteria_set) is True])

    def get_assignment(self, ap):
        categories = list(reversed(self.categories))
        cat = categories[0]
        for i, profile in enumerate(reversed(self.profiles)):
            bp = self.bpt[profile]
            cw = self.concordance(ap, bp)
            if cw >= self.lbda:
                if self.vpt is None:
                    break
                else:
                    vp = self.vpt[profile]
                    vw = self.veto_concordance(ap, vp)
                    if self.veto_lbda and vw < self.veto_lbda:
                        break

                    if vw == 0:
                        break

            cat = categories[i + 1]

        return AlternativeAssignment(ap.id, cat)

    def get_assignments(self, pt):
        aa = AlternativesAssignments()
        for ap in pt:
            a = self.get_assignment(ap)
            aa.append(a)
        return aa

    def pessimist(self, pt):
        return self.get_assignments(pt)

    def credibility(self, x, y, profile):
        c = self.concordance(x, y)

        if self.vpt is None:
            return c

        vp = self.vpt[profile]
        vc = self.veto_concordance(x, vp)
        if self.veto_lbda and (eq(vc, self.veto_lbda)
                               or vc > self.veto_lbda):
            return 0
        elif self.veto_lbda is None and vc > 0:
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

            vc = self.veto_concordance(ap, self.bpt[profile])
            if self.veto_lbda and (eq(vc, self.veto_lbda)
                                   or vc > self.veto_lbda):
                n += 1
            elif self.veto_lbda is None and vc > 0:
                n += 1

        return n

    def get_profile_upper_limit(self, bid):
        index = self.profiles.index(bid)
        if index == (len(self.profiles) - 1):
            return None

        return self.bpt[self.profiles[index + 1]]

    def get_profile_lower_limit(self, bid):
        index = self.profiles.index(bid)
        if self.vpt is None:
            if index == 0:
                return None
            else:
                return self.bpt[self.profiles[index - 1]]

        if index == 0:
            return self.vpt[bid]

        bp = self.bpt[self.profiles[index - 1]]
        vp = self.vpt[self.profiles[index]]

        ap = AlternativePerformances(bid, {})
        for crit in bp.performances.keys():
            direction = self.criteria[crit].direction
            bperf = bp.performances[crit] * direction
            vperf = vp.performances[crit] * direction
            ap.performances[crit] = max(bperf, vperf) * direction

        return ap

    def get_veto_profile_upper_limit(self, bid):
        index = self.profiles.index(bid)
        if index == (len(self.profiles) - 1):
            return self.bpt[self.profiles[index]]

        bp = self.bpt[bid]
        vp = self.vpt[self.profiles[index + 1]]

        ap = AlternativePerformances(bid, {})
        for crit in bp.performances.keys():
            direction = self.criteria[crit].direction
            bperf = bp.performances[crit] * direction
            vperf = vp.performances[crit] * direction
            ap.performances[crit] = min(bperf, vperf) * direction

        return ap

    def get_veto_profile_lower_limit(self, bid):
        index = self.profiles.index(bid)
        if index == 0:
            return None

        return self.vpt[self.profiles[index - 1]]

    def to_xmcda(self):
        root = super(MRSort, self).to_xmcda()

        for obj in ['veto', 'veto_weights']:
            mcda = getattr(self, obj)
            if mcda is None:
                continue

            mcda.id = obj
            xmcda = mcda.to_xmcda()
            root.append(xmcda)

        if self.veto_lbda:
            mparams = ElementTree.SubElement(root, 'methodParameters')
            param = ElementTree.SubElement(mparams, 'parameter')
            value = ElementTree.SubElement(param, 'value')
            value.set('id', 'veto_lbda')
            lbda = marshal(self.veto_lbda)
            value.append(lbda)

        return root

    def from_xmcda(self, xmcda, id = None):
        super(MRSort, self).from_xmcda(xmcda, id)

        xmcda = find_xmcda_tag(xmcda, 'ElectreTri', id)
        value = xmcda.find(".//methodParameters/parameter/value[@id='veto_lbda']")
        if value is not None:
            self.veto_lbda = unmarshal(value.getchildren()[0])

        if xmcda.find(".//criteriaValues[@id='veto_weights']") is not None:
            setattr(self, 'veto_weights',
                    CriteriaValues().from_xmcda(xmcda, 'veto_weights'))
        if xmcda.find(".//performanceTable[@id='veto']") is not None:
            setattr(self, 'veto',
                    PerformanceTable().from_xmcda(xmcda, 'veto'))

        return self
