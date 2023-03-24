import json
import os
import pickle
import random
import sys

import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage
from tensorflow import keras

from features.communicate import *
from features.communicate import speak, takecommand, replyAI
from features.task import *


class WebCam(QObject):
    import cv2
    import mediapipe as mp
    test_img = None
    image_emmited = pyqtSignal(QImage)
    progress = pyqtSignal(int)
    close = pyqtSignal()

    keepRunning = True
    rate = 0

    def __init__(self):
        super().__init__()
        self.camera = self.getCam()
        if self.camera == "on":
            self.minDetectionCon = 0.5
            self.mpFaceDetection = self.mp.solutions.face_detection  # type: ignore
            self.mpDraw = self.mp.solutions.drawing_utils  # type: ignore
            self.faceDetection = self.mpFaceDetection.FaceDetection(self.minDetectionCon)
            
            self.cap = self.cv2.VideoCapture(0)
            success, img = self.cap.read()
            while self.rate < 5:
                success, img = self.cap.read()
                print(success)
                img = self.cv2.resize(img, (1920, 1040))
                img = self.cv2.flip(img, 1)
                img = QImage(img, img.shape[1], img.shape[0], img.strides[0], QImage.Format_RGB888).rgbSwapped()  # type: ignore
                # self.image_emmited.emit(img)
                self.rate += 1
    def getCam(self):
        with open("static/settings.json", "r") as jsonData:
            settings = json.load(jsonData)
            return settings['camera']

    def findFaces(self, img, draw=True):
        try:
            imgRGB = self.cv2.cvtColor(img, self.cv2.COLOR_BGR2RGB)
            self.results = self.faceDetection.process(imgRGB)
            # print(self.results)
            bboxs = []
            if self.results.detections:
                for id, detection in enumerate(self.results.detections):
                    bboxC = detection.location_data.relative_bounding_box
                    ih, iw, ic = img.shape  # type: ignore
                    bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                        int(bboxC.width * iw), int(bboxC.height * ih)
                    bboxs.append([id, bbox, detection.score])
                    if draw:
                        img = self.fancyDraw(img, bbox)
            return img, bboxs
        except Exception as e:
            log(e)
            
    def fancyDraw(self, img, bbox, l=30, t=5, rt= 1):
        try:
            x, y, w, h = bbox
            h1 = int(h/8)
            w1 = int(w/10)
            y = y-int(3.5*h1)
            h = h+int(3*h1)
            x = x-int(1.5*w1)
            w = w+int(3*w1)
            x1, y1 = x + w, y + h
            # print(x, y, w, h)

            if w<800:
                self.cv2.rectangle(img, (x, y, w, h), (255, 0, 255), rt)
                # Top Left  x,y
                self.cv2.line(img, (x, y), (x + l, y), (255, 0, 255), t)
                self.cv2.line(img, (x, y), (x, y+l), (255, 0, 255), t)
                # Top Right  x1,y
                self.cv2.line(img, (x1, y), (x1 - l, y), (255, 0, 255), t)
                self.cv2.line(img, (x1, y), (x1, y+l), (255, 0, 255), t)
                # Bottom Left  x,y1
                self.cv2.line(img, (x, y1), (x + l, y1), (255, 0, 255), t)
                self.cv2.line(img, (x, y1), (x, y1 - l), (255, 0, 255), t)
                # Bottom Right  x1,y1
                self.cv2.line(img, (x1, y1), (x1 - l, y1), (255, 0, 255), t)
                self.cv2.line(img, (x1, y1), (x1, y1 - l), (255, 0, 255), t)
            return img
        except Exception as e:
            log(e)

    @pyqtSlot()
    def run(self):
        try:
            if self.camera == 'on':
                while self.cap.isOpened() and self.keepRunning:
                    try:
                        success, img = self.cap.read()
                        if img is not None and success:
                            try:
                                img = self.cv2.resize(img, (1920, 1040))
                                img = self.cv2.flip(img, 1)
                                img, bboxs = self.findFaces(img)  # type: ignore
                                img = QImage(img, img.shape[1], img.shape[0], img.strides[0], QImage.Format_RGB888).rgbSwapped()  # type: ignore
                                self.image_emmited.emit(img)
                            except Exception as e:
                                if "can't grab frame" in str(e):
                                    pass
                                else:
                                    log(e)
                                    raise Exception(f"CamImg error: {e}")
                        else:
                            pass
                    except Exception as e:
                        print(type(e))
                        if str(e).startswith("[ WARN:0@128.049]"):
                            pass
                        else:
                            log(e)
                            raise Exception(f"Cam error: {e}")
            # else:
            #     self.progress.emit(20)
        except Exception as e:
            print(type(e))
            log(e)

    def stop(self):
        self.camera = 'off'
        self.keepRunning = False

