from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
from PyQt4 import QtCore
from PyQt4 import QtGui
import sys

COL_NAME = 0
COL_DIRECTION = 1
COL_WEIGHT = 2

class qt_criteria_table(QtGui.QTableWidget):

    def __init__(self, parent = None):
        super(QtGui.QTableWidget, self).__init__(parent)

        self.row_crit = {}

        self.setColumnCount(3)
        self.setShowGrid(False)
        self.setDragEnabled(False)
        self.__add_headers()
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setSortIndicatorShown(False)
        self.horizontalHeader().setHighlightSections(False)

    def reset_table(self):
        self.clearContents()
        self.setRowCount(0)
        self.row_crit = {}

    def __add_headers(self):
        item = QtGui.QTableWidgetItem()
        item.setText("Criterion")
        item.setTextAlignment(QtCore.Qt.AlignLeft)
        self.setHorizontalHeaderItem(COL_NAME, item)

        item = QtGui.QTableWidgetItem()
        self.setHorizontalHeaderItem(COL_DIRECTION, item)

        item = QtGui.QTableWidgetItem()
        item.setText("Weight")
        item.setTextAlignment(QtCore.Qt.AlignRight)
        self.setHorizontalHeaderItem(COL_WEIGHT, item)

    def __on_criterion_direction_changed(self, row):
        c, cv = self.row_crit[row]
        item = self.cellWidget(row, 1)
        if item.currentIndex() == 0:
            c.direction = 1
        else:
            c.direction = -1
        self.emit(QtCore.SIGNAL("criterion_direction_changed"), c.id)

    def __on_criterion_state_changed(self, row):
        c, cv = self.row_crit[row]
        item = self.cellWidget(row, 0)
        if item.isChecked() == 1:
            c.disabled = False
        else:
            c.disabled = True
        self.emit(QtCore.SIGNAL("criterion_state_changed"), c.id)

    def __add_combo_signal(self, combo, row):
        smapper = QtCore.QSignalMapper(self)
        QtCore.QObject.connect(combo,
                               QtCore.SIGNAL("currentIndexChanged(int)"),
                               smapper, QtCore.SLOT("map()"))
        smapper.setMapping(combo, row)
        QtCore.QObject.connect(smapper, QtCore.SIGNAL("mapped(int)"),
                               self.__on_criterion_direction_changed)

    def __add_cbox_signal(self, cbox, row):
        smapper = QtCore.QSignalMapper(self)
        QtCore.QObject.connect(cbox, QtCore.SIGNAL("stateChanged(int)"),
                                smapper, QtCore.SLOT("map()"))
        smapper.setMapping(cbox, row)
        QtCore.QObject.connect(smapper, QtCore.SIGNAL("mapped(int)"),
                                self.__on_criterion_state_changed)

    def add_criterion(self, c, cv):
        row = self.rowCount()
        self.insertRow(row)

        self.row_crit[row] = (c, cv)

        # Add first cell with name and checkbox
        item = QtGui.QTableWidgetItem()
        item.setFlags(QtCore.Qt.ItemIsTristate)
        self.setItem(row, COL_NAME, item)

        cbox = QtGui.QCheckBox(self)
        if c.disabled is not True:
            cbox.setCheckState(QtCore.Qt.Checked)
        if c.name:
            cbox.setText(c.name)
        else:
            cbox.setText(c.id)
        self.__add_cbox_signal(cbox, row)
        self.setCellWidget(row, COL_NAME, cbox)

        # Add direction cell
        item = QtGui.QTableWidgetItem()
        item.setFlags(QtCore.Qt.ItemIsTristate)
        self.setItem(row, COL_DIRECTION, item)
        combo = QtGui.QComboBox(self)
        combo.addItem("Max")
        combo.addItem("Min")
        if c.direction == -1:
            combo.setCurrentIndex(1)
        self.__add_combo_signal(combo, row)
        self.setCellWidget(row, COL_DIRECTION, combo)

        # Add weight column
        item = QtGui.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        item.setText(str(cv.value))
        self.setItem(row, COL_WEIGHT, item)

    def add_criteria(self, cs, cvs):
        for c in cs:
            self.add_criterion(c, cvs[c.id])

if __name__ == "__main__":
    from tools.generate_random import generate_random_criteria
    from tools.generate_random import generate_random_criteria_weights

    c = generate_random_criteria(5)
    cw = generate_random_criteria_weights(c)

    app = QtGui.QApplication(sys.argv)

    table = qt_criteria_table()
    table.add_criteria(c, cw)
    table.resize(640, 480)
    table.show()

    app.exec_()
