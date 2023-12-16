import requests
from bs4 import BeautifulSoup

def get_details_from_tmdb(id, content_type):
    base_url = "https://www.themoviedb.org"
    url = f"{base_url}/{content_type}/{id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        year_element = soup.find('span', class_='tag release_date')
        year = year_element.text.strip('()') if year_element else '未知'

        genres_elements = soup.find('div', class_='facts').find('span', class_='genres')
        genres = [genre.get_text() for genre in genres_elements.find_all('a')] if genres_elements else []
        certifications_element = soup.find('div', class_='facts').find('span', class_='certification')
        certifications = certifications_element.get_text() if certifications_element else ""

        category_id = None
        child = 0

        if "16-" in str(genres):
            category_id = 3 if content_type == 'movie' else 4
        elif "99-" in str(genres) and content_type == 'tv':
            category_id = 6
        elif ("10764" in str(genres) or "10767" in str(genres)) and content_type == 'tv':
            category_id = 5
        elif content_type == 'tv':
            category_id = 2
        else:
            category_id = 1

        if any(c in certifications for c in ['Y', 'G']) or "10762" in str(genres):
            child = 1

        return year, category_id, child,genres
    else:
        return '未知', None, None

# 测试函数
def test_get_details_from_tmdb():
    test_id = '550' # 例如，电影《搏击俱乐部》的TMDB ID
    test_type = 'movie'
    year, category_id, child, genres = get_details_from_tmdb(test_id, test_type)
    print(f"年份: {year}, 类别ID: {category_id}, 是否儿童资源: {child}, {genres}")

if __name__ == "__main__":
    test_get_details_from_tmdb()
