import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.dockWidgets.dockWidgetAutoComplete  import DockWidgetAutoComplete
 
class SetPriorityActivity(DockWidgetAutoComplete):

    def __init__(self, users, controller):
        super(SetPriorityActivity, self).__init__(controller)
        self.users = users
        self.usersCb.addItems(sorted([ user['nome'] for user in self.users]))

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..', 'uis',
            "setPriorityActivity.ui"
        )

    def clearInput(self):
        self.activityIdLe.setText('')
        self.priorityLe.setText('')

    def validInput(self):
        return  self.activityIdLe.text() and self.priorityLe.text() and self.getUserId()

    def getPritority(self):
        return int(self.priorityLe.text())

    def getUserId(self):
        for user in self.users:
            if user['nome'] == self.usersCb.currentText():
                return user['id']

    def getActivitiesIds(self):
        return [ int(d) for d in self.activityIdLe.text().split(',') if d ]

    def runFunction(self):
        self.controller.setSapPriorityActivity(
            self.getActivitiesIds(),
            self.getPritority(),
            self.getUserId()
        )
    
    def autoCompleteInput(self):
        values = self.controller.getValuesFromLayer('setPriorityActivity', 'activity')
        self.activityIdLe.setText(values)