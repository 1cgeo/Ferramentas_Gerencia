import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.dockWidgets.dockWidget  import DockWidget
 
class  LoadLayersQgisProject(DockWidget):

    def __init__(self, controller):
        super(LoadLayersQgisProject, self).__init__(controller)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..', 'uis',
            "loadLayersQgisProject.ui"
        )

    def clearInput(self):
        self.projectInProgressCkb.setChecked(False)

    def validInput(self):
        return  True

    def runFunction(self):
        self.controller.loadLayersQgisProject(
            self.projectInProgressCkb.isChecked()
        )