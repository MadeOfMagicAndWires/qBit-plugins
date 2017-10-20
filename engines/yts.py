#VERSION: 1.02
#AUTHORS: Bruno Barbieri (brunorex@gmail.com)

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the author nor the names of its contributors may be
#      used to endorse or promote products derived from this software without
#      specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


from novaprinter import prettyPrinter
from helpers import retrieve_url, download_file
try:
    from HTMLParser import HTMLParser
except ImportError:
    from html.parser import HTMLParser


class yts(object):
    url = 'http://yts.ag'
    name = 'YTS'
    supported_categories = {'all': ''}

    def download_torrent(self, info):
        print(download_file(info))

    class SimpleHTMLParser(HTMLParser):

        def __init__(self, results, url, index, pages_left):
            HTMLParser.__init__(self)
            self.current_item = None
            self.results = results
            self.has_results = False
            self.url = url
            self.index = index
            self.pages_left = pages_left

            self.div_found = False
            self.a_name_found = False
            self.data_counter = 0
            self.span_counter = 0
            self.last_pag_nav = []

            self.start_dispatcher = {'a': self.start_a,
                                     'div': self.start_div,
                                     'span': self.start_span}

            self.end_dispatcher = {'a': self.end_a,
                                   'span': self.end_span}

        def handle_starttag(self, tag, attrs):
            if tag in self.start_dispatcher:
                self.start_dispatcher[tag](attrs)

        def handle_endtag(self, tag):
            if tag in self.end_dispatcher:
                self.end_dispatcher[tag]()

        def start_a(self, attrs):
            params = dict(attrs)
            if 'href' in params and self.div_found:
                if (not self.a_name_found and
                        params['href'].startswith(self.url + '/movie/')):
                    self.current_item['desc_link'] = params['href']
                    self.data_counter += 1
                    self.a_name_found = True
                elif params['href'].startswith(self.url + '/download/start/'):
                    # Download link found
                    self.current_item['link'] = params['href']
                    self.current_item['link']
                    self.data_counter += 1
            elif ('href' in params and
                  len(self.pages_left) > 0 and
                  self.data_counter < 1):
                if '/All/All/0/seeds/' in params['href']:
                    pgnum = params['href'].split(
                        '/All/All/0/seeds/')[1].strip()
                    if pgnum.isdigit():
                        self.last_pag_nav.append(self.get_num(pgnum))
                        self.last_pag_nav.sort()

        def start_div(self, attrs):
            params = dict(attrs)
            if ('class' in params and
                    not self.div_found and
                    params['class'].strip().startswith('pagination')):
                # Detect if there's more than one result page since
                # the search will work with any number at the end of the URL
                if not self.has_results:
                    self.pages_left.append('p')
            elif ('class' in params and
                  params['class'].strip().startswith('browse-info')):
                self.current_item = {}
                self.data_counter = 0
                self.span_counter = 0
                self.a_name_found = False
                self.div_found = True
                self.has_results = False

        def start_span(self, attrs):
            params = dict(attrs)
            if self.data_counter == 2:
                self.span_counter += 1
            elif self.span_counter == 1 and 'class' in params:
                if params['class'].strip().startswith('peers'):
                    self.span_counter += 1
            elif self.span_counter == 2 and 'class' in params:
                if params['class'].strip().startswith('seeds'):
                    self.span_counter += 1

        def end_a(self):
            # Description link found
            if self.a_name_found and self.data_counter < 2:
                self.data_counter += 1

        def end_span(self):
            # Size found
            if self.span_counter == 1 and self.data_counter == 2:
                self.data_counter += 1
            # Leechers found
            elif self.span_counter == 2 and self.data_counter == 3:
                self.data_counter += 1
            # Seeders found
            elif self.span_counter == 3 and self.data_counter == 4:
                self.data_counter += 1

        def handle_data(self, data):
            if self.a_name_found and self.data_counter < 2:
                if 'name' not in self.current_item:
                    self.current_item['name'] = ''
                self.current_item['name'] += data
            elif self.span_counter == 1 and self.data_counter < 3:
                self.current_item['size'] = data.strip()
            elif self.span_counter == 2 and self.data_counter < 4:
                self.current_item['leech'] = data.strip()
            elif self.span_counter == 3 and self.data_counter < 5:
                self.current_item['seeds'] = data.strip()
            elif self.data_counter == 6 and not self.has_results:
                self.div_found = False
                self.current_item['engine_url'] = self.url
                prettyPrinter(self.current_item)
                self.has_results = True
                self.results.append('a')
                if (len(self.pages_left) > 0 and
                        self.index > self.last_pag_nav[-1]):
                    # Don't go beyond the last page
                    del self.pages_left[:]
                    del self.results[:]

        def handle_charref(self, ref):
            self.handle_entityref("#" + ref)

        def handle_entityref(self, ref):
            self.handle_data(self.unescape("&%s;" % ref))

        def get_num(self, x):
            return int(''.join(ele for ele in x if ele.isdigit()))

    def __init__(self):
        self.results = []
        self.pages_left = []
        self.index = 0
        self.parser = self.SimpleHTMLParser(self.results,
                                            self.url,
                                            self.index,
                                            self.pages_left)

    def search(self, what, cat='all'):
        i = 0
        while True and i < 11:
            results = []
            pages_left = []
            index = i + 1
            parser = self.SimpleHTMLParser(results,
                                           self.url,
                                           index,
                                           pages_left)
            what = what.replace('%2B', '+')
            search_url = self.url + \
                '/browse-movies/%s/all/all/0/seeds/%s' % (what, index)
            dat = retrieve_url(search_url)
            print(search_url);
            parser.feed(dat)
            parser.close()
            if len(results) <= 0 or len(pages_left) <= 0:
                break
            i += 1
