from PyQt5.QtCore import QObject
from Ferramentas_Gerencia.interfaces.IManagementToolCtrl import IManagementToolCtrl

from Ferramentas_Gerencia.factories.functionsSettingsSingleton import FunctionsSettingsSingleton
from Ferramentas_Gerencia.factories.managementDockBuilder import ManagementDockBuilder
from Ferramentas_Gerencia.factories.dockDirector import DockDirector
from Ferramentas_Gerencia.factories.managementStylesSingleton  import ManagementStylesSingleton
from Ferramentas_Gerencia.factories.managementModelsSingleton  import ManagementModelsSingleton
from Ferramentas_Gerencia.factories.managementFmeServersSingleton  import ManagementFmeServersSingleton
from Ferramentas_Gerencia.factories.managementFmeProfilesSingleton  import ManagementFmeProfilesSingleton
from Ferramentas_Gerencia.factories.managementRulesSingleton  import ManagementRulesSingleton
from Ferramentas_Gerencia.factories.managementRuleSetSingleton  import ManagementRuleSetSingleton
from Ferramentas_Gerencia.factories.managementUsersPrivilegesSingleton  import ManagementUsersPrivilegesSingleton
from Ferramentas_Gerencia.factories.managementEditLayersSingleton  import ManagementEditLayersSingleton
from Ferramentas_Gerencia.factories.managementImportLayersSingleton  import ManagementImportLayersSingleton
from Ferramentas_Gerencia.factories.addStyleFormSingleton  import AddStyleFormSingleton
from Ferramentas_Gerencia.factories.addModelFormSingleton  import AddModelFormSingleton
from Ferramentas_Gerencia.factories.addRuleFormSingleton  import AddRuleFormSingleton
from Ferramentas_Gerencia.factories.addRuleSetFormSingleton  import AddRuleSetFormSingleton
from Ferramentas_Gerencia.factories.addRulesCsvFormSingleton  import AddRulesCsvFormSingleton
from Ferramentas_Gerencia.factories.addFmeServerFormSingleton  import AddFmeServerFormSingleton
from Ferramentas_Gerencia.factories.addFmeProfileFormSingleton  import AddFmeProfileFormSingleton
from Ferramentas_Gerencia.factories.rulesSingleton  import RulesSingleton

from Ferramentas_Gerencia.modules.databases.factories.databasesFactory  import DatabasesFactory
from Ferramentas_Gerencia.modules.utils.factories.utilsFactory import UtilsFactory

import os
import re

