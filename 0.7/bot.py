# ptpit-timetable tg bot 
version="0.7 tg"
import os
import requests
import subprocess
import sqlite3
import json
from datetime import datetime, timezone
from datetime import timedelta as td
from dotenv import load_dotenv
from chatIDs import chatIDs
from adminIDs import admins
load_dotenv(".env")

times = {# расписание звонков
        1: "1⃣ 08:30-10:05",
        2: "2⃣ 10:25-12:00",
        3: "3⃣ 12:20-14:10",
        4: "4⃣ 14:15-15:50",
        5: "5⃣ 16:10-17:55",
        6: "6⃣ 18:00-19:35",
        7: "7️⃣ ",
        8: "[8] ",
}
weekDays={# дни недели 
        0:'понедельник',
        1:'вторник',
        2:'среду',
        3:'четверг',
        4:'пятницу',
        5:'субботу',
        6:'воскресенье',
}

# # tg # #
from telegram.ext import MessageHandler, Filters, InlineQueryHandler, Updater
from telegram import InlineQueryResultArticle, InputTextMessageContent, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

updater = Updater(os.environ.get("TOKEN"))
dispatcher = updater.dispatcher

# inline # 
def inline_caps(update, context):
    query = update.inline_query.query.lower()
    if not query:
        return
    print(getDateTime("text")+" inline")
    results = list()
    # inline variants #
    if not any(map(str.isdigit, query)): #если запрос без цифр
        teachers = requests.get("https://api.ptpit.ru/persons/teachers")
        teachers = teachers.json()
        teachers_format = {}
        for teacher in teachers:
            id = teacher.get("id")
            name = teacher.get("name").lower()[:-5]
            teachers_format.update({name: id})
        if not query in teachers_format:
                results.append(InlineQueryResultArticle(
                id="notfoundteacher",
                title='Преподаватель '+query+' не найден',
                input_message_content=InputTextMessageContent('Преподаватель '+query+' не найден'),
                thumb_url="https://raw.githubusercontent.com/kompot69/ptpit_timetable_bot/main/no.png"
                ))
        else: 
            results.append(InlineQueryResultArticle(
            id=query,
            title='Расписание на сегодня',
            description="для преподавателя "+query,
            input_message_content=InputTextMessageContent(getTimetableTeacher(getDateTime(0), query)),
            thumb_url="https://raw.githubusercontent.com/kompot69/ptpit_timetable_bot/main/list.png"
            ))
            if getDateTime(0).weekday() == 6: # сб
                results.append(InlineQueryResultArticle(
                id=query+"2",
                title='Расписание на понедельник',
                description="для преподавателя "+query,
                input_message_content=InputTextMessageContent(getTimetableTeacher(getDateTime(0)+td(days=2), query)),
                thumb_url="https://raw.githubusercontent.com/kompot69/ptpit_timetable_bot/main/list.png"
                ))
            else:
                results.append(InlineQueryResultArticle(
                id=query+"1",
                title='Расписание на завтра',
                description="для преподавателя "+query,
                input_message_content=InputTextMessageContent(getTimetableTeacher(getDateTime(0)+td(days=1), query)),
                thumb_url="https://raw.githubusercontent.com/kompot69/ptpit_timetable_bot/main/list.png"
                ))
    else: #если запрос с цифрами
        groups = requests.get("https://api.ptpit.ru/groups")
        groups = groups.json()
        groups_format = {}
        for group in groups:
            id = group.get("id")
            name = group.get("name").lower()
            groups_format.update({name: id})
        if not query in groups_format:
            results.append(InlineQueryResultArticle(
                id="notfoundgroup",
                title='Группа '+query+' не найдена',
                input_message_content=InputTextMessageContent('Группа '+query+' не найдена'),
                thumb_url="https://raw.githubusercontent.com/kompot69/ptpit_timetable_bot/main/no.png"
            ))
        else:
            results.append(InlineQueryResultArticle(
                id=query,
                title='Расписание на сегодня',
                description="для группы "+query,
                input_message_content=InputTextMessageContent(getTimetable(getDateTime(0), query, True)),
                thumb_url="https://raw.githubusercontent.com/kompot69/ptpit_timetable_bot/main/list.png"
            ))
            if getDateTime(0).weekday() == 6: # сб
                results.append(InlineQueryResultArticle(
                    id=query+"2",
                    title='Расписание на понедельник',
                    description="для группы "+query,
                    input_message_content=InputTextMessageContent(getTimetable(getDateTime(0)+td(days=2), query, True)),
                    thumb_url="https://raw.githubusercontent.com/kompot69/ptpit_timetable_bot/main/list.png"
                ))
            else:
                results.append(InlineQueryResultArticle(
                    id=query+"1",
                    title='Расписание на завтра',
                    description="для группы "+query,
                    input_message_content=InputTextMessageContent(getTimetable(getDateTime(0)+td(days=1), query, True)),
                    thumb_url="https://raw.githubusercontent.com/kompot69/ptpit_timetable_bot/main/list.png"
                ))

    # end inline variants #
    context.bot.answer_inline_query(update.inline_query.id, results)
