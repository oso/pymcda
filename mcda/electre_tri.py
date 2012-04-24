from __future__ import division
import math
from mcda.types import alternative_affectation, alternatives_affectations
from copy import deepcopy

def eq(a, b, eps=10e-10):
    return abs(a-b) <= eps

class electre_tri:

    def __init__(self, criteria=None, cv=None, profiles=None, lbda=None,
                 cats=None):
        self.criteria = criteria
        self.cv = cv
        self.profiles = profiles
        self.lbda = lbda
        self.categories = cats

    def copy(self):
        return deepcopy(self)

    def __check_input_params(self):
        if self.criteria is None:
            raise KeyError('No criteria specified')
        if self.cv is None:
            raise KeyError('No criteria values specified')
        if self.profiles is None:
            raise KeyError('No profiles specified')
        if self.lbda is None:
            raise KeyError('No cut threshold specified')
        if self.categories is None:
            raise KeyError('No cut threshold specified')

    def __get_threshold_by_profile(self, c, threshold_id, profile_rank):
        if c.thresholds is None:
            return None

        threshid = "%s%s" % (threshold_id, profile_rank)
        if c.thresholds.has_threshold(threshid):
            return c.thresholds(threshid).values.value
        elif c.thresholds.has_threshold(threshold_id):
            return c.thresholds(threshold_id).values.value
        else:
            return None

    def __partial_concordance(self, x, y, c, profile_rank):
        # compute g_j(b) - g_j(a)
        diff = (y.performances[c.id]-x.performances[c.id])*c.direction

        # compute c_j(a, b)
        p = self.__get_threshold_by_profile(c, 'p', profile_rank)
        q = self.__get_threshold_by_profile(c, 'q', profile_rank)
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

    def __concordance(self, x, y, clist, cv, profile_rank):
        wsum = 0
        pjcj = 0
        for c in clist:
            if c.disabled == 1:
                continue

            cj = self.__partial_concordance(x, y, c, profile_rank)

            cval = cv(c.id)
            weight = cval.value
            wcj = float(weight)*cj

            pjcj += wcj
            wsum += weight

        return pjcj/wsum

    def __partial_discordance(self, x, y, c, profile_rank):
        # compute g_j(b) - g_j(a)
        diff = (y.performances[c.id]-x.performances[c.id])*c.direction

        # compute d_j(a,b)
        p = self.__get_threshold_by_profile(c, 'p', profile_rank)
        v = self.__get_threshold_by_profile(c, 'v', profile_rank)
        if v is None:
            return 0
        elif diff > v:
            return 1
        elif p is None or diff <= p:
            return 0
        else:
            num = float(v-diff)
            den = float(v-p)
            return num/den

    def credibility(self, x, y, clist, cv, profile_rank):
        self.__check_input_params()
        concordance = self.__concordance(x, y, clist, cv, profile_rank)

        sigma = concordance
        for c in clist:
            if c.disabled == 1:
                continue

            dj = self.__partial_discordance(x, y, c, profile_rank)
            if dj > concordance:
                num = float(1-dj)
                den = float(1-concordance)
                sigma = sigma*num/den

        return sigma

    def __outrank(self, action_perfs, criteria, cv, profile, profile_rank, lbda):
        s_ab = self.credibility(action_perfs, profile, criteria, cv, profile_rank)
        s_ba = self.credibility(profile, action_perfs, criteria, cv, profile_rank)

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
        affectations = alternatives_affectations([])
        for action_perfs in pt:
            cat_rank = len(profiles)
            for i, profile in enumerate(profiles):
                outr = self.__outrank(action_perfs, self.criteria, self.cv,
                                      profile, i+1, self.lbda)
                if outr != "S" and outr != "I":
                    cat_rank -= 1

            cat_id = self.categories[cat_rank].id
            alternative_id = action_perfs.alternative_id
            alt_affect = alternative_affectation(alternative_id, cat_id)
            affectations.append(alt_affect)

        return affectations

    def optimist(self, pt):
        self.__check_input_params()
        profiles = self.profiles
        affectations = alternatives_affectations([])
        for action_perfs in pt:
            cat_rank = 0
            for i, profile in enumerate(profiles):
                outr = self.__outrank(action_perfs, self.criteria, self.cv,
                                      profile, i+1, self.lbda)
                if outr != "-":
                    cat_rank += 1

            cat_id = self.categories[cat_rank].id
            alternative_id = action_perfs.alternative_id
            alt_affect = alternative_affectation(alternative_id, cat_id)
            affectations.append(alt_affect)

        return affectations
