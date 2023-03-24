import re
import datetime
import subprocess
from PyQt5.QtCore import QObject
from threading import Thread


class ReminderClient(QObject):
    def __init__(self, query, patterns):
        self.query = query
        self.patterns = patterns

    def extract_time(self):
        try:
            time_regex = re.compile(r'\d{1,2}:\d{2} (AM|PM)')
            time_match = time_regex.search(self.query)
            if time_match:
                time_str = time_match.group()
                # str(self.query).replace(time_str, "")
                time = datetime.datetime.strptime(time_str, '%I:%M %p').time()
                return time, time_str
            else:
                raise Exception("No Time found")
        except:
            time_regex = re.compile(r'\d{1,2} (AM|PM)')
            time_match = time_regex.search(self.query)
            if time_match:
                time_str = time_match.group()
                # str(self.query).replace(time_str, "")
                time = datetime.datetime.strptime(time_str, '%I %p').time()
                return time, time_str
            else:
                raise Exception("No Time found", self.query)
    
    def extract_purpose(self, time):
        try:
            for item in self.patterns:
                pattern = item.replace("[purpose]", "(.*)").replace("[time]", time)
                if "everyday" in pattern or "daily" in pattern:
                    repeat = "True"
                else:
                    repeat = "False"
                match = re.search(pattern, self.query)
                if match:
                    purpose = match.group(1)
                    return purpose, repeat
        except:
            raise Exception("No Purpose found", self.query)

    def retrieve(self):
        time, timestr = self.extract_time()
        purpose, repeat = self.extract_purpose(timestr)
        thread = Thread(target= lambda: subprocess.run(["./v_env/Scripts/python.exe", "features/libraries/notifier.py", str(time), str(purpose).capitalize()]))
        thread.start()
        return timestr, purpose


# if __name__ == "__main__":
    # user_inputs = ["remind me to pick up groceries at 2:08 PM", "can you remind me at 10:30 PM to take medicines"]
    # patterns = ["please remind me to [purpose] at [time]",
    #             "can you set a reminder for me at [time] to [purpose]",
    #             "remind me at [time] to [purpose]",
    #             "can you remind me to [purpose] at [time]",
    #             "remind me to [purpose] at [time]",
    #             "can you remind me to [purpose] for a walk at [time]",
    #             "remind me to [purpose] at [time]",
    #             "set a reminder for [purpose] at [time]",
    #             "make a reminder for [purpose] at [time]",
    #             "create a reminder for [purpose] at [time]",
    #             "don't forget to remind me to [purpose] at [time]",
    #             "can you make a reminder for [purpose] at [time]"]
    # for user_input in user_inputs:
    #     client = AlarmClient(user_input, patterns)
    #     time, purpose = client.retrieve()
    #     print(time, purpose)
