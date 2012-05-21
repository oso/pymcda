#!/usr/bin/python
import sys
sys.path.append("..")
from mcda.electre_tri import electre_tri
from ui.graphic import graph_etri
from PyQt4 import QtCore
from PyQt4 import QtGui
import data_ticino
import data_loulouka
#from data_ticino import c, cv, ptb, lbda, pt, aap, cps
#from data_loulouka import c, cv, ptb, lbda, pt, aap, cps

class mygraphicsview(QtGui.QGraphicsView):

    def __init__(self, parent = None):
        super(QtGui.QGraphicsView, self).__init__(parent)

    def resizeEvent(self, event):
        scene = self.scene()
        scene.update(self.size())
        self.resetCachedContent()

if __name__ == "__main__":
    etri = electre_tri(data_ticino.c, data_ticino.cv, data_ticino.ptb,
                       data_ticino.lbda, data_ticino.cps)
    etri2 = electre_tri(data_loulouka.c, data_loulouka.cv,
                        data_loulouka.ptb, data_loulouka.lbda,
                        data_loulouka.cps)

    app = QtGui.QApplication(sys.argv)

    sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding);
    sizePolicy.setHorizontalStretch(1);
    sizePolicy.setVerticalStretch(0);
    sizePolicy.setHeightForWidth(sizePolicy.hasHeightForWidth());

    view = mygraphicsview()
    view.setRenderHint(QtGui.QPainter.Antialiasing)
    view.setSizePolicy(sizePolicy)
    view2 = mygraphicsview()
    view2.setRenderHint(QtGui.QPainter.Antialiasing)
    view2.setSizePolicy(sizePolicy)

    layout = QtGui.QHBoxLayout()
    layout.addWidget(view)
    layout.addWidget(view2)

    dialog = QtGui.QDialog()
    dialog.setLayout(layout)
#    dialog.resize(640, 480)
    dialog.resize(1024, 400)

    graph = graph_etri(etri, data_ticino.pt, view.size())
    graph2 = graph_etri(etri2, data_loulouka.pt, view2.size())
    view.setScene(graph)
    view2.setScene(graph2)

    dialog.show()
    app.exec_()
