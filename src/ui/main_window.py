from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                             QHBoxLayout, QLabel, QStackedWidget, QFrame,
                             QSlider, QCheckBox, QComboBox, QLineEdit, QColorDialog)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QPainter, QPainterPath, QIcon, QPixmap
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(720, 916)  # 360 * 2, 458 * 2
        self.stats_label = None
        self.icons = self.load_icons()
        self.setup_ui()

    def load_icons(self):
        icons = {}
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
        icon_files = {
            'setting': ['Setting_none.png', 'setting.png'],
            'vision': ['vision_none.png', 'vision.png'],
            'user': ['user_none.png', 'User.png']
        }
        for icon_name, file_names in icon_files.items():
            icons[icon_name] = []
            for file_name in file_names:
                icon_file = os.path.join(icon_path, file_name)
                if os.path.exists(icon_file):
                    icons[icon_name].append(QPixmap(icon_file))
                else:
                    print(f"警告：图标文件 {icon_file} 不存在")
        return icons

    def setup_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建标题栏
        title_bar = self.create_title_bar()
        main_layout.addWidget(title_bar)

        # 创建自定义标签栏
        tab_bar = self.create_tab_bar()
        main_layout.addWidget(tab_bar)

        # 创建内容区域
        self.content_widget = QStackedWidget()
        self.content_widget.addWidget(self.create_display_tab())
        self.content_widget.addWidget(self.create_settings_tab())
        self.content_widget.addWidget(self.create_personal_tab())
        main_layout.addWidget(self.content_widget)

        self.setCentralWidget(main_widget)

        # 设置整体样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #D9D9D9;
                border-radius: 20px;
            }
        """)

    def create_title_bar(self):
        title_bar = QWidget()
        title_bar.setFixedHeight(100)  # 50 * 2
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(20, 10, 20, 10)

        # 添加logo
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'logo.png')
        if os.path.exists(logo_path):
            logo_label = QLabel()
            logo_pixmap = QPixmap(logo_path).scaled(57, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
            title_bar_layout.addWidget(logo_label)
        else:
            print(f"警告：logo文件 {logo_path} 不存在")

        # 添加标题
        title_label = QLabel("Keymira")
        title_label.setFont(QFont("Noto Sans TC", 20, QFont.Bold))  
        title_bar_layout.addWidget(title_label)

        title_bar_layout.addStretch()

        # 创建最小化和关闭按钮
        minimize_button = self.create_circle_button("－", "#4CAF50")
        close_button = self.create_circle_button("×", "#FF6B6B")
        
        title_bar_layout.addWidget(minimize_button)
        title_bar_layout.addWidget(close_button)

        return title_bar

    def create_circle_button(self, text, color):
        button = QPushButton(text)
        button.setFixedSize(60, 60)  # 30 * 2
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border-radius: 30px;
                font-size: 40px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
            }}
        """)
        return button

    def darken_color(self, color):
        c = QColor(color)
        h, s, v, _ = c.getHsv()
        return QColor.fromHsv(h, s, max(0, v - 20), 255).name()

    def create_tab_bar(self):
        tab_bar = QWidget()
        tab_bar.setObjectName("tab_bar")
        tab_bar.setFixedHeight(200)  # 100 * 2
        tab_bar.setStyleSheet("background-color: #FFFFFF; border-radius: 20px;")
        tab_layout = QHBoxLayout(tab_bar)

        tab_names = ['setting', 'vision', 'user']
        for i, name in enumerate(tab_names):
            tab_button = QPushButton()
            tab_button.setFixedSize(96, 96)  # 80 * 2
            icon = QIcon(self.icons[name][0])
            tab_button.setIcon(icon)
            tab_button.setIconSize(QSize(96, 96))  # 80 * 2
            tab_button.setStyleSheet("background-color: transparent; border: none;")
            tab_button.clicked.connect(lambda checked, index=i: self.change_tab(index))
            tab_layout.addWidget(tab_button)

        return tab_bar

    def change_tab(self, index):
        self.content_widget.setCurrentIndex(index)
        self.update_tab_icons(index)

    def update_tab_icons(self, selected_index):
        tab_bar = self.findChild(QWidget, "tab_bar")
        if tab_bar:
            tab_names = ['setting', 'vision', 'user']
            for i, button in enumerate(tab_bar.findChildren(QPushButton)):
                icon_index = 1 if i == selected_index and len(self.icons[tab_names[i]]) > 1 else 0
                button.setIcon(QIcon(self.icons[tab_names[i]][icon_index]))

    def create_display_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("显示标签页内容"))
        return tab

    def create_settings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("设置标签页内容"))
        return tab

    def create_personal_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("个人标签页内容"))
        return tab

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 20, 20)

        painter.setClipPath(path)
        painter.fillPath(path, QColor("#D9D9D9"))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
