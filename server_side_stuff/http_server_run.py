from __future__ import print_function

from http import server
import socketserver
from os import getcwd,fchdir
import os

from spotipy import oauth2,SpotifyException
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs


import json

class CLAHandler(server.SimpleHTTPRequestHandler):

    def do_GET(self):
        rootdir = '/home/themagicalplace/PycharmProjects/ConcertLoactor/server_side_stuff'  # file location



        query = urlparse(self.path).query
        link = urlparse(self.path).path

        access_token = None
        print(query,self.path)
        if self.path.endswith('spotify_auth_link.json'):

            self.json_get(sp_oauth.get_authorize_url())
        elif link.endswith('access_token.json'):
            query_components = dict(qc.split("=") for qc in query.split("&"))
            code = query_components['code']
            self.json_get(sp_oauth.get_access_token(code))

        elif (urlparse(self.path).path).endswith('.html'):
            with open(rootdir + link) as auth_url:  # open requested file

                # send code 200 response
                self.send_response(200)

                # send header first
                self.send_header('Content-type', 'text-html')
                self.end_headers()
                # send file content to client
                self.wfile.write(bytes(auth_url.read(), "utf-8"))
        else:
            self.send_response(404)

    def json_get(self,json_file):
        self.send_response(200)

        # send header first
        self.send_header('Content-type', 'application-json')
        self.end_headers()

        # send file content to client
        self.wfile.write(bytes(json.dumps(json_file), "utf-8"))
        return


def run():

    global sp_oauth
    # ip and port of server
    # by default http server port is 80
    server_address = ('10.0.0.187', 8085)
    httpd = server.HTTPServer(server_address, CLAHandler)

    print('http server is running...')
    httpd.serve_forever()

if __name__ == '__main__':
    handler = server.SimpleHTTPRequestHandler
    PORT = 8085
    redirect_uri = "http://10.0.0.187:8085/index.html"
    redirect_uri = 'http://localhost:8080/index.html'
    client_id = os.getenv('SPOTIPY_CLIENT_ID') or 'ce4091c720c04087ad60ed054ffd9760'
    client_secret = os.getenv('SPOTIPY_CLIENT_SECRET') or 'c1710a69f80c405d9ecad0eb1c6f548d'
    sp_oauth = oauth2.SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri,
                                   scope='playlist-read-private', cache_path=".cache-user-token")
    run()

