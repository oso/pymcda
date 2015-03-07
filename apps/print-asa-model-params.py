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

criteria_discarded = {c: 0 for c in criteria_order}

criteria_names = {}
criteria_names['age'] = "Age"
criteria_names['diabetic'] = "Diabetic"
criteria_names['hypertension'] = "Hypertension"
criteria_names['respiratory_failure'] = "Respiratory failure"
criteria_names['heart_failure'] = "Heart rate failure"
criteria_names['hr2'] = "Heart rate"
criteria_names['cardiac_steadiness'] = "Heart rate steadiness"
criteria_names['pacemaker'] = "Pacemaker"
criteria_names['avb'] = "Atrio-ventricular block"
criteria_names['lvh'] = "Left-ventricular hypertrophy"
criteria_names['spo2'] = "Oxygen saturation"
criteria_names['gly'] = "Blood glucose level"
criteria_names['sys'] = "Systole"
criteria_names['dia'] = "Diastole"

criteria_worst = {}
criteria_worst['age'] = 105
criteria_worst['diabetic'] = 1
criteria_worst['hypertension'] = 1
criteria_worst['respiratory_failure'] = 1
criteria_worst['heart_failure'] = 1
criteria_worst['hr2'] = 123
criteria_worst['cardiac_steadiness'] = 0
criteria_worst['pacemaker'] = 1
criteria_worst['avb'] = 1
criteria_worst['lvh'] = 1
criteria_worst['spo2'] = 43
criteria_worst['gly'] = 3.8
criteria_worst['sys'] = 20.5
criteria_worst['dia'] = 13

criteria_best = {}
criteria_best['age'] = 0
criteria_best['diabetic'] = 0
criteria_best['hypertension'] = 0
criteria_best['respiratory_failure'] = 0
criteria_best['heart_failure'] = 0
criteria_best['hr2'] = 55
criteria_best['cardiac_steadiness'] = 1
criteria_best['pacemaker'] = 0
criteria_best['avb'] = 0
criteria_best['lvh'] = 0
criteria_best['spo2'] = 100
criteria_best['gly'] = 0.5
criteria_best['sys'] = 9
criteria_best['dia'] = 5

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

    criteria = m.criteria.keys()
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

    print("{lambda} %.4f" % m.lbda, file = fweights)
    for c in criteria:
        print("{%s} %.4f" % (criteria_names[c], m.cv[c].value), file = fweights)

    fweights.close()
    fprofiles.close()

    fcoalitions = open('%s-wcoalitions.dat' % bname, 'w+')

    winning, loosing = compute_winning_and_loosing_coalitions(m.cv, m.lbda)
    mwinning = compute_minimal_winning_coalitions(winning)
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

    fca = open('%s-ca.dat' % bname, 'w+')
    ca = compute_ca(aa_learning, aa_learned)
    print("%.4f" % ca, end = '', file=fca)
    fca.close()

    fauc = open('%s-auc.dat' % bname, 'w+')
    auc = m.auc(aa_learning, pt_learning)
    print("%.4f" % auc, end = '', file=fauc)
    fauc.close()

for c in criteria_order:
    print("%s: %d" % (c, criteria_discarded[c]))