inline_caps_handler = InlineQueryHandler(inline_caps)
dispatcher.add_handler(inline_caps_handler)
# end inline #

def echo(update, context):
    pattern = update.message.text.lower()
    chatid = str(update.effective_chat.id)
    fromid = str(update.effective_chat.id)
    # # end tg # #

    lasttimes=" "
    # установка группы
    if pattern.startswith("бот группа "):
        activityTyping(chatid)
        print(getDateTime("text")+" [bot] group registration...")
        gr0up=pattern[11:]
        # проверка сайта
        site_status = checkSiteStatus("https://ptpit.ru")
        if site_status != "200 OK":
            return sendMessage(chatid, "⚠ ptpit.ru: "+site_status, context)
        # поиск группы
        groups = requests.get("https://api.ptpit.ru/groups")
        groups = groups.json()
        groups_format = {}
        for group in groups:
            id = group.get("id")
            name = group.get("name").lower()
            groups_format.update({name: id})
        text = "✖ Группа "+gr0up+" не найдена.\nПример правильного запроса: Бот группа 18сзи1п"
        if not gr0up in groups_format:
            gr0up=gr0up+"п"
            if not gr0up in groups_format:
                return sendMessage(chatid, text, context)
        # добавление группы
        add_user(chatid, gr0up)
        print(getDateTime("text")+" [bot] group registered successfully, exit")
        text="☑ Установлена группа "+gr0up
        if fromid in admins:
            text+=" для чата "+chatid
        sendMessage(chatid, text, context)
        os._exit(0)
        
    # выбор группы
    #set_user(chatid)
    #if set_user:
    gr0up = set_user(chatid)[0]
    print(f"(test) set group {gr0up}")
    if gr0up == None:
        text="Ваш ID не найден в боте. Установите группу:\nБот группа <имя группы>"
        return sendMessage(chatid, text, context)
    """
    gr0up=int(chatid)
    if gr0up in chatIDs:
        gr0up=str(chatIDs[gr0up])
    else:
        print(getDateTime("text")+" [bot] message from NF id")
        if "бот" in pattern:
            text="Ваш ID не найден в боте. Установите группу:\nБот группа <имя группы>"
            return sendMessage(chatid, text, context)
        else:
            return
    """
    
# # # # # # # # # #

    
    if "бот помощь" in pattern or ("/start" in pattern or "/help" in pattern):
        activityTyping(chatid)
        print(getDateTime("text")+" [bot] help requested")
        text='[ Доступные команды: ]\n• Расписание/пары сегодня/завтра/послезавтра\n• Пара/пары сейчас/следующие\n• Расписание/пары на <день недели>\n• Расписание на <дд.мм.гг>\n• Расписание звонков\n\n• Бот помощь\n• Бот статус\n• Бот группа <группа>\n'
        if fromid in admins:
            text+='• Бот рестарт\n• Добавить админа <id>\n'
        text+='\n • Чтобы воспользоваться inline режимом напишите @ptpit_timetable_bot и группу/фамилию'
        return sendMessage(chatid, text, context)
        
        
