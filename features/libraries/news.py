import os

from PyQt5.QtCore import QObject


class NewsClient(QObject):
    def __init__(self, query):
        self.main_query = str(query).strip()
        self.main_url = "https://newsapi.org"
        self.version = "v2"
        self.main_query_params = {
        "apiKey": "e885d04a980e4629af6a487991bf3981"
        }
    
    def checkStatus(self, page):
        status = page["status"]
        if status == "ok":
            return True
        else:
            error = str(page["message"])
            raise Exception(error)
    
    def findCountry(self):
        import json
        with open("features/libraries/country_code.json", "r") as jsonData:
            countries = json.load(jsonData)
        self.query = str(self.query).replace("of", "")
        
        if countries != []:
            for country in countries:
                if str(country).lower() in self.query:
                    code = str(countries[country]).lower()
                    country = str(country).lower()
                    break
                else:
                    country = ""
                    code = ""
            return country, code  # type: ignore
        else:
            raise Exception("Country codes not found in the respective file.")
    
    def findDate(self):
        import datefinder
        matches = list(datefinder.find_dates(self.query))
        results = []

        if len(matches) > 0:
            for date in matches:
                date = date.strftime("%Y-%m-%d")  # type: ignore
                results.append(date)
                print(date)
        else:
            if "today" in self.query or "today's" in self.query or "todays" in self.query:
                import datetime
                date = datetime.datetime.now()
                date = date.strftime("%Y-%m-%d")
                results.append(date)
                results.append(date)
                self.query = self.query.replace("today's", "").replace("todays", "").replace("today", "")
            else:
                results.append("")
                results.append("")
        return results[0], results[1]

    def topHeadlines(self, query:str, query_params:dict):
        self.query = query
        self.query_params = query_params
        ignoreWords = ["top", "latest", "trending", "popular", "breaking", "headlines", "headline", "today's", "today", "bulletin"]
        for words in ignoreWords:
            self.query = self.query.replace(words, "")

        self.full_url = f"{self.main_url}/{self.version}/top-headlines"

        categories = ["business", "entertainment", "general", "health", "science", "sports", "technology"]
        
        for category in categories:
            if category in self.query:
                self.query_params.update({"category": category})
                self.query = self.query.replace(category, "")
                break
            else:
                pass

        import re
        pageSize = re.findall(r'\d+', self.query)
        if pageSize != []:
            pageSize = int(pageSize[0])
        else:
            pageSize = 10
        self.query = self.query.replace(str(pageSize), "")

        country, code = self.findCountry()
        if country != "":
            self.query_params.update({"country": code})
            self.query = self.query.replace(country, "")
        else:
            pass

        self.query = " ".join(self.query.split())
        self.query_params.update({"q": self.query})
        
        import requests
        res = requests.get(self.full_url, params=self.query_params)
        print(res.url)
        page = res.json()
    
        self.checkStatus(page)

        article = page["articles"]
        if pageSize > len(article):
            pageSize = len(article)
        else:
            pass
        results = []

        if pageSize != 0:    
            for ar in article:
                results.append(ar)
        else:
            raise Exception(f"No results found on {res.url}.")
        
        return pageSize, results
    
    def everything(self, query:str, query_params:dict):
        self.query = query
        self.query_params = query_params
        import requests
        self.full_url = f"{self.main_url}/{self.version}/everything"

        categories = {"related":"relevancy", "about":"relevancy", "popular":"popularity", "top":"popularity", "latest":"publishedAt", "trending":"publishedAt"}
        
        for category in categories:
            if category in self.query:
                sorting = categories[category]
                self.query_params.update({"sortBy": sorting})
                self.query = self.query.replace(category, "")
                break
            else:
                pass

        import re
        pageSize = re.findall(r'\d+', self.query)
        if pageSize != []:
            pageSize = int(pageSize[0])
            l = self.query.split(" ")
            for i in range(len(l)):
                if l[i] == pageSize and l[i+1] == "news":
                    self.query = self.query.replace(str(pageSize), "", 1)
                else:
                    pageSize = 10
        else:
            pageSize = 10

        fdate, tdate = self.findDate()
        if fdate != "":
            import datetime
            fdte = datetime.datetime.strptime(fdate, "%Y-%m-%d")
            tdte = datetime.datetime.strptime(tdate, "%Y-%m-%d")

            dates = ["%Y", "%B", "%d"]
            for stripper in dates:
                strippedData = fdte.strftime(stripper).lower()
                self.query = self.query.replace(strippedData, "")
                # print(strippedData)
                strippedData = tdte.strftime(stripper).lower()
                self.query = self.query.replace(strippedData, "")
                # print(self.query)
            self.query_params.update({"from": fdate})
            self.query_params.update({"to": tdate})
            self.query = str(self.query).replace("from", "").replace("to", "")
        else:
            pass
        
        self.query = " ".join(self.query.split())
        self.query_params.update({"language": "en"})
        self.query_params.update({"q": self.query})
        
        import requests
        res = requests.get(self.full_url, params=self.query_params)
        print(res.url)
        page = res.json()
    
        self.checkStatus(page)

        article = page["articles"]
        if pageSize > len(article):
            pageSize = len(article)
        else:
            pass
        results = []

        if pageSize != 0:    
            for ar in article:
                results.append(ar)
        else:
            raise Exception(f"No results found on {res.url}.")
        
        return pageSize, results
        
    def cFile(self, results:list, file="features/libraries/template/news.html"):
        if os.path.isfile(file):
            pass
        else:
            file = "features/libraries/template/news.html"
        html = open(file, "r").read()

        i = 1
        for result in results:
            reporter = result['reporter']
            reporter = str(reporter).encode("ascii", "ignore").decode()
            news_url = result['url']
            news = result['news']
            news = str(news).encode("ascii", "ignore").decode()
            img_url = result['imgUrl']
            html = html.replace("$reporter", reporter, 1)
            html = html.replace("$newslink", news_url, 1)
            html = html.replace("$news-headline", news, 1)
            html = html.replace("$imglink", img_url, 1)
            html = html.replace("$flex", f"flex-{i}", 1)
            html = html.replace("$break", f"break-{i}", 1)
            i += 1

        file_lst = file.split("/")
        cachefile = f"browser/Files/{file_lst[len(file_lst)-1]}"
        open(cachefile, "w", encoding='utf-8').write(html)
        url = f"file:///{os.getcwd()}/{cachefile}".replace("\\", "/")
        return url

    def retrieve(self):
        try:
            if "headline" in self.main_query:
                try:
                    return self.topHeadlines(self.main_query, self.main_query_params)
                except Exception as e:
                    self.main_query = self.main_query.replace("headlines", "").replace("headline", "")
                    try:
                        return self.everything(self.main_query, self.main_query_params)
                    except:
                        return self.everything("news", self.main_query_params)
            else:
                return self.everything(self.main_query, self.main_query_params)
        except Exception as e:
            raise Exception(f"News: {e}")

# --------------------------------------------------------------------------------------------------------
# query = input("Enter: ")
# newsclient = NewsClient(query)

# resultnum, results = newsclient.retrieve()
# print(resultnum)
# # print(newsclient.cFile(results))
    
# result_list = []

# for result in results:
#     reporter = result['source']['name']
#     news_url = result['url']
#     news = result['title']
#     img_url = result['urlToImage']
#     if "<" in news and ">" in news or "..." in news or "…" in news:
#         print(str(news))
#         # if "\\x" in str(bytes(news, 'utf-8')):
#         pass
#     else:
#         try:
#             str(news)
#             result_list.append({'reporter':f'{reporter}', 'url':f'{news_url}', 'news':f'{news}', 'imgUrl':f'{img_url}'})
#         except:
#             pass

# try:
#     i = 0
#     count = 0
#     for result in result_list:
#         if i != resultnum:
#             print(f"{i+1}. {result['news']}")
#             i += 1
#             count += 1
#         else:
#             break
# except Exception as e:
#     print(e)

# print(newsclient.cFile(result_list))