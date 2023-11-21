from utils.info.imdb_id import get_imdb_id,get_tmdb_id_from_imdb
from utils.info.mal_id import get_mal_id
import logging
logger = logging.getLogger(__name__)
def get_additional_ids(tmdb_id, item_type, title):
    imdb_id = get_imdb_id(tmdb_id, item_type)
    mal_id = get_mal_id(title)
    return imdb_id, mal_id

def search_ids_from_imdb(imdb_id, title,item_type):
    # 使用 IMDb ID 搜索 TMDb ID
    tmdb_id = get_tmdb_id_from_imdb(imdb_id)
    if tmdb_id:
        print(f"根据 IMDb ID 找到 TMDb ID: {tmdb_id}")
        # 使用英文标题搜索 MAL ID
        mal_id = get_mal_id(title,item_type)
        return tmdb_id, imdb_id, mal_id
    else:
        print("无法根据 IMDb ID 找到 TMDb ID")
        return None, imdb_id, None

