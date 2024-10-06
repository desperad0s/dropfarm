import json
import os

def load_config(bot_name):
    config_path = os.path.join(os.path.dirname(__file__), 'config', f'{bot_name}_config.json')
    with open(config_path, 'r') as config_file:
        return json.load(config_file)