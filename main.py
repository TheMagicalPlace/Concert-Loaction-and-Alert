

import os
import logging
from Locator_GUI import *
from Notifier import Notifications




if __name__ =='__main__':
    """Checks if there is a user_settings file, and if not launches the first time startup"""
    os.chdir(os.getcwd())
    logging.log(sys.platform)
    try:
        with open('user_settings','r') as usr:
            data = json.load(usr)
            logging.log(data['last_checked'])
    except FileNotFoundError:
        startup_gui = Tk()
        FirstTimeStartup(startup_gui)
    else:
        notification_update = Notifications()
        notification_update.check_dates()
        root = Tk()
        mainGUI = Main_GUI(root)
        mainGUI()
        root.mainloop()
