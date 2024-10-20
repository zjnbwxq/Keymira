import json
import os
from pathlib import Path
import shutil

class DataProcessor:
    def __init__(self):
        self.user_data = {}
        self.current_user = "guest"
        self.data_dir = os.path.join(os.path.expanduser('~'), '.keymira')
        self.guest_file = os.path.join(self.data_dir, "guest_data.json")
        self.load_data()

    def get_user_list(self):
        return [user for user in self.user_data.keys() if user != "guest"]

    def add_user(self, username):
        if username not in self.user_data and username != "guest":
            self.user_data[username] = {
                'key_counts': {},
                'settings': {},
                'styles': [],
                'fonts': []
            }
            self.save_data()
            return True
        return False

    def remove_user(self, username):
        if username in self.user_data and username != "guest":
            del self.user_data[username]
            file_path = os.path.join(self.data_dir, f"{username}_data.json")
            if os.path.exists(file_path):
                os.remove(file_path)
            self.save_data()
            return True
        return False

    def set_current_user(self, username):
        if username in self.user_data:
            self.current_user = username
            if username == "guest":
                self.cleanup_guest_data()
            return True
        return False

    def process_key(self, key):
        keys = key.split('+')
        for k in keys:
            k = k.strip().lower()
            if k == '':
                k = 'space'
            self.user_data[self.current_user]['key_counts'][k] = self.user_data[self.current_user]['key_counts'].get(k, 0) + 1
        self.save_data()

    def get_key_stats(self):
        return self.user_data[self.current_user]['key_counts']

    def save_data(self):
        os.makedirs(self.data_dir, exist_ok=True)
        for username, data in self.user_data.items():
            file_path = os.path.join(self.data_dir, f"{username}_data.json")
            with open(file_path, 'w') as f:
                json.dump(data, f)

    def load_data(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        for file in os.listdir(self.data_dir):
            if file.endswith("_data.json"):
                username = file[:-10]  # Remove "_data.json"
                file_path = os.path.join(self.data_dir, file)
                with open(file_path, 'r') as f:
                    self.user_data[username] = json.load(f)
        if "guest" not in self.user_data:
            self.user_data["guest"] = {
                'key_counts': {},
                'settings': self.get_default_settings(),
                'styles': [],
                'fonts': []
            }

    def clear_data(self):
        self.user_data[self.current_user] = {
            'key_counts': {},
            'settings': {},
            'styles': [],
            'fonts': []
        }
        self.save_data()

    def export_data(self, file_path):
        shutil.copy2(os.path.join(self.data_dir, f"{self.current_user}_data.json"), file_path)

    def import_data(self, file_path):
        with open(file_path, 'r') as f:
            imported_data = json.load(f)
        self.user_data[self.current_user] = imported_data
        self.save_data()

    def get_user_settings(self, username):
        if username in self.user_data:
            return self.user_data[username].get('settings', {})
        return {}

    def save_user_settings(self, username, settings):
        if username in self.user_data:
            self.user_data[username]['settings'] = settings
            self.save_data()

    def update_settings(self, settings):
        self.user_data[self.current_user]['settings'] = settings
        self.save_data()

    def get_default_settings(self):
        return {
            "display_顯示普通鍵": True,
            "display_顯示修飾鍵": True,
            "display_顯示組合鍵": True,
            "display_顯示小鍵盤": True,
            "display_顯示F1~F12": True,
            "slider_字體大小": 50,
            "slider_顯示時長": 50,
            "slider_淡出時長": 50,
            "color_懸浮窗顏色": "#FFFFFF",
            "color_字體顏色": "#000000",
            "floating_window_fixed": False
        }

    def add_style(self, style_id):
        if style_id not in self.user_data[self.current_user]['styles']:
            self.user_data[self.current_user]['styles'].append(style_id)
            self.save_data()

    def add_font(self, font_name):
        if font_name not in self.user_data[self.current_user]['fonts']:
            self.user_data[self.current_user]['fonts'].append(font_name)
            self.save_data()

    def cleanup_guest_data(self):
        if os.path.exists(self.guest_file):
            os.remove(self.guest_file)
        self.user_data["guest"] = {
            'key_counts': {},
            'settings': self.get_default_settings(),
            'styles': [],
            'fonts': []
        }
        self.save_data()
