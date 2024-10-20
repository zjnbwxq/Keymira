from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QLineEdit, QFileDialog, QWidget)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap, QFont
import os
import shutil

class StyleImportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("自定义样式")
        self.setFixedSize(1000, 800)  # 增加窗口大小
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
                border-radius: 20px;
            }
        """)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(40)  # 增加间距
        layout.setContentsMargins(40, 40, 40, 40)  # 增加边距

        # 标题和关闭按钮
        title_layout = QHBoxLayout()
        title = QLabel("自定义样式")
        title.setFont(QFont("Noto Sans TC Regular", 32, QFont.Bold))  # 增加字体大小
        title_layout.addWidget(title)
        title_layout.addStretch()

        close_button = QPushButton("×")
        close_button.setFixedSize(60, 60)  # 增加按钮大小
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #FF6B6B;
                color: white;
                border-radius: 30px;
                font-size: 40px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF8888;
            }
        """)
        close_button.clicked.connect(self.reject)
        title_layout.addWidget(close_button)
        layout.addLayout(title_layout)

        # Logo
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")
        logo_pixmap = QPixmap(logo_path).scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # 增加logo大小
        logo_label.setPixmap(logo_pixmap)
        layout.addWidget(logo_label, alignment=Qt.AlignCenter)

        # 输入字段
        self.url_input = self.create_input_field("样式URL")
        self.style_path_input = self.create_input_field("样式路径", True)
        self.style_id_input = self.create_input_field("样式ID")
        self.font_path_input = self.create_input_field("字体路径", True)

        layout.addWidget(self.url_input)
        layout.addWidget(self.style_path_input)
        layout.addWidget(self.style_id_input)
        layout.addWidget(self.font_path_input)

        # 确认按钮
        self.confirm_button = QPushButton("确认")
        self.confirm_button.setFixedSize(200, 80)  # 增加按钮大小
        self.confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border-radius: 10px;
                font-weight: bold;
                font-size: 24px;
            }
            QPushButton:hover {
                background-color: #5AA0F2;
            }
        """)
        self.confirm_button.clicked.connect(self.accept)
        layout.addWidget(self.confirm_button, alignment=Qt.AlignRight)

        main_layout.addWidget(main_widget)

    def create_input_field(self, label_text, is_file_input=False):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel(label_text)
        label.setFixedWidth(160)  # 增加标签宽度
        label.setFont(QFont("Noto Sans TC Regular", 18))  # 增加字体大小
        layout.addWidget(label)

        line_edit = QLineEdit()
        line_edit.setFixedHeight(60)  # 增加输入框高度
        line_edit.setFont(QFont("Noto Sans TC Regular", 16))  # 增加字体大小
        layout.addWidget(line_edit)

        if is_file_input:
            browse_button = QPushButton("浏览")
            browse_button.setFixedSize(120, 60)  # 增加按钮大小
            browse_button.setFont(QFont("Noto Sans TC Regular", 16))  # 增加字体大小
            browse_button.clicked.connect(lambda: self.browse_file(line_edit))
            layout.addWidget(browse_button)

        return widget

    def browse_file(self, line_edit):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件")
        if file_path:
            destination_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "styles")
            os.makedirs(destination_folder, exist_ok=True)
            destination_path = os.path.join(destination_folder, os.path.basename(file_path))
            shutil.copy2(file_path, destination_path)
            line_edit.setText(destination_path)

    def get_style_data(self):
        return {
            "url": self.url_input.findChild(QLineEdit).text(),
            "style_path": self.style_path_input.findChild(QLineEdit).text(),
            "style_id": self.style_id_input.findChild(QLineEdit).text(),
            "font_path": self.font_path_input.findChild(QLineEdit).text()
        }
