import requests
import logging
logger = logging.getLogger(__name__)
def get_mal_id(title):
    response = requests.get(f'https://api.jikan.moe/v4/anime?q={title}')
    if response.status_code == 200:
        data = response.json()
        if 'data' in data and len(data['data']) > 0:
            # 获取第一个搜索结果的 MAL ID
            logger.info(f"MAL ID匹配成功{data['data'][0]['mal_id']}")
            #return data['data'][0]['mal_id']
            return None
    return None