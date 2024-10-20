from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                             QHBoxLayout, QLabel, QSlider, QCheckBox, QColorDialog, QGridLayout, QSpacerItem, QStackedWidget, QComboBox, QDialog, QFrame)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QPainter, QPainterPath, QIcon, QPixmap, QLinearGradient, QFontDatabase, QDesktopServices
from PyQt5.QtCore import QUrl
import os
from .special_key_dialog import SpecialKeyDialog
from .style_import_dialog import StyleImportDialog
from .user_management_dialog import UserManagementDialog  # 更新导入语句

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(720, 916)  # 360 * 2, 458 * 2
        self.icons = self.load_icons()
        self.load_fonts()
        self.current_page = 0
        self.stacked_widget = QStackedWidget()
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
        # 这里包含原来的设置页面内容（现在作为视觉界面）
        vision_widget = QWidget()
        layout = QVBoxLayout(vision_widget)

        # 创建显示选项
        display_options = ["顯示普通鍵", "顯示修飾鍵", "顯示組合鍵", "顯示小鍵盤", "顯示F1~F12", "顯示特殊鍵位"]
        options_grid = QGridLayout()
        options_grid.setVerticalSpacing(25)
        options_grid.setColumnStretch(0, 1)
        options_grid.setColumnStretch(1, 0)
        options_grid.setColumnStretch(2, 1)
        options_grid.setColumnStretch(3, 0)
        for i, option in enumerate(display_options):
            label = QLabel(option)
            checkbox = QCheckBox()
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
            color_button.clicked.connect(lambda _, btn=color_button: self.choose_color(btn))
            checkbox = QCheckBox("懸浮窗固定" if option == "懸浮窗顏色" else "圖像模式")
            color_grid.addWidget(label, i, 0)
            color_grid.addWidget(color_button, i, 1)
            color_grid.addWidget(checkbox, i, 3, Qt.AlignRight)
        layout.addLayout(color_grid)

        layout.addStretch(1)
        return vision_widget

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

        # 特殊键位
        special_key_layout = QHBoxLayout()
        special_key_layout.addWidget(QLabel("特殊鍵位"))
        special_key_layout.addStretch()
        bind_key_button = QPushButton("綁定新鍵位")
        bind_key_button.setFixedSize(200, 40)
        bind_key_button.clicked.connect(self.open_special_key_dialog)
        special_key_layout.addWidget(bind_key_button)
        layout.addLayout(special_key_layout)

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

        # 用户管理按钮
        user_management_button = QPushButton("用户管理")
        user_management_button.setFont(QFont("Noto Sans TC Regular", 14))
        user_management_button.setFixedSize(150, 40)
        user_management_button.clicked.connect(self.open_user_management)
        layout.addWidget(user_management_button, alignment=Qt.AlignRight)

        # 用户选择
        user_layout = QHBoxLayout()
        user_label = QLabel("用户")
        user_label.setFont(QFont("Noto Sans TC Regular", 16))
        user_layout.addWidget(user_label)

        self.user_combo = QComboBox()
        self.user_combo.setFont(QFont("Noto Sans TC Regular", 14))
        self.user_combo.setFixedSize(300, 40)
        self.user_combo.addItem("新增用户")
        self.update_user_list()
        self.user_combo.currentIndexChanged.connect(self.on_user_selected)
        user_layout.addWidget(self.user_combo)
        user_layout.addStretch()

        layout.addLayout(user_layout)

        # 统计信息
        stats_layout = QHBoxLayout()
        stats_label = QLabel("统计信息")
        stats_label.setFont(QFont("Noto Sans TC Regular", 16))
        stats_layout.addWidget(stats_label)

        self.stats_combo = QComboBox()
        self.stats_combo.setFont(QFont("Noto Sans TC Regular", 14))
        self.stats_combo.setFixedSize(300, 40)
        self.stats_combo.addItems(["热力图", "柱状图", "折线图"])
        stats_layout.addWidget(self.stats_combo)
        stats_layout.addStretch()

        layout.addLayout(stats_layout)

        # 图表显示区域
        chart_frame = QFrame()
        chart_frame.setFrameShape(QFrame.StyledPanel)
        chart_frame.setFixedSize(640, 360)
        layout.addWidget(chart_frame, alignment=Qt.AlignCenter)

        # 按钮
        button_layout = QHBoxLayout()
        import_button = QPushButton("历史信息导入")
        export_button = QPushButton("导出")
        for button in [import_button, export_button]:
            button.setFont(QFont("Noto Sans TC Regular", 14))
            button.setFixedSize(150, 40)
        button_layout.addWidget(import_button)
        button_layout.addWidget(export_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)
        layout.addStretch()

        return user_widget

    def update_user_list(self):
        # 从某个地方获取用户列表，可能是从文件或数据库
        # 暂时使用示例数据
        users = ["User1", "User2", "User3"]
        self.user_combo.clear()
        self.user_combo.addItem("新增用户")
        self.user_combo.addItems(users)

    def on_user_selected(self, index):
        if self.user_combo.currentText() == "新增用户":
            dialog = UserManagementDialog(self)  # 使用新的类名
            if dialog.exec_() == QDialog.Accepted:
                new_users = dialog.get_users()  # 获取所有用户，而不是单个用户
                # 这里应该保存新用户数据
                print(f"Updated users: {new_users}")
                self.update_user_list()
        else:
            # 处理选择已有用户的逻辑
            selected_user = self.user_combo.currentText()
            print(f"Selected user: {selected_user}")

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

    def choose_color(self, button):
        color = QColorDialog.getColor()
        if color.isValid():
            button.setStyleSheet(f"background-color: {color.name()}; border-radius: 30px;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 40, 40)

        painter.setClipPath(path)
        painter.fillPath(path, QColor("#D9D9D9"))

    def update_stats_display(self, stats):
        # 更新统计信息显示的逻辑
        pass  # 根据需要实现具体的更新逻辑

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

    def open_special_key_dialog(self):
        dialog = SpecialKeyDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # 处理用户在对话框中的输入
            special_keys = []
            for row in range(dialog.table.rowCount()):
                key = dialog.table.item(row, 0).text()
                display_name = dialog.table.item(row, 1).text()
                note = dialog.table.item(row, 2).text()
                special_keys.append((key, display_name, note))
            
            # 这里可以添加保存特殊键位数据的逻辑
            print("Special keys:", special_keys)

    def open_user_manual(self):
        user_manual_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "doc", "User Manual.md")
        QDesktopServices.openUrl(QUrl.fromLocalFile(user_manual_path))

    def open_style_import_dialog(self):
        dialog = StyleImportDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            style_data = dialog.get_style_data()
            # 这里可以添加处理导入样式的逻辑
            print("Imported style data:", style_data)

    def open_user_management(self):
        dialog = UserManagementDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            users = dialog.get_users()
            # 更新用户列表或进行其他操作
            print(f"Updated users: {users}")





















