#!/usr/bin/env python

import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
from xml.etree import ElementTree

from pymcda.electre_tri import MRSort
from pymcda.types import PerformanceTable
from pymcda.utils import compute_ca
from pymcda.utils import compute_confusion_matrix
from pymcda.utils import print_confusion_matrix

f = sys.argv[1]
if not os.path.isfile(f):
    printf("Invalid file %s" % f)
    sys.exit(1)

tree = ElementTree.parse(f)
root = tree.getroot()

m1 = MRSort().from_xmcda(root, 'initial')
m2 = MRSort().from_xmcda(root, 'learned')

pt_learning = PerformanceTable().from_xmcda(root, 'learning_set')
pt_test = PerformanceTable().from_xmcda(root, 'test_set')

aa_learning_m1 = m1.pessimist(pt_learning)
aa_learning_m2 = m2.pessimist(pt_learning)
aa_test_m1 = m1.pessimist(pt_test)
aa_test_m2 = m2.pessimist(pt_test)

ca_learning = compute_ca(aa_learning_m1, aa_learning_m2)
ca_test = compute_ca(aa_test_m1, aa_test_m2)

print("Learning set")
print("============")
print("CA: %g\n" % ca_learning)
matrix = compute_confusion_matrix(aa_learning_m1, aa_learning_m2,
                                  m1.categories)
print_confusion_matrix(matrix)

print("\n\nTest set")
print("========")
print("CA: %g\n" % ca_test)
matrix = compute_confusion_matrix(aa_test_m1, aa_test_m2, m1.categories)
print_confusion_matrix(matrix)
