import os
import re
from tmdbv3api import TMDb, Movie, TV

tmdb = TMDb()
tmdb.api_key = '107492d808d58cb5f5fae5005c7d764d'
tmdb.language = 'zh-CN'

movie = Movie()
tv = TV()


def contains_chinese(text):
    return any('\u4e00' <= char <= '\u9fff' for char in text)


def rename_folder(folder_path):
    folder_name = os.path.basename(folder_path)
    if contains_chinese(folder_name):
        # 搜索 TMDB
        search_results = movie.search(folder_name) + tv.search(folder_name)
        if search_results:
            # 如果有多个结果，让用户选择
            for i, result in enumerate(search_results, start=1):
                print(
                    f"{i}. 中文名: {result.title}, 英文名: {result.original_title}, 类别: {'电影' if isinstance(result, Movie) else '电视剧'}, 年份: {result.release_date[:4]}")
            choice = int(input("请选择一个选项: ")) - 1
            selected_result = search_results[choice]

            new_name = f"{selected_result.title}.{selected_result.original_title}.{selected_result.release_date[:4]}"
            new_name = new_name.replace(" ", ".")

            if isinstance(selected_result, TV):
                seasons = tv.details(selected_result.id).number_of_seasons
                if seasons > 1:
                    season_num = input("请输入季数 (例如: 01, 02): ")
                    new_name += f".S{season_num}"
                else:
                    new_name += ".S01"

            # 重命名文件夹
            new_path = os.path.join(os.path.dirname(folder_path), new_name)
            os.rename(folder_path, new_path)
            print(f"文件夹重命名为: {new_name}")
        else:
            print("没有找到匹配的 TMDB 资源。")


# 示例：重命名特定文件夹
rename_folder("/Users/Ethan/Desktop/河西走廊")
