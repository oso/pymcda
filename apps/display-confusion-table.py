#!/usr/bin/env python

import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
import bz2
from xml.etree import ElementTree

from pymcda.electre_tri import MRSort
from pymcda.uta import AVFSort
from pymcda.types import PerformanceTable
from pymcda.types import AlternativesAssignments
from pymcda.utils import compute_ca
from pymcda.utils import compute_confusion_matrix
from pymcda.utils import print_confusion_matrix
from test_utils import is_bz2_file

f = sys.argv[1]
if not os.path.isfile(f):
    print("Invalid file %s" % f)
    sys.exit(1)

if is_bz2_file(f) is True:
    f = bz2.BZ2File(f)

tree = ElementTree.parse(f)
root = tree.getroot()

try:
    pt_learning = PerformanceTable().from_xmcda(root, 'learning_set')
except:
    pt_learning = None

try:
    pt_test = PerformanceTable().from_xmcda(root, 'test_set')
except:
    pt_test = None

aa_learning_m1, aa_learning_m2 = None, None
aa_test_m1, aa_test_m2 = None, None

if root.find("ElectreTri[@id='initial']") is not None:
    m1 = MRSort().from_xmcda(root, 'initial')
    if pt_learning is not None:
        aa_learning_m1 = m1.pessimist(pt_learning)
    if pt_test is not None:
        aa_test_m1 = m1.pessimist(pt_test)
elif root.find("AVFSort[@id='initial']") is not None:
    m1 = AVFSort().from_xmcda(root, 'initial')
    if pt_learning is not None:
        aa_learning_m1 = m1.get_assignments(pt_learning)
    if pt_test is not None:
        aa_test_m1 = m1.get_assignments(pt_test)
else:
    if root.find("alternativesAffectations[@id='learning_set']") is not None:
        aa_learning_m1 = AlternativesAssignments().from_xmcda(root,
                                                              'learning_set')

    if root.find("alternativesAffectations[@id='test_set']") is not None:
        aa_test_m1 = AlternativesAssignments().from_xmcda(root, 'test_set')

if root.find("ElectreTri[@id='learned']") is not None:
    m2 = MRSort().from_xmcda(root, 'learned')
    if pt_learning is not None:
        aa_learning_m2 = m2.pessimist(pt_learning)
    if pt_test is not None:
        aa_test_m2 = m2.pessimist(pt_test)
elif root.find("AVFSort[@id='learned']") is not None:
    m2 = AVFSort().from_xmcda(root, 'learned')
    if pt_learning is not None:
        aa_learning_m2 = m2.get_assignments(pt_learning)
    if pt_test is not None:
        aa_test_m2 = m2.get_assignments(pt_test)

if aa_learning_m1 is not None:
    ca_learning = compute_ca(aa_learning_m1, aa_learning_m2)

    print("Learning set")
    print("============")
    print("CA: %g\n" % ca_learning)
    matrix = compute_confusion_matrix(aa_learning_m1, aa_learning_m2,
                                      m2.categories)
    print_confusion_matrix(matrix)

if aa_test_m1 is not None:
    ca_test = compute_ca(aa_test_m1, aa_test_m2)

    print("\n\nTest set")
    print("========")
    print("CA: %g\n" % ca_test)
    matrix = compute_confusion_matrix(aa_test_m1, aa_test_m2, m2.categories)
    print_confusion_matrix(matrix)