# # # # #


    if "пар" in pattern  and ("сейчас" in pattern or "следующ" in pattern):
        activityTyping(chatid)
        print(getDateTime("text")+" [bot] current timetable requested")
        # настройка даты
        dateneed=getDateTime(0)
        datestrf = dateneed.strftime("%Y-%m-%d")
        # проверка сайта
        site_main_code = subprocess.check_output('curl -is https://ptpit.ru | head -n 1', shell=True).decode("UTF-8")
        site_main_code=site_main_code[:-2]
        if site_main_code != "HTTP/1.1 200 OK":
            return sendMessage(chatid, "⚠ ptpit.ru: "+site_main_code, context)
        # поиск
        groups = requests.get("https://api.ptpit.ru/groups")
        groups = groups.json()
        groups_format = {}
        for group in groups:
            id = group.get("id")
            name = group.get("name").lower()
            groups_format.update({name: id})
        while True:
            group = gr0up
            if group in groups_format:
                break
        dates = requests.get("https://api.ptpit.ru/timetable/weeks?visible=1")
        dates = dates.json()
        # поиск даты для запроса
        dates2 = dates[0]["start_week"]
        datecounter=0
        while dates2 > datestrf:
            datecounter+=1
            dates2 = dates[datecounter]["start_week"]
            if datecounter>10:
                break
        # запрос расписания
        timetable = requests.get(f"https://api.ptpit.ru/timetable/groups/" + str(groups_format[group]) + "/" + dates2)
        timetable = timetable.json()
        text = ""
        # получение текущих пар
        for r in timetable:
            if r['date'] == datestrf:
                timeend=str(times[r['num']])[-5:]
                timenow=getDateTime(0).strftime("%H:%M")
                if timeend > timenow:
                    subgroup=str(r['subgroup'])
                    room=r['room_name']
                    if subgroup == "0":
                        subgroup=" "
                    else:
                        subgroup="("+subgroup+"П)"
                    if lasttimes == " " :
                        lasttimes=r['num']
                    if lasttimes!=r['num']:
                        text+= "\n"
                    text += f"{times[r['num']]} {subgroup}\n"
                    text += f"{r['subject_name']}\n"
                    if r['room_name'] != None:
                        if r['room_name'] == "ДО":
                            if (r['moodle']) != None:
                                moodle=json.loads(r['moodle'])[0]
                                room=requests.get("https://chilp.it/api.php?url="+moodle["url"]).text[7:-1]
                                if len(room)>30:
                                    room=" ссылка (api error)"
                            else:
                                room="ДО| без ссылки "
                            text += "["+room+"]"
                        else:
                            text += "[к."+room+"]"
                    if r['teacher_surname'] != None:
                        text += f" {r['teacher_surname']} {r['teacher_name'][0]}. {r['teacher_secondname'][0]}.\n"
                    if lasttimes!=r['num'] and "пара" in pattern:
                        break
                    
        # вывод
        if "пара" in pattern:
            title="Текущая пара:\n\n"
        else:
            title="Текущие пары:\n\n"
        if text != "":
            return sendMessage(chatid, title+text+checkNotice(datestrf), context)
        else:
            return sendMessage(chatid, f"Пар на сегодня не найдено."+checkNotice(datestrf), context)


# # # # #


    if "расписание звонков" in pattern:
        activityTyping(chatid)
        print(getDateTime("text")+" [bot] call timetable requested")
        text="Расписание звонков:\n"+times[1]+"\n"+times[2]+"\n"+times[3]+"\n"+times[4]+"\n"+times[5]+"\n"+times[6]
        return sendMessage(chatid, text, context)


