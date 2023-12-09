import os
from tmdbv3api import TMDb, Movie, TV

# 初始化 TMDB
tmdb = TMDb()
tmdb.api_key = '107492d808d58cb5f5fae5005c7d764d'
tmdb.language = 'zh-CN'

movie = Movie()
tv = TV()


def contains_chinese(text):
    return any('\u4e00' <= char <= '\u9fff' for char in text)


def extract_details(result):
    if isinstance(result, str):
        return '未知', '未知', ''
    title = result.title if hasattr(result, 'title') else result.name if hasattr(result, 'name') else '未知'
    original_title = result.original_title if hasattr(result, 'original_title') else result.original_name if hasattr(
        result, 'original_name') else '未知'
    release_date = result.release_date[:4] if hasattr(result, 'release_date') else result.first_air_date[:4] if hasattr(
        result, 'first_air_date') else ''

    # 检查并获取对应的英文或中文名称
    if contains_chinese(original_title):
        title = original_title
        original_title = get_alternative_title(result.id, 'en')
    else:
        original_title = title
        title = get_alternative_title(result.id, 'zh')

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
    movie_results = list(movie.search(folder_name))
    tv_results = list(tv.search(folder_name))
    search_results = movie_results + tv_results

    if search_results:
        for i, result in enumerate(search_results, start=1):
            title, original_title, release_date = extract_details(result)
            print(f"{i}. 中文名: {title}, 英文名: {original_title}, 年份: {release_date}")
        choice = int(input("请选择一个选项: ")) - 1
        selected_result = search_results[choice]
        title, original_title, release_date = extract_details(selected_result)

        season_num = 'S01'  # 默认季数
        if isinstance(selected_result, TV):
            seasons = tv.details(selected_result.id).number_of_seasons
            if seasons > 1:
                season_num_input = input("请输入季数 (仅数字，例如: 1, 2): ")
                season_num = f"S{season_num_input.zfill(2)}"

        new_name = f"{title}.{original_title}.{season_num}.{release_date}".strip('.')
        new_path = os.path.join(os.path.dirname(folder_path), new_name)
        os.rename(folder_path, new_path)
        print(f"文件夹重命名为: {new_name}")
    else:
        print("没有找到匹配的 TMDB 资源。")


# 示例
rename_folder("/Users/Ethan/Desktop/河西走廊")
