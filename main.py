# -*- coding: utf-8 -*-
import os
from time import sleep 
import uuid
from pathlib import Path
import re
from pyrogram import Client, filters
from pyrogram.raw.functions.account import ReportPeer
from pyrogram.raw.types import InputPeerChannel, InputReportReasonOther
from datetime import datetime

session_path = Path('session')
report_path = Path('reports')
last_time_upd = datetime.now()

MAX_REPORT_BY_HOUR = 40 # Кількість репортів після яких буде перерва
current_reports = 0

print("Очікуйте конфігурацію скрипта")

def on_start():
    global last_time_upd
    global current_reports
    if report_path.exists():
        with open(report_path, 'r') as file:
            info = file.read().split("\n")
            last_time_upd = info[0]
            current_reports = int(info[1])
    else:
        with open(report_path, 'w') as file:
            file.write(str(last_time_upd) + "\n" + str(current_reports))



    if session_path.exists():
        with open(session_path) as file:
            session_string = file.read()

            if not session_string:
                os.remove(session_path)
                print("Стара конфігурація видалена")
                print("Перезапустіть програму щоб почати користування")
                exit()

            return Client(session_string)

    else:
        with Client(uuid.uuid4().hex) as tmp_app:
            with open(session_path, 'w') as file:
                session_string = tmp_app.export_session_string()
                file.write(session_string)  # noqa

        print("Програма сконфігурована")
        print("Перезапустіть програму щоб почати користування")
        exit()

app = on_start()

def new_report_channel(_,__,query):
    return query.chat.id == -1001663460417
new_report_channel_filter = filters.create(new_report_channel)


def updTimeRep(value):
    global last_time_upd
    count = getCount()
    with open(report_path, 'w') as file:
                file.write(str(last_time_upd) + "\n")
                file.write(str(count+value))

def getCount(): 
    global current_reports  
    with open(report_path, 'r') as file:
        info = file.read().split("\n")
        current_reports = int(info[1])
        return int(info[1])

@app.on_message(new_report_channel_filter)
def cmd_report(client, message):
    global last_time_upd
    global current_reports
    global isSendNotif

    urls = re.findall(r'https?://t.me/\S+', message.text)
    new_urls = []
    for i in urls:
        new_urls.append("@"+i[13:])

    for url in  new_urls:
        try:
            
            if int(getCount()) >= MAX_REPORT_BY_HOUR:
                
                timeOverSec = 0

                if type(last_time_upd) == str:
                    timeOverSec = (datetime.now() - datetime.fromisoformat(last_time_upd)).total_seconds()
                else:
                    timeOverSec = (datetime.now() - last_time_upd).total_seconds()
                app.send_message("me",f"На сьогодні кількість можливих скарг(40) вичерпано, скрипт переходить в режим перерви({ 0 if  43200-timeOverSec < 0 else int(43200-timeOverSec) } сек.) - очікування.\nЩоб уникнути зловжиння скаргами.")

                if timeOverSec >= 43200:
                    app.send_message("me","Перерва закінчилась, скрипт продовжує роботу.")
                    last_time_upd = datetime.now()
                    with open(report_path, 'w') as file:
                        file.write(str(last_time_upd) + "\n")
                        file.write(str(0))
                    current_reports = 0
                else:
                    return

            updTimeRep(1)

            peer: InputPeerChannel =  client.resolve_peer(url)
            response = client.send(data=ReportPeer(peer=peer, reason=InputReportReasonOther(), message="Propaganda of the war in Ukraine. Propaganda of the murder of Ukrainians and Ukrainian soldiers."))
            response = False
            app.send_message("me", f"Канал {url} отримав скаргу, {response}")

        except Exception as exc:   
            app.send_message("me", f"Схоже, що канал {url} не знайдено або ж він вже заблокований\nМожливо скрипт дав збій")

        finally:
            sleep(5)  # Спимо щоб не перегружати


app.connect()

app.send_message("me", "Скрипт вийшов на стабільну роботу, канали на які будуть надсилатись скарги беруться з - https://t.me/stoprussiachannel")
app.send_message("me", "Звіт з надісланими скаргами буде приходити в це й ж чат")

app.disconnect()

print("Готово")
print("Не закривайте це вікно, перейдіть в телеграм")

app.run()
