from __future__ import division
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
import random
import time
from itertools import combinations
from PyQt4 import QtCore
from PyQt4 import QtGui
from pymcda.generate import generate_random_avfsort_model
from pymcda.generate import generate_random_mrsort_model
from pymcda.generate import generate_random_profiles
from pymcda.generate import generate_alternatives
from pymcda.generate import generate_random_performance_table
from pymcda.generate import generate_criteria
from pymcda.pt_sorted import SortedPerformanceTable
from pymcda.types import CriteriaValues, CriterionValue
from pymcda.uta import AVFSort
from pymcda.learning.lp_avfsort import LpAVFSort
from pymcda.learning.meta_mrsort3 import MetaMRSortPop3
from pymcda.ui.graphic_uta import QGraphCriterionFunction
from pymcda.ui.graphic import QGraphicsSceneEtri
from pymcda.utils import compute_ca
from multiprocessing import Process, Pipe

# FIXME
from pymcda.types import AlternativePerformances

COMBO_AVFSORT = 0
COMBO_MRSORT = 1

def run_meta_mr(pipe, criteria, categories, worst, best, nmodels, niter,
                nmeta, pt, aa):
    pt_sorted = SortedPerformanceTable(pt)

    meta = MetaMRSortPop3(nmodels, criteria, categories, pt_sorted, aa)

    ca = meta.metas[0].meta.good / len(aa)
    pipe.send([meta.metas[0].model, ca])

    for i in range(1, niter + 1):
        model, ca = meta.optimize(nmeta)
        pipe.send([model, ca])
        if ca == 1:
            break

    pipe.close()

class qt_thread_mr(QtCore.QThread):

    def __init__(self, criteria, categories, worst, best, nmodels, niter,
                 nmeta, pt, aa, parent = None):
        super(qt_thread_mr, self).__init__(parent)
        self.mutex = QtCore.QMutex()
        self.criteria = criteria
        self.categories = categories
        self.worst = worst
        self.best = best
        self.nmodels = nmodels
        self.niter = niter
        self.nmeta = nmeta
        self.pt = pt
        self.aa = aa
        self.learned_model = None
        self.stopped = False
        self.results = list()
        self.fitness = list()

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
        pt_sorted = SortedPerformanceTable(self.pt)

        meta = MetaMRSortPop3(self.nmodels, self.criteria,
                              self.categories, pt_sorted,
                              self.aa)

        self.mutex.lock()
        self.results.append(meta.metas[0].model.copy())
        self.fitness.append(meta.metas[0].ca)
        self.mutex.unlock()
        self.emit(QtCore.SIGNAL('update(int)'), 0)

        for i in range(1, self.niter + 1):
            if self.is_stopped() is True:
                break

            model, ca = meta.optimize(self.nmeta)

            self.mutex.lock()
            self.results.append(model.copy())
            self.fitness.append(ca)
            self.mutex.unlock()

            self.emit(QtCore.SIGNAL('update(int)'), i)

            if ca == 1:
                break

def run_lp_avf(pipe, criteria, categories, worst, best, css, pt, aa):
    lp = LpAVFSort(criteria, css, categories, worst, best)
    obj, cvs, cfs, catv = lp.solve(aa, pt)

    model = AVFSort(criteria, cvs, cfs, catv)
    aa2 = model.get_assignments(pt)
    ca = compute_ca(aa, aa2)
    pipe.send([model, ca])

    pipe.close()

class qt_thread_avf(QtCore.QThread):

    def __init__(self, criteria, categories, worst, best, css, pt, aa,
                 parent = None):
        super(qt_thread_avf, self).__init__(parent)
        self.criteria = criteria
        self.categories = categories
        self.worst = worst
        self.best = best
        self.css = css
        self.pt = pt
        self.aa = aa
        self.learned_model = None

    def stop(self):
        self.parent_pipe.close()
        self.p.join()

    def run(self):
        self.parent_pipe, child_pipe = Pipe(False)
        self.p = Process(target = run_lp_avf,
                         args = (child_pipe, self.criteria,
                                 self.categories, self.worst, self.best,
                                 self.css, self.pt, self.aa))
        self.p.start()

        try:
            self.learned_model = self.parent_pipe.recv()
        except IOError:
            pass

        self.parent_pipe.close()
        self.p.join()