# # # # #


    if "расписани" in pattern or "пары" in pattern:
        if "сегодня" in pattern and "завтра" in pattern:
             return
        activityTyping(chatid)
        # настрока даты
        if "сегодня" in pattern:
            dateneed=getDateTime(0)
        elif "послезавтра" in pattern:
            dateneed=getDateTime(0) +td(days=2)
            if dateneed.weekday() == 6: # вс>>>пн
                dateneed=dateneed+td(days=1)
        elif "завтра" in pattern:
            dateneed=getDateTime(0)+td(days=1)
            if dateneed.weekday() == 6: # вс>>>пн
                dateneed=dateneed+td(days=1)
        elif "вчера" in pattern:
            dateneed=getDateTime(0)-td(days=1)
            if dateneed.weekday() == 6: # вс>>>пн
                dateneed=dateneed-td(days=1)
        # дни недели
        elif "понедельни" in pattern: 
            dateneed=getDateTime(0)
            while dateneed.weekday() != 0: # >пн
                print(dateneed.weekday())
                dateneed=dateneed+td(days=1)
        elif "вторни" in pattern: 
            dateneed=getDateTime(0)
            while dateneed.weekday() != 1: # >вт
                dateneed=dateneed+td(days=1)
        elif "сред" in pattern: 
            dateneed=getDateTime(0)
            while dateneed.weekday() != 2: # >ср
                dateneed=dateneed+td(days=1)
        elif "четвер" in pattern: 
            dateneed=getDateTime(0)
            while dateneed.weekday() != 3: # >чт
                dateneed=dateneed+td(days=1)
        elif "пятн" in pattern: 
            dateneed=getDateTime(0)
            while dateneed.weekday() != 4: # >пт
                dateneed=dateneed+td(days=1)
        elif "суббот" in pattern: 
            dateneed=getDateTime(0)
            while dateneed.weekday() != 5: # >сб
                dateneed=dateneed+td(days=1)
        elif "воскрес" in pattern: 
            dateneed=getDateTime(0)
            while dateneed.weekday() != 6: # >вс
                dateneed=dateneed+td(days=1)
        
        elif pattern.startswith("расписание на "): # дата
            dateneed=pattern[14:]
            dateneed=datetime.strptime(dateneed,"%d.%m.%y")
        else: 
            return 
        return sendMessage(chatid, getTimetable(dateneed, gr0up, False), context)


# # # # #


    if pattern.startswith("добавить админа "):
        activityTyping(chatid)
        admID=pattern[16:]
        # проверка на админа
        if not fromid in admins:
            return sendMessage(chatid, "✖ Только для админов", context)
        if int(admID) < 1000000:
            return sendMessage(chatid, "✖ Проверьте правильность ID", context)
        # запись
        IDsFile=open("adminIDs.py", "r+")
        IDs=IDsFile.read()[:-1]
        IDs=IDs+"\'"+admID+"\',\n]"
        IDsFile.close()
        IDsFile=open("adminIDs.py", "w")
        IDsFile.write(IDs)
        IDsFile.close()
        print(getDateTime("text")+" [bot] new admin "+admID+" added by "+fromid)
        return sendMessage(chatid, "☑ "+admID+" добавлен в админы", context)


# # # # #

    if "статус" in pattern and "бот" in pattern:
        activityTyping(chatid)
        print(getDateTime("text")+" [bot] status requested")
        text=" "
        # проверка сайтов - главный
        site_status = checkSiteStatus("https://ptpit.ru")
        if site_status == "200 OK":
            text+="\n🆗 ptpit.ru: "+site_status
        else:
            text+="\n⚠ ptpit.ru: "+site_status
        # проверка сайтов - API
        site_status = checkSiteStatus("https://api.ptpit.ru")
        if site_status == "401 Unauthorized":
            text+="\n🆗 api.ptpit.ru: "+site_status
        else:
            text+="\n⚠ api.ptpit.ru: "+site_status
        # проверка сайтов - мудл
        site_status = checkSiteStatus("https://moodle.ptpit.ru")
        if site_status == "200 OK":
            text+="\n🆗 moodle.ptpit.ru: "+site_status
        else:
            text+="\n⚠ moodle.ptpit.ru: "+site_status
        # проверка сайтов - расписание
        site_status = checkSiteStatus("https://timetable.ptpit.ru")
        if site_status == "200 OK":
            text+="\n🆗 timetable.ptpit.ru: "+site_status
        else:
            text+="\n⚠ timetable.ptpit.ru: "+site_status
        if fromid in admins:
            # дата
            text+="\n🕰 "+getDateTime("text")
            # версия бота
            text+="\n⚙ v."+version
            # кол-во админов
            text+=" | 👮‍♀ "+str(len(admins))
        # разделитель
        text+="\n"+"    —    "*4
        # чат
        text+="\n👥 "+gr0up+" | 🆔 "+str(chatid)
        # вывод
        return sendMessage(chatid, text, context)

    
