#!/usr/bin/env python2

import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
from xml.etree import ElementTree
import bz2

from PyQt4 import QtCore
from PyQt4 import QtGui
from pymcda.electre_tri import MRSort
from pymcda.types import AlternativePerformances
from pymcda.ui.graphic import QGraphicsSceneEtri
from pymcda.ui.graphic import _MyGraphicsview
from pymcda.utils import compute_winning_and_loosing_coalitions
from pymcda.utils import compute_minimal_winning_coalitions
from pymcda.utils import compute_maximal_loosing_coalitions
from pymcda.learning.lp_mrsort_post_weights import LpMRSortPostWeights
from test_utils import is_bz2_file

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

    xmcda_models += root.findall(".//ElectreTri")

models = []
for xmcda_model in xmcda_models:
    m = MRSort().from_xmcda(xmcda_model)

    if len(xmcda_models_toshow) > 0 and m.id not in xmcda_models_toshow:
        continue

    string = "Model '%s'" % m.id
    print(string)
    print('=' * len(string))

    print(m.bpt)
    print(m.cv)
    print("lambda: %s\n" % m.lbda)

    if m.veto is not None:
        print(m.veto)
    else:
        print("No veto profiles")

    if m.veto_weights is not None:
        print(m.veto_weights)
        print("veto_lambda: %s\n" % m.veto_lbda)
    else:
        print("No veto weights\n")

    print("Adjusted weights and lambda")
    lp = LpMRSortPostWeights(m.cv, m.lbda)
    obj, m.cv, m.lbda = lp.solve()
    print(m.cv)
    print("lambda: %s\n" % m.lbda)

    if m.veto is not None:
        print("Adjusted veto weights and lambda")
        lp = LpMRSortPostWeights(m.veto_weights, m.veto_lbda)
        obj, m.veto_weights, m.veto_lbda = lp.solve()
        print(m.veto_weights)
        print("lambda: %s\n" % m.veto_lbda)

    if len(m.criteria) < 15:
        winning, loosing = compute_winning_and_loosing_coalitions(m.cv, m.lbda)
        nwinning = len(winning)
        print("Number of winning concordance relations: %d (/%d)"
              % (nwinning, 2**len(m.criteria)))

        mwinning = compute_minimal_winning_coalitions(winning)
        mloosing = compute_maximal_loosing_coalitions(loosing)
        print("Minimal winning coalitions:")
        for win in mwinning:
            print(win)
        print("Maximal loosing coalitions:")
        for loose in mloosing:
            print(loose)

    print("\n\n")

    models.append(m)


app = QtGui.QApplication(sys.argv)

sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                               QtGui.QSizePolicy.Expanding)
sizePolicy.setHorizontalStretch(1)
sizePolicy.setVerticalStretch(0)
sizePolicy.setHeightForWidth(sizePolicy.hasHeightForWidth())

layout = QtGui.QGridLayout()

for m in models:
    worst = m.bpt.get_worst(m.criteria)
    best = m.bpt.get_best(m.criteria)

    for c in m.criteria:
        if worst.performances[c.id] >= 0 and worst.performances[c.id] <= 1:
            if c.direction == 1:
                worst.performances[c.id] = 0
                best.performances[c.id] = 1
            else:
                worst.performances[c.id] = 1
                best.performances[c.id] = 0
        else:
            diff = best.performances[c.id] - worst.performances[c.id]
            worst.performances[c.id] -= diff
            best.performances[c.id] += diff

            if diff == 0:
                if c.direction == 1:
                    best.performances[c.id] += 1
                    worst.performances[c.id] -= 1
                else:
                    best.performances[c.id] -= 1
                    worst.performances[c.id] += 1

    view = _MyGraphicsview()
    graph = QGraphicsSceneEtri(m, worst, best, view.size(), parent = view)
    if m.veto is not None:
        for veto in m.veto:
            graph.plot_alternative_performances(m.vpt[veto.id], False, QtGui.QColor("blue"), True)

    view.setRenderHint(QtGui.QPainter.Antialiasing)
    view.setSizePolicy(sizePolicy)
    view.setScene(graph)
    layout.addWidget(view)

dialog = QtGui.QDialog()
dialog.setLayout(layout)
dialog.resize(1024, 768)
dialog.show()

app.exec_()
