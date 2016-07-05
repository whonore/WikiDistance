import argparse
import csv
import logging
import re
import sys
try:
    import urllib.request as urls
except ImportError:
    import urllib2 as urls
from bs4 import BeautifulSoup


INF = float('inf')


class WikiCrawler(object):
    WIKI_URL = 'https://en.wikipedia.org/wiki/'

    TITLE_RE = re.compile(r'(.+) - Wikipedia')

    BAD_LINKS = ('Book', 'Help', 'Wikipedia', 'File', 'Special')
    LINK_RE = re.compile(r"/wiki/(?!{}:)".format('|'.join(BAD_LINKS)))

    BAD_PARENTS = ('div', 'span', 'table', 'b', 'i')

    def __init__(self, topic='Special:Random'):
        url = self.WIKI_URL + topic
        self.page = BeautifulSoup(urls.urlopen(url), 'html.parser')
        self.title = self.TITLE_RE.match(self.page.title.text).group(1)
        self.content = self.page.find(id='mw-content-text')

    def get_first_link(self):
        link = self.content.find(self.is_valid)

        if link is None:
            logging.info("No link found on %s", self.title)
            return None
        else:
            return link['href'].split('/')[2]

    def is_valid(self, tag):
        if tag.name != 'a':
            return False

        if not re.match(self.LINK_RE, tag['href']):
            return False

        for parent in tag.parents:
            if parent.get('id') == 'mw-content-text':
                break

            if parent.name in self.BAD_PARENTS:
                return False

        if in_parens(str(self.content), str(tag)):
            return False

        return True


def compute_distance(dists, topic=None):
    '''Finds the "distance" to the Philosophy page by following the first
       valid link. Also stores the next page in the chain.
    '''
    if topic is None:
        page = WikiCrawler()
    else:
        page = WikiCrawler(topic)

    title = page.title
    logging.info(title)

    if title not in dists:
        dists[title] = ('Unknown', INF)  # Needed to catch loops

        link = page.get_first_link()

        if link is None:                # No links found
            dists[title] = ('NULL', INF)
        else:
            next_, dist = compute_distance(dists, link)

            if dist == INF:
                logging.info("Loop found from %s to %s", title, next_)

            dists[title] = (next_, dist + 1)

    return (title, dists[title][1])


def in_parens(text, target):
    if '(' not in text or ')' not in text:
        return False

    open = 1
    contained = []

    start = text.find('(')
    end = text.rfind(')')
    for c in text[start + 1:end]:
        if c == '(':
            open += 1
        elif c == ')':
            open -= 1
        elif open > 0:
            contained.append(c)

    return target in ''.join(contained)


def load_dists():
    '''Loads the csv file into a dictionary.'''
    if sys.version_info.major < 3:
        kwargs = {'mode': 'rb'} 
    else:
        kwargs = {'mode': 'r', 'newline': ''}
    
    dists = {'Philosophy': ('NONE', 0)}
    
    try:
        with open('wikidist.csv', **kwargs) as in_f:
            reader = csv.reader(in_f)
            next(reader)

            for title, next_, dist in reader:
                if dist == 'inf':
                    dists[title] = (next_, float(dist))
                else:
                    dists[title] = (next_, int(dist))
    except IOError:
        pass

    return dists


def write_dists(dists):
    '''Writes the dictionary back to the csv file.'''
    if sys.version_info.major < 3:
        kwargs = {'mode': 'wb'} 
    else:
        kwargs = {'mode': 'w', 'newline': ''}
    
    with open('wikidist.csv', **kwargs) as out_f:
        writer = csv.writer(out_f)
        writer.writerow(['Title', 'Next', 'Dist'])

        for title, (next_, dist) in dists.items():
            writer.writerow([title, next_, dist])


def main(iters, start):
    dists = load_dists()

    for i in range(iters):
        logging.info('Starting from a random article')
        compute_distance(dists, start)

    write_dists(dists)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--iters', type=int, default=10)
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-s', '--start', default=None)

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO if args.verbose else logging.ERROR)
    main(args.iters, args.start)
