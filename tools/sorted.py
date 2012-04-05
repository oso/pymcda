from __future__ import division
import sys
sys.path.insert(0, "..")
import bisect

class sorted_performance_table():

    def __init__(self, pt):
        self.pt = pt
        self.__sort()
        self.__build_index()

    def __sort(self):
        self.cids = self.pt[0].performances.keys()
        self.n = len(self.pt)
        self.sorted_pt = { cid: list() for cid in self.cids }
        for ap in self.pt:
            p = ap.performances
            aid = ap.alternative_id
            for cid in self.cids:
                bisect.insort(self.sorted_pt[cid], (p[cid], aid))

    def __build_index(self):
        self.sorted_values = { cid: list() for cid in self.cids }
        self.sorted_altid = { cid: list() for cid in self.cids }
        for cid in self.cids:
            self.sorted_values[cid] = [ r[0] for r in self.sorted_pt[cid] ]
            self.sorted_altid[cid] = [ r[1] for r in self.sorted_pt[cid] ]

    def get_all(self, cid):
        return self.sorted_altid[cid]

    def get_below(self, cid, val):
        i = bisect.bisect(self.sorted_values[cid], val)
        return self.sorted_altid[cid][:i]

    def get_above(self, cid, val):
        i = bisect.bisect_left(self.sorted_values[cid], val)
        return self.sorted_altid[cid][i:]

    def get_middle(self, cid, val_l, val_r):
        i = bisect.bisect_left(self.sorted_values[cid], val_l)
        i2 = bisect.bisect(self.sorted_values[cid], val_r)
        return self.sorted_altid[cid][i:i2]

    def get_below_len(self, cid, val):
        return bisect.bisect(self.sorted_values[cid], val)

    def get_above_len(self, cid, val):
        return self.n - bisect.bisect_left(self.sorted_values[cid], val)

    def get_middle_len(self, cid, val_l, val_r):
        i = bisect.bisect_left(self.sorted_values[cid], val_l)
        i2 = bisect.bisect(self.sorted_values[cid], val_r)
        return i2-i

if __name__ == "__main__":
    from tools.generate_random import generate_random_alternatives
    from tools.generate_random import generate_random_criteria
    from tools.generate_random import generate_random_performance_table

    a = generate_random_alternatives(500)
    c = generate_random_criteria(5)
    pt = generate_random_performance_table(a, c, 1234)

    sorted_pt = sorted_performance_table(pt)

    print len(sorted_pt.get_below('c1', 0.1))
    print len(sorted_pt.get_above('c1', 0.1))
    print len(sorted_pt.get_middle('c1', 0, 1))
    print sorted_pt.get_below_len('c1', 0.1)
    print sorted_pt.get_above_len('c1', 0.1)
    print sorted_pt.get_middle_len('c1', 0, 1)
    print len(sorted_pt.get_all('c1'))
