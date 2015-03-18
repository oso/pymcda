#!/usr/bin/env python2

from __future__ import print_function
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
from xml.etree import ElementTree
from itertools import product
import bz2

from pymcda.electre_tri import MRSort
from pymcda.types import AlternativePerformances, PerformanceTable
from pymcda.types import AlternativesAssignments
from pymcda.ui.graphic import QGraphicsSceneEtri
from pymcda.ui.graphic import _MyGraphicsview
from pymcda.utils import compute_winning_and_loosing_coalitions
from pymcda.utils import compute_minimal_winning_coalitions
from pymcda.utils import compute_maximal_loosing_coalitions
from pymcda.utils import compute_ca
from pymcda.learning.lp_mrsort_post_weights import LpMRSortPostWeights
from test_utils import is_bz2_file

criteria_order = ['age', 'diabetic', 'hypertension', 'respiratory_failure',
                  'heart_failure', 'hr2', 'cardiac_steadiness', 'pacemaker',
                  'avb', 'lvh', 'spo2', 'gly', 'sys', 'dia']


criteria_names = {}
criteria_worst = {}
criteria_best = {}

ca_learning = []
auc_learning = []
ca_test = []
auc_test = []
xmcda_models_toshow = []
xmcda_models = []
for f in sys.argv[1:]:
    if not os.path.isfile(f):
        xmcda_models_toshow.append(f)
        continue

    if is_bz2_file(f) is True:
        f = bz2.BZ2File(f)

    tree = ElementTree.parse(f)
    root = tree.getroot()

    xmcda_models = root.findall(".//ElectreTri")

    m = MRSort().from_xmcda(xmcda_models[0])

    bname = os.path.basename(os.path.splitext(f.name)[0])
    fweights = open('%s-w.dat' % bname, 'w+')
    fprofiles = open('%s-p.dat' % bname, 'w+')

    print("Processing %s..." % bname)

    ncriteria = len(m.criteria)
    for c in m.criteria.keys():
        criteria_names[c] = c
        criteria_worst[c] = 0
        criteria_best[c] = 1

    criteria_order = sorted(m.criteria.keys())
    criteria_discarded = {c: 0 for c in criteria_order}

    criteria = criteria_order
    for c in criteria:
        print("{%s} " % criteria_names[c], end = '', file = fprofiles)
    print('', file = fprofiles)

    profiles = reversed(m.categories_profiles.get_ordered_profiles())
    for c in criteria:
        print("%s " % criteria_best[c], end = '', file = fprofiles)
        if m.cv[c].value == 0:
            criteria_discarded[c] += 1
    print('', file = fprofiles)

    for p in profiles:
        for c in criteria:
            if m.cv[c].value == 0:
                print("%s " % criteria_worst[c], end = '', file = fprofiles)
            else:
                print("%s " % m.bpt[p].performances[c], end = '',
                      file = fprofiles)
        print('', file = fprofiles)

    for c in criteria:
        print("%s " % criteria_worst[c], end = '', file = fprofiles)
    print('', file = fprofiles)

    try:
        lp = LpMRSortPostWeights(m.cv, m.lbda, 100)
        obj, m.cv, m.lbda = lp.solve()
    except:
        lp = LpMRSortPostWeights(m.cv, m.lbda, 1000)
        obj, m.cv, m.lbda = lp.solve()

    print("{lambda} %d" % m.lbda, file = fweights)
    for c in criteria:
        print("{%s} %d" % (criteria_names[c], m.cv[c].value), file = fweights)

    fweights.close()
    fprofiles.close()

    fcoalitions = open('%s-wcoalitions.dat' % bname, 'w+')

    mwinning = compute_minimal_winning_coalitions(lp.fmins)
    for win in mwinning:
        win = list(win)
        win.sort(key=criteria_order.index)
        buf = ""
        for c in win:
            buf += "%s, " % criteria_names[c]
        print('[%s]' % buf[:-2], file=fcoalitions)

    fcoalitions.close()

    pt_learning = PerformanceTable().from_xmcda(root, 'learning_set')
    aa_learning = AlternativesAssignments().from_xmcda(root,
                                                       'learning_set')
    aa_learned = m.pessimist(pt_learning)

    fca = open('%s-ca_learning.dat' % bname, 'w+')
    ca = compute_ca(aa_learning, aa_learned)
    print("%.4f" % ca, end = '', file=fca)
    fca.close()

    fauc = open('%s-auc_learning.dat' % bname, 'w+')
    auc = m.auc(aa_learning, pt_learning)
    print("%.4f" % auc, end = '', file=fauc)
    fauc.close()

    ca_learning.append(ca)
    auc_learning.append(auc)

    pt_test = PerformanceTable().from_xmcda(root, 'test_set')
    aa_test = AlternativesAssignments().from_xmcda(root, 'test_set')

    aa_test2 = m.pessimist(pt_test)

    fca = open('%s-ca_test.dat' % bname, 'w+')
    ca = compute_ca(aa_test, aa_test2)
    print("%.4f" % ca, end = '', file=fca)
    fca.close()

    fauc = open('%s-auc_test.dat' % bname, 'w+')
    auc = m.auc(aa_test, pt_test)
    print("%.4f" % auc, end = '', file=fauc)
    fauc.close()

    ca_test.append(ca)
    auc_test.append(auc)

print("CA learning: %.4f" % (sum(ca_learning) / float(len(ca_learning))))
print("AUC learning: %.4f" % (sum(auc_learning) / float(len(auc_learning))))
print("CA test: %.4f" % (sum(ca_test) / float(len(ca_test))))
print("AUC test: %.4f" % (sum(auc_test) / float(len(auc_test))))

for c in criteria_order:
    print("%s: %d" % (c, criteria_discarded[c]))
