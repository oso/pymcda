import math
import random
import bisect

class htable:

    def __init__(self, data, size):
        self.data = data
        self.size = size
        self.__doit()

    def __doit(self):
        min_val = min(self.data.values())
        max_val = max(self.data.values())
        self.isize = (max_val-min_val)/self.size

        self.odata = [ list() for i in range(self.size) ]
        for i, d in self.data.items():
            h = self.hash(d)
            self.odata[h].append((i, d))
            self.odata[h].sort(key=lambda r: r[1])

    def hash(self, val):
        h = int(val/self.isize)
        if h >= self.size:
            h = self.size-1
        return h

    def get_left(self, val):
        h = self.hash(val)
        l = self.odata[h]

        k = [r[1] for r in l]
        i = bisect.bisect(k, val)
        out = self.odata[h][:i]

        return sum(self.odata[:h], []) + out

    def get_right(self, val):
        h = self.hash(val)
        l = self.odata[h]

        k = [r[1] for r in l]
        i = bisect.bisect_left(k, val)
        out = self.odata[h][i:]

        return out + sum(self.odata[h+1:], [])

    def get_middle(self, left, right):
        h = self.hash(left)
        l = self.odata[h]
        h2 = self.hash(right)
        l2 = self.odata[h2]

        k = [r[1] for r in l]
        i = bisect.bisect_left(k, left)
        out = self.odata[h][i:]

        k2 = [r[1] for r in l2]
        i2 = bisect.bisect(k, right)
        out2 = self.odata[h2][:i2+1]
        print out2
        print 'h', h, h2
        print 'i', i, i2

        return out + sum(self.odata[h+1:h2], []) + out2

    def get_left_keys(self, val):
        l = self.get_left(val)
        return [r[0] for r in l]

    def get_right_keys(self, val):
        l = self.get_right(val)
        return [r[0] for r in l]

    def get_middle_keys(self, left, right):
        l = self.get_middle(left, right)
        return [r[0] for r in l]

if __name__ == "__main__":
    random.seed(123)

    data = { i: round(random.random(), 4) for i in range(1000) }
    h_table = htable(data, 100000)
    print h_table.get_left(0.4883)
    print h_table.get_left_keys(0.4883)
    print h_table.get_right(0.4881)
    print h_table.get_right_keys(0.4881)
    print h_table.get_middle(0.992, 0.9951)
    print h_table.get_middle_keys(0.992, 0.9951)
    print len(h_table.get_middle_keys(0.0001, 1))

    import time
    t1 = time.time()
    print h_table.get_middle(0.5, 0.6)
    print time.time()-t1

#    data2 = [ (i, round(random.random(), 4)) for i in range(1000) ]
    data2 = [ (k, v) for k, v in data.items() ]
    data2.sort(key=lambda r: r[1])
    k = [r[1] for r in data2]
    t1 = time.time()
    i = bisect.bisect_left(k, 0.5)
    i2 = bisect.bisect_left(k, 0.6)
    print data2[i:i2+1]
    print time.time()-t1
