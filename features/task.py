import datetime
import os
import pathlib
import re
import subprocess
import time
import webbrowser
from random import choice
from threading import Thread

import psutil
import pyautogui
from googleapiclient.discovery import build

from features.communicate import log, log_chat, speak, takecommand, replyAI
from features.libraries.reminder import ReminderClient
from features.libraries.clondar import ClondarClient
from features.libraries.google import GoogleClient
from features.libraries.jokes import JokeClient
from features.libraries.map import MapClient
from features.libraries.news import NewsClient
from features.libraries.weather import WeatherClient
from features.libraries.wikipedia import WikipediaClient

SSPATH = "C:/Users/Pawan/Pictures/Screenshots"

def getTime(self, query):
    """Tell user the current time"""
    try:
        client = ClondarClient(query)
        time, date, location = client.retrieve()
        location = location.replace("Time in", "")

        url = client.cFile()
        self.func_dataEmmited.emit(url)

        speak(f"Master, It is {time} in {location}.")

    except Exception as e:
        client = ClondarClient(query)

        location = "India"
        now = datetime.datetime.now()
        hour = str(now.hour)
        minute = str(now.minute)
        second = str(now.second)
        time = f"{hour}:{minute}"
        date = str(now.strftime("%A, %d %B, %Y"))

        url = client.cFile(location, hour, minute, second, date)
        self.func_dataEmmited.emit(url)

        speak(f"Master, It is {time} in {location}.")
        log(e)

def getDate(self, query):
    """Tell user the date"""
    try:
        client = ClondarClient(query)
        time, date, location = client.retrieve()

        url = client.cFile()
        self.func_dataEmmited.emit(url)

        speak(f"Master, It is {date}")

    except Exception as e:
        client = ClondarClient(query)

        location = "Time in India now:"
        now = datetime.datetime.now()
        hour = str(now.hour)
        minute = str(now.minute)
        second = str(now.second)
        time = f"{hour}:{minute}"
        date = str(now.strftime("%A, %d %B, %Y"))

        url = client.cFile(location, hour, minute, second, date)
        self.func_dataEmmited.emit(url)

        speak(f"Master, It is {date}")

        log(e)

def wishMe(self, start=True):
    """Wish the user"""
    try:
        now = datetime.datetime.now()
        hour = int(now.hour)
        strTime = time.strftime("%I:%M %p")

        if start:
            import random

            replies = ["It's $time on $day, $month $date $year.", "Today is $day, the $date of $month $year, and it's currently $time.", "The time is $time on $day, $month $date $year.", "It's currently $time on $day, $month $date $year.", "Today is $day, $month $date $year, and the current time is $time."]

            day = str(now.strftime("%A"))
            date = str(now.strftime("%d"))
            month = str(now.strftime("%B"))
            year = str(now.strftime("%Y"))

            reply = random.choice(replies).replace("$time", strTime).replace("$day", day).replace("$date", date).replace("$month", month).replace("$year", year)
            
            if hour >= 0 and hour < 12:
                # log_chat("\nUser: Good morning jessica")
                speak(f"Good Morning! {reply}")
            elif hour >= 12 and hour < 16:
                # log_chat("\nUser: Good afternoon jessica")
                speak(f"Good Afternoon! {reply}")
            else:
                # log_chat("\nUser: Good evening jessica")
                speak(f"Good Evening! {reply}")
            speak(f"Hello Master, How may I help you?", logging=False)

        else:
            if hour >= 0 and hour < 12:
                ttime = "Morning"
            elif hour >= 12 and hour < 16:
                ttime = "Afternoon"
            else:
                ttime = "Evening"

            import os

            html = open("features/libraries/template/greetings.html", "r").read()
            html = html.replace("$time", ttime, 1)

            file_lst = "features/libraries/template/greetings.html".split("/")
            cachefile = f"browser/Files/{file_lst[len(file_lst)-1]}"
            open(cachefile, "w").write(html)
            url = f"file:///{os.getcwd()}/{cachefile}".replace("\\", "/")
                
            w_client = WeatherClient("weather")
            temp, info, h_temp, l_temp, location = w_client.retrieve()
            url = w_client.cFile(file=cachefile)

            n_client = NewsClient("today's news")
            resultnum, results = n_client.retrieve()
            result_list = []
            for result in results:
                reporter = result['source']['name']
                news_url = result['url']
                news = result['title']
                img_url = result['urlToImage']
                if "<" in news and ">" in news or "..." in news or "…" in news:
                    pass
                else:
                    try:
                        str(news)
                        result_list.append({'reporter':f'{reporter}', 'url':f'{news_url}', 'news':f'{news}', 'imgUrl':f'{img_url}'})
                    except:
                        pass
            url = n_client.cFile(result_list, file=cachefile)

            self.func_dataEmmited.emit(url)
            time.sleep(2)
            self.func_dataEmmited.emit(f"{url}#card-1")
            speak(f"Good {ttime} Master!")
            self.func_dataEmmited.emit(f"{url}#card-2")
            speak(f"It's {temp} ({info}) with a high of {h_temp} and low of {l_temp} in {location}.")
            # self.func_dataEmmited.emit(f"{url}#card-3")
            speak("Here's the latest news.")

            i = 1
            for result in result_list:
                if i <= 5:
                    furl = f"{url}#flex-{i}"
                    self.func_dataEmmited.emit(furl)
                    speak(f"{result['news']}")
                    i += 1
                else:
                    break
            
    except Exception as e:
        log(e)

