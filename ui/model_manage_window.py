# -*- coding: utf-8 -*-
"""

ModelManageDialog：
    波管型号管理页面

修改人： hnchen
修改时间： 2025/06/20
"""
from PySide6.QtWidgets import (
  QDialog, QListWidgetItem, QMessageBox, QDialogButtonBox,
  QLabel, QLineEdit, QInputDialog, QFormLayout
)

from ui.model_manage_dialog import Ui_ModelManageDialog
from util.file import (load_ini, get_exe_dir)
import os

class ModelManageDialog(QDialog, Ui_ModelManageDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setFixedSize(700, 800)
        self.ini_path = os.path.join(get_exe_dir(), 'settings.ini')

        # 1. 初始化列表
        self.cfg = load_ini()
        self.load_models()

        # 保存按钮
        btn_save = self.buttonBox.button(QDialogButtonBox.Save)
        if btn_save:
            btn_save.setText("保存")
        # 取消按钮
        btn_cancel = self.buttonBox.button(QDialogButtonBox.Cancel)
        if btn_cancel:
            btn_cancel.setText("取消")

        # 2. 连接信号
        self.listModels.currentRowChanged.connect(self.on_model_selected)
        self.btnAddModel.clicked.connect(self.on_add_model)
        self.btnRemoveModel.clicked.connect(self.on_remove_model)
        self.btnAddParam.clicked.connect(self.on_add_param)
        self.btnRemoveParam.clicked.connect(self.on_remove_param)
        self.buttonBox.accepted.connect(self.on_save)
        self.buttonBox.rejected.connect(self.reject)

        # 默认选中第一个
        if self.listModels.count()>0:
            self.listModels.setCurrentRow(0)

    def load_models(self):
        """把 INI 节名加载到 listModels"""
        self.listModels.clear()
        for sec in self.cfg.sections():
            if sec not in ['Auth']:
                self.listModels.addItem(sec)

    def on_model_selected(self, row):
        """选中型号后，只填充 listParams（参数名列表）"""
        self.listParams.clear()
        if row < 0:
            return
        sec = self.listModels.item(row).text()
        for key in self.cfg[sec].keys():
            self.listParams.addItem(key)

    def on_add_model(self):
        """添加一个新型号"""
        dlg = QInputDialog(self)
        dlg.setWindowTitle("新增型号")
        dlg.setLabelText("型号名称：")
        # 把按钮改成中文
        dlg.setOkButtonText("确认")
        dlg.setCancelButtonText("取消")

        font = dlg.font()  # 取出当前字体（family、weight 都保留）
        font.setPointSize(12)  # 改为 12pt，按需调整
        dlg.setFont(font)  # 应用到整个对话框

        if dlg.exec() == QInputDialog.Accepted:
            name = dlg.textValue().strip()
            if name in self.cfg.sections():
                box = QMessageBox(self)
                box.setWindowTitle("错误")
                box.setText(f"型号已存在！")
                box.setStandardButtons(QMessageBox.NoButton)
                box.addButton("确认", QMessageBox.YesRole)
                box.addButton("取消", QMessageBox.NoRole)
                box.exec()
                return
            self.cfg[name] = {}
            self.listModels.addItem(name)
            self.listModels.setCurrentRow(self.listModels.count()-1)

    def on_remove_model(self):
        """删除一个型号"""
        row = self.listModels.currentRow()
        if row<0: return
        sec = self.listModels.currentItem().text()
        box = QMessageBox(self)
        box.setWindowTitle("删除型号")
        box.setText(f"确认要删除型号 “{sec}”？")
        box.setStandardButtons(QMessageBox.NoButton)
        btn_yes = box.addButton("确认", QMessageBox.YesRole)
        box.addButton("取消", QMessageBox.NoRole)
        font = box.font()  # 取出当前字体（family、weight 都保留）
        font.setPointSize(12)  # 改为 12pt，按需调整
        box.setFont(font)  # 应用到整个对话框
        box.exec()
        if box.clickedButton() == btn_yes:
            self.cfg.remove_section(sec)
            self.listModels.takeItem(row)

    def on_add_param(self):
        """给当前型号加一个参数"""
        row = self.listModels.currentRow()
        if row<0: return
        sec = self.listModels.item(row).text()
        dlg = QInputDialog(self)
        dlg.setWindowTitle("新增参数")
        dlg.setLabelText("参数名：")
        # 把按钮改成中文
        dlg.setOkButtonText("确认")
        dlg.setCancelButtonText("取消")
        font = dlg.font()  # 取出当前字体（family、weight 都保留）
        font.setPointSize(12)  # 改为 12pt，按需调整
        dlg.setFont(font)  # 应用到整个对话框

        if dlg.exec() == QInputDialog.Accepted:
            param = dlg.textValue().strip()
            dlg = QInputDialog(self)
            dlg.setWindowTitle("新增参数")
            dlg.setLabelText("默认值：")
            # 把按钮改成中文
            dlg.setOkButtonText("确认")
            dlg.setCancelButtonText("取消")
            font = dlg.font()  # 取出当前字体（family、weight 都保留）
            font.setPointSize(12)  # 改为 12pt，按需调整
            dlg.setFont(font)  # 应用到整个对话框
            if dlg.exec() == QInputDialog.Accepted:
                value = dlg.textValue().strip()
                self.cfg[sec][param] = value
                self.on_model_selected(row)

    def on_remove_param(self):
        """删除当前选中的参数名"""
        row = self.listParams.currentRow()
        if row < 0:
            return
        key = self.listParams.currentItem().text()
        sec = self.listModels.currentItem().text()
        box = QMessageBox(self)
        box.setWindowTitle("删除参数")
        box.setText(f"确认要删除参数 “{key}”？")
        box.setStandardButtons(QMessageBox.NoButton)
        btn_yes = box.addButton("确认", QMessageBox.YesRole)
        box.addButton("取消", QMessageBox.NoRole)
        font = box.font()  # 取出当前字体（family、weight 都保留）
        font.setPointSize(12)  # 改为 12pt，按需调整
        box.setFont(font)  # 应用到整个对话框
        box.exec()
        if box.clickedButton() == btn_yes:
            # 从配置和列表都删掉
            self.cfg.remove_option(sec, key)
            self.listParams.takeItem(row)

    def on_save(self):
        """保存回 INI 并关闭"""
        with open(self.ini_path, 'w', encoding='utf-8') as f:
            self.cfg.write(f)
        self.accept()
