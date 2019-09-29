
from spotipy.oauth2 import SpotifyClientCredentials

import time
import json
from collections import defaultdict
import logging

import spotipy

import Spotify_token_handler


class SpotifyIntegration:
    """Despite the name, this class contains functions both for the aquisition of the artists a user wished to track
    using the Spotify API, as well as extracting and storing the important bits in the database used across this app"""


    scopes = ['user-top-read','','user-read-recently-played']

    # 'secret' is a strong word here, this'll be changed before release to get the client id and secret from a server
    # or something instead of just having it right here


    def __init__(self,scope,user_id):
        self.uid = str(user_id)
        self.token = Spotify_token_handler.spotify_get_token(scope)


    def __call__(self):
        """the coroutine, with each yield used to return control to the GUI in order to get data for the next method"""
        if isinstance(self.token,Exception):
            return self.token
        self.sp = spotipy.Spotify(auth=self.token)
        #What does this do?
        self.sp.trace = False
        playlists = self.sp.user_playlists(self.uid,limit=50)
        playlist_data = yield self.search_playlists(playlists)
        yield self.log_bands(playlist_data)


    def search_playlists(self,playlists):
        """
        Searches through all of a users playlists and returns a dictionary of the resultant dictionaries
        keyed to each playlist name
        """
        results = defaultdict(list)
        # Loops through all of a users playlists
        for playlist in playlists['items']:
            if playlist['owner']['id'] == self.uid: # the auth token is limited to reading only user-owned playlists

                logging.debug(msg=playlist['name'])
                logging.debug('total tracks', playlist['tracks']['total'])

                run_results = self.sp.user_playlist(self.uid, playlist['id'], fields="tracks,next")
                tracks = run_results['tracks']
                results[playlist['name']].append(tracks)
                while tracks['next']:
                    tracks = (self.sp.next(tracks))
                    results[playlist['name']].append(tracks)
        return results

    def log_bands(self,playlist_data):
        """Compiles a list of the all the artists appearing in the selected playlists"""
        tracked_bands = []
        for playlist_id,play_data in playlist_data.items():
            for track_data in play_data:
                for tdata in track_data['items']:
                    for artist in tdata['track']['artists']:
                        tracked_bands.append(artist['name'])
                        logging.debug(artist['name'])
                        time.sleep(0.01) # there's really no reason for this to be here, but eh
        return set(tracked_bands)  # returned as a set to remove duplicates

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    with open('userdata\\user_settings','r') as settings:
        data = json.load(settings)
        user_id = data['spotify_id']

    spotify_update =SpotifyIntegration('playlist-read-private',user_id)
    updater = spotify_update()
    playlists = next(updater)
    updater.send({'a':playlists['Offline']})
    logging.info(',')