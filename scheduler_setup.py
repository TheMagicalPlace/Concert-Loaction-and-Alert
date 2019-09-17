import sys
from crontab import CronTab
import json
from os import getcwd

def initialize_scheduler():
    user_os = sys.platform
    if user_os in ['linux','darwin']:
        return SchedulerLinux()
    elif user_os is 'win32':
        pass
    else:
        return 'Unsupported Operating System'


class SchedulerLinux:
    system = 'linux/mac'

    def __init__(self):
        try:
            with open('schedule_settings','r') as schedule:
                data = json.load(schedule)
                for key,value in data.items():
                    if key == 'user':
                        self.user = value
                    else:
                        exec(f'self.{key} = {str(value)}')
        except FileNotFoundError:
            self.init_on_startup = True
            self.web_scraper_delay = 1800
            self.gui_launch_delay = 3600
            self.user = None
    def update(self):
        """updates the instance variables for use in the GUI"""
        with open('schedule_settings', 'r') as schedule:
            data = json.load(schedule)
            for key, value in data.items():
                if key == 'user':
                    self.user = value
                else:
                    exec(f'self.{key} = {str(value)}')


    def cron_enable(self,response):
        """enables/disables the cron job"""
        if response:
            self.init_on_startup = True
        else:
            self.init_on_startup = False
            self.web_scraper_delay = None
            self.gui_launch_delay = None
            if self.user is not None:
                cron = CronTab(user=self.user)
                cron.remove_all(comment='concert_location_and_alert')
                cron.write()
        self.write_settings()

    def cron_setup(self,user,web_scraper_delay=1800,gui_launch_delay=3600):
        """sets up or modifies a cron job as well as the delay's for launching of the scraper and gui"""
        self.user = user
        self.web_scraper_delay = web_scraper_delay
        self.gui_launch_delay = gui_launch_delay
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


    def write_settings(self):
        with open('schedule_settings', 'w') as schedule:
            sch = {'user':self.user,
                   'init_on_startup': self.init_on_startup,
                   'web_scraper_delay': self.web_scraper_delay,
                   'gui_launch_delay': self.gui_launch_delay}
            json.dump(sch, schedule)
        self.update()

class SchedulerWindows:
    def __init__(self):
        pass


if __name__ == '__main__':
    sch = SchedulerLinux()
    sch.cron_enable(False)