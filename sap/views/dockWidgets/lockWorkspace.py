import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.sap.views.dockWidgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
 
class LockWorkspace(DockWidgetAutoComplete):

    def __init__(self, sapCtrl):
        super(LockWorkspace, self).__init__(sapCtrl=sapCtrl)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'uis', 
            "lockWorkspace.ui"
        )

    def validInput(self):
        return  self.workspaces_ids_le.text()

    def getWorkspacesIds(self):
        return [ int(d) for d in self.workspaces_ids_le.text().split(',') ]

    def runFunction(self):
        self.sapCtrl.lockWorkspace(
            self.getWorkspacesIds()
        )
    
    def autoCompleteInput(self):
        values = self.sapCtrl.getValuesFromLayer('lockWorkspace', 'workUnit')
        self.workspaces_ids_le.setText(values)