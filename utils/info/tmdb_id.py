from tmdbv3api import TMDb, Movie, TV
import requests
import logging
import re
logger = logging.getLogger(__name__)

def setup_tmdb():
    tmdb = TMDb()
    tmdb.api_key = '107492d808d58cb5f5fae5005c7d764d'
    tmdb.language = 'zh-CN'

setup_tmdb()

#筛选所有结果
def search_and_select(results, movie_results_en):
    if not results:
        logger.info("没有搜索到任何结果")
        return None, None
    for i, result in enumerate(results, start=1):
        print(f"{i}: {result.title if hasattr(result, 'title') else result.name}")
    choice = int(input("选择一个结果 (输入编号): "))
    selected_result = results[choice - 1]
    item_type = 'movie' if selected_result in movie_results_en else 'tv'
    return selected_result, item_type
#确定TMDBID
def search_tmdb(english_title):
    movie = Movie()
    tv = TV()
    attempt_count = 0
    def contains_chinese(text):
        if isinstance(text, str):
            return bool(re.search(r'[\u4e00-\u9fff]', text))
        return False
    while attempt_count < 3:
        try:
            if english_title:
                logger.info(f"正在搜索 TMDb: {english_title}")
                movie_results_en = [m for m in movie(english_title)]
                tv_results_en = [t for t in tv(english_title)]
                combined_results_en = movie_results_en + tv_results_en

                if combined_results_en:
                    print("找到以下结果:")
                    for index, result in enumerate(combined_results_en, start=1):
                        title_or_name = result.title if hasattr(result, 'title') else result.name if hasattr(result,
                                                                                                             'name') else 'Unknown'
                        release_date = result.release_date[:4] if hasattr(result,
                                                                          'release_date') else result.first_air_date[
                                                                                               :4] if hasattr(result,
                                                                                                              'first_air_date') else 'Unknown'
                        resource_type = '电影' if result in movie_results_en else '电视剧'

                        print(f"{index}: {title_or_name} ({release_date}) [{resource_type}]")

                    user_input = input("如果无法确定列表中对应的影片，请手动在TMDb搜索确认后，输入类型+TMDb ID，（例如 'movie300212' 或 'tv12345'）。如果TMDb中没有该词条，请输入 'q': ")
                    if user_input.lower() == 'q':
                        logger.warning("退出 TMDb 搜索，尝试使用 IMDb 搜索")
                        return None, None, None, None, None, None
                    elif user_input.lower().startswith('movie') or user_input.lower().startswith('tv'):
                        if user_input.lower().startswith('movie'):
                            item_type = 'movie'
                            tmdb_id_start_pos = 5
                        else:
                            item_type = 'tv'
                            tmdb_id_start_pos = 2

                        tmdb_id = int(user_input[tmdb_id_start_pos:])
                        if item_type == 'movie':
                            logger.info('正在搜索TMDb_movie元数据')
                            item_type, media_type, chinese_name, child, keywords = get_movie_type(tmdb_id)
                        else:
                            logger.info('正在搜索TMDb_tv元数据')
                            item_type, media_type, chinese_name, child, keywords = get_tv_type(tmdb_id)
                        logger.info(
                            f"找到匹配的 TMDb ID: {tmdb_id}, 类型: {media_type}, 片名: {chinese_name},child:{child}, 开始查找其他元数据ID")
                        return item_type, tmdb_id, media_type, chinese_name, child, keywords

                    selected_index = int(user_input) - 1
                    selected_result = combined_results_en[selected_index]
                    item_type = 'movie' if selected_result in movie_results_en else 'tv'
                    tmdb_id = selected_result.id
                    if item_type == 'movie':
                        logger.info('正在搜索TMDb_movie元数据')
                        item_type, media_type, chinese_name, child, keywords = get_movie_type(tmdb_id)
                    else:
                        logger.info('正在搜索TMDb_tv元数据')
                        item_type, media_type, chinese_name, child, keywords = get_tv_type(tmdb_id)
                    # 检查中文名称是否包含中文字符
                    if contains_chinese(title_or_name):
                        chinese_name = title_or_name
                    logger.info(
                        f"找到匹配的 TMDb ID: {tmdb_id}, 类型: {media_type}, 片名: {chinese_name},child:{child}, 开始查找其他元数据ID")
                    return item_type, tmdb_id, media_type, chinese_name, child, keywords

            logger.info("没有在 TMDb 中搜索到数据，尝试通过 IMDb 搜索")
            return None, None, None, None, None, None

        except requests.Timeout:
            attempt_count += 1
            logger.error(f"TMDb 连接失败，正在进行第 {attempt_count} 次尝试...")

    logger.error("连接 TMDb 失败，请检查网络连接")
    return None, None, None, None, None, None

