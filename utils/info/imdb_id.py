from tmdbv3api import Movie, TV
import requests
import re
import logging
logger = logging.getLogger(__name__)

def get_imdb_id(tmdb_id, item_type):
    imdb_id = None
    if item_type == 'movie':
        movie = Movie()
        details = movie.details(tmdb_id)
        imdb_id = details.imdb_id if hasattr(details, 'imdb_id') else None
    elif item_type == 'tv':
        tv = TV()
        external_ids = tv.external_ids(tmdb_id)
        imdb_id = external_ids['imdb_id'] if 'imdb_id' in external_ids else None
    if imdb_id:
        match = re.search(r'\d+', imdb_id)
        if match:
            return match.group()
    return None

def search_imdb(title):
    api_key = "c167b680"
    url = f"http://www.omdbapi.com/?t={title}&apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data and 'imdbID' in data:
            imdb_id = data['imdbID']
            category = categorize_media(data)
            logger.info(f"找到匹配的 IMDb ID: {imdb_id}, 类型: {category}")
            return imdb_id, category
    return None, None

def categorize_media(data):
    item_type = data.get('Type')
    genres = data.get('Genre', '').lower()
    logger.info(f"使用IMDb判定上传类别成功")
    if item_type == 'movie':
        if 'anim' in genres:
            return "anime-movie"
        else:
            return "movie"
    elif "documentary" in genres:
        return "doc"
    elif item_type == 'series':
        if 'anim' not in genres:
                return "anime-tv"
        elif 'animation' in genres and 'anime' in genres:
                return "anime-movie"
        elif 'reality-tv' in genres or 'show' in genres:
                return "show"
        else:
                return "series"
    else:
        return "other"

def get_tmdb_id_from_imdb(imdb_id):
    movie = Movie()
    search_results = movie.external(imdb_id=imdb_id)
    if search_results:
        return search_results.id
    return None