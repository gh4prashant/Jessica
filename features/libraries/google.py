import urllib

import requests
from bs4 import BeautifulSoup
from PyQt5.QtCore import QObject


class GoogleClient(QObject):
    def __init__(self, query):
        self.query = urllib.parse.quote_plus(query)  # type: ignore
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36', 'Set-Cookie':'HttpOnly;Secure;SameSite=Strict'}
    
    def link(self):
        res = requests.get(f'https://www.google.com/search?q={self.query}&oq={self.query}&aqs=chrome.0.69i59j0i512l3j0i22i30l6.1684j1j7&sourceid=chrome&ie=UTF-8', headers=self.headers)
        link = res.url
        # soup = BeautifulSoup(res.text, 'lxml')
        # soup = str(soup).replace("<script>", "<script src=\"https://www.youtube.com/iframe_api\"></script>\n<script>")

        return link

    def search(self, link):
        res = requests.get(link, headers=self.headers)
        soup = BeautifulSoup(res.text, 'lxml')

        klasses = ['LGOjhe', 'Z0LcW', 'IZ6rdc', 'kno-rdesc']
        results = []

        for klass in klasses:
            data = soup.find('div', class_=klass)
            if data != None:
                results.append(data)
            else:
                pass

        size = len(results)

        if size != 0:
            for data in results:
                if "." in data.get_text() or size == 1:
                    try:
                        repldata = str(data.find('span', class_='JPfdse').get_text())
                        repdata = str(data.find('g-bubble').get_text())
                        repldata2 = str(data.find('h3', class_='zsYMMe').get_text())
                        repdata2 = ""
                    except:
                        repldata = ""
                        repdata = ""
                        repldata2 = ""
                        repdata2 = ""
                        data = str(data.get_text())
                    data = data.replace(repdata, repldata).replace(repldata2, repdata2)
        else:
            pass
        return data  # type: ignore

    def retrieve(self):
        url = str(self.link())
        print(url)
        return self.search(url)