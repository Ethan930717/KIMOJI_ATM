import os
from tmdbv3api import TMDb, Movie, TV
import requests
from bs4 import BeautifulSoup
from pymediainfo import MediaInfo
import re
import logging
import csv
from config_loader import config
logging.basicConfig(level=logging.INFO)

# 初始化 TMDB
tmdb = TMDb()
tmdb.api_key = '107492d808d58cb5f5fae5005c7d764d'
tmdb.language = 'zh-CN'

movie = Movie()
tv = TV()

#模糊搜索逻辑
def preprocess_name_for_search(folder_name):
    # 移除一些常见的无关词汇或符号
    remove_words = ['4k','2160p','1080p','1080i', '720p', 'x264', 'x265', 'HDTV', 'BluRay', 'WEB-DL']
    for word in remove_words:
        folder_name = folder_name.replace(word, '')
    # 替换一些常见符号
    folder_name = folder_name.replace('.', ' ').replace('-', ' ').replace('_', ' ').replace('·', ' ')
    # 如果名称中有空格，只保留空格前的部分
    if ' ' in folder_name:
        folder_name = folder_name.split(' ')[0]
    # 可以在这里加入其他预处理逻辑
    return folder_name.strip()

def is_video_file(filename):
    return filename.endswith(('.mp4', '.mkv', '.avi', '.mov'))

def find_largest_video_file(folder_path):
    largest_size = 0
    video_file = None
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path) and is_video_file(file):
            size = os.path.getsize(file_path)
            if size > largest_size:
                largest_size = size
                video_file = file_path
    return video_file

def should_skip_folder(folder_path):
    return any(os.path.exists(os.path.join(folder_path, skip_file)) for skip_file in ["kimoji_pass", "kimoji_enclude"])

def find_video_folders(base_path):
    folders = []
    for folder in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder)
        if os.path.isdir(folder_path) and not should_skip_folder(folder_path) and "KIMOJI" not in folder:
            video_file = find_largest_video_file(folder_path)
            if video_file:
                folders.append(folder_path)
    return folders

def format_resolution(height, scan_type):
    if height == 1080:
        return '1080p' if scan_type == 'P' else '1080i'
    elif height == 720:
        return '720p'
    elif height == 2160:
        return '2160p'
    elif height == 4320:
        return '4320p'
    else:
        return f"{height}p"

def get_media_info(file_path):
    media_info = MediaInfo.parse(file_path)
    video_tracks = [track for track in media_info.tracks if track.track_type == 'Video']
    audio_tracks = [track for track in media_info.tracks if track.track_type == 'Audio']

    if not video_tracks:
        return None

    video_track = video_tracks[0]
    audio_track = audio_tracks[0] if audio_tracks else None
    audio_count = len(audio_tracks)  # 获取音轨数量


    # 检测视频编码器
    video_codec = video_track.format
    is_encode = False
    if 'x265' in video_track.format_info:
        video_codec = 'x265'
        is_encode = True
    elif 'x264' in video_track.format_info:
        video_codec = 'x264'
        is_encode = True
    elif video_codec == 'AVC':
        video_codec = 'H264'
    elif video_codec == 'HEVC':
        video_codec = 'H265'

    audio_codec = audio_track.format if audio_track else None
    scan_type = 'P' if video_track.scan_type == 'Progressive' else 'I'
    resolution = format_resolution(video_track.height, scan_type)

    # 其他属性，如HDR等
    additional_attrs = []
    if 'HDR' in video_track.format_profile:
        additional_attrs.append('HDR')
    if 'Dolby Vision' in video_track.format_profile:
        additional_attrs.append('DV')
    if video_track.bit_depth:
        bit_depth = video_track.bit_depth
        if bit_depth in ['10', '20']:
            additional_attrs.append(f'{bit_depth}bit')

    return video_codec, audio_codec, resolution, '.'.join(additional_attrs), is_encode, audio_count

def contains_chinese(text):
    return any('\u4e00' <= char <= '\u9fff' for char in text)

def get_details_from_tmdb(id, content_type):
    base_url = "https://www.themoviedb.org"
    url = f"{base_url}/{content_type}/{id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # 获取年份
        year_element = soup.find('span', class_='tag release_date')
        year = year_element.text.strip('()') if year_element else '未知'

        # 获取类别信息
        genres = soup.find('div', class_='facts').find('span', class_='genres').find_all('a') if soup.find('div', class_='facts') and soup.find('div', class_='facts').find('span', class_='genres') else []
        certifications = soup.find('div', class_='facts').find('span', class_='certification').get_text() if soup.find('div', class_='facts') and soup.find('div', class_='facts').find('span', class_='certification') else ""

        # 确定 category_id
        if "16-" in genres:
            category_id = 3 if content_type == 'movie' else 4
            print('判定类别为动漫')
        elif "99-" in genres and content_type == 'tv':
            category_id = 6
            print('判定类别为纪录片')
        elif ("10764" in genres or "10767" in genres) and content_type == 'tv':
            category_id = 5
            print('判定类别为综艺')
        elif content_type == 'tv':
            category_id = 2
            print('判定类别为电视剧')

        else:
            category_id = 1
            print('判定类别为电影')


        # 确定 child
        child = 1 if any(c in certifications for c in ['Y', 'G']) or "10762" in genres else 0

        return year, category_id, child
    else:
        return '未知', None, None