class ManagementToolCtrl(QObject, IManagementToolCtrl):

    def __init__(self, 
            qgis, 
            fmeCtrl, 
            sapCtrl,
            databasesFactory=DatabasesFactory(),
            functionsSettings=FunctionsSettingsSingleton.getInstance(),
            messageFactory=UtilsFactory().createMessageFactory()
        ):
        super(ManagementToolCtrl, self).__init__()
        self.qgis = qgis
        self.fmeCtrl = fmeCtrl
        teste = IManagementToolCtrl()
        self.databasesFactory = databasesFactory
        self.messageFactory = messageFactory
        self.functionsSettings = functionsSettings
        self.sapCtrl = sapCtrl
        self.dockSap = None
        self.menuBarActions = []
        self.createActionsMenuBar()
        self.createMenuBar() 

    def showErrorMessageBox(self, parent, title, message):
        parent = self.qgis.getMainWindow() if not parent else parent
        errorMessageBox = self.messageFactory.createMessage('ErrorMessageBox')
        errorMessageBox.show(parent, title, message)

    def showQuestionMessageBox(self, parent, title, message):
        parent = self.qgis.getMainWindow() if not parent else parent
        questionMessageBox = self.messageFactory.createMessage('QuestionMessageBox')
        return questionMessageBox.show(parent, title, message)
    
    def showInfoMessageBox(self, parent, title, message):
        parent = self.qgis.getMainWindow() if not parent else parent
        infoMessageBox = self.messageFactory.createMessage('InfoMessageBox')
        infoMessageBox.show(parent, title, message)       

    def createMenuBar(self):
        self.menuBarMain = self.qgis.addMenuBar('Ferramentas de Gerência')
        for action in self.getMenuBarActions():
            self.menuBarMain.addAction(action)
        self.menuBarMain.setDisabled(True)

    def createActionsMenuBar(self):
        menuBarActions = []
        for actionConfig in self.getMenuBarActionSettings():
            action = self.qgis.createAction(
                actionConfig['name'],
                actionConfig['iconPath'],
                actionConfig['callback'],
                actionConfig['shortcut']
            )
            menuBarActions.append(action)
        self.setMenuBarActions(menuBarActions)

    def setMenuBarActions(self, menuBarActions):
        self.menuBarActions = menuBarActions

    def getMenuBarActions(self):
        return self.menuBarActions

    def getMenuBarActionSettings(self):
        return []

    def loadDockSap(self):
        dockDirector = DockDirector()
        managementDockBuilder = ManagementDockBuilder()
        dockDirector.constructSapManagementDock(managementDockBuilder, managementToolCtrl=self)
        self.dockSap = managementDockBuilder.getResult()
        self.dockSap.closeEvent = self.closedDock
        self.qgis.addDockWidget(self.dockSap)
        self.menuBarMain.setDisabled(False)

    def closedDock(self, e):
        self.menuBarMain.setDisabled(True)

    def getValuesFromLayer(self, functionName, fieldName):
        fieldSettings = self.functionsSettings.getSettings(functionName, fieldName)
        try:
            for layerOptions in fieldSettings:
                values = self.qgis.getFieldValuesFromLayer(
                    layerOptions['layerName'],
                    layerOptions['fieldName'],
                    layerOptions['allSelection'],
                    layerOptions['chooseAttribute']
                )
                if values:
                    break
            return ",".join([ str(fid) for fid in values ])
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))
            return ''    

    def createWorkUnit(self, layerName, size, overlay, deplace, prefixName, onlySelected):
        try:
            self.qgis.generateWorkUnit(
                layerName, size, overlay, deplace, prefixName, onlySelected
            )
            self.showInfoMessageBox(self.dockSap, 'Aviso', 'Unidades de trabalho geradas com sucesso!')
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))

    def openManagementStyles(self):
        managementStyles = ManagementStylesSingleton.getInstance(self)
        if managementStyles.isVisible():
            managementStyles.toTopLevel()
            return
        managementStyles.addRows( self.sapCtrl.getSapStyles(parent=managementStyles) )
        managementStyles.show()

    def getSapStyles(self, parent=None):
        try:
            return self.sapCtrl.getStyles()
        except Exception as e:
            self.showErrorMessageBox(parent, 'Aviso', str(e))
        return []
        
    def loadStylesFromLayersSelection(self):
        managementStyles = ManagementStylesSingleton.getInstance(self)
        stylesData = self.qgis.getQmlStyleFromLayersTreeSelection()
        if len(stylesData) == 0:
            managementStyles.showError('Aviso', "Selecione no mínimo uma camada.")
            return
        addStyleForm = AddStyleFormSingleton.getInstance(parent=managementStyles)
        if not addStyleForm.exec():
            return
        stylesRows = []
        styleName = addStyleForm.getData()['styleName']
        for styleData in stylesData:
            managementStyles.addRow(
                styleData['f_table_schema'],
                styleData['f_table_name'],
                styleName,
                styleData['styleqml'],
                styleData['stylesld'],
                styleData['ui'],
                styleData['f_geometry_column']
            )

    def applyStylesOnLayers(self, stylesData):
        self.qgis.applyStylesOnLayers(stylesData)

    def updateSapStyles(self, stylesData):
        managementStyles = ManagementStylesSingleton.getInstance(self)
        try:
            message = self.sapCtrl.updateStyles(stylesData)
            self.showInfoMessageBox(managementStyles, 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(managementStyles, 'Aviso', str(e))
        managementStyles.addRows( self.sapCtrl.getSapStyles(parent=managementStyles) )        

    def openManagementModels(self):
        managementModels = ManagementModelsSingleton.getInstance(self)
        if managementModels.isVisible():
            managementModels.toTopLevel()
            return
        managementModels.addRows( self.getSapModels(parent=managementModels) )
        managementModels.show()

    def getSapModels(self, parent=None):
        try:
            return self.sapCtrl.getModels()
        except Exception as e:
            self.showErrorMessageBox(parent, 'Aviso', str(e))
        return []

    def addModel(self):
        managementModels = ManagementModelsSingleton.getInstance(self)
        addModelForm = AddModelFormSingleton.getInstance(parent=managementModels)
        if not addModelForm.exec():
            return
        inputModelData = addModelForm.getData()
        managementModels.addRow(
            inputModelData['modelName'],
            inputModelData['modelDescription'],
            inputModelData['modelXml']
        )

    def updateSapModels(self, modelsData):
        managementModels = ManagementModelsSingleton.getInstance(self)
        try:
            message = self.sapCtrl.updateModels(modelsData)
            self.showInfoMessageBox(managementModels, 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(managementModels, 'Aviso', str(e))
        managementModels.addRows( self.getSapModels(parent=managementModels) )    

    def openManagementRules(self):
        managementRules = ManagementRulesSingleton.getInstance(self)
        if managementRules.isVisible():
            managementRules.toTopLevel()
            return
        sapRules = self.getSapRules(parent=managementRules)
        managementRules.setGroupData(sapRules['grupo_regras'])
        rulesData = sapRules['regras']
        for ruleData in rulesData:
            ruleData['qgisExpressionWidget'] = self.getQgisLineEditExpression()
        managementRules.addRows(rulesData)
        managementRules.show()

    def getSapRules(self, parent=None):
        try:
            return self.sapCtrl.getRules()
        except Exception as e:
            self.showErrorMessageBox(parent, 'Aviso', str(e))
        return {'grupo_regras': [], 'regras': []}

    def getQgisLineEditExpression(self):
        return self.qgis.getWidgetByName('lineEditExpression')
    
    def openManagementRuleSet(self, groupData):
        managementRules = ManagementRulesSingleton.getInstance(self)
        managementRuleSet = ManagementRuleSetSingleton.getInstance(self, managementRules)
        managementRuleSet.addRows(groupData)
        if not managementRuleSet.exec():
            return
        managementRules.setGroupData(
            managementRuleSet.getAllTableData()
        )
        
    def addRules(self, groupList):
        managementRules = ManagementRulesSingleton.getInstance(self)
        addRuleForm = AddRuleFormSingleton.getInstance(
            self.getQgisLineEditExpression(),
            parent=managementRules
        )
        addRuleForm.setGroupList(groupList)
        if not addRuleForm.exec():
            return
        inputRuleData = addRuleForm.getData()
        managementRules.addRow(
            '', 
            inputRuleData['grupo_regra'], 
            inputRuleData['schema'], 
            inputRuleData['camada'],
            inputRuleData['atributo'],
            inputRuleData['regra'], 
            inputRuleData['descricao'],
            self.getQgisLineEditExpression()
        )

    def addRuleSet(self, groupList):
        managementRules = ManagementRulesSingleton.getInstance(self)
        managementRuleSet = ManagementRuleSetSingleton.getInstance(self, managementRules)
        addRuleSetForm = AddRuleSetFormSingleton.getInstance(
            parent=managementRuleSet
        )
        addRuleSetForm.setCurrentGroups(groupList)
        if not addRuleSetForm.exec():
            return
        inputRuleSetData = addRuleSetForm.getData()
        managementRuleSet.addRow(inputRuleSetData['grupo_regra'], inputRuleSetData['cor_rgb'], '0')
    
    def importRulesCsv(self):
        managementRules = ManagementRulesSingleton.getInstance(self)
        addRulesCsvForm = AddRulesCsvFormSingleton.getInstance(self, parent=managementRules)
        if not addRulesCsvForm.exec():
            return
        currentGroupRules = [ d['grupo_regra'].lower() for d in managementRules.getGroupData()]
        rules = RulesSingleton.getInstance()
        newRules = rules.getRulesFromCsv(addRulesCsvForm.getData()['pathRulesCsv'])
        for groupRule in newRules:
            if not ( groupRule.lower() in currentGroupRules):
                groupData = managementRules.getGroupData()
                groupData.append({
                    'grupo_regra' : groupRule,
                    'cor_rgb' : newRules[groupRule]['cor_rgb']
                })
                managementRules.setGroupData(groupData)
            for ruleData in newRules[groupRule]['regras']:
                managementRules.addRow(
                    '', 
                    groupRule, 
                    ruleData['schema'], 
                    ruleData['camada'],
                    ruleData['atributo'], 
                    ruleData['regra'], 
                    ruleData['descricao'],
                    self.getQgisLineEditExpression()
                )
        self.showInfoMessageBox(managementRules, 'Aviso', 'Regras carregadas!')

    def downloadCsvRulesTemplate(self, destPath):
        rules = RulesSingleton.getInstance()
        rules.saveTemplateCsv(destPath)

    ####
    def updateSapRules(self, rulesData, groupsData):
        managementRules = ManagementRulesSingleton.getInstance(self)
        try:
            message = self.sapCtrl.updateRules(rulesData, groupsData)
            self.showInfoMessageBox(managementRules, 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(managementRules, 'Aviso', str(e))
        sapRules = self.getSapRules(parent=managementRules)
        for ruleData in sapRules['regras']:
            ruleData['qgisExpressionWidget'] = self.getQgisLineEditExpression()
        managementRules.setGroupData(sapRules['grupo_regras'])
        managementRules.addRows(sapRules['regras'])

    def downloadSapQgisProject(self, destPath):
        self.sapCtrl.downloadQgisProject(destPath)

    def loadLayersQgisProject(self, projectInProgress):
        try:
            layersData = self.sapCtrl.getLayersQgisProject(projectInProgress)
            dbName = layersData['banco_dados']['nome_db']
            dbHost = layersData['banco_dados']['servidor']
            dbPort = layersData['banco_dados']['porta']
            dbUser = layersData['banco_dados']['login']
            dbPassword = layersData['banco_dados']['senha']
            groupBase = self.qgis.addLayerGroup('Acompanhamento')
            groupProduction = self.qgis.addLayerGroup('Linha de produção', groupBase)
            groupPhase = self.qgis.addLayerGroup('Fase', groupBase)
            groupSubPhase = self.qgis.addLayerGroup('Subfase', groupBase)
            for viewData in layersData['views']:
                """ if viewData['tipo'] == 'fase':
                    groupParent = groupPhase
                elif viewData['tipo'] == 'subfase':
                    groupParent = groupSubPhase
                else:
                    groupParent = groupProduction
                groupProject = self.qgis.addLayerGroup(viewData['projeto'], groupParent) """
                self.qgis.loadLayer(
                    dbName, 
                    dbHost, 
                    dbPort, 
                    dbUser, 
                    dbPassword, 
                    viewData['schema'], 
                    viewData['nome'], 
                    #groupProject
                )
        except Exception as e:
            self.showErrorMessageBox(self.dockSap, 'Aviso', str(e))

    def activeRemoveByClip(self):
        self.qgis.activeMapToolByToolName('removeByClip')

    def activeRemoveByIntersect(self):
        self.qgis.activeMapToolByToolName('removeByIntersect')

    def openManagementUsersPrivileges(self):
        managementUsersPrivileges = ManagementUsersPrivilegesSingleton.getInstance(self)
        if managementUsersPrivileges.isVisible():
            managementUsersPrivileges.toTopLevel()
            return
        managementUsersPrivileges.addRows( self.getSapUsers(parent=managementUsersPrivileges) )
        managementUsersPrivileges.show()

    def getSapUsers(self, parent=None):
        try:
            return self.sapCtrl.getUsers()
        except Exception as e:
            self.showErrorMessageBox(parent, 'Aviso', str(e))
        return []

    def updateUsersPrivileges(self, usersData):
        managementUsersPrivileges = ManagementUsersPrivilegesSingleton.getInstance(self)
        try:
            message = self.sapCtrl.updateUsersPrivileges(usersData)
            self.showInfoMessageBox(managementUsersPrivileges, 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(managementUsersPrivileges, 'Aviso', str(e)) 
        managementUsersPrivileges.addRows( self.getSapUsers(parent=managementUsersPrivileges) )
    
    def openManagementImportLayers(self):
        managementImportLayers = ManagementImportLayersSingleton.getInstance(self)
        if managementImportLayers.isVisible():
            managementImportLayers.toTopLevel()
            return
        managementImportLayers.show()

    def loadManagementImportLayers(self, dbHost, dbPort, dbName):
        managementImportLayers = ManagementImportLayersSingleton.getInstance(self)
        postgresLayers = self.getLayersFromPostgres(dbHost, dbPort, dbName)
        layersRows = []
        sapLayers = self.getSapLayers(parent=managementImportLayers)
        sapLayersNames = [ d['nome'] for d in sapLayers ]
        for layerData in postgresLayers:
            if layerData['nome'] in sapLayersNames:
                continue
            layersRows.append({
                'nome' : layerData['nome'],
                'schema' : layerData['schema'],
                'alias' : '',
                'documentacao' : ''
                
            })
        managementImportLayers.addRows(layersRows)

    def getSapLayers(self, parent=None):
        try:
            return self.sapCtrl.getLayers()
        except Exception as e:
            self.showErrorMessageBox(parent, 'Aviso', str(e))
        return []

    def importLayers(self, layersImported):
        managementImportLayers = ManagementImportLayersSingleton.getInstance(self)
        try:
            message = self.sapCtrl.importLayers(layersImported)
            self.showInfoMessageBox(managementImportLayers, 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(managementImportLayers, 'Aviso', str(e))
        dbName = managementImportLayers.getCurrentDatabase()
        dbData = managementImportLayers.getDatabaseData(dbName)
        if not ( dbData is None ):
            self.loadManagementImportLayers(
                dbData['servidor'],
                dbData['porta'],
                dbData['nome']
            )

    def getLayersFromPostgres(self, dbHost, dbPort, dbName):
        managementImportLayers = ManagementImportLayersSingleton.getInstance(self)
        try:
            postgres = self.databasesFactory.getDatabase('Postgresql')
            auth = self.sapCtrl.getAuthDatabase()
            postgres.setConnection(dbName, dbHost, dbPort, auth['login'], auth['senha'])
            return postgres.getLayers()
        except Exception as e:
            self.showErrorMessageBox(managementImportLayers, 'Aviso', str(e))
        return []

    def openManagementEditLayers(self):
        managementEditLayers = ManagementEditLayersSingleton.getInstance(self)
        if managementEditLayers.isVisible():
            managementEditLayers.toTopLevel()
            return
        managementEditLayers.addRows(self.getSapLayers(parent=managementEditLayers))
        managementEditLayers.show()

    def updateLayers(self, layersData):
        managementEditLayers = ManagementEditLayersSingleton.getInstance(self)
        self.sapCtrl.updateLayers(layersData)
        managementEditLayers.addRows(self.getSapLayers(parent=managementEditLayers))

    def deleteLayers(self, deletedLayersIds):
        managementEditLayers = ManagementEditLayersSingleton.getInstance(self)
        self.sapCtrl.deleteLayers(deletedLayersIds)
        managementEditLayers.addRows(self.getSapLayers(parent=managementEditLayers))

    def copySapSettingsToLocalMode(self,
            dbHost,
            dbPort,
            dbName,
            copyStyles,
            copyModels,
            copyRules,
            copyMenus
        ):
        try:
            postgres = self.databasesFactory.getDatabase('Postgresql')
            auth = self.sapCtrl.getAuthDatabase()
            postgres.setConnection(dbName, dbHost, dbPort, auth['login'], auth['senha'])
            if copyStyles:
                postgres.insertStyles(self.getSapStyles(parent=self.dockSap))
            if copyModels:
                postgres.insertModels(self.getSapModels(parent=self.dockSap))
            if copyRules:
                rulesData = self.getSapRules(parent=self.dockSap)
                postgres.insertRuleGroups(rulesData['grupo_regras'])
                postgres.insertRules(rulesData['regras'])
            if copyMenus:
                postgres.insertMenus(self.getSapMenus(parent=self.dockSap))
            self.showInfoMessageBox(self.dockSap, 'Aviso', "Dados copiados!")
        except Exception as e:
            self.dockSap.showError('Aviso', str(e))

    def getSapMenus(self, parent=None):
        try:
            return self.sapCtrl.getMenus()
        except Exception as e:
            self.showErrorMessageBox(parent, 'Aviso', str(e))
        return []

    def openManagementFmeServers(self):
        managementFmeServers = ManagementFmeServersSingleton.getInstance(self)
        if managementFmeServers.isVisible():
            managementFmeServers.toTopLevel()
            return
        managementFmeServers.addRows(self.getSapFmeServers())
        managementFmeServers.show()

    def getSapFmeServers(self, parent=None):
        try:
            return self.sapCtrl.getFmeServers()
        except Exception as e:
            self.showErrorMessageBox(parent, 'Aviso', str(e))
        return []

    def addFmeServer(self):
        managementFmeServers = ManagementFmeServersSingleton.getInstance(self)
        addFmeServerForm = AddFmeServerFormSingleton.getInstance(parent=managementFmeServers)
        if not addFmeServerForm.exec():
            return
        inputFmeServerData = addFmeServerForm.getData()
        self.createFmeServers([inputFmeServerData])

    def createFmeServers(self, fmeServers):
        managementFmeServers = ManagementFmeServersSingleton.getInstance(self)
        try:
            message = self.sapCtrl.createFmeServers(fmeServers)
            self.showInfoMessageBox(managementFmeServers, 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(managementFmeServers, 'Aviso', str(e))
        managementFmeServers.addRows(self.getSapFmeServers(parent=managementFmeServers))

    def deleteFmeServers(self, fmeServersIds):
        managementFmeServers = ManagementFmeServersSingleton.getInstance(self)
        try:
            message = self.sapCtrl.deleteFmeServers(fmeServersIds)
            self.showInfoMessageBox(managementFmeServers, 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(managementFmeServers, 'Aviso', str(e))
        managementFmeServers.addRows(self.getSapFmeServers(parent=managementFmeServers))

    def updateFmeServers(self, fmeServers):
        managementFmeServers = ManagementFmeServersSingleton.getInstance(self)
        try:
            message = self.sapCtrl.updateFmeServers(fmeServers)
            self.showInfoMessageBox(managementFmeServers, 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(managementFmeServers, 'Aviso', str(e))
        managementFmeServers.addRows(self.getSapFmeServers(parent=managementFmeServers))

    def openManagementFmeProfiles(self):
        managementFmeProfiles = ManagementFmeProfilesSingleton.getInstance(self)
        managementFmeProfiles.setFmeServers(self.getSapFmeServers(parent=managementFmeServers))
        managementFmeProfiles.setSubphases(self.getSapSubphases())
        if managementFmeProfiles.isVisible():
            managementFmeProfiles.toTopLevel()
            return
        managementFmeProfiles.addRows(self.getSapFmeProfiles())
        managementFmeProfiles.show()

    def getSapSubphases(self):
        return self.sapCtrl.getSubphases()

    def getSapFmeProfiles(self):
        return self.sapCtrl.getFmeProfiles()

    def getFmeRoutines(self, server, port):
        try:
            return self.fmeCtrl.getRoutines(server, port)
        except Exception as e:
            self.showErrorMessageBox(self.dockSap, 'Aviso', 'Erro ao buscar rotinas no servidor do FME. Verifique se o servidor está ativo.')
            return []

    def addFmeProfile(self):
        managementFmeProfiles = ManagementFmeProfilesSingleton.getInstance(self)
        addFmeProfileForm = AddFmeProfileFormSingleton.getInstance(self, parent=managementFmeProfiles)
        addFmeProfileForm.loadFmeServers(self.getSapFmeServers())
        addFmeProfileForm.loadSubphases(self.getSapSubphases())
        if not addFmeProfileForm.exec():
            return
        inputFmeProfileData = addFmeProfileForm.getData()
        self.createFmeProfiles([inputFmeProfileData])

    def createFmeProfiles(self, fmeProfiles):
        managementFmeProfiles = ManagementFmeProfilesSingleton.getInstance(self)
        try:
            message = self.sapCtrl.createFmeProfiles(fmeProfiles)
            self.showInfoMessageBox(managementFmeProfiles, 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(managementFmeProfiles, 'Aviso', str(e))
        managementFmeProfiles.addRows(self.getSapFmeProfiles())

    def deleteFmeProfiles(self, fmeProfilesIds):
        managementFmeProfiles = ManagementFmeProfilesSingleton.getInstance(self)
        try:
            message = self.sapCtrl.deleteFmeProfiles(fmeProfilesIds)
            self.showInfoMessageBox(managementFmeProfiles, 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(managementFmeProfiles, 'Aviso', str(e))
        managementFmeProfiles.addRows(self.getSapFmeProfiles())

    def updateFmeProfiles(self, fmeProfiles):
        managementFmeProfiles = ManagementFmeProfilesSingleton.getInstance(self)
        try:
            message = self.sapCtrl.updateFmeProfiles(fmeProfiles)
            self.showInfoMessageBox(managementFmeProfiles, 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(managementFmeProfiles, 'Aviso', str(e))
        managementFmeProfiles.addRows(self.sapCtrl.getFmeProfiles())

    def getSapStepsByFeatureId(self, featureId):
        subphaseId = self.qgis.getActiveLayerAttribute(featureId, 'subfase_id')
        return self.getSapStepsByTag(tag='nome', tagFilter=('subfase_id', subphaseId))

    def getSapStepsByTag(self, tag, withDuplicate=False, numberTag='', tagFilter=('', ''), sortByTag=''):
        def defaultOrder(elem):
            return elem['ordem']
        def atoi(text):
            return int(text) if text.isdigit() else text
        def orderBy(elem):
            return [ atoi(c) for c in re.split(r'(\d+)', elem[sortByTag].lower()) ]
        steps = self.sapCtrl.getSteps()
        steps.sort(key=defaultOrder)  
        selectedSteps = []   
        for step in steps:
            value = step[tag]
            tagTest = [ t[tag] for t in selectedSteps if str(value).lower() in str(t[tag]).lower() ]
            if not(withDuplicate) and tagTest:
                continue
            if numberTag:
                number = len([ t for t in selectedSteps if str(step[numberTag]).lower() in str(t[numberTag]).lower() ]) + 1
                step[numberTag] = "{0} {1}".format(step[numberTag], number)
            selectedSteps.append(step)
        if sortByTag:
            selectedSteps.sort(key=orderBy)
        if tagFilter[0] and tagFilter[1]:
            selectedSteps = [ s for s in selectedSteps if s[tagFilter[0]] == tagFilter[1]]   
        return selectedSteps

    def getQgisComboBoxPolygonLayer(self):
        return self.qgis.getWidgetByName('comboBoxPolygonLayer')

    def createProducts(self, layer, productionLineId, associatedFields, onlySelected):
        features = self.qgis.dumpFeatures(layer, onlySelected)
        products = []
        for feat in features:
            data = {}
            for field in associatedFields:
                data[field] = str(feat[ associatedFields[field] ])
            data['geom'] = self.qgis.geometryToEwkt( feat['geometry'], layer.crs().authid(), 'EPSG:4326' )
            products.append(data)
        invalidProducts = [ p for p in products if not p['escala'] ]
        if invalidProducts:
            Exception('Há feições com dados nulo. Para criar produtos as feições não podem ter escala nula.')
        try:
            message = self.sapCtrl.createProducts(productionLineId, products)
            self.showInfoMessageBox(None, 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(None, 'Aviso', str(e))

    def loadWorkUnit(self, layer, subphaseId, onlySelected, associatedFields):
        features = self.qgis.dumpFeatures(layer, onlySelected)
        fieldsType = {
            'disponivel' : bool,
            'dado_producao_id' : int,
            'lote_id' : int,
            'prioridade' : int
        }
        workUnits = []
        for feat in features:
            data = {}
            for field in associatedFields:
                value = str(feat[ associatedFields[field]])
                data[field] = fieldsType[field](value) if field in fieldsType else value
            data['geom'] = self.qgis.geometryToEwkt( feat['geometry'], layer.crs().authid(), 'EPSG:4326' )
            workUnits.append(data)
        invalidWorkUnits = [ 
            p for p in workUnits 
            if not (
                p['nome'] and p['epsg'] and p['dado_producao_id'] 
                and 
                p['disponivel'] and p['prioridade'] and p['lote_id']
            ) 
        ]
        if invalidWorkUnits:
            self.showErrorMessageBox(self.dockSap, 'Aviso', 'Há feições com dados nulo. Para carregar unidades de trabalho as feições só podem ter a observação nula.')
            return
        try:
            message = self.sapCtrl.loadWorkUnit(subphaseId, workUnits)
            self.showInfoMessageBox(None, 'Aviso', message)
        except Exception as e:
            self.showErrorMessageBox(None, 'Aviso', str(e))

    def addSapNewRevision(self, activityIds):
        self.sapCtrl.addNewRevision(activityIds)

    def addSapNewRevisionCorrection(self, activityIds):
        self.sapCtrl.addNewRevisionCorrection(activityIds)

    def advanceSapActivityToNextStep(self, activityIds, endStep):
        self.sapCtrl.advanceActivityToNextStep(
            activityIds, 
            endStep
        )

    def getSapLots(self):
        return self.sapCtrl.getLots()

    def alterSapLot(self, workspacesIds, lotId):
        self.sapCtrl.alterLot(workspacesIds, lotId)

    def getSapAssociationStrategies(self):
        return self.sapCtrl.getAssociationStrategies()

    def associateSapInputs(self, workspacesIds, inputGroupId, associationStrategyId, defaultPath):
        self.sapCtrl.associateInputs(workspacesIds, inputGroupId, associationStrategyId, defaultPath)

    def deleteSapUserActivities(self, userId):
        self.sapCtrl.deleteUserActivities(userId)

    def copySapWorkUnit(self, workspacesIds, stepIds, associateInputs):
        self.sapCtrl.copyWorkUnit(workspacesIds, stepIds, associateInputs)

    def createSapActivities(self, workspacesIds, stepId):
        self.sapCtrl.createActivities(workspacesIds, stepId )

    def getSapProfiles(self):
        return self.sapCtrl.getProfiles()

    def createSapPriorityGroupActivity(self, activityIds, priority, profileId):
        self.sapCtrl.createPriorityGroupActivity(
            activityIds, 
            priority, 
            profileId
        )

    def getSapProductionLines(self):
        return self.sapCtrl.getProductionLines()

    def deleteSapActivities(self, activityIds):
        self.sapCtrl.deleteActivities(
            activityIds
        )

    def deleteSapAssociatedInputs(self, workspacesIds, inputGroupId):
        self.sapCtrl.deleteAssociatedInputs(workspacesIds, inputGroupId) 

    def deleteSapRevisionCorrection(self, stepId):
        self.sapCtrl.deleteRevisionCorrection(stepId)

    def deleteSapWorkUnits(self, workspacesIds):
        self.sapCtrl.deleteWorkUnits(workspacesIds)       

    def fillSapCommentActivity(self, activityIds, commentActivity, commentWorkspace, commentStep, commentSubfase, commentLot):
        self.sapCtrl.fillCommentActivity(
            activityIds, 
            commentActivity, 
            commentWorkspace, 
            commentStep, 
            commentSubfase,
            commentLot
        )

    def getSapCommentsByActivity(self, activityId):
        return self.sapCtrl.getCommentsByActivity(activityId)

    def getSapUsersFromAuthService(self):
        return self.sapCtrl.getUsersFromAuthService()

    def importSapUsersAuthService(self, usersIds):
        self.managementToolCtrl.importUsersAuthService(usersIds)

    def lockSapWorkspace(self, workspacesIds):
        self.sapCtrl.lockWorkspace(workspacesIds)

    def openSapActivity(self, activityId):
        self.sapApi.loadActivityById(activityId)
        self.qgis.startSapFP(self.sapCtrl)
        
    def openSapNextActivityByUser(self, userId, nextActivity):
        self.sapCtrl.loadNextActivityByUser(userId, nextActivity)
        self.qgis.startSapFP(self.sapCtrl)

    def pauseSapActivity(self, workspacesIds):
        self.sapCtrl.pauseActivity(workspacesIds)

    def resetSapPrivileges(self):
        self.sapCtrl.resetPrivileges()

    def restartSapActivity(self, workspacesIds):
        self.sapCtrl.restartActivity(workspacesIds)

    def returnSapActivityToPreviousStep(self, activityIds, preserveUser):
        self.sapCtrl.returnActivityToPreviousStep(activityIds, preserveUser)

    def revokeSapPrivileges(self, dbHost, dbPort, dbName):
        self.sapCtrl.revokePrivileges(dbHost, dbPort, dbName)

    def setSapPriorityActivity(self, activityIds, priority, userId):
        self.sapCtrl.setPriorityActivity(activityIds, priority, userId)

    def synchronizeSapUserInformation(self):
        self.sapCtrl.synchronizeUserInformation()

    def unlockSapWorkspace(self, workspacesIds):
        self.sapCtrl.unlockWorkspace(workspacesIds)
    
    def updateSapBlockedActivities(self):
        self.sapCtrl.updateBlockedActivities()

    def getSapDatabases(self):
        return self.sapCtrl.getDatabases()

    def getSapInputGroups(self):
        return self.sapCtrl.getInputGroups()

            