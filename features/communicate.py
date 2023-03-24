import os
import subprocess

import openai
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
from playsound import playsound

error_list = [""]

def log(error):
    """Log an error into the log file."""
    import time
    curr_time = time.strftime("%x %H:%M:%S", time.localtime())

    if error != "":
        try:
            error = str(error).replace("\n", ",")
            error_list.append(error)
            list_len = len(error_list)
            
            if error == error_list[list_len-1] and error == error_list[list_len-2] and error == error_list[list_len-3]:
                pass
            else:
                open('static/error.log', 'a').write(f"[{curr_time}]   {error}\n")
        except:
            pass
    else:
        pass

def log_chat(data, error=False, file="static/chat_log.txt"):
    try:
        FileLog = open(file, "r+")
        chat_log_template = FileLog.read()

        chat_log_list = chat_log_template.split("\n")
        last_chat = chat_log_list[len(chat_log_list)-2]
        if not error:
            if data != last_chat:
                if data != "User: Error" and data != "User: Restart" and data != "User: Retrain" and data != "User: Exit":
                    FileLog.write(f"{data}\n")
        else:
            FileLog = open(file, "w")
            FileLog.write(chat_log_template.replace(f"{last_chat}\n", ""))
        FileLog.close()

    except Exception as e:
        log(e)

def rmlast_chat(file="static/chat_log.txt"):
    try:
        FileLog = open(file, "r+")
        chat_log_template = FileLog.read()

        chat_log_list = chat_log_template.split("\n")
        last_chat = chat_log_list[len(chat_log_list)-2]

        FileLog = open(file, "w")
        FileLog.write(chat_log_template.replace(f"{last_chat}\n", ""))
        FileLog.close()

    except Exception as e:
        log(e)

def speak(audio, FILE='static/sound/output.mp3', logging=True, error=False):
    """Speaks a string using gTTS."""
    try:
        if audio == "init":
            print(f"Jessica: Initializing system...\n")
            playsound("static/sound/initializing.mp3", True)
        elif audio == "import":
            print(f"Jessica: Importing dependencies...\n")
            playsound("static/sound/importing.mp3", True)
        else:
            tts = gTTS(audio, lang="en-in", slow=False)
            tts.save(FILE)

            # subprocess.call(["edge-tts", "--rate=-25%", "--voice", "en-US-JessaNeural", "--text", audio, "--write-media", FILE])

            print(f"Jessica: {audio}\n")
            playsound(FILE, True)
            os.remove(FILE)

        if logging and not error:
            log_chat(f"Jessica: {audio}")

    except Exception as e:
        log(e)

def translateText(text):
    try:
        translator = Translator()
        result = translator.translate(text)
        data = result.text  # type: ignore
        return str(data)
    
    except Exception as e:
        log(e)
        return text

def takecommand(self, logging=True):
    """Take microphone input from the user and return a string output"""
    try:
        r = sr.Recognizer()

        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            r.pause_threshold = 1
            # audio = r.listen(source, 0, 5)
            print("Listening...")
            self.right_dataEmmited.emit(1)
            audio = r.listen(source, phrase_time_limit=8)
        try:
            print("Recognizing")
            self.right_dataEmmited.emit(2)
            query = str(r.recognize_google(audio, language='en-in'))
            query = translateText(query)
            print(f"User: {query.capitalize()}\n")
        except Exception as e:
            if type(e) == str:
                log(e)
            else:
                pass
            query = "Error"

        if logging and not self.sleep and query != "Error":
            log_chat(f"User: {query.capitalize()}")
        
        return query.lower()
    except Exception as e:
        log(e)


openai.api_key = "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"
completion = openai.Completion()

def replyAI(question, chat_log=None):
    try:
        FileLog = open("static/chat_log.txt", "r")
        chat_log_template = FileLog.read()
        FileLog.close()

        if chat_log == None:
            chat_log = chat_log_template

        prompt = f"{chat_log}User: {question}\nJessica: "

        response = completion.create(
            model = "text-davinci-003",
            prompt=prompt,
            temperature=0.5,
            max_tokens=256,
            top_p=0.3,
            frequency_penalty=0.5,
            presence_penalty=0
        )

        answer = response.choices[0].text.strip()   # type: ignore

        return answer
    except Exception as e:
        log(e)