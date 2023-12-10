import requests
from bs4 import BeautifulSoup
import re
def get_year_from_web():
    url = f"https://www.themoviedb.org/tv/123"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        #print(soup)
        # Find the element with class 'tag release_date'
        year_element = soup.find('span', class_='tag release_date')

        if year_element:
            year_text = year_element.text.strip()
            # Extract year from the text within parentheses
            year = re.search(r'\((\d{4})\)', year_text)
            print(year.group(1))
            return year.group(1) if year else '未知'
        else:
            return '未知'
    else:
        return '未知'

get_year_from_web()