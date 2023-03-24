import urllib
import requests
from bs4 import BeautifulSoup
import re

from PyQt5.QtCore import QObject


class MapClient(QObject):
    def __init__(self, query, patterns):
        self.patterns = patterns
        self.query = query  # type: ignore
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'}
        # self.query = self.extractLocation(query)
        self.destination = ""
        self.origin = ""

    def extractRoute(self, query):
        if "to" in query:
            pattern = r"to (.*) from (.*)"
        elif "for" in query:
            pattern = r"for (.*) from (.*)"
        elif "at" in query:
            pattern = r"at (.*) from (.*)"

        match = re.search(pattern, query)
        if match:
            self.destination = match.group(1)
            self.origin = match.group(2)
            return (self.origin, self.destination)
        else:
            return "", ""
        
    def extractDestination(self, query):
        if "to" in query:
            pattern = r"to (.*)"
        elif "for" in query:
            pattern = r"for (.*)"
        elif "at" in query:
            pattern = r"at (.*)"

        match = re.search(pattern, query)
        if match:
            self.destination = match.group(1)
            return self.destination
        else:
            return ""
        
    def extractLocation(self):
        # simple = True
        # if "where" in self.query:
        #     location_regex = r"where is (\w+)"
        #     simple = True
        # elif "locate" in self.query:
        #     location_regex = r"locate (\w+)"
        #     simple = True
        # elif "location" in self.query:
        #     location_regex = re.compile(r'(\b(of|the)\s+)?location\s+(of|on)\s+(the\s+map\s+)?(?P<location>\b\w+\b)')
        #     simple = False

        # match = re.search(location_regex, self.query)
        # if match and simple:
        #     self.destination = match.group(1)
        #     return self.destination
        # elif match and not simple:
        #     self.destination = match.group("location")
        #     return self.destination
        # else:
        #     return ""
        for item in self.patterns:
            pattern = item.replace("[location]", "(.*)")
            match = re.search(pattern, self.query)
            if match:
                self.destination = match.group(1)
                return self.destination

    def locate(self, location):
        self.url = f"https://www.google.nl/maps/place/{location}"

    def navigate(self, origin, destination):
        if origin == "home" :
            origin = self.homeLocation()
        elif destination == "home" :
            destination = self.homeLocation()
        self.url = f"https://www.google.nl/maps/dir/{origin}/{destination}"
    def navigateHome(self, home):
        self.url = f"https://www.google.nl/maps/dir//{home}"
    
    def homeLocation(self):
        print("Fetching Home location")
        res = requests.get(f'https://www.google.com/search?q=my+location&oq=my+location&aqs=chrome.0.69i59j0i512l3j0i22i30l6.1684j1j7&sourceid=chrome&ie=UTF-8', headers=self.headers)
        print(res.url)
        soup = BeautifulSoup(res.content, 'lxml')
        data = soup.select('#swml > div > div > a > div:nth-child(1) > span.dfB0uf')
        self.myLocation = data[0].get_text()
        return self.myLocation

    def retrieve(self):
        return self.url