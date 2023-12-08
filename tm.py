import os
import re
from tmdbv3api import TMDb, Movie, TV

# 初始化 TMDB
tmdb = TMDb()
tmdb.api_key = '107492d808d58cb5f5fae5005c7d764d'
tmdb.language = 'zh-CN'

movie = Movie()
tv = TV()

def contains_chinese(text):
    return any('\u4e00' <= char <= '\u9fff' for char in text)

def extract_name(json_data):
    if 'titles' in json_data:
        for title in json_data['titles']:
            if title.get('iso_3166_1') == 'CN':
                return title.get('title')
    if 'translations' in json_data and 'translations' in json_data['translations']:
        for translation in json_data['translations']['translations']:
            if translation['iso_3166_1'] == 'CN' and translation['iso_639_1'] == 'zh':
                return translation['data'].get('title')
    return json_data.get('original_title', json_data.get('original_name', 'Unknown'))

def rename_folder(folder_path):
    folder_name = os.path.basename(folder_path)
    if contains_chinese(folder_name):
        search_results = movie.search(folder_name) + tv.search(folder_name)
        if search_results:
            for i, result in enumerate(search_results, start=1):
                title = extract_name(result._data)
                print(f"{i}. 中文名: {title}, 英文名: {result.original_title}, 类别: {'电影' if isinstance(result, Movie) else '电视剧'}")
            choice = int(input("请选择一个选项: ")) - 1
            selected_result = search_results[choice]
            new_name = f"{extract_name(selected_result._data)}.{selected_result.original_title}"
            if isinstance(selected_result, TV):
                seasons = tv.details(selected_result.id).number_of_seasons
                season_num = "S01"
                if seasons > 1:
                    season_num = input("请输入季数 (例如: S01, S02): ")
                new_name += f".{season_num}"
            new_path = os.path.join(os.path.dirname(folder_path), new_name)
            os.rename(folder_path, new_path)
            print(f"文件夹重命名为: {new_name}")
        else:
            print("没有找到匹配的 TMDB 资源。")

# 示例
rename_folder("/Users/Ethan/Desktop/河西走廊")
