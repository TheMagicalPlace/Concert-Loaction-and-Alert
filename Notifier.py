import json as json
import sqlite3 as sqlite
import time
from datetime import timedelta,date as dt_date
import threading
from collections import defaultdict
import re



class Notifications:

    def __init__(self):
        """most of this is just defining the conversion dictionaries for the band in order to (try to) sanatize the
        database input. """
        current_date = dt_date.today().isoformat()
        with open('user_settings','r') as settings:
            data = json.load(settings)
            self.bands = data['bands']
            self.notification_range = data['concert_notification_range']
            self.banddb = {band: str("_".join(band.split(' '))) for band in self.bands}
            for band in self.banddb:
                self.banddb[band] = re.sub(r'[\[|\-*/<>\'\"&+%,.=~!^()\]]', '', self.banddb[band])
        self.concert_database = sqlite.connect('concert_db.db')
        try:
            with self.concert_database as cdb:
             cur = cdb.cursor()
             cur.execute(f'DELETE FROM Upcoming WHERE date < {current_date}')
        except sqlite.OperationalError:
            with self.concert_database as cdb:
                cur = cdb.cursor()
                cur.execute('CREATE TABLE Upcoming (band TEXT,location TEXT,time TEXT,date DATE, days_to TEXT)')


    def check_dates(self):
        """This method does the bulk of the database managment, being responsable for pruning entries that
        are older than the current date, as well as for creating and maintaining the 'Upcoming' table used in
        the creation of the notifications for upcoming concerts"""

        upcoming_events = defaultdict(list)
        current_date = dt_date.today().isoformat()

        # Getting the data for concert entries already present in the Upcoming table to avoid inserting duplicates
        with self.concert_database as cdb:
            cur = cdb.cursor()
            cur.execute(f'DELETE FROM Upcoming WHERE Upcoming.date < {current_date}')
            result = cur.execute('SELECT band,date FROM Upcoming').fetchall()
        [upcoming_events[band].append(date) for band,date in result]

        #
        for band in self.bands:

            # The database is opened & closed for each band in order to prevent losing all data should
            # the containing loop terminate unexpectedly
            with self.concert_database as cdb:
                cur = cdb.cursor()

                # Clearing out entries older than the current date
                cur.execute(f'DELETE FROM {self.banddb[band]} WHERE Date < {current_date}')
                concert_info = list(zip(*[(cdate[0],cdate[1],cdate[2],cdate[3],cdate[4]) for cdate in
                                          cur.execute(f'SELECT * FROM {self.banddb[band]}').fetchall()]))


                if not concert_info:
                    # Skips empty tables
                    continue

                for concert_date,location,distance,hour,inrange in zip(*concert_info):
                    if inrange == 'Out of Range':  # Ignores entries outside of local-ish area
                        continue

                    date = time.strptime(concert_date,'%Y-%m-%d')
                    current = time.strptime(current_date,'%Y-%m-%d')
                    time_to = time.mktime(date)-time.mktime(current)
                    time_to_repr = str(timedelta(seconds=time_to))[:-9]

                    if time_to < 60*60*24*7*self.notification_range: # set in InitialSetup.LocatorMain, default 2 weeks

                        # This updates the 'time_to' colunm in the database if an entry for the current band and date exist,
                        # and creates a new entry otherwise
                        if upcoming_events and concert_date in upcoming_events[self.banddb[band]]:
                            cur.execute(f'UPDATE Upcoming SET days_to =:days_to WHERE Upcoming.date =:date AND Upcoming.band =:band',
                                        {'days_to':time_to_repr,'date':concert_date,'band':self.banddb[band]})
                        else:
                            cur.execute('INSERT INTO Upcoming VALUES (:band,:location,:time,:date,:days_to)',
                                        {'band':self.banddb[band],'date':concert_date,'location':location,'time':hour,'days_to':time_to_repr})
                    else: continue

    def notify_user_(self):
        with self.concert_database as cdb:
            cur = cdb.cursor()
            upcoming_concerts = cur.execute('SELECT * FROM Upcoming ORDER BY date;')
            print('\n'.join([" ".join(x) for x in upcoming_concerts]))

if __name__ == '__main__':

    test = Notifications()
    test.check_dates()
    test.notify_user_()