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


class template(object):
    """Class used by qBittorrent to search for torrents"""

    url = 'http://example.org'
    name = 'template'
    # defines which search categories are supported by this search engine
    # and their corresponding id. Possible categories are:
    # 'all', 'movies', 'tv', 'music', 'games', 'anime', 'software', 'pictures',
    # 'books'
    supported_categories = {
            'software': 0}

    class LinuxSearchParser(HTMLParser):
        """ Parses Template browse page for search results and prints them"""
        def __init__(self, res, url):
            try:
                super().__init__()
            except:
                # See: http://stackoverflow.com/questions/9698614/
                HTMLParser.__init__(self)
            self.results = res
            self.engine_url = url
            self.curr = None
            self.strong_count = 0
            self.wait_for_data = True

        def handle_starttag(self, tag, attr):
            """Tell the parser what to do with which tags"""

    def __init__(self):
        """class initialization"""

    #  def download_torrent(self, info):
        #  """Retrieve and save url as a temporary file."""

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

        # url = str("self.url/page?parameter=value&query={}".format(what))
        #
        #  hits = []
        #  page = 1
        #  parser = self.LinuxSearchParser(hits, url)
        #  while True:
            #  res = retrieve_url(url + "&pages={}".format(page))
            #  parser.feed(res)
            #  for each in hits:
                #  prettyPrinter(each)

            #  if len(hits) < 15:
                #  break
            #  del hits[:]
            #  page += 1

        #  parser.close()
