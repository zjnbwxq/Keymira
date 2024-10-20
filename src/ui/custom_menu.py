from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QRectF
from PyQt5.QtGui import QFont, QColor, QPainter, QPainterPath, QLinearGradient

class CustomMenu(QWidget):
    setting_clicked = pyqtSignal()
    display_clicked = pyqtSignal()
    personal_clicked = pyqtSignal()
    quit_clicked = pyqtSignal()
    toggle_listening = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.is_listening = False
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.title = QPushButton("Keymira")
        self.title.setFixedSize(202, 76)
        self.title.setFont(QFont("Noto Sans TC", 16, QFont.Bold))
        self.update_title_style()
        self.title.clicked.connect(self.toggle_listening_state)
        layout.addWidget(self.title)

        buttons = [
            ("設  置", self.setting_clicked),
            ("顯  示", self.display_clicked),
            ("個  人", self.personal_clicked),
            ("登  出", self.quit_clicked)
        ]

        for i, (text, signal) in enumerate(buttons):
            btn = QPushButton(text)
            btn.setFixedSize(202, 76)
            btn.setFont(QFont("Noto Sans TC", 20, QFont.Bold))
            btn_style = """
                QPushButton {
                    background-color: #EAEAEA;
                    border: none;
                    color: black;
                    padding: 0px;
                    text-align: center;
                    font-size: 31px;
                }
                QPushButton:hover {
                    background-color: #D9D9D9;
                }
            """
            if i == len(buttons) - 1:  # 最后一个按钮（退出）
                btn_style += """
                    border-bottom-left-radius: 13px;
                    border-bottom-right-radius: 13px;
                """
            btn.setStyleSheet(btn_style)
            btn.clicked.connect(signal)
            layout.addWidget(btn)

        self.setFixedSize(202, 396)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        path = QPainterPath()
        rect = self.rect()
        path.addRoundedRect(
            rect.x(),
            rect.y(),
            rect.width(),
            rect.height(),
            13, 13
        )

        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor("#EAEAEA"))
        gradient.setColorAt(1, QColor("#D9D9D9"))

        painter.fillPath(path, gradient)

    def toggle_listening_state(self):
        self.is_listening = not self.is_listening
        self.update_title_style()
        self.toggle_listening.emit(self.is_listening)

    def update_title_style(self):
        self.title.setStyleSheet(f"""
            QPushButton {{
                color: {'#4C7F56' if self.is_listening else '#8D5656'};
                background-color: #EAEAEA;
                border: none;
                text-align: center;
                padding: 0px;
                border-top-left-radius: 13px;
                border-top-right-radius: 13px;
            }}
            QPushButton:hover {{
                background-color: #D9D9D9;
            }}
        """)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(self.title)
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(2, 2)
        self.title.setGraphicsEffect(shadow)

    def update_listening_state(self, is_listening):
        self.is_listening = is_listening
        self.update_title_style()

    def show_menu(self, pos):
        self.move(pos)
        self.adjustSize()
        self.update()
        self.show()
