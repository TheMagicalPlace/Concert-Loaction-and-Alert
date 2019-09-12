

import os
import json
from crontab import CronTab
import threading
import multiprocessing

from Locator_GUI import *

def activation_delay():
    '''This method is used to automatically update the upcoming concerts & is run on a delayed timer to
    run ~ 30 minutes after startup (or if the application is open for >24 hours, once every 24 hours'''
    with open('user_settings','r') as settings:
        last_checked = json.load(settings)['last_checked']
    if last_checked != datetime.date.today().isoformat():
        concert_finder = CFinder()
        concert_finder()
    else:
        print('Already Checked Today!')

def cron_conc_scraper():
    cron = CronTab(user='themagicalplace')
    job = cron.new(command='/home/themagicalplace/PycharmProjects/Python3.7Interp/bin/python /home/themagicalplace/PycharmProjects/ConcertLoactor/main.py')
    job.every_reboot()



input('test')
os.chdir('/home/themagicalplace/PycharmProjects/ConcertLoactor')
print('yeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeet')
try:
    with open('user_settings','r+') as usr:
        data = json.load(usr)
        print(data['last_checked'])
except FileNotFoundError:
    startup_gui = Tk()
    FirstTimeStartup(startup_gui)
    #startup_GUI = FirstTimeStartup(startup_gui)
except KeyError:
    startup_gui = Tk()
    FirstTimeStartup(startup_gui)
    #startup_GUI = FirstTimeStartup(startup_gui)
else:
    concert_db_update = threading.Timer(1, activation_delay)
    concert_db_update.start()
    startup_gui = Tk()
    FirstTimeStartup(startup_gui)
