# -*- coding: utf-8 -*-
#VERSION: 1.0
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


try:
    from HTMLParser import HTMLParser
except ImportError:
    from html.parser import HTMLParser

# import qBT modules
try:
    from novaprinter import prettyPrinter
    from helpers import retrieve_url
except:
    pass


class skytorrents(object):
    """Class used by qBittorrent to search for torrents"""

    url = 'https://skytorrents.in'
    name = 'Sky Torrents'
    # defines which search categories are supported by this search engine
    # and their corresponding id. Possible categories are:
    # 'all', 'movies', 'tv', 'music', 'games', 'anime', 'software', 'pictures',
    # 'books'
    supported_categories = {'all': 'all'}

    class SkySearchParser(HTMLParser):
        """ Parses Template browse page for search results and prints them"""
        def __init__(self, res=[], url="https://skytorrents.in"):
            try:
                super().__init__()
            except:
                # See: http://stackoverflow.com/questions/9698614/
                HTMLParser.__init__(self)
            self.results = res
            self.engine_url = url
            self.curr = None
            self.td_counter = -1

        def handle_starttag(self, tag, attr):
            """Tell the parser what to do with which tags"""
            if tag == 'a':
                self.handle_a(attr)

        def handle_endtag(self, tag):
            if tag == 'td':
                self.handle_td()

        def handle_a(self, attr):
            params = dict(attr)
            if 'href' in params and params['href'].startswith('/info'):
                hit = {'desc_link': self.engine_url + params['href'],
                       'engine_url': self.engine_url,
                       'name': params['title']}
                if not self.curr:
                    self.curr = hit
            elif 'href' in params and params['href'].startswith('magnet:?'):
                self.curr['link'] = params['href']
                self.td_counter += 1

        def handle_td(self):
            if self.td_counter >= 0:
                self.td_counter += 1

            # we've caught all info, add it to the results
            # then reset the counters for the next result
            if self.td_counter > 5:
                self.results.append(self.curr)
                self.curr = None
                self.td_counter = -1

        def handle_data(self, data):
            # Catch size
            if self.td_counter == 1:
                self.curr['size'] = data.strip()
            # Catch seeds
            elif self.td_counter == 4:
                try:
                    self.curr['seeds'] = int(data.strip())
                except:
                    self.curr['seeds'] = -1
            # Catch peers
            elif self.td_counter == 5:
                try:
                    self.curr['leech'] = int(data.strip())
                except:
                    self.curr['leech'] = -1

    # DO NOT CHANGE the name and parameters of this function
    # This function will be the one called by nova2.py
    def search(self, what, cat='all'):
        """
        Retreive and parse engine search results by category and query.

        Parameters:
        :param what: a string with the search tokens, already escaped
                     (e.g. "Ubuntu+Linux")
        :param cat:  the name of a search category, see supported_categories.
        """

        hits = []
        page = 1
        parser = self.SkySearchParser(hits, self.url)
        while True:
            url = str(
                "{site}/search/{cat}/ed/{page}/?q={query}"
                .format(site=self.url,
                        cat=cat,
                        page=page,
                        query=what))
            res = retrieve_url(url)
            parser.feed(res)
            for each in hits:
                prettyPrinter(each)

            # SkyTorrents serves max 25 pages of 40 results,
            # Any further requests get redirected to the 1st
            if len(hits) >= 1000:
                break
            page += 1

        parser.close()
