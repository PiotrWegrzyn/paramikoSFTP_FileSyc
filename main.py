import json
import sys
import paramiko
import getpass
from datetime import datetime
from dateutil.parser import parse
from FileSender import FileSender

def unix_time_seconds(dt):
    epoch = datetime.utcfromtimestamp(0)
    return (dt - epoch).total_seconds()

with open("config.json") as txtfile:
    fromJson = json.load(txtfile)

FileSender1 = FileSender(fromJson["mode"], fromJson["ignore"])
loopController = True
while(loopController):
    try:
        password = input("Please enter password:\n  ")
        FileSender1.connect(fromJson["username"],password,fromJson["server_address"],fromJson["port"])
        loopController = False
    except paramiko.SSHException:
        print("Error while authenticating.")
        loopController = True

if(fromJson["mode"] == "move_by_date"):
    loopController = True
    # date = '15-06-18 18:18'

    while (loopController):
        try:
            loopController = False
            date = input("Please enter a date (dd-mm-yy hh:mm):\n  ")
            dateObject = datetime.strptime(date, '%d-%m-%y  %H:%M')

        except ValueError:
            print("Date does not match format. Try again.")
            loopController = True

    timeSinceUnix = unix_time_seconds(dateObject)
    print(date + "time from UnixEra:" + str(timeSinceUnix));
    filesSent = FileSender1.moveFromServer(fromJson["local_folder"], fromJson["remote_folder"], timeSinceUnix)
    print("\n A list of files that have been moved:")
    for file in filesSent:
        print(file)

else:
    filesSent =  FileSender1.synchronize(fromJson["local_folder"],fromJson["remote_folder"])
    print("\n A list of files that have been sent:")
    for file in filesSent:
        print(file)

FileSender1.disonnect()
print("Done.")
