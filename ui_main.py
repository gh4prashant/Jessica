import json
import sys
import random
from threading import Thread

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *

from features.communicate import speak, log
from static.ui.ui_interface import Ui_MainWindow


class Window(QMainWindow, Ui_MainWindow):
    finished = pyqtSignal()
    def __init__(self):
        QMainWindow.__init__(self)
        try:
            self.setupUi(self)
            self.setWindowTitle("Jessica")
            self.setWindowIcon(QIcon("static/icons/logo.ico"))
            self.resize(width, height)
            self.showMaximized()
            self.setWindowFlags(Qt.FramelessWindowHint)  # type: ignore

            self.close_button.clicked.connect(self.quit)
            
            self.timer1 = QTimer(self)
            self.timer1.timeout.connect(self.animate_progress)

            self.min_browser.clicked.connect(self.animate_func)

            self.shortcut_1 = QShortcut(self)
            self.shortcut_1.setKey(QKeySequence('Alt+Left'))
            self.shortcut_1.activated.connect(self.browser.back)
            self.shortcut_2 = QShortcut(self)
            self.shortcut_2.setKey(QKeySequence('Alt+Right'))
            self.shortcut_2.activated.connect(self.browser.forward)
            self.shortcut_3 = QShortcut(self)
            self.shortcut_3.setKey(QKeySequence('Ctrl+R'))
            self.shortcut_3.activated.connect(self.browser.reload)
            self.shortcut_4 = QShortcut(self)
            self.shortcut_4.setKey(QKeySequence('Escape'))
            self.shortcut_4.activated.connect(self.animate_func)

            profile = QWebEngineProfile("jbrowser-data", self)
            profile.setCachePath("browser/")
            profile.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)  # type: ignore

            self.webpage = QWebEnginePage(profile, self.browser)
            self.webpage.settings().setAttribute(QWebEngineSettings.PlaybackRequiresUserGesture, False)  # type: ignore
            
            self.browser.setPage(self.webpage)
            self.browser.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)  # type: ignore
            self.browser.settings().setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)  # type: ignore
            self.browser.settings().setAttribute(QWebEngineSettings.AllowRunningInsecureContent, True)  # type: ignore
            self.browser.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)  # type: ignore
            self.browser.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)  # type: ignore
            self.browser.show()

            self.keepRunning = True
            self.processing = True
            self.webLoaded = False
            self.value = 0
            self.browser.loadFinished.connect(self.check_webLoad)

            self.prompt_box.hide()
            self.func_menu.raise_()

        except Exception as e:
            if type(e) == RuntimeError:
                log(e)
                self.quit()
            else:
                log(e)    
    
    def getSettings(self):
        with open("static/settings.json", "r") as jsonData:
            settings = json.load(jsonData)
            self.camera = settings['camera']

    def progress(self, value):
        try:
            nValue = self.value + value
            self.value = nValue

            print(f"[{self.value}/100] Loading...")
            if nValue >= 100:
                try:
                    speak(random.choice(["We're ready Master", "System initialization complete", "System is ready", "System is ready to operate", "System check complete"]), logging=False)
                except Exception as e:
                    log(e)
                finally:
                    self.finished.emit()
                    self.th1.start()
                    self.processing = False
        except Exception as e:
            log(e)

    def start(self):
        try:
            speak("init", logging=False)
            self.getSettings()
            self.timer1.start(1000)
            self.progress(10)
            
            self.animate_progress()
            self.animate_opmenu(label_no=3)
            self.add_memory()
            self.scroll('Report')
            self.progress(10)
            speak("import", logging=False)

            from static.tools import WebCam
            self.th1 = QThread(self)
            self.cam = WebCam()
            self.cam.moveToThread(self.th1)
            self.cam.image_emmited.connect(self.set_webCam)
            self.cam.progress.connect(self.progress)
            self.th1.started.connect(self.cam.run)
            self.cam.close.connect(self.quit)
            self.progress(25)
            
            from static.tools import Network
            self.th2 = QThread(self)
            self.network = Network()
            self.network.moveToThread(self.th2)
            self.network.data_emmited.connect(self.set_networkInfo)
            self.network.progress.connect(self.progress)
            self.th2.started.connect(self.network.run)
            self.network.close.connect(self.quit)
            self.th2.start()
            self.progress(10)

            from static.tools import Worker
            self.th3 = QThread(self)
            self.worker = Worker()
            self.worker.moveToThread(self.th3)
            self.worker.left_dataEmmited.connect(self.scroll)
            self.worker.right_dataEmmited.connect(self.animate_opmenu)
            self.worker.func_dataEmmited.connect(self.set_webPage)
            self.worker.youtube_action.connect(self.send_webKey)
            self.worker.progress.connect(self.progress)
            self.th3.started.connect(self.worker.run)
            self.worker.close.connect(self.quit)
            self.progress(25)

            # self._show()

        except Exception as e:
            log(e)

    def _start(self):
        Thread(target=self.start, daemon=True).start()

    def _show(self):
        self.show()
        self.th3.start()

    def quit(self, camWin=True, netWin=True, workWin=True, mainWin=True):
        if camWin:
            try:
                self.cam.stop()
                if self.camera == 'on':
                    self.cam.cap.release()
                self.th1.terminate()
                self.th1.wait()
                self.cam.deleteLater()
                self.th1.deleteLater()
            except Exception as e:
                log(e)
        if netWin:
            try:
                self.network.stop()
                self.th2.terminate()
                self.th2.wait()
                self.network.deleteLater()
                self.th2.deleteLater()
            except Exception as e:
                log(e)
        if workWin:
            try:
                self.worker.stop()
                self.th3.terminate()
                self.th3.wait()
                self.worker.deleteLater()
                self.th3.deleteLater()
            except Exception as e:
                log(e)
        if mainWin:
            try:
                self.keepRunning = False
                self.browser.close()
                self.close()
                self.deleteLater()
            except Exception as e:
                log(e)

    def set_webCam(self, image):
        try:
            if self.camera == 'on':
                self.centralwidget.setPixmap(QPixmap.fromImage(image))
            else:
                self.centralwidget.setPixmap(QPixmap('static/icons/background.png'))
        except Exception as e:
            self.centralwidget.setPixmap(QPixmap('static/icons/background.png'))
            log(e)

    def animate_opmenu(self, label_no:int):
        try:
            self.anim1 = QPropertyAnimation(self.animated_label, b"pos")
            label_ypos = self.animated_label.geometry().y()
            if label_no == 1:
                label_ypos = 215
            elif label_no == 2:
                label_ypos = 352
            elif label_no == 3:
                label_ypos = 489
            elif label_no == 4:
                label_ypos = 626
            elif label_no == 5:
                label_ypos = 763
            self.anim1.setEndValue(QPoint(1610, label_ypos))
            self.anim1.setEasingCurve(QEasingCurve.InOutCubic)  # type: ignore
            self.anim1.setDuration(2000)
            self.anim1.start()
        except Exception as e:
            log(e)

    def animate_func(self):
        try:
            self.anim2 = QPropertyAnimation(self.func_menu, b"pos")
            if self.min_browser.text() == "<":
                self.anim2.setEndValue(QPoint(-760, self.func_menu.y()))
                self.min_browser.setText(">")
                self.shortcut_4.setEnabled(False)
            elif self.min_browser.text() == ">":
                self.anim2.setEndValue(QPoint(20, self.func_menu.y()))
                self.min_browser.setText("<")
                self.shortcut_4.setEnabled(True)
            else:
                self.anim2.setEndValue(QPoint(20, self.func_menu.y()))
                self.min_browser.setText("<")
                self.shortcut_4.setEnabled(True)
            self.anim2.setEasingCurve(QEasingCurve.InOutCubic)  # type: ignore
            self.anim2.setDuration(2000)
            self.anim2.start()
        except Exception as e:
            log(e)
            
    def set_webPage(self, data:str):
        try:
            self.min_browser.setText("!")
            self.animate_func()
            if data.startswith(("https", "http", "file")):
                self.browser.load(QUrl(data))
            else:
                self.browser.setHtml(data)
        except Exception as e:
            log(e)

    def check_webLoad(self):
        self.webLoaded = True

    def send_webKey(self, key):
        while self.keepRunning:
            if self.webLoaded == True:
                if key == "pause" or key == "resume":
                    event = QKeyEvent(QEvent.KeyPress, Qt.Key_K, Qt.NoModifier)     # type: ignore
                    event.artificial = True     # type: ignore
                    QCoreApplication.postEvent(self.browser.focusProxy(), event)
                elif key == "next":
                    event = QKeyEvent(QEvent.KeyPress, Qt.Key_N, Qt.ShiftModifier)     # type: ignore
                    event.artificial = True     # type: ignore
                    QCoreApplication.postEvent(self.browser.focusProxy(), event)
                else:
                    pass
                break
            else:
                pass

    def scroll(self, scroll_to: str):
        try:
            for x in range(self.command_list.count()):
                item = self.command_list.item(x)
                if scroll_to.lower() in item.text().lower():
                    item.setSelected(True)
                    self.command_list.scrollToItem(item, QAbstractItemView.PositionAtCenter)  # type: ignore
                else:
                    pass
        except Exception as e:
            log(e)

    def animate_progress(self):
        try:
            import psutil
            cpu_usage = int(psutil.cpu_percent())
            ram_usage = int(psutil.virtual_memory()[2])
            disk_usage = int(psutil.disk_usage("/")[3])

            self.cpu_progressBar.setValue(cpu_usage)
            self.ram_progressBar.setValue(ram_usage)
            self.disk_progressBar.setValue(disk_usage)
        except Exception as e:
            log(e)

    def set_networkInfo(self, ip_address, ping):
        try:
            if ping == 999:
                self.ping_label.setStyleSheet("background: none; color: rgb(255, 0, 0); font: 14pt \"Orbitron\";")
            else:
                self.ping_label.setStyleSheet("background: none; color: rgb(255, 255, 255); font: 14pt \"Orbitron\";")

            self.ip_label.setText(ip_address)
            self.ping_label.setText(str(ping))
        except Exception as e:
            log(e)

    def add_memory(self):
        try:
            self.command_list.addItem("M01 : Report")
            self.command_list.addItem("M02 : File")
            self.command_list.addItem("M03 : Message")
            self.command_list.addItem("M04 : Search")
            self.command_list.addItem("M05 : MultiMedia")
            self.command_list.addItem("M06 : Battery")
            self.command_list.addItem("M07 : Weather")
            self.command_list.addItem("M08 : Clock")
            self.command_list.addItem("M09 : Calendar")
            self.command_list.addItem("M10 : News")
            self.command_list.addItem("M11 : Location")
            self.command_list.addItem("M12 : Applications")
            self.command_list.addItem("M13 : System")

            self.command_list.setAutoScroll(True)
            self.command_list.setDisabled(True)
            self.command_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # type: ignore
        except Exception as e:
            log(e)