def get_title_from_web(id, content_type, language):
    base_url = "https://www.themoviedb.org"
    if content_type == 'movie':
        url = f"{base_url}/movie/{id}?language={language}"
    elif content_type == 'tv':
        url = f"{base_url}/tv/{id}?language={language}"
    else:
        return '未知'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        title_element = soup.select_one('h2 a')
        return title_element.text.strip() if title_element else '未知'
    else:
        return '未知'

def extract_details(result, result_type):
    if isinstance(result, str):
        return '未知', '未知', '未知', '未知', '未知'

    id = result.id
    title = get_title_from_web(id, result_type, 'zh-CN')
    original_title = get_title_from_web(id, result_type, 'en-US')
    year, category_id, child = get_details_from_tmdb(id, result_type)  # 从网页获取年份

    return title, original_title, year, category_id, child

def get_alternative_title(id, language):
    try:
        if language == 'zh':
            return movie.details(id).translations.translations[0].data.title if movie else \
            tv.details(id).translations.translations[0].data.title
        elif language == 'en':
            return movie.details(id).original_title if movie else tv.details(id).original_name
    except:
        return '未知'

def rename_folder(folder_path):
    folder_name = os.path.basename(folder_path)

    search_name = preprocess_name_for_search(folder_name)

    # 1. 使用TMDB API获取文件夹名称对应的影片信息
    movie_results = [(result, 'movie') for result in movie.search(search_name)]
    tv_results = [(result, 'tv') for result in tv.search(search_name)]
    search_results = movie_results + tv_results

    if search_results:
        for i, (result, result_type) in enumerate(search_results, start=1):
            title, original_title, release_date, category_id, child = extract_details(result, result_type)
            print(f"{i}. 类型: {'电影' if result_type == 'movie' else '电视剧'}, 中文名: {title}, 英文名: {original_title}, 年份: {release_date}")
        user_input = input(
            "如果无法确定列表中对应的影片，请手动在TMDb搜索确认后，输入类型+TMDb ID（例如 'movie300212' 或 'tv12345'）。如果TMDb中没有该词条，请输入 'q'跳过当前文件: ")

        if user_input.lower() == 'q':
            pass_file_path = os.path.join(folder_path, "kimoji_pass")
            with open(pass_file_path, 'w') as pass_file:
                pass_file.write("Skipped by user\n")
            print("已标记当前文件。")
            return None, None, None, None, None
        elif user_input.startswith('movie') or user_input.startswith('tv'):
            if user_input.startswith('movie'):
                selected_type = 'movie'
                tmdb_id = user_input[len('movie'):]  # 从字符串 "movie" 后开始截取
            else:
                selected_type = 'tv'
                tmdb_id = user_input[len('tv'):]  # 从字符串 "tv" 后开始截取

            if selected_type == 'movie':
                selected_result = movie.details(tmdb_id)
            else:
                selected_result = tv.details(tmdb_id)
            title, original_title, release_date, category_id, child = extract_details(selected_result, selected_type)
        else:
            choice = int(user_input) - 1
            selected_result, selected_type = search_results[choice]
            title, original_title, release_date, category_id, child = extract_details(selected_result, selected_type)

        season_num = ''
        if selected_type == 'tv':
            seasons = tv.details(selected_result.id).number_of_seasons
            if seasons > 1:
                season_num_input = input("请输入季数 (仅数字，例如: 1, 2): ")
                season_num = f"S{season_num_input.zfill(2)}."
                # 获取特定季的年份
                release_date = get_season_year_from_web(selected_result.id, season_num_input)
            else:
                season_num = "S01."
                # 如果只有一季，使用电视剧的发布年份
                release_date = release_date


        # 2. 查找并分析最大的视频文件以获取编码和分辨率信息
        largest_video_file = find_largest_video_file(folder_path)
        if largest_video_file:
            video_codec, audio_codec, resolution, additional, is_encode, audio_count = get_media_info(
                largest_video_file)
            if audio_count > 1:
                audio_info = f"{audio_count}Audio {audio_codec}"
            else:
                audio_info = audio_codec
            # 根据是否为Encode来调整文件名
            source_type = 'Encode' if is_encode else 'WEB-DL'
            # 构建新名称，并替换空格为点
            new_name = f"{title}.{original_title}.{season_num}{release_date}.{resolution}.{source_type}.{audio_info}.{video_codec}-{additional}KIMOJI"
            new_name = new_name.replace(' ', '.').replace(':', '').replace('/', '.').strip('.')
            # 处理upload_name
            upload_name = new_name.replace('.', ' ')

            # 处理特殊情况，例如 "5.1" 和 "7.1"
            placeholder_map = {
                "5 10": "PLACEHOLDER_5_10",
                "7 10": "PLACEHOLDER_7_10"
            }
            for original, placeholder in placeholder_map.items():
                upload_name = upload_name.replace(original, placeholder)

            upload_name = re.sub(r'(?<=5) 1', '.1', upload_name)
            upload_name = re.sub(r'(?<=7) 1', '.1', upload_name)

            # 将占位符转换回来
            for placeholder, original in placeholder_map.items():
                upload_name = upload_name.replace(placeholder, original)

            if "-" in new_name:
                maker_candidate = new_name.split('-')[-1]
                if "@" in maker_candidate:
                    maker = maker_candidate.split('@')[-1]
                elif re.match(r'^[A-Za-z0-9_]+$', maker_candidate):
                    maker = maker_candidate
                else:
                    maker_input = input(f'{new_name}\n在文件名中无法获取到制作组信息，请手动输入，确认留空请回车: ')
                    maker = maker_input.strip() if maker_input.strip() != '' else None
            else:
                maker_input = input(f'{new_name}\n在文件名中无法获取到制作组信息，请手动输入，确认留空请回车: ')
                maker = maker_input.strip() if maker_input.strip() != '' else None

            tmdb_id = selected_result.id
            new_path = os.path.join(os.path.dirname(folder_path), new_name)
            os.rename(folder_path, new_path)
            print(f"文件夹重命名为: {new_name}")

            is_tv_show = selected_type == 'tv'
            rename_files_in_folder(new_path, new_name, is_tv_show)
            return new_name, tmdb_id, category_id, child, season_num, resolution, source_type, maker, upload_name
        else:
            print("未找到有效的视频文件。")
            return None, None, None, None, None, None, None, None, None
    else:
        print("没有找到匹配的 TMDB 资源。")
        return None, None, None, None, None, None, None, None, None

