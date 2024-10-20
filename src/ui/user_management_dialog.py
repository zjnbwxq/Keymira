from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QLineEdit, QListWidget, QFrame, QWidget, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPixmap
import os

class UserManagementDialog(QDialog):
    user_added = pyqtSignal(str)
    user_removed = pyqtSignal(str)

    def __init__(self, data_processor, parent=None):
        super().__init__(parent)
        self.data_processor = data_processor
        self.setWindowTitle("用户管理")
        self.setFixedSize(500, 600)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_widget = QWidget(self)
        main_widget.setObjectName("mainWidget")
        main_widget.setStyleSheet("""
            #mainWidget {
                background-color: #F0F0F0;
                border-radius: 10px;
            }
        """)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # 标题和关闭按钮
        title_layout = QHBoxLayout()
        title = QLabel("用户管理")
        title.setFont(QFont("Noto Sans TC Regular", 18, QFont.Bold))  # 调整字体大小
        title_layout.addWidget(title)
        title_layout.addStretch()

        close_button = QPushButton("×")
        close_button.setFixedSize(25, 25)  # 调整按钮大小
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #FF6B6B;
                color: white;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF8888;
            }
        """)
        close_button.clicked.connect(self.reject)
        title_layout.addWidget(close_button)
        layout.addLayout(title_layout)

        # 用户图标
        icon_layout = QHBoxLayout()
        icon_layout.addStretch()
        for _ in range(2):
            user_icon = QLabel()
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "users.png")
            user_pixmap = QPixmap(icon_path).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            user_icon.setPixmap(user_pixmap)
            icon_layout.addWidget(user_icon)
        icon_layout.addStretch()
        layout.addLayout(icon_layout)

        # 用户列表
        self.user_list = QListWidget()
        self.user_list.setFont(QFont("Noto Sans TC Regular", 10))  # 设置字体大小
        self.user_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
            }
        """)
        self.update_user_list()
        layout.addWidget(self.user_list)

        # 新用户输入
        self.new_user_input = QLineEdit()
        self.new_user_input.setFont(QFont("Noto Sans TC Regular", 10))  # 设置字体大小
        self.new_user_input.setPlaceholderText("在此键入新用户")
        self.new_user_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        layout.addWidget(self.new_user_input)

        # 添加和删除按钮
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("+")
        self.remove_button = QPushButton("-")
        for button in [self.add_button, self.remove_button]:
            button.setFixedSize(25, 25)  # 调整按钮大小
            button.setFont(QFont("Noto Sans TC Regular", 12, QFont.Bold))  # 调整字体大小
        self.add_button.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 12px;")
        self.remove_button.setStyleSheet("background-color: #F44336; color: white; border-radius: 12px;")
        button_layout.addStretch()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        layout.addLayout(button_layout)

        # 确认按钮
        self.confirm_button = QPushButton("確認")
        self.confirm_button.setFont(QFont("Noto Sans TC Regular", 10))  # 设置字体大小
        self.confirm_button.setFixedSize(80, 30)  # 调整按钮大小
        self.confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #5AA0F2;
            }
        """)
        layout.addWidget(self.confirm_button, alignment=Qt.AlignRight)

        main_layout.addWidget(main_widget)

        # 连接信号
        self.add_button.clicked.connect(self.add_user)
        self.remove_button.clicked.connect(self.remove_user)
        self.confirm_button.clicked.connect(self.accept)

    def update_user_list(self):
        self.user_list.clear()
        users = self.data_processor.get_user_list()
        self.user_list.addItems(users)

    def add_user(self):
        new_user = self.new_user_input.text().strip()
        if new_user:
            if self.data_processor.add_user(new_user):
                self.update_user_list()
                self.new_user_input.clear()
                self.user_added.emit(new_user)
                self.accept()  # 添加用户后自动关闭对话框
            else:
                QMessageBox.warning(self, "错误", "用户名已存在或无效")
        else:
            QMessageBox.warning(self, "错误", "请输入有效的用户名")

    def remove_user(self):
        current_item = self.user_list.currentItem()
        if current_item:
            username = current_item.text()
            if username != "guest":
                if self.data_processor.remove_user(username):
                    self.update_user_list()
                    self.user_removed.emit(username)
                else:
                    QMessageBox.warning(self, "错误", "无法删除用户")
            else:
                QMessageBox.warning(self, "错误", "不能删除 guest 用户")
        else:
            QMessageBox.warning(self, "错误", "请选择要删除的用户")

    def get_users(self):
        return [self.user_list.item(i).text() for i in range(self.user_list.count())]