def googleData(self, query, patterns=[""]):
    """Search Google for a query"""
    try:
        print("Searching Google...")
        nquery = query
        for item in patterns:
            pattern = item.replace("[search]", "(.*)")
            match = re.search(pattern, query)
            if match:
                nquery = match.group(1)
                return nquery

        client = GoogleClient(query)

        url = client.link()
        speak(self.reply.replace("[search]", nquery))
        self.func_dataEmmited.emit(url)

        result = client.retrieve()
        if str(result) == "None":
            pass
        else:
            speak(result)

    except Exception as e:
        log(e)
    
def wikiData(self, query, patterns=[""]):
    "Search Wikipedia for a query"
    try:
        print("Searching WikiPedia...")
        nquery = query
        for item in patterns:
            pattern = item.replace("[query]", "(.*)")
            match = re.search(pattern, query)
            if match:
                nquery = match.group(1)
                return nquery

        client = WikipediaClient(nquery)

        url = client.link()
        self.func_dataEmmited.emit(url)

        result = client.retrieve()
        speak(f"According to Wikipedia, {result}")
    except Exception as e:
        log(e)
        googleData(self, query)

def youtubeData(self, query, patterns=[""]):
    """Search Youtube for a query"""
    try:
        print("Searching Youtube...")
        for item in patterns:
            pattern = item.replace("[query]", "(.*)")
            match = re.search(pattern, query)
            if match:
                query = match.group(1)
                return query
        self.func_dataEmmited.emit(f"https://www.youtube.com/search?q={query}")
    except Exception as e:
        log(e)

def youtubeTool(self, query):
    if self.action == "pause" and query == "youtube_pause":
        self.youtube_action.emit("pause")
        self.action = "resume"
        print("Paused")
    elif self.action == "resume" and query == "youtube_resume":
        self.youtube_action.emit("resume")
        self.action = "pause"
        print("Resumed")
    elif query == "youtube_next":
        self.youtube_action.emit("next")
        self.action = "pause"
        print("Next video played")
    else:
        print("No action")
        pass

def getWeather(self, query):
    """Get Weather data of a particular location"""
    try:
        client = WeatherClient(query)
        temp, info, h_temp, l_temp, location = client.retrieve()
        url = client.cFile()

        self.func_dataEmmited.emit(url)
        if h_temp != "--" and l_temp != "--":
            speak(f"The current weather condition is {info} with a high of {h_temp} degrees and a low of {l_temp} degrees.")
        else:
            speak(f"The temperature is currently {temp} degrees and the condition is {info}.")

    except Exception as e:
        speak("Master, Can't fetch the weather at the moment!", error=True)
        log(e)

def getPrecipitation(self, query):
    """Get Precipitation data of a particular location"""
    try:
        client = WeatherClient(query)
        client.retrieve()
        url = client.cFile()

        ppChance = client.ppChance
        self.func_dataEmmited.emit(url)

        # speak(f"It is {temp}°C ({info}) in {location}.")
        ppChanceInt = int(str(ppChance).replace("%", ""))
        if ppChanceInt >= 1 and ppChanceInt < 10:
            speak(f"I have checked the weather, it is not expected to rain today.")
        elif ppChanceInt >= 10:
            speak(f"According to the latest weather update, there's a {ppChance} chance of rain today.")
        else:
            speak("According to the latest weather update, there's no chance of rain today.")
        print(f"Percentage Of Precipitation (PoP): {ppChance}")

    except Exception as e:
        speak("Master, Can't fetch the precipitation data at the moment!", error=True)
        log(e)