class _MyGraphicsview(QtGui.QGraphicsView):

    def __init__(self, parent = None):
        super(QtGui.QGraphicsView, self).__init__(parent)

    def resizeEvent(self, event):
        scene = self.scene()
        scene.update(self.size())
        self.resetCachedContent()

class qt_mainwindow(QtGui.QMainWindow):

    def __init__(self, parent = None):
        super(qt_mainwindow, self).__init__(parent)

        self.setup_ui()
        self.setup_connect()
        self.setup_shortcuts()

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
        self.left_top_layout.setContentsMargins(0, 0, 0, 0)
        self.scrollarea_original = QtGui.QScrollArea(self.groupbox_original)
        self.scrollarea_original.setWidgetResizable(True)
        self.widget_original = QtGui.QWidget()
        self.layout_original = QtGui.QGridLayout(self.widget_original)
        self.layout_original.setContentsMargins(0, 0, 0, 0)
        self.layout_original.setSpacing(0)
        self.scrollarea_original.setWidget(self.widget_original)
        self.left_top_layout.addWidget(self.scrollarea_original)
        self.leftlayout.addWidget(self.groupbox_original)

        self.groupbox_learned = QtGui.QGroupBox(self.centralwidget)
        self.groupbox_learned.setTitle("Learned model")
        self.left_bottom_layout = QtGui.QVBoxLayout(self.groupbox_learned)
        self.left_bottom_layout.setContentsMargins(0, 0, 0, 0)
        self.scrollarea_learned = QtGui.QScrollArea(self.groupbox_learned)
        self.scrollarea_learned.setWidgetResizable(True)
        self.widget_learned = QtGui.QWidget()
