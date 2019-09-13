import sys
from crontab import CronTab
import json
from os import getcwd

class SchedulerLinux:

    def __init__(self):
        try:
            with open('schedule_settings','r') as schedule:
                data = json.load(schedule)
                for key,value in data.items():
                    exec(f'self.{key} = {value}')
        except FileNotFoundError:
            self.init_on_startup = True
            self.web_scraper_delay = 1800
            self.gui_launch_delay = 3600

    def cron_enable(self,response):
        if response:
            self.init_on_startup = True
        else:
            self.init_on_startup = False
            self.web_scraper_delay = None
            self.gui_launch_delay = None
            self.write_settings()

    def cron_setup(self,user,web_scraper_delay=1800,gui_launch_delay=3600):
        self.web_scraper_delay = web_scraper_delay
        self.gui_launch_delay = gui_launch_delay
        cron = CronTab(user=user)
        for job in cron:
            if job.comment == 'concert_location_and_alert':
                break
        else:
            startup = cron.new(f'export DISPLAY=:0 && python3 {getcwd()}/main.py',comment='concert_location_and_alert')
            startup.every_reboot()
            cron.write()
        self.write_settings()


    def write_settings(self):
        with open('schedule_settings', 'w') as schedule:
            sch = {'init_on_startup': True,
                   'web_scraper_delay': self.web_scraper_delay,
                   'gui_launch_delay': self.gui_launch_delay}
            json.dump(sch, schedule)

class SchedulerWindows:
    def __init__(self):
        pass


if __name__ == '__main__':
    sch = SchedulerLinux()
    sch.cron_setup('themagicalplace',1800,3600)