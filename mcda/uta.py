from tools.utils import normalize_criteria_weights

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

        return u

    def global_utilities(self, pt):
        au = {}

        for ap in pt:
            u = self.global_utility(ap)
            au[ap.alternative_id] = u

        return au

class utadis(uta):
    pass
