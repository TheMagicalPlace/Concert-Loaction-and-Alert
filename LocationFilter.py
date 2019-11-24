
import json as json
from time import sleep
import os.path
from geopy import geocoders,distance,exc as geopy_exc
import requests

class LocationFilter:

    state_pairs = {}
    abbreviation_to_state = {}
    state_to_abbreviation = {}
    user_location = [None, None]
    bands = []

    def __init__(self):
        with open(os.path.join('userdata','user_settings'), 'r') as settings:
            data = json.load(settings)
            for key, value in data.items():
                if key == 'last_checked':
                    self.last_checked = value
                else:
                    exec(f'self.{key} = {value}')
        home_state = [state for abbv,state in self.abbreviation_to_state.items()
                      if abbv in self.user_location[0] or state in self.user_location[0]]
        self.adjacent = [self.state_to_abbreviation[state.split(' ')[0]] for state in self.state_pairs[home_state[0]]+home_state]


    def __call__(self, location):
        """Filters out concert locations based on if they are nearby the user imputted location, currently
        limited to the 50 US states"""
        isvalidlocation = self.filter_by_state(location)
        if isvalidlocation:
            isvalidlocation = self.filter_by_range(isvalidlocation)
            if isvalidlocation:
                return location
        else:
            return False

    def filter_by_state(self,location):
        """Filters concert locations to adjacent states in order to minimize the number of
        times the geolocator has to be called"""

        try:
            location_state = [abbv for abbv,state in self.abbreviation_to_state.items()
                      if abbv in location or state in location][0]
            return location if location_state in self.adjacent else False
        except IndexError: return False # Can not currently be used outside the 50 US States

    def filter_by_range(self,isvalidlocation):
        """Further filters out results to be within an arbitrary geographic distance. Note that this uses
        a shortest-line method of finding distance and does not account for road layout (or bodies of water)"""
        try:
            concertloc = geocoders.Nominatim(user_agent="testing_location_find_10230950239").geocode(isvalidlocation,True)
        except geopy_exc.GeocoderTimedOut:
            print('Locator timed out, waiting 30s before continuing')
            sleep(30)
        else:
            if concertloc:
                concertloc = (concertloc.latitude,concertloc.longitude)
                # TODO update to allow for user input of maximum range
                valid_range = 200 # miles
                dist = distance.distance(self.user_location[1],concertloc).miles
                print(f'Finding geographic distance between {self.user_location} and {concertloc}')
                sleep(5)
                return False if dist > valid_range else concertloc
            else: return False


        # alternate method for getting distances, currently excluded in the interest of not potentially abusing a free service

        if not True:
             dist = requests.get(
                 f'https://www.distance-cities.com/distance-{" ".join(self.user_location[0])}-to-{"-".join(concertloc)}')




