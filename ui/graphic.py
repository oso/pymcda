from __future__ import division
import colorsys
import sys
sys.path.insert(0, "..")
from PyQt4 import QtCore
from PyQt4 import QtGui
from tools.utils import get_worst_alternative_performances
from tools.utils import get_best_alternative_performances

def display_electre_tri_models(etri, pt):
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
        graph = graph_etri(m, pt[i], views[m].size())
        views[m].setScene(graph)

    dialog.show()
    app.exec_()

class mygraphicsview(QtGui.QGraphicsView):

    def __init__(self, parent = None):
        super(QtGui.QGraphicsView, self).__init__(parent)

    def resizeEvent(self, event):
        scene = self.scene()
        scene.update(self.size())
        self.resetCachedContent()

class axis(QtGui.QGraphicsItem):

    def __init__(self, x1, y1, x2, y2, direction, parent=None):
        super(QtGui.QGraphicsItem, self).__init__(parent)

        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

        self.path = QtGui.QPainterPath()
        self.path.moveTo(x1, y1)
        self.path.lineTo(x2, y2)
        self.__set_arrow(direction)

    def boundingRect(self):
        return self.path.boundingRect()

    def paint(self, painter, option, widget=None):
        pen = QtGui.QPen()
        pen.setWidth(2)
        brush = QtGui.QBrush(QtGui.QColor("black"))
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawPath(self.path)

    def __set_arrow(self, direction):
        if direction == -1:
            x = self.x1
            y = self.y1
        else:
            x = self.x2
            y = self.y2

        self.path.moveTo(x, y)
        self.path.lineTo(x-3, y+direction*6)
        self.path.lineTo(x+3, y+direction*6)
        self.path.closeSubpath()

class QGraphicsPathItem_profile(QtGui.QGraphicsPathItem):

    def __init__(self, ap, ymin, ymax, ap_worst, ap_best, criteria_order,
                 hspacing, parent = None):
        super(QtGui.QGraphicsPathItem, self).__init__(parent)
        self.ap = ap
        self.ap_worst = ap_worst
        self.ap_best = ap_best
        self.ymin = ymin
        self.ymax = ymax
        self.criteria_order = criteria_order
        self.hspacing = hspacing

        pen = QtGui.QPen()
        pen.setBrush(QtGui.QColor("blue"))
        self.setPen(pen)

        self.__draw_profile()

    def __compute_y(self, id):
        num = self.ap.performances[id] - self.ap_worst.performances[id]
        den = self.ap_best.performances[id] - self.ap_worst.performances[id]
        y = self.ymin + num / den * (self.ymax - self.ymin)
        return y

    def __draw_profile(self):
        path = self.path()

        x = 0
        y = self.__compute_y(self.criteria_order[0])
        path.moveTo(0, y)
        for cid in self.criteria_order[1:]:
            x += self.hspacing
            y = self.__compute_y(cid)
            path.lineTo(x, y)

        self.setPath(path)

class QGraphicsPathItem_category(QtGui.QGraphicsPathItem):

    def __init__(self, c_rank, ncategories,  path_below, path_above,
                 parent = None):
        super(QtGui.QGraphicsPathItem, self).__init__(parent)

        self.c_rank = c_rank
        self.ncategories = ncategories

        path = self.path()

        path.addPath(path_above)
        pathb = path_below.toReversed()
        path.connectPath(pathb)
        path.closeSubpath()

        color = self.__get_category_color()
        self.setBrush(color);

        self.setPath(path)

    def __get_category_color(self):
        g = 255 - 220 * (self.ncategories - self.c_rank) / self.ncategories
        return QtGui.QColor(0, g, 0)

