import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.dockWidgets.dockWidget  import DockWidget
 
class ManagementStyles(DockWidget):

    def __init__(self, controller):
        super(ManagementStyles, self).__init__(controller)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..', 'uis',
            "openManagement.ui"
        )

    def clearInput(self):
        pass
        
    def validInput(self):
        return  True

    def runFunction(self):
        self.controller.openManagementStyles()