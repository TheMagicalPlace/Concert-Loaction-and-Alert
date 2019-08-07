


import re
import bs4
import requests
from collections import defaultdict
import sqlite3 as sqlite
from LocationFilter import LocationFilter
from pathlib import Path
import json as json


class ConcertFinder:

    # TODO - impliment automatic removal of dates that have passes

    ymd_format = re.compile(r'\d{4}-\d{2}-\d{2}')
    hms_format = re.compile(r'(?<=\d{4}-\d{2}-\d{2}T)(\d{2}:\d{2}:\d{2})')

    def __init__(self):
        with open('user_settings','r') as settings:
            data = json.load(settings)
            self.bands = data['bands']

        self.bandwb = {band:str("+".join(band.split(' ')))  for band in self.bands} #for use in website searches
        self.banddb = {band:str("_".join(band.split(' '))) for band in self.bands} # for use in database write and lookup
        self.concerts = defaultdict(list)
        self.lcfilter = LocationFilter()
        self._setUp()

    def __call__(self, *args, **kwargs):
        self.band_iterator()

    def _setUp(self):
        """Checks if a database already exists for concert info, and creates one if not"""
        path = Path('./concert_db.db')
        try:
            assert path.exists() is True
            self.concert_database = sqlite.connect('concert_db.db')
        except AssertionError:
            self.concert_database = sqlite.connect('concert_db.db')

    def _website_search_songkick(self,band,concert_dates=None):
        """Searches out concerts from songkick based on the imputted band"""
        print(band)
        for page in range(1,5):

            yeet = requests.get(f'https://www.songkick.com/search?page={page}&per_page=10&query={self.bandwb[band]}&type=upcoming')
            concpage = bs4.BeautifulSoup(yeet.text)
            concpage = concpage.select('li[class="concert event"]')
            for concert in concpage:
                date = concert.select('time[datetime]')
                datestr = str(*date[0].attrs.values())
                date_time_list = re.findall(self.ymd_format,datestr)+re.findall(self.hms_format,datestr) \
                    if re.findall(self.hms_format,datestr) else re.findall(self.ymd_format,datestr)+['Not Specified']
                if date[0].getText() in self.concerts.keys():
                    return
                elif concert_dates is not None:
                    if date_time_list[0] in concert_dates:
                        continue
                self.concerts[date[0].getText()].append(date_time_list)
                location = concert.select('p[class="location"]')
                wsp = re.compile(r'(?:\s)+(\S+|[ ,]?)',re.MULTILINE.DOTALL)
                location = " ".join(wsp.findall(location[0].getText())[1:])
                formatted_location = ", ".join(location.split(', ')[1:])
                location = location if self.lcfilter(formatted_location) else 'Out of Range'
                self.concerts[date[0].getText()].append(location)

    def _band_info_write(self,band,cur):
        """Takes the isolated info from the website search and saves it to the database"""
        # TODO convert to UTC and input it into the database via sqlite's builtins for the time module
        for keys,vals in self.concerts.items():
            cur.execute(f"INSERT INTO {self.banddb[band]} VALUES (?,?,?)",(vals[0][0],vals[1],vals[0][1]))

    def band_iterator(self):
        """Iterates through all of the bands given in the JSON file"""

        for band in self.bands:
            with self.concert_database as cdb:
                self.concerts = defaultdict(list)
                cur = cdb.cursor()
                self.banddb[band] = re.sub(r'[\[|\-*/<>,=~!^()\]]', '', self.banddb[band])
                try:
                    concert_dates = [cdate[0] for cdate in cur.execute(f'SELECT Date FROM {self.banddb[band]}').fetchall()]
                    self._website_search_songkick(band,concert_dates)
                except sqlite.OperationalError:
                    cur.execute(f"CREATE TABLE {self.banddb[band]} (Date TEXT,Location TEXT,Time TEXT)")
                    self._website_search_songkick(band)
                self._band_info_write(band,cur)




print(repr('!'))
test = ConcertFinder()
test.band_iterator()

#test.band_info_sort()
#test._website_search_songkick()
#test._band_info_write()




















