# Facial Recognition Attendance GUI.
"""
Kindly use "Visual Studio Code" to run this GUI Desktop App as it will be easier to run as I am giving the requirements according to 
VSCode.
"pip install pyqt5" - use this command to install pyqt5.
"pip install pyqt5-tools" - use this command to install pyqt5 tools.
Use "Python 3.9" version in your PC or Desktop, as pyqt5 may give error while you are installing pyqt5-tools in your command prompt or in 
VSCode terminal for Python 3.10 and above versions.
"""
import sys
from PyQt5.uic import loadUi 
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog
import resource
from out_window import Ui_OutputDialog

#UI File loading
class Ui_Dialog(QDialog): # A QDialog widget presents a top level window mostly used to collect response from the user.
    def __init__(self): # Creating Object
        super(Ui_Dialog, self).__init__() # the self variable represents the instance of the object itself
        loadUi("mainwindow.ui", self) # load QTUI file
        self.runButton.clicked.connect(self.runSlot)
        self._new_window = None
        self.Videocapture_ = None

    # Camera call
    def refreshAll(self):
        # Set the text of line Edit once it's valid
        self.Videocapture_ = "0" # 0 - Built in camera, 1 by USB External camera

    @pyqtSlot()
    def runSlot(self):
        # Called when the user presses the Run button
        print("Clicked Run")
        self.refreshAll()
        print(self.Videocapture_)
        ui.hide()  # hide the main window
        self.outputWindow_()  # Create and open new output window

    def outputWindow_(self):
        # Created new window for vidual output of the video in GUI
        self._new_window = Ui_OutputDialog()
        self._new_window.show()
        self._new_window.startVideo(self.Videocapture_)
        print("Video Played")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = Ui_Dialog()
    ui.show()
    sys.exit(app.exec_())