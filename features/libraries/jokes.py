import os
import urllib
from random import choice

import requests
from bs4 import BeautifulSoup
from PyQt5.QtCore import QObject


class JokeClient(QObject):
    def __init__(self, query):
        self.query = urllib.parse.quote_plus(query)  # type: ignore
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36', 'Set-Cookie':'HttpOnly;Secure;SameSite=Strict'}

    def link(self):
        query = f"{self.query}+site%3Ard.com"
        res = requests.get(f'https://www.google.com/search?q={query}&oq={query}&aqs=chrome.0.69i59j0i512l3j0i22i30l6.1684j1j7&sourceid=chrome&ie=UTF-8', headers=self.headers)
        soup = BeautifulSoup(res.text, 'lxml')
        link = soup.find('div', class_="yuRUbf").find('a')['href']  # type: ignore
        return link

    def searchJoke(self, url):
        res = requests.get(url, headers=self.headers)
        self.url = res.url
        
        soup = BeautifulSoup(res.text, 'lxml')
        # ejokes = soup.select('div.content-wrapper.hidden')
        ejokes = soup.select('div.card-wrapper.fixed-height')
        if len(ejokes) == 0:
            raise IndexError
        else:
            pass
        jokes = []

        for joke in ejokes:
            try:
                title = joke.select("h3.entry-title")[0].get_text()
                content = joke.select('div.content-wrapper.hidden')[0].get_text()
                # content = content.replace("Q. ", "").replace("A. ", "").strip()
                content = content.strip()
                # content = content.encode("ascii", "ignore").decode()
                if len(content) <= 200:
                    if "—" in content:
                        l = content.split("—")
                        llen = len(l)
                        if llen == 2:
                            content = l[0]
                        else:
                            l.pop(llen-1)
                            content = ""
                            for item in l:
                                content = f"{content} — {item}"
                    else:
                        pass
                    jokes.append({"title":title, "content":content})
                else:
                    pass
            except:
                pass 
                
        joke = choice(jokes)
        # laugh = ["Ha ha ha!", "Haha! Ha!", "Haha", "Hehehe", "Hahaha"]
        self.laugh = {"&#x1F602;":"Ha ha ha!", "&#x1F601;":"Hihihi", "&#x1F923;":"Hahaha", "&#x1F600;":"Haha"}
        self.key, self.value = choice(list(self.laugh.items()))

        self.joke = str(joke['content']).replace("�", "").replace("’", "'").replace("“", '"').replace("”", '"').replace("‑", "-")
        self.title = str(joke['title']).replace("�", "").replace("’", "'").replace("“", '"').replace("”", '"').replace("‑", "-")
        return self.joke + self.value
    
    def cFile(self, file="features/libraries/template/jokes.html"):
        if os.path.isfile(file):
            pass
        else:
            file = "features/libraries/template/jokes.html"
        html = open(file, "r").read()

        laugh = [{"&#x1F602;":"Ha ha ha!"},{"&#x1F605;":"Hehehe"},{"&#x1F923;":"Hahaha"}]
        html = html.replace("$title", self.title)
        chose = choice(laugh)
        html = html.replace("$joke", f"{self.joke} {self.key}")
        html = html.replace("$url", self.url)

        file_lst = file.split("/")
        cachefile = f"browser/Files/{file_lst[len(file_lst)-1]}"
        open(cachefile, "w").write(html)
        url = f"file:///{os.getcwd()}/{cachefile}".replace("\\", "/")
        return url

    def retrieve(self):
        try:
            url = str(self.link())
            return self.searchJoke(url)
        except Exception as e:
            if type(e) == IndexError:
                url = "https://www.rd.com/jokes/"
                return self.searchJoke(url)
            else:
                raise Exception(e)

# --------------------------------------------------------------------------------------------------------
# jokeclient = JokeClient("joke about animals")
# joke = jokeclient.retrieve()
# jokeclient.cFile()

# print(joke)