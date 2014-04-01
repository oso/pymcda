#!/usr/bin/env python

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
from test_utils import is_bz2_file

xmcda_models = []
for f in sys.argv[1:]:
    if not os.path.isfile(f):
        printf("Invalid file %s" % f)
        sys.exit(1)

    if is_bz2_file(f) is True:
        f = bz2.BZ2File(f)

    tree = ElementTree.parse(f)
    root = tree.getroot()

    xmcda_models += root.findall(".//ElectreTri")

models = []
for xmcda_model in xmcda_models:
    m = MRSort().from_xmcda(xmcda_model)

    print("\n\n")
    string = "Model %s" % m.id
    print(string)
    print('=' * len(string))

    m.bpt.display()
    m.cv.display()
    print("lambda: %s\n" % m.lbda)

    if m.veto is not None:
        m.veto.display()
    else:
        print("No veto profiles")

    if m.veto_weights is not None:
        m.veto_weights.display()
        print("veto_lambda: %s" % m.veto_lbda)
    else:
        print("No veto weights")

    models.append(m)


app = QtGui.QApplication(sys.argv)

sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                               QtGui.QSizePolicy.Expanding)
sizePolicy.setHorizontalStretch(1)
sizePolicy.setVerticalStretch(0)
sizePolicy.setHeightForWidth(sizePolicy.hasHeightForWidth())

layout = QtGui.QGridLayout()

for m in models:
    worst = AlternativePerformances("worst", {crit.id: 0
                                              for crit in m.criteria})
    best = AlternativePerformances("best", {crit.id: 1
                                            for crit in m.criteria})

    view = _MyGraphicsview()
    graph = QGraphicsSceneEtri(m, worst, best, view.size())
    if m.veto is not None:
        for veto in m.veto:
            vb = m.bpt[veto.id] - veto
            graph.plot_alternative_performances(vb)

    view.setRenderHint(QtGui.QPainter.Antialiasing)
    view.setSizePolicy(sizePolicy)
    view.setScene(graph)
    layout.addWidget(view)

dialog = QtGui.QDialog()
dialog.setLayout(layout)
dialog.resize(1024, 768)
dialog.show()

app.exec_()
