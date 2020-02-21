# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Forms\test_async.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!
import time
import traceback

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, QObject, QRunnable, pyqtSlot, QThreadPool


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        `tuple` (exctype, value, traceback.format_exc() )

    result
        `object` data returned from processing, anything

    progress
        `int` indicating % progress

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    # progress = pyqtSignal(int)
    progress = pyqtSignal(object)

class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done



class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(702, 437)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.txt_debug = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.txt_debug.setGeometry(QtCore.QRect(10, 160, 681, 231))
        self.txt_debug.setObjectName("txt_debug")
        self.test_worker_btn = QtWidgets.QPushButton(self.centralwidget)
        self.test_worker_btn.setGeometry(QtCore.QRect(294, 60, 121, 31))
        self.test_worker_btn.setObjectName("test_worker_btn")
        self.stop_test_btn = QtWidgets.QPushButton(self.centralwidget)
        self.stop_test_btn.setGeometry(QtCore.QRect(290, 100, 131, 31))
        self.stop_test_btn.setObjectName("stop_test_btn")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 702, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.test_worker_btn.setText(_translate("MainWindow", "test worker Thread"))
        self.stop_test_btn.setText(_translate("MainWindow", "Stop Test"))
        self.customUI(MainWindow)

    def customUI(self,MainWindow):
        self.mw = MainWindow
        self.working = False
        self.threadpool = QThreadPool()
        self.test_worker_btn.clicked.connect(lambda : self.test_click())
        self.stop_test_btn.clicked.connect(lambda : self.test_stop_click())

    def test_click(self):
        # self.txt_debug.appendPlainText("test worker")
        self.working = True
        worker = Worker(self.execute_this_fn)  # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)

        # Execute
        self.threadpool.start(worker)


    def progress_fn(self, n):
        # print("%d%% done" % n)
        self.txt_debug.appendPlainText(n)

    def test_stop_click(self):
        self.working = False


    def execute_this_fn(self,progress_callback):
        while self.working:
            time.sleep(1)
            progress_callback.emit("test_worker")
            #print("test_worker")
            # self.txt_debug.appendPlainText("test worker")
        return "Done."

    def print_output(self, s):
        print(s)

    def thread_complete(self):
        self.txt_debug.appendPlainText("THREAD COMPLETE!")


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