class Network(QObject):
    data_emmited = pyqtSignal(str, int)
    progress = pyqtSignal(int)
    close = pyqtSignal()

    keepRunning = True
    fip_addressEmmited = pyqtSignal()

    @pyqtSlot()
    def run(self):
        import socket

        import pythonping
        self.fip_addressEmmited.connect(self.fip_address)
        self.progress.emit(10)
        self.fIp = None
        while self.keepRunning:
            try:
                ip_address = str(socket.gethostbyname(socket.gethostname()))
                ping = 999

                if ip_address != "127.0.0.1":
                    if self.fIp is None:
                        self.fIp = ip_address
                        self.fip_addressEmmited.emit()
                    ping_result = pythonping.ping(target='google.com', timeout=2)
                    ping = int(ping_result.rtt_avg_ms)
                    if ping < 1000:
                        ping = ping
                    else:
                        ping = 999
                else:
                    pass

                self.data_emmited.emit(ip_address, ping)
            except Exception as e:
                log(e)
    
    def fip_address(self):
        # speak(random.choice(["We're online, Master", "System is online"]))
        print("Ip")

    def stop(self):
        self.keepRunning = False

class Worker(QObject):
    left_dataEmmited = pyqtSignal(str)
    right_dataEmmited = pyqtSignal(int)
    func_dataEmmited = pyqtSignal(str)
    youtube_action = pyqtSignal(str)
    progress = pyqtSignal(int)
    close = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.keepRunning = True
        self.sleep = False
        self.action = "pause"

        with open("static/intents.json") as file:
            self.intents = json.load(file)

        self.model = keras.models.load_model('static/chat_model')  # type: ignore

        with open('static/tokenizer.pickle', 'rb') as handle:
            self.tokenizer = pickle.load(handle)

        with open('static/label_encoder.pickle', 'rb') as enc:
            self.lbl_encoder = pickle.load(enc)

        self.max_len = 20
        self.ignoreWords = [',', '?', '.', '!', '/']

        self.homeLocation = self.getHome()

    def getHome(self):
        self.progress.emit(20)
        with open("static/settings.json", "r") as jsonData:
            settings = json.load(jsonData)
            return settings['homeLocation']
        
    @pyqtSlot()
    def run(self):
        try:
            wishMe(self)
            while self.keepRunning:
                query = str(takecommand(self))
                for word in self.ignoreWords:
                    query = query.replace(word, "")
                
                result = self.model.predict(keras.preprocessing.sequence.pad_sequences(self.tokenizer.texts_to_sequences([query]), truncating='post', maxlen=self.max_len))  # type: ignore
                self.tag = self.lbl_encoder.inverse_transform([np.argmax(result)])
                print(self.tag)
                
                if self.keepRunning:
                    for intent in self.intents['intents']:
                        if self.tag == intent['tag']:
                            self.reply = random.choice(intent['responses'])
                            patterns = intent['patterns']
                            if not self.sleep:
                                if query == "error":
                                    self.left_dataEmmited.emit("Report")
                                    self.right_dataEmmited.emit(3)
                                    print("Jessica: ...\n")
                                elif query == "exit" or query == "quit":
                                    self.left_dataEmmited.emit("System")
                                    self.right_dataEmmited.emit(3)
                                    speak("Exiting..", logging=False)
                                    self.close.emit()
                                    self.stop()
                                    break
                                elif query == "restart":
                                    self.left_dataEmmited.emit("System")
                                    self.right_dataEmmited.emit(3)
                                    speak("Restarting", logging=False)
                                    os.execv(sys.executable, ['python'] + sys.argv)
                                elif query == "retrain":
                                    self.left_dataEmmited.emit("System")
                                    self.right_dataEmmited.emit(3)
                                    speak("Retraining...", logging=False)
                                    os.execv(sys.executable, ["python", "train.py"])
                                elif query == "jessica":
                                    self.left_dataEmmited.emit("Report")
                                    self.right_dataEmmited.emit(3)
                                    speak("At your service Master.")
                                elif self.tag == "welcome":
                                    self.left_dataEmmited.emit("Report")
                                    self.right_dataEmmited.emit(3)
                                    rmlast_chat()
                                    speak(self.reply, logging=False)
                                elif self.tag == "health":
                                    self.left_dataEmmited.emit("Report")
                                    self.right_dataEmmited.emit(3)
                                    rmlast_chat()
                                    speak(self.reply, logging=False)
                                elif self.tag == "my_health":
                                    self.left_dataEmmited.emit("Report")
                                    self.right_dataEmmited.emit(3)
                                    rmlast_chat()
                                    speak(self.reply, logging=False)
                                elif self.tag == "thanks":
                                    self.left_dataEmmited.emit("Report")
                                    self.right_dataEmmited.emit(3)
                                    rmlast_chat()
                                    speak(self.reply, logging=False)
                                elif self.tag == "dev_intro":
                                    self.left_dataEmmited.emit("Report")
                                    self.right_dataEmmited.emit(3)
                                    speak(self.reply)
                                elif self.tag == "cmd_list":
                                    self.left_dataEmmited.emit("Report")
                                    self.right_dataEmmited.emit(3)
                                    speak(self.reply)
                                elif self.tag == "time":
                                    self.left_dataEmmited.emit("Clock")
                                    self.right_dataEmmited.emit(3)
                                    getTime(self, query)
                                elif self.tag == "search":
                                    self.left_dataEmmited.emit("Search")
                                    self.right_dataEmmited.emit(3)
                                    if "wikipedia" in query:
                                        wikiData(self, query, patterns)
                                    if "google search" in query:
                                        googleData(self, query, patterns)
                                    else:
                                        self.reply = replyAI(self, query)
                                        speak(self.reply)
                                elif self.tag == "youtube":
                                    self.left_dataEmmited.emit("Search")
                                    self.right_dataEmmited.emit(3)
                                    query = str(youtubeData(self, query))
                                    speak(self.reply.replace("[query]", query))
                                elif self.tag == "multimedia":
                                    self.left_dataEmmited.emit("MultiMedia")
                                    self.right_dataEmmited.emit(3)
                                    playMedia(self, query)
                                elif self.tag == "youtube_pause":
                                    self.left_dataEmmited.emit("MultiMedia")
                                    self.right_dataEmmited.emit(3)
                                    rmlast_chat()
                                    youtubeTool(self, self.tag)
                                elif self.tag == "youtube_resume":
                                    self.left_dataEmmited.emit("MultiMedia")
                                    self.right_dataEmmited.emit(3)
                                    rmlast_chat()
                                    youtubeTool(self, self.tag)
                                elif self.tag == "youtube_next":
                                    self.left_dataEmmited.emit("MultiMedia")
                                    self.right_dataEmmited.emit(3)
                                    rmlast_chat()
                                    youtubeTool(self, self.tag)
                                elif self.tag == "weather":
                                    self.left_dataEmmited.emit("Weather")
                                    self.right_dataEmmited.emit(3)
                                    getWeather(self, query)
                                elif self.tag == "precipitate":
                                    self.left_dataEmmited.emit("Weather")
                                    self.right_dataEmmited.emit(3)
                                    getPrecipitation(self, query)
                                elif self.tag == "news":
                                    self.left_dataEmmited.emit("News")
                                    self.right_dataEmmited.emit(3)
                                    getNews(self, query)
                                elif self.tag == "locate":
                                    self.left_dataEmmited.emit("Location")
                                    self.right_dataEmmited.emit(3)
                                    location = getLocation(self, query)
                                    speak(self.reply.replace("[location]", location))
                                elif self.tag == "navigate":
                                    self.left_dataEmmited.emit("Location")
                                    self.right_dataEmmited.emit(3)
                                    location = navigateMap(self, query)
                                    speak(self.reply.replace("[location]", location))
                                elif self.tag == "open":
                                    self.left_dataEmmited.emit("Applications")
                                    self.right_dataEmmited.emit(3)
                                    rmlast_chat()
                                    openApp(self, query)
                                elif self.tag == "greet":
                                    self.left_dataEmmited.emit("Report")
                                    self.right_dataEmmited.emit(3)
                                    wishMe(self, start=False)
                                elif self.tag == "screenshot":
                                    self.left_dataEmmited.emit("System")
                                    self.right_dataEmmited.emit(3)
                                    rmlast_chat()
                                    getScrnShot()
                                    speak(self.reply, logging=False)
                                elif self.tag == "clear_cache":
                                    self.left_dataEmmited.emit("System")
                                    self.right_dataEmmited.emit(3)
                                    rmlast_chat()
                                    clearCache()
                                    speak(self.reply, logging=False)
                                elif self.tag == "battery":
                                    self.left_dataEmmited.emit("Battery")
                                    self.right_dataEmmited.emit(3)
                                    rmlast_chat()
                                    getBattery(self)
                                elif self.tag == "reminder":
                                    self.left_dataEmmited.emit("Clock")
                                    self.right_dataEmmited.emit(3)
                                    nreply = remindUser(query, patterns)
                                    speak(nreply)
                                elif self.tag == "mail":
                                    self.left_dataEmmited.emit("Message")
                                    self.right_dataEmmited.emit(3)
                                    sub = sendMail(self, query, patterns)
                                    if sub != "" or sub != None:
                                        speak(self.reply.replace("[reason]", sub))
                                    else:
                                        speak("Can't reach the Mail client")
                                elif self.tag == "sleep":
                                    self.left_dataEmmited.emit("Report")
                                    self.right_dataEmmited.emit(3)
                                    rmlast_chat()
                                    speak(self.reply, logging=False)
                                    self.sleep = True
                                elif self.tag == "goodnight":
                                    rmlast_chat()
                                    self.right_dataEmmited.emit(3)
                                    import datetime
                                    hour = int(datetime.datetime.now().hour)
                                    if hour >= 20 and hour <= 23:
                                        self.left_dataEmmited.emit("System")
                                        speak(self.reply, logging=False)
                                        self.sleep = True
                                        break
                                    else:
                                        self.left_dataEmmited.emit("Report")
                                        speak("Master, You are going to bed too early!", logging=False)
                                elif self.tag == "logout":
                                    self.left_dataEmmited.emit("System")
                                    self.right_dataEmmited.emit(3)
                                    # speak(self.reply)
                                    logOut(self)
                                elif self.tag == "shutdown":
                                    self.left_dataEmmited.emit("System")
                                    self.right_dataEmmited.emit(3)
                                    shutDown(self)
                                else:
                                    self.left_dataEmmited.emit("Report")
                                    self.right_dataEmmited.emit(3)
                                    print("OpenAI")
                                    self.reply = replyAI(query)
                                    speak(self.reply)
                            else:
                                if self.tag == "wakeup" and self.sleep:
                                    rmlast_chat()
                                    speak(self.reply, logging=False)
                                    self.sleep = False
                else:
                    speak("Master, I can't understand your command!")
            self.close.emit()
        except Exception as e:
            log(e)

    def stop(self):
        self.keepRunning = False