# # # # #
    
    
    if "рестарт" in pattern and "бот" in pattern:
        activityTyping(chatid)
        if fromid in admins:
            sendMessage(chatid, '☑ Выход...', context)
            print(getDateTime("text")+" [bot] restart by "+fromid)
            os._exit(0)
        else:
            return sendMessage(chatid, '✖ Только для админов', context)


# # # # # # # # # # #

print("[bot] bot started")

def getTimetable(dateneed, gr0up, inline):
    if 1==1:
        print(getDateTime("text")+" [bot] timetable requested")
        datestrf = dateneed.strftime("%Y-%m-%d")
        # проверка сайта
        site_status = checkSiteStatus("https://ptpit.ru")
        if site_status != "200 OK":
            #return sendMessage(chatid, "⚠ ptpit.ru: "+site_status, context)
            return "⚠ ptpit.ru: "+site_status
        # очиска буферов
        buffer=''
        lastbuffer=''
        # запрос данных
        groups = requests.get("https://api.ptpit.ru/groups")
        groups = groups.json()
        groups_format = {}
        for group in groups:
            id = group.get("id")
            name = group.get("name").lower()
            groups_format.update({name: id})
        group = gr0up
        dates = requests.get("https://api.ptpit.ru/timetable/weeks?visible=1")
        dates = dates.json()
        text = ""
        # поиск даты в свитче
        dates2 = dates[0]["start_week"]
        datecounter=0
        while dates2 > datestrf:
            datecounter+=1
            dates2 = dates[datecounter]["start_week"]
            if datecounter>10:
                break 
        # запрос расписания  
        timetable = requests.get(f"https://api.ptpit.ru/timetable/groups/" + str(groups_format[group]) + "/" + dates2)
        timetable = timetable.json()
        lasttimes=" "
        for r in timetable:
            if r['date'] == datestrf:
                room=r['room_name']
                subgroup=str(r['subgroup'])
                if lasttimes!=times[r['num']]:
                    buffer+= "\n"
                lasttimes=times[r['num']]
                if subgroup == "0":
                    subgroup=" "             
                else:
                    subgroup="("+subgroup+"П)"
                    
                buffer+= f"{times[r['num']]} "
                buffer+= f"{subgroup}\n"

                if r['note'] != None and r['note']!="":
                    buffer+= f"({r['note']})\n"

                buffer+= f"{r['subject_name']}\n"
                if r['room_name'] != None:
                    if r['room_name'] == "ДО":
                        if (r['moodle']) != None:
                            moodleList=json.loads(r['moodle'])
                            for l in moodleList:
                                room=cutLink(l["url"])
                                if l["type"]=='meeting':
                                    room="🗣 "+room
                                else:
                                    room="🔗 "+room
                                buffer += "["+room+"]"
                        else:
                            room="ДО (без ссылки)"
                            buffer += "["+room+"]"
                    else:
                        buffer += "["
                        if not room[:2].isalpha():
                            buffer += "к."
                        #спортзал fix
                        if room[:10]=="спорт. зал": room=room[:-1]
                        buffer += room+"]"
                if r['teacher_surname'] != None:
                    buffer+= f" {r['teacher_surname']} {r['teacher_name'][0]}. {r['teacher_secondname'][0]}.\n"
                if buffer[:16]+buffer[17:] == lastbuffer[1:17]+lastbuffer[18:] :
                    buffer=buffer[:15]+buffer[19:]
                    lastbuffer="\n"

                text += lastbuffer
                lastbuffer = buffer
                buffer=''
        text += lastbuffer
        # вывод
        dateneed=str(weekDays[dateneed.weekday()])+dateneed.strftime(", %d.%m.%y")
        if int(getDateTime(0).strftime("%H")) < 2:
            dateneed=dateneed.upper()
        if text != "":
            if inline:
                return "Расписание на "+dateneed+"\nдля группы "+group+"\n"+text+checkNotice(datestrf)
            return "Расписание на "+dateneed+"\n"+text+checkNotice(datestrf)
        else:
            if inline:
                return "Расписание на "+dateneed+"\n для группы "+group+" не найдено."+checkNotice(datestrf)
            return "Расписание на "+dateneed+" не найдено."+checkNotice(datestrf)

