# ptpit-timetable vk ubot controller v.0.1
import subprocess
import time
import os
from datetime import timedelta 
from datetime import datetime
restarttry=0
# # # # #
dateNow=str((datetime.now()+timedelta(hours=5)).strftime("%d-%m-%y %H:%M:%S"))
logFile=open("botLog.log", "a")
logFile.write("\n["+dateNow+"] [BC] botController was started")
logFile.close()
dateLastRes=datetime.now()+timedelta(hours=5)
# проверка файлов
checkEnvFile=os.path.isfile('.env')
checkChatIDsFile=os.path.isfile('chatIDs.py')
checkAdminIDsFile=os.path.isfile('adminIDs.py')

if checkChatIDsFile == False:
    # log
    dateNow=str((datetime.now()+timedelta(hours=5)).strftime("%d-%m-%y %H:%M:%S"))
    logFile=open("botLog.log", "a")
    logFile.write("\n["+dateNow+"] [BC] start without chatIDs file, creating")
    logFile.close()
    # create chatIDs
    logFile=open("chatIDs.py", "a")
    logFile.write("chatIDs={ \n}")
    logFile.close()
    
if checkAdminIDsFile == False:
    # log
    dateNow=str((datetime.now()+timedelta(hours=5)).strftime("%d-%m-%y %H:%M:%S"))
    logFile=open("botLog.log", "a")
    logFile.write("\n["+dateNow+"] [BC] start without adminIDs file, creating")
    logFile.close()
    # create adminIDs
    logFile=open("adminIDs.py", "a")
    logFile.write("admins=[ \n'472153219', \n]")
    logFile.close()
    
if checkEnvFile == False:
    # log
    dateNow=str((datetime.now()+timedelta(hours=5)).strftime("%d-%m-%y %H:%M:%S"))
    logFile=open("botLog.log", "a")
    logFile.write("\n["+dateNow+"] [BC] start without .env file, creating")
    logFile.close()
    # create .env
    logFile=open(".env", "a")
    logFile.write("TOKEN=\"\"")
    logFile.close()
    # exit
    print('paste token into .env file and restart botController')
    restarttry=101
    
# start bot
while 1>0:
    if restarttry > 100:
        break
    os.system("python3 bot.py")
    print("[BC] bot was closed")
    dateNow=str((datetime.now()+timedelta(hours=5)).strftime("%d-%m-%y %H:%M:%S"))
    logFile=open("botLog.log", "a")
    logFile.write("\n["+dateNow+"] [BC] bot was closed")
    logFile.close()
    time.sleep(restarttry)
    restarttry+=1
    dateNow=str((datetime.now()+timedelta(hours=5)).strftime("%d-%m-%y %H:%M:%S"))
    logFile=open("botLog.log", "a")
    logFile.write("\n["+dateNow+"] [BC] trying restart bot "+str(restarttry))
    logFile.close()
    print("[BC] trying restart bot")
    
# # # # #
dateNow=str((datetime.now()+timedelta(hours=5)).strftime("%d-%m-%y %H:%M:%S"))
logFile=open("botLog.log", "a")
logFile.write("\n["+dateNow+"] [BC] botController was closed")
logFile.close()