import os
from tmdbv3api import TMDb, Movie, TV
import requests
from bs4 import BeautifulSoup

# 初始化 TMDB
tmdb = TMDb()
tmdb.api_key = '107492d808d58cb5f5fae5005c7d764d'
tmdb.language = 'zh-CN'

movie = Movie()
tv = TV()


def contains_chinese(text):
    return any('\u4e00' <= char <= '\u9fff' for char in text)

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
        return '未知', '未知', ''

    id = result.id
    title = get_title_from_web(id, result_type, 'zh-CN')
    original_title = get_title_from_web(id, result_type, 'en-US')
    release_date = result.release_date[:4] if hasattr(result, 'release_date') else result.first_air_date[:4] if hasattr(
        result, 'first_air_date') else ''

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

    # 搜索电影和电视剧结果
    movie_results = [(result, 'movie') for result in movie.search(folder_name)]
    tv_results = [(result, 'tv') for result in tv.search(folder_name)]
    search_results = movie_results + tv_results

    if search_results:
        for i, (result, result_type) in enumerate(search_results, start=1):
            title, original_title, release_date = extract_details(result, result_type)
            print(
                f"{i}. 类型: {'电影' if result_type == 'movie' else '电视剧'}, 中文名: {title}, 英文名: {original_title}, 年份: {release_date}")
        choice = int(input("请选择一个选项: ")) - 1
        selected_result, selected_type = search_results[choice]
        title, original_title, release_date = extract_details(selected_result, selected_type)

        # 根据类型确定是否需要季数
        season_num = ''
        if selected_type == 'tv':
            seasons = tv.details(selected_result.id).number_of_seasons
            if seasons > 1:
                season_num_input = input("请输入季数 (仅数字，例如: 1, 2): ")
                season_num = f"S{season_num_input.zfill(2)}."

        # 构建新名称，并替换空格为点
        new_name = f"{title}.{original_title}.{season_num}{release_date}".replace(' ', '.').strip('.')
        new_path = os.path.join(os.path.dirname(folder_path), new_name)
        os.rename(folder_path, new_path)
        print(f"文件夹重命名为: {new_name}")
    else:
        print("没有找到匹配的 TMDB 资源。")
def list_folders(base_path):
    folders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]
    return folders

def main():
    base_path = input("请输入文件夹的基本路径: ")  # 例如 '/Users/Ethan/Desktop'
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
