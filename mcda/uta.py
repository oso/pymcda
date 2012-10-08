import bisect

from tools.utils import normalize_criteria_weights
from tools.utils import get_categories_upper_limits
from mcda.types import alternative_value, alternatives_values
from mcda.types import alternative_affectation
from mcda.types import alternatives_affectations

class uta(object):

    def __init__(self, criteria = None, cvs = None, cfs = None):
        self.criteria = criteria
        self.cvs = cvs
        self.cfs = cfs
        normalize_criteria_weights(cvs)

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

        av = alternative_value(ap.alternative_id, u)

        return av

    def global_utilities(self, pt):
        au = alternatives_values()

        for ap in pt:
            av = self.global_utility(ap)
            au[av.id] = av

        return au

class utadis(uta):

    def __init__(self, criteria = None, cvs = None, cfs = None,
                 cat_values = None):
        super(utadis, self).__init__(criteria, cvs, cfs)
        self.cat_values = cat_values
        upper = get_categories_upper_limits(cat_values)
        self.cat_limits = sorted(upper.iteritems(),
                                 key = lambda (k, v): (v, k))
        self.limits = [ cat_limit[1] for cat_limit in self.cat_limits ]

    def get_assignment(self, ap):
        av = self.global_utility(ap)
        i = bisect.bisect_left(self.limits, av.value)
        cat = self.cat_limits[i][0]
        return alternative_affectation(ap.alternative_id, cat)

    def get_assignments(self, pt):
        assignments = alternatives_affectations([])
        for ap in pt:
            assignments.append(self.get_assignment(ap))
        return assignments
