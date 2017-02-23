# -*- coding: utf-8 -*-
# VERSION: 0.50
# AUTHORS: Joost Bremmer (toost.b@gmail.com)
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

try:
    import urllib2 as request
    from urllib import urlencode
    from cookielib import CookieJar
    from HTMLParser import HTMLParser
    import htmlentitydefs,re
    chr = unichr
except ImportError:
    import urllib.request as request
    from urllib.parse import urlencode
    from http.cookiejar import CookieJar
    from html.parser import HTMLParser
    import html.entities as htmlentitydefs
    import re

# import qBT modules
#  from novaprinter import prettyPrinter
#  from helpers import htmlentitydefs

class BakaBT(object):
    url = 'https://bakabt.me'
    name = 'BakaBT'
    # Which search categories are supported by this search engine and their corresponding id
    # Possible categories are ('all', 'movies', 'tv', 'music', 'games', 'anime', 'software', 'pictures', 'books')
    supported_categories = {
            'all': 0,
            'anime': 1,
            'music': 3,
            'books': 4,     # Manga
            'movies': 5,
            'tv': 6,        # Live Action
            'pictures': 7}  # Artbooks

    def __init__(self):
        """class initialization, requires personal login information"""
        # SET THESE VALUES!!
        self.username = "username"
        self.password = "password"

        # Leave these values alone
        self.useragent = \
                'Mozilla/5.0 (X11; Linux i686; rv:38.0) Gecko/20100101 Firefox/38.0'
        self.sesh = None

        self._login(self.username, self.password)

    def _login(self, username, password):
        """Initiate a session and log into BakaBT"""

        # Build opener
        cj = CookieJar()
        params = {
                'username' : self.username,
                'password': self.password,
                'returnto': 'browse.php'}
        sesh = request.build_opener(request.HTTPCookieProcessor(cj))

        # change user-agent
        sesh.addheaders.pop()
        sesh.addheaders.append(('User-Agent', self.useragent))


        # send request
        try:
            res = sesh.open(
                    self.url + '/login.php',
                    urlencode(params).encode('utf-8'))
            self.sesh = sesh
        except request.URLError as errorno:
            print("Connection Error: {}".format(errorno.reason))


    def _retreive_url(self, url):
        """Return the content of the url page as a string """
        try:
            res = self.sesh.open(url)
        except request.URLError as errorno:
            print("Connection Error: {}".format(errorno.reason))
            return ""

        charset = 'utf-8'
        try:
           _, charset = info['Content-Type'].split('charset=')
        except:
           pass
        dat = res.read()
        dat = dat.decode(charset, 'replace')
        info = res.info()
        charset = 'utf-8'

        def htmlentitydecode(s):
            """convert all HTML entities to unicode readable characters """
            # First convert alpha entities (such as &eacute;)
            # (Inspired from http://mail.python.org/pipermail/python-list/2007-June/443813.html)
            def entity2char(m):
                entity = m.group(1)
                if entity in htmlentitydefs.name2codepoint:
                     return chr(htmlentitydefs.name2codepoint[entity])
                return u" "  # Unknown entity: We replace with a space.
            t = re.sub(u'&(%s);' % u'|'.join(htmlentitydefs.name2codepoint), entity2char, s)

            # Then convert numerical entities (such as &#233;)
            t = re.sub(u'&#(\d+);', lambda x: chr(int(x.group(1))), t)

            # Then convert hexa entities (such as &#x00E9;)
            return re.sub(u'&#x(\w+);', lambda x: chr(int(x.group(1),16)), t)

        dat = htmlentitydecode(dat)
        return dat

    def download_torrent(self, info):
        """
        Providing this function is optional. It can however be interesting to provide
        your own torrent download implementation in case the search engine in question
        does not allow traditional downloads (for example, cookie-based download)
        """
        print(download_file(info))

    class BakaParser(HTMLParser):
        """ Parse BakaBT browse page for search results """
        def __init__(self, res, url):
            super().__init__()
            self.results = res
            self.url = url
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
                hit = { 'url' : self.url + '/' + params['href']}
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
                    self.wait_for_date = True
                elif params['class'] == 'size':
                    self.wait_for_size = True

        def handle_data(self, data):
            if self.wait_for_title:
                self.curr['name'] = data.strip()
                self.wait_for_title = False
            elif self.wait_for_date:
                try:
                    date = datetime.datetime.strptime(data.strip(), "%d %b '%y")
                except ValueError:
                    date = datetime.datetime.now()
                self.curr['date'] = date.strftime("%Y-%m-%d")
                self.wait_for_date = False
            elif self.wait_for_size:
                self.curr['size'] = data
                self.wait_for_size = False
            elif self.wait_for_seeds:
                self.curr['seeds'] = data
                self.wait_for_seeds = False
            elif self.wait_for_peers:
                self.curr['leechers'] = data
                self.curr['engine_url'] = "bakabt.me"
                self.results.append(self.curr)
                self.curr = None
                self.wait_for_peers = False
            #  print(self.results)
    # DO NOT CHANGE the name and parameters of this function
    # This function will be the one called by nova2.py
    def search(self, what, cat='all'):
        # what is a string with the search tokens, already escaped (e.g. "Ubuntu+Linux")
        # cat is the name of a search category in ('all', 'movies', 'tv', 'music', 'games', 'anime', 'software', 'pictures', 'books')
        #
        # Here you can do what you want to get the result from the
        # search engine website.
        # everytime you parse a result line, store it in a dictionary
        # and call the prettyPrint(your_dict) function
        if cat in self.supported_categories:
            url = "{0}/browse.php?limit=100&ordertype=seeders&q={1}&cat={2}"\
                    .format(
                            self.url,
                            what,
                            self.supported_categories[cat])
        else:
            url = "{0}/browse.php?limit=100&ordertype=seeders&q={1}"\
                    .format(self.url, what)

        hits = []
        parser = self.BakaParser(hits, self.url)
        i = 0
        while i < 100:
            res = self._retreive_url(url + "&page={}".format(i))
            #  print(res)
            parser.feed(res)
            if len(hits) <= 0:
                break
            # Pretty print here
            print(hits)
            print(len(hits))
            del hits[:]
            i += 1
        parser.close()
test = BakaBT()
test.search('test', 'all')