#        self.layout_learned = QtGui.QHBoxLayout(self.widget_learned)
        self.layout_learned = QtGui.QGridLayout(self.widget_learned)
        self.layout_learned.setContentsMargins(0, 0, 0, 0)
        self.layout_learned.setSpacing(0)
        self.scrollarea_learned.setWidget(self.widget_learned)
        self.left_bottom_layout.addWidget(self.scrollarea_learned)
        self.leftlayout.addWidget(self.groupbox_learned)

        # Model parameters
        self.groupbox_model_params = QtGui.QGroupBox(self.centralwidget)
        self.groupbox_model_params.setTitle("Model parameters")
        self.rightlayout.addWidget(self.groupbox_model_params)

        self.layout_model_params = QtGui.QVBoxLayout(self.groupbox_model_params)

        self.layout_seed = QtGui.QHBoxLayout()
        self.label_seed = QtGui.QLabel(self.groupbox_model_params)
        self.label_seed.setText("Seed")
        self.spinbox_seed = QtGui.QSpinBox(self.groupbox_model_params)
        self.spinbox_seed.setMinimum(0)
        self.spinbox_seed.setMaximum(1000000)
        self.spinbox_seed.setProperty("value", 123)
        self.layout_seed.addWidget(self.label_seed)
        self.layout_seed.addWidget(self.spinbox_seed)
        self.layout_model_params.addLayout(self.layout_seed)

        self.layout_criteria = QtGui.QHBoxLayout()
        self.label_criteria = QtGui.QLabel(self.groupbox_model_params)
        self.label_criteria.setText("Criteria")
        self.spinbox_criteria = QtGui.QSpinBox(self.groupbox_model_params)
        self.spinbox_criteria.setMinimum(2)
        self.spinbox_criteria.setMaximum(100)
        self.spinbox_criteria.setProperty("value", 8)
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

        # Original model
        self.groupbox_original_model = QtGui.QGroupBox(self.centralwidget)
        self.groupbox_original_model.setTitle("Original model")
        self.rightlayout.addWidget(self.groupbox_original_model)
        self.layout_original_model = QtGui.QVBoxLayout(self.groupbox_original_model)

        self.layout_type_ori = QtGui.QHBoxLayout()
        self.label_type_ori = QtGui.QLabel(self.groupbox_original_model)
        self.label_type_ori.setText("Type of model")
        self.combobox_type_ori = QtGui.QComboBox()
        self.combobox_type_ori.insertItems(0, ["AVF-Sort", "MR-Sort"])
        self.layout_type_ori.addWidget(self.label_type_ori)
        self.layout_type_ori.addWidget(self.combobox_type_ori)
        self.layout_original_model.addLayout(self.layout_type_ori)

        # Alternative parameters
        self.groupbox_alt_params = QtGui.QGroupBox(self.centralwidget)
        self.groupbox_alt_params.setTitle("Alternatives")
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

        # Learned model
        self.groupbox_meta_params = QtGui.QGroupBox(self.centralwidget)
        self.groupbox_meta_params.setTitle("Learned model")
        self.rightlayout.addWidget(self.groupbox_meta_params)
        self.layout_meta_params = QtGui.QVBoxLayout(self.groupbox_meta_params)

        self.layout_type = QtGui.QHBoxLayout()
        self.label_type = QtGui.QLabel(self.groupbox_meta_params)
        self.label_type.setText("Type of model")
        self.combobox_type = QtGui.QComboBox()
        self.combobox_type.insertItems(0, ["AVF-Sort", "MR-Sort"])
        self.layout_type.addWidget(self.label_type)
        self.layout_type.addWidget(self.combobox_type)
        self.layout_meta_params.addLayout(self.layout_type)

        # Initialization
        self.groupbox_init = QtGui.QGroupBox(self.centralwidget)
        self.groupbox_init.setTitle("Initialization")
        self.rightlayout.addWidget(self.groupbox_init)
        self.layout_init = QtGui.QVBoxLayout(self.groupbox_init)

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

        # Spacer
        self.spacer_item = QtGui.QSpacerItem(20, 20,
                                             QtGui.QSizePolicy.Minimum,
                                             QtGui.QSizePolicy.Expanding)
        self.rightlayout.addItem(self.spacer_item)

        self.gridlayout.addLayout(self.leftlayout, 0, 1, 1, 1)
        self.gridlayout.addLayout(self.rightlayout, 0, 2, 1, 1)
        self.setCentralWidget(self.centralwidget)

        # Update layout of original model parameters
        self.update_layout_model_avf_ori(self.layout_original_model)
        self.update_layout_model_avf(self.layout_meta_params)

    def setup_connect(self):
        QtCore.QObject.connect(self.button_generate,
                               QtCore.SIGNAL('clicked()'),
                               self.on_button_generate)
        QtCore.QObject.connect(self.button_run,
                               QtCore.SIGNAL('clicked()'),
                               self.on_button_run)
        QtCore.QObject.connect(self.combobox_type_ori,
                               QtCore.SIGNAL('currentIndexChanged(int)'),
                               self.on_combobox_type_ori_index_changed)
        QtCore.QObject.connect(self.combobox_type,
                               QtCore.SIGNAL('currentIndexChanged(int)'),
                               self.on_combobox_type_index_changed)

    def setup_shortcuts(self):
        action = QtGui.QAction('&Exit', self)
        action.setShortcut('Ctrl+W')
        action.setStatusTip('Exit application')
        action.triggered.connect(QtGui.qApp.quit)
        self.addAction(action)

    def resizeEvent(self, event):
        for i in range(self.layout_original.count()):
            item = self.layout_original.itemAt(i)
            gv = item.widget()
            scene = gv.scene()
            scene.update(gv.size())

        for i in range(self.layout_learned.count()):
            item = self.layout_learned.itemAt(i)
            gv = item.widget()
            scene = gv.scene()
            scene.update(gv.size())

    def clear_layout(self, layout):
        item = layout.takeAt(0)
        while item:
            layout.removeItem(item)
            widget = item.widget()
            widget.deleteLater()
            item = layout.takeAt(0)

    def delete_layout(self, layout):
        self.clear_layout(layout)
        del layout

    def update_layout_model_avf_ori(self, layout):
        while layout.itemAt(1):
            self.delete_layout(layout.takeAt(1))

        self.layout_nsegments_ori = QtGui.QHBoxLayout()
        self.label_nsegments_ori = QtGui.QLabel(self.groupbox_original_model)
        self.label_nsegments_ori.setText("Segments")
        self.spinbox_nsegments_ori = QtGui.QSpinBox(self.groupbox_original_model)
        self.spinbox_nsegments_ori.setMinimum(1)
        self.spinbox_nsegments_ori.setMaximum(10)
        self.spinbox_nsegments_ori.setProperty("value", 3)
        self.layout_nsegments_ori.addWidget(self.label_nsegments_ori)
        self.layout_nsegments_ori.addWidget(self.spinbox_nsegments_ori)
        layout.addLayout(self.layout_nsegments_ori)

    def update_layout_model_avf(self, layout):
        while layout.itemAt(1):
            self.delete_layout(layout.takeAt(1))

        self.layout_nsegments = QtGui.QHBoxLayout()
        self.label_nsegments = QtGui.QLabel(self.groupbox_meta_params)
        self.label_nsegments.setText("Segments")
        self.spinbox_nsegments = QtGui.QSpinBox(self.groupbox_meta_params)
        self.spinbox_nsegments.setMinimum(1)
        self.spinbox_nsegments.setMaximum(10)
        self.spinbox_nsegments.setProperty("value", 3)
        self.layout_nsegments.addWidget(self.label_nsegments)
        self.layout_nsegments.addWidget(self.spinbox_nsegments)
        layout.addLayout(self.layout_nsegments)

    def update_layout_model_mr_ori(self, layout):
        while layout.itemAt(1):
            self.delete_layout(layout.takeAt(1))

    def update_layout_model_mr(self, layout):
        while layout.itemAt(1):
            self.delete_layout(layout.takeAt(1))

        self.layout_nmodels = QtGui.QHBoxLayout()
        self.label_nmodels = QtGui.QLabel(self.groupbox_meta_params)
        self.label_nmodels.setText("Nb. models")
        self.spinbox_nmodels = QtGui.QSpinBox(self.groupbox_meta_params)
        self.spinbox_nmodels.setMinimum(1)
        self.spinbox_nmodels.setMaximum(1000000)
        self.spinbox_nmodels.setProperty("value", 10)
        self.layout_nmodels.addWidget(self.label_nmodels)
        self.layout_nmodels.addWidget(self.spinbox_nmodels)
        layout.addLayout(self.layout_nmodels)

        self.layout_niter = QtGui.QHBoxLayout()
        self.label_niter = QtGui.QLabel(self.groupbox_meta_params)
        self.label_niter.setText("Max iterations")
        self.spinbox_niter = QtGui.QSpinBox(self.groupbox_meta_params)
        self.spinbox_niter.setMinimum(1)
        self.spinbox_niter.setMaximum(1000000)
        self.spinbox_niter.setProperty("value", 30)
        self.layout_niter.addWidget(self.label_niter)
        self.layout_niter.addWidget(self.spinbox_niter)
        layout.addLayout(self.layout_niter)

        self.layout_nmeta = QtGui.QHBoxLayout()
        self.label_nmeta = QtGui.QLabel(self.groupbox_meta_params)
        self.label_nmeta.setText("Profiles it.")
        self.spinbox_nmeta = QtGui.QSpinBox(self.groupbox_meta_params)
        self.spinbox_nmeta.setMinimum(1)
        self.spinbox_nmeta.setMaximum(1000000)
        self.spinbox_nmeta.setProperty("value", 20)
        self.layout_nmeta.addWidget(self.label_nmeta)
        self.layout_nmeta.addWidget(self.spinbox_nmeta)
        layout.addLayout(self.layout_nmeta)

    def on_combobox_type_ori_index_changed(self, index):
        if index == COMBO_AVFSORT:
            self.update_layout_model_avf_ori(self.layout_original_model)
        else:
            self.update_layout_model_mr_ori(self.layout_original_model)

    def on_combobox_type_index_changed(self, index):
        if index == COMBO_AVFSORT:
            self.update_layout_model_avf(self.layout_meta_params)
        else:
            self.update_layout_model_mr(self.layout_meta_params)

    def on_button_generate(self):
        seed = self.spinbox_seed.value()
        random.seed(seed)

        # FIXME
        ncrit = self.spinbox_criteria.value()
        crit = generate_criteria(ncrit)
        self.worst = AlternativePerformances("worst",
                                    {c.id: 0 for c in crit})
        self.best = AlternativePerformances("best",
                                    {c.id: 1 for c in crit})

        if self.combobox_type_ori.currentIndex() == COMBO_AVFSORT:
            self.generate_avf_sort_model()
        else:
            self.generate_mr_sort_model()

        self.generate_assignments()

    def plot_mr_sort_model(self, model, layout):
        self.clear_layout(layout)
        gv = _MyGraphicsview()
        graph_model = QGraphicsSceneEtri(model,
                                         self.worst, self.best,
                                         gv.size())
        gv.setScene(graph_model)
        layout.addWidget(gv)

    def plot_avf_sort_model(self, model, layout):
        n_per_row = len(model.cfs) / 2
        i = 0
        self.clear_layout(layout)
        for cf in model.cfs:
            gv = _MyGraphicsview()
            scene = QGraphCriterionFunction(cf, QtCore.QSize(130, 130))
            gv.setScene(scene)
            gv.setMinimumSize(QtCore.QSize(130, 130))
            gv.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            gv.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            layout.addWidget(gv, i / n_per_row, i % n_per_row)
            i = i + 1

    def generate_mr_sort_model(self):
        ncrit = self.spinbox_criteria.value()
        ncat = self.spinbox_categories.value()

        self.model = generate_random_mrsort_model(ncrit, ncat,
                                                  worst = self.worst,
                                                  best = self.best)
        self.categories = self.model.categories_profiles.to_categories()
        self.plot_mr_sort_model(self.model, self.layout_original)

    def generate_avf_sort_model(self):
        ncrit = self.spinbox_criteria.value()
        ncat = self.spinbox_categories.value()
        nseg_min = self.spinbox_nsegments_ori.value()
        nseg_max = self.spinbox_nsegments_ori.value()

        self.model = generate_random_avfsort_model(ncrit, ncat, nseg_min,
                                                   nseg_max)
        self.model.set_equal_weights()
        self.categories = self.model.categories

        self.plot_avf_sort_model(self.model, self.layout_original)

    def generate_assignments(self):
        ncrit = len(self.model.criteria)
        ncat = len(self.model.categories)
        nalt = self.spinbox_nalt.value()

        self.a = generate_alternatives(nalt)
        self.pt = generate_random_performance_table(self.a,
                                                    self.model.criteria)
        self.aa = self.model.get_assignments(self.pt)

    def init_results_avf(self):
        while self.layout_result.itemAt(0):
            self.delete_layout(self.layout_result.takeAt(0))

        self.layout_time = QtGui.QHBoxLayout()
        self.label_time = QtGui.QLabel(self.groupbox_result)
        self.label_time.setText("Time:")
        self.label_time2 = QtGui.QLabel(self.groupbox_result)
        self.label_time2.setText("")
        self.layout_time.addWidget(self.label_time)
        self.layout_time.addWidget(self.label_time2)
        self.layout_result.addLayout(self.layout_time)

        self.layout_ca = QtGui.QHBoxLayout()
        self.label_ca = QtGui.QLabel(self.groupbox_result)
        self.label_ca.setText("CA:")
        self.label_ca2 = QtGui.QLabel(self.groupbox_result)
        self.label_ca2.setText("")
        self.layout_ca.addWidget(self.label_ca)
        self.layout_ca.addWidget(self.label_ca2)
        self.layout_result.addLayout(self.layout_ca)

    def init_results_mr(self):
        self.init_results_avf()

        self.layout_ca = QtGui.QHBoxLayout()
        self.layout_loop = QtGui.QHBoxLayout()
        self.label_loop = QtGui.QLabel(self.groupbox_model_params)
        self.label_loop.setText("Iteration:")
        self.spinbox_loop = QtGui.QSpinBox(self.groupbox_result)
        self.spinbox_loop.setMinimum(0)
        self.spinbox_loop.setMaximum(0)
        self.spinbox_loop.setProperty("value", 0)
        self.layout_loop.addWidget(self.label_loop)
        self.layout_loop.addWidget(self.spinbox_loop)
        self.layout_result.addLayout(self.layout_loop)

        QtCore.QObject.connect(self.spinbox_loop,
                               QtCore.SIGNAL('valueChanged(int)'),
                               self.on_spinbox_loop_value_changed)

    def on_spinbox_loop_value_changed(self, value):
        self.thread.mutex.lock()
        model = self.thread.results[value]
        fitness = self.thread.fitness[value]
        self.thread.mutex.unlock()

        self.plot_mr_sort_model(model, self.layout_learned)
        self.label_ca2.setText("%g" % fitness)

    def timeout(self):
        t = time.time() - self.start_time
        self.label_time2.setText("%.1f sec" % t)

    def update(self, i):
        self.spinbox_loop.setMaximum(i)
        self.spinbox_loop.setProperty("value", i)

        if i == 0:
            self.on_spinbox_loop_value_changed(0)

    def finished(self):
        self.timer.stop()
        self.timeout()

        self.button_run.setText("Start")
        self.started = False

        if self.thread.learned_model:
            model = self.thread.learned_model[0]
            ca = self.thread.learned_model[1]
            self.label_ca2.setText("%g" % ca)
            self.plot_avf_sort_model(model, self.layout_learned)

    def on_button_run(self):
        if hasattr(self, 'started') and self.started is True:
            self.thread.stop()
            return

        if not hasattr(self, 'model'):
            self.on_button_generate()

        if self.combobox_type.currentIndex() == COMBO_AVFSORT:
            self.init_results_avf()

            ns = self.spinbox_nsegments.value()
            css = CriteriaValues([])
            for c in self.model.criteria:
                cs = CriterionValue(c.id, ns)
                css.append(cs)

            self.thread = qt_thread_avf(self.model.criteria,
                                        self.categories,
                                        self.worst, self.best, css,
                                        self.pt, self.aa, None)

        else:
            self.init_results_mr()

            nmodels = self.spinbox_nmodels.value()
            niter = self.spinbox_niter.value()
            nmeta = self.spinbox_nmeta.value()
            self.thread = qt_thread_mr(self.model.criteria,
                                       self.categories,
                                       self.worst, self.best,
                                       nmodels, niter, nmeta,
                                       self.pt, self.aa, None)

            self.connect(self.thread, QtCore.SIGNAL("update(int)"),
                         self.update)

        self.connect(self.thread, QtCore.SIGNAL("finished()"),
                     self.finished)

        self.label_time2.setText("")
        self.start_time = time.time()
        self.timer.start(100)
        self.thread.start()

        self.button_run.setText("Stop")
        self.groupbox_result.setVisible(True)
        self.started = True

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("AVF Sort inference")

    font = QtGui.QFont("Sans Serif", 8)
    app.setFont(font)

    form = qt_mainwindow()
    form.show()

    app.exec_()
