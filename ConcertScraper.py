


import unittest

import re
import bs4
import requests
from collections import defaultdict
import sqlite3 as sqlite
from time import strptime,gmtime,mktime,localtime
import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.common.keys import Keys
import page

from selenium.webdriver.support.ui import Select
from pathlib import Path
test = 1

class ConcertFinder():

    adjacent_states = {}

    def __init__(self,band):

        self.band = str("-".join(band.split(' '))) #for use in website searches
        self.banddb = str("_".join(band.split(' '))) # for use in database write and lookup
        self.concerts = defaultdict(list)
        self._setUp()


    def _setUp(self):
        path = Path('./concert_db.db')
        "Checks if a database already exists for concert info, and creates one if not"
        try:
            assert path.exists() is True
            self.concert_database = sqlite.connect('concert_db.db')
        except AssertionError:
            self.concert_database = sqlite.connect('concert_db.db')


    def _website_search_songkick(self):
        """Searches out concerts from songkick based on the imputted band"""

        for page in range(0,5):
            yeet = requests.get(f'https://www.songkick.com/search?page={page}&amp;per_page=20&amp;query={self.band}&type=upcoming')
            concpage = bs4.BeautifulSoup(yeet.text)
            concpage = concpage.select('li[class="concert event"]')
            for x in concpage:
                date = x.select('time[datetime]')
                if date[0].getText() in self.concerts.keys():
                    return
                utc_time = (str(*date[0].attrs.values())[:-5].split('T',2))
                self.concerts[date[0].getText()].append(utc_time)

                location = x.select('p[class="location"]')
                wsp = re.compile(r'(?:\s)+(\S+|[ ,]?)',re.MULTILINE.DOTALL)
                location = " ".join(wsp.findall(location[0].getText())[:-1])

                self.concerts[date[0].getText()].append(location)


    def _band_info_write(self):
        """Takes the isolated info from the website search and saves it to the database"""
        with self.concert_database:
            cur = self.concert_database.cursor()
            try:
                # TODO convert to UTC and input it into the database via sqlite's builtins for the time module
                dates = [date[0] for date in cur.execute(f'SELECT date FROM {self.banddb}').fetchall()]
                for keys,vals in self.concerts.items():
                    if vals[0][0] in dates: continue
                    cur.execute(f'SELECT date FROM {self.banddb}')
                    print(vals[0])
                    cur.execute(f"INSERT INTO {self.banddb} VALUES (?,?,?)",(vals[0][0],vals[1],vals[0][1]))
            except sqlite.OperationalError:
                cur.execute(f"CREATE TABLE {self.banddb} (Date TEXT,Location TEXT,Time TEXT)")
                self._band_info_write()

    def band_info_sort(self):
        """Filters out concerts base on time and location criteria"""
        # TODO - impliment fitering of concert results by location (and make optional?)
        with self.concert_database:
            pass
        date = '2019-01-01' # Test value, remove when done
        current_date = gmtime()

        date = strptime(date, f"{date[:2]}%y-%m-%d")
        time_until_concert = ((mktime(date)-mktime(current_date))/604800) # in weeks, as '1607005' seconds isn't exactly informative

    def location_filter(self):


#test = ConcertFinder('streetlight manifesto')

#test.band_info_sort()



def test():
    e = requests.get('https://www.google.com/maps/place/SunOpta+Minerals')
    print(e.url)
test()





















