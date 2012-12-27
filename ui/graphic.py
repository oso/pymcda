from __future__ import division
import colorsys
import sys
sys.path.insert(0, "..")
from itertools import combinations
from PyQt4 import QtCore
from PyQt4 import QtGui
from tools.utils import get_worst_alternative_performances
from tools.utils import get_best_alternative_performances

def display_electre_tri_models(etri, worst = [], best = [], aps = []):
    app = QtGui.QApplication(sys.argv)

    sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding);
    sizePolicy.setHorizontalStretch(1);
    sizePolicy.setVerticalStretch(0);
    sizePolicy.setHeightForWidth(sizePolicy.hasHeightForWidth());

    layout = QtGui.QGridLayout()

    ncol = len(etri) / 2
    i = j = 0
    views = {}
    for m in etri:
        view = mygraphicsview()
        view.setRenderHint(QtGui.QPainter.Antialiasing)
        view.setSizePolicy(sizePolicy)

        if j == ncol-1:
            i += 1
            j = 0
        else:
            j += 1

        views[m] = view
        layout.addWidget(view, i, j, 1, 1)

    dialog = QtGui.QDialog()
    dialog.setLayout(layout)
    dialog.resize(1024, 768)

    for i, m in enumerate(etri):
        graph = QGraphicsScene_etri(m, worst[i], best[i], views[m].size())
        views[m].setScene(graph)
        if aps and aps[i]:
            for ap in aps[i]:
                graph.plot_alternative_performances(ap)

    dialog.show()
    app.exec_()

class mygraphicsview(QtGui.QGraphicsView):

    def __init__(self, parent = None):
        super(QtGui.QGraphicsView, self).__init__(parent)

    def resizeEvent(self, event):
        scene = self.scene()
        scene.update(self.size())
        self.resetCachedContent()

class QGraphicsScene_etri(QtGui.QGraphicsScene):

    def __init__(self, model, worst, best, size, criteria_order = None,
                 parent = None):
        super(QtGui.QGraphicsScene, self).__init__(parent)
        self.model = model
        if criteria_order:
            self.criteria_order = criteria_order
        else:
            self.criteria_order = self.model.criteria.keys()
            self.criteria_order.sort()
        self.worst = worst
        self.best = best

        self.ap_items = {}

        self.update(size)

    def update(self, size):
        self.size = size
        self.axis_height = self.size.height() - 45
        self.ymax = -self.axis_height + 25 / 2
        self.ymin = -25 / 2

        self.hspacing = size.width()/len(self.model.criteria)
        if self.hspacing < 100:
            self.hspacing = 100

        self.clear()
        self.__plot_axis()
        self.__plot_profiles()
        self.__plot_categories()
        self.__higlight_intersections()
        self.__plot_alternatives()
        self.setSceneRect(self.itemsBoundingRect())

    def __create_axis(self, xmin, xmax, ymin, ymax, direction):
        item = QtGui.QGraphicsPathItem()

        path = item.path()
        path.moveTo(xmin, ymin)
        path.lineTo(xmax, ymax)

        if direction == -1:
            x = xmin
            y = ymin
        else:
            x = xmax
            y = ymax

        path.moveTo(x, y)
        path.lineTo(x - 3, y + direction * 6)
        path.lineTo(x + 3, y + direction * 6)
        path.closeSubpath()

        pen = QtGui.QPen()
        pen.setWidth(2)
        item.setPen(pen)

        brush = QtGui.QBrush(QtGui.QColor("black"))
        item.setBrush(brush)

        item.setPath(path)

        return item

    def __plot_axis(self):
        self.axis_text_items = {}
        self.axis_items = {}

        for i, id in enumerate(self.criteria_order):
            criterion = self.model.criteria[id]
            x = i * self.hspacing

            axis = self.__create_axis(x, x, 0, -self.axis_height,
                                      criterion.direction)
            axis.setZValue(1)
            self.addItem(axis)
            self.axis_items[id] = axis

            if criterion.name:
                text = self.addText(criterion.name)
            else:
                text = self.addText(criterion.id)
            font = QtGui.QFont()
            font.setBold(True)
            text.setFont(font)
            text.setZValue(1)
            text.setPos(x - text.boundingRect().width() / 2, 0)

            self.axis_text_items[criterion] = text

    def __compute_y(self, ap, id):
        num = ap.performances[id] - self.worst.performances[id]
        den = self.best.performances[id] - self.worst.performances[id]
        return self.ymin + num / den * (self.ymax - self.ymin)

    def __create_text_value(self, value):
        item = QtGui.QGraphicsTextItem()

        item.setPlainText(value)

        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(6)
        item.setFont(font)
        item.setZValue(1)

        return item

    def __create_profile(self, ap, print_values = False,
                         color = QtGui.QColor("red")):
        item = QtGui.QGraphicsPathItem()

        pen = QtGui.QPen()
        pen.setBrush(color)
        item.setPen(pen)

        text_items = []

        path = item.path()
        for i, cid in enumerate(self.criteria_order):
            y = self.__compute_y(ap, cid)
            if y > self.worst.performances[cid]:
                y = self.worst.performances[cid]

            if i == 0:
                x = 0
                path.moveTo(0, y)
            else:
                x += self.hspacing
                path.lineTo(x, y)

            if print_values is True:
                txt = "%g" % ap.performances[cid]
                txtitem = self.__create_text_value(txt)
                txtitem.setPos(x, y)
                text_items.append(txtitem)

        item.setPath(path)

        return item, text_items

    def __plot_profiles(self):
        self.profiles_items = {}
        self.profiles_text_items = {}

        bpt = self.model.bpt
        for profile in self.model.profiles:
            item, text_items = self.__create_profile(bpt[profile], True)
            self.addItem(item)
            self.profiles_items[profile] = item
            self.profiles_text_items[profile] = text_items
            for txtitem in text_items:
                self.addItem(txtitem)

        for profile in [self.worst, self.best]:
            item, text_items = self.__create_profile(profile)
            self.addItem(item)
            self.profiles_items[profile.alternative_id] = item
            self.profiles_text_items[profile.alternative_id] = text_items
            for txtitem in text_items:
                self.addItem(txtitem)

    def __get_category_color(self, i):
        n = len(self.model.categories)
        g = 255 - 220 * (n - i) / n
        return QtGui.QColor(0, g, 0)

    def __create_category(self, i, path_below, path_above):
        item = QtGui.QGraphicsPathItem()

        path = item.path()
        path.addPath(path_above)
        path.connectPath(path_below.toReversed())
        path.closeSubpath()

        color = self.__get_category_color(i)
        item.setBrush(color);

        item.setPath(path)

        return item

    def __plot_categories(self):
        self.category_items = {}
        for i, category in enumerate(self.model.categories):
            if i == 0:
                lower = self.profiles_items['worst']
            else:
                lower = self.profiles_items[self.model.profiles[i - 1]]
            if i == len(self.model.profiles):
                lower = self.profiles_items['best']
            else:
                upper = self.profiles_items[self.model.profiles[i]]

            item = self.__create_category(i, lower.path(), upper.path())
            self.addItem(item)

            self.category_items[category] = item

    def __clear_intersections(self):
        for item in self.intersection_items:
            self.removeItem(item)
        self.intersection_items = []

    def __higlight_intersections(self):
        self.intersection_items = []
        combis = list(combinations(self.category_items.values(), r = 2))
        for combi in combis:
            a = combi[0].path()
            b = combi[1].path()
            c = a.intersected(b)

            item = QtGui.QGraphicsPathItem(c)
            brush = QtGui.QBrush(QtGui.QColor("yellow"))
            item.setBrush(brush)
            self.addItem(item)

            self.intersection_items.append(item)

    def __plot_alternatives(self):
        for ap, item in self.ap_items.items():
            item, text_items = self.__create_profile(ap)
            self.addItem(item)

    def plot_alternative_performances(self, ap):
        item, text_items = self.__create_profile(ap)
        self.addItem(item)

        self.ap_items[ap] = item

