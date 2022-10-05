# ptpit-timetable tg bot controller
version='0.4 tg'
import subprocess
import time
import os
from datetime import timedelta 
from datetime import datetime
# # # # #
dateNow=str((datetime.now()+timedelta(hours=5)).strftime("%d.%m.%y %H:%M:%S"))
print(dateNow+" [BC] botController was started")

# check files
checkEnvFile=os.path.isfile('.env')
checkChatIDsFile=os.path.isfile('chatIDs.py')
checkAdminIDsFile=os.path.isfile('adminIDs.py')

if checkChatIDsFile == False:
    dateNow=str((datetime.now()+timedelta(hours=5)).strftime("%d.%m.%y %H:%M:%S"))
    print(dateNow+" [BC] start without chatIDs file, creating")
    # create chatIDs
    File=open("chatIDs.py", "a")
    File.write("chatIDs={ \n}")
    File.close()
    
if checkAdminIDsFile == False:
    dateNow=str((datetime.now()+timedelta(hours=5)).strftime("%d.%m.%y %H:%M:%S"))
    print(dateNow+" [BC] start without adminIDs file, creating")
    # input adminID
    adminID=input("[BC] Input your account ID: ")
    # create adminIDs
    File=open("adminIDs.py", "a")
    File.write("admins=[ \n'472153219', \n'"+adminID+"', \n]")
    File.close()
    print("[BC] You can change admims ID in adminIDs.py file\n")
    
if checkEnvFile == False:
    dateNow=str((datetime.now()+timedelta(hours=5)).strftime("%d.%m.%y %H:%M:%S"))
    print(dateNow+" [BC] start without .env file, creating")
    # input token
    token=input("[BC] Input your token: ")
    # create .env
    File=open(".env", "a")
    File.write("TOKEN=\""+token+"\"")
    File.close()
    print("[BC] You can change token in .env file\n")
    
# start bot
while True:
    os.system("python3 bot.py")
    dateNow=str((datetime.now()+timedelta(hours=5)).strftime("%d.%m.%y %H:%M:%S"))
    print(dateNow+" [BC] bot was closed, restart")
    
# # # # #
dateNow=str((datetime.now()+timedelta(hours=5)).strftime("%d.%m.%y %H:%M:%S"))
print(dateNow+" [BC] botController was closed")