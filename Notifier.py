import json as json
import sqlite3 as sqlite
import time
from datetime import timedelta


import re



class Notifications:

    def __init__(self):
        with open('user_settings','r') as settings:
            data = json.load(settings)
            self.bands = data['bands']
            self.banddb = {band: str("_".join(band.split(' '))) for band in self.bands}
            for band in self.banddb:
                self.banddb[band] = re.sub(r'[\[|\-*/<>,=~!^()\]]', '', self.banddb[band])
        self.concert_database = sqlite.connect('concert_db.db')

    def check_dates(self):
        current_date = time.gmtime()
        cur = self.concert_database.cursor()
        for band in self.bands:
            concert_info = list(zip(*[(cdate[0],cdate[1],cdate[2]) for cdate in
                                      cur.execute(f'SELECT * FROM {self.banddb[band]}').fetchall()]))
            if len(concert_info):
                concert_dates,location,hour = concert_info
            else:continue
            for date,location,hour in zip(concert_dates,location,hour):
                if location == 'Out of Range':
                    continue
                date = time.strptime(date,'%Y-%m-%d')
                time_to = time.mktime(date)-time.mktime(current_date)
                if time_to < 0:
                    continue
                elif time_to < 60*60*24*7*5: # currently one week, modify as needed
                    print(band,location,timedelta(seconds=time_to),hour)
                else: print(band,timedelta(seconds=time_to),hour)


    def notify_user_(self):
        pass


test = Notifications()
test.check_dates()