def getNews(self, query:str):
    """Search news with (newsapi.com) to get required news"""
    try:
        newsclient = NewsClient(query)

        resultnum, results = newsclient.retrieve()
        result_list = []

        for result in results:
            reporter = result['source']['name']
            news_url = result['url']
            news = result['title']
            img_url = result['urlToImage']
            if "<" in news and ">" in news or "..." in news or "…" in news:
                pass
            else:
                try:
                    str(news)
                    result_list.append({'reporter':f'{reporter}', 'url':f'{news_url}', 'news':f'{news}', 'imgUrl':f'{img_url}'})
                except:
                    pass

        main_url = newsclient.cFile(result_list)
        self.func_dataEmmited.emit(main_url)
        speak(self.reply)

        i = 1
        for result in result_list:
            if i <= resultnum:
                url = f"{main_url}#flex-{i}"
                self.func_dataEmmited.emit(url)
                speak(f"{result['news']}")
                i += 1
            else:
                break

    except Exception as e:
        log(e)
        speak("Master, Can't fetch the news at the moment!", error=True)

def playMedia(self, query:str):
    """Play media on Youtube"""
    try:
        apiKey = 'AIzaSyCLJ77KOHuRB7jLJmSn78MQtePP0O9q838'
        service = build('youtube', 'v3', developerKey=apiKey)

        title = ""
        url = "https://www.youtube.com"

        request = service.search().list(
            q=query,
            part='snippet',
            type='video',
            maxResults=1
        )

        response = request.execute()

        for item in response['items']:
            title = item['snippet']['title']
            videoID = item['id']['videoId']
            url = f"https://www.youtube.com/watch?v={videoID}"

        speak(f"Playing {title}")

        self.func_dataEmmited.emit(url)
        service.close()

    except Exception as e:
        speak("Master, Can't play the media at the moment!", error=True)
        log(e)

def getLocation(self, query:str, patterns=[""]):
    """Get Location of a place"""
    try:
        
        mapclient = MapClient(query, patterns)
        location = str(mapclient.extractLocation())
        mapclient.locate(location)
        url = mapclient.retrieve()
        self.func_dataEmmited.emit(url)

        return location.title()

    except Exception as e:
        log(e)
        speak("Can't locate the queried location", error=True)

def navigateMap(self, query:str, patterns=[""]):
    """Navigate to a place"""
    try:
        mapclient = MapClient(query, patterns)

        if "from" in query:
            origin, destination = mapclient.extractRoute(query)
            mapclient.navigate(origin, destination)
            
            url = mapclient.retrieve()
            print(url)
            self.func_dataEmmited.emit(url)

            return f"{destination.title()} from {origin.title()}"
        else:
            destination = mapclient.extractDestination(query)
            mapclient.navigate("", destination)

            url = mapclient.retrieve()
            print(url)
            self.func_dataEmmited.emit(url)

            return destination.title()
        
    except Exception as e:
        log(e)
        speak("Can't get directions for the location", error=True)

def getJoke(self, query:str):
    "Search the joke related to the user query"
    try:
        query = query.replace("jessica", "")

        jokeclient = JokeClient(query)
        joke = jokeclient.retrieve()
        url = jokeclient.cFile()

        ignoreWords = ["Q: ", "Q. ", "A: ", "A. "]
        for words in ignoreWords:
            joke = joke.replace(words, "")

        self.func_dataEmmited.emit(url)
        starts = ["One joke, coming up!", "This might make you laugh."]
        joke = f"{choice(starts)} {joke}"
        speak(joke)

    except Exception as e:
        log(e)
        speak("Can't crack any joke at the moment", error=True)

def getScrnShot():
    try:
        speak("Master, Hold on the screen I am taking a screenshot.", logging=False)

        if not os.path.exists(SSPATH):
            os.mkdir(SSPATH)

        list = os.listdir(SSPATH)
        if len(list) != 0:
            num_list = []
            for file in list:
                try:
                    file = re.findall(r'\d+', file)[0]
                    num_list.append(int(file))
                except IndexError:
                    pass

            num_list.sort()
            num_file = num_list[len(num_list)-1]+1
        else:
            num_file = 1

        img = pyautogui.screenshot()  # type: ignore
        img.save(f"{SSPATH}/Screenshot ({num_file}).png")
    except Exception as e:
        log(e)
        speak("Can't take screenshot at the moment", error=True)

def clearCache():
    """Clear cache from windows temp directories"""
    try:
        speak("Clearing Cache files", logging=False)
        pathList = [f"{pathlib.Path.home()}/AppData/Local/Temp/", "C:/Windows/Temp/"]
        for path in pathList:
            os.chdir(path)
            list = os.listdir(path)
            for file in list:
                try:
                    os.remove(f"{path}{file}")
                except Exception as e:
                    pass

    except Exception as e:
        log(e)

