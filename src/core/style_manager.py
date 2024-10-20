import os
import json
import shutil
import requests
from PyQt5.QtCore import QSettings

class StyleManager:
    def __init__(self):
        self.styles_dir = os.path.join(os.path.expanduser('~'), '.keymira', 'styles')
        self.ensure_styles_dir()
        self.load_styles()
        self.current_style = 'default'

    def ensure_styles_dir(self):
        os.makedirs(self.styles_dir, exist_ok=True)

    def load_styles(self):
        self.styles = {}
        for style_name in os.listdir(self.styles_dir):
            style_path = os.path.join(self.styles_dir, style_name)
            if os.path.isdir(style_path):
                with open(os.path.join(style_path, 'style.json'), 'r') as f:
                    self.styles[style_name] = json.load(f)

    def get_style_names(self):
        return list(self.styles.keys())

    def get_style(self, style_name):
        return self.styles.get(style_name)

    def add_style(self, style_name, style_data, icon_files):
        style_path = os.path.join(self.styles_dir, style_name)
        os.makedirs(style_path, exist_ok=True)
        
        for key, file_path in icon_files.items():
            shutil.copy(file_path, os.path.join(style_path, os.path.basename(file_path)))
        
        style_data['icons'] = {k: os.path.basename(v) for k, v in icon_files.items()}
        
        with open(os.path.join(style_path, 'style.json'), 'w') as f:
            json.dump(style_data, f, indent=2)
        
        self.styles[style_name] = style_data

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
            
            self.add_style(style_name, style_data, icon_files)
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
        self.current_style = style_name
        # 加载指定的样式
        
    def get_style(self):
        # 返回当前样式的设置
        return {}
