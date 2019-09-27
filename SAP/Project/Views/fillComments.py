# -*- coding: utf-8 -*-
import os, sys, copy
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from Ferramentas_Gerencia.utils import msgBox

class FillComments(QtWidgets.QWidget):

    dialog_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 
        'fillComments.ui'
    )

    icon_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 
        '..',
        '..',
        '..',
        'icons',
        'extract.png'
    )

    run = QtCore.pyqtSignal()

    extractValues = QtCore.pyqtSignal()

    def __init__(self, iface):
        super(FillComments, self).__init__()
        self.iface = iface
        uic.loadUi(self.dialog_path, self)
        self.extract_field_btn.setIcon(QtGui.QIcon(self.icon_path))
        self.extract_field_btn.setIconSize(QtCore.QSize(24,24))
        self.extract_field_btn.setToolTip('Extrair valores mediante seleções')
        self.extract_field_btn.clicked.connect(
            self.extractValues.emit
        )
        self.ok_btn.clicked.connect( 
            self.validate_input    
        )

    def validate_input(self):
        if ( 
            self.activity_id_le.text() 
            and
            self.obs_activity_le.text() 
            and
            self.obs_workspace_le.text() 
            and
            self.obs_step_le.text() 
            and
            self.obs_subfase_le.text() 
            ):
            self.run.emit()
        else:
            html = "<p>Preencha todos os campos!</p>"
            msgBox.show(text=html, title=u"Erro", parent=self)

    def get_input_data(self):
        return {
            "param" : {
                "atividade_id" : int(self.activity_id_le.text()),
                "observacao_atividade" : self.obs_activity_le.text(),
                "observacao_unidade_trabalho" : self.obs_workspace_le.text(),
                "observacao_etapa" : self.obs_step_le.text(),
                "observacao_subfase" : self.obs_subfase_le.text()
            },
            "function_name" : "fill_comment_activity"
        }

    def get_extraction_config(self):
        return [
            {
                "layer_name" : "atividades_em_execucao",
                "field_name" : "atividade_id",
                "all_selection" : False
            },
            {
                "layer_name" : "problema_atividade",
                "field_name" : "atividade_id",
                "all_selection" : False
            },
            {
                "layer_name" : "subfase_",
                "field_name" : "atividade_id",
                "all_selection" : False
            }
        ]