def getBattery(self):
    """Get information about the system battery"""
    try:
        battery = psutil.sensors_battery()  # type: ignore
        battery_usage = str(battery.percent)
        battery_plug = battery.power_plugged
        battery_hour = time.strftime("%H", time.gmtime(battery.secsleft))
        battery_min = time.strftime("%M", time.gmtime(battery.secsleft))

        if battery_hour == "01":
            battery_htime = f"an hour"
        elif battery_hour == "00":
            battery_htime = ""
        else:
            battery_htime = f"{battery_hour} hours"

        if battery_min == "01":
            battery_mtime = f"{battery_min} minute"
        elif battery_min == "00":
            battery_mtime = ""
        else:
            battery_mtime = f"{battery_min} minutes"

        battery_time = f"{battery_htime} {battery_mtime}"

        if battery_plug == True:
            speak(str(self.reply).replace("[battery]", battery_usage).replace("[status]", "charging"), logging=False)
        else:
            speak(str(self.reply).replace("[battery]", battery_usage).replace("[status]", f"able to work for {battery_time}"), logging=False)

    except Exception as e:
        speak("Can't retrieve the battery information.", error=True)
        log(e)

def logOut(self):
    """Get logout from the system"""
    try:
        speak(self.reply)
        confirmation = str(takecommand(self))
        if "yes" in confirmation:
            speak("Logging you out from the System...")
            time.sleep(5)
            os.system("rundll32.exe user32.dll,LockWorkStation")
        else:
            print("Jessica: Cancelled Log Out")
    except Exception as e:
        log(e)

def shutDown(self):
    """Shutdown the system"""
    try:
        speak(self.reply)
        confirmation = str(takecommand(self))
        if "yes" in confirmation:
            speak("Shutting down the System...")
            print(confirmation)
            time.sleep(5)
            os.system("shutdown /s /t l")
        else:
            print(confirmation)
            print("Jessica: Cancelled Shut Down")
    except Exception as e:
        log(e)

def sleep():
    try:
        # import os, sys
        # from features.libraries.freq_detection import Tester
        # from threading import Thread
        # Thread(target=Tester).start()
        # Tester()
        # while self.keepRunning:s
        #     kk = tt.listen()
        #     if "True-Mic" == kk:
        #         print("Clapped")
        #         self.sleep = False
        #         break
        # os.execv(sys.executable, ["python", "features/libraries/freq_detection.py"])

        Thread(target=lambda: subprocess.call(["python", "features/libraries/freq_detection.py"])).start()

    except Exception as e:
        log(e)
        
def winRun(command):
    """Open Windows Run app and run a command"""
    pyautogui.hotkey('winleft', 'r')

    for word in command:
        pyautogui.press(word)
    pyautogui.press("enter")

def shellRun(command):
    """Run the given command in shell"""

    if command is str:
        command = command.split(" ")
    subprocess.run(command)

