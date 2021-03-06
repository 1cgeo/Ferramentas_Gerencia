import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.dockWidgets.dockWidget  import DockWidget
 
class ClearUserActivities(DockWidget):

    def __init__(self, users, controller):
        super(ClearUserActivities, self).__init__(controller)
        self.users = users
        self.usersCb.addItems(sorted([ user['nome'] for user in self.users]))

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..', 'uis',
            "clearUserActivities.ui"
        )

    def clearInput(self):
        pass

    def validInput(self):
        return  self.getUserId()

    def getUserId(self):
        for user in self.users:
            if user['nome'] == self.usersCb.currentText():
                return user['id']
        return False

    def runFunction(self):
        self.controller.deleteSapUserActivities(
            self.getUserId()
        )