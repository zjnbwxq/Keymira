import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSystemTrayIcon, QMenu, QAction, QDesktopWidget, QMainWindow, QMessageBox, QFileDialog, QInputDialog, QDialog
from PyQt5.QtCore import QTimer, Qt, QSize, pyqtSlot, QObject, pyqtSignal, QPoint, QMetaObject, QMetaType
from PyQt5.QtGui import QColor, QPainter, QPainterPath, QFont, QIcon, QPixmap, QFontDatabase
from ui.main_window import MainWindow
from core.keyboard_listener import KeyboardListener
from core.data_processor import DataProcessor
from ui.floating_window import FloatingWindow
from core.style_manager import StyleManager
import json
from datetime import datetime
import os
from ui.custom_menu import CustomMenu


class Keymira(QObject):
    update_stats_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        self.style_manager = StyleManager()
        self.keyboard_listener = KeyboardListener()
        self.data_processor = DataProcessor()
        self.main_window = None
        self.floating_window = FloatingWindow(self.style_manager)
        self.stats = {}
        self.tray_icon = None
        self.is_listening = False
        self.keymira_action = None
        self.active_icon = None
        self.inactive_icon = None
        self.custom_menu = CustomMenu()
        
        self.load_fonts()
        
        self.main_window = MainWindow(self.data_processor)
        self.main_window.show()

        self.setup_connections()
        self.setup_timers()

        self.update_stats_signal.connect(self.update_stats)

    def load_fonts(self):
        font_dir = os.path.join(os.path.dirname(__file__), 'fonts')
        for font_file in ['NotoSansTC-Bold.ttf', 'NotoSansTC-Regular.ttf']:
            font_path = os.path.join(font_dir, font_file)
            if os.path.exists(font_path):
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id != -1:
                    font_families = QFontDatabase.applicationFontFamilies(font_id)
                    if font_families:
                        self.data_processor.add_font(font_families[0])
            else:
                print(f"警告：字体文件 {font_file} 不存在")

    def setup_connections(self):
        self.keyboard_listener.key_event.connect(self.floating_window.update_content)
        self.keyboard_listener.clear_event.connect(self.floating_window.clear_content)
        self.keyboard_listener.key_for_stats.connect(self.on_key_for_stats)
        self.app.aboutToQuit.connect(self.save_data)
        self.main_window.import_data_signal.connect(self.data_processor.import_data)
        self.main_window.export_data_signal.connect(self.data_processor.export_data)
        self.main_window.add_user_signal.connect(self.add_user)
        self.main_window.update_floating_window_signal.connect(self.update_floating_window_settings)

    def setup_timers(self):
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.on_update_timer)
        self.update_timer.start(1000)

        self.save_timer = QTimer(self)
        self.save_timer.timeout.connect(self.save_data)
        self.save_timer.start(300000)

    def on_update_timer(self):
        self.update_stats_signal.emit()

    def update_stats(self):
        if self.main_window:
            self.main_window.update_stats_display(self.data_processor.get_key_stats())

    def on_key_for_stats(self, key):
        self.data_processor.process_key(key)
        self.update_stats_signal.emit()

    def save_data(self):
        # 如果 self.stats 是一个包含两个元素的元组或列表
        stats, additional_data = self.stats
        self.data_processor.save_data(stats)
        # 或者如果只需要保存 stats 中的第一个元素
        # self.data_processor.save_data(self.stats[0])
        print("数据已保存")

    def clear_data(self):
        self.data_processor.clear_data()
        if self.main_window:
            self.main_window.update_stats_display({})
        print("清除数据")

    def toggle_floating_window(self, visible):
        if visible:
            self.floating_window.show()
        else:
            self.floating_window.hide()

    def change_display_mode(self, mode):
        print(f"更改显示模式为: {mode}")
        # 实现更改显示模式的逻辑

    def change_style(self, style_name):
        self.floating_window.load_style(style_name)
        self.data_processor.add_style(style_name)

    def quit_app(self):
        self.keyboard_listener.stop()
        if self.tray_icon:
            self.tray_icon.hide()
        if self.data_processor.current_user == "guest":
            self.data_processor.cleanup_guest_data()
        self.app.quit()

    def setup_tray_icon(self):
        if self.tray_icon is not None:
            return

        active_icon_path = os.path.join(os.path.dirname(__file__), "assets", "online.png")
        inactive_icon_path = os.path.join(os.path.dirname(__file__), "assets", "offline.png")

        if not os.path.exists(active_icon_path) or not os.path.exists(inactive_icon_path):
            print(f"警告：图标文件不存在")
            self.active_icon = QIcon.fromTheme("application-x-executable")
            self.inactive_icon = QIcon.fromTheme("application-x-executable")
        else:
            self.active_icon = QIcon(active_icon_path)
            self.inactive_icon = QIcon(inactive_icon_path)

        self.tray_icon = QSystemTrayIcon(self.inactive_icon, parent=self.app)
        
        # 移除默认右键菜单置
        # tray_menu = QMenu()
        # self.tray_icon.setContextMenu(tray_menu)
        
        self.update_keymira_color()
        
        if self.tray_icon.isSystemTrayAvailable():
            self.tray_icon.show()
            print("系统托盘图标已显示")
        else:
            print("系统托盘不可用")

        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        # 连接自定义菜单的信号
        self.custom_menu.setting_clicked.connect(self.show_settings)
        self.custom_menu.display_clicked.connect(self.toggle_floating_window)
        self.custom_menu.personal_clicked.connect(self.show_personal)
        self.custom_menu.quit_clicked.connect(self.quit_app)
        self.custom_menu.toggle_listening.connect(self.toggle_listening)

    def show_settings(self):
        if not self.main_window:
            self.main_window = MainWindow(self.data_processor)
            self.main_window.start_listening_signal.connect(self.keyboard_listener.start)
            self.main_window.stop_listening_signal.connect(self.keyboard_listener.stop)
            self.main_window.clear_data_signal.connect(self.clear_data)
            self.main_window.toggle_floating_window_signal.connect(self.toggle_floating_window)
            self.main_window.change_display_mode_signal.connect(self.change_display_mode)
            self.main_window.change_style_signal.connect(self.change_style)
            self.main_window.update_floating_window_signal.connect(self.floating_window.update_settings)
        self.main_window.show()
        self.main_window.activateWindow()

    def show_personal(self):
        self.show_settings()

    def toggle_listening(self, is_listening):
        if is_listening:
            self.start_listening()
        else:
            self.stop_listening()
        self.update_tray_icon()

    def update_keymira_color(self):
        if self.keymira_action:
            color = QColor(0, 255, 0) if self.is_listening else QColor(255, 0, 0)
            self.keymira_action.setIcon(self.create_color_icon(color))

    def update_tray_icon(self):
        if self.tray_icon:
            self.tray_icon.setIcon(self.active_icon if self.is_listening else self.inactive_icon)

    def create_color_icon(self, color):
        pixmap = QPixmap(16, 16)
        pixmap.fill(color)
        return QIcon(pixmap)

    def start_listening(self):
        print("开始监听")
        self.keyboard_listener.start()
        self.is_listening = True

    def stop_listening(self):
        print("停止监听")
        self.keyboard_listener.stop()
        self.is_listening = False

    def on_tray_icon_activated(self, reason):
        if reason in [QSystemTrayIcon.Trigger, QSystemTrayIcon.Context]:
            geometry = self.tray_icon.geometry()
            screen = QDesktopWidget().screenNumber(QDesktopWidget().cursor().pos())
            screen_rect = QDesktopWidget().screenGeometry(screen)
            
            # 计算菜单的位置
            menu_x = max(screen_rect.left(), min(geometry.x() - self.custom_menu.width() // 2, screen_rect.right() - self.custom_menu.width()))
            menu_y = max(screen_rect.top(), min(geometry.y() - self.custom_menu.height(), screen_rect.bottom() - self.custom_menu.height()))
            
            pos = QPoint(menu_x, menu_y)
            
            # 切换监听状态
            self.is_listening = not self.is_listening
            self.custom_menu.update_listening_state(self.is_listening)
            
            self.custom_menu.show_menu(pos)

    def run(self):
        self.setup_tray_icon()
        sys.exit(self.app.exec_())

    def add_user(self, username):
        if self.data_processor.add_user(username):
            self.main_window.update_user_list()
            self.main_window.user_combo.setCurrentText(username)
            self.main_window.update_stats_display(self.data_processor.get_key_stats())
        else:
            QMessageBox.warning(self.main_window, "错误", "用户名已存在或无效")

    def update_floating_window_settings(self, settings):
        self.floating_window.update_settings(settings)
        if settings.get("floating_window_fixed", False):
            self.floating_window.setWindowFlags(self.floating_window.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            self.floating_window.setWindowFlags(self.floating_window.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.floating_window.show()

if __name__ == "__main__":
    keymira = Keymira()
    keymira.run()
