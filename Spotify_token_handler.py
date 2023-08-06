""""The code used in this is almost all from https://github.com/plamere/spotipy, and
has only been broken up like this such as to minimize the number of times
the server is accessed"""

from __future__ import print_function

import json
import os
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

import requests
import spotipy

REDIRECT_URI = 'http://localhost:8080/index.html'
PORT = 8080


class SpotifyTokenCheck:
    cache_path = os.path.join('userdata','.cache-user-token')
    def __init__(self):
        self.token_info = None

    def get_cached_token(self,scope):
        ''' Gets a cached auth token
        '''

        if self.cache_path:
            try:
                with open(self.cache_path,'r') as cache:
                    self.token_info = json.load(cache)
                # if scopes don't match, then bail
                if 'scope' not in self.token_info.keys() or not self._is_scope_subset(scope, self.token_info['scope']):
                    return 'Invalid Scope'
                if self._is_token_expired(self.token_info):
                    return 'Token is Expired'
            except FileNotFoundError:
                return 'Token Info not found'
        return self.token_info

    def _is_token_expired(self, token_info):
        now = int(time.time())
        return token_info['expires_at'] < now

    def _is_scope_subset(self, needle_scope, haystack_scope):
        needle_scope = set(needle_scope.split())
        haystack_scope = set(haystack_scope.split())

        return needle_scope <= haystack_scope

def get_authentication_code():
    """
    Create a temporary http server and get authentication code.
    As soon as a request is received, the server is closed.
    :return: the authentication code
    """
    httpd = MicroServer((REDIRECT_URI.split("://")[1].split(":")[0], PORT), CustomHandler)
    # stop the server once a request is received
    while not httpd.latest_query_components:
        httpd.handle_request()
    httpd.server_close()
    if "error" in httpd.latest_query_components:
        if httpd.latest_query_components["error"][0] == "access_denied":
            raise spotipy.SpotifyException(200, -1, 'The user rejected Spotify access')
        else:
            raise spotipy.SpotifyException(200, -1, 'Unknown error from Spotify authentication server: {}'.format(
                httpd.latest_query_components["error"][0]))
    if "code" in httpd.latest_query_components:
        code = httpd.latest_query_components["code"][0]
    else:
        raise spotipy.SpotifyException(200, -1, 'Unknown response from Spotify authentication server: {}'.format(
            httpd.latest_query_components))
    return code

class CustomHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.server.latest_query_components = parse_qs(urlparse(self.path).query)
        with open(os.getcwd()+'/server_side_stuff/index.html') as red_link:
            self.wfile.write(bytes(red_link.read(),'utf-8'))

class MicroServer(HTTPServer):
    def __init__(self, server_address, RequestHandlerClass):
        self.latest_query_components = None
        super().__init__(server_address, RequestHandlerClass)

def spotify_get_token(scope):
    token = SpotifyTokenCheck().get_cached_token(scope)
    if token == 'Invalid Scope':
        pass # this should never happen
    elif token == 'Token is Expired' or token =='Token Info not found':
        res = requests.get('http://73.18.119.167:8080/spotify_auth_link.json',timeout=10)
        try:

            webbrowser.open(res.json())
            code = get_authentication_code()
            token_info = requests.get('http://73.18.119.167:8080/access_token.json',params={'code':code})
            tkinfo = token_info.json()
            einfo = token_info.text
            with open('userdata\\.cache-user-token','w') as cache:
                json.dump(tkinfo,cache)
                return tkinfo['access_token']
        except requests.exceptions.ConnectionError as exc:
            return exc
    else:
        print('Valid Token Found!')
        return token



if __name__ == '__main__':
    spotify_get_token('playlist-read-private')