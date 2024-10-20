from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QPoint, QTimer, QPropertyAnimation, QEasingCurve, QSize
from PyQt5.QtGui import QColor, QPainter, QFont, QFontMetrics, QMouseEvent

class FloatingWindow(QWidget):
    def __init__(self, style_manager=None):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.layout = QVBoxLayout()
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: white; background-color: rgba(0, 0, 0, 150); border-radius: 10px;")
        self.label.setFont(QFont("Arial", 20))
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        
        self.style_manager = style_manager
        
        self.fade_in_duration = 500
        self.fade_out_duration = 500
        self.display_delay = 1500  # 1.5秒无活动后开始淡出
        self.font_size = 20
        self.color = QColor(255, 255, 255)  # 默认白色
        self.font = QFont("Arial", self.font_size)
        self.min_width = 200  # 最小宽度
        self.max_width = 800  # 最大宽度
        self.min_height = 50  # 最小高度
        self.padding = 20  # 文本左右padding

        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)

        self.activity_timer = QTimer(self)
        self.activity_timer.setSingleShot(True)
        self.activity_timer.timeout.connect(self.start_fade_out)

        self.is_visible = False
        self.dragging = False
        self.offset = QPoint()
        self.apply_style()

    def apply_style(self):
        self.label.setFont(self.font)
        self.label.setStyleSheet(f"color: {self.color.name()}")
        if self.label.text():
            self.adjust_size(self.label.text())
        if self.is_visible:
            self.reset_activity_timer()

    def update_content(self, text):
        self.label.setText(text)
        self.adjust_size(text)
        
        if not self.is_visible:
            self.show()
            self.start_fade_in()
        
        self.reset_activity_timer()

    def clear_content(self):
        self.label.clear()
        self.adjust_size("")
        self.reset_activity_timer()

    def adjust_size(self, text):
        fm = QFontMetrics(self.font)
        text_width = fm.horizontalAdvance(text)  # 使用 horizontalAdvance 替代 width
        text_height = fm.height()
        
        window_width = max(self.min_width, min(text_width + self.padding * 2, self.max_width))
        window_height = max(self.min_height, text_height + self.padding)
        
        self.setGeometry(self.x(), self.y(), window_width, window_height)
        self.label.setGeometry(0, 0, window_width, window_height)

    def start_fade_in(self):
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)
        self.fade_animation.setDuration(self.fade_in_duration)
        self.fade_animation.start()
        self.is_visible = True

    def start_fade_out(self):
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

    def update_settings(self, settings):
        self.fade_in_duration = settings.get('fade_in', self.fade_in_duration)
        self.fade_out_duration = settings.get('fade_out', self.fade_out_duration)
        self.display_delay = settings.get('display_delay', self.display_delay)
        self.font_size = settings.get('font_size', self.font_size)
        self.font.setPointSize(self.font_size)
        if settings.get('color'):
            self.color = QColor(settings['color'])
        self.apply_style()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(0, 0, 0, 200))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 10, 10)
        super().paintEvent(event)

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

    def update_text(self, text):
        self.label.setText(text)
        self.adjust_size(text)

    def clear_text(self):
        self.label.clear()
        self.adjust_size("")