def rename_files_in_folder(folder_path, new_folder_name, is_tv_show):
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path):
            file_extension = os.path.splitext(file_path)[1]
            if is_tv_show:
                # 仅替换文件名中的空格为点
                new_file_name = file.replace(' ', '.')
            else:
                # 将文件名更改为与文件夹相同的名称
                new_file_name = new_folder_name + file_extension
            new_file_path = os.path.join(folder_path, new_file_name)
            os.rename(file_path, new_file_path)

def list_folders(base_path):
    folders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f)) and "KIMOJI" not in f]
    if not folders:
        print("目前没有未更名的文件")
    return folders

def get_season_year_from_web(tv_id, season_num):
    url = f"https://www.themoviedb.org/tv/{tv_id}/season/{season_num}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        year_element = soup.find('span', class_='tag release_date')
        if year_element:
            year_text = year_element.text.strip()
            return year_text.strip('()')
        else:
            return '未知'
    else:
        return '未知'

def write_to_log(log_directory, data):
    os.makedirs(log_directory, exist_ok=True)
    log_path = os.path.join(log_directory, 'logfile.csv')

    # 检查文件是否存在，如果不存在，则创建并写入标题
    file_exists = os.path.isfile(log_path)
    with open(log_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # 如果文件不存在，写入标题
        if not file_exists:
            headers = ["路径", "TMDb", "类型", "儿童资源", "季数", "分辨率", "媒介", "制作组", "上传名", "状态"]
            writer.writerow(headers)

        # 写入数据
        writer.writerow(data)

def generate(folder_path):
    # 获取当前工作目录，即main.py所在的目录
    current_directory = os.path.dirname(os.path.realpath(__file__))
    log_directory = os.path.join(current_directory, 'log')

    # 确保日志目录存在
    if not os.path.isdir(log_directory):
        os.mkdir(log_directory)

    # 遍历folder_path下的每个条目
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        # 检查这个条目是否是一个文件夹，并且符合处理条件
        if os.path.isdir(item_path) and not should_skip_folder(item_path) and "KIMOJI" not in item:
            print(f"处理文件夹: {item_path}")
            new_name, tmdb_id, category_id, child, season_num, resolution, source_type, maker, upload_name = rename_folder(item_path)
            file_url = os.path.join(folder_path, new_name)  # 构造file_url
            write_to_log(log_directory, [file_url, tmdb_id, category_id, child, season_num, resolution, source_type, maker, upload_name])

        else:
            print(f"文件夹 {item_path} 不符合处理条件或不存在。")
