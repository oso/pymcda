import bisect

from tools.utils import normalize_criteria_weights
from tools.utils import get_categories_upper_limits
from mcda.types import alternative_value, alternative_values

class uta():

    def __init__(self, criteria = None, cvs = None, cfs = None):
        self.criteria = criteria
        self.cvs = cvs
        self.cfs = cfs
        normalize_criteria_weights(cvs)

    def marginal_utility(self, cid, aps):
        gi = aps(cid)
        cf = self.cfs(cid)
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
        au = alternative_values()

        for ap in pt:
            av = self.global_utility(ap)
            au[av.id] = av

        return au

class utadis(uta):

    def __init__(self, criteria = None, cvs = None, cfs = None,
                 cat_values = None):
        super(utadis, self).__init__(criteria, cvs, cfs)
        self.cat_values = cat_values
        self.limits = get_categories_upper_limits(cat_values)

    def get_assignment(self, ap):
        av = self.global_utility(ap)
        a = self.limits.keys()
        a.sort()
        i = bisect.bisect_left(a, av.value)
        cat = self.cat_values[i]
        return alternative_affectation(ap.alternative_id, cat)
