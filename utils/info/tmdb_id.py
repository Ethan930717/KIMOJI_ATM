from tmdbv3api import TMDb, Movie, TV
import requests
import logging
logger = logging.getLogger(__name__)

def setup_tmdb():
    tmdb = TMDb()
    tmdb.api_key = '107492d808d58cb5f5fae5005c7d764d'
    tmdb.language = 'zh-CN'

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
    setup_tmdb()
    movie = Movie()
    tv = TV()
    attempt_count = 0
    while attempt_count < 3:
        try:
            if english_title:
                logger.info(f"正在搜索 TMDb: {english_title}")
                movie_results_en = [m for m in movie.search(english_title)]
                tv_results_en = [t for t in tv.search(english_title)]
                combined_results_en = movie_results_en + tv_results_en
                if combined_results_en:
                    print("找到以下结果:")
                    for index, result in enumerate(combined_results_en, start=1):
                        title_or_name = result.title if hasattr(result, 'title') else result.name if hasattr(result,
                                                                                                             'name') else 'Unknown'
                        release_date = result.release_date[:4] if hasattr(result, 'release_date') else 'Unknown'

                        print(f"{index}: {title_or_name} ({release_date})")

                    user_input = input("请选择一个结果 (如果输出错误信息或没有匹配资源，请输入q退出): ")
                    if user_input.lower() == 'q':
                        logger.warning("退出 TMDb 搜索 ,尝试使用IMDb搜索")
                        return None, None, None, None, None, None

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
                    logger.info(f"找到匹配的 TMDb ID: {tmdb_id}, 类型: {media_type}, 中文名: {chinese_name},child:{child}, 开始查找其他元数据ID")
                    return item_type, tmdb_id, media_type, chinese_name, child, keywords

            logger.info("没有在TMDb中搜索到数据，尝试通过IMDb搜索")
            return None, None, None, None, None, None

        except requests.Timeout:
            attempt_count += 1
            logger.error(f"tmdb连接失败，正在进行第{attempt_count}次尝试...")

    logger.error("连接 tmdb 失败，请检查网络连接")
    return None, None, None, None, None

#判定类别
def extract_name(json_data):
    for key in ["original_title", "original_name", "title", "name"]:
        if key in json_data:
            return json_data[key]
    return 'noname'

def extract_genres(json_data):
    return json_data.get('genres', [])

def extract_keywords(json_data):
    if "keywords" in json_data and "keywords" in json_data["keywords"]:
        return [keyword['name'] for keyword in json_data["keywords"]["keywords"]]
    return []

def determine_media_type(genres):
    if any(genre['name'] in ['动漫', '动画', 'anim'] for genre in genres):
        return "anime"
    elif any(genre['name'] in ['纪录', 'documentary', 'Documentary'] for genre in genres):
        return "doc"
    else:
        return "other"

def determine_child_flag(genres):
    return 1 if any(genre['name'] in ['儿童', '家庭'] for genre in genres) else 0
def get_movie_type(tmdb_id):
    setup_tmdb()
    movie = Movie()
    try:
        movie_json = movie.details(tmdb_id)
        chinese_name = extract_name(movie_json)
        genres = extract_genres(movie_json)
        keywords = extract_keywords(movie_json)
        item_type = determine_media_type(genres)
        child = determine_child_flag(genres)
        print (f"movie, {item_type}, {chinese_name}, {child}, {keywords}")
        return item_type,"movie", chinese_name, child, keywords
    except Exception as e:
        logger.error(f"获取电影详情时发生错误: {e}")
        return "movie", "other", None, None, None

def get_tv_type(tmdb_id):
    setup_tmdb()
    tv = TV()
    try:
        tv_json = tv.details(tmdb_id)
        chinese_name = extract_name(tv_json)
        genres = extract_genres(tv_json)
        keywords = extract_keywords(tv_json)
        item_type = determine_media_type(genres)
        child = determine_child_flag(genres)

        return item_type, "tv", chinese_name, child, keywords

    except Exception as e:
        logger.error(f"获取电视详情时发生错误: {e}")
        return "tv", "other", None, None, None