from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QLineEdit, QListWidget, QFrame, QWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon, QPixmap
import os

class UserManagementDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("用户")
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
        title = QLabel("用户")
        title.setFont(QFont("Noto Sans TC Regular", 24, QFont.Bold))
        title_layout.addWidget(title)
        title_layout.addStretch()

        close_button = QPushButton("×")
        close_button.setFixedSize(30, 30)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #FF6B6B;
                color: white;
                border-radius: 15px;
                font-size: 20px;
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
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "user_icon.png")
            user_pixmap = QPixmap(icon_path).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            user_icon.setPixmap(user_pixmap)
            icon_layout.addWidget(user_icon)
        icon_layout.addStretch()
        layout.addLayout(icon_layout)

        # 用户列表
        self.user_list = QListWidget()
        self.user_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.user_list)

        # 新用户输入
        self.new_user_input = QLineEdit()
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
            button.setFixedSize(30, 30)
            button.setFont(QFont("Noto Sans TC Regular", 16, QFont.Bold))
        self.add_button.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 15px;")
        self.remove_button.setStyleSheet("background-color: #F44336; color: white; border-radius: 15px;")
        button_layout.addStretch()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        layout.addLayout(button_layout)

        # 字体样式导入按钮
        self.import_font_button = QPushButton("字体样式导入")
        self.import_font_button.setStyleSheet("""
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
        layout.addWidget(self.import_font_button, alignment=Qt.AlignRight)

        main_layout.addWidget(main_widget)

        # 连接信号
        self.add_button.clicked.connect(self.add_user)
        self.remove_button.clicked.connect(self.remove_user)
        self.import_font_button.clicked.connect(self.import_font_style)

    def add_user(self):
        new_user = self.new_user_input.text().strip()
        if new_user:
            self.user_list.addItem(new_user)
            self.new_user_input.clear()

    def remove_user(self):
        current_item = self.user_list.currentItem()
        if current_item:
            self.user_list.takeItem(self.user_list.row(current_item))

    def import_font_style(self):
        # 实现字体样式导入逻辑
        pass

    def get_users(self):
        return [self.user_list.item(i).text() for i in range(self.user_list.count())]