#判定类别
def extract_name(json_data):
    if 'titles' in json_data:
        for title in json_data['titles']:
            if title.get('iso_3166_1') == 'CN':  # 检查国家代码
                return title['title']
    if 'titles' in json_data:
        for title in json_data['titles']:
            if title.get('iso_639_1') == 'zh':  # 检查语言代码
                return title['title']
    if 'translations' in json_data and 'translations' in json_data['translations']:
        for translation in json_data['translations']['translations']:
            if translation['iso_3166_1'] == 'CN' and translation['iso_639_1'] == 'zh':
                return translation['data']['title']
    for key in ["original_title", "original_name", "title", "name"]:
        if key in json_data:
            return json_data[key]
    return 'noname'


def extract_genres(json_data):
    return json_data.get('genres', [])


def extract_keywords(json_data):
    # 检查是否存在 'keywords' 键，并且其下还有一个 'keywords' 键
    if "keywords" in json_data and "keywords" in json_data["keywords"]:
        return [keyword['name'] for keyword in json_data["keywords"]["keywords"]]

    # 检查是否直接存在 'keywords' 键，且为列表类型
    elif "keywords" in json_data and isinstance(json_data["keywords"], list):
        return [keyword['name'] for keyword in json_data["keywords"]]

    # 如果上述条件均不符合，则返回空列表
    return []


def determine_media_type(genres, caller_type):
    if any(genre['name'] in ['动漫', '动画', 'anim'] for genre in genres):
        return "anime"
    elif any(genre['name'] in ['纪录', 'documentary', 'Documentary'] for genre in genres):
        return "doc"
    elif any(genre['name'] in ['reality-tv', 'show' ,'综艺','真人秀'] for genre in genres):
        return "show"
    else:
        return "movie" if caller_type == "movie" else "series"

def determine_child_flag(genres):
    return 1 if any(genre['name'] in ['儿童'] for genre in genres) else 0
def get_movie_type(tmdb_id):
    movie = Movie()
    try:
        movie_json = movie.details(tmdb_id)
        chinese_name = extract_name(movie_json)
        genres = extract_genres(movie_json)
        keywords = extract_keywords(movie_json)
        item_type = determine_media_type(genres, "movie")
        child = determine_child_flag(genres)
        if item_type == 'anime':
            item_type = "anime-movie"
        #print(movie_json)
        #print(f'{item_type},{chinese_name},{child},{keywords}')
        return item_type,"movie", chinese_name, child, keywords
    except Exception as e:
        logger.error(f"获取电影详情时发生错误: {e}")
        return "movie", "movie", None, None, None

def get_tv_type(tmdb_id):
    tv = TV()
    try:
        tv_json = tv.details(tmdb_id)
        chinese_name = extract_name(tv_json)
        genres = extract_genres(tv_json)
        keywords = extract_keywords(tv_json)
        item_type = determine_media_type(genres, "tv")
        child = determine_child_flag(genres)
        if item_type == 'anime':
            item_type = "anime-tv"
        return item_type, "series", chinese_name, child, keywords
    except Exception as e:
        logger.error(f"获取电视详情时发生错误: {e}")
        return "tv", "seires", None, None, None
