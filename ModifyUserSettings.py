import json
import os

import requests
from bs4 import BeautifulSoup as soup
from geopy import geocoders

from Models.user_settings import UserSettings


class LocatorSetup:
    """The (poorly named) class containing the methods used to format and save the data from the first
    time setup into a user_settings file"""

    bordering_states = {
        "AL": ["FL", "GA", "MS", "TN"],
        "AK": [],
        "AZ": ["CA", "NM", "NV", "UT"],
        "AR": ["LA", "MO", "MS", "OK", "TN", "TX"],
        "CA": ["AZ", "NV", "OR"],
        "CO": ["AZ", "KS", "NE", "NM", "OK", "UT", "WY"],
        "CT": ["MA", "NY", "RI"],
        "DE": ["MD", "NJ", "PA"],
        "FL": ["AL", "GA"],
        "GA": ["AL", "FL", "NC", "SC", "TN"],
        "HI": [],
        "ID": ["MT", "NV", "OR", "UT", "WA", "WY"],
        "IL": ["IA", "IN", "KY", "MO", "WI"],
        "IN": ["IL", "KY", "MI", "OH"],
        "IA": ["IL", "MN", "MO", "NE", "SD", "WI"],
        "KS": ["CO", "MO", "NE", "OK"],
        "KY": ["IL", "IN", "MO", "OH", "TN", "VA", "WV"],
        "LA": ["AR", "MS", "TX"],
        "ME": ["NH"],
        "MD": ["DE", "PA", "VA", "WV"],
        "MA": ["CT", "NH", "NY", "RI", "VT"],
        "MI": ["IN", "OH", "WI"],
        "MN": ["IA", "ND", "SD", "WI"],
        "MS": ["AL", "AR", "LA", "TN"],
        "MO": ["AR", "IA", "IL", "KS", "KY", "NE", "OK", "TN"],
        "MT": ["ID", "ND", "SD", "WY"],
        "NE": ["CO", "IA", "KS", "MO", "SD", "WY"],
        "NV": ["AZ", "CA", "ID", "OR", "UT"],
        "NH": ["MA", "ME", "VT"],
        "NJ": ["DE", "NY", "PA"],
        "NM": ["AZ", "CO", "OK", "TX", "UT"],
        "NY": ["CT", "MA", "NJ", "PA", "VT"],
        "NC": ["GA", "SC", "TN", "VA"],
        "ND": ["MN", "MT", "SD"],
        "OH": ["IN", "KY", "MI", "PA", "WV"],
        "OK": ["AR", "CO", "KS", "MO", "NM", "TX"],
        "OR": ["CA", "ID", "NV", "WA"],
        "PA": ["DE", "MD", "NJ", "NY", "OH", "WV"],
        "RI": ["CT", "MA"],
        "SC": ["GA", "NC"],
        "SD": ["IA", "MN", "MT", "NE", "ND", "WY"],
        "TN": ["AL", "AR", "GA", "KY", "MO", "MS", "NC", "VA"],
        "TX": ["AR", "LA", "NM", "OK"],
        "UT": ["AZ", "CO", "ID", "NV", "WY"],
        "VT": ["MA", "NH", "NY"],
        "VA": ["KY", "MD", "NC", "TN", "WV"],
        "WA": ["ID", "OR"],
        "WV": ["KY", "MD", "OH", "PA", "VA"],
        "WI": ["IA", "IL", "MI", "MN"],
        "WY": ["CO", "ID", "MT", "NE", "SD", "UT"],
    }

    state_names = {
        "AL": "Alabama",
        "AK": "Alaska",
        "AZ": "Arizona",
        "AR": "Arkansas",
        "CA": "California",
        "CO": "Colorado",
        "CT": "Connecticut",
        "DE": "Delaware",
        "FL": "Florida",
        "GA": "Georgia",
        "HI": "Hawaii",
        "ID": "Idaho",
        "IL": "Illinois",
        "IN": "Indiana",
        "IA": "Iowa",
        "KS": "Kansas",
        "KY": "Kentucky",
        "LA": "Louisiana",
        "ME": "Maine",
        "MD": "Maryland",
        "MA": "Massachusetts",
        "MI": "Michigan",
        "MN": "Minnesota",
        "MS": "Mississippi",
        "MO": "Missouri",
        "MT": "Montana",
        "NE": "Nebraska",
        "NV": "Nevada",
        "NH": "New Hampshire",
        "NJ": "New Jersey",
        "NM": "New Mexico",
        "NY": "New York",
        "NC": "North Carolina",
        "ND": "North Dakota",
        "OH": "Ohio",
        "OK": "Oklahoma",
        "OR": "Oregon",
        "PA": "Pennsylvania",
        "RI": "Rhode Island",
        "SC": "South Carolina",
        "SD": "South Dakota",
        "TN": "Tennessee",
        "TX": "Texas",
        "UT": "Utah",
        "VT": "Vermont",
        "VA": "Virginia",
        "WA": "Washington",
        "WV": "West Virginia",
        "WI": "Wisconsin",
        "WY": "Wyoming",
    }

    def __init__(self,user_settings):
        self.user_settings = user_settings
    def __call__(self):
        """If the user_settings file already exists this does nothing, but otherwise gets the required
        user info and saves to to a JSON file. Note this should only ever be called by the GUI, individual methods
        should be called directly, if needed."""

        if self.user_settings.user_location.__contains__(None):
            location = yield
            self.user_location_set(location)
        if self.user_settings.spotify_id is None:
            self.user_settings.spotify_id = yield
            self.user_settings.save_to_file()
        if len(self.user_settings.bands) == 0:
            bands = yield
            self.get_bands(bands)
            self.user_settings.save_to_file()
            yield

        self.user_settings.save_to_file()

    def user_location_set(self,location):
        # TODO - find out what this returns for non-existant places (i.e. typos in user input)
        """Finds user location (latitude,longitude) via Nominatim"""
        if location:
            userloc = geocoders.Nominatim(user_agent="testing_location_find_10230950239").geocode(location,exactly_one=True)
            self.user_settings.user_location[0] = tuple(abv for abv in self.state_names.keys()
                                     if abv in location or self.state_names[abv] in location)
            if not self.user_settings.user_location[0]: self.user_settings.user_location[0] = 'none'
            self.user_settings.user_location[1] = (userloc.latitude,userloc.longitude)
        else:
            self.user_settings.user_location = ['Not Specified',('Not Specified','Not Specified')]

        self.user_settings.save_to_file()

    def get_bands(self,bands=None):
        """ Creating a list of bands for which concert info is wanted"""
        [self.user_settings.bands.append(band) for band in bands if band not in self.user_settings.bands and band not in self.user_settings.removed_bands]


