from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,QWidget)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor
import os

class SpecialKeyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("特殊键位")
        self.setFixedSize(500, 600)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 主窗口
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
        title = QLabel("特殊鍵位")
        title.setFont(QFont("Noto Sans TC Regular", 16, QFont.Bold))
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

        # 键盘图像
        keyboard_label = QLabel()
        # 更新键盘图像的路径
        keyboard_image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "keyboard.png")
        keyboard_pixmap = QPixmap(keyboard_image_path).scaled(300, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        keyboard_label.setPixmap(keyboard_pixmap)
        layout.addWidget(keyboard_label, alignment=Qt.AlignCenter)

        # 表格
        self.table = QTableWidget(1, 3)
        self.table.setHorizontalHeaderLabels(["鍵位", "顯示名稱", "備註"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setItem(0, 0, QTableWidgetItem("Mouse2"))
        self.table.setItem(0, 1, QTableWidgetItem("侧2"))
        self.table.setItem(0, 2, QTableWidgetItem("鼠标侧键"))
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #E0E0E0;
                padding: 5px;
                border: none;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.table)

        # 在键盘上键入按钮
        self.input_button = QPushButton("在鍵盤上鍵入")
        self.input_button.setFixedHeight(40)
        self.input_button.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #D0D0D0;
            }
        """)
        layout.addWidget(self.input_button)

        # 添加和删除按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.add_button = QPushButton("+")
        self.remove_button = QPushButton("-")
        for button in [self.add_button, self.remove_button]:
            button.setFixedSize(30, 30)
            button.setFont(QFont("Noto Sans TC Regular", 16, QFont.Bold))
        self.add_button.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 15px;")
        self.remove_button.setStyleSheet("background-color: #F44336; color: white; border-radius: 15px;")
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        layout.addLayout(button_layout)

        # 确认按钮
        self.confirm_button = QPushButton("确认")
        self.confirm_button.setFixedSize(100, 40)
        self.confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5AA0F2;
            }
        """)
        layout.addWidget(self.confirm_button, alignment=Qt.AlignRight)

        main_layout.addWidget(main_widget)

        # 连接按钮信号
        self.add_button.clicked.connect(self.add_row)
        self.remove_button.clicked.connect(self.remove_row)
        self.confirm_button.clicked.connect(self.accept)
        self.input_button.clicked.connect(self.start_key_input)

    def add_row(self):
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)

    def remove_row(self):
        current_row = self.table.currentRow()
        if current_row > -1:
            self.table.removeRow(current_row)

    def start_key_input(self):
        # 这里添加键盘输入逻辑
        pass
