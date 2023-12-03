import cloudscraper
from bs4 import BeautifulSoup
import logging
import os
import re
import sys
import csv
import datetime
from utils.progress.agent import add_torrent_based_on_agent
current_file_path = os.path.abspath(__file__)
project_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
log_dir = os.path.join(project_root_dir, 'log')
os.makedirs(log_dir, exist_ok=True)
log_file_path = os.path.join(log_dir, 'kimoji.html')
log_csv_path = os.path.join(log_dir, 'record.csv')

logger = logging.getLogger(__name__)

# 获取登录页面的XSRF Token
def get_xsrf_token(url, scraper):
    response = scraper.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    token = soup.find('input', {'name': '_token'})
    return token['value'] if token else None

# 此函数模拟登录过程
def login(login_url, username, password, scraper):
    xsrf_token = get_xsrf_token(login_url, scraper)
    if not xsrf_token:
        print("无法获取登录页面的XSRF Token")
        return False, None

    login_data = {
        '_token': xsrf_token,
        'username': username,
        'password': password,
    }
    response = scraper.post(login_url, data=login_data)
    return response.ok, scraper

def kimoji_upload(torrent_path, file_name, username, password, chinese_title, english_title, year, season, media, codec, audiocodec, maker, pic_urls, tmdb_id, imdb_id, media_type, child, resolution , bd_info, internal,personal,keywords,upload_title, mediainfo_output ,chinese_name,media_type):
    episode = "0"
    logger.info(f'已选择类型为{media_type}')
    if not season and (not media_type =='anime-movie' or not media_type =='movie'):
        season = "0"
    if media_type == 'anime-tv':
        select_type='4'
    elif media_type == 'anime-movie':
        select_type='3'
        season = ""
        episode = ""
    elif media_type == 'doc':
        select_type='6'
    elif media_type == 'show':
        select_type='5'
    elif media_type == 'series':
        select_type='2'
    elif media_type == 'movie':
        select_type='1'
        season = ""
        episode = ""
    else:
        select_type='2'
    logger.info(f'已成功选择类型为{media_type}')

    #选择规格
    if 'REMUX' in file_name.upper():
        medium_sel='3'
        logger.info('已成功选择媒介为REMUX')
    elif 'WEB-DL' in file_name.upper():
        medium_sel='4'
        logger.info('已成功选择媒介为WEB-DL')
    elif media.upper() == 'UHD' and ('x264' in file_name.lower() or 'x265' in file_name.lower()):
        medium_sel='5'
        logger.info('已成功选择媒介为ENCODE')
    elif media.upper() == 'BLURAY' and ('x264' in file_name.lower() or 'x265' in file_name.lower()):
        medium_sel='5'
        logger.info('已成功选择媒介为ENCODE')
    elif media.upper() == 'BLU-RAY' and ('x264' in file_name.lower() or 'x265' in file_name.lower()):
        medium_sel='3'
        logger.info('已成功选择媒介为ENCODE')
    elif media.upper() == 'UHD':
        medium_sel='1'
        logger.info('已成功选择媒介为UHD')
    elif media.upper() == 'BLURAY' or media.upper() == 'BLU-RAY':
        medium_sel='2'
        logger.info('已成功选择媒介为BLURAY')
    elif media.upper() == 'ENCODE':
        medium_sel='5'
        logger.info('已成功选择媒介为ENCODE')
    elif media.upper() == 'HDTV':
        medium_sel='6'
        logger.info('已成功选择媒介为HDTV')
    elif media.upper() == 'FLAC':
        medium_sel='7'
        logger.info('已成功选择媒介为FLAC')
    elif media.upper() == 'ALAC':
        medium_sel='8'
        logger.info('已成功选择媒介为FLAC')
    elif media.upper() == 'DVD':
        medium_sel='9'
        logger.info('已成功选择媒介为DVD')
    elif media.upper() == 'MP3':
        medium_sel='11'
        logger.info('已成功选择媒介为MP3')
    else:
        medium_sel='4'
        logger.info('未识别到媒介信息，默认选择WEB-DL')


    # 选择分辨率
    if resolution == "4320p":
        standard_sel = '1'
    elif resolution == "2160p":
        standard_sel = '2'
    elif resolution == "1080p":
        standard_sel = '3'
    elif resolution == "1080i":
        standard_sel = '4'
    elif resolution == "720p":
        standard_sel = '5'
    else:
        standard_sel = '6'
    logger.info('已成功选择分辨率为' + resolution)

    if season:
        season = int(season)
        logger.info(f'发布资源为第{season}季')
    else:
        season = ""
    if child == 1:
        logger.info('识别到当前资源为儿童资源，已勾选PG-12标签')
    if not imdb_id:
        imdb_id = "0"
    if keywords:
        keywords= ', '.join(keywords)
        logger.info(f'拉取关键词:\n{keywords}')
    else:
        keywords = ""

    if maker and not (personal == 1  or internal == 1):
        pic_urls = f"""
        [center][color=#bbff88][size=24][b][spoiler=转载致谢][img]https://kimoji.club/img/friendsite/{maker}.png[/img][/spoiler][/b][/size][/color]
        [color=#bbff88][size=24][b][spoiler=截图赏析]
        {pic_urls}[/spoiler][/b][/size][/color][/center]
        """

    if not chinese_title and chinese_name:
        upload_title = upload_title.replace("None", chinese_name)

    scraper = cloudscraper.create_scraper()
    # 登录
    login_url = 'https://kimoji.club/login'
    username = username
    password = password
    logged_in, scraper = login(login_url, username, password, scraper)
    if logged_in:
        logger.info("KIMOJI登陆页面打开成功")
        # 访问种子上传页面并获取新的XSRF Token
        upload_url = 'https://kimoji.club/torrents'
        xsrf_token = get_xsrf_token(upload_url, scraper)
        if not xsrf_token:
            logger.error("无法获取上传页面的XSRF Token")
            return False, "无法获取上传页面的XSRF Token"
        else:
            print("获取到的XSRF Token:", xsrf_token)
            # 准备上传文件
            torrent_file = torrent_path
            with open(torrent_file, 'rb') as torrent_file_opened:
                files = {
                    'torrent': (os.path.basename(torrent_file), torrent_file_opened, 'application/x-bittorrent'),
                    # 'nfo': ('file.nfo', open('file.nfo', 'rb'), 'text/plain'),
                    # 'torrent-cover': ('cover.jpg', open('cover.jpg', 'rb'), 'image/jpeg'),
                    # 'torrent-banner': ('banner.jpg', open('banner.jpg', 'rb'), 'image/jpeg')
                }
                form_data = {
                    '_token': xsrf_token,
                    '_method': 'post',
                    'name': upload_title,
                    'category_id': select_type,
                    'type_id': medium_sel,
                    'resolution_id': standard_sel,
                    'distributor_id':'',
                    'region_id':'',
                    'season_number': season,
                    'episode_number': episode,
                    'tmdb': tmdb_id,
                    'imdb': imdb_id,
                    'tvdb': "0",
                    'mal': "0",
                    'igdb': '0',
                    'keywords': keywords,
                    'description': pic_urls,
                    'mediainfo':mediainfo_output,
                    'bdinfo': bd_info,
                    'anon': '0', #默认不匿名
                    'stream': '0', #默认非补档资源
                    'sd': child,
                    'internal': internal,
                    'personal_release': personal,
                    'mod_queue_opt_in': '0',
                    'refundable': '0',
                    'free': '100',
                    'post': 'true',
                    'isPreviewEnabled': '0',
                }
                log_prepared_request(upload_url, form_data, files, log_file_path)
                response = scraper.post(upload_url, files=files, data=form_data)
                log_request_response_details(response, log_file_path)

                if response.ok:
                    if response.history:
                        torrent_page_url = response.url
                        if "download_check" in torrent_page_url:
                            # 发种成功，修改URL获取下载链接
                            torrent_download_url = re.sub("download_check", "download", torrent_page_url)
                            logger.info(f"种子下载URL: {torrent_download_url},正在尝试下载种子并添加到下载器")
                            temp_torrent_path = os.path.join('log', 'temp.torrent')
                            file_path = os.path.join(file_name, "kimoji_exclude")
                            log_to_csv(file_name, "成功", log_csv_path, torrent_page_url)
                            open(file_path, 'w').close()
                            if download_torrent_file_with_scraper(scraper, torrent_download_url, temp_torrent_path):
                                add_torrent_based_on_agent(temp_torrent_path, project_root_dir)
                            else:
                                logger.error("下载种子文件失败，请手动做种")
                                file_path = os.path.join(file_name, "kimoji_pass")
                                open(file_path, 'w').close()
                                return False
                        else:
                            logger.error("发种未成功，未找到期望的重定向URL，请查看日志，已跳过本资源")
                            file_path = os.path.join(file_name, "kimoji_pass")
                            open(file_path, 'w').close()
                            log_to_csv(file_name, "失败", log_csv_path, "")
                            with open(log_file_path, 'w', encoding='utf-8') as log_file:
                                log_file.write(response.text)
                            return False
                        bdinfo_file_path = os.path.join(log_dir, 'BDINFO.bd.txt')
                        if os.path.exists(bdinfo_file_path):
                            try:
                                os.remove(bdinfo_file_path)
                            except Exception as e:
                                logger.error(f"删除文件时发生错误: {e}")
                        else:
                            pass
                    else:
                        logger.error("发种请求未发生重定向，请查看日志，已跳过本资源")
                        file_path = os.path.join(file_name, "kimoji_pass")
                        open(file_path, 'w').close()

                        log_to_csv(file_name, "失败", log_csv_path, "")
                        with open(log_file_path, 'w', encoding='utf-8') as log_file:
                            log_file.write(response.text)
                        return False
                else:
                    logger.error("种子上传失败，请查看日志")
                    with open(log_file_path, 'w', encoding='utf-8') as log_file:
                        log_file.write(response.text)
                    return False
    else:
        logger.error("KIMOJI登陆页面打开失败，请检查网站运行状况")
        return False

