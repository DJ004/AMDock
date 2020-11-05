#!/bin/python
import sys
from checker import Checker
from file_loader import *
from info_tab import Help
from input_tab import Program_body
from lobby_tab import Lobby
from output_file import OutputFile
from result_tab import Results
from setting_tab import Configuration_tab
from variables import Variables
from log_window import LogWindow
from PyQt4 import QtGui, QtCore
from tools import (PROJECT, BASE)
from warning import internal_error

class EmittingStream(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))

class AMDock(QtGui.QMainWindow, Variables):
    def __init__(self):
        super(AMDock, self).__init__()
        QtGui.QMainWindow.__init__(self)
        Variables.__init__(self)

        # redirect stderr to log window
        sys.stderr = EmittingStream(textWritten=self.normalOutputWritten)

        self.checker = Checker(self)
        self.output2file = OutputFile(self)
        self.loader = Loader(self)
        self.project = PROJECT()
        self.target = BASE()
        self.offtarget = BASE()
        self.ligand = BASE()
        self.log_thread = QtCore.QThreadPool()
        self.numeric_version = [1, 5, 2]
        self.version = "{}.{}.{} For Windows and Linux".format(*self.numeric_version)
        self.spacing_autoligand = 1.0
        self.spacing_autodock = 0.375
        self.pH = 7.40
        self.para_file = None
        self.state = 0  # 0 not running, 2 running
        self.section = -1  # -1 only PD selected, 0 project, 1 input files, 2 bsd, 3 docking

        with open(self.style_file) as f:
            self.setStyleSheet(f.read())

        self.icon = QtGui.QIcon()
        self.icon.addPixmap(QtGui.QPixmap(self.home_icon), QtGui.QIcon.Active, QtGui.QIcon.Off)
        self.icon.addPixmap(QtGui.QPixmap(self.home_icon), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.icon.addPixmap(QtGui.QPixmap(self.home_icon), QtGui.QIcon.Selected, QtGui.QIcon.Off)
        self.icon.addPixmap(QtGui.QPixmap(self.home_icon), QtGui.QIcon.Disabled, QtGui.QIcon.Off)
        self.icon.addPixmap(QtGui.QPixmap(self.home_icon_white), QtGui.QIcon.Selected, QtGui.QIcon.On)
        self.icon.addPixmap(QtGui.QPixmap(self.home_icon_white), QtGui.QIcon.Active, QtGui.QIcon.On)

        ##--TABS
        self.main_window = QtGui.QTabWidget(self)
        self.setCentralWidget(self.main_window)

        ##--Tabs for Docking Options
        self.lobby = Lobby(self)
        self.main_window.addTab(self.lobby, self.icon, "")
        self.program_body = Program_body(self)
        self.main_window.addTab(self.program_body, "Docking Options")
        self.main_window.setTabEnabled(1, False)

        ##Tabs for result analysis
        self.result_tab = Results(self)
        self.main_window.addTab(self.result_tab, "Results Analysis")
        self.main_window.setTabEnabled(2, False)

        # **Configurations_Tab
        self.configuration_tab = Configuration_tab(self)
        self.main_window.addTab(self.configuration_tab, "Configuration")

        # ** Help_Tab
        self.help_tab = Help(self)
        self.main_window.addTab(self.help_tab, "Info")

        # ** log dockwidget
        self.log_widget = LogWindow(self)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.log_widget)
        if self.configuration_tab.log_view.isChecked():
            self.log_widget.show()
        else:
            self.log_widget.hide()

        self.statusbar = QtGui.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        QtCore.QMetaObject.connectSlotsByName(self)
        self.version_label = QtGui.QLabel("Version: %s" % self.version)
        self.statusbar.addPermanentWidget(self.version_label)

    def __del__(self):
        # Restore sys.stdout
        sys.stdout = sys.__stdout__

    def normalOutputWritten(self, text):
        """Append text to the QTextEdit."""
        # Maybe QTextEdit.append() works as well, but this is how I do it:
        # internal_error(self, text)
        print(text)
        self.log_widget.textedit.append(Ft(text).error())
        # cursor = self.log_widget.textedit.textCursor()
        # cursor.movePosition(QtGui.QTextCursor.End)
        # cursor.insertText(text)
        # self.log_widget.textedit.setTextCursor(cursor)
        # self.log_widget.textedit.ensureCursorVisible()

    def closeEvent(self, event):
        if self.state:
            reply = QtGui.QMessageBox.question(self, 'Message', "There are processes in the background. Are you sure "
                                                                "to quit?", QtGui.QMessageBox.Yes,
                                               QtGui.QMessageBox.No)
        else:
            reply = QtGui.QMessageBox.question(self, 'Message', "Are you sure to quit?", QtGui.QMessageBox.Yes,
                                           QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            #  ensures that nothing is left in the background
            try:
                self.program_body.W.force_finished()
            except:
                pass
            try:
                self.program_body.b_pymol.force_finished()
            except:
                pass
            try:
                self.result_tab.pymol.force_finished()
            except:
                pass
            event.accept()
        else:
            event.ignore()

from splash_screen import SplashScreen
# from variables import Objects as ob

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    app_icon = QtGui.QIcon()
    v = Variables()
    # dw = QtGui.QDesktopWidget()
    app_icon.addFile(v.app_icon, QtCore.QSize(16, 20))
    app_icon.addFile(v.app_icon, QtCore.QSize(24, 30))
    app_icon.addFile(v.app_icon, QtCore.QSize(32, 40))
    app_icon.addFile(v.app_icon, QtCore.QSize(48, 60))
    app_icon.addFile(v.app_icon, QtCore.QSize(223, 283))
    # app.setStyle("cleanlooks")
    app.setWindowIcon(app_icon)
    app.setApplicationName('AMDock: Assisted Molecular Docking for AutoDock and AutoDock Vina')
    splash = SplashScreen(QtGui.QPixmap(v.splashscreen_path), app)
    main = AMDock()
    splash.finish(main)
    main.setWindowState(QtCore.Qt.WindowMaximized)
    # main.setMinimumSize(1080, 740)
    # main.resize(1200, int(dw.height() * 0.9))
    main.setWindowTitle('AMDock: Assisted Molecular Docking with AutoDock4 and AutoDock Vina')
    main.setWindowIcon(app_icon)
    main.show()
    if splash.import_error():
        sys.exit(app.exec_())
    else:
        sys.exit(app.exit(1))
