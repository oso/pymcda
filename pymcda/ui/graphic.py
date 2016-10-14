from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../../")
import colorsys
from itertools import combinations
from PyQt4 import QtCore
from PyQt4 import QtGui

def display_electre_tri_models(etri, worst = list(), best = list(),
                               aps = list(), aps2 = list(), aps3 = list(),
                               aps4 = list()):
    app = QtGui.QApplication(sys.argv)

    sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
    sizePolicy.setHorizontalStretch(1)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(sizePolicy.hasHeightForWidth())

    layout = QtGui.QGridLayout()

    ncol = len(etri) / 2
    i = j = 0
    views = {}
    for n, m in enumerate(etri):
        view = _MyGraphicsview()
        view.setRenderHint(QtGui.QPainter.Antialiasing)
        view.setSizePolicy(sizePolicy)

        if j == ncol-1:
            i += 1
            j = 0
        else:
            j += 1

        views[n] = view
        layout.addWidget(view, i, j, 1, 1)

    dialog = QtGui.QDialog()
    dialog.setLayout(layout)
    dialog.resize(1024, 768)

    for i, m in enumerate(etri):
        graph = QGraphicsSceneEtri(m, worst[i], best[i], views[i].size(),
                                   parent = views[i])
        if aps and aps[i]:
            for ap in aps[i]:
                graph.plot_alternative_performances(ap, False,
                                                    QtGui.QColor("blue"))

        if aps2 and aps2[i]:
            for ap in aps2[i]:
                graph.plot_alternative_performances(ap, False,
                                                    QtGui.QColor("red"),
                                                    False)

        if aps3 and aps3[i]:
            for ap in aps3[i]:
                graph.plot_alternative_performances(ap, False,
                                                    QtGui.QColor("yellow"),
                                                    False)
        if aps4 and aps4[i]:
            for ap in aps4[i]:
                graph.plot_alternative_performances(ap, False,
                                                    QtGui.QColor("orange"),
                                                    False)

        views[i].setScene(graph)

    dialog.show()
    app.exec_()

class _MyGraphicsview(QtGui.QGraphicsView):

    def __init__(self, parent = None):
        super(QtGui.QGraphicsView, self).__init__(parent)

    def resizeEvent(self, event):
        scene = self.scene()
        scene.update(self.size())
        self.resetCachedContent()

