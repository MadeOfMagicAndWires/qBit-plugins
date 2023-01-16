# -*- coding: utf-8 -*-
#VERSION: 1.4
#AUTHORS: Joost Bremmer (toost.b@gmail.com)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import datetime
import os
import tempfile

try:
    import urllib2 as request
    from urllib import urlencode
    from cookielib import CookieJar
    from HTMLParser import HTMLParser
except ImportError:
    import urllib.request as request
    from urllib.parse import urlencode
    from http.cookiejar import CookieJar
    from html.parser import HTMLParser

# import qBT modules
try:
    from novaprinter import prettyPrinter
    from helpers import htmlentitydecode
except:
    pass


class bakabt(object):
    """Class used by qBittorrent to search bakabt.me for torrents

    It is important to replace the username and password values with your
    personal login information. Without this, this plugin will *not* work.
    """

    # Login information ######################################################
    #
    # SET THESE VALUES!!
    #
    username = "username"
    password = "password"
    ###########################################################################

    url = 'https://bakabt.me'
    name = 'BakaBT'
    # defines which search categories are supported by this search engine
    # and their corresponding id. Possible categories are:
    # 'all', 'movies', 'tv', 'music', 'games', 'anime', 'software', 'pictures',
    # 'books'
    supported_categories = {
            'all': [1, 2, 3, 4, 5, 6, 7, 8, 9],
            'anime': [1, 2],  # Anime Series and OVA
            'music': [3, 8],  # Soundtracks and Music Video
            'books': [4, 9],  # Manga and Light Novel
            'movies': [5],    # Anime Movie
            'tv': [6],        # Live Action
            'pictures': [7]}  # Artbooks

    class BakaDownloadParser(HTMLParser):
        """Parses BakaBT torrent page for download link"""
        def __init__(self):
            try:
                super().__init__()
            except:
                # See: http://stackoverflow.com/questions/9698614/
                HTMLParser.__init__(self)
            self.download = None

        def handle_starttag(self, tag, attr):
            if tag == 'a':
                self.start_a(attr)

        def start_a(self, attr):
            params = dict(attr)
            if 'class' in params and params['class'] == 'download_link':
                self.download = params['href']

    class BakaSearchParser(HTMLParser):
        """ Parses BakaBT browse page for search results and prints them"""
        def __init__(self, res, url):
            try:
                super().__init__()
            except:
                # See: http://stackoverflow.com/questions/9698614/
                HTMLParser.__init__(self)
            self.download = None
            self.results = res
            self.engine_url = url
            self.curr = None
            self.wait_for_title = False
            self.wait_for_date = False
            self.wait_for_size = False
            self.wait_for_seeds = False
            self.wait_for_peers = False

        def handle_starttag(self, tag, attr):
            if tag == 'a':
                self.start_a(attr)
            elif tag == 'td':
                self.start_td(attr)

        def start_a(self, attr):
            params = dict(attr)
            if 'class' in params and 'title' in params['class']:
                hit = {
                        'link': self.engine_url + '/' + params['href'],
                        'desc_link': self.engine_url + '/' + params['href']}
                self.curr = hit
                self.wait_for_title = True
            elif 'style' in params and params['style'] == "color: #00cc00":
                self.wait_for_seeds = True
            elif self.curr is not None and 'seeds' in self.curr:
                self.wait_for_peers = True

        def start_td(self, attr):
            params = dict(attr)
            if 'class' in params and self.curr is not None:
                if params['class'] == 'added':
                    pass
                    #  self.wait_for_date = True
                elif params['class'] == 'size':
                    self.wait_for_size = True

        def handle_data(self, data):
            if self.wait_for_title:
                self.curr['name'] = data.strip()
                self.wait_for_title = False
            elif self.wait_for_date:
                try:
                    date = datetime.datetime.strptime(data.strip(),
                                                      "%d %b '%y")
                except ValueError:
                    date = datetime.datetime.now()
                self.curr['date'] = date.strftime("%Y-%m-%d")
                self.wait_for_date = False
            elif self.wait_for_size:
                self.curr['size'] = data.strip()
                self.wait_for_size = False
            elif self.wait_for_seeds:
                self.curr['seeds'] = int(data.strip())
                self.wait_for_seeds = False
            elif self.wait_for_peers:
                self.curr['leech'] = int(data.strip())
                self.curr['engine_url'] = self.engine_url
                prettyPrinter(self.curr)
                self.results.append(self.curr)
                self.curr = None
                self.wait_for_peers = False

    def __init__(self):
        """class initialization, requires personal login information"""

        self.ua = \
            'Mozilla/5.0 (X11; Linux i686; rv:38.0) ' + \
            'Gecko/20100101 Firefox/38.0'
        self.sesh = None

        self._login(self.username, self.password)

    def _login(self, username, password):
        """Initiate a session and log into BakaBT"""

        # Build opener
        cj = CookieJar()
        params = {
                'username': self.username,
                'password': self.password,
                'returnto': 'browse.php'}
        sesh = request.build_opener(request.HTTPCookieProcessor(cj))

        # change user-agent
        sesh.addheaders.pop()
        sesh.addheaders.append(('User-Agent', self.ua))

        # send request
        try:
            sesh.open(
                    self.url + '/splash.php',
                    urlencode(params).encode('utf-8'))
            self.sesh = sesh
        except request.URLError as errorno:
            print("Connection Error: {}".format(errorno.reason))

    def _retreive_url(self, url):
        """Return the HTML content of url page as a string """
        try:
            res = self.sesh.open(url)
        except request.URLError as errorno:
            print("Connection Error: {}".format(errorno.reason))
            return ""

        charset = 'utf-8'
        info = res.info()
        try:
            _, charset = info['Content-Type'].split('charset=')
        except:
            pass
        dat = res.read()
        dat = dat.decode(charset, 'replace')

        dat = htmlentitydecode(dat)
        return dat

    def download_torrent(self, info):
        """Retrieve and save url as a temporary file."""
        file, path = tempfile.mkstemp()
        url = info

        parser = self.BakaDownloadParser()
        res = self._retreive_url(url)
        parser.feed(res)
        download = self.url + '/' + parser.download
        parser.close()

        torrent = self.sesh.open(download)
        with os.fdopen(file, "wb") as f:
            f.write(torrent.read())
        f.close()
        # Print file path and url.
        print(path+" "+download)
        parser.close()

    # DO NOT CHANGE the name and parameters of this function
    # This function will be the one called by nova2.py
    def search(self, what, cat='all'):
        """
        Retreive and parse all BakaBT search results by category and query.

        Parameters:
        :param what: a string with the search tokens, already escaped
                     (e.g. "Ubuntu+Linux")
        :param cat:  the name of a search category, see supported_categories.
        """
        url = "{}/browse.php?limit=100&ordertype=seeders&q={}".format(self.url, what)
        if cat in self.supported_categories:
            url += "&reorder=1"
            for i in self.supported_categories[cat]:
                url += "&c{}=1".format(i)

        hits = []
        parser = self.BakaSearchParser(hits, self.url)
        i = 0
        while True:
            res = self._retreive_url(url + "&page={}".format(i))
            parser.feed(res)
            if len(hits) < 100:
                break
            del hits[:]
            i += 1
        parser.close()
