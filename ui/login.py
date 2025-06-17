# -*- coding: utf-8 -*-
"""

LoginDialog：登录/跳过/修改密码对话框
在主程序入口调用登录对话框，验证通过后显示主窗口

修改人： hnchen
修改时间： 2025/06/17
"""
from PySide6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFormLayout,
    QMessageBox, QInputDialog, QDialogButtonBox,
    QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt
from util.file import (load_ini, write_ini)
from util.crypto import (decrypt, encrypt)

# === 统一样式表，用于所有对话框 ===
_DLG_STYLE = """
QDialog { background: #f0f2f5; }
QLabel#title { font-size:20px; font-weight:bold; color:#2c3e50; }
QLabel { font-size:16px; }
QLineEdit { height:30px; font-size:14px; padding:4px; border:1px solid #bdc3c7; border-radius:4px; }
QPushButton { height: 32px; font-size: 14px; padding: 0 12px; border-radius: 4px; }
QPushButton#btnPrimary { background-color: #3498db; color: white; }
QPushButton#btnSecondary { background-color: transparent; color: #3498db; }
QPushButton:hover#btnPrimary { background-color: #2980b9; }
QPushButton:hover#btnSecondary { color: #2980b9; }
"""


def make_bold_label(text: str):
    lbl = QLabel(f"{text}：")
    lbl.setStyleSheet('font-size:16px; font-weight:bold;')
    return lbl

# === 自定义对话框基类 ===
def show_custom_message(parent, title, text, icon=QMessageBox.Warning):
    """统一样式的消息框，按钮文字为“确认”"""
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.setIcon(icon)
    msg.setStandardButtons(QMessageBox.Ok)
    ok_btn = msg.button(QMessageBox.Ok)
    # 设置按钮对象名以应用统一样式
    ok_btn.setObjectName('btnPrimary')
    ok_btn.setText('确认')
    msg.setStyleSheet(_DLG_STYLE)
    msg.exec()

# === 自定义输入对话框函数 ===
def get_custom_input(parent, window_title, label, echo_mode=QLineEdit.Normal):
    """统一样式的输入框，按钮文字为“确认”“取消"""
    dlg = QDialog(parent)
    # 调整对话框大小
    dlg.setFixedSize(320, 110)
    dlg.setWindowTitle(window_title)
    dlg.setStyleSheet(_DLG_STYLE)
    dlg.setWindowFlags((Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
                       & ~Qt.WindowContextHelpButtonHint)
    # 主垂直布局
    vbox = QVBoxLayout(dlg)
    # 表单布局：label 与 edit 同一行
    form = QFormLayout()
    form.setLabelAlignment(Qt.AlignRight)
    edit = QLineEdit()
    edit.setEchoMode(echo_mode)
    edit.setPlaceholderText(label)
    form.addRow(make_bold_label(label), edit)
    # 按钮区域
    btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    ok = btn_box.button(QDialogButtonBox.Ok)
    ok.setObjectName('btnPrimary')
    ok.setText('确认')
    cancel = btn_box.button(QDialogButtonBox.Cancel)
    cancel.setObjectName('btnSecondary')
    cancel.setText('取消')
    btn_box.accepted.connect(dlg.accept)
    btn_box.rejected.connect(dlg.reject)
    # 将form和按钮添加到主布局
    vbox.addLayout(form)
    vbox.addStretch()
    vbox.addWidget(btn_box)
    dlg.setLayout(vbox)
    # 执行对话框并返回输入与确认状态
    result = dlg.exec()
    return edit.text(), result == QDialog.Accepted

# === 登录对话框 ===
class LoginDialog(QDialog):
    """
    登录对话框：
      - 输入用户名/密码
    按钮：登录、跳过登录、修改密码
    配置文件：settings.ini 内 [Auth] 节保存加密后的密码
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("系统登录")
        self.setFixedSize(360, 220)

        # 加载并应用 QSS
        self.setStyleSheet("""
                    QDialog { background: #f0f2f5; }
                    QLabel#title { font-size: 20px; font-weight: bold; color: #2c3e50; }
                    QLineEdit { height: 30px; font-size: 14px; padding: 4px; border: 1px solid #bdc3c7; border-radius: 4px; }
                    QPushButton { height: 32px; font-size: 14px; padding: 0 12px; border-radius: 4px; }
                    QPushButton#btnPrimary { background-color: #3498db; color: white; }
                    QPushButton#btnSecondary { background-color: transparent; color: #3498db; }
                    QPushButton:hover#btnPrimary { background-color: #2980b9; }
                    QPushButton:hover#btnSecondary { color: #2980b9; }
                """)
        # 标题
        title = QLabel("安全登录", objectName='title', alignment=Qt.AlignCenter)
        # 表单布局
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        self.user_edit = QLineEdit()
        self.user_edit.setPlaceholderText("用户名")
        self.pwd_edit = QLineEdit()
        self.pwd_edit.setEchoMode(QLineEdit.Password)
        self.pwd_edit.setPlaceholderText("密码")
        form_layout.addRow(make_bold_label('用户名'), self.user_edit)
        form_layout.addRow(make_bold_label('密码'), self.pwd_edit)
        # 按钮布局
        btn_layout = QHBoxLayout()
        btn_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.btn_login = QPushButton("登录", objectName='btnPrimary')
        self.btn_skip = QPushButton("跳过", objectName='btnSecondary')
        self.btn_change = QPushButton("修改密码", objectName='btnSecondary')
        btn_layout.addWidget(self.btn_login)
        btn_layout.addWidget(self.btn_skip)
        btn_layout.addWidget(self.btn_change)
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(title)
        main_layout.addSpacing(15)
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        main_layout.addLayout(btn_layout)
        main_layout.setContentsMargins(20, 20, 20, 20)
        # 信号
        self.btn_login.clicked.connect(self.do_login)
        self.btn_change.clicked.connect(self.change_password)
        # 跳过登录，记录跳过标志并关闭对话框
        self.skipped = False
        self.btn_skip.clicked.connect(self.skip_login)

    def skip_login(self):
        """跳过登录，标记并关闭对话框"""
        self.skipped = True
        self.accept()

    def load_password(self) -> str:
        # 解析密码
        cfg = load_ini()
        enc = cfg.get('Auth', 'password', fallback='')
        if enc == 'admin':
            return enc
        else:
            return decrypt(enc)

    def save_password(self, new_pwd: str):
        # 保存密码
        enc = encrypt(new_pwd)
        write_ini('Auth', 'password', 'admin' if enc == '' else enc)
        show_custom_message(self, '提示', '密码已更新', icon=QMessageBox.Information)

    def do_login(self):
        # 登录
        usr = self.user_edit.text().strip()
        pwd = self.pwd_edit.text()
        if usr == 'admin' and pwd == self.load_password():
            self.accept()
        else:
            show_custom_message(self, '错误', '用户名或密码错误')

    def change_password(self):
        # 验证旧密码
        old, ok1 = get_custom_input(self, '验证旧密码', '旧密码', echo_mode=QLineEdit.Password)
        if ok1:
            if old != self.load_password() :
                show_custom_message(self, '错误', '旧密码错误')
                return
            if old == self.load_password() :
                # 输入新密码
                new, ok2 = get_custom_input(self, '新密码', '新密码', echo_mode=QLineEdit.Password)
                if not ok2 or not new:
                    return
                # 确认密码
                confirm, ok3 = get_custom_input(self, '确认新密码', '请再次输入', echo_mode=QLineEdit.Password)
                if not ok3 or new != confirm:
                    show_custom_message(self, '错误', '两次输入不一致')
                    return
                    # 保存
                self.save_password(new)
