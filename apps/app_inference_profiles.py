from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
import random
import time
from itertools import combinations
from PyQt4 import QtCore
from PyQt4 import QtGui
from pymcda.generate import generate_random_electre_tri_bm_model
from pymcda.generate import generate_random_profiles
from pymcda.generate import generate_alternatives
from pymcda.generate import generate_random_performance_table
from pymcda.generate import generate_criteria
from pymcda.pt_sorted import SortedPerformanceTable
from pymcda.utils import compute_ca
from pymcda.learning.meta_etri_profiles3 import meta_etri_profiles3
from pymcda.learning.meta_etri_profiles4 import meta_etri_profiles4
from pymcda.ui.graphic import QGraphicsScene_etri
from multiprocessing import Process, Pipe

# FIXME
from pymcda.types import AlternativePerformances

def run_metaheuristic(pipe, model, pt, aa, algo, n, worst = None,
                      best = None):

    model.bpt = generate_random_profiles(model.profiles,
                                         model.criteria,
                                         worst = worst,
                                         best = best)

    pt_sorted = SortedPerformanceTable(pt)

    if algo == "Meta 3":
        meta = meta_etri_profiles3(model, pt_sorted, aa)
    elif algo == "Meta 4":
        meta = meta_etri_profiles4(model, pt_sorted, aa)
    else:
        print("Invalid algorithm %s" % algo)
        pipe.close()
        return

    f = compute_ca(aa, meta.aa)

    pipe.send([model.copy(), f])

    for i in range(1, n + 1):
        meta.optimize()
        f = compute_ca(aa, meta.aa)

        pipe.send([model.copy(), f])

        if f == 1:
            break

    pipe.close()

class qt_thread_algo(QtCore.QThread):

    def __init__(self, n, model, pt, aa, algo, worst = None, best = None,
                 parent = None):
        super(qt_thread_algo, self).__init__(parent)
        self.mutex = QtCore.QMutex()
        self.stopped = False
        self.results = []
        self.fitness = []
        self.model = model.copy()
        self.n = n
        self.ncrit = len(model.criteria)
        self.ncat = len(model.categories)
        self.pt = pt
        self.aa = aa
        self.worst = worst
        self.best = best
        self.algo = algo

    def stop(self):
        try:
            self.mutex.lock()
            self.stopped = True
        finally:
            self.mutex.unlock()

    def is_stopped(self):
        try:
            self.mutex.lock()
            return self.stopped
        finally:
            self.mutex.unlock()

    def run(self):
        parent_pipe, child_pipe = Pipe(False)
        p = Process(target = run_metaheuristic,
                    args = (child_pipe, self.model, self.pt, self.aa,
                            self.algo, self.n, self.worst, self.best))
        p.start()

        for i in range(self.n + 1):
            if self.is_stopped() is True:
                parent_pipe.close()
                p.terminate()
                return

            try:
                result = parent_pipe.recv()
            except:
                break

            self.results.append(result[0])
            self.fitness.append(result[1])
            self.emit(QtCore.SIGNAL('update(int)'), i)

        parent_pipe.close()
        p.join()

