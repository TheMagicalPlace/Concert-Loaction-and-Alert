import json as json
import sqlite3 as sqlite
import time
from datetime import timedelta,date as dt_date


import re



class Notifications:

    def __init__(self):
        with open('user_settings','r') as settings:
            data = json.load(settings)
            self.bands = data['bands']
            self.banddb = {band: str("_".join(band.split(' '))) for band in self.bands}
            for band in self.banddb:
                self.banddb[band] = re.sub(r'[\[|\-*/<>\'\"&+%,.=~!^()\]]', '', self.banddb[band])
        self.concert_database = sqlite.connect('concert_db.db')

    def check_dates(self):

        # TODO - refactor this to use a context manager so that the database actually saves the changes made


        current_date = dt_date.today().isoformat()
        #current_date = '2020-01-01'
        cur = self.concert_database.cursor()
        for band in self.bands:
            print(band)
            concert_info = list(zip(*[(cdate[0],cdate[1],cdate[2]) for cdate in
                                      cur.execute(f'SELECT * FROM {self.banddb[band]}').fetchall()]))
            print(concert_info)
            cur.execute(f'DELETE FROM {self.banddb[band]} WHERE Date < {current_date}')
            z = list(zip(*[(cdate[0],cdate[1],cdate[2]) for cdate in
                                      cur.execute(f'SELECT * FROM {self.banddb[band]}').fetchall()]))
            print(z)

            if len(concert_info):
                concert_dates,location,hour = concert_info
            else:continue
            for date,location,hour in zip(concert_dates,location,hour):
                if location == 'Out of Range':
                    continue
                #date = time.strptime(date,'%Y-%m-%d')

                continue
                time_to = time.mktime(date)-time.mktime(current_date)
                if time_to < 0:
                    continue
                elif time_to < 60*60*24*7*5: # currently one week, modify as needed
                    print(band,location,timedelta(seconds=time_to),hour)
                else: print(band,timedelta(seconds=time_to),hour)







    def notify_user_(self):
        pass

if __name__ == '__main__':
    s = dt_date.today().isoformat()
    print(s)
    test = Notifications()
    test.check_dates()