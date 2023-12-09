import requests
from bs4 import BeautifulSoup

# URL of the page to scrape
url = 'https://www.themoviedb.org/tv/549-law-order?language=en-US'

# Cookies to be sent with the request

# Send a request to the URL with cookies
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find elements with class 'title ott_false'
    titles = soup.find_all(class_='title ott_false')

    # Print the extracted titles or process them as needed
    for title in titles:
        print(title.text.strip())
else:
    print(f"Failed to retrieve data: Status code {response.status_code}")
