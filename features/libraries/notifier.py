import sys
from plyer import notification
import datetime, time
from pygame import mixer


def show_notification(wait_time, message):
    mixer.init() 
    sound=mixer.Sound("static/sound/reminder.mp3")
    time.sleep(wait_time)

    notification.notify(title="Alarms & Reminder", message=message, app_name='Jessica', timeout=10)
    sound.play()


alarm_time = datetime.datetime.strptime(str(sys.argv[1]), '%H:%M:%S').time()
purpose = sys.argv[2]
print(alarm_time, purpose)

current_time = datetime.datetime.now().time()
wait_time = (datetime.datetime.combine(datetime.datetime.today(), alarm_time) -
                datetime.datetime.combine(datetime.datetime.today(), current_time)).total_seconds()
print(wait_time)

show_notification(wait_time, purpose)