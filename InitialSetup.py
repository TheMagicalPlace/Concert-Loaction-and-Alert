
import requests
from bs4 import BeautifulSoup as soup
from geopy import geocoders
import json

import Spotify_API_Integration

class setup_data:

    def __init__(self):
        try:
            with open('user_settings','r') as settings:
                data = json.load(settings)
                for key,value in data.items():
                    exec(f'self.{key} = {value}')

        except FileNotFoundError:
            self.state_pairs = {}
            self.abbreviation_to_state = {}
            self.state_to_abbreviation = {}
            self.user_location = [None,None]
            self.bands = []
            self()


    def __call__(self, location,bands):
        """If the user_settings file already exists this does nothing, but otherwise gets the required
        user info and saves to to a JSON file"""
        try:
            user_settings = open('user_settings', 'r')
        except:
            self.state_pairs_find()
            self.state_abbreviation_associations()
            #location = input('Enter your current location in the form (optional = address), City, State,')
            self.user_location_set(location)
            self.get_bands(bands)
            self.save_data()



    def state_pairs_find(self):
        """Generates a list of adjacent states for use with narrowing down the locations to be searched in order
        to limit queries to geolocators"""
        states = requests.get('https://state.1keydata.com/bordering-states-list.php', verify=False)
        stsoup = soup(states.text,features="html.parser")
        stsoup = stsoup.select("table[class='content4']")
        stsoup = stsoup[0].select("tr")
        for subsoup in stsoup[1:]:
            sres = subsoup.select('td')
            self.state_pairs[sres[0].string] = tuple(sres[1].string.split(', '))

    def state_abbreviation_associations(self):
        """Generates a dictionary of state full names to abbreviations"""
        sabv = requests.get('https://abbreviations.yourdictionary.com/articles/state-abbrev.html')
        assocs = soup(sabv.text,features="html.parser")
        assocs = assocs.select('ul')
        for pairs in assocs[0].select('li'):
            pairs = pairs.string.split(' - ')
            self.state_to_abbreviation[pairs[0]] = pairs[1][:-1]
            self.abbreviation_to_state[pairs[1][:-1]] = pairs[0]

    def user_location_set(self,location):
        """Finds user location (latitude,longitude) via Nominatim"""
        userloc = geocoders.Nominatim(user_agent="testing_location_find_10230950239").geocode(location,True)
        self.user_location[0] = tuple(abv for abv in self.abbreviation_to_state.keys()
                                 if abv in location or self.abbreviation_to_state[abv] in location)
        if not self.user_location[0]: self.user_location[0] = 'none'
        self.user_location[1] = (userloc.latitude,userloc.longitude)

    def get_bands(self,bands):
        """ Creating a list of bands for which concert info is wanted"""
        for band in bands:
            self.bands.append(band)

    def save_data(self):
        "Saves user data to a JSON file"
        data = {'state_pairs':self.state_pairs,
                 'user_location':self.user_location,
                 'state_to_abbreviation':self.state_to_abbreviation,
                 'abbreviation_to_state':self.abbreviation_to_state,
                 'bands':self.bands}
        with open('user_settings','w') as settings:
            json.dump(data,settings)
