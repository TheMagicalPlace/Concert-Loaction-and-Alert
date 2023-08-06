import json
from os import getcwd
import os.path
import sys
from os import getcwd

from crontab import CronTab


def initialize_scheduler():
    user_os = sys.platform
    if user_os in ['linux','darwin']:
        return SchedulerLinux()
    elif user_os == 'win32':
        return SchedulerWindows()
    else:
        return 'Unsupported Operating System'

class SchedulerGeneric:
    def __init__(self):
        try:
            self.update()
        except FileNotFoundError:
            self.init_on_startup = True
            self.web_scraper_delay = 1800
            self.gui_launch_delay = 3600
            self.user = None
        self.write_settings()

    def update(self):
        """updates the instance variables for use in the GUI"""
        with open(os.path.join('userdata','schedule_settings'), 'r') as schedule:
            data = json.load(schedule)
            for key, value in data.items():
                if key == 'user':
                    self.user = value
                else:
                    exec(f'self.{key} = {str(value)}')

    def write_settings(self):
        with open(os.path.join('userdata','schedule_settings'), 'w') as schedule:
            sch = {'user':self.user,
                   'init_on_startup': self.init_on_startup,
                   'web_scraper_delay': self.web_scraper_delay,
                   'gui_launch_delay': self.gui_launch_delay}
            json.dump(sch, schedule)

    def enabledisable(self,enabled):
        """enables/disables startup launch"""
        if enabled:
            self.init_on_startup = True
        else:
            self.init_on_startup = False
            self.web_scraper_delay = None
            self.gui_launch_delay = None
        self.write_settings()

    def activation_delay(self,web_scraper_delay=1800//60,gui_launch_delay=3600//60):
        self.web_scraper_delay = web_scraper_delay*60
        self.gui_launch_delay = gui_launch_delay*60
        self.write_settings()

class SchedulerLinux(SchedulerGeneric):
    system = 'linux/mac'

    def enabledisable(self,enabled):
        super().enabledisable(enabled)
        if not enabled and self.user is not None:
            cron = CronTab(user=self.user)
            cron.remove_all(comment='concert_location_and_alert')
            cron.write()


    def cron_setup(self,user):
        """sets up or modifies a cron job"""
        self.user = user
        cron = CronTab(user=user)
        for job in cron:
            if job.comment == 'concert_location_and_alert':
                # the original cron is deleted in case the user moved the application files somewhere else and launched
                # the program manually
                cron.remove_all(comment='concert_location_and_alert')
        else:
            startup = cron.new(f'sleep 30 && export DISPLAY=:0 && cd {os.getcwd()} && {sys.executable} {os.path.join(getcwd(),"main.py")} >> a.txt',comment='concert_location_and_alert')
            startup.every_reboot()
            startup.env['STARTUP'] = 'yes'
            cron.write()
        self.write_settings()

class SchedulerWindows(SchedulerGeneric):
    def __init__(self):
        super().__init__()
        self.path_to_interp ='"'+sys.executable+'"'
        self.current_directory = '"'+getcwd()+'\main.py'+'"'

    def create_startup_file(self):
        with open('userdata\\concert_tracker_startup.bat','w') as startup:
            startup.write('echo off\nsetlocal\nset STARTUP=yes\nstart ')
            startup.write(self.path_to_interp)
            startup.write('\nendlocal')
        startup_file = getcwd()+'\\userdata\\concert_tracker_startup.bat'
        return startup_file

    def enabledisable(self,enabled):
        if enabled:
            self.init_on_startup = True
        else:
            self.init_on_startup = False
            self.web_scraper_delay = None
            self.gui_launch_delay = None



if __name__ == '__main__':
    sch = SchedulerWindows()
    sch.create_startup_file()