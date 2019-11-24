

import os
import logging
import datetime
import json

from Locator_GUI import *
from Notifier import Notifications

def activation_delay():
    '''This method is used to automatically update the upcoming concerts & is run on a delayed timer to
    run ~ 30 minutes after startup (or if the application is open for >24 hours, once every 24 hours'''
    with open(os.path.join(os.getcwd(),'userdata','user_settings'),'r') as settings:
        last_checked = json.load(settings)['last_checked']
    if last_checked != datetime.date.today().isoformat():
        concert_finder = CFinder()
        concert_finder()
        noteupdate = Notifications()
        noteupdate.check_dates()
    else:
        print('Already Checked Today!')

def autostartup():
    print(os.getcwd())
    """on windows the bat file will always run, but if launch on startup is disabled the program
    shuts itself down almost immediately. This seemed a reasonable compromise between having it
     always run and having to change the bat file every time"""
    # really, this should never except unless
    # the user has deleted their files from the first time startup for some reason
    try:
        with open(os.path.join(os.getcwd(),'userdata','schedule_settings'), 'r') as usr:
            data = json.load(usr)
        with open(os.path.join(os.getcwd(),'userdata','schedule_settings'), 'r') as schedule:
            sch = json.load(schedule)
            if sch['init_on_startup']:
                web_scraper_delay = int(sch['web_scraper_delay'])
                gui_launch_delay = int(sch['gui_launch_delay'])
            else:
                web_scraper_delay, gui_launch_delay = None, None
    except FileNotFoundError:
        if sch['init_on_startup']:
            startup_gui = Tk()
            FirstTimeStartup(startup_gui)
    except KeyError:
        if sch['init_on_startup']:
            startup_gui = Tk()
            FirstTimeStartup(startup_gui)
    else:
        if sch['init_on_startup']:
            notification_update = Notifications()
            notification_update.check_dates()
            concert_db_update = threading.Timer(web_scraper_delay, activation_delay)
            concert_db_update.start()
            time.sleep(gui_launch_delay)
            root = Tk()
            mainGUI = Main_GUI(root)
            mainGUI()
            root.mainloop()

def user_startup():
    try:
        with open(os.path.join('userdata','schedule_settings'), 'r') as usr:
            data = json.load(usr)
    except FileNotFoundError:
        startup_gui = Tk()
        FirstTimeStartup(startup_gui)
    else:
        # updating conderts to display
        notification_update = Notifications()
        notification_update.check_dates()
        # launching gui
        root = Tk()
        mainGUI = Main_GUI(root)
        mainGUI()
        root.mainloop()

if __name__ =='__main__':

    if not os.path.exists(os.path.join(os.getcwd(),'userdata')):
        os.makedirs('userdata')
    print(os.path.join(os.getcwd(),'userdata','schedule_settings'))

    """if the program is started through the created bat file (on windows) or by a cron job (on unix systems) 
    the autostartup is run based on user settings, otherwise the program assumes that the user is starting
    the application manually"""

    try:
        os.environ['STARTUP']
    except KeyError:
        user_startup()
    else:
        autostartup()



