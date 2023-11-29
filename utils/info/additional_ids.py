from utils.info.imdb_id import get_imdb_id,get_tmdb_id_from_imdb
import logging
logger = logging.getLogger(__name__)
def get_additional_ids(tmdb_id, item_type ,title):
    imdb_id = get_imdb_id(tmdb_id, item_type)
    return imdb_id ,"0"

def search_ids_from_imdb(imdb_id, title,item_type):
    # 使用 IMDb ID 搜索 TMDb ID
    tmdb_id = get_tmdb_id_from_imdb(imdb_id)
    if tmdb_id:
        print(f"根据 IMDb ID 找到 TMDb ID: {tmdb_id}")
        # 使用英文标题搜索 MAL ID
        return tmdb_id, imdb_id ,"0"
    else:
        print("无法根据 IMDb ID 找到 TMDb ID")
        return None, imdb_id ,"0"

