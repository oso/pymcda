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
#from pymcda.ui.graphic import QGraphicsSceneEtri
#from pymcda.ui.graphic import _MyGraphicsview
from pymcda.utils import compute_winning_and_loosing_coalitions
from pymcda.utils import compute_minimal_winning_coalitions
from pymcda.utils import compute_maximal_loosing_coalitions
from pymcda.utils import compute_ca
from pymcda.learning.lp_mrsort_post_weights import LpMRSortPostWeights
from test_utils import is_bz2_file

criteria_order = ['age', 'diabetic', 'hypertension', 'respiratory_failure',
                  'heart_failure', 'bradycardia', 'tachycardia',
                  'cardiac_steadiness', 'pacemaker', 'avb', 'lvh', 'spo2',
                  'hypoglycemia', 'hyperglycemia', 'sys', 'dia']

criteria_discarded = {c: 0 for c in criteria_order}

criteria_names = {}
criteria_names['age'] = "Age"
criteria_names['diabetic'] = "Diabetic"
criteria_names['hypertension'] = "Hypertension"
criteria_names['respiratory_failure'] = "Respiratory failure"
criteria_names['heart_failure'] = "Heart rate failure"
criteria_names['bradycardia'] = "Bradycardia"
criteria_names['tachycardia'] = "Tachycardia"
criteria_names['cardiac_steadiness'] = "Heart rate steadiness"
criteria_names['pacemaker'] = "Pacemaker"
criteria_names['avb'] = "Atrio-ventricular block"
criteria_names['lvh'] = "Left-ventricular hypertrophy"
criteria_names['spo2'] = "Oxygen saturation"
criteria_names['hypoglycemia'] = "Hypoglycemia"
criteria_names['hyperglycemia'] = "Hyperglycemia"
criteria_names['sys'] = "Systole"
criteria_names['dia'] = "Diastole"

criteria_worst = {}
criteria_worst['age'] = 105
criteria_worst['diabetic'] = 1
criteria_worst['hypertension'] = 1
criteria_worst['respiratory_failure'] = 1
criteria_worst['heart_failure'] = 1
criteria_worst['tachycardia'] = 123
criteria_worst['bradycardia'] = 55
criteria_worst['cardiac_steadiness'] = 0
criteria_worst['pacemaker'] = 1
criteria_worst['avb'] = 1
criteria_worst['lvh'] = 1
criteria_worst['spo2'] = 43
criteria_worst['hypoglycemia'] = 0.5
criteria_worst['hyperglycemia'] = 3.8
criteria_worst['sys'] = 20.5
criteria_worst['dia'] = 13

criteria_best = {}
criteria_best['age'] = 0
criteria_best['diabetic'] = 0
criteria_best['hypertension'] = 0
criteria_best['respiratory_failure'] = 0
criteria_best['heart_failure'] = 0
criteria_best['bradycardia'] = 70
criteria_best['tachycardia'] = 70
criteria_best['cardiac_steadiness'] = 1
criteria_best['pacemaker'] = 0
criteria_best['avb'] = 0
criteria_best['lvh'] = 0
criteria_best['spo2'] = 100
criteria_best['hypoglycemia'] = 0.92
criteria_best['hyperglycemia'] = 0.92
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

    pt_learning = PerformanceTable().from_xmcda(root, 'learning_set')
    aa_learning = AlternativesAssignments().from_xmcda(root,
                                                       'learning_set')

    uniquevalues = pt_learning.get_unique_values()

    bname = os.path.basename(os.path.splitext(f.name)[0])
    fweights = open('%s-w.dat' % bname, 'w+')
    fprofiles = open('%s-p.dat' % bname, 'w+')

    print("Processing %s..." % bname)

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
                if m.criteria[c].direction == -1:
                    for val in reversed(uniquevalues[c]):
                        if val == m.bpt[p].performances[c]:
                            break

                        if val < m.bpt[p].performances[c]:
                            break

                    if val < m.bpt[p].performances[c]:
                        m.bpt[p].performances[c] = val
                else:
                    for val in uniquevalues[c]:
                        if val == m.bpt[p].performances[c]:
                            break

                        if val > m.bpt[p].performances[c]:
                            break

                    if val > m.bpt[p].performances[c]:
                        m.bpt[p].performances[c] = val

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
        try:
            lp = LpMRSortPostWeights(m.cv, m.lbda, 1000)
            obj, m.cv, m.lbda = lp.solve()
        except:
            lp = LpMRSortPostWeights(m.cv, m.lbda, 10000)
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

    aa_learned = m.pessimist(pt_learning)

    fca = open('%s-ca.dat' % bname, 'w+')
    ca = compute_ca(aa_learning, aa_learned)
    print("%.4f" % ca, end = '', file=fca)
    fca.close()

    fauc = open('%s-auc.dat' % bname, 'w+')
    auc = m.auc(aa_learning, pt_learning)
    print("%.4f" % auc, end = '', file=fauc)
    fauc.close()

    fmisclassified = open('%s-misclassified.dat' % bname, 'w+')
    print("{Alternative} ", file = fmisclassified, end = '')
    print("{Original assignment} ", file = fmisclassified, end = '')
    print("{Model assignment}", file = fmisclassified, end = '')
    for c in criteria:
        print(" {%s}" % criteria_names[c], file = fmisclassified, end = '')
    print("\n", file = fmisclassified, end = '')

    misclassified_aids = []
    for aid in aa_learning.keys():
        aa1 = aa_learning[aid].category_id
        aa2 = aa_learned[aid].category_id
        if aa1 == aa2:
            continue

        misclassified_aids.append(aid)

    misclassified_aids.sort(key = lambda item: (len(item), item))

    for aid in misclassified_aids:
        ap = pt_learning[aid]
        aa1 = aa_learning[aid].category_id
        aa2 = aa_learned[aid].category_id
        print("%s " % aid, file = fmisclassified, end = '')
        print("%s %s" % (aa1, aa2), file = fmisclassified, end = '')
        for c in criteria:
            print(" %s" % ap.performances[c], file = fmisclassified, end = '')
        print("\n", file = fmisclassified, end = '')

    fmisclassified.close()

for c in criteria:
    print("%s: %d" % (c, criteria_discarded[c]))
