from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
import bisect
from mcda.types import alternative_performances

class sorted_performance_table():

    def __init__(self, pt):
        self.pt = pt
        self.__sort()
        self.__build_index()

    def __getitem__(self, id):
        return self.pt[id]

    def __sort(self):
        self.cids = next(self.pt.itervalues()).performances.keys()
        self.n = len(self.pt)
        self.sorted_pt = { cid: list() for cid in self.cids }
        for ap in self.pt:
            p = ap.performances
            aid = ap.id
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

    def get_below(self, cid, val, b=True):
        if b is True:
            i = bisect.bisect(self.sorted_values[cid], val)
        else:
            i = bisect.bisect_left(self.sorted_values[cid], val)
        return self.sorted_altid[cid][:i], self.sorted_values[cid][:i]

    def get_above(self, cid, val, a=True):
        if a is True:
            i = bisect.bisect_left(self.sorted_values[cid], val)
        else:
            i = bisect.bisect(self.sorted_values[cid], val)
        return self.sorted_altid[cid][i:], self.sorted_values[cid][i:]

    def get_middle(self, cid, val_l, val_r, l=True, r=True):
        if val_l > val_r:
            val_l, val_r = val_r, val_l
            l, r = r, l

        if l is True:
            i = bisect.bisect_left(self.sorted_values[cid], val_l)
        else:
            i = bisect.bisect(self.sorted_values[cid], val_l)
        if r is True:
            i2 = bisect.bisect(self.sorted_values[cid], val_r)
        else:
            i2 = bisect.bisect_left(self.sorted_values[cid], val_r)

        return self.sorted_altid[cid][i:i2], self.sorted_values[cid][i:i2]

    def get_below_len(self, cid, val, r=True):
        if r is True:
            return bisect.bisect(self.sorted_values[cid], val)
        else:
            return bisect.bisect_left(self.sorted_values[cid], val)

    def get_above_len(self, cid, val, l=True):
        if l is True:
            return self.n - bisect.bisect_left(self.sorted_values[cid], val)
        else:
            return self.n - bisect.bisect(self.sorted_values[cid], val)

    def get_middle_len(self, cid, val_l, val_r, l=True, r=True):
        if val_l > val_r:
            val_l, val_r = val_r, val_l
            l, r = r, l

        if l is True:
            i = bisect.bisect_left(self.sorted_values[cid], val_l)
        else:
            i = bisect.bisect(self.sorted_values[cid], val_l)
        if r is True:
            i2 = bisect.bisect(self.sorted_values[cid], val_r)
        else:
            i2 = bisect.bisect_left(self.sorted_values[cid], val_r)

        return i2-i

    def get_worst_ap(self):
        a = alternative_performances('worst', {})
        for cid in self.cids:
            a.performances[cid] = self.sorted_values[cid][0]
        return a

    def get_best_ap(self):
        a = alternative_performances('best', {})
        for cid in self.cids:
            a.performances[cid] = self.sorted_values[cid][-1]
        return a

if __name__ == "__main__":
    from tools.generate_random import generate_random_alternatives
    from tools.generate_random import generate_random_criteria
    from tools.generate_random import generate_random_performance_table
    import time

    a = generate_random_alternatives(500)
    c = generate_random_criteria(5)
    pt = generate_random_performance_table(a, c, 1234)

    sorted_pt = sorted_performance_table(pt)

    t1 = time.time()
    print len(sorted_pt.get_below('c1', 0.1)[0])
    print len(sorted_pt.get_above('c1', 0.1)[0])
    print len(sorted_pt.get_middle('c1', 0, 1)[0])
    print sorted_pt.get_below_len('c1', 0.1)
    print sorted_pt.get_above_len('c1', 0.1)
    print sorted_pt.get_middle_len('c1', 0, 1)
    print sorted_pt.get_middle_len('c1', 1, 0)
    print len(sorted_pt.get_all('c1'))
    print sorted_pt.get_worst_ap()
    print sorted_pt.get_best_ap()
    print time.time() - t1