def openApp(self, query):
    """Open the specified application"""
    try:
        query = str(query).replace(" ", "").replace("open", "").replace("jessica", "")
        ibrowser = webbrowser.get('C:/Program Files/Google/Chrome/Application/chrome.exe %s --incognito')
        browser = webbrowser.get('windows-default')
        # speak("Opening...")
        if "screenshot" in query:
            os.startfile(SSPATH)
            speak(str(self.reply).replace("[application]", "Screenshots Folder"), logging=False)
        elif "google" in query:
            self.func_dataEmmited.emit("https://www.google.com/")
            speak(str(self.reply).replace("[application]", "Google"), logging=False)
        elif "youtubemusic" in query:
            self.func_dataEmmited.emit("https://music.youtube.com/")
            speak(str(self.reply).replace("[application]", "Youtube Music"), logging=False)
        elif "youtube" in query:
            self.func_dataEmmited.emit("https://www.youtube.com/")
            speak(str(self.reply).replace("[application]", "Youtube"), logging=False)
        elif "mail" in query or "gmail" in query:
            self.func_dataEmmited.emit("https://mail.google.com/")
            speak(str(self.reply).replace("[application]", "G-Mail"), logging=False)
        elif "whatsapp" in query:
            self.func_dataEmmited.emit("https://web.whatsapp.com/")
            speak(str(self.reply).replace("[application]", "WhatsApp"), logging=False)
        elif "instagram" in query:
            self.func_dataEmmited.emit("https://www.instagram.com/")
            speak(str(self.reply).replace("[application]", "Instagram"), logging=False)
        elif "facebook" in query:
            self.func_dataEmmited.emit("https://www.facebook.com/")
            speak(str(self.reply).replace("[application]", "Facebook"), logging=False)
        elif "chrome" in query:
            browser.open("https://chrome://new-tab-page")
            speak(str(self.reply).replace("[application]", "Chrome"), logging=False)
        elif "taskmanager" in query:
            shellRun("Taskmgr")
            speak(str(self.reply).replace("[application]", "Task Manager"), logging=False)
        elif "commandprompt" in query or "cmd" in query:
            shellRun("cmd")
            speak(str(self.reply).replace("[application]", "Command Prompt"), logging=False)
        elif "explorer" in query:
            shellRun("explorer")
            speak(str(self.reply).replace("[application]", "Windows Explorer"), logging=False)
        elif "notepad" in query:
            shellRun("notepad")
            speak(str(self.reply).replace("[application]", "Notepad"), logging=False)
        elif "controlpanel" in query:
            shellRun("control")
            speak(str(self.reply).replace("[application]", "Control Panel"), logging=False)
        elif "registryeditor" in query:
            shellRun("regedit")
            speak(str(self.reply).replace("[application]", "Registry Editor"), logging=False)
        elif "services" in query:
            shellRun("services.msc")
            speak(str(self.reply).replace("[application]", "Windows Services"), logging=False)
        elif "gpeditor" in query or "grouppolicyeditor" in query:
            shellRun("gpedit.msc")
            speak(str(self.reply).replace("[application]", "Windows Group Policy Editor"), logging=False)
        elif "taskview" in query:
            pyautogui.hotkey('winleft', 'tab')
            speak(str(self.reply).replace("[application]", "Task View"), logging=False)
        elif "hiddenmenu" in query:
            pyautogui.hotkey('winleft', 'x')
            speak(str(self.reply).replace("[application]", "Hidden Menu"), logging=False)
        elif "windowsetting" in query or "windowssettings" in query or "windowssetting" in query:
            shellRun("start ms-settings:winsettingshome")
            speak(str(self.reply).replace("[application]", "Windows Setting"), logging=False)
        else:
            ibrowser.open_new(f"https://www.google.com/search?q={query}")
    except Exception as e:
        speak("Master, Can't reach the application at the moment.", error=True)
        log(e)

def remindUser(query, patterns=[""]):
    try:
        query = str(query).replace("pm", "PM").replace("am", "AM")

        client = ReminderClient(query, patterns)
        time, purpose = client.retrieve()

        if purpose != None:
            responses = ["Okay, I've set a reminder to [purpose] at [time].", "Okay master, I've set a reminder for you to [purpose] at [time].", "Got it master, reminder set for [time] to [purpose].", "Reminder set for [time] to [purpose].", "Reminder set for [time] to [purpose]."]
        else:
            responses = ["Sure, reminder set for [time].", "Reminder set for [time]", "Master I've set an reminder for [time]", "Okay master, I've set the reminder for [time]."]

        return choice(responses).replace("[time]", time).replace("[purpose]", purpose)    # type: ignore        
    except Exception as e:
        speak("Can't set a reminder at the moment", error=True)
        log(e)

def sendMail(self, query, patterns=[""]):
    try:
        cancel = False

        mail_reason = ""
        for item in patterns:
            if "[reason]" in item:
                pattern = item.replace("[reason]", "(.*)")
                match = re.search(pattern, query)
                if match:
                    mail_reason = match.group(1)
                    break
            
        if mail_reason == "":
            speak("Master, what would you like to say in the email?")

            while self.keepRunning:
                query = takecommand(self)
                if query != "error":
                    break

            if "write an email" in query or "write email" in query or "write the email" in query:
                pass
            elif "cancel it" in query or "cancel email" in query or "cancel the email" in query or query == "cancel":
                cancel = True
                return ""
            else:
                query = f"Write an email to {query}"
            
        if not cancel:
            mail_body = str(replyAI(query))
            mail_id = ""
            mail_sub = ""

            mail_l = mail_body.split("\n")
            for data in mail_l:
                if "Subject: " in data:
                    mail_body = mail_body.replace(data, "").strip()
                    mail_sub = data.replace("Subject: ", "")

            url = f"https://mail.google.com/mail/u/0/?fs=1&tf=cm&to={mail_id}&su={mail_sub}&body={mail_body}"
            self.func_dataEmmited.emit(url)
            return mail_sub

    except Exception as e:
        speak("Can't reach the Mail client")
        log(e)