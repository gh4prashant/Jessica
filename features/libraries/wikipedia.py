import urllib

import requests
from bs4 import BeautifulSoup
from PyQt5.QtCore import QObject


class WikipediaClient(QObject):
    def __init__(self, query):
        self.query = urllib.parse.quote_plus(query)
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36', 'Set-Cookie':'HttpOnly;Secure;SameSite=Strict'}

    def link(self):
        query = f"{self.query}+site%3Awikipedia.org"
        res = requests.get(f'https://www.google.com/search?q={query}&oq={query}&aqs=chrome.0.69i59j0i512l3j0i22i30l6.1684j1j7&sourceid=chrome&ie=UTF-8', headers=self.headers)
        soup = BeautifulSoup(res.text, 'lxml')
        link = soup.find('div', class_="yuRUbf").find('a')['href']  # type: ignore
        return link
    
    def search(self, url):
        res = requests.get(url, headers=self.headers)

        soup = BeautifulSoup(res.content, 'lxml')
        results = soup.select('#mw-content-text > div.mw-parser-output > p')
        for result in results:
            if result.get_text().strip() == '':
                pass
            else:
                data = result.get_text()
                break
        return data

    def retrieve(self):
        url = str(self.link())
        return self.search(url)