class LocatorMain(LocatorSetup):
    ''' This class is essentially a container for all the operations required by the GUI, with
    some stuff recycled from the class that is used for first time setup (LocatorSetup). Notable differences include
    that the class itself is not callable, as all methods are called directly by the corresponding GUI element'''


    def __call__(self):
        pass # Not Callable

    def update_user_location(self,location):
        '''Changes user location'''
        # TODO - currently setting it like this wont update location for already tracked concerts, either
        # TODO find a way to track multiple or dump all the tables & start fresh
        super().user_location_set(location)
        self.user_settings.save_to_file()

    def remove_spotify_tracking(self):
        self.user_settings.spotify_user_id = None
        self.user_settings.save_to_file()

    def save_spotify_username(self,user_id):
        self.user_settings.spotify_user_id = user_id
        self.user_settings.save_to_file()

    def add_bands(self,bands):
        super().get_bands(bands)
        self.user_settings.save_to_file()

    def remove_bands(self,bands):
        [self.user_settings.removed_bands.append(band) for band in bands]
        self.user_settings.bands = [band for band in self.user_settings.bands if band not in self.user_settings.removed_bands]
        self.user_settings.save_to_file()

    def add_removed_bands(self,bands):
        [self.user_settings.removed_bands.remove(band) for band in bands]
        super().get_bands(bands)
        self.user_settings.save_to_file()

    def change_time_to_display(self,ttd):
        'changes the range of dates for which notifications will be given'
        self.user_settings.concert_notification_time_to_display = ttd
        self.user_settings.save_to_file()

if __name__ == '__main__':
    l = LocatorMain()
    l.user_settings.save_to_file()