import csv
import os
import logging
import sys
from progress.bar import IncrementalBar
from torf import Torrent
from pathlib import Path
import time
import subprocess
from config_loader import config
from ffmpeg import screenshot_from_video
import random
import requests
logging.basicConfig(level=logging.INFO)

def get_largest_video_file(folder_path):
    largest_size = 0
    largest_file = None
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path) and file.endswith(('.mp4', '.mkv', '.avi', '.mov')):
            size = os.path.getsize(file_path)
            if size > largest_size:
                largest_size = size
                largest_file = file_path
    return largest_file

def get_resolution_id(resolution):
    resolution_map = {
        "4320p": 1,
        "2160p": 2,
        "1080p": 3,
        "1080i": 4,
        "720p": 5
    }
    resolution_id = resolution_map.get(resolution)
    if resolution_id is None:
        logging.error("分辨率判定有误，请检查")
        sys.exit(1)
    return resolution_id

def generate_mediainfo(file_path):
    mediainfo_output = subprocess.check_output(['mediainfo', file_path], text=True)
    return mediainfo_output

def start_seeding(csv_file):
    log_file = os.path.dirname(os.path.abspath(csv_file))
    torrent_dir = config.torrent_dir  # 从配置文件中获取种子文件存放路径

    updated_rows = []  # 用于存储更新后的数据行

    # 读取 CSV 文件并查找未发种的条目
    with open(csv_file, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        headers = next(reader)  # 读取并保存标题行
        updated_rows.append(headers)  # 将标题行添加到更新后的数据行列表中
        for row in reader:
            file_path = row[0]
            tmdb_id = row[1]
            category_id = row[2]
            child = row[3]
            season = row[4]
            resolution = row[5]
            type_id = row[6]
            maker = row[7]
            upload_name = row[8]
            status = row[9]
            resolution_id = get_resolution_id(resolution)
            if status == '0':  # 假设 '0' 表示未发种
                file_name = os.path.basename(file_path)  # 获取文件名
                torrent_name = os.path.splitext(file_name)[0]  # 移除文件后缀
                torrent_file = os.path.join(torrent_dir, f"{torrent_name}.torrent")
                # 检查是否存在对应的 torrent 文件
                if not os.path.exists(torrent_file):
                    # 制作种子
                    logging.info(f"正在为 {file_name} 制作种子...")
                    torrent_file = create_torrent(file_path, torrent_name, torrent_dir)
                if torrent_file:
                    largest_video_file = get_largest_video_file(file_path)
                    if largest_video_file:
                        mediainfo = generate_mediainfo(largest_video_file)
                        pic_urls = screenshot_from_video(largest_video_file,log_file)
                        internal = 1 if maker.lower() == "kimoji" else 0
                        if internal:
                            fl_until =3
                            n = random.randint(1, 10)
                            description = f"""
                            [center][color=#bbff88][size=24][b][spoiler=Made By Kimoji][img]https://kimoji.club/img/friendsite/kimoji{n}.webp[/img][/spoiler][/b][/size][/color]
                            [color=#bbff88][size=24][b][spoiler=截图赏析]{pic_urls}[/spoiler][/b][/size][/color][/center]
                            """
                        else:
                            fl_until =1
                            description = f"""
                            [center][color=#bbff88][size=24][b][spoiler=转载致谢][img]https://kimoji.club/img/friendsite/{maker}.webp[/img][/spoiler][/b][/size][/color]
                            [color=#bbff88][size=24][b][spoiler=截图赏析]{pic_urls}[/spoiler][/b][/size][/color][/center]
                            """
                    else:
                        logging.error("文件夹中未找到视频文件，请核查")
                        row[9] = '1'  # 更新 status 为 '1'，表示处理失败或跳过
                upload_torrent(torrent_file, upload_name, description, mediainfo, category_id, type_id, resolution_id, season, tmdb_id, child, internal, fl_until)

                updated_rows.append(row)
            updated_rows.append(row)  # 将当前行添加到更新后的数据行列表中

        with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(updated_rows)


def create_torrent(directory, torrent_name, torrent_dir, comment="KIMOJI PARK", tracker="https://kimoji.club/announce"):
    content_path = os.path.join(directory)
    torrent_path = os.path.join(torrent_dir, f"{torrent_name}.torrent")
    print(f'torrent_path:{torrent_path}')
    logging.info(f'开始制作种子，种子保存路径{torrent_path}')

    piece_size = 4 * 1024 * 1024
    max_attempts = 3
    path = Path(content_path)
    torrent = Torrent(path=str(path.absolute()), trackers=[tracker], piece_size=piece_size, private=True,
                      created_by="KIMOJI PARK", source="KIMOJI PARK")

    # 设置创建时间为当前时间
    torrent.created = int(time.time())

    bar = IncrementalBar('阿K正在努力制种', max=torrent.pieces, suffix="%(index)d/%(max)d [%(eta_td)s]")

    def cb(__torrent: Torrent, path: str, hashed_pieces: int, total_pieces: int):
        bar.next()

    for attempt_count in range(max_attempts):
        if Path(torrent_path).exists():
            try:
                os.remove(torrent_path)
            except Exception as e:
                logging.error(f"删除已存在的种子文件时出错: {e}")
        try:
            torrent.generate(callback=cb, interval=0)
            torrent.write(str(torrent_path))
            logging.info(f"种子文件已创建: {torrent_path}")
            bar.finish()
            return torrent_path
        except Exception as e:
            logging.error(f"创建种子文件时出错: {e}")
            bar.next()
            if attempt_count + 1 < max_attempts:
                logging.warning(f"重试制作种子（第 {attempt_count + 1} 次）")
            else:
                logging.error("达到最大重试次数，停止尝试")
                sys.exit()

    bar.finish()
    return None

def upload_torrent(torrent_file_path, upload_name, description, mediainfo, category_id, type_id, resolution_id, season, tmdb_id, child, internal, fl_until):
    url = 'https://kimoji.club/api/torrents/upload'  # 更改为您的站点API端点
    headers = {
        'Authorization': f'Bearer {config.apikey}',
        'Accept': 'application/json',
    }
    files = {
        'torrent': open(torrent_file_path, 'rb')
    }
    data = {
        'name': upload_name,
        'description': description,
        'mediainfo': mediainfo,
        'category_id': category_id,
        'type_id': type_id,
        'resolution_id': resolution_id,
        'season_number': season,
        'tmdb': tmdb_id,
        'imdb': 0,
        'tvdb': 0,
        'mal': 0,
        'igdb': 0,  # 假设游戏数据库ID不适用，设为0
        'anonymous': 0,
        'sd': child,
        'free': 100,
        'episode_number':0,
        'fl_until': fl_until,
        'sticky': config.sticky,
        'stream': config.stream,
        'featured': config.stream,
        'doubleup': config.doubleup,
        'internal': internal,
        'personal_release': 0  # 如果是个人作品可以设置为 1
    }

    response = requests.post(url, headers=headers, files=files, data=data)

    if response.status_code == 200:
        print(f"种子上传成功: {response.json()}")
        return response.json()
    else:
        print(f"种子上传失败: {response.text}")
        return None