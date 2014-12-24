import urllib.request
import re
import sys

wikiURL = "https://en.wikipedia.org/wiki/{}"

def fetchPage(topic="Special:Random"):
    url = wikiURL.format(topic)
    page = urllib.request.urlopen(url)
    source = str(page.read())[2:-1]

    return source

def getTitle(source):
    titleRe = re.compile(".*<title>(.*) - Wikipedia, the free encyclopedia</title>.*")
    return titleRe.match(source).group(1)

print(getTitle(fetchPage()))