class QGraphicsSceneEtri(QtGui.QGraphicsScene):

    def __init__(self, model, worst, best, size, criteria_order = None,
                 parent = None):
        super(QGraphicsSceneEtri, self).__init__(parent)
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
        self.axis_height = self.size.height() - 100
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

            if self.model.veto_weights is None:
                txt = "%s<br>(%g)" % (criterion.id, self.model.cv[id].value)
            else:
                txt = "%s<br>(%g)<br>(%g)" % (criterion.id, self.model.cv[id].value,
                                   self.model.veto_weights[id].value)

            text = QtGui.QGraphicsTextItem()
            text.setHtml("<div align=\"center\">%s</div>" % txt)
            text.setTextWidth(text.boundingRect().width())
            font = QtGui.QFont()
            font.setBold(True)
            text.setFont(font)
            text.setZValue(1)
            text.setPos(x - text.boundingRect().width() / 2, 0)
            self.addItem(text)

            self.axis_text_items[criterion] = text

    def __compute_y(self, ap, id):
        direction = self.model.criteria[id].direction
        p = ap.performances[id] * direction
        best = self.best.performances[id] * direction
        worst = self.worst.performances[id] * direction
        if p > best:
            p = best
        elif p < worst:
            p = worst
        num = p - worst
        den = best - worst
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

    def __create_profile(self, ap, print_values,
                         color = QtGui.QColor("red"),
                         link = True,
                         points = False):
        item = QtGui.QGraphicsPathItem()

        pen = QtGui.QPen()
        pen.setBrush(color)
        item.setPen(pen)

        text_items = []

        path = item.path()
        for i, cid in enumerate(self.criteria_order):
            y = self.__compute_y(ap, cid)

            if i == 0:
                x = 0
                path.moveTo(0, y)
            else:
                x += self.hspacing
                if link is True:
                    path.lineTo(x, y)

            if points is True:
                it = self.addEllipse(x - 3, y - 3, 6, 6, pen, pen.brush())
                it.setZValue(2)

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
            item, text_items = self.__create_profile(profile, False)
            self.addItem(item)
            self.profiles_items[profile.id] = item
            self.profiles_text_items[profile.id] = text_items
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
        item.setBrush(color)

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

    def update_intersections(self):
        self.__clear_intersections()
        self.__higlight_intersections()

    def __plot_alternatives(self):
        for ap, (item, print_values, color, link) in self.ap_items.items():
            item, text_items = self.__create_profile(ap, print_values, color, link, True)
            self.addItem(item)

    def __update_category(self, i, cat, ap_below, ap_above):
        item = self.category_items[cat]
        path = item.path()

        for i, cid in enumerate(self.criteria_order):
            y_above = self.__compute_y(ap_above, cid)
            y_below = self.__compute_y(ap_below, cid)

            i2 = 2 * len(self.criteria_order) - 1 - i
            if i == 0:
                x = 0
            else:
                x += self.hspacing

            path.setElementPositionAt(i, x, y_above)
            path.setElementPositionAt(i2, x, y_below)

        item.setPath(path)

    def update_categories(self):
        ncat = len(self.model.categories)
        for i, cat in enumerate(self.model.categories):
            if i == 0:
                ap_below = self.worst
            else:
                ap_below = self.model.bpt[self.model.profiles[i - 1]]

            if i == ncat - 1:
                ap_above = self.best
            else:
                ap_above = self.model.bpt[self.model.profiles[i]]

            self.__update_category(i, cat, ap_below, ap_above)

        self.update_intersections()

    def update_profile(self, profile):
        item = self.profiles_items[profile]
        text_items = self.profiles_text_items[profile]
        if profile == 'worst':
            ap = self.worst
        elif profile == 'best':
            ap = self.best
        else:
            ap = self.model.bpt[profile]

        path = item.path()

        for i, cid in enumerate(self.criteria_order):
            y = self.__compute_y(ap, cid)

            if i == 0:
                x = 0
            else:
                x += self.hspacing

            path.setElementPositionAt(i, x, y)

            if len(text_items) > 0:
                txtitem = text_items[i]
                txtitem.setPos(x, y)
                txtitem.setPlainText("%g" % ap.performances[cid])

        item.setPath(path)

    def update_profiles(self):
        for profile in self.profiles_items.keys():
            self.update_profile(profile)

    def plot_alternative_performances(self, ap,
                                      print_values = False,
                                      color = QtGui.QColor("red"),
                                      link = True):
        item, text_items = self.__create_profile(ap, print_values, color,
                                                 link, True)
        self.addItem(item)

        self.ap_items[ap] = (item, print_values, color, link)

if __name__ == "__main__":
    import random
    from pymcda.generate import generate_alternatives
    from pymcda.generate import generate_criteria
    from pymcda.generate import generate_random_criteria_values
    from pymcda.generate import generate_random_performance_table
    from pymcda.generate import generate_categories
    from pymcda.generate import generate_random_profiles
    from pymcda.generate import generate_categories_profiles
    from pymcda.electre_tri import ElectreTri
    from pymcda.types import AlternativePerformances

    a = generate_alternatives(2)
    c = generate_criteria(5)
    cv = generate_random_criteria_values(c, 1234)
    cv.normalize_sum_to_unity()

    worst = AlternativePerformances("worst", {crit.id: 0 for crit in c})
    best = AlternativePerformances("best", {crit.id: 1 for crit in c})
    pt = generate_random_performance_table(a, c)

    cat = generate_categories(3)
    cps = generate_categories_profiles(cat)
    b = cps.get_ordered_profiles()
    bpt = generate_random_profiles(b, c)
    bpt['b2'].performances['c3'] = 0.2

    lbda = random.uniform(0.5, 1)

    model = ElectreTri(c, cv, bpt, lbda, cps)

    app = QtGui.QApplication(sys.argv)

    sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
    sizePolicy.setHorizontalStretch(1)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(sizePolicy.hasHeightForWidth())

    view = _MyGraphicsview()
    view.setRenderHint(QtGui.QPainter.Antialiasing)
    view.setSizePolicy(sizePolicy)

    graph = QGraphicsSceneEtri(model, worst, best, view.size())

    view.setScene(graph)
    view.show()
    graph.plot_alternative_performances(pt['a1'], False, QtGui.QColor("red"))
    graph.plot_alternative_performances(pt['a2'], False, QtGui.QColor("blue"))

    app.exec_()
