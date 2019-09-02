
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy,spotipy.util as util
import time
import json
from collections import  defaultdict


class SpotifyIntegration:
    """Despite the name, this class contains functions both for the aquisition of the artists a user wished to track
    using the Spotify API, as well as extracting and storing the important bits in the database used across this app"""


    scopes = ['user-top-read','playlist-read-private','user-read-recently-played']

    # 'secret' is a strong word here, this'll be changed before release to get the client id and secret from a server
    # or something instead of just having it right here

    secret = 'c1710a69f80c405d9ecad0eb1c6f548d'
    client_id = 'ce4091c720c04087ad60ed054ffd9760'

    def __init__(self,user_id):
        """Sets up user permissions if not already done"""
        self.uid = user_id
        scope = self.scopes[1]
        token = util.prompt_for_user_token(user_id,f'{scope}',redirect_uri='http://localhost/',client_secret='c1710a69f80c405d9ecad0eb1c6f548d',client_id=self.client_id)

    def __call__(self, *args, **kwargs):



        secret = 'c1710a69f80c405d9ecad0eb1c6f548d'
        client_id ='ce4091c720c04087ad60ed054ffd9760'

        # TODO remove token aquisition here and simpilify to just get tokens on initialization of an insance

        #This is mostly redundant as the token can just be taken from init
        token = util.prompt_for_user_token(self.uid, f'playlist-read-private', redirect_uri='http://localhost/',
                                           client_secret='c1710a69f80c405d9ecad0eb1c6f548d', client_id=self.client_id)
        self.sp = spotipy.Spotify(auth=token)

        #What does this do?
        self.sp.trace = False

        # Again, is there any reason for this to be here? -- Prevents StopIteration for 'reasons'
        if True:
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

                #print(playlist['name'])
                #print('  total tracks', playlist['tracks']['total']) # prints no. of tracks in each playlist

                run_results = self.sp.user_playlist(self.uid, playlist['id'], fields="tracks,next")
                tracks = run_results['tracks']
                results[playlist['name']].append(tracks)
                while tracks['next']:
                    tracks = (self.sp.next(tracks))
                    results[playlist['name']]+=tracks
        return results

    def log_bands(self,playlist_data):
        """Compiles a list of the all the artists appearing in the selected playlists"""
        tracked_bands = []
        for playlist_id,play_data in playlist_data.items():
            for track_data in play_data[0]['items']:
                for artist in track_data['track']['artists']:
                    tracked_bands.append(artist['name'])
                    print(artist['name'])
                    time.sleep(0.01)
        print(set(tracked_bands),len(set(tracked_bands)))
        return set(tracked_bands)

if __name__ == '__main__':
    d =SpotifyIntegration('1214002279')
    e = d()
    playlists = next(e)
    e.send(playlists)
