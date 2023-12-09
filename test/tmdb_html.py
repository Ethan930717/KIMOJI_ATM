import requests
from bs4 import BeautifulSoup

# URL of the page to scrape
url = 'https://www.themoviedb.org/tv/549-law-order?language=en-US'

# Send a request to the URL
response = requests.get(url)

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