class SplashScreen(QSplashScreen):
    def __init__(self):
        try:
            QSplashScreen.__init__(self, QPixmap("static/icons/full_logo2.png"))
            # self.setWindowTitle("Jessica [Initializing...]")
            # self.setWindowFlags(Qt.WindowStaysOnTopHint)  # type: ignore
            # self.setWindowFlags(Qt.SplashScreen | Qt.WindowStaysOnTopHint)  # type: ignore
            self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)  # type: ignore
            self.setEnabled(False)
            # self.showMessage("Initializing...", Qt.AlignBottom | Qt.AlignHCenter)  # type: ignore
            self.show()
            # Thread(target=lambda: self.show()).start()
            self.activateWindow()
            self.raise_()
            # Thread(target=lambda: speak("init")).start()
        
        except Exception as e:
            log(e)
    
    def _close(self):
        self.close()
        self.deleteLater()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    screen_resolution = app.desktop().screenGeometry()
    width, height = screen_resolution.width(), screen_resolution.height()
    
    splash = SplashScreen()
    win = Window()
    # win.processing = True
    win.finished.connect(splash._close)
    win.progress(10)
    Thread(target=win.start, daemon=True).start()
    # win.start()
    while win.processing:
        app.processEvents()
    win._show()
    
    app.aboutToQuit.connect(win.quit)
    try:
        sys.exit(app.exec_())
    except SystemExit:
        print('Closing Window...')