def getTimetableTeacher(dateneed, query):
    if 1==1:
        print(getDateTime("text")+" [bot] teacher timetable requested")
        datestrf = dateneed.strftime("%Y-%m-%d")
        # проверка сайта
        site_status = checkSiteStatus("https://ptpit.ru")
        if site_status != "200 OK":
            #return sendMessage(chatid, "⚠ ptpit.ru: "+site_status, context)
            return "⚠ ptpit.ru: "+site_status
        # очиска буферов
        buffer=''
        lastbuffer=''
        # запрос данных
        teachers = requests.get("https://api.ptpit.ru/persons/teachers")
        teachers = teachers.json()
        teachers_format = {}
        for teacher in teachers:
            id = teacher.get("id")
            name = teacher.get("name").lower()[:-5]
            teachers_format.update({name: id})
        teacher = query.lower()
        dates = requests.get("https://api.ptpit.ru/timetable/weeks?visible=1")
        dates = dates.json()
        text = ""
        # поиск даты в свитче
        dates2 = dates[0]["start_week"]
        datecounter=0
        while dates2 > datestrf:
            datecounter+=1
            dates2 = dates[datecounter]["start_week"]
            if datecounter>10:
                break 
        # запрос расписания  
        timetable = requests.get(f"https://api.ptpit.ru/timetable/teachers/" + str(teachers_format[teacher]) + "/" + dates2)
        timetable = timetable.json()
        lasttimes=" "
        for r in timetable:
            if r['date'] == datestrf:
                room=r['room_name']
                subgroup=str(r['subgroup'])
                if lasttimes!=times[r['num']]:
                    buffer+= "\n"
                lasttimes=times[r['num']]
                    
                buffer+= f"{times[r['num']]} \n"

                if r['note'] != None and r['note']!="":
                    buffer+= f"({r['note']})\n"

                buffer+= f"{r['subject_name']}\n"
                if r['room_name'] != None:
                    if r['room_name'] == "ДО":
                        if (r['moodle']) != None:
                            moodleList=json.loads(r['moodle'])
                            for l in moodleList:
                                room=cutLink(l["url"])
                                if l["type"]=='meeting':
                                    room="🗣 "+room
                                else:
                                    room="🔗 "+room
                                buffer += "["+room+"]\n"
                        else:
                            room="ДО (без ссылки)"
                            buffer += "["+room+"]"
                    else:
                        buffer += "["
                        if not room[:2].isalpha():
                            buffer += "к."
                        #спортзал fix
                        if room[:10]=="спорт. зал": room=room[:-1]
                        buffer += room+"]"
                buffer +=f" {r['group_name']}"
                if subgroup == "0":
                    subgroup="\n"             
                else:
                    subgroup="("+subgroup+"П)\n"
                buffer+= f"{subgroup}"
                if buffer[:-4]+buffer[-3:]== lastbuffer[1:-4]+lastbuffer[-3:] :
                    buffer=buffer[:-5]+"\n"
                    lastbuffer="\n"

                text += lastbuffer
                lastbuffer = buffer
                buffer=''
        text += lastbuffer
        # вывод
        dateneed=str(weekDays[dateneed.weekday()])+dateneed.strftime(", %d.%m.%y")
        if int(getDateTime(0).strftime("%H")) < 2:
            dateneed=dateneed.upper()
        surname=r['teacher_surname']
        if surname[-1:]=="а":
            surname=surname[:-1]+"ой"
        else:
            surname+="а"
        if text != "":
            return "Расписание на "+dateneed+"\nдля "+surname+f" {r['teacher_name'][0]}. {r['teacher_secondname'][0]}.\n"+text+checkNotice(datestrf)
        else:
            return "Расписание на "+dateneed+"\nдля "+surname+f" {r['teacher_name'][0]}. {r['teacher_secondname'][0]}. не найдено"+checkNotice(datestrf)

