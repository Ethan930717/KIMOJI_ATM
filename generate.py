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
logger = logging.getLogger(__name__)
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
    # 设置默认返回值
    default_return = (None, None, None, None, False, 1 )

    media_info = MediaInfo.parse(file_path)
    video_tracks = [track for track in media_info.tracks if track.track_type == 'Video']
    audio_tracks = [track for track in media_info.tracks if track.track_type == 'Audio']

    # 检查是否存在视频轨道
    if not video_tracks:
        return default_return + ("视频异常",)

    video_track = video_tracks[0]

    # 检查视频分辨率
    if video_track.height < 720:
        return default_return + ("分辨率异常",)

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

    return video_codec, audio_codec, resolution, '.'.join(additional_attrs), is_encode, audio_count, 0

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

        # 获取类别信息
        genre_elements = soup.find('span', class_='genres').find_all('a') if soup.find('span', class_='genres') else []
        genres = [a['href'] for a in genre_elements]  # 提取 href 属性值

        # 确定 category_id 和 child
        category_id, child = determine_category_and_child(genres, soup, content_type)

        # 获取年份
        year_element = soup.find('span', class_='tag release_date')
        year = year_element.text.strip('()') if year_element else '未知'

        return year, category_id, child
    else:
        return '未知', None, None

def determine_category_and_child(genres, soup, content_type):
    # 检查 genres 中的数字是否符合特定条件
    if any("/genre/16-" in genre for genre in genres):
        category_id = 1 if content_type == 'movie' else 2
    elif any("/genre/99-" in genre for genre in genres) and content_type == 'tv':
        category_id = 2
    elif any("/genre/10764-" in genre or "/genre/10767-" in genre for genre in genres) and content_type == 'tv':
        category_id = 2
    elif content_type == 'tv':
        category_id = 2
    else:
        category_id = 1

    # 确定 child
    certifications = soup.find('span', class_='certification').get_text() if soup.find('span', class_='certification') else ""
    child = 1 if any(c in certifications for c in ['TV-Y', 'TV-G']) or any(c == 'G' for c in certifications) or any(
        "/genre/10762-" in genre for genre in genres) else 0

    return category_id, child
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
    year, category_id, child = get_details_from_tmdb(id, result_type)


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
            print(
                f"\033[94m{i}. 类型: {'电影' if result_type == 'movie' else '电视剧'}, 中文名: {title}, 英文名: {original_title}, 年份: {release_date}\033[0m")
        user_input = input(
            f"如果无法确定影片序号，请尝试手动搜索后输入'类型ID'（例如 'movie300212' 或 'tv12345'，不含引号），\n"
            f"手动搜索链接：\n"
            f"\033[93m电影类：https://www.themoviedb.org/search/movie?query={search_name}\033[0m\n"
            f"\033[93m剧集类：https://www.themoviedb.org/search/tv?query={search_name}\033[0m\n"
            "\033[91m如果TMDb中没有该词条，请根据当前影片类别输入对应值，电影资源输入'm',剧集资源输入't': \033[0m")
        season_num = ''
        season_onlynum = ''
        if user_input.lower() in ['m', 't']:
            selected_type = 'movie' if user_input.lower() == 'm' else 'tv'
            tmdb_id = '1218677' if selected_type == 'movie' else '241652'
            selected_result = movie.details(tmdb_id) if selected_type == 'movie' else tv.details(tmdb_id)

            title, original_title, release_date, category_id, child = extract_details(selected_result, selected_type)


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

        if user_input.lower() == "t":
            print("您选择的是默认剧集词条，需手动输入季数，请直接输入数字，如: 1, 2, 3")
            user_input = input()
            seasons = int(user_input)
            if seasons > 1:
                season_num_input = input("该剧集有多季，请手动输入季数 (仅数字，例如: 1, 2, 3): ")
                season_num = f"S{season_num_input.zfill(2)}."
                season_onlynum = str(int(season_num_input))  # 将季数转换为整数，然后转换回字符串
                # 获取特定季的年份
                release_date = get_season_year_from_web(selected_result.id, season_num_input)
            else:
                season_num = "S01."
                season_onlynum = "1"  # 如果只有一季，season_onlynum 为 "1"
                # 如果只有一季，使用电视剧的发布年份
                release_date = release_date

        elif selected_type == 'tv':
            logger.info('正在确认剧集季数信息')
            seasons = tv.details(selected_result.id).number_of_seasons
            if seasons > 1:
                season_num_input = input("该剧集有多季，请手动输入季数 (仅数字，例如: 1, 2, 3): ")
                season_num = f"S{season_num_input.zfill(2)}."
                season_onlynum = str(int(season_num_input))  # 将季数转换为整数，然后转换回字符串
                # 获取特定季的年份
                release_date = get_season_year_from_web(selected_result.id, season_num_input)
            else:
                season_num = "S01."
                season_onlynum = "1"  # 如果只有一季，season_onlynum 为 "1"
                # 如果只有一季，使用电视剧的发布年份
                release_date = release_date

        if user_input.lower() in ['m', 't']:
            print("您选择的是默认词条，需要手动输入中文名、英文名与年份，请您首先输入中文标题：")
            user_input = input()
            title = user_input
        # 如果标题不包含中文，提示用户手动输入
        elif not contains_chinese(title):
            print("当前资源似乎没有中文词条，请手动输入中文名，如需跳过请输入q：")
            user_input = input()
            if user_input.lower() != 'q':
                title = user_input
        # 如果原始标题包含中文，提示用户手动输入
        if user_input.lower() in ['m', 't']:
            print("请输入英文标题：")
            user_input = input()
            original_title = user_input
        elif contains_chinese(original_title):
            print("当前资源似乎没有英文词条，请手动输入英文名，如需跳过请输入q：")
            user_input = input()
            if user_input.lower() != 'q':
                original_title = user_input
        # 如果年份未知，提示用户手动输入
        if user_input.lower() in ['m', 't']:
            print("请输入年份：")
            user_input = input()
            release_date = user_input
        elif release_date == '未知':
            print("当前资源在TMDb词条中没有年份，请确认年份信息后手动输入，跳过请按q：")
            user_input = input()
            if user_input.lower() != 'q':
                release_date = user_input

        # 2. 查找并分析最大的视频文件以获取编码和分辨率信息
        largest_video_file = find_largest_video_file(folder_path)
        if largest_video_file:
            video_codec, audio_codec, resolution, additional, is_encode, audio_count, error = get_media_info(largest_video_file)
            if error == "视频异常":
                status = -3
            elif error == "分辨率异常":
                status = -2
            else:
                status = 0
            if audio_count > 1:
                audio_info = f"{audio_count}Audio {audio_codec}"
            else:
                audio_info = audio_codec
            # 根据是否为Encode来调整文件名
            source_type = 'Encode' if is_encode else 'WEB-DL'
            # 构建新名称，并替换空格为点
            new_name = f"{title}.{original_title}.{season_num}{release_date}.{resolution}.{source_type}.{audio_info}.{video_codec}-{additional}KIMOJI"
            new_name = new_name.replace(' ', '.').replace(':', '').replace('/', '.').strip('.')
            new_name = re.sub(r'\.{2,}', '.', new_name) #处理两个点的情况
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
            logger.info(f'\033[92m文件夹重命名为: {new_name}\033[0m')

            is_tv_show = selected_type == 'tv'
            rename_files_in_folder(new_path, new_name, is_tv_show)
            type_id = get_type_id(new_name)
            return new_name, tmdb_id, category_id, child, season_onlynum, resolution, type_id, maker, upload_name, status
        else:
            logger.error("未找到有效的视频文件。")
            return None, None, None, None, None, None, None, None, None, None
    else:
        logger.warning("没有找到匹配的 TMDB 资源。")
        return None, None, None, None, None, None, None, None, None, None

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
    try:
        os.makedirs(log_directory, exist_ok=True)
        log_path = os.path.join(log_directory, 'logfile.csv')

        # 检查并读取现有文件内容
        if os.path.isfile(log_path):
            with open(log_path, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                existing_rows = list(reader)
        else:
            existing_rows = []

        # 检查是否已有标题行，如果没有则添加
        headers = ["路径", "TMDb", "类型", "儿童资源", "季数", "分辨率", "媒介", "制作组", "上传名", "状态"]
        if not existing_rows or existing_rows[0] != headers:
            existing_rows.insert(0, headers)

        # 将新数据添加到文件内容中
        existing_rows.append(data)

        # 将更新后的内容写回文件
        with open(log_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(existing_rows)
            logger.info('信息写入成功')

    except Exception as e:
        logger.error(f"写入日志文件时出错: {e}")
def get_type_id(new_name):
    new_name_upper = new_name.upper()

    if 'REMUX' in new_name_upper:
        type_id = '3'
    elif 'WEB-DL' in new_name_upper:
        type_id = '4'
    elif 'UHD' in new_name_upper and ('X264' in new_name_upper or 'X265' in new_name_upper):
        type_id = '5'
    elif 'BLURAY' in new_name_upper or 'BLU-RAY' in new_name_upper:
        if 'X264' in new_name_upper or 'X265' in new_name_upper:
            type_id = '5'
        else:
            type_id = '2'
    elif 'HDTV' in new_name_upper:
        type_id = '6'
    else:
        type_id = '未知'
    return type_id

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
            logger.info(f"\033[91m处理文件夹: {item_path}\033[0m")
            new_name, tmdb_id, category_id, child, season_onlynum, resolution, type_id, maker, upload_name, status= rename_folder(item_path)
            if status == "分辨率异常" or status == "视频异常":
                logger.warning("当前视频资源分辨率过低或视频异常，不符合发种要求")
                continue  # 继续下一个循环
            file_url = os.path.join(folder_path, new_name)  # 构造file_url
            write_to_log(log_directory, [file_url, tmdb_id, category_id, child, season_onlynum, resolution, type_id, maker, upload_name, status])
            logger.info(f'\033[92m{file_url}添加完成\033[0m')
        else:
            logger.error(f"文件夹 {item_path} 不符合处理条件")
