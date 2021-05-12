# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PingMonitorSettings_design.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PySide2 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(267, 267)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.lstIPs = QtWidgets.QListWidget(Form)
        self.lstIPs.setObjectName("lstIPs")
        self.verticalLayout.addWidget(self.lstIPs)
        self.horizontalLayout0 = QtWidgets.QHBoxLayout()
        self.horizontalLayout0.setObjectName("horizontalLayout0")
        self.horizontalLayout1 = QtWidgets.QHBoxLayout()
        self.horizontalLayout1.setObjectName("horizontalLayout1")
        self.horizontalLayout2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout2.setObjectName("horizontalLayout2")
        self.ip_name = QtWidgets.QLineEdit('___.___.___.___')
        self.ip_name.setObjectName("ip_name")
        self.horizontalLayout0.addWidget(self.ip_name)
        self.btnAdd = QtWidgets.QPushButton(Form)
        self.btnAdd.setObjectName("btnAdd")
        self.horizontalLayout1.addWidget(self.btnAdd)
        self.btnRemove = QtWidgets.QPushButton(Form)
        self.btnRemove.setObjectName("btnRemove")
        self.btnUpdateList = QtWidgets.QPushButton(Form)
        self.btnUpdateList.setObjectName("btnUpdateList")
        self.horizontalLayout1.addWidget(self.btnRemove)
        self.horizontalLayout2.addWidget(self.btnUpdateList)
        self.verticalLayout.addLayout(self.horizontalLayout0)
        self.verticalLayout.addLayout(self.horizontalLayout1)
        self.verticalLayout.addLayout(self.horizontalLayout2)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Настройки"))
        self.label.setText(_translate("Form", "Список IP-адресов"))
        self.btnAdd.setText(_translate("Form", "Добавить IP"))
        self.btnRemove.setText(_translate("Form", "Удалить"))
        self.btnUpdateList.setText(_translate("Form", "Обновить список ip"))