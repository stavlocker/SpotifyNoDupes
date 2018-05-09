import spotipy
import os
import spotipy.util as util
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

os.environ["SPOTIPY_CLIENT_ID"] = ""
os.environ["SPOTIPY_CLIENT_SECRET"] = ""
SERVER_PORT = 14523
os.environ["SPOTIPY_REDIRECT_URI"] = "http://localhost:{}".format(SERVER_PORT)

scope = 'user-library-read playlist-read-private playlist-read-collaborative playlist-modify-public playlist-modify-private'


class FailedAuth(BaseException):
    """Failed authentication for spotify"""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class NotFound(BaseException):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class MyHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write('<html><body><h1 style="text-align:center">Great! Now go back to the python program and insert the URL of this page:</h1><button onclick="copy()" style="margin: 0 auto;display:block">Copy to clipboard</button><textarea id="textarea" style="display: block; margin: 0 auto; width: 60%"></textarea><script>var txt = document.getElementById("textarea"); txt.value = window.location.href;txt.select();function copy() {txt.select();document.execCommand("copy");}</script></body></html>'.encode('utf-8'))

    def log_message(self, format, *args):
        return


class StoppableSilentHTTPServer(HTTPServer):
    stopped = False

    def __init__(self, *args, **kw):
        HTTPServer.__init__(self, *args, **kw)

    def serve_forever(self):
        while not self.stopped:
            self.handle_request()

    def force_stop(self):
        self.stopped = True
        self.server_close()


class SpotifyAuth:
    def __init__(self, username):
        self._username = username
        self._sp = None

    def wait_for_auth(self):
        self.httpd = StoppableSilentHTTPServer(('', SERVER_PORT), MyHTTPHandler)
        Thread(target=self.httpd.serve_forever).start()
        token = util.prompt_for_user_token(self._username, scope)

        if token:
            self._sp = spotipy.Spotify(auth=token)
        else:
            raise FailedAuth

    def get_spotify(self):
        return self._sp

    def stop_server(self):
        self.httpd.force_stop()


def __list_add_tracks__(list_object, tracks):
    for item in tracks["items"]:
        track = item["track"]
        if track["id"] is not None:
            list_object.append(track["id"])
    return list_object


def __add_playlist__(playlist_list, playlists):
    for item in playlists["items"]:
        playlist_list.append(item)
    return playlist_list


def __chunk_list__(data, size):
    return [data[x:x + size] for x in range(0, len(data), size)]


class SpotifyTool:
    def __init__(self, username, sp):
        self._username = username
        self._sp = sp
        self._playlist = None

    def set_playlist_by_id(self, playlist_id):
        try:
            self._playlist = self._sp.user_playlist(self._username, playlist_id)
        except BaseException:
            raise NotFound("No playlist found")

        if self._playlist is None:
            raise NotFound("No playlist found")

    def set_playlist_by_name(self, name):
        self._playlist = self.__find_playlist__(name)

        if self._playlist is None:
            raise NotFound("No playlist found")

    def __find_playlist__(self, name):
        playlists = self._sp.user_playlists(self._username)

        for item in playlists["items"]:
            if item["name"] == name:
                return item
        return None

    def get_playlist_tracks(self):
        results = self._sp.user_playlist_tracks(self._username, self._playlist['id'])
        tracks = results['items']
        while results['next']:
            results = self._sp.next(results)
            tracks.extend(results['items'])
        return tracks

    def remove_track_by_id(self, id):
        self._sp.user_playlist_remove_all_occurrences_of_tracks(self._username, self._playlist['id'], [id])

    def get_all_playlists(self):
        playlist_list = []

        playlists = self._sp.user_playlists(self._username)
        __add_playlist__(playlist_list, playlists)

        while playlists["next"]:
            playlists = self._sp.next(playlists)
            __add_playlist__(playlist_list, playlists)
        return playlist_list
