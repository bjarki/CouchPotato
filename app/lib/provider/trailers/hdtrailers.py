from app.lib.provider.rss import rss
from imdb.parser.http.bsouplxml._bsoup import SoupStrainer, BeautifulSoup
from string import letters, digits
from urllib2 import URLError
import logging
import re
import urllib2

log = logging.getLogger(__name__)

class HdTrailers(rss):

    apiUrl = 'http://www.hd-trailers.net/movie/%s/'
    backupUrl = 'http://www.hd-trailers.net/AllTrailers/'
    providers = ['apple', 'yahoo', 'moviefone']

    def __init__(self, config):
        self.config = config

    def conf(self, value):
        return self.config.get('Trailer', value)

    def find(self, movie):

        url = self.apiUrl % self.movieUrlName(movie.name)
        log.info('Searching %s', url)

        try:
            data = urllib2.urlopen(url, timeout = self.timeout).read()
        except (IOError, URLError):
            log.error('Failed to open %s.' % url)
            return []

        for provider in self.providers:
            results = self.findByProvider(data, provider)
            if results:
                return results

        return results

    def findByProvider(self, data, provider):

        try:
            tables = SoupStrainer('table')
            html = BeautifulSoup(data, parseOnlyThese = tables)
            resultTable = html.find('table', attrs = {'class':'bottomTable'})

            results = {'480p':[], '720p':[], '1080p':[]}
            for tr in resultTable.findAll('tr'):
                trtext = str(tr).lower()
                if 'clips' in trtext:
                    break
                if 'trailer' in trtext and not 'clip' in trtext and provider in trtext:
                    nr = 0
                    resolutions = tr.findAll('td', attrs = {'class':'bottomTableResolution'})
                    #sizes = tr.findNext('tr').findAll('td', attrs = {'class':'bottomTableFileSize'})
                    for res in resolutions:
                        results[str(res.a.contents[0])].append(res.a['href'])
                        #int(sizes[nr].contents[0].replace('MB', ''))
                        nr += 1

            return results

        except AttributeError:
            log.debug('No trailers found in provider %s.' % provider)

        return []

    def movieUrlName(self, string):
        safe_chars = letters + digits + ' '
        r = ''.join([char if char in safe_chars else ' ' for char in string])
        return re.sub('\s+' , '-', r).lower()
