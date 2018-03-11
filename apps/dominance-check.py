#!/usr/bin/env python

from __future__ import print_function
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")

from collections import OrderedDict
import csv

from test_utils import load_mcda_input_data

def usage(pname):
    print("%s csvfile" % pname)

def dominance_check(csvfile):
    data = load_mcda_input_data(csvfile)
    cats = data.cats.get_ordered_categories()

    nincompatibilities = 0
    for ap in data.pt:
        a = ap.id
        aa = data.aa[a]
        categories = cats[cats.index(aa.category_id)+1:]
        aids = data.aa.get_alternatives_in_categories(categories)

        incompatibility = False
        for a2 in aids:
            ap2 = data.pt[a2]
            if ap.dominates(ap2, data.c):
                print("Alternative %s (cat %s) is as good as %s (cat %s)"
                      % (a, aa.category_id, a2, data.aa[a2].category_id))
#                print("%s" % ap)
#                print("%s" % ap2)
                incompatibility = True

        if incompatibility:
            nincompatibilities += 1

    print("#incompatibilities: %d" % nincompatibilities)

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        usage(argv[0])
        sys.exit(1)

    dominance_check(sys.argv[1])
