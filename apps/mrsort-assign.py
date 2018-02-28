#!/usr/bin/env python

from __future__ import print_function
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")

from collections import OrderedDict
from xml.etree import ElementTree
from itertools import product
import bz2
import csv

from pymcda.electre_tri import MRSort
from pymcda.types import AlternativePerformances, PerformanceTable
from pymcda.learning.lp_mrsort_post_weights import LpMRSortPostWeights
from test_utils import is_bz2_file

def mrsort_assign(xmcdafile, csvfile):
    if is_bz2_file(xmcdafile) is True:
        xmcdafile = bz2.BZ2File(xmcdafile)

    tree = ElementTree.parse(xmcdafile)
    root = tree.getroot()

    xmcda_models =  root.findall(".//ElectreTri")
    m = MRSort().from_xmcda(xmcda_models[0])

    csvfile = open(csvfile, 'rb')
    csvreader = csv.reader(csvfile, delimiter = ",")
    csvfile.seek(0)
    pt = PerformanceTable(OrderedDict({})).from_csv(csvreader, "pt", [c.id for c in m.criteria])
    aa = m.pessimist(pt)
    print(aa)

def usage(pname):
    print("usage: %s xmcdamodel csvpt" % pname)

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        usage(argv[0])
        sys.exit(1)

    mrsort_assign(sys.argv[1], sys.argv[2])
