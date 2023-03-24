import os
import time
import urllib

import requests
from bs4 import BeautifulSoup
from PyQt5.QtCore import QObject


class ClondarClient(QObject):
    def __init__(self, query):
        self.query = urllib.parse.quote_plus(query)  # type: ignore
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36', 'Set-Cookie':'HttpOnly;Secure;SameSite=Strict'}
        self.start_time = 0

    def link(self):
        query = f"{self.query}+site%3Atime.is"
        res = requests.get(f'https://www.google.com/search?q={query}&oq={query}&aqs=chrome.0.69i59j0i512l3j0i22i30l6.1684j1j7&sourceid=chrome&ie=UTF-8', headers=self.headers)
        soup = BeautifulSoup(res.text, 'lxml')
        link = soup.find('div', class_="yuRUbf").find('a')['href']  # type: ignore
        return link

    def searchDatetime(self, url):
        res = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(res.text, 'lxml')

        # self.location = soup.find('span', {'itemprop':'name'}).get_text()  # type: ignore
        location = soup.find('div', id='front_loc')
        if location is None:
            location = soup.find('div', id='msgdiv')
        self.location = location.get_text()  # type: ignore

        self.time = soup.find('time', id='clock').get_text()  # type: ignore
        self.date = soup.find('div', id='dd').get_text()  # type: ignore
        self.sun = soup.find('span', id='sun').get_text()  # type: ignore
        self.sun = self.sun.replace("↑", "&#x2191;").replace("↓", "&#x2193;")

        t_time = str(self.time).split(':')
        self.h_time = t_time[0]
        self.m_time = t_time[1]
        self.s_time = t_time[2]

        self.end_time = time.localtime().tm_sec
        if self.start_time > self.end_time:
            self.end_time = 60 + self.end_time
        # print(self.start_time, self.end_time)
        # print(self.end_time-self.start_time)

        self.s_time = str(int(self.s_time)+(self.end_time-self.start_time))

        self.t_time = f"{self.h_time}:{self.m_time}"

        return self.t_time, self.date, self.location

    def cFile(self, location=None, h_time=None, m_time=None, s_time=None, date=None, file="features/libraries/template/clondar.html"):
        if os.path.isfile(file):
            pass
        else:
            file = "features/libraries/template/clondar.html"
        html = open(file, "r").read()

        if  location != None and h_time != None and m_time != None and s_time != None and date != None:
            html = html.replace("%location", location)
            html = html.replace("%hour", h_time)
            html = html.replace("%minute", m_time)
            html = html.replace("%second", s_time)
            html = html.replace("%date", date)
            html = html.replace("%sun", "")
        else:
            html = html.replace("%location", self.location.encode("ascii", "ignore").decode())
            html = html.replace("%hour", self.h_time)
            html = html.replace("%minute", self.m_time)
            html = html.replace("%second", self.s_time)
            html = html.replace("%date", self.date)
            html = html.replace("%sun", self.sun)

        file_lst = file.split("/")
        cachefile = f"browser/Files/{file_lst[len(file_lst)-1]}"
        open(cachefile, "w").write(html)
        url = f"file:///{os.getcwd()}/{cachefile}".replace("\\", "/")
        return url

    def retrieve(self):
        try:
            url = str(self.link())
            self.start_time = time.localtime().tm_sec
            return self.searchDatetime(url)
        except Exception as e:
            raise Exception(f"Clondar: {e}")

# --------------------------------------------------------------------------------------------------------
# client = ClondarClient("what is the date in london")
# str_time, date, location = client.retrieve()

# url = client.cFile()

# print(f"It is {date}")