def download_torrent_file_with_scraper(scraper, torrent_url, save_path):
    try:
        response = scraper.get(torrent_url)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(response.content)
        logger.info("种子下载成功")
        return True
    except Exception as e:
        logger.error(f"下载种子文件失败: {e}")
        return False

def log_request_response_details(response, log_directory):
    log_file_name = "requests_log.txt"  # 定义日志文件名
    parent_directory = os.path.dirname(log_directory)  # 获取上一级目录
    log_file_path = os.path.join(parent_directory, log_file_name)  # 创建完整的文件路径

    with open(log_file_path, 'w', encoding='utf-8') as log_file:
        log_file.write("请求URL:\n")
        log_file.write(response.request.url + "\n\n")

        log_file.write("请求方法:\n")
        log_file.write(response.request.method + "\n\n")

        log_file.write("请求头:\n")
        for header, value in response.request.headers.items():
            log_file.write(f"{header}: {value}\n")
        log_file.write("\n")

        # log_file.write("请求体:\n")
        # log_file.write(str(response.request.body) + "\n\n")

        log_file.write("响应头:\n")
        for header, value in response.headers.items():
            log_file.write(f"{header}: {value}\n")
        log_file.write("\n")

        log_file.write("响应体:\n")
        log_file.write(response.text + "\n")

        log_file.write("==================================================\n\n")


def log_prepared_request(url, form_data, files, log_directory):
    log_file_name = "post_data.txt"  # 定义日志文件名
    parent_directory = os.path.dirname(log_directory)  # 获取上一级目录
    log_file_path = os.path.join(parent_directory, log_file_name)  # 创建完整的文件路径
    with open(log_file_path, 'w', encoding='utf-8') as log_file:
        log_file.write("准备发送的请求URL:\n")
        log_file.write(url + "\n\n")

        log_file.write("准备发送的表单数据:\n")
        for key, value in form_data.items():
            log_file.write(f"{key}: {value}\n")
        log_file.write("\n")

        log_file.write("准备发送的文件:\n")
        for file_key, file_value in files.items():
            log_file.write(f"{file_key}: {file_value[0]}\n")  # 只记录文件名
        log_file.write("==================================================\n\n")

def log_to_csv(url_name, status, log_file_path,torrent_url):
    with open(log_file_path, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        writer.writerow([url_name, status, current_time, torrent_url])

