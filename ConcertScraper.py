


import re
from collections import defaultdict
import sqlite3 as sqlite
from pathlib import Path
import json as json
import datetime
import logging

import bs4
import requests

from LocationFilter import LocationFilter

class ConcertFinder:
    """Contains the methods used in the lookup of concerts near the user's given location and save them
    to a database"""

    # used for date formatting
    ymd_format = re.compile(r'\d{4}-\d{2}-\d{2}')
    hms_format = re.compile(r'(?<=\d{4}-\d{2}-\d{2}T)(\d{2}:\d{2}:\d{2})')

    def __init__(self):
        with open('userdata\\user_settings','r') as settings:
            data = json.load(settings)
            self.bands = data['bands']
            data['last_checked'] = datetime.date.today().isoformat()
        with open('userdata\\user_settings','w') as settings:
            json.dump(data,settings)

        # used to modify band names to be web search and SQL database friendly
        self.bandwb = {band:str("+".join(band.split(' ')))  for band in self.bands} #for use in website searches
        self.banddb = {band:str("_".join(band.split(' '))) for band in self.bands} # for use in database write and lookup

        self.concerts = defaultdict(list)
        self.lcfilter = LocationFilter() # from LocationFilter.py, used to track if a concert is nearby or not
        self._setUp()

    def __call__(self):
        """returns a primed coroutine to be used by a child thread, band_iterator_thread is used
        to allow quick killing of the thread without risking corrupting of user data (i.e. so that the process
        isnt suspended in the middle of a context manager)"""
        return self.band_iterator_thread()

    def _setUp(self):
        """Checks if a database already exists for concert info, and creates one if not"""
        path = Path('./concert_db.db')
        try:
            assert path.exists() is True
            self.concert_database = sqlite.connect('userdata\\concert_db.db')
        except AssertionError:
            self.concert_database = sqlite.connect('userdata\\concert_db.db')

    def _website_search_songkick(self,band,concert_dates=None):
        """Searches out concerts from songkick based on the bands in user_settings"""
        for page in range(1,5):

            params = {'page':page,'per_page':15,'query':self.bandwb[band],'type':'upcoming'}
            try:
                yeet = requests.get(f'https://www.songkick.com/search',params=params,timeout=30) # i refuse to change this

            # timeouts are just skipped over, as a rule of thumb 2-3 runs are needed to get info for large amounts of bands
            except requests.exceptions.ConnectionError as timeout:
                logging.info(timeout)
                continue
            except requests.exceptions.ReadTimeout as rtimeout:
                logging.info(rtimeout)
                continue

            #parsing the html response
            concpage = bs4.BeautifulSoup(yeet.text,features="html.parser")
            concpage = concpage.select('li[class="concert event"]')

            for concert in concpage:

                date = concert.select('time[datetime]')
                datestr = str(*date[0].attrs.values())
                date_time_list = re.findall(self.ymd_format,datestr)+re.findall(self.hms_format,datestr) \
                    if re.findall(self.hms_format,datestr) else re.findall(self.ymd_format,datestr)+['Not Specified']

                # Converting to a datetime.date object to simplify date checking for SQL
                date_time_list[0] = datetime.date.fromisoformat(date_time_list[0])
                if date[0].getText() in self.concerts.keys():
                    return # indicates that this page has already been seen, common if the number of concerts < 5 pages
                elif concert_dates is not None:
                    if date_time_list[0].isoformat() in concert_dates:
                        continue #
                self.concerts[date[0].getText()].append(date_time_list)
                location = concert.select('p[class="location"]')

                # breaks up the location info into something usable for geolocation lookup
                wsp = re.compile(r'(?:\s)+(\S+|[ ,]?)',re.MULTILINE.DOTALL)
                location = " ".join(wsp.findall(location[0].getText())[1:])
                formatted_location = ", ".join(location.split(', ')[1:])
                self.concerts[date[0].getText()].append(formatted_location)
                in_range = True if self.lcfilter(formatted_location) else 'Out of Range' # calls the location checker
                self.concerts[date[0].getText()].append(in_range)

    def _band_info_write(self,band,cur):
        """Takes the isolated info from the website search and saves it to the database. Note that this
        entire method takes place within the context manager of its caller"""

        for _,vals in self.concerts.items():
            'the format for enteries is as follows (Date of concert,location of concert (Venue,City,State),Distance to' \
            'location (if applicable),time of concert (if avalible)'
            try:
                cur.execute(f"INSERT INTO {self.banddb[band]} VALUES (?,?,?,?,?)",(vals[0][0],vals[1],'Not Implimented Yet',vals[0][1],vals[2]))
            except sqlite.OperationalError :
                cur.execute(f'DROP TABLE {self.banddb[band]}') #for bad data and/or modification of table params
                cur.execute(f"CREATE TABLE {self.banddb[band]} (Date DATE,Location TEXT,Distance TEXT, Time TEXT,IsInRange TEXT)")
                cur.execute(f"INSERT INTO {self.banddb[band]} VALUES (?,?,?,?,?)",
                            (vals[0][0], vals[1], 'Not Implimented Yet', vals[0][1], vals[2]))



    def band_iterator(self):
        # This has been replaced by band_iterator thread in in order to allow the spawned threads to safely exit without
        # risking data corruption, and is mostly here for reference.

        """Iterates through all of the bands given in the JSON file"""
        for band in self.bands:
            with self.concert_database as cdb:
                self.concerts = defaultdict(list)
                cur = cdb.cursor()
                self.banddb[band] = re.sub(r'[\[|\-*/<>\'\"&+%,.=~!^()\]]', '', self.banddb[band])
                try:
                    concert_dates = [cdate[0] for cdate in cur.execute(f'SELECT Date FROM {self.banddb[band]}').fetchall()]
                    self._website_search_songkick(band,concert_dates)
                except sqlite.OperationalError:
                    cur.execute(f"CREATE TABLE {self.banddb[band]} "
                                f"(Date DATE,Location TEXT,Distance TEXT, Time TEXT,IsInRange TEXT)")
                    self._website_search_songkick(band)
                self._band_info_write(band,cur)


    def band_iterator_thread(self):
        """sequentially iterates through each band in user_settings, with one band looked up
        per call"""
        bands = (band for band in self.bands)
        print('test')
        while bands:
            band = next(bands)
            yield self.bands.index(band)
            # The database is reopened for each band so that in the event the web scraper exits unexpectedly
            # only data for the last band is lost
            with self.concert_database as cdb:
                self.concerts = defaultdict(list)
                cur = cdb.cursor()
                self.banddb[band] = re.sub(r'[\[|\-*/<>\'\"&+%,.=~!^()\]]', '', self.banddb[band])
                try:
                    concert_dates = [cdate[0] for cdate in cur.execute(f'SELECT Date FROM {self.banddb[band]}').fetchall()]
                    self._website_search_songkick(band,concert_dates)
                except sqlite.OperationalError:
                    cur.execute(f"CREATE TABLE {self.banddb[band]} "
                                f"(Date DATE,Location TEXT,Distance TEXT, Time TEXT,IsInRange TEXT)")
                    self._website_search_songkick(band) # the web scraper
                self._band_info_write(band,cur)




if __name__ == '__main__':
    # called by a cronjob on a user determined schedule
    scraper = ConcertFinder()
    scraper()





















