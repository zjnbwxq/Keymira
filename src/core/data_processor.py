import json
from datetime import datetime
import os
from pathlib import Path

class DataProcessor:
    def __init__(self):
        self.key_counts = {}
        self.data_file = os.path.join(os.path.expanduser('~'), '.keymira', 'key_data.json')
        self.load_data()

    def process_key(self, key):
        keys = key.split('+')
        for k in keys:
            k = k.strip().lower()  # 去除首尾空格并转换为小写
            if k == '':
                k = 'space'  # 将空字符串视为空格键
            if k in self.key_counts:
                self.key_counts[k] += 1
            else:
                self.key_counts[k] = 1
        self.save_data()  # 不再传递参数

    def get_key_stats(self):
        return self.key_counts

    def save_data(self):  # 移除 data 参数
        path = Path(self.data_file).parent
        if not path.exists():
            path.mkdir(parents=True)
        with open(self.data_file, 'w') as f:
            json.dump(self.key_counts, f)  # 直接使用 self.key_counts

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.key_counts = json.load(f)
            except json.JSONDecodeError:
                print(f"文件 {self.data_file} 格式错误，将创建新的数据文件。")
                self.key_counts = {}
        else:
            print(f"文件 {self.data_file} 不存在，将创建新的数据文件。")
            self.key_counts = {}

    def clear_data(self):
        self.key_counts = {}
        if os.path.exists(self.data_file):
            os.remove(self.data_file)
