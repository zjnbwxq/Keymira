<<<<<<< HEAD
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                             QHBoxLayout, QLabel, QStackedWidget, QFrame,
                             QSlider, QCheckBox, QComboBox, QLineEdit, QColorDialog, QGridLayout, QToolTip, QTabWidget)
from PyQt5.QtCore import Qt, QSize, QTimer, QMetaObject, Q_ARG, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont, QColor, QPainter, QPainterPath, QIcon, QPixmap, QCursor
import os
import traceback

class MainWindow(QMainWindow):
    save_settings_signal = pyqtSignal()
    
    def __init__(self, keyboard_listener, style_manager):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(720, 916)  # 360 * 2, 458 * 2
        self.stats_label = QLabel("按键次数: 0, 单词数: 0")
        self.icons = self.load_icons()
        self.keyboard_listener = keyboard_listener
        self.style_manager = style_manager
        self.setup_ui()
        self.layout().addWidget(self.stats_label)  # 确保将标签添加到布局中

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

        title_bar = self.create_title_bar()
        main_layout.addWidget(title_bar)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        tab_bar = self.create_tab_bar()
        content_layout.addWidget(tab_bar)

        self.content_widget = QStackedWidget()
        self.content_widget.addWidget(self.create_settings_tab())
        self.content_widget.addWidget(self.create_vision_tab())
        self.content_widget.addWidget(self.create_personal_tab())
        content_layout.addWidget(self.content_widget)

        main_layout.addWidget(content_widget)

        self.setCentralWidget(main_widget)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #D9D9D9;
                border-radius: 20px;
            }
        """)

    def create_title_bar(self):
        title_bar = QWidget()
        title_bar.setFixedHeight(100)  # 50 * 2
        main_layout = QHBoxLayout(title_bar)
        main_layout.setContentsMargins(20, 10, 20, 10)

        # 左侧布局（logo和标题）
        left_layout = QHBoxLayout()
        
        # 添加logo
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'logo.png')
        if os.path.exists(logo_path):
            logo_label = QLabel()
            logo_pixmap = QPixmap(logo_path).scaled(57, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
            left_layout.addWidget(logo_label)
        else:
            print(f"警告：logo文件 {logo_path} 不存在")

        # 添加标题
        title_label = QLabel("Keymira")
        title_label.setFont(QFont("Noto Sans TC", 20, QFont.Bold))  
        left_layout.addWidget(title_label)

        main_layout.addLayout(left_layout)
        main_layout.addStretch()

        # 右侧布局（关闭按钮）
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建关闭按钮
        close_button = self.create_circle_button("×", "#FF6B6B", 34) 
        close_button.clicked.connect(self.close)
        
        # 添加一个顶部的弹簧来将按钮推到顶部
        right_layout.addSpacing(20)  # 10 * 2 (考虑2倍DPI缩放)
        right_layout.addWidget(close_button, alignment=Qt.AlignRight)
        right_layout.addStretch()

        main_layout.addLayout(right_layout)

        return title_bar

    def create_circle_button(self, text, color, size):
        button = QPushButton(text)
        button.setFixedSize(size, size)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border-radius: {size // 2}px;
                font-size: {size // 2}px;
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
        tab_layout = QHBoxLayout(tab_bar)
        tab_layout.setContentsMargins(20, 10, 20, 10)

        for icon_name in ["setting", "vision", "user"]:
            button = QPushButton()
            button.setObjectName(f"{icon_name}_button")
            button.setFixedSize(80, 80)
            button.setIcon(QIcon(self.icons[icon_name][0]))
            button.setIconSize(QSize(40, 40))
            button.clicked.connect(lambda checked, name=icon_name: self.switch_to_tab(name))
            tab_layout.addWidget(button)

        return tab_bar

    def change_tab(self, index):
        if hasattr(self, 'content_widget'):
            self.content_widget.setCurrentIndex(index)
        tab_bar = self.findChild(QWidget, "tab_bar")
        if tab_bar:
            for i in range(3):  # 假设有3个选项卡
                tab_container = tab_bar.findChild(QWidget, f"tab_container_{i}")
                if tab_container:
                    if i == index:
                        tab_container.setStyleSheet("""
                            background-color: rgba(0, 0, 0, 10);
                        """)
                    else:
                        tab_container.setStyleSheet("""
                            background-color: transparent;
                        """)

    def create_styled_checkbox(self):
        checkbox = QCheckBox()
        checkbox.setStyleSheet("""
            QCheckBox::indicator {
                width: 30px;
                height: 30px;
                border-radius: 15px;
            }
            QCheckBox::indicator:unchecked {
                background-color: #FFFFFF;
                border: 2px solid #CCCCCC;
            }
            QCheckBox::indicator:checked {
                background-color: #4CAF50;
                border: 2px solid #4CAF50;
            }
        """)
        return checkbox

    def create_styled_slider(self, min_value, max_value, unit=""):
        slider = QSlider(Qt.Horizontal)
        slider.setFixedWidth(400)
        slider.setMinimum(min_value)
        slider.setMaximum(max_value)
        slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 20px;
                background: #FFFFFF;
                margin: 0px;
                border-radius: 10px;
            }
            QSlider::handle:horizontal {
                background: #4CAF50;
                border: 1px solid #4CAF50;
                width: 40px;
                height: 40px;
                margin: -10px 0;
                border-radius: 20px;
            }
            QSlider::sub-page:horizontal {
                background: #4CAF50;
                border-radius: 10px;
            }
        """)
        
        def show_tooltip(value):
            QToolTip.showText(QCursor.pos(), f"{value}{unit}", slider)

        slider.valueChanged.connect(show_tooltip)
        slider.sliderMoved.connect(show_tooltip)

        return slider

    def open_color_dialog(self, text):
        color = QColorDialog.getColor()
        if color.isValid():
            if text == "悬浮窗颜色":
                self.key_display.set_window_color(color)
            elif text == "字体颜色":
                self.key_display.set_font_color(color)
            self.vision_color_buttons[text].setStyleSheet(f"background-color: {color.name()};")

    def create_settings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("设置标签页内容"))
        return tab

    def create_personal_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("个人签页内容"))
        return tab

    def create_vision_tab(self):
        tab = QWidget()
        layout = QGridLayout(tab)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # 创建复选框
        checkboxes = [
            "顯示普通鍵", "顯示修飾鍵",
            "顯示組合鍵", "顯示小鍵盤",
            "顯示F1~F12", "顯示特殊鍵"
        ]
        self.vision_checkboxes = {}
        for i, text in enumerate(checkboxes):
            label = QLabel(text)
            label.setFont(QFont("Noto Sans TC", 12, QFont.Bold))
            checkbox = self.create_styled_checkbox()
            checkbox.stateChanged.connect(lambda state, text=text: self.on_vision_checkbox_changed(text, state))
            row = i // 2
            col = (i % 2) * 2
            layout.addWidget(label, row, col)
            layout.addWidget(checkbox, row, col + 1, Qt.AlignRight)
            self.vision_checkboxes[text] = checkbox

        # 创建滑块
        sliders = [
            ("字體大小", 5, 60, ""),
            ("淡入時長", 200, 2000, "ms"),
            ("淡出時長", 200, 2000, "ms")
        ]
        self.vision_sliders = {}
        for i, (slider_text, min_value, max_value, unit) in enumerate(sliders):
            label = QLabel(slider_text)
            label.setFont(QFont("Noto Sans TC", 12, QFont.Bold))
            
            slider = self.create_styled_slider(min_value, max_value, unit)
            slider.valueChanged.connect(lambda value, text=slider_text: self.on_vision_slider_changed(text, value))
            
            layout.addWidget(label, 3 + i, 0)
            layout.addWidget(slider, 3 + i, 1, 1, 3)
            
            self.vision_sliders[slider_text] = slider

        # 创建颜色选择器和其他选项
        color_items = [
            ("懸浮窗顏色", "懸浮窗固定"), 
            ("字體顏色", "圖像模式")
        ]
        self.vision_color_buttons = {}
        self.vision_option_checkboxes = {}

        for i, (color_text, option_text) in enumerate(color_items):
            color_label = QLabel(color_text)
            color_label.setFont(QFont("Noto Sans TC", 12, QFont.Bold))
            color_button = QPushButton()
            color_button.setFixedSize(30, 30)
            color_button.setStyleSheet("""
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #FF0000, stop:0.25 #00FF00,
                                            stop:0.5 #0000FF, stop:0.75 #FFFF00,
                                            stop:1 #00FFFF);
                border-radius: 15px;
            """)
            color_button.clicked.connect(lambda checked, text=color_text: self.open_color_dialog(text))
            
            option_label = QLabel(option_text)
            option_label.setFont(QFont("Noto Sans TC", 12, QFont.Bold))
            option_checkbox = self.create_styled_checkbox()
            option_checkbox.stateChanged.connect(lambda state, text=option_text: self.on_vision_option_changed(text, state))
            
            layout.addWidget(color_label, 6 + i, 0)
            layout.addWidget(color_button, 6 + i, 1, Qt.AlignLeft)
            layout.addWidget(option_label, 6 + i, 2, Qt.AlignLeft)
            layout.addWidget(option_checkbox, 6 + i, 3, Qt.AlignRight)

            self.vision_color_buttons[color_text] = color_button
            self.vision_option_checkboxes[option_text] = option_checkbox

        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(3, 1)

        # 连接滑块和复选框的信号到保存设置的槽
        for slider in self.vision_sliders.values():
            slider.valueChanged.connect(self.save_settings_signal.emit)
        for checkbox in self.vision_checkboxes.values():
            checkbox.stateChanged.connect(self.save_settings_signal.emit)

        return tab

    def on_vision_checkbox_changed(self, text, state):
        print(f"复选框 '{text}' 状态改变为: {'选中' if state == Qt.Checked else '未选中'}")
        # 在这里添加更多的逻辑来处理复选框状态变化

    def on_vision_slider_changed(self, text, value):
        print(f"滑块 '{text}' 值改变为: {value}")
        # 在这里添加更多的逻辑来处理滑块值变化

    def on_vision_option_changed(self, text, state):
        print(f"选项 '{text}' 状态改变为: {'选中' if state == Qt.Checked else '未选中'}")
        # 在这里添加更多的逻辑来处理选项状态变化

    def open_color_dialog(self, text):
        color = QColorDialog.getColor()
        if color.isValid():
            if text == "悬浮窗颜色":
                self.key_display.set_window_color(color)
            elif text == "字体颜色":
                self.key_display.set_font_color(color)
            self.vision_color_buttons[text].setStyleSheet(f"background-color: {color.name()};")

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

    @pyqtSlot(dict)
    def update_stats_display(self, stats):
        try:
            if hasattr(self, 'stats_label'):
                self.stats_label.setText(f"按键次数: {stats.get('key_count', 0)}, 单词数: {stats.get('word_count', 0)}")
            else:
                print("警告：stats_label 不存在")
        except Exception as e:
            print(f"更新统计显示时出错: {e}")
            print(traceback.format_exc())

    def safe_update_stats_display(self, stats):
        try:
            QTimer.singleShot(0, lambda: self.update_stats_display(stats))
        except Exception as e:
            print(f"安全更新统计显示时出错: {e}")
            print(traceback.format_exc())

    def on_checkbox_changed(self, text, state):
        is_checked = state == Qt.Checked
        if text == "显示普通键":
            self.key_display.set_show_normal_keys(is_checked)
        elif text == "显示修飾键":
            self.key_display.set_show_modifier_keys(is_checked)
        elif text == "显示组合键":
            self.key_display.set_show_combination_keys(is_checked)
        elif text == "显示小键盘":
            self.key_display.set_show_numpad(is_checked)
        elif text == "显示F1~F12":
            self.key_display.set_show_function_keys(is_checked)
        elif text == "显示特殊键位":
            self.key_display.set_show_special_keys(is_checked)

    def on_slider_changed(self, text, value):
        if text == "字体大小":
            self.key_display.set_font_size(value)
        elif text == "显示时长":
            self.key_display.set_display_duration(value)
        elif text == "淡出时长":
            self.key_display.set_fade_out_duration(value)

    def on_extra_checkbox_changed(self, text, state):
        is_checked = state == Qt.Checked
        if text == "悬浮窗固定":
            self.key_display.set_window_fixed(is_checked)
        elif text == "图像模式":
            self.key_display.set_image_mode(is_checked)

    def switch_to_tab(self, icon_name):
        tab_index = {"setting": 0, "vision": 1, "user": 2}.get(icon_name, -1)
        if tab_index != -1:
            self.content_widget.setCurrentIndex(tab_index)
            # 更新图标状态
            for name in ["setting", "vision", "user"]:
                button = self.findChild(QPushButton, f"{name}_button")
                if button:
                    button.setIcon(QIcon(self.icons[name][1 if name == icon_name else 0]))
        else:
            print(f"警告：找不到 {icon_name} 对应的选项卡")












=======
>>>>>>> parent of 42d14a8 (实现基本前后端)
