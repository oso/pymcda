import bisect

from pymcda.types import AlternativeValue, AlternativesValues
from pymcda.types import AlternativeAssignment
from pymcda.types import AlternativesAssignments

class uta(object):

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

class utadis(uta):

    def __init__(self, criteria = None, cvs = None, cfs = None,
                 cat_values = None):
        super(utadis, self).__init__(criteria, cvs, cfs)
        self.cat_values = cat_values
        upper = cat_values.get_upper_limits()
        self.cat_limits = sorted(upper.iteritems(),
                                 key = lambda (k, v): (v, k))
        self.limits = [ cat_limit[1] for cat_limit in self.cat_limits ]

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