if __name__ == "__main__":
    import random
    from tools.generate_random import generate_random_alternatives
    from tools.generate_random import generate_random_criteria
    from tools.generate_random import generate_random_criteria_values
    from tools.generate_random import generate_random_performance_table
    from tools.generate_random import generate_random_categories
    from tools.generate_random import generate_random_profiles
    from tools.generate_random import generate_random_categories_profiles
    from tools.utils import normalize_criteria_weights
    from mcda.electre_tri import electre_tri
    from mcda.types import alternative_performances

    a = generate_random_alternatives(1)
    c = generate_random_criteria(5)
    cv = generate_random_criteria_values(c, 1234)
    normalize_criteria_weights(cv)

    worst = alternative_performances("worst", {crit.id: 0 for crit in c})
    best = alternative_performances("best", {crit.id: 1 for crit in c})
    pt = generate_random_performance_table(a, c)

    cat = generate_random_categories(3)
    cps = generate_random_categories_profiles(cat)
    b = cps.get_ordered_profiles()
    bpt = generate_random_profiles(b, c)
    bpt['b2'].performances['c3'] = 0.2

    lbda = random.uniform(0.5, 1)

    model = electre_tri(c, cv, bpt, lbda, cps)

    app = QtGui.QApplication(sys.argv)

    sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding);
    sizePolicy.setHorizontalStretch(1);
    sizePolicy.setVerticalStretch(0);
    sizePolicy.setHeightForWidth(sizePolicy.hasHeightForWidth());

    view = mygraphicsview()
    view.setRenderHint(QtGui.QPainter.Antialiasing)
    view.setSizePolicy(sizePolicy)

    graph = QGraphicsScene_etri(model, worst, best, view.size())

    view.setScene(graph)
    view.show()
    graph.plot_alternative_performances(pt['a1'])

    app.exec_()
