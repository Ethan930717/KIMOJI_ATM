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
import qbittorrentapi
import transmission_rpc
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def remove_ffmpeg_containers():
    try:
        logging.info("开始清除冗余ffmpeg容器")
        cmd = "docker ps -a | grep 'ffmpeg' | awk '{print $1}' | xargs -I {} docker rm {}"
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"删除 Docker 容器时出错: {e}")
        sys.exit(1)
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
    logger.info(f'提取体积最大的视频文件路径{largest_file}')
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
    torrent_dir = config.torrent_dir

    with open(csv_file, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        rows = list(reader)  # 读取所有行

    headers = rows[0]  # 保存标题行
    rows = rows[1:]  # 剩余的数据行

    for index, row in enumerate(rows):
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
        remove_ffmpeg_containers() #清除冗余ffmpeg容器
        if status == '0':
            logger.info(f'开始对文件夹"{file_path}"进行发种操作')
            logger.info(f'开始对"{upload_name}"进行查重')
            url = f"https://kimoji.club/api/torrents/filter?name={upload_name}&api_token={config.apikey}"
            response = requests.get(url)
            if response.status_code == 200:
                response_data = response.json()
                # 检查响应中的每个种子是否包含 'id' 字段
                if any('id' in torrent_data for torrent_data in response_data.get('data', [])):
                    logger.warning(f"种子 '{upload_name}' 已存在。跳过当前文件")
                    row[9] = '3'  # 更新CSV文件中的状态为 '3'
                    rows[index] = row
                    continue  # 跳过当前循环
                else:
                    # 如果种子不存在，继续进行发种
                    logger.info(f"查重通过，继续发种")
                    file_name = os.path.basename(file_path)  # 获取文件名
                    torrent_file = os.path.join(torrent_dir, f"{file_name}.torrent")
                    # 检查是否存在对应的 torrent 文件
                    if not os.path.exists(torrent_file):
                        # 制作种子
                        logging.info(f"正在为 {file_name} 制作种子...")
                        torrent_file = create_torrent(file_path, file_name, torrent_dir)
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
                    response_json = upload_torrent(torrent_file, upload_name, description, mediainfo, category_id, type_id, resolution_id, season, tmdb_id, child, internal, fl_until)
                    if 'data' in response_json:
                        data = response_json['data']
                        if 'name' in data and "该名称已经被使用过了" in data['name'] or 'info_hash' in data and "该 info hash 已经被使用过了" in data['info_hash']:
                            logger.warning("种子已存在,跳过当前资源")
                            row[9] = '3'  # 更新状态为 '3'
                            rows[index] = row
                            continue  # 跳过当前循环
                    if 'data' in response_json and response_json['success']:
                        download_link = response_json['data']
                        seeding_success = add_torrent_based_on_agent(download_link)
                        if seeding_success:
                            logger.info("种子已成功添加到下载器并开始做种")
                            update_row_status(rows, index, seeding_success, download_link)
                        else:
                            logger.error("种子添加到下载器失败，请手动处理")
                            update_row_status(rows, index, False, None, error=True, response_json=response_json)
                    else:
                        logger.error("无法从响应中提取种子下载地址")
                        row[9] = '-1'  # 标记为处理失败
                        rows[index] = row  # 更新行列表
                        # 将更新后的数据写回 CSV 文件
                        with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
                            writer = csv.writer(file)
                            writer.writerow(headers)  # 写入标题行
                            writer.writerows(rows)  # 写入更新后的数据行
            # 检查是否还有未处理的种子
            remaining = any(row[9] == '0' for row in rows)
            if not remaining:
                print("没有可以发送的种子，请先生成信息")

def update_row_status(rows, index, seeding_success, download_link, error=False, response_json=None):
    row = rows[index]
    if error and response_json:
        # 将 JSON 错误消息转换为中文
        error_message = json.dumps(response_json, ensure_ascii=False)
        row[9] = '-1'  # 标记为处理失败
        row.append("种子发送失败，错误信息：" + error_message)
    else:
        if seeding_success:
            row[9] = '3'  # 标记为做种成功
            row.append(download_link)
        else:
            row[9] = '2'  # 标记为做种失败
            row.append(download_link if download_link else "N/A")
    rows[index] = row  # 更新行列表

def create_torrent(directory, file_name, torrent_dir, comment="KIMOJI PARK", tracker="https://kimoji.club/announce"):
    content_path = os.path.join(directory)
    torrent_path = os.path.join(torrent_dir, f"{file_name}.torrent")
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
        logger.info(f"种子上传成功: {response.json()}")
        return response.json()
    else:
        logger.error(f"种子上传失败: {response.text}")
        return None


def add_torrent_based_on_agent(download_link, max_retries=3):
    agent = config.agent
    logger.info(f'检测到当前选择的下载器为{agent}')
    success = False  # 默认设置为未成功
    if agent == 'qb':
        logger.info('正在尝试将种子添加到qbittorrent')
        success = add_torrent_to_qbittorrent(download_link, max_retries=max_retries)
    elif agent == 'tr':
        logger.info('正在尝试将种子添加到transmission')
        success = add_torrent_to_transmission(download_link, max_retries=max_retries)
    else:
        logger.error("未正确指定做种下载器，请手动做种")
    if success:
        logger.info("种子添加成功")
    else:
        logger.error("种子添加失败")
    return success


def add_torrent_to_qbittorrent(download_link, skip_checking=True, max_retries=3):
    qbt_client = qbittorrentapi.Client(
        host=config.qb_url,
        port=config.qb_port,
        username=config.qb_username,
        password=config.qb_password
    )
    try:
        qbt_client.auth_log_in()
    except Exception as e:
        logger.error(f"登录失败: {e}")
        return False

    retries = 0
    while retries < max_retries:
        try:
            qbt_client.torrents_add(
                urls=[download_link],
                category='KIMOJI',
                save_path=config.qb_save_path,
                skip_checking=skip_checking
            )
            print("种子添加成功,小K收工啦")
            return True
        except Exception as e:
            retries += 1
            logger.warning(f"添加种子时发生错误: {e}")
            if retries >= max_retries:
                logger.error("达到最大重试次数，停止尝试")
                logger.error(f"种子添加失败，种子链接 {download_link}，请尝试手动添加。")
                return False
            logger.warning(f"正在尝试第 {retries} 次重试")
            time.sleep(5)
def add_torrent_to_transmission(download_link, max_retries=3):
    # 初始化 Transmission 客户端
    tc = transmission_rpc.Client(
        host=config.tr_address,
        port=config.tr_port,
        username=config.tr_username,
        password=config.tr_password
    )

    retries = 0
    while retries < max_retries:
        try:
            # 添加种子
            tc.add_torrent(download_link, download_dir=config.tr_save_path)

            print("种子成功添加到Transmission，小K收工啦")
            return True
        except Exception as e:
            retries += 1
            logger.warning(f"添加种子时发生错误: {e}")
            if retries >= max_retries:
                logger.error("达到最大重试次数，停止尝试")
                logger.error(f"种子添加失败，种子链接 {download_link}，请尝试手动添加。")
                return False

            logger.warning(f"正在尝试第 {retries} 次重试")
            time.sleep(5)
