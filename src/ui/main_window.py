from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                             QHBoxLayout, QLabel, QSlider, QCheckBox, QColorDialog, QGridLayout, QSpacerItem, QStackedWidget, QComboBox, QDialog, QFrame, QFileDialog, QInputDialog, QMessageBox)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPainter, QPainterPath, QIcon, QPixmap, QLinearGradient, QFontDatabase, QDesktopServices
from PyQt5.QtCore import QUrl
import os
from .style_import_dialog import StyleImportDialog
from .user_management_dialog import UserManagementDialog

class MainWindow(QMainWindow):
    import_data_signal = pyqtSignal(str)
    export_data_signal = pyqtSignal(str)
    add_user_signal = pyqtSignal(str)
    update_floating_window_signal = pyqtSignal(dict)  # 添加这行

    def __init__(self, data_processor):
        super().__init__()
        self.data_processor = data_processor
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(720, 916)  # 360 * 2, 458 * 2
        self.icons = self.load_icons()
        self.load_fonts()
        self.current_page = 0
        self.stacked_widget = QStackedWidget()
        self.current_user = "guest"
        self.user_settings = {}
        self.load_user_settings()
        self.setup_ui()

    def load_icons(self):
        # 保持原有的图标加载逻辑不变
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

    def load_fonts(self):
        font_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'NotoSansTC-Bold.otf')
        QFontDatabase.addApplicationFont(font_path)

    def setup_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建标题栏
        title_bar = self.create_title_bar()
        main_layout.addWidget(title_bar)

        # 创建内容区域
        content_widget = self.create_content_widget()
        main_layout.addWidget(content_widget)

        self.setCentralWidget(main_widget)

        # 设置整体样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #D9D9D9;
                border-radius: 20px;
            }
            QLabel {
                color: #000000;
                font-size: 36px;
                font-family: 'Noto Sans TC';
                font-weight: bold;
            }
            QCheckBox {
                color: #000000;
                font-size: 36px;
                font-family: 'Noto Sans TC';
                font-weight: bold;
            }
            QCheckBox::indicator {
                width: 40px;
                height: 40px;
                border-radius: 20px;
                border: none;
            }
            QCheckBox::indicator:unchecked {
                background-color: #FFFFFF;
            }
            QCheckBox::indicator:checked {
                background-color: #4CAF50;
            }
            QSlider::groove:horizontal {
                background: #FFFFFF;
                height: 20px;
                border-radius: 10px;
            }
            QSlider::handle:horizontal {
                background: #4CAF50;
                width: 40px;
                margin: -10px 0;
                border-radius: 20px;
            }
        """)

    def create_title_bar(self):
        title_bar = QWidget()
        title_bar.setFixedHeight(80)
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(12, 12, 12, 12)

        # 添logo和标题
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'logo.png')
        logo_pixmap = QPixmap(logo_path).scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)
        title_bar_layout.addWidget(logo_label)

        title_label = QLabel("Keymira")
        title_label.setFont(QFont("Noto Sans TC", 38, QFont.Bold))
        title_bar_layout.addWidget(title_label)

        title_bar_layout.addStretch()

        # 创建关闭按钮
        close_button = self.create_circle_button("×", "#FF6B6B")
        close_button.clicked.connect(self.close)  # 连接关闭按钮到 close 方法
        title_bar_layout.addWidget(close_button, alignment=Qt.AlignVCenter)

        return title_bar

    def create_circle_button(self, text, color):
        button = QPushButton(text)
        button.setFixedSize(34, 34)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border-radius: 17px;
                font-size: 20px;
                font-weight: bold;
                font-family: 'Noto Sans TC';
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

    def create_content_widget(self):
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 0, 20, 20)
        content_layout.setSpacing(30)

        content_layout.addSpacing(10)

        # 创建图标栏
        icon_bar = self.create_icon_bar()
        content_layout.addWidget(icon_bar, alignment=Qt.AlignCenter)

        # 添加页面到 stacked_widget
        self.stacked_widget.addWidget(self.create_vision_page())
        self.stacked_widget.addWidget(self.create_settings_page())
        self.stacked_widget.addWidget(self.create_user_page())
        content_layout.addWidget(self.stacked_widget)

        return content_widget

    def create_icon_bar(self):
        icon_bar = QWidget()
        icon_layout = QHBoxLayout(icon_bar)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setSpacing(40)

        icon_names = ['vision', 'setting', 'user']  # 调整顺序
        self.icon_buttons = []
        for i, name in enumerate(icon_names):
            button = QPushButton()
            button.setFixedSize(96, 96)
            button.setStyleSheet("background-color: transparent; border: none;")
            button.clicked.connect(lambda checked, index=i: self.switch_page(index))
            icon_layout.addWidget(button)
            self.icon_buttons.append(button)

        self.update_icon_states()  # 初始化图标状态
        return icon_bar

    def switch_page(self, index):
        self.current_page = index
        self.stacked_widget.setCurrentIndex(index)
        self.update_icon_states()

    def update_icon_states(self):
        icon_names = ['vision', 'setting', 'user']  # 确保这里的顺序与 create_icon_bar 中一致
        for i, button in enumerate(self.icon_buttons):
            icon = self.icons[icon_names[i]][1 if i == self.current_page else 0]
            button.setIcon(QIcon(icon))
            button.setIconSize(QSize(96, 96))

    def create_vision_page(self):
        vision_widget = QWidget()
        layout = QVBoxLayout(vision_widget)

        # 创建显示选项
        display_options = ["顯示普通鍵", "顯示修飾鍵", "顯示組合鍵", "顯示小鍵盤", "顯示F1~F12"]
        options_grid = QGridLayout()
        options_grid.setVerticalSpacing(25)
        options_grid.setColumnStretch(0, 1)
        options_grid.setColumnStretch(1, 0)
        options_grid.setColumnStretch(2, 1)
        options_grid.setColumnStretch(3, 0)
        for i, option in enumerate(display_options):
            label = QLabel(option)
            checkbox = QCheckBox()
            checkbox.setChecked(self.data_processor.get_user_settings(self.data_processor.current_user).get(f"display_{option}", True))
            checkbox.stateChanged.connect(lambda state, opt=option: self.update_display_option(opt, state))
            options_grid.addWidget(label, i // 2, (i % 2) * 2)
            options_grid.addWidget(checkbox, i // 2, (i % 2) * 2 + 1, Qt.AlignRight)
        layout.addLayout(options_grid)

        layout.addSpacing(20)

        # 创建滑动条选项
        slider_options = ["字體大小", "顯示時長", "淡出時長"]
        for option in slider_options:
            slider_layout = QHBoxLayout()
            slider_layout.addWidget(QLabel(option))
            slider = QSlider(Qt.Horizontal)
            slider.setFixedWidth(500)
            slider.setValue(self.get_user_setting(f"slider_{option}", 50))
            slider.valueChanged.connect(lambda value, opt=option: self.update_user_setting(f"slider_{opt}", value))
            slider_layout.addWidget(slider)
            layout.addLayout(slider_layout)
            layout.addSpacing(10)

        layout.addSpacing(20)

        # 创建颜色选择器
        color_options = [("懸浮窗顏色", self.create_gradient_button), ("字體顏色", self.create_gradient_button)]
        color_grid = QGridLayout()
        color_grid.setVerticalSpacing(25)
        color_grid.setColumnStretch(0, 1)
        color_grid.setColumnStretch(1, 0)
        color_grid.setColumnStretch(2, 1)
        color_grid.setColumnStretch(3, 0)
        for i, (option, create_button_func) in enumerate(color_options):
            label = QLabel(option)
            color_button = create_button_func()
            color_button.clicked.connect(lambda _, btn=color_button, opt=option: self.choose_color(btn, opt))
            checkbox = QCheckBox("懸浮窗固定" if option == "懸浮窗顏色" else "")
            if option == "懸浮窗顏色":
                checkbox.setChecked(self.data_processor.get_user_settings(self.data_processor.current_user).get("floating_window_fixed", False))
                checkbox.stateChanged.connect(self.update_floating_window_fixed)
            color_grid.addWidget(label, i, 0)
            color_grid.addWidget(color_button, i, 1)
            color_grid.addWidget(checkbox, i, 3, Qt.AlignRight)
        layout.addLayout(color_grid)

        layout.addStretch(1)
        return vision_widget

    def update_display_option(self, option, state):
        settings = self.data_processor.get_user_settings(self.data_processor.current_user)
        settings[f"display_{option}"] = state == Qt.Checked
        self.data_processor.save_user_settings(self.data_processor.current_user, settings)
        self.update_floating_window_signal.emit(settings)  # 发射信号

    def update_floating_window_fixed(self, state):
        settings = self.data_processor.get_user_settings(self.data_processor.current_user)
        settings["floating_window_fixed"] = state == Qt.Checked
        self.data_processor.save_user_settings(self.data_processor.current_user, settings)
        self.update_floating_window_signal.emit(settings)  # 发射信号

    def create_settings_page(self):
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # 开机自启和开始监听
        auto_start_layout = QHBoxLayout()
        auto_start_layout.addWidget(QLabel("開機自啟"))
        auto_start_checkbox = QCheckBox()
        auto_start_layout.addWidget(auto_start_checkbox)
        auto_start_layout.addStretch()
        auto_start_layout.addWidget(QLabel("開始監聽"))
        start_listening_checkbox = QCheckBox()
        auto_start_layout.addWidget(start_listening_checkbox)
        layout.addLayout(auto_start_layout)

        # 主题样式
        layout.addWidget(self.create_combo_box("主題樣式", ["Default", "Dark", "Light"]))

        # 悬浮窗样式
        layout.addWidget(self.create_combo_box("懸浮窗樣式", ["Default", "Minimal", "Expanded"]))

        # 字体样式
        layout.addWidget(self.create_combo_box("字體樣式", ["Default", "Sans-serif", "Serif", "Monospace"]))

        # 样式导入按钮
        import_style_button = QPushButton("样导入")
        import_style_button.setFixedSize(120, 40)
        import_style_button.clicked.connect(self.open_style_import_dialog)
        layout.addWidget(import_style_button, alignment=Qt.AlignRight)

        # 添加链接
        links_layout = QHBoxLayout()
        
        more_styles_link = QPushButton("更多样式")
        more_styles_link.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/zjnbwxq/keymira-styles")))
        
        about_link = QPushButton("关于")
        about_link.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/zjnbwxq/Keymira")))
        
        user_manual_link = QPushButton("用户手册")
        user_manual_link.clicked.connect(self.open_user_manual)
        
        for link in [more_styles_link, about_link, user_manual_link]:
            link.setFlat(True)
            link.setFont(QFont("Noto Sans TC Regular", 12))
            link.setCursor(Qt.PointingHandCursor)
            links_layout.addWidget(link)
        
        links_layout.addStretch()
        layout.addLayout(links_layout)

        return settings_widget

    def create_user_page(self):
        user_widget = QWidget()
        layout = QVBoxLayout(user_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # 用户选择
        user_layout = QHBoxLayout()
        user_label = QLabel("用户")
        user_label.setFont(QFont("Noto Sans TC Regular", 10))  # 减小字体
        user_layout.addWidget(user_label)

        self.user_combo = QComboBox()
        self.user_combo.setFont(QFont("Noto Sans TC Regular", 9))  # 减小字体
        self.user_combo.setFixedSize(300, 40)  # 保持原始大小
        self.user_combo.addItem("guest")
        self.update_user_list()
        self.user_combo.currentIndexChanged.connect(self.on_user_selected)
        user_layout.addWidget(self.user_combo)

        # 用户理钮
        user_management_button = QPushButton("用户管理")
        user_management_button.setFont(QFont("Noto Sans TC Regular", 9))  # 减小字体
        user_management_button.setFixedSize(150, 40)  # 保持原始大小
        user_management_button.clicked.connect(self.open_user_management)
        user_layout.addWidget(user_management_button)
        user_layout.addStretch()

        layout.addLayout(user_layout)

        # 统计信息
        stats_layout = QHBoxLayout()
        stats_label = QLabel("统计信息")
        stats_label.setFont(QFont("Noto Sans TC Regular", 10))  # 减小字体
        stats_layout.addWidget(stats_label)

        self.stats_combo = QComboBox()
        self.stats_combo.setFont(QFont("Noto Sans TC Regular", 9))
        self.stats_combo.setFixedSize(300, 40)
        self.stats_combo.addItems(["热力图", "纯文字数据"])  # 只保留这两个选项
        stats_layout.addWidget(self.stats_combo)
        stats_layout.addStretch()

        layout.addLayout(stats_layout)

        # 图表显示区域
        chart_frame = QFrame()
        chart_frame.setFrameShape(QFrame.StyledPanel)
        chart_frame.setFixedSize(640, 360)  # 保持原始大小
        layout.addWidget(chart_frame, alignment=Qt.AlignCenter)

        # 按钮
        button_layout = QHBoxLayout()
        import_button = QPushButton("历史信息导入")
        export_button = QPushButton("导出")
        for button in [import_button, export_button]:
            button.setFont(QFont("Noto Sans TC Regular", 9))  # 减小字体
            button.setFixedSize(200, 40)  # 保持原始大小
        button_layout.addWidget(import_button)
        button_layout.addWidget(export_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)
        layout.addStretch()

        # 修改导入和导出按钮的连接
        import_button.clicked.connect(self.import_data)
        export_button.clicked.connect(self.export_data)

        return user_widget

    def update_user_list(self):
        current_user = self.user_combo.currentText()
        self.user_combo.clear()
        self.user_combo.addItem("guest")
        users = self.data_processor.get_user_list()
        self.user_combo.addItems(users)
        self.user_combo.addItem("新增用户")
        if current_user in users or current_user == "guest":
            self.user_combo.setCurrentText(current_user)
        else:
            self.user_combo.setCurrentText("guest")

    def on_user_selected(self, index):
        if self.user_combo.currentText() == "新增用户":
            self.open_user_management()
        else:
            selected_user = self.user_combo.currentText()
            self.data_processor.set_current_user(selected_user)
            self.update_stats_display(self.data_processor.get_key_stats())

    def open_user_management(self):
        dialog = UserManagementDialog(self.data_processor, self)
        dialog.user_added.connect(self.on_user_added)
        dialog.user_removed.connect(self.update_user_list)
        if dialog.exec_() == QDialog.Accepted:
            self.update_user_list()

    def on_user_added(self, username):
        self.update_user_list()
        self.user_combo.setCurrentText(username)
        self.update_stats_display(self.data_processor.get_key_stats())

    def create_gradient_button(self):
        button = QPushButton()
        button.setFixedSize(60, 60)
        gradient = QLinearGradient(0, 0, 60, 0)
        gradient.setColorAt(0.0, Qt.red)
        gradient.setColorAt(0.5, Qt.yellow)
        gradient.setColorAt(1.0, Qt.green)
        button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 red, stop:0.5 yellow, stop:1 green);
                border-radius: 30px;
            }}
        """)
        return button

    def choose_color(self, button, option):
        color = QColorDialog.getColor()
        if color.isValid():
            button.setStyleSheet(f"background-color: {color.name()};")
            settings = self.data_processor.get_user_settings(self.data_processor.current_user)
            settings[f"color_{option}"] = color.name()
            self.data_processor.save_user_settings(self.data_processor.current_user, settings)
            self.update_floating_window_signal.emit(settings)  # 发射信号

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 40, 40)

        painter.setClipPath(path)
        painter.fillPath(path, QColor("#D9D9D9"))

    def update_stats_display(self, stats):
        # 根据选择的统计类型（热力图或纯文字数据）更新显示
        selected_type = self.stats_combo.currentText()
        if selected_type == "热力图":
            # 实现热力图显示逻辑
            pass
        elif selected_type == "纯文字数据":
            # 实现纯文字数据显示逻辑
            pass

    def create_combo_box(self, label_text, items):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        label = QLabel(label_text)
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        label.setFont(QFont("Noto Sans TC Regular", 12))
        layout.addWidget(label)

        layout.addStretch()

        combo_box = QComboBox()
        combo_box.addItems(items)
        combo_box.setFont(QFont("Noto Sans TC Regular", 12))
        combo_box.setFixedHeight(40)
        combo_box.setMinimumWidth(300)
        combo_box.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        
        # 获取 drop.png 的绝对路径
        drop_icon_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'drop.png'))
        
        # 更新样式表，使用 drop.png 作为下拉箭头
        combo_box.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 5px 10px;
                background-color: white;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left: 1px solid #CCCCCC;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
            }}
            QComboBox::down-arrow {{
                image: url({drop_icon_path});
                width: 16px;
                height: 16px;
            }}
        """)
        
        layout.addWidget(combo_box)

        return widget

    def open_user_manual(self):
        user_manual_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "doc", "User Manual.md")
        QDesktopServices.openUrl(QUrl.fromLocalFile(user_manual_path))

    def open_style_import_dialog(self):
        dialog = StyleImportDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            style_data = dialog.get_style_data()
            # 这里可以添加处理导入样式的逻辑
            print("Imported style data:", style_data)

    def import_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "导入数据", "", "JSON Files (*.json)")
        if file_path:
            self.data_processor.import_data(file_path)
            self.update_stats_display(self.data_processor.get_key_stats())

    def export_data(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "导出数据", "", "JSON Files (*.json)")
        if file_path:
            self.data_processor.export_data(file_path)
            QMessageBox.information(self, "成功", "数据已成功导出")

    def load_user_settings(self):
        # 从数据处理器加载用户设置
        self.user_settings = self.data_processor.get_user_settings(self.current_user)

    def save_user_settings(self):
        # 保存用户设置到数据处理器
        self.data_processor.save_user_settings(self.current_user, self.user_settings)

    def get_user_setting(self, key, default_value):
        return self.user_settings.get(key, default_value)

    def update_user_setting(self, key, value):
        self.user_settings[key] = value
        self.save_user_settings()

    def on_user_changed(self, username):
        self.current_user = username
        self.load_user_settings()
        self.update_vision_page()

    def update_vision_page(self):
        # 重新创建视觉页面以反映新的用户设置
        vision_page_index = self.stacked_widget.indexOf(self.vision_page)
        self.stacked_widget.removeWidget(self.vision_page)
        self.vision_page = self.create_vision_page()
        self.stacked_widget.insertWidget(vision_page_index, self.vision_page)




























