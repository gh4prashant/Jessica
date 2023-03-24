import os

import requests
from bs4 import BeautifulSoup
from PyQt5.QtCore import QObject, pyqtProperty  # type: ignore


class WeatherClient(QObject):
    def __init__(self, query):
        self.main_query = str(query).strip()
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'}
        # self.main_url = "https://api.openweathermap.org/data/2.5/weather?"
        # self.main_query_params = {
        # "apiKey": "331cde0bf78afe848e6169ebd772521e"
        # }

    def getGWeather(self):
        query = self.main_query

        res = requests.get(f'https://www.google.com/search?q={query}&oq={query}&aqs=chrome.0.69i59j0i512l3j0i22i30l6.1684j1j7&sourceid=chrome&ie=UTF-8', headers=self.headers)
        soup = BeautifulSoup(res.content, 'lxml')

        self.url = str(soup.find("a", {'style':'text-decoration:underline'})['href'])  # type: ignore

        conditionImg = soup.find("img", id="dimg_1")
        self.imgLink = f"https:{conditionImg['src']}"  # type: ignore
        self.condition = str(conditionImg['alt'])  # type: ignore
        self.temp = soup.find("span", id="wob_tm").get_text()  # type: ignore
        self.datetime = soup.find("div", id="wob_dts").get_text()  # type: ignore
        self.pChance = soup.find("span", id="wob_pp").get_text()  # type: ignore
        self.wind_speed = soup.find("span", id="wob_ws").get_text()  # type: ignore
        
    def getWeather(self):
        self.getGWeather()
        res = requests.get(self.url, headers=self.headers)
        # print(res.url, res.status_code)
        soup = BeautifulSoup(res.text, 'lxml')

        self.location = soup.find("h1", class_="CurrentConditions--location--1YWj_").get_text()  # type: ignore
        hl_temp = soup.find("div", class_="WeatherDetailsListItem--wxData--kK35q").get_text()  # type: ignore
        hl_temp = hl_temp.split("/")
        self.h_temp = hl_temp[0].replace("°", "")
        self.l_temp = hl_temp[1].replace("°", "")
        self.humidity = soup.find("span", {'data-testid':'PercentageValue'}).get_text()  # type: ignore

        return self.temp, self.condition, self.h_temp, self.l_temp, self.location
    
    def cFile(self, file="features/libraries/template/weather.html"):
        if os.path.isfile(file):
            pass
        else:
            file = "features/libraries/template/weather.html"
        html = open(file, "r").read()

        html = html.replace("$location", self.location)
        html = html.replace("$time", self.datetime)
        html = html.replace("$temp", self.temp)
        html = html.replace("$condition", self.condition)
        html = html.replace("$max_temp", self.h_temp)
        html = html.replace("$min_temp", self.l_temp)
        html = html.replace("$pp_chance", self.pChance)
        html = html.replace("$humidity", self.humidity)
        html = html.replace("$wind-speed", self.wind_speed)
        html = html.replace("$w_conditionUrl", self.imgLink)
        html = str(html).encode("ascii", "ignore").decode()

        file_lst = file.split("/")
        cachefile = f"browser/Files/{file_lst[len(file_lst)-1]}"
        open(cachefile, "w").write(html)
        url = f"file:///{os.getcwd()}/{cachefile}".replace("\\", "/")
        return url

    @pyqtProperty(str)
    def ppChance(self):
        return self.pChance

    def retrieve(self):
        try:
            return self.getWeather()
        except Exception as e:
            raise Exception(f"Weather: {e}")

        
# --------------------------------------------------------------------------------------------------------

# client = WeatherClient("weather")
# data = client.retrieve()
# url = client.cFile()
# ppchance = client.ppChance
# print(data)
# print(ppchance)
# print(url)