class graph_etri(QtGui.QGraphicsScene):

    def __init__(self, model, pt, size, criteria_order = None,
                 worst = None, best = None, parent = None):
        super(QtGui.QGraphicsScene, self).__init__(parent)
        self.model = model
        self.pt = pt
        if criteria_order:
            self.criteria_order = criteria_order
        else:
            self.criteria_order = self.model.criteria.keys()
            self.criteria_order.sort()
        self.worst = worst
        self.best = best

        self.profiles_items = dict()

        self.update(size)

    def update(self, size):
        self.size = size
        if self.worst is None:
            self.worst = get_worst_alternative_performances(self.pt,
                                                        self.model.criteria)
        if self.best is None:
            self.best = get_best_alternative_performances(self.pt,
                                                      self.model.criteria)
        self.axis_height = self.size.height()-45
        self.model_height = self.axis_height-25

        self.hspacing = size.width()/len(self.model.criteria)
        if self.hspacing < 100:
            self.hspacing = 100

        self.clear()
        self.__plot_axis()
        self.__plot_profiles()
        self.__plot_categories()
        self.setSceneRect(self.itemsBoundingRect())

    def __plot_axis(self):
        self.criteria_text = {}

        for i, id in enumerate(self.criteria_order):
            criterion = self.model.criteria[id]
            x = i*self.hspacing

            line = axis(x, 0, x, -self.axis_height, criterion.direction)
            line.setZValue(1)
            self.addItem(line)

            if criterion.name:
                text = self.addText(criterion.name)
            else:
                text = self.addText(criterion.id)
            font = QtGui.QFont()
            font.setBold(True)
            text.setFont(font)
            text.setZValue(1)
            text.setPos(x-text.boundingRect().width()/2, 0)

            self.criteria_text[criterion] = text

#    def __profile_get_points(self, ap):
#        axis_unused = self.axis_height-self.model_height
#        limsup = -self.axis_height+axis_unused/2
#        liminf = -axis_unused/2
#
#        n = len(self.model.criteria)
#        points = []
#        for i, id in enumerate(self.criteria_order):
#            criterion = self.model.criteria[id]
#            x = i*self.hspacing
#
#            num = ap.performances[criterion.id] - self.worst.performances[criterion.id]
#            den = self.best.performances[criterion.id] - self.worst.performances[criterion.id]
#            if den == 0:
#                p = QtCore.QPointF(x, liminf)
#            elif num == 0:
#                p = QtCore.QPointF(x, liminf)
#            else:
#                y = liminf+(limsup-liminf)*num/den
#                p = QtCore.QPointF(x, y)
#
#            text = self.addText("%g" % ap.performances[criterion.id])
#            font = QtGui.QFont()
#            font.setBold(True)
#            font.setPointSize(6)
#            text.setFont(font)
#            text.setPos(p)
#            text.setZValue(1)
#
#            points.append(p)
#
#        return points

    def __add_profile(self, ap):
        pass

    def __plot_profiles(self):
        axis_unused = self.axis_height - self.model_height
        limsup = -self.axis_height + axis_unused / 2
        liminf = -axis_unused / 2

        bpt = self.model.bpt
        for profile in self.model.profiles:
            item = QGraphicsPathItem_profile(bpt[profile], liminf, limsup, self.worst, self.best, self.criteria_order, self.hspacing)
            self.addItem(item)
            self.profiles_items[profile] = item

        for profile in [self.worst, self.best]:
            item = QGraphicsPathItem_profile(profile, liminf, limsup, self.worst, self.best, self.criteria_order, self.hspacing)
            self.addItem(item)
            self.profiles_items[profile.alternative_id] = item

    def __plot_categories(self):
        n = len(self.model.categories)
        for i, category in enumerate(self.model.categories):
            if i == 0:
                lower = self.profiles_items['worst']
            else:
                lower = self.profiles_items[self.model.profiles[i - 1]]
            if i == len(self.model.profiles):
                lower = self.profiles_items['best']
            else:
                upper = self.profiles_items[self.model.profiles[i]]

            item = QGraphicsPathItem_category(i, n, lower.path(),
                                              upper.path())
            self.addItem(item)

    def plot_alternative_performances(self, ap):
        axis_unused = self.axis_height - self.model_height
        limsup = -self.axis_height + axis_unused / 2
        liminf = -axis_unused / 2

        item = QGraphicsPathItem_profile(ap, liminf, limsup, self.worst, self.best, self.criteria_order, self.hspacing)
        self.addItem(item)

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

    a = generate_random_alternatives(10000)
    c = generate_random_criteria(5)
    cv = generate_random_criteria_values(c, 1234)
    normalize_criteria_weights(cv)
    pt = generate_random_performance_table(a, c)

    cat = generate_random_categories(3)
    cps = generate_random_categories_profiles(cat)
    b = cps.get_ordered_profiles()
    bpt = generate_random_profiles(b, c)

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

    graph = graph_etri(model, pt, view.size())

    view.setScene(graph)
    view.show()
    graph.plot_alternative_performances(pt['a1'])

    app.exec_()