def add_user(chatid, gr0up): #add_user(chatid, gr0up)
    conn = sqlite3.connect('users.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO users (chatid, gr0up) VALUES (?, ?)''', (chatid, gr0up))
    conn.commit()
    conn.close()

def set_user(chatid):
    conn = sqlite3.connect('users.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT gr0up FROM users WHERE chatid=?", (chatid,))
    user_data = cursor.fetchone()
    conn.close()
    return user_data

def checkSiteStatus(url):
    siteStatus=subprocess.check_output('curl -is '+url+' | head -n 1', shell=True).decode("UTF-8")
    return siteStatus[9:-2]

def cutLink(url):
    alphabet=set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
    if not alphabet.isdisjoint(url.lower()):# zoom fix
        url=url.partition('http')[1]+url.partition('http')[2]
        url=url.partition(' ')[0]
    url=requests.get("https://chilp.it/api.php?url="+url).text[:-1]
    if len(url) > 50:
        return "ссылка (api error)"
    return url[7:]

def checkNotice(date):
    if '<p class="text-center">' in requests.get("https://timetable.ptpit.ru").text :
        return "\nНа сайте есть предупреждение!"
    if '<strong class="text-danger">' in requests.get("https://timetable.ptpit.ru/assets/timetable.js").text and date in requests.get("https://timetable.ptpit.ru/assets/timetable.js").text:
        return "\nПары укороченные!"
    else:
        return ""

def getDateTime(text):
    
    date=datetime.now(tz=timezone(offset=td(hours=5)))
    if text=="text":
        return str(date.strftime("%d.%m.%y %H:%M:%S"))
    elif text=="date4SearchTimes":
        print(str(date.strftime("%Y-%M-%d")))
        return str(date.strftime("%Y-%M-%d"))
    else:
        return date
     

# # tg # # 

echo_handler = MessageHandler(Filters.text, echo)
dispatcher.add_handler(echo_handler) 
    
def sendMessage(chatid, text, context):
    if int(chatid) < 0:
        keyboard=None
        if "е!" in text:
            keyboard=InlineKeyboardMarkup([[InlineKeyboardButton(text='Открыть сайт', url='https://timetable.ptpit.ru')]])
        return context.bot.send_message(chat_id=chatid, text=text, reply_markup=keyboard, disable_web_page_preview=True) 
    else:
        keyboard=ReplyKeyboardMarkup([['Пары сегодня','Пары завтра'],['Бот помощь']], resize_keyboard=True)
        if "е!" in text:
            keyboard=InlineKeyboardMarkup([[InlineKeyboardButton(text='Открыть сайт', url='https://timetable.ptpit.ru')]])
        #message=context.bot.send_message(chat_id=chatid, text=text )#, reply_markup=keyboard, disable_web_page_preview=True) 
        #return context.bot.editMessageText(chat_id = chatid, message_id = message.message_id, text = text+'[E]', reply_markup=keyboard)
        return context.bot.send_message(chat_id=chatid, text=text, reply_markup=keyboard, disable_web_page_preview=True) 

def activityTyping(chatid):
    return 

#bot.infinity_polling()
updater.start_polling()
# # end tg # #

