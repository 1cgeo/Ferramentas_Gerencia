import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.sap.dockWidgets.dockWidget  import DockWidget
 
class  LoadLayersQgisProject(DockWidget):

    def __init__(self, sapCtrl):
        super(LoadLayersQgisProject, self).__init__(sapCtrl=sapCtrl)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis', 
            "loadLayersQgisProject.ui"
        )

    def clearInput(self):
        self.projectInProgressCkb.setChecked(False)

    def validInput(self):
        return  True

    def runFunction(self):
        self.sapCtrl.loadLayersQgisProject(
            self.projectInProgressCkb.isChecked()
        )