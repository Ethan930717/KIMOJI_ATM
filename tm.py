import os
from tmdbv3api import TMDb, Movie, TV
import requests
from bs4 import BeautifulSoup
from pymediainfo import MediaInfo
import re

# 初始化 TMDB
tmdb = TMDb()
tmdb.api_key = '107492d808d58cb5f5fae5005c7d764d'
tmdb.language = 'zh-CN'

movie = Movie()
tv = TV()

def find_largest_video_file(folder_path):
    largest_size = 0
    video_file = None
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path) and file_path.endswith(('.mp4', '.mkv', '.avi', '.mov')):
            size = os.path.getsize(file_path)
            if size > largest_size:
                largest_size = size
                video_file = file_path
    return video_file

def format_resolution(width, height, scan_type):
    if height == 1080:
        return '1080p' if scan_type == 'P' else '1080i'
    elif height == 720:
        return '720p'
    elif height == 2160:
        return '2160p'
    else:
        return f"{width}x{height}"


def get_media_info(file_path):
    media_info = MediaInfo.parse(file_path)
    video_tracks = [track for track in media_info.tracks if track.track_type == 'Video']
    audio_tracks = [track for track in media_info.tracks if track.track_type == 'Audio']

    if not video_tracks:
        return None

    video_track = video_tracks[0]
    audio_track = audio_tracks[0] if audio_tracks else None

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
    resolution = format_resolution(video_track.width, video_track.height, scan_type)

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

    return video_codec, audio_codec, resolution, '.'.join(additional_attrs), is_encode


def contains_chinese(text):
    return any('\u4e00' <= char <= '\u9fff' for char in text)

def get_year_from_web(id, content_type):
    base_url = "https://www.themoviedb.org"
    url = f"{base_url}/{content_type}/{id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # Find the element with class 'tag release_date'
        year_element = soup.find('span', class_='tag release_date')
        if year_element:
            year_text = year_element.text.strip()
            # Extract year from the text within parentheses
            year = re.search(r'\((\d{4})\)', year_text)
            return year.group(1) if year else '未知'
        else:
            return '未知'
    else:
        return '未知'


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
        return '未知', '未知', '未知'

    id = result.id
    title = get_title_from_web(id, result_type, 'zh-CN')
    original_title = get_title_from_web(id, result_type, 'en-US')
    release_date = get_year_from_web(id, result_type)  # 从网页获取年份

    return title, original_title, release_date

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

    # 1. 使用TMDB API获取文件夹名称对应的影片信息
    movie_results = [(result, 'movie') for result in movie.search(folder_name)]
    tv_results = [(result, 'tv') for result in tv.search(folder_name)]
    search_results = movie_results + tv_results

    if search_results:
        for i, (result, result_type) in enumerate(search_results, start=1):
            title, original_title, release_date = extract_details(result, result_type)
            print(f"{i}. 类型: {'电影' if result_type == 'movie' else '电视剧'}, 中文名: {title}, 英文名: {original_title}, 年份: {release_date}")
        user_input = input(
            "如果无法确定列表中对应的影片，请手动在TMDb搜索确认后，输入类型+TMDb ID（例如 'movie300212' 或 'tv12345'）。如果TMDb中没有该词条，请输入 'q'退出脚本: ")

        if user_input.lower() == 'q':
            print("退出脚本。")
            return
        elif user_input.startswith('movie') or user_input.startswith('tv'):
            selected_type = user_input[:5]
            tmdb_id = user_input[5:]
            if selected_type == 'movie':
                selected_result = movie.details(tmdb_id)
            else:
                selected_result = tv.details(tmdb_id)
            title, original_title, release_date = extract_details(selected_result, selected_type)
        else:
            choice = int(user_input) - 1
            selected_result, selected_type = search_results[choice]
            title, original_title, release_date = extract_details(selected_result, selected_type)

        season_num = ''
        if selected_type == 'tv':
            seasons = tv.details(selected_result.id).number_of_seasons
            if seasons > 1:
                season_num_input = input("请输入季数 (仅数字，例如: 1, 2): ")
                season_num = f"S{season_num_input.zfill(2)}."
            else:
                season_num = "S01."


        # 2. 查找并分析最大的视频文件以获取编码和分辨率信息
        largest_video_file = find_largest_video_file(folder_path)
        if largest_video_file:
            video_codec, audio_codec, resolution, additional, is_encode = get_media_info(largest_video_file)
            # 根据是否为Encode来调整文件名
            source_type = 'WEB-DL'
            # 构建新名称，并替换空格为点
            new_name = f"{title}.{original_title}.{season_num}{release_date}.{resolution}.{source_type}.{audio_codec}.{video_codec}-{additional}KIMOJI".replace(
                ' ', '.').replace(':', '').strip('.')
            new_path = os.path.join(os.path.dirname(folder_path), new_name)
            os.rename(folder_path, new_path)
            print(f"文件夹重命名为: {new_name}")

            # 在这里调用 rename_files_in_folder 函数
            is_tv_show = selected_type == 'tv'
            rename_files_in_folder(new_path, new_name, is_tv_show)

        else:
            print("未找到有效的视频文件。")
    else:
        print("没有找到匹配的 TMDB 资源。")

def list_folders(base_path):
    folders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]
    return folders

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
def main():
    base_path = '/home/encoded'  # 例如 '/Users/Ethan/Desktop'
    folders = list_folders(base_path)

    if not folders:
        print("该路径下没有文件夹。")
        return

    print("在以下文件夹中选择一个进行重命名:")
    for i, folder in enumerate(folders, start=1):
        print(f"{i}. {folder}")

    choice = int(input("请选择一个文件夹（输入序号）: ")) - 1
    if 0 <= choice < len(folders):
        folder_to_rename = os.path.join(base_path, folders[choice])
        rename_folder(folder_to_rename)
    else:
        print("无效的选择。")

if __name__ == "__main__":
    main()
