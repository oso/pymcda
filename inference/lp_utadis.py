from __future__ import division
import sys
sys.path.insert(0, "..")
from tools.generate_random import generate_random_piecewise_linear

class lp_utadis(object):

    def __init__(self, c_segments, gi_worst, gi_best):
        pass

    def solve(self, aa, pt):
        pass

if __name__ == "__main__":
    pl1 = generate_random_piecewise_linear(0, 5, 2)
    pl2 = generate_random_piecewise_linear(0, 10, 4)
    pl3 = generate_random_piecewise_linear(0, 15, 3)
    print(pl1, pl2, pl3)
