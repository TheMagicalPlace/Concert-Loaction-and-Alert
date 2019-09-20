import sys
from crontab import CronTab
import json
from os import getcwd
from collections import abc


def initialize_scheduler():
    user_os = sys.platform
    if user_os in ['linux','darwin']:
        return SchedulerLinux()
    elif user_os is 'win32':
        return SchedulerWindows()
    else:
        return 'Unsupported Operating System'

class SchedulerGeneric:
    def __init__(self):
        try:
            self.update()
        except FileNotFoundError:
            self.init_on_startup = True
            self.web_scraper_delay = 1800//60
            self.gui_launch_delay = 3600//60
            self.user = None
        self.write_settings()

    def update(self):
        """updates the instance variables for use in the GUI"""
        with open('schedule_settings', 'r') as schedule:
            data = json.load(schedule)
            for key, value in data.items():
                if key == 'user':
                    self.user = value
                else:
                    exec(f'self.{key} = {str(value)}')

    def write_settings(self):
        with open('schedule_settings', 'w') as schedule:
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
        self.web_scraper_delay = web_scraper_delay
        self.gui_launch_delay = gui_launch_delay
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
                break
        else:
            startup = cron.new(f'export DISPLAY=:0 && python3 {getcwd()}/startup_file.py',comment='concert_location_and_alert')
            startup.every_reboot()
            startup.env['IS_RUN_BY_CRON'] = True
            cron.write()
        self.write_settings()



class SchedulerWindows(SchedulerGeneric):
    def __init__(self):
        super().__init__()
        self.path_to_interp =sys.executable+'/python.exe'
        self.current_directory = getcwd()+'/startup_file.py'

    def create_startup_file(self):
        print('\n',self.path_to_interp,'\n',self.current_directory)
        with open('Startup_Init.bat','w') as startup:
            startup.write(self.path_to_interp+' ')
            startup.write(self.current_directory)
            startup.write('\npause')
        startup_file = getcwd()+'/Startup_Init.bat'
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