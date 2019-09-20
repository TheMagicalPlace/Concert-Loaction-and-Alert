

import os
import time
import datetime

from Locator_GUI import *
from Notifier import Notifications

def activation_delay():
    '''This method is used to automatically update the upcoming concerts & is run on a delayed timer to
    run ~ 30 minutes after startup (or if the application is open for >24 hours, once every 24 hours'''
    with open('user_settings','r') as settings:
        last_checked = json.load(settings)['last_checked']
    if last_checked != datetime.date.today().isoformat() or testing:
        concert_finder = CFinder()
        concert_finder()
        noteupdate = Notifications()
        noteupdate.check_dates()
    else:
        print('Already Checked Today!')

if __name__ == '__main__':
    '''this is essentially the same as the script run in main.py, with the delaying the web scraper and/or
    GUI display based on user specifications. This should only ever be used in the context of auto launch
    on startup'''
    testing = False  # Should be False except for testing and debugging
    os.chdir(os.getcwd())

    print(sys.platform)

    try:
        with open('user_settings', 'r') as usr:
            data = json.load(usr)
            print(data['last_checked'])
        with open('schedule_settings', 'r') as schedule:
            sch = json.load(schedule)
            if sch['init_on_startup']:
                web_scraper_delay = int(sch['web_scraper_delay'])*60
                gui_launch_delay = int(sch['gui_launch_delay'])*60
            else:
                web_scraper_delay, gui_launch_delay = None, None
    except FileNotFoundError:
        startup_gui = Tk()
        FirstTimeStartup(startup_gui)
    except KeyError:
        startup_gui = Tk()
        FirstTimeStartup(startup_gui)
    else:
        notification_update = Notifications()
        notification_update.check_dates()
        if sch['init_on_startup']:
            concert_db_update = threading.Timer(web_scraper_delay if not None else 1, activation_delay)
            concert_db_update.start()
            time.sleep(gui_launch_delay)
            root = Tk()
            mainGUI = Main_GUI(root)
            mainGUI()
            root.mainloop()