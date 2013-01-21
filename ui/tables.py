from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")
from PyQt4 import QtCore
from PyQt4 import QtGui
import sys

COL_NAME = 0
COL_DIRECTION = 1
COL_WEIGHT = 2

class float_delegate(QtGui.QItemDelegate):

    def __init__(self, parent=None, columns=None):
        super(QtGui.QItemDelegate, self).__init__(parent)
        self.columns = columns

    def createEditor(self, parent, option, index):
        if self.columns == None or index.column() in self.columns:
            line = QtGui.QLineEdit(parent)
            expr = QtCore.QRegExp("[0-9]*\.?[0-9]*")
            line.setValidator(QtGui.QRegExpValidator(expr, self))
            return line
        else:
            QtGui.QItemDelegate.createEditor(self, parent, option, index)

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

        self.connect(self, QtCore.SIGNAL("cellChanged(int,int)"),
                     self.__cell_changed)
        self.setItemDelegate(float_delegate(self, [COL_WEIGHT]))

    def __cell_changed(self, row, col):
        if col == COL_WEIGHT:
            if self.row_crit.has_key(row) is False:
                return

            c, cv = self.row_crit[row]
            item = self.cellWidget(row, col)
            if item == None:
                return

            try:
                value = str(item.text())
                if value.find('.') == -1:
                    cv.value = int(value)
                else:
                    cv.value = float(value)
            except:
                QtGui.QMessageBox.warning(self,
                                          "Criterion [%s] %s"
                                          % (c.id, c.name),
                                          "Invalid weight value")

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

class qt_performance_table(QtGui.QTableWidget):

    def __init__(self, crits = None, parent = None):
        super(QtGui.QTableWidget, self).__init__(parent)
        self.parent = parent
        self.col_crit = {}
        self.row_ap = {}

        self.setItemDelegate(float_delegate(self))

        self.connect(self, QtCore.SIGNAL("cellChanged(int,int)"),
                     self.__cell_changed)

        if crits is not None:
            self.add_criteria(crits)

    def __cell_changed(self, row, col):
        if self.col_crit.has_key(col) is False or   \
            self.row_ap.has_key(row) is False:
            return

        ap = self.row_ap[row]
        crit = self.col_crit[col]

        item = self.cellWidget(row, col)
        if item == None:
            return

        try:
            value = str(item.text())
            if value.find('.') == -1:
               ap.performances[crit.id] = int(value)
            else:
               ap.performances[crit.id] = float(value)
        except:
            QtGui.QMessageBox.warning(self,
                                      "Alternative [%s] %s"
                                      % (alt.id, alt.name),
                                      "Invalid evaluation")

    def reset_table(self):
        self.clear()
        self.setRowCount(0)
        self.setColumnCount(0)
        self.col_crit = {}
        self.row_ap = {}

    def add_criterion(self, c):
        col = self.columnCount()
        self.insertColumn(col)
        item = QtGui.QTableWidgetItem()
        self.setHorizontalHeaderItem(col, item)
        if c.name:
            self.horizontalHeaderItem(col).setText(c.name)
        else:
            self.horizontalHeaderItem(col).setText(c.id)
        if c.disabled is True:
            self.setColumnHidden(col, True)
        self.col_crit[col] = c

    def add_criteria(self, cs):
        for c in cs:
            self.add_criterion(c)

    def add_alternative_performances(self, a, ap):
        row = self.rowCount()
        self.insertRow(row)

        item = QtGui.QTableWidgetItem()
        self.setVerticalHeaderItem(row, item)
        if a.name:
            self.verticalHeaderItem(row).setText(a.name)
        else:
            self.verticalHeaderItem(row).setText(a.id)

        performances = ap.performances
        for col, crit in self.col_crit.iteritems():
            item = QtGui.QTableWidgetItem()
            if performances.has_key(crit.id):
                 item.setText(str(performances[crit.id]))
            self.setItem(row, col, item)

        self.row_ap[row] = ap

    def add_pt(self, alts, pt):
        for a in alts:
            self.add_alternative_performances(a, pt[a.id])

if __name__ == "__main__":
    from mcda.generate import generate_criteria
    from mcda.generate import generate_random_criteria_weights
    from mcda.generate import generate_alternatives
    from mcda.generate import generate_random_performance_table

    c = generate_criteria(5)
    cw = generate_random_criteria_weights(c)

    a = generate_alternatives(100)
    pt = generate_random_performance_table(a, c)

    app = QtGui.QApplication(sys.argv)

    layout = QtGui.QVBoxLayout()
    tabs = QtGui.QTabWidget()
    layout.addWidget(tabs)

    # Criteria table
    table = qt_criteria_table()
    table.add_criteria(c, cw)

    tab = QtGui.QWidget()
    layout = QtGui.QVBoxLayout(tab)
    layout.addWidget(table)
    tabs.addTab(tab, "Criteria")

    # Performance table
    table = qt_performance_table(c)
    table.add_pt(a, pt)

    tab = QtGui.QWidget()
    layout = QtGui.QVBoxLayout(tab)
    layout.addWidget(table)
    tabs.addTab(tab, "Performance table")

    layout = QtGui.QVBoxLayout()
    layout.addWidget(tabs)
    dialog = QtGui.QDialog()
    dialog.setLayout(layout)
    dialog.resize(640, 480)
    dialog.show()

    app.exec_()
