from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QPoint, QTimer, QPropertyAnimation, QEasingCurve, QSize, QMetaObject
from PyQt5.QtGui import QColor, QPainter, QFont, QFontMetrics, QMouseEvent, QPalette, QFontDatabase, QBrush

class FloatingWindow(QWidget):
    def __init__(self, style_manager):
        super().__init__()
        self.style_manager = style_manager
        self.current_style = self.style_manager.get_style("default_simple")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        self.layout = QVBoxLayout()
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        
        self.settings = {}
        self.font = QFont(self.current_style['font'], self.current_style['font_size'])
        self.min_width = 300  # 增加最小宽度
        self.max_width = 800  # 增加最大宽度
        self.padding = self.current_style['padding']
        self.border_radius = self.current_style['border_radius']
        
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.activity_timer = QTimer(self)
        self.activity_timer.setSingleShot(True)
        self.activity_timer.timeout.connect(self.start_fade_out)
        self.is_visible = False
        self.dragging = False
        self.fade_in_duration = 200
        self.fade_out_duration = 200
        self.display_delay = 2000
        self.color = QColor(self.current_style['background_color'])
        self.text_color = QColor(self.current_style['text_color'])

        self.apply_style()

    def update_settings(self, settings):
        self.settings = settings
        style_name = settings.get('style', 'default_simple')
        self.current_style = self.style_manager.get_style(style_name)
        self.fade_in_duration = settings.get('fade_in', self.fade_in_duration)
        self.fade_out_duration = settings.get('fade_out', self.fade_out_duration)
        self.display_delay = settings.get('display_delay', self.display_delay)
        self.font_size = settings.get('font_size', 36)  # 默认字体大小设为36
        self.font.setPointSize(self.font_size)
        self.color = QColor(settings.get('color_懸浮窗顏色', self.color.name()))
        self.text_color = QColor(settings.get('color_字體顏色', self.text_color.name()))
        self.apply_style()

    def apply_style(self):
        palette = self.palette()
        palette.setColor(QPalette.Window, self.color)
        palette.setColor(QPalette.WindowText, self.text_color)
        self.setPalette(palette)
        
        font_files = self.style_manager.get_style_font_files("default_simple")
        if font_files:
            font_id = QFontDatabase.addApplicationFont(font_files[0])
            if font_id != -1:
                font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
                self.font = QFont(font_family, self.current_style['font_size'])
        self.label.setFont(self.font)
        self.label.setStyleSheet(f"color: {self.text_color.name()}; background-color: transparent;")
        self.update()

    def update_content(self, text):
        simplified_text = self.simplify_key_text(text)
        self.label.setText(simplified_text)
        self.adjust_size(simplified_text)
        if not self.isVisible():
            self.start_fade_in()
        self.reset_activity_timer()

    def clear_content(self):
        self.label.clear()
        self.adjust_size("")
        self.reset_activity_timer()

    def adjust_size(self, text):
        fm = QFontMetrics(self.font)
        text_width = fm.horizontalAdvance(text)
        text_height = fm.height()
        
        window_width = max(self.min_width, min(text_width + self.padding * 2, self.max_width))
        window_height = text_height + self.padding * 2
        
        self.setFixedSize(window_width, window_height)
        self.label.setFixedSize(window_width - self.padding * 2, window_height - self.padding * 2)

    def start_fade_in(self):
        self.fade_animation.stop()
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)
        self.fade_animation.setDuration(self.fade_in_duration)
        self.fade_animation.start()
        self.show()
        self.is_visible = True

    def start_fade_out(self):
        self.fade_animation.stop()
        self.fade_animation.setStartValue(1)
        self.fade_animation.setEndValue(0)
        self.fade_animation.setDuration(self.fade_out_duration)
        self.fade_animation.finished.connect(self.hide_window)
        self.fade_animation.start()

    def hide_window(self):
        self.hide()
        self.is_visible = False
        self.fade_animation.finished.disconnect(self.hide_window)

    def reset_activity_timer(self):
        self.activity_timer.stop()
        self.activity_timer.start(self.display_delay)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 创建半透明磨砂玻璃效果
        blur_color = QColor(0, 0, 0, 180)  # 黑色半透明
        painter.setBrush(QBrush(blur_color))
        painter.setPen(Qt.NoPen)

        # 绘制圆角矩形
        painter.drawRoundedRect(self.rect(), self.border_radius, self.border_radius)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging:
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.dragging = False

    def simplify_key_text(self, text):
        key_display = self.current_style['key_display']
        for key, symbol in key_display.items():
            text = text.replace(key, symbol)
        return text
