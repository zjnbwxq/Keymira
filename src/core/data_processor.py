<<<<<<< HEAD
<<<<<<< HEAD
import json
from datetime import datetime
import os
from pathlib import Path

class DataProcessor:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.key_counts = {}
        self.data_file = os.path.join(os.path.expanduser('~'), '.keymira', 'key_data.json')
        self.load_data()

    def process_key(self, key):
        if key in self.key_counts:
            self.key_counts[key] += 1
        else:
            self.key_counts[key] = 1
        self.save_data()

    def get_key_stats(self):
        return {
            'key_count': sum(self.key_counts.values()),
            'word_count': len(self.key_counts)
        }

    def save_data(self):
        # 保存数据到 config_manager
        self.config_manager.set('key_counts', self.key_counts)

    def load_data(self):
        # 从 config_manager 加载数据
        self.key_counts = self.config_manager.get('key_counts', {})

    def clear_data(self):
        self.key_counts = {}
        if os.path.exists(self.data_file):
            os.remove(self.data_file)
=======
>>>>>>> parent of 42d14a8 (实现基本前后端)
=======
>>>>>>> parent of 42d14a8 (实现基本前后端)
