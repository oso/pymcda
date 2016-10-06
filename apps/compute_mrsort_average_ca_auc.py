import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
from xml.etree import ElementTree
import bz2
import numpy as np

from pymcda.electre_tri import MRSort
from pymcda.types import PerformanceTable
from pymcda.types import AlternativesAssignments
from pymcda.utils import compute_ca
from pymcda.utils import print_confusion_matrix
from test_utils import is_bz2_file

def compute_aa(m, pt_learning, pt_test):
    aa

table_ca_learning = []
table_ca_test = []
table_auc_learning = []
table_auc_test = []
cmatrix_learning = {}
cmatrix_test = {}

nveto = 0
for f in sys.argv[1:]:
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

    # Compute classification accuracy
    ca_learning = compute_ca(aa_learning, aa_learning_m2)
    ca_test = compute_ca(aa_test, aa_test_m2)

    table_ca_learning.append(ca_learning)
    table_ca_test.append(ca_test)

    # Compute area under the curve
    auc_learning = m.auc(aa_learning, pt_learning)
    auc_test = m.auc(aa_test, pt_test)

    table_auc_learning.append(auc_learning)
    table_auc_test.append(auc_test)

    if m.veto_lbda is not None:
        nveto += 1

    # Compute confusion matrices
    for a in aa_learning.keys():
        key = (aa_learning[a].category_id, aa_learning_m2[a].category_id)
        if key in cmatrix_learning:
            cmatrix_learning[key] += 1
        else:
            cmatrix_learning[key] = 1

    for a in aa_test.keys():
        key = (aa_test[a].category_id, aa_test_m2[a].category_id)
        if key in cmatrix_test:
            cmatrix_test[key] += 1
        else:
            cmatrix_test[key] = 1

print("nveto: %d" % nveto)
avg_ca_learning = sum(table_ca_learning) / float(len(table_ca_learning))
avg_ca_test = sum(table_ca_test) / float(len(table_ca_test))
avg_auc_learning = sum(table_auc_learning) / float(len(table_auc_learning))
avg_auc_test = sum(table_auc_test) / float(len(table_auc_test))

stdev_ca_learning = np.std(np.array(table_ca_learning), axis=0)
stdev_ca_test = np.std(np.array(table_ca_test), axis=0)
stdev_auc_learning = np.std(np.array(table_auc_learning), axis=0)
stdev_auc_test = np.std(np.array(table_auc_test), axis=0)

nfiles = len(sys.argv) - 1
cmatrix_learning.update((x, round(y / float(nfiles), 2))
                        for x, y in cmatrix_learning.items())
cmatrix_test.update((x, round(y / float(nfiles), 2))
                    for x, y in cmatrix_test.items())

print("CA learning avg: %g +- %g" % (avg_ca_learning, stdev_ca_learning))
print("CA test avg: %g +- %g" % (avg_ca_test, stdev_ca_test))
print("AUC learning avg: %g +- %g" % (avg_auc_learning, stdev_auc_learning))
print("AUC test avg: %g +- %g" % (avg_auc_test, stdev_auc_test))

print("Confusion matrix learning set")
print_confusion_matrix(cmatrix_learning, m.categories)
print("Confusion matrix test set")
print_confusion_matrix(cmatrix_test, m.categories)

cmatrix_learning_total = sum(cmatrix_learning.values())
cmatrix_test_total = sum(cmatrix_test.values())
cmatrix_learning.update((x, round(100 * y / float(cmatrix_learning_total), 2))
                        for x, y in cmatrix_learning.items())
cmatrix_test.update((x, round(100 * y / float(cmatrix_test_total), 2))
                    for x, y in cmatrix_test.items())

print("Confusion matrix learning set")
print_confusion_matrix(cmatrix_learning, m.categories)
print("Confusion matrix test set")
print_confusion_matrix(cmatrix_test, m.categories)
