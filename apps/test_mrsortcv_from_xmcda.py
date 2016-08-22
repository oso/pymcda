import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
from xml.etree import ElementTree
import bz2

from pymcda.electre_tri import MRSort
from pymcda.types import PerformanceTable
from pymcda.types import AlternativesAssignments
from pymcda.utils import compute_ca
from pymcda.utils import print_confusion_matrix
from pymcda.utils import discard_undersorted_alternatives
from pymcda.utils import discard_alternatives_in_category
from test_utils import is_bz2_file
from pymcda.learning.meta_mrsortvc3 import MetaMRSortVCPop3
from pymcda.pt_sorted import SortedPerformanceTable
from test_utils import save_to_xmcda

table_ca_learning = []
table_ca_test = []
table_auc_learning = []
table_auc_test = []
cmatrix_learning = {}
cmatrix_test = {}

directory='data/test-veto'

for f in sys.argv[1:]:
    fname = os.path.splitext(os.path.basename(f))[0]

    if is_bz2_file(f) is True:
        f = bz2.BZ2File(f)

    tree = ElementTree.parse(f)
    root = tree.getroot()
    m = MRSort().from_xmcda(root, 'learned')

    pt_learning = PerformanceTable().from_xmcda(root, 'learning_set')
    pt_test = PerformanceTable().from_xmcda(root, 'test_set')

    aa_learning = AlternativesAssignments().from_xmcda(root,
                                                       'learning_set')
    aa_test = AlternativesAssignments().from_xmcda(root,
                                                  'test_set')

    aa_learning_m2 = m.pessimist(pt_learning)
    aa_test_m2 = m.pessimist(pt_test)

#    # Remove alternatives that cannot be corrected with a veto rule
#    aa_learning_m2p = discard_undersorted_alternatives(m.categories,
#                                                      aa_learning,
#                                                      aa_learning_m2)
#    aa_learning_m2p = discard_alternatives_in_category(aa_learning_m2p,
#                                                      m.categories[0])

    # Run the metaheuristic
    meta = MetaMRSortVCPop3(10, m, SortedPerformanceTable(pt_learning),
                            aa_learning)
    nloops = 10
    nmeta = 20
    for i in range(nloops):
        m2, ca = meta.optimize(nmeta)

    m2.id = 'learned'
    aa_learning.id, aa_test.id = 'learning_set', 'test_set'
    pt_learning.id, pt_test.id = 'learning_set', 'test_set'
    save_to_xmcda("%s/%s.bz2" % (directory, fname),
                  m2, aa_learning, aa_test, pt_learning, pt_test)
