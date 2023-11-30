from tmdbv3api import TMDb, Movie, TV
import requests
import logging
logger = logging.getLogger(__name__)

def setup_tmdb():
    tmdb = TMDb()
    tmdb.api_key = '107492d808d58cb5f5fae5005c7d764d'
    tmdb.language = 'zh-CN'

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
    else:
        return "movie" if caller_type == "movie" else "series"

def determine_child_flag(genres):
    return 1 if any(genre['name'] in ['儿童'] for genre in genres) else 0
def get_movie_type(tmdb_id):
    setup_tmdb()
    movie = Movie()

    try:
        movie_json = movie.details(tmdb_id)
        chinese_name = extract_name(movie_json)
        genres = extract_genres(movie_json)
        keywords = extract_keywords(movie_json)
        item_type = determine_media_type(genres, "movie")
        child = determine_child_flag(genres)
        #print(genres,item_type)
        print(chinese_name)
        print(movie_json)
        #print(f'{item_type},{chinese_name},{child},{keywords}')
        return item_type,"movie", chinese_name, child, keywords
    except Exception as e:
        logger.error(f"获取电影详情时发生错误: {e}")
        return "movie", "movie", None, None, None

def get_tv_type(tmdb_id):
    setup_tmdb()
    tv = TV()
    try:
        tv_json = tv.details(tmdb_id)
        chinese_name = extract_name(tv_json)
        genres = extract_genres(tv_json)
        keywords = extract_keywords(tv_json)
        item_type = determine_media_type(genres, "tv")
        child = determine_child_flag(genres)
        print(tv_json)
        #print(genres,item_type)
        return item_type, "series", chinese_name, child, keywords
    except Exception as e:
        logger.error(f"获取电视详情时发生错误: {e}")
        return "tv", "seires", None, None, None

tmdb_id="7131"
get_tv_type(tmdb_id)