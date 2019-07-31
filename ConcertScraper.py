



import bs4
import request
import os
from selenium import webdriver

test = 1

class ConcertFinder():

    def __init__(self,band):
        """Initializes the selenium webdriver (firefox only)"""
        self.browser = webdriver.Firefox()
        self.band = band

    def _website_search_songkick(self):
        """Searches out concerts from songkick based on the imputted band"""
        self.browser.get('https://www.songkick.com/')
        search = self.browser.find_element_by_name("query")
        print(search)

    def _band_info_write(self):
        """Takes the isolated info from the website search and saves it to the disk"""
        pass

    def _raw_to_html(self):
        """Converts the raw informtion from _bband_info_write & formats it into an HTML doc before saving"""
        pass



test = ConcertFinder()
test._website_search_songkick()
#<input name="query" type="search" value="" class="text navigation-search" placeholder="Find concerts for any artist or city">