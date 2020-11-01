import requests
from bs4 import BeautifulSoup

def scrap_page(link):
    page = requests.get(link)
    # check the page status; if success then it should be 200
    if page.status_code != 200:
        return
    soup = BeautifulSoup(page.content, 'html.parser')
    print(soup)
    return