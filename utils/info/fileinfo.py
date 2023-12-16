import yaml
import os
import re
import csv
from tmdbv3api import TMDb, Movie, TV
tmdb = TMDb()
tmdb.api_key = '107492d808d58cb5f5fae5005c7d764d'
tmdb.language = 'zh-CN'

movie = Movie()
tv = TV()
def load_config(config_path):
    """
    加载 YAML 配置文件并返回配置字典。
    """
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config

def is_video_file(filename):

    video_file_extensions = ['.mp4', '.avi', '.mkv', '.flv', '.mov', '.wmv']
    return any(filename.lower().endswith(ext) for ext in video_file_extensions)

def sanitize_folder_name(folder_name):
    safe_name = re.sub(r'[^a-zA-Z0-9_\-\s]', '_', folder_name)
    return safe_name
def find_video_folders(path, log_directory):
    """
    遍历给定路径并找到所有包含视频文件的文件夹。
    清理文件夹名称并将它们写入日志文件。
    """
    video_folders = []

    # 遍历目录
    for root, dirs, files in os.walk(path):
        for file in files:
            if is_video_file(file):
                # 重命名文件夹并提取信息
                new_name, category_id = rename_and_extract_info(root)
                video_folders.append((new_name, category_id))
                break  # 一旦在一个文件夹中找到视频文件就停止查找

    # 写入日志文件
    log_path = os.path.join(log_directory, 'filelog.csv')
    os.makedirs(log_directory, exist_ok=True)  # 如果不存在则创建日志目录
    with open(log_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for folder_name, category_id in video_folders:
            writer.writerow([folder_name, category_id])

    return video_folders
# 加载配置文件
config_path = '/path/to/your/config.yaml'  # 将这里的路径替换为你的配置文件路径
config = load_config(config_path)
path_to_search = config['basic']['file_dir']
log_directory = '/path/to/log/directory'  # 替换为你希望存储日志文件的路径
find_video_folders(path_to_search, log_directory)

# 使用配置文件中的路径
path_to_search = config['basic']['file_dir']
log_directory = '/path/to/log/directory'  # 替换为你希望存储日志文件的路径

# 调用函数
find_video_folders(path_to_search, log_directory)
