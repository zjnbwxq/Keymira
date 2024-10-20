from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QLineEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class UserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新增用户")
        self.setFixedSize(400, 200)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # 用户名输入
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        self.username_input.setFont(QFont("Noto Sans TC Regular", 14))
        layout.addWidget(self.username_input)

        # 确认按钮
        confirm_button = QPushButton("确认")
        confirm_button.setFont(QFont("Noto Sans TC Regular", 14))
        confirm_button.setFixedSize(100, 40)
        confirm_button.clicked.connect(self.accept)
        layout.addWidget(confirm_button, alignment=Qt.AlignRight)

    def get_user_data(self):
        return self.username_input.text()
