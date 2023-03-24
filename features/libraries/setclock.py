import datetime
import sys

import pywinauto

time_str = str(sys.argv[1])
time_obj = datetime.datetime.strptime(time_str, "%I:%M %p")
hour = time_obj.strftime("%I")
if hour.startswith("0"):
    hour = hour.replace("0", "")
min = time_obj.strftime("%M")
am_pm = time_obj.strftime("%p")

title = str(sys.argv[2])
repeat = str(sys.argv[3])

print(hour, min, am_pm, title, repeat)

app = pywinauto.Application(backend="uia").start("explorer.exe shell:Appsfolder\Microsoft.WindowsAlarms_8wekyb3d8bbwe!App")
app = app.connect(title_re="Alarms & Clock", timeout=10)

window = app.window(title_re="Alarms & Clock")

alarmTab = window.child_window(title="Alarm", auto_id="AlarmButton", control_type="ListItem")
alarmTab.wait('visible')
alarmTab.select()

alarmButton = window.child_window(title="Add new alarm", auto_id="AddAlarmButton", control_type="Button")
alarmButton.click()

alarmWindow = app.window(title_re="Alarms & Clock")

# Pick the Correct Time
timePicker = alarmWindow.child_window(title="Time Picker", auto_id="AlarmTimePicker", control_type="Pane")

hrPicker = timePicker.child_window(title="Hour", auto_id="HourLoopingSelector", control_type="List")
hrButton = hrPicker.child_window(title=hour, control_type="ListItem")
print(hrButton.exists())
hrButton.select()

minPicker = timePicker.child_window(title="Minute", auto_id="MinuteLoopingSelector", control_type="List")
minButton = minPicker.child_window(title=min, control_type="ListItem")
print(minButton.exists())
minButton.select()

pdPicker = timePicker.child_window(title="Period", auto_id="PeriodLoopingSelector", control_type="List")
pdButton = pdPicker.child_window(title=am_pm, control_type="ListItem")
print(pdButton.exists())
pdButton.select()

# Change the Alarm title
alarmTitle = alarmWindow.child_window(auto_id="AlarmNameTextBox")
print(alarmTitle.exists())
alarmTitle.type_keys(title, with_spaces=True)

if repeat == "True":
    # Set Alarm Frequency to Every day
    alarmFreq = alarmWindow.child_window(title="Repeats, Only once, ", auto_id="AlarmRepeatsToggleButton", control_type="Button")
    print(alarmFreq.exists())
    alarmFreq.click()

    freqPicker = alarmWindow.child_window(auto_id="AlarmRepeatsListView", control_type="List")
    print(freqPicker.exists())
    checkboxes = freqPicker.children(control_type='CheckBox')
    for checkbox in checkboxes:
        checkbox.toggle()
    pywinauto.keyboard.send_keys('{VK_ESCAPE}')

# Save the Alarm
saveButton = alarmWindow.child_window(title="Save", auto_id="AlarmSaveButton", control_type="Button")
print(saveButton.exists())
saveButton.click()

app.kill()