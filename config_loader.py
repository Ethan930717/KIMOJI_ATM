# config_loader.py
import os
import yaml

class Config:
    def __init__(self, config_path):
        self.load_config(config_path)

    def load_config(self, config_path):
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            self.file_dir = config['basic']['file_dir']
            self.torrent_dir = config['basic']['torrent_dir']
            self.apikey = config['basic']['apikey']
            self.agent = config['basic']['agent']
            self.pic_num = config['basic']['pic_num']
            self.internal = config['basic']['internal']
            self.personal = config['basic']['personal']

            # qbittorrent 和 transmission 的配置
            self.qb_url = config['qbittorrent']['url']
            self.qb_port = config['qbittorrent']['port']
            self.qb_username = config['qbittorrent']['username']
            self.qb_password = config['qbittorrent']['password']
            self.qb_save_path = config['qbittorrent']['save_path']

            self.tr_address = config['transmission']['address']
            self.tr_port = config['transmission']['port']
            self.tr_username = config['transmission']['username']
            self.tr_password = config['transmission']['password']
            self.tr_save_path = config['transmission']['save_path']

# 获取当前文件的绝对路径
current_directory = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(current_directory, 'config.yaml')
config = Config(config_path)
