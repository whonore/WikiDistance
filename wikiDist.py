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

def getFirstLink(source):
    linkRe = re.compile(".*<a href=\"/wiki/(.+)\" title.*")
    contentStart = source.find("mw-content-text")
    pStart = source[contentStart:-1].find("<p>") + contentStart
    aStart = source[pStart:-1].find("<a href=\"/wiki/") + pStart
    aEnd = source[aStart:-1].find("/a>") + aStart
    try:
        return linkRe.match(source[pStart:aEnd]).group(1)
    except AttributeError:
        sys.exit("Nope bad")
    
page = fetchPage()
title = getTitle(page)
while title != "Philosophy":
    title = getTitle(page)
    print(title)
    page = fetchPage(getFirstLink(page))