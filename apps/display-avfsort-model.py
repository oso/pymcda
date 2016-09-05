#!/usr/bin/env python

import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
from xml.etree import ElementTree
import bz2

from PyQt4 import QtCore
from PyQt4 import QtGui
from pymcda.uta import AVFSort
from pymcda.types import AlternativePerformances
from pymcda.ui.graphic import QGraphicsSceneEtri
from pymcda.ui.graphic import _MyGraphicsview
from test_utils import is_bz2_file
from pymcda.ui.graphic_uta import display_utadis_model

xmcda_models = []
for f in sys.argv[1:]:
    if not os.path.isfile(f):
        print("Invalid file %s" % f)
        sys.exit(1)

    print("!!")
    if is_bz2_file(f) is True:
        f = bz2.BZ2File(f)

    tree = ElementTree.parse(f)
    root = tree.getroot()

    xmcda_models += root.findall(".//AVFSort")

models = []
for xmcda_model in xmcda_models:
    m = AVFSort().from_xmcda(xmcda_model)

    string = "Model '%s'" % m.id
    print(string)
    print('=' * len(string))

    models.append(m)


m.cfs.display()
m.cat_values.display()
display_utadis_model(m.cfs)

sys.exit(0)

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