class qt_mainwindow(QtGui.QMainWindow):

    def __init__(self, parent = None):
        super(qt_mainwindow, self).__init__(parent)

        self.setup_ui()
        self.setup_connect()

        self.timer = QtCore.QTimer()
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"),
                               self.timeout)

    def setup_ui(self):
        self.resize(800, 600)
        self.centralwidget = QtGui.QWidget()
        self.gridlayout = QtGui.QGridLayout(self.centralwidget)

        self.leftlayout = QtGui.QVBoxLayout()
        self.rightlayout = QtGui.QVBoxLayout()

        # Left layout
        self.groupbox_original = QtGui.QGroupBox(self.centralwidget)
        self.groupbox_original.setTitle("Original model")
        self.left_top_layout = QtGui.QVBoxLayout(self.groupbox_original)
        self.graphicv_original = QtGui.QGraphicsView(self.groupbox_original)
        self.left_top_layout.addWidget(self.graphicv_original)
        self.leftlayout.addWidget(self.groupbox_original)

        self.groupbox_learned = QtGui.QGroupBox(self.centralwidget)
        self.groupbox_learned.setTitle("Learned model")
        self.left_bottom_layout = QtGui.QVBoxLayout(self.groupbox_learned)
        self.graphicv_learned = QtGui.QGraphicsView(self.groupbox_learned)
        self.left_bottom_layout.addWidget(self.graphicv_learned)
        self.leftlayout.addWidget(self.groupbox_learned)

        # Model parameters
        self.groupbox_model_params = QtGui.QGroupBox(self.centralwidget)
        self.groupbox_model_params.setTitle("Model parameters")
        self.rightlayout.addWidget(self.groupbox_model_params)

        self.layout_model_params = QtGui.QVBoxLayout(self.groupbox_model_params)

        self.layout_criteria = QtGui.QHBoxLayout()
        self.label_criteria = QtGui.QLabel(self.groupbox_model_params)
        self.label_criteria.setText("Criteria")
        self.spinbox_criteria = QtGui.QSpinBox(self.groupbox_model_params)
        self.spinbox_criteria.setMinimum(2)
        self.spinbox_criteria.setMaximum(100)
        self.spinbox_criteria.setProperty("value", 7)
        self.layout_criteria.addWidget(self.label_criteria)
        self.layout_criteria.addWidget(self.spinbox_criteria)
        self.layout_model_params.addLayout(self.layout_criteria)

        self.layout_categories = QtGui.QHBoxLayout()
        self.label_categories = QtGui.QLabel(self.groupbox_model_params)
        self.label_categories.setText("Categories")
        self.spinbox_categories = QtGui.QSpinBox(self.groupbox_model_params)
        self.spinbox_categories.setMinimum(2)
        self.spinbox_categories.setMaximum(10)
        self.spinbox_categories.setProperty("value", 3)
        self.layout_categories.addWidget(self.label_categories)
        self.layout_categories.addWidget(self.spinbox_categories)
        self.layout_model_params.addLayout(self.layout_categories)

        # Alternative parameters
        self.groupbox_alt_params = QtGui.QGroupBox(self.centralwidget)
        self.groupbox_alt_params.setTitle("Alternative parameters")
        self.rightlayout.addWidget(self.groupbox_alt_params)
        self.layout_alt_params = QtGui.QVBoxLayout(self.groupbox_alt_params)

        self.layout_nalt = QtGui.QHBoxLayout()
        self.label_nalt = QtGui.QLabel(self.groupbox_alt_params)
        self.label_nalt.setText("Alternatives")
        self.spinbox_nalt = QtGui.QSpinBox(self.groupbox_alt_params)
        self.spinbox_nalt.setMinimum(1)
        self.spinbox_nalt.setMaximum(1000000)
        self.spinbox_nalt.setProperty("value", 1000)
        self.layout_nalt.addWidget(self.label_nalt)
        self.layout_nalt.addWidget(self.spinbox_nalt)
        self.layout_alt_params.addLayout(self.layout_nalt)

        # Metaheuristic parameters
        self.groupbox_meta_params = QtGui.QGroupBox(self.centralwidget)
        self.groupbox_meta_params.setTitle("Parameters")
        self.rightlayout.addWidget(self.groupbox_meta_params)
        self.layout_meta_params = QtGui.QVBoxLayout(self.groupbox_meta_params)

        self.layout_algo = QtGui.QHBoxLayout()
        self.label_algo = QtGui.QLabel(self.groupbox_meta_params)
        self.label_algo.setText("Strategy")
        self.combobox_algo = QtGui.QComboBox(self.groupbox_meta_params)
        self.combobox_algo.addItem("Meta 3")
        self.combobox_algo.addItem("Meta 4")
        self.combobox_algo.setCurrentIndex(1)
        self.layout_algo.addWidget(self.label_algo)
        self.layout_algo.addWidget(self.combobox_algo)
        self.layout_meta_params.addLayout(self.layout_algo)

        self.layout_seed = QtGui.QHBoxLayout()
        self.label_seed = QtGui.QLabel(self.groupbox_meta_params)
        self.label_seed.setText("Seed")
        self.spinbox_seed = QtGui.QSpinBox(self.groupbox_meta_params)
        self.spinbox_seed.setMinimum(0)
        self.spinbox_seed.setMaximum(1000000)
        self.spinbox_seed.setProperty("value", 123)
        self.layout_seed.addWidget(self.label_seed)
        self.layout_seed.addWidget(self.spinbox_seed)
        self.layout_meta_params.addLayout(self.layout_seed)

        self.layout_nloop = QtGui.QHBoxLayout()
        self.label_nloop = QtGui.QLabel(self.groupbox_meta_params)
        self.label_nloop.setText("Loops")
        self.spinbox_nloop = QtGui.QSpinBox(self.groupbox_meta_params)
        self.spinbox_nloop.setMinimum(1)
        self.spinbox_nloop.setMaximum(1000000)
        self.spinbox_nloop.setProperty("value", 500)
        self.layout_nloop.addWidget(self.label_nloop)
        self.layout_nloop.addWidget(self.spinbox_nloop)
        self.layout_meta_params.addLayout(self.layout_nloop)

        # Initialization
        self.groupbox_init = QtGui.QGroupBox(self.centralwidget)
        self.groupbox_init.setTitle("Initialization")
        self.rightlayout.addWidget(self.groupbox_init)
        self.layout_init = QtGui.QVBoxLayout(self.groupbox_init)

        self.button_seed = QtGui.QPushButton(self.centralwidget)
        self.button_seed.setText("Reset seed")
        self.layout_init.addWidget(self.button_seed)

        self.button_generate = QtGui.QPushButton(self.centralwidget)
        self.button_generate.setText("Generate model and\n performance table")
        self.layout_init.addWidget(self.button_generate)

        # Algorithm
        self.groupbox_algo = QtGui.QGroupBox(self.centralwidget)
        self.groupbox_algo.setTitle("Algorithm")
        self.rightlayout.addWidget(self.groupbox_algo)
        self.layout_algo = QtGui.QVBoxLayout(self.groupbox_algo)

        self.button_run = QtGui.QPushButton(self.centralwidget)
        self.button_run.setText("Start")
        self.layout_algo.addWidget(self.button_run)

        # Result
        self.groupbox_result = QtGui.QGroupBox(self.centralwidget)
        self.groupbox_result.setTitle("Result")
        self.groupbox_result.setVisible(False)
        self.rightlayout.addWidget(self.groupbox_result)
        self.layout_result = QtGui.QVBoxLayout(self.groupbox_result)

        self.layout_time = QtGui.QHBoxLayout()
        self.label_time = QtGui.QLabel(self.groupbox_result)
        self.label_time.setText("Time:")
        self.label_time2 = QtGui.QLabel(self.groupbox_result)
        self.label_time2.setText("")
        self.layout_time.addWidget(self.label_time)
        self.layout_time.addWidget(self.label_time2)
        self.layout_result.addLayout(self.layout_time)

        self.layout_tloop = QtGui.QHBoxLayout()
        self.label_tloop = QtGui.QLabel(self.groupbox_result)
        self.label_tloop.setText("Total loop:")
        self.label_tloop2 = QtGui.QLabel(self.groupbox_result)
        self.label_tloop2.setText("")
        self.layout_tloop.addWidget(self.label_tloop)
        self.layout_tloop.addWidget(self.label_tloop2)
        self.layout_result.addLayout(self.layout_tloop)

        self.layout_ca = QtGui.QHBoxLayout()
        self.label_ca = QtGui.QLabel(self.groupbox_result)
        self.label_ca.setText("CA:")
        self.label_ca2 = QtGui.QLabel(self.groupbox_result)
        self.label_ca2.setText("")
        self.layout_ca.addWidget(self.label_ca)
        self.layout_ca.addWidget(self.label_ca2)
        self.layout_result.addLayout(self.layout_ca)

        self.layout_loop = QtGui.QHBoxLayout()
        self.label_loop = QtGui.QLabel(self.groupbox_model_params)
        self.label_loop.setText("Loop")
        self.spinbox_loop = QtGui.QSpinBox(self.groupbox_result)
        self.spinbox_loop.setMinimum(0)
        self.spinbox_loop.setMaximum(0)
        self.spinbox_loop.setProperty("value", 0)
        self.layout_loop.addWidget(self.label_loop)
        self.layout_loop.addWidget(self.spinbox_loop)
        self.layout_result.addLayout(self.layout_loop)

        # Spacer
        self.spacer_item = QtGui.QSpacerItem(20, 20,
                                             QtGui.QSizePolicy.Minimum,
                                             QtGui.QSizePolicy.Expanding)
        self.rightlayout.addItem(self.spacer_item)

        self.gridlayout.addLayout(self.leftlayout, 0, 1, 1, 1)
        self.gridlayout.addLayout(self.rightlayout, 0, 2, 1, 1)
        self.setCentralWidget(self.centralwidget)

    def setup_connect(self):
        QtCore.QObject.connect(self.button_seed,
                               QtCore.SIGNAL('clicked()'),
                               self.on_button_seed)
        QtCore.QObject.connect(self.button_generate,
                               QtCore.SIGNAL('clicked()'),
                               self.on_button_generate)
        QtCore.QObject.connect(self.button_run,
                               QtCore.SIGNAL('clicked()'),
                               self.on_button_run)
        QtCore.QObject.connect(self.spinbox_loop,
                               QtCore.SIGNAL('valueChanged(int)'),
                               self.on_spinbox_loop_value_changed)

    def resizeEvent(self, event):
        scene = self.graphicv_original.scene()
        if scene:
            scene.update(self.graphicv_original.size())
            self.graphicv_original.resetCachedContent()

        scene = self.graphicv_learned.scene()
        if scene:
            scene.update(self.graphicv_learned.size())
            self.graphicv_original.resetCachedContent()

    def on_button_seed(self):
        seed = self.spinbox_seed.value()
        random.seed(seed)

    def on_button_generate(self):
        self.generate_model()
        self.generate_alt()

    def generate_model(self):
        ncrit = self.spinbox_criteria.value()
        ncat = self.spinbox_categories.value()

        # FIXME
        crit = generate_criteria(ncrit)
        self.worst = AlternativePerformances("worst",
                                    {c.id: 0 for c in crit})
        self.best = AlternativePerformances("best",
                                    {c.id: 10 for c in crit})

        self.model = generate_random_electre_tri_bm_model(ncrit, ncat,
                                    worst = self.worst, best = self.best)

        self.graph_model = QGraphicsScene_etri(self.model,
                                              self.worst, self.best,
                                              self.graphicv_original.size())
        self.graphicv_original.setScene(self.graph_model)

    def generate_alt(self):
        ncrit = len(self.model.criteria)
        ncat = len(self.model.categories)
        nalt = self.spinbox_nalt.value()

        self.a = generate_alternatives(nalt)
        self.pt = generate_random_performance_table(self.a,
                                                    self.model.criteria,
                                                    worst = self.worst,
                                                    best = self.best)
        self.aa = self.model.pessimist(self.pt)


    def on_spinbox_loop_value_changed(self, value):
        model = self.thread.results[value]
        self.model2.bpt = model.bpt
        self.graph_model2.update_profiles()
        self.graph_model2.update_categories()

        fitness = self.thread.fitness[value]
        self.label_ca2.setText("%g" % fitness)

    def timeout(self):
        t = time.time() - self.start_time
        self.label_time2.setText("%.1f sec" % t)

    def update(self, i):
        model = self.thread.results[i]

        if i == 0:
            self.groupbox_result.setVisible(True)

            self.model2 = model.copy()
            self.graph_model2 = QGraphicsScene_etri(self.model2,
                                               self.worst, self.best,
                                               self.graphicv_learned.size())
            self.graphicv_learned.setScene(self.graph_model2)

        self.label_tloop2.setText("%d" % i)
        self.spinbox_loop.setMaximum(i)
        self.spinbox_loop.setProperty("value", i)

    def finished(self):
        self.timer.stop()
        self.timeout()

        self.button_run.setText("Start")
        self.started = False
        self.spinbox_loop.setEnabled(True)

    def on_button_run(self):
        if hasattr(self, 'started') and self.started is True:
            self.thread.stop()
            return

        if not hasattr(self, 'model'):
            self.on_button_generate()

        self.spinbox_loop.setEnabled(False)
        self.label_tloop2.setText("0")
        self.spinbox_loop.setMaximum(0)
        self.spinbox_loop.setProperty("value", 0)
        self.label_time2.setText("")

        nloop = self.spinbox_nloop.value()
        algo = self.combobox_algo.currentText()

        self.thread = qt_thread_algo(nloop, self.model, self.pt, self.aa,
                                     algo, self.worst, self.best, None)
        self.connect(self.thread, QtCore.SIGNAL("update(int)"),
                     self.update)
        self.connect(self.thread, QtCore.SIGNAL("finished()"),
                     self.finished)

        self.start_time = time.time()
        self.timer.start(100)
        self.thread.start()


        self.button_run.setText("Stop")
        self.started = True

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("ELECTRE TRI profile inference")

    font = QtGui.QFont("Sans Serif", 8)
    app.setFont(font)

    form = qt_mainwindow()
    form.show()

    app.exec_()
