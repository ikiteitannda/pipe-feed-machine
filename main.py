# -*- coding: utf-8 -*-
"""
主程序入口：
- 负责 UI 初始化、布局控制
- 启动/停止 CameraWorker & PlcWorker 线程
- 连接信号槽进行图像显示、日志输出、PLC 通信
- 动态加载/保存配置、运行时参数变更

修改人： hnchen
修改时间： 2025/06/13
"""
import sys
import os
import math
import datetime

import cv2
from PySide6.QtWidgets import (
    QMainWindow, QApplication, QLabel, QLineEdit,
    QGridLayout, QGraphicsScene, QGraphicsView, QDialog
)
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QPixmap

from util.file import (load_ini, get_exe_dir, write_ini)
from ui.ui_main_window import Ui_MainWindow
from work.camera_work import CameraWorker
from work.plc_work import PlcWorker
from ui.login import LoginDialog

def on_param_changed(section: str, key: str, value: str):
    """
    回写配置
    """
    write_ini(section, key, value)

def clear_layout(layout: QGridLayout):
    """
    清空一个 QGridLayout 中的所有控件
    """
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget:
            layout.removeWidget(widget)
            widget.deleteLater()

class MainWindow(QMainWindow, Ui_MainWindow):
    """
    主窗口类，继承自 QMainWindow + QtDesigner 生成的 Ui_MainWindow
    """
    MAX_LOG_ENTRIES = 2000  # 日志最大行数，超过则自动删除最旧

    def __init__(self, skipped: bool = True):
        super().__init__()
        self.skipp_login = skipped
        # 加载 UI
        self.setupUi(self)

        # ------ 顶部主布局权重调整 ------
        self.gridLayout.setColumnStretch(0, 6)
        self.gridLayout.setColumnStretch(1, 4)
        self.gridLayout.setRowStretch(0, 7)
        self.gridLayout.setRowStretch(1, 3)

        # ------ 准备动态模式切换和参数编辑 ------
        # 所有节名（含 Calib, Plc, Camera...）
        config = load_ini()
        exclude = {'Calib', 'Plc', 'Camera', 'Detector', 'Auth'} if skipped else {'Auth', 'Detector'}
        self.sections = [s for s in config.sections() if s not in exclude]
        self.current_section = self.sections[0]
        self.config_widgets = {}  # 存放 label+edit
        self._edits = {}  # 存放 (section,key)->QLineEdit

        # 过滤特定节，构建参数控件列表（但不布局）
        for section in self.sections:
            if section not in self.config_widgets:
                for key, val in config[section].items():
                    lbl = QLabel(f"{key.replace('_', ' ').title()}:")
                    edit = QLineEdit(val)
                    edit.setMaximumWidth(320)
                    self.config_widgets[f"{section}.{key}"] = (lbl, edit)

        # ------ 模式选择下拉框 ------
        # modes 所有的节
        self.modes = [sec for sec in self.sections]
        # 清空旧项
        self.comboMode.clear()
        # 添加选项
        self.comboMode.addItems(self.modes)
        # 初始选中第一个
        self.comboMode.setCurrentIndex(0)
        # 绑定信号，切换模式时刷新
        self.comboMode.currentIndexChanged.connect(self.on_mode_changed_combo)

        # ------ 底部布局比例 ------
        self.gridLayoutBottom.setColumnStretch(0, 2)
        self.gridLayoutBottom.setColumnStretch(1, 8)
        self.gridLayoutBottom.setContentsMargins(4, 4, 4, 4)
        self.verticalLayoutControls.setContentsMargins(2, 2, 2, 2)

        # 清空参数编辑区
        clear_layout(self.gridConfig)

        # ------ 按钮和复选框信号 ------
        self.labelCameraStatus.setStyleSheet("color:red;font-size:16px;")
        self.btnConnectCamera.clicked.connect(self.on_connect_camera)
        self.save_image = False
        self.chkSaveImage.toggled.connect(self.on_check_save_image_toggled)

        # ------ GraphicsView 场景准备 ------
        self._scene = QGraphicsScene(self)
        self.graphicsView.setScene(self._scene)
        self.graphicsView.setResizeAnchor(QGraphicsView.AnchorViewCenter)

        # ------ 默认模式、线程变量 ------
        self.current_section = self.sections[0]
        self.cam_thread = None
        self.plc_thread = None

        # 模式切换一次，触发参数区绘制
        self.on_mode_changed_combo(self.comboMode.currentIndex())

        # ------ 日志系统初始化 ------
        self.listLogs.clear()
        self.logs_dir = os.path.join(get_exe_dir(), "logs")
        os.makedirs(self.logs_dir, exist_ok=True)
        self.log_date = datetime.date.today()
        self.log_name = f"{self.log_date.isoformat()}.log"
        self.log_file = open(os.path.join(self.logs_dir, self.log_name), 'a', encoding='utf-8')
        self.log_file.close()

    def on_check_save_image_toggled(self, checked: bool):
        """
        切换是否保存原始图片，联动 CameraWorker
        """
        self.save_image = checked
        if self.cam_thread:
            self.cam_thread.check_save_image(checked)

    def on_frame(self, pix: QPixmap):
        """
        CameraWorker 发来 QPixmap，直接展示到 graphicsView
        """
        self._scene.clear()
        self._scene.addPixmap(pix)
        self._scene.setSceneRect(pix.rect())
        self.graphicsView.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)

    def on_check(self, dev_count: int):
        """
        CameraWorker 发来状态更新：设备数量
        更新 UI 状态标签和日志
        """
        if dev_count < 1:
            # 断开或未检测到，停止所有线程
            if self.cam_thread:
                try:
                    self.cam_thread.stop()
                finally:
                    pass
            if self.plc_thread:
                try:
                    self.plc_thread.stop()
                finally:
                    pass
            self.cam_thread = None
            self.plc_thread = None
            self.btnConnectCamera.setText("连接相机")
            self.labelCameraStatus.setText("相机状态： 未检测到相机")
            self.labelCameraStatus.setStyleSheet("color:red;font-size:16px;")
            self.on_log_message(f"[{self.current_section}] 相机断开连接")
            self.btnConnectCamera.setEnabled(True)
        else:
            self.btnConnectCamera.setText("断开相机")
            self.labelCameraStatus.setText("相机状态： 已连接")
            self.labelCameraStatus.setStyleSheet("color:green;font-size:16px;")
            self.on_log_message(f"[{self.current_section}] 相机已连接")
            self.btnConnectCamera.setEnabled(True)
        self.btnConnectCamera.setFocus()

    def on_connect_camera(self):
        """
        连接/断开 相机 & PLC 线程
        """
        self.btnConnectCamera.setEnabled(False)
        if self.cam_thread:
            self.labelCameraStatus.setText("相机状态： 断开中...")
            self.labelCameraStatus.setStyleSheet("color:orange;font-size:16px;")
            # 立刻刷新 UI
            QApplication.processEvents()
            # 停止所有线程
            try:
                self.cam_thread.stop()
            finally:
                pass
            try:
                self.plc_thread.stop()
            finally:
                pass
            self.cam_thread = None
            self.plc_thread = None
            self.btnConnectCamera.setText("连接相机")
            self.labelCameraStatus.setText("相机状态： 未连接")
            self.labelCameraStatus.setStyleSheet("color:red;font-size:16px;")
            self.on_log_message(f"[{self.current_section}] 相机未连接")
        else:
            try:
                self.labelCameraStatus.setText("相机状态： 连接中...")
                self.labelCameraStatus.setStyleSheet("color:orange;font-size:16px;")
                # 从 INI 读取 PLC 配置
                config = load_ini()
                plc_conf = config['Plc']
                host = plc_conf.get('Host')
                port = plc_conf.getint('Port')
                slave_id = plc_conf.getint('SlaveId')
                start_addr = plc_conf.getint('StartAddr')
                # 启动 PLC 线程
                self.plc_thread = PlcWorker(
                    section=self.current_section, host=host, port=port, slave_id=slave_id, start_addr=start_addr
                )
                # 信号连接
                self.plc_thread.logMessage.connect(self.on_log_message)
                self.plc_thread.start()
                # 从 INI 读取 Camera 配置
                cam_conf = config['Camera']
                index = cam_conf.getint('Index', fallback=1)
                timeout = cam_conf.getint('Timeout', fallback=3000)
                # 启动 Camera 线程
                self.cam_thread = CameraWorker(
                    section=self.current_section,
                    index=index, timeout=timeout,
                    save_image=self.save_image
                )
                # 信号连接
                self.cam_thread.frameReady.connect(self.on_frame)
                self.cam_thread.statusCheck.connect(self.on_check)
                self.cam_thread.coordReady.connect(self.plc_thread.send_coord)
                self.cam_thread.logMessage.connect(self.on_log_message)
                self.cam_thread.start()
            except Exception as e:
                self.on_log_message(f"[{self.current_section}] 连接相机失败，失败原因：{e}")
                self.btnConnectCamera.setText("连接相机")
                self.labelCameraStatus.setText("相机状态： 未连接")
                self.labelCameraStatus.setStyleSheet("color:red;font-size:16px;")
        self.btnConnectCamera.setEnabled(True)
        self.btnConnectCamera.setFocus()

    def on_log_message(self, msg: str):
        """
        接收各线程日志信号：
        - 添加到 QListWidget
        - 写入当天 rolling log 文件
        """
        now = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        line = f"{now}  {msg}"
        self.listLogs.addItem(line)
        # 控制最大行数
        while self.listLogs.count() > self.MAX_LOG_ENTRIES:
            old = self.listLogs.takeItem(0)
            del old
        self.listLogs.scrollToBottom()
        # 分日期切换日志文件
        today = datetime.date.today()
        if today != self.log_date:
            self.log_date = today
            self.log_name = f"{today.isoformat()}.log"
        try:
            self.log_file = open(os.path.join(self.logs_dir, self.log_name), 'a', encoding='utf-8')
            # 写到文件并 flush
            self.log_file.write(line + "\n")
            self.log_file.flush()
            self.log_file.close()
        finally:
            pass

    def on_mode_changed_combo(self, index: int):
        """ComboBox 模式切换槽，按选中索引加载不同节"""
        if index < 0 or index >= len(self.modes):
            return
        section = self.modes[index]
        # 更新当前节并重建参数区
        config = load_ini()
        self.current_section = section
        # 更新线程读取的节
        if self.cam_thread and self.cam_thread.isRunning():
            self.cam_thread.set_section(self.current_section)
        if self.plc_thread and self.plc_thread.isRunning():
            self.plc_thread.set_section(self.current_section)

        clear_layout(self.gridConfig)
        # 根据模式绘制参数项目
        if self.skipp_login:
            exclude = ['ui_offest_x', 'ui_offest_z']
            items = [item for item in list(config[self.current_section].items()) if item[0] in exclude]
        else:
            items = list(config[self.current_section].items())
        n = len(items)
        # 计算网格行列
        cols = math.ceil(math.sqrt(n))
        rows = math.ceil(n / cols)
        # 遍历参数
        for idx, (key, val) in enumerate(items):
            r = idx % rows
            c = idx // rows
            lbl = QLabel(f"{key.replace('_', ' ').capitalize()}:")
            edit = QLineEdit(val)
            edit.setMaximumWidth(320)
            self._edits[(self.current_section, key)] = edit
            # 实时写回 INI
            edit.textChanged.connect(
                lambda text, s=self.current_section, k=key: on_param_changed(s, k, text)
            )
            self.gridConfig.addWidget(lbl, r, c * 2, Qt.AlignRight | Qt.AlignVCenter)
            self.gridConfig.addWidget(edit, r, c * 2 + 1, Qt.AlignLeft | Qt.AlignVCenter)

    def resizeEvent(self, event):
        """
        窗口大小改变：保持 imageView 图像自适应
        """
        if not self._scene.sceneRect().isEmpty():
            self.graphicsView.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)
        super().resizeEvent(event)

    def closeEvent(self, event):
        """
        程序关闭：先停止后台线程，再退出应用
        """
        if self.cam_thread:
            try:
                self.cam_thread.stop()
            finally:
                pass
        if self.plc_thread:
            try:
                self.plc_thread.stop()
            finally:
                pass
        super().closeEvent(event)


if __name__ == '__main__':
    app = QApplication([])
    dlg = LoginDialog()
    if dlg.exec() == QDialog.Accepted:
        # 登录或跳过，打开主窗口
        w = MainWindow(dlg.skipped)
        w.showMaximized()
        sys.exit(app.exec())
