import os
import json
import shutil
import requests
from PyQt5.QtCore import QSettings

class StyleManager:
    def __init__(self):
        self.styles = {}
        self.add_default_styles()

    def add_default_styles(self):
        font_dir = os.path.join(os.path.dirname(__file__), '..', 'fonts')

        # 默认简洁样式
        self.add_style("default_simple", {
            "name": "默认简洁样式",
            "description": "以简洁的方式展示修饰键、空格键和大写锁定键",
            "key_display": {
                "ctrl": "⌃",
                "alt": "⌥",
                "shift": "⇧",
                "win": "⊞",
                "cmd": "⌘",
                "space": "␣",
                "capslock": "⇪",
                "tab": "⇥",
                "enter": "↵",
                "backspace": "⌫",
                "esc": "⎋",
                "up": "↑",
                "down": "↓",
                "left": "←",
                "right": "→",
            },
            "font": "Noto Sans TC Regular",
            "font_size": 36,
            "background_color": "#000000CC",
            "text_color": "#FFFFFF",
            "padding": 20,
            "border_radius": 10,
        }, 
        font_files=[os.path.join(font_dir, 'NotoSansTC-Regular.ttf')])

        # 如果需要，可以在这里添加更多默认样式

    def add_style(self, style_id, style_data, font_files=None):
        if font_files is None:
            font_files = []

        # 验证必要的样式数据
        required_keys = ['name', 'description', 'key_display', 'font', 'font_size', 
                         'background_color', 'text_color', 'padding', 'border_radius']
        for key in required_keys:
            if key not in style_data:
                raise ValueError(f"Style data missing required key: {key}")

        # 验证字体文件是否存在
        for file in font_files:
            if not os.path.exists(file):
                raise FileNotFoundError(f"Font file not found: {file}")

        # 添加样式
        self.styles[style_id] = {
            'data': style_data,
            'font_files': font_files
        }

    def get_style(self, style_id):
        return self.styles.get(style_id, {}).get('data', {})

    def get_style_font_files(self, style_id):
        return self.styles.get(style_id, {}).get('font_files', [])

    def ensure_styles_dir(self):
        os.makedirs(self.styles_dir, exist_ok=True)
        if not os.path.exists(os.path.join(self.styles_dir, 'default', 'style.json')):
            self.create_default_style()

    def create_default_style(self):
        default_style = {
            "name": "default",
            "floating_window_color": "#FFFFFF",
            "font_color": "#000000",
            "font_size": 24,
            "fade_in_time": 200,
            "fade_out_time": 500,
            "display_time": 1000
        }
        default_style_path = os.path.join(self.styles_dir, 'default')
        os.makedirs(default_style_path, exist_ok=True)
        with open(os.path.join(default_style_path, 'style.json'), 'w') as f:
            json.dump(default_style, f, indent=2)

    def load_styles(self):
        self.styles = {}
        for style_name in os.listdir(self.styles_dir):
            style_path = os.path.join(self.styles_dir, style_name)
            if os.path.isdir(style_path):
                with open(os.path.join(style_path, 'style.json'), 'r') as f:
                    self.styles[style_name] = json.load(f)

    def get_style_names(self):
        return list(self.styles.keys())

    def get_style(self, style_name=None):
        # 如果请求的样式不存在，返回 default_simple 样式
        if style_name is None:
            style_name = self.current_style
        return self.styles.get(style_name, {}).get('data', self.styles.get('default_simple', {}).get('data', {}))

    def remove_style(self, style_name):
        if style_name in self.styles:
            shutil.rmtree(os.path.join(self.styles_dir, style_name))
            del self.styles[style_name]

    def download_style_from_github(self, repo_owner, repo_name, style_name):
        base_url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/main/styles/{style_name}"
        style_data_url = f"{base_url}/style.json"
        
        response = requests.get(style_data_url)
        if response.status_code == 200:
            style_data = response.json()
            icon_files = {}
            
            for key, icon_file in style_data['icons'].items():
                icon_url = f"{base_url}/{icon_file}"
                icon_response = requests.get(icon_url)
                if icon_response.status_code == 200:
                    local_path = os.path.join(self.styles_dir, style_name, icon_file)
                    os.makedirs(os.path.dirname(local_path), exist_ok=True)
                    with open(local_path, 'wb') as f:
                        f.write(icon_response.content)
                    icon_files[key] = local_path
            
            # 下载字体文件
            for font_file in style_data.get('fonts', []):
                font_url = f"{base_url}/{font_file}"
                font_response = requests.get(font_url)
                if font_response.status_code == 200:
                    local_path = os.path.join(self.styles_dir, style_name, font_file)
                    os.makedirs(os.path.dirname(local_path), exist_ok=True)
                    with open(local_path, 'wb') as f:
                        f.write(font_response.content)
            
            self.add_style(style_name, style_data, icon_files, [])
            return True
        return False

    def download_style_from_url(self, style_url):
        try:
            response = requests.get(f"{style_url}/style.json")
            response.raise_for_status()
            style_data = response.json()
            style_name = style_data['name']
            
            style_path = os.path.join(self.styles_dir, style_name)
            os.makedirs(style_path, exist_ok=True)
            
            for key, icon_file in style_data['icons'].items():
                icon_url = f"{style_url}/{icon_file}"
                icon_response = requests.get(icon_url)
                icon_response.raise_for_status()
                with open(os.path.join(style_path, icon_file), 'wb') as f:
                    f.write(icon_response.content)
            
            # 下载字体文件
            for font_file in style_data.get('fonts', []):
                font_url = f"{style_url}/{font_file}"
                font_response = requests.get(font_url)
                font_response.raise_for_status()
                with open(os.path.join(style_path, font_file), 'wb') as f:
                    f.write(font_response.content)
            
            with open(os.path.join(style_path, 'style.json'), 'w') as f:
                json.dump(style_data, f)
            
            self.styles[style_name] = style_data
            return style_name
        except requests.RequestException as e:
            print(f"Error downloading style: {e}")
            return None

    def import_local_style(self, style_path):
        try:
            with open(os.path.join(style_path, 'style.json'), 'r') as f:
                style_data = json.load(f)
            
            style_name = style_data['name']
            new_style_path = os.path.join(self.styles_dir, style_name)
            
            if os.path.exists(new_style_path):
                return None, "样式名称已存在"
            
            shutil.copytree(style_path, new_style_path)
            self.styles[style_name] = style_data
            return style_name, None
        except Exception as e:
            return None, str(e)

    def load_style(self, style_name):
        if style_name in self.styles:
            self.current_style = style_name
        else:
            print(f"Style '{style_name}' not found, using default style.")
            self.current_style = 'default'
        return self.get_style()

    def get_font_path(self, font_name):
        for style_name, style_data in self.styles.items():
            font_path = os.path.join(self.styles_dir, style_name, font_name)
            if os.path.exists(font_path):
                return font_path
        return None  # 如果找不到字件，返回 None

    def get_style_font(self, style_name=None):
        style = self.get_style(style_name)
        font_family = style.get('font_family', 'Roboto-Medium.ttf')
        return self.get_font_path(font_family)

    def get_all_fonts(self):
        fonts = {}
        for style_name, style_data in self.styles.items():
            style_dir = os.path.join(self.styles_dir, style_name)
            for file in os.listdir(style_dir):
                if file.lower().endswith('.ttf'):
                    fonts[file] = os.path.join(style_dir, file)
        return fonts
