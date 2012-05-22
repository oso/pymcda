from PyQt4 import QtCore
from PyQt4 import QtGui
import colorsys
import sys
from mcda.electre_tri import electre_tri
from tools.utils import get_worst_alternative_performances
from tools.utils import get_best_alternative_performances

def display_electre_tri_models(etri, etri2, pt, pt2):
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
    dialog.resize(1024, 400)

    graph = graph_etri(etri, pt, view.size())
    graph2 = graph_etri(etri2, pt, view2.size())
    view.setScene(graph)
    view2.setScene(graph2)

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


class graph_etri(QtGui.QGraphicsScene):

    def __init__(self, model, pt, size, parent=None):
        super(QtGui.QGraphicsScene, self).__init__(parent)
        self.model = model
        self.pt = pt
        self.update(size)

    def update(self, size):
        self.size = size
        self.worst = get_worst_alternative_performances(self.pt,
                                                        self.model.criteria)
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
        self.setSceneRect(self.itemsBoundingRect())

    def __plot_axis(self):
        self.criteria_text = {}

        for i, criterion in enumerate(self.model.criteria):
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

    def __profile_get_points(self, ap):
        axis_unused = self.axis_height-self.model_height
        limsup = -self.axis_height+axis_unused/2
        liminf = -axis_unused/2

        n = len(self.model.criteria)
        points = []
        for i, criterion in enumerate(self.model.criteria):
            x = i*self.hspacing

            num = ap.performances[criterion.id] - self.worst.performances[criterion.id]
            den = self.best.performances[criterion.id] - self.worst.performances[criterion.id]
            if den == 0:
                p = QtCore.QPointF(x, liminf)
            elif num == 0:
                p = QtCore.QPointF(x, liminf)
            else:
                y = liminf+(limsup-liminf)*num/den
                p = QtCore.QPointF(x, y)

            text = self.addText("%g" % ap.performances[criterion.id])
            font = QtGui.QFont()
            font.setBold(True)
            font.setPointSize(6)
            text.setFont(font)
            text.setPos(p)
            if i == n-1:
                text.moveBy(-text.boundingRect().width(), 0)
            text.setZValue(1)

            points.append(p)

        return points

    def __get_category_brush(self, category):
        ncategories = len(self.model.categories)
        color = QtGui.QColor(0, 255-220*(ncategories-category)/(ncategories), 0)
        return QtGui.QBrush(QtGui.QColor(color))

    def __plot_profiles(self):
        bpt = self.model.bpt
        polygon_list = []
        below = self.__profile_get_points(self.worst)
        for i, ap in enumerate(bpt):
            below.reverse()
            above = self.__profile_get_points(ap)
            ppoints = below + above
            polygon = QtGui.QPolygonF(ppoints)
            polygon_list.append(polygon)
            brush = self.__get_category_brush(i)
            self.addPolygon(polygon, QtGui.QPen(), brush)
            below = above[:]

        i = len(bpt)-1
        above = self.__profile_get_points(self.best)
        below.reverse()
        ppoints = below + above
        polygon = QtGui.QPolygonF(ppoints)
        polygon_list.append(polygon)
        brush = self.__get_category_brush(i+1)
        self.addPolygon(polygon, QtGui.QPen(), brush)

        for i, p in enumerate(polygon_list):
            for j, q in enumerate(polygon_list):
                if j >= i:
                    continue

                u = p.intersected(q)
                if u == None:
                    continue

                brush = QtGui.QBrush()
                brush.setColor(QtGui.QColor("yellow"))
                brush.setStyle(QtCore.Qt.SolidPattern)
                self.addPolygon(u, QtGui.QPen(), brush)
