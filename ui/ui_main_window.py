# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGraphicsView,
    QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QMainWindow, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1400, 900)
        self.central_widget = QWidget(MainWindow)
        self.central_widget.setObjectName(u"central_widget")
        font = QFont()
        font.setPointSize(12)
        self.central_widget.setFont(font)
        self.gridLayout = QGridLayout(self.central_widget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.graphicsView = QGraphicsView(self.central_widget)
        self.graphicsView.setObjectName(u"graphicsView")

        self.gridLayout.addWidget(self.graphicsView, 0, 0, 1, 1)

        self.listLogs = QListWidget(self.central_widget)
        self.listLogs.setObjectName(u"listLogs")

        self.gridLayout.addWidget(self.listLogs, 0, 1, 1, 1)

        self.groupBottom = QGroupBox(self.central_widget)
        self.groupBottom.setObjectName(u"groupBottom")
        self.gridLayoutBottom = QGridLayout(self.groupBottom)
        self.gridLayoutBottom.setSpacing(10)
        self.gridLayoutBottom.setObjectName(u"gridLayoutBottom")
        self.groupControls = QGroupBox(self.groupBottom)
        self.groupControls.setObjectName(u"groupControls")
        self.groupControls.setMinimumHeight(250)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupControls.sizePolicy().hasHeightForWidth())
        self.groupControls.setSizePolicy(sizePolicy)
        self.verticalLayoutControls = QVBoxLayout(self.groupControls)
        self.verticalLayoutControls.setSpacing(5)
        self.verticalLayoutControls.setObjectName(u"verticalLayoutControls")
        self.groupMode = QGroupBox(self.groupControls)
        self.groupMode.setObjectName(u"groupMode")
        self.gridLayoutModes = QGridLayout(self.groupMode)
        self.gridLayoutModes.setObjectName(u"gridLayoutModes")
        self.gridLayoutModes.setHorizontalSpacing(4)
        self.gridLayoutModes.setVerticalSpacing(4)
        self.comboMode = QComboBox(self.groupMode)
        self.comboMode.setObjectName(u"comboMode")
        sizePolicy.setHeightForWidth(self.comboMode.sizePolicy().hasHeightForWidth())
        self.comboMode.setSizePolicy(sizePolicy)

        self.gridLayoutModes.addWidget(self.comboMode, 0, 0, 1, 1)


        self.verticalLayoutControls.addWidget(self.groupMode)

        self.horizontalLayoutSaveReturn = QHBoxLayout()
        self.horizontalLayoutSaveReturn.setObjectName(u"horizontalLayoutSaveReturn")
        self.groupSave = QGroupBox(self.groupControls)
        self.groupSave.setObjectName(u"groupSave")
        self.verticalLayoutSave = QVBoxLayout(self.groupSave)
        self.verticalLayoutSave.setSpacing(5)
        self.verticalLayoutSave.setObjectName(u"verticalLayoutSave")
        self.chkSaveImage = QCheckBox(self.groupSave)
        self.chkSaveImage.setObjectName(u"chkSaveImage")

        self.verticalLayoutSave.addWidget(self.chkSaveImage)


        self.horizontalLayoutSaveReturn.addWidget(self.groupSave)

        self.btnReturnLogin = QPushButton(self.groupControls)
        self.btnReturnLogin.setObjectName(u"btnReturnLogin")
        self.btnReturnLogin.setMinimumWidth(80)

        self.horizontalLayoutSaveReturn.addWidget(self.btnReturnLogin)


        self.verticalLayoutControls.addLayout(self.horizontalLayoutSaveReturn)

        self.groupCamera = QGroupBox(self.groupControls)
        self.groupCamera.setObjectName(u"groupCamera")
        self.horizontalLayoutCamera = QHBoxLayout(self.groupCamera)
        self.horizontalLayoutCamera.setSpacing(20)
        self.horizontalLayoutCamera.setObjectName(u"horizontalLayoutCamera")
        self.btnConnectCamera = QPushButton(self.groupCamera)
        self.btnConnectCamera.setObjectName(u"btnConnectCamera")
        self.btnConnectCamera.setMinimumWidth(120)
        self.btnConnectCamera.setMinimumHeight(40)
        self.btnConnectCamera.setMaximumWidth(120)
        self.btnConnectCamera.setMaximumHeight(40)

        self.horizontalLayoutCamera.addWidget(self.btnConnectCamera)

        self.labelCameraStatus = QLabel(self.groupCamera)
        self.labelCameraStatus.setObjectName(u"labelCameraStatus")

        self.horizontalLayoutCamera.addWidget(self.labelCameraStatus)


        self.verticalLayoutControls.addWidget(self.groupCamera)


        self.gridLayoutBottom.addWidget(self.groupControls, 0, 0, 1, 1)

        self.groupConfig = QGroupBox(self.groupBottom)
        self.groupConfig.setObjectName(u"groupConfig")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.groupConfig.sizePolicy().hasHeightForWidth())
        self.groupConfig.setSizePolicy(sizePolicy1)
        self.verticalLayoutConfig = QVBoxLayout(self.groupConfig)
        self.verticalLayoutConfig.setObjectName(u"verticalLayoutConfig")
        self.labelConfigWarning = QLabel(self.groupConfig)
        self.labelConfigWarning.setObjectName(u"labelConfigWarning")
        self.labelConfigWarning.setVisible(False)

        self.verticalLayoutConfig.addWidget(self.labelConfigWarning)

        self.configContent = QWidget(self.groupConfig)
        self.configContent.setObjectName(u"configContent")
        self.gridConfig = QGridLayout(self.configContent)
        self.gridConfig.setObjectName(u"gridConfig")
        self.gridConfig.setContentsMargins(0, 0, 0, 0)

        self.verticalLayoutConfig.addWidget(self.configContent)


        self.gridLayoutBottom.addWidget(self.groupConfig, 0, 1, 1, 1)


        self.gridLayout.addWidget(self.groupBottom, 1, 0, 1, 2)

        MainWindow.setCentralWidget(self.central_widget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"\u4e0a\u7ba1\u7a0b\u5e8f", None))
        self.groupBottom.setTitle(QCoreApplication.translate("MainWindow", u"Operations", None))
        self.groupControls.setTitle(QCoreApplication.translate("MainWindow", u"Controls", None))
        self.groupMode.setTitle(QCoreApplication.translate("MainWindow", u"Mode", None))
        self.groupSave.setTitle(QCoreApplication.translate("MainWindow", u"Save Options", None))
        self.chkSaveImage.setText(QCoreApplication.translate("MainWindow", u"\u4fdd\u5b58\u56fe\u7247", None))
        self.btnReturnLogin.setText(QCoreApplication.translate("MainWindow", u"\u8fd4\u56de\u767b\u5f55", None))
        self.groupCamera.setTitle(QCoreApplication.translate("MainWindow", u"Camera", None))
        self.btnConnectCamera.setText(QCoreApplication.translate("MainWindow", u"\u8fde\u63a5\u76f8\u673a", None))
        self.labelCameraStatus.setText(QCoreApplication.translate("MainWindow", u"\u76f8\u673a\u72b6\u6001\uff1a \u5c1a\u672a\u8fde\u63a5", None))
        self.groupConfig.setTitle(QCoreApplication.translate("MainWindow", u"Config", None))
        self.labelConfigWarning.setText(QCoreApplication.translate("MainWindow", u"\u4fee\u6539 Camera \u6216 Plc \u53c2\u6570\u540e\uff0c\u8bf7\u52a1\u5fc5\u91cd\u65b0\u8fde\u63a5\u76f8\u673a", None))
        self.labelConfigWarning.setStyleSheet(QCoreApplication.translate("MainWindow", u"color: red; font-weight: bold; font-size:22px;", None))
    # retranslateUi

