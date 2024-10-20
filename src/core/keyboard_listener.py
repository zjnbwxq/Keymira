from pynput import keyboard
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
import time
import json

class KeyboardListener(QObject):
    key_event = pyqtSignal(str)
    clear_event = pyqtSignal()
    key_for_stats = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.listener = None
        self.modifier_keys = set()
        self.last_key_time = 0
        self.current_phrase = ""
        self.load_settings()
        self.max_consecutive_chars = 11  # 默认值为11
        self.clear_timer = QTimer()
        self.clear_timer.setSingleShot(True)
        self.clear_timer.timeout.connect(self.clear_display)
        self.display_settings = {}

    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                self.settings = json.load(f)
        except FileNotFoundError:
            self.settings = {'fn_key_code': 0x1D, 'max_consecutive_chars': 11}
        
        # 设置默认值
        if 'fn_key_code' not in self.settings:
            self.settings['fn_key_code'] = 0x1D
        if 'max_consecutive_chars' not in self.settings:
            self.settings['max_consecutive_chars'] = 11
        
        self.max_consecutive_chars = self.settings['max_consecutive_chars']
        self.save_settings()

    def save_settings(self):
        with open('settings.json', 'w') as f:
            json.dump(self.settings, f)

    def set_max_consecutive_chars(self, value):
        self.max_consecutive_chars = value
        self.settings['max_consecutive_chars'] = value
        self.save_settings()

    def update_display_settings(self, settings):
        self.display_settings = {k: v for k, v in settings.items() if k.startswith("display_")}

    def on_press(self, key):
        current_time = time.time()
        key_char = self.normalize_key(key)
        print(f"按下的键: {key_char}")  # 调试信息

        if current_time - self.last_key_time > 1.5:
            self.clear_display()

        self.last_key_time = current_time

        if key_char in {'ctrl', 'alt', 'shift', 'win', 'fn'}:
            if key_char not in self.modifier_keys:
                self.modifier_keys.add(key_char)
                self.emit_current_keys()
        else:
            if not self.modifier_keys:
                self.current_phrase += key_char
                if len(self.current_phrase) > self.max_consecutive_chars:
                    self.current_phrase = self.current_phrase[-self.max_consecutive_chars:]
                key_string = self.current_phrase
            else:
                key_string = "+".join(sorted(self.modifier_keys)) + "+" + key_char
            
            print(f"发送键字符串: {key_string}")  # 调试信息
            self.key_event.emit(key_string)
        
        # 总是发送统计事件
        self.key_for_stats.emit(key_char)

        # 重置计时器
        self.clear_timer.start(1500)

        self.key_for_stats.emit(key_char)

    def on_release(self, key):
        key_char = self.normalize_key(key)
        print(f"Released key: {key_char}")  # 调试信息

        if key_char in self.modifier_keys:
            self.modifier_keys.remove(key_char)
            if self.modifier_keys:
                self.emit_current_keys()
            else:
                # 如果所有修饰键都已释放，立即清除显示
                self.clear_display()

    def clear_display(self):
        self.clear_event.emit()
        self.current_phrase = ""
        self.modifier_keys.clear()

    def emit_current_keys(self):
        if self.modifier_keys:
            key_string = "+".join(sorted(self.modifier_keys))
            print(f"发送当前修饰键: {key_string}")  # 调试信息
            self.key_event.emit(key_string)
            # 重置计时器
            self.clear_timer.start(1500)

    def normalize_key(self, key):
        if isinstance(key, keyboard.Key):
            if key in {keyboard.Key.ctrl_l, keyboard.Key.ctrl_r}:
                return 'ctrl'
            elif key in {keyboard.Key.alt_l, keyboard.Key.alt_r}:
                return 'alt'
            elif key in {keyboard.Key.shift_l, keyboard.Key.shift_r}:
                return 'shift'
            elif key in {keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r}:
                return 'win'
            elif key == keyboard.Key.space:
                return 'space'
            return key.name.lower()
        elif isinstance(key, keyboard.KeyCode):
            if key.vk == self.settings['fn_key_code']:
                return 'fn'
            return self.vk_to_char(key.vk if key.vk else ord(key.char))
        return str(key).lower()

    def should_display_key(self, key):
        if key in {'ctrl', 'alt', 'shift', 'win', 'fn'}:
            return self.display_settings.get("display_顯示修飾鍵", True)
        elif key.startswith('f') and key[1:].isdigit():
            return self.display_settings.get("display_顯示F1~F12", True)
        elif key in {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '+', '-', '*', '/', 'enter', 'num_lock'}:
            return self.display_settings.get("display_顯示小鍵盤", True)
        else:
            return self.display_settings.get("display_顯示普通鍵", True)

    def start(self):
        if not self.listener:
            self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
            self.listener.start()
        print("开始监听键盘")

    def stop(self):
        if self.listener:
            self.listener.stop()
            self.listener = None
        self.modifier_keys.clear()
        self.current_phrase = ""
        print("停止监听键盘")

    def vk_to_char(self, vk):
        vk_mapping = {
            # 字母键
            65: 'a', 66: 'b', 67: 'c', 68: 'd', 69: 'e', 70: 'f', 71: 'g', 72: 'h',
            73: 'i', 74: 'j', 75: 'k', 76: 'l', 77: 'm', 78: 'n', 79: 'o', 80: 'p',
            81: 'q', 82: 'r', 83: 's', 84: 't', 85: 'u', 86: 'v', 87: 'w', 88: 'x',
            89: 'y', 90: 'z',
            # 数字键
            48: '0', 49: '1', 50: '2', 51: '3', 52: '4', 53: '5', 54: '6', 55: '7', 56: '8', 57: '9',
            # 常用标点符号
            186: ';', 187: '=', 188: ',', 189: '-', 190: '.', 191: '/', 192: '`',
            219: '[', 220: '\\', 221: ']', 222: "'",
            # 功能键
            8: 'backspace', 9: 'tab', 13: 'enter', 16: 'shift', 17: 'ctrl', 18: 'alt',
            19: 'pause', 20: 'caps_lock', 27: 'esc', 32: 'space', 33: 'page_up',
            34: 'page_down', 35: 'end', 36: 'home', 37: 'left', 38: 'up', 39: 'right',
            40: 'down', 45: 'insert', 46: 'delete',
        }
        return vk_mapping.get(vk, f'special_{vk}')
