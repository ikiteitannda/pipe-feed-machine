# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'model_manage_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QAbstractItemView, QApplication, QDialog,
    QDialogButtonBox, QGroupBox, QHBoxLayout, QListWidget,
    QListWidgetItem, QPushButton, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_ModelManageDialog(object):
    def setupUi(self, ModelManageDialog):
        if not ModelManageDialog.objectName():
            ModelManageDialog.setObjectName(u"ModelManageDialog")
        font = QFont()
        font.setPointSize(12)
        ModelManageDialog.setFont(font)
        self.verticalLayout = QVBoxLayout(ModelManageDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.hLayoutMain = QHBoxLayout()
        self.hLayoutMain.setObjectName(u"hLayoutMain")
        self.groupModels = QGroupBox(ModelManageDialog)
        self.groupModels.setObjectName(u"groupModels")
        self.vLayoutModels = QVBoxLayout(self.groupModels)
        self.vLayoutModels.setObjectName(u"vLayoutModels")
        self.hLayoutModelBtns = QHBoxLayout()
        self.hLayoutModelBtns.setObjectName(u"hLayoutModelBtns")
        self.btnAddModel = QPushButton(self.groupModels)
        self.btnAddModel.setObjectName(u"btnAddModel")

        self.hLayoutModelBtns.addWidget(self.btnAddModel)

        self.btnRemoveModel = QPushButton(self.groupModels)
        self.btnRemoveModel.setObjectName(u"btnRemoveModel")

        self.hLayoutModelBtns.addWidget(self.btnRemoveModel)


        self.vLayoutModels.addLayout(self.hLayoutModelBtns)

        self.listModels = QListWidget(self.groupModels)
        self.listModels.setObjectName(u"listModels")

        self.vLayoutModels.addWidget(self.listModels)


        self.hLayoutMain.addWidget(self.groupModels)

        self.groupParams = QGroupBox(ModelManageDialog)
        self.groupParams.setObjectName(u"groupParams")
        self.vLayoutParams = QVBoxLayout(self.groupParams)
        self.vLayoutParams.setObjectName(u"vLayoutParams")
        self.hLayoutParamBtns = QHBoxLayout()
        self.hLayoutParamBtns.setObjectName(u"hLayoutParamBtns")
        self.btnAddParam = QPushButton(self.groupParams)
        self.btnAddParam.setObjectName(u"btnAddParam")

        self.hLayoutParamBtns.addWidget(self.btnAddParam)

        self.btnRemoveParam = QPushButton(self.groupParams)
        self.btnRemoveParam.setObjectName(u"btnRemoveParam")

        self.hLayoutParamBtns.addWidget(self.btnRemoveParam)


        self.vLayoutParams.addLayout(self.hLayoutParamBtns)

        self.listParams = QListWidget(self.groupParams)
        self.listParams.setObjectName(u"listParams")
        self.listParams.setAlternatingRowColors(True)
        self.listParams.setSelectionMode(QAbstractItemView.SingleSelection)

        self.vLayoutParams.addWidget(self.listParams)


        self.hLayoutMain.addWidget(self.groupParams)


        self.verticalLayout.addLayout(self.hLayoutMain)

        self.buttonBox = QDialogButtonBox(ModelManageDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Save|QDialogButtonBox.Cancel)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(ModelManageDialog)

        QMetaObject.connectSlotsByName(ModelManageDialog)
    # setupUi

    def retranslateUi(self, ModelManageDialog):
        ModelManageDialog.setWindowTitle(QCoreApplication.translate("ModelManageDialog", u"\u6ce2\u7ba1\u578b\u53f7\u7ba1\u7406", None))
        self.groupModels.setTitle(QCoreApplication.translate("ModelManageDialog", u"\u578b\u53f7\u5217\u8868", None))
        self.btnAddModel.setText(QCoreApplication.translate("ModelManageDialog", u"\uff0b\u578b\u53f7", None))
        self.btnRemoveModel.setText(QCoreApplication.translate("ModelManageDialog", u"\uff0d\u578b\u53f7", None))
        self.groupParams.setTitle(QCoreApplication.translate("ModelManageDialog", u"\u53c2\u6570\u5217\u8868", None))
        self.btnAddParam.setText(QCoreApplication.translate("ModelManageDialog", u"\uff0b\u53c2\u6570", None))
        self.btnRemoveParam.setText(QCoreApplication.translate("ModelManageDialog", u"\uff0d\u53c2\u6570", None))
    # retranslateUi

