'''Some with too many commas'''
import urllib.request
import re
import sys

wikiURL = "https://en.wikipedia.org/wiki/{}"
badLinks = ["Book", "Help", "Wikipedia", "File"]
badContain = [("(", ")"),
              ("<table", "</table>"),
              ("<div", "</div>"),
              ("<i>", "</i>")]
INF = -1


def fetchPage(topic="Special:Random"):
    '''Returns the HTTPResponse object for a given Wikipedia topic.'''
    url = wikiURL.format(topic)
    page = urllib.request.urlopen(url)
    source = str(page.read())[2:-1]

    return source


def getTitle(source):
    '''Finds the title of the page.'''
    titleRe = re.compile(
        ".*<title>(.*) - Wikipedia, the free encyclopedia</title>.*")
    return titleRe.match(source).group(1)


def getFirstLink(source):
    '''Finds the first "valid" link of the page.'''
    linkRe = re.compile(".*<a href=\"/wiki/(.+)\" title.*")

    contentStart = source.find("mw-content-text")  # find start of content
    content = source[contentStart:]

    aStart = content.find("<a href=\"/wiki/")      # find start of link
    aEnd = content[aStart:].find("</a>") + aStart  # find end of link
    while not validLink(content, aStart, aEnd):    # make sure it is valid
        aStart = content[aEnd:].find("<a href=\"/wiki/") + aEnd
        if aStart < aEnd:
            return fail()
        aEnd = content[aStart:].find("</a>") + aStart

    try:  # get the name of the next page
        return linkRe.match(content[aStart:aEnd]).group(1)
    except AttributeError:
        return fail()


def validLink(content, start, end):
    '''Checks that the link is valid.
       The link must not be in italics, parentheses a table or a div.
    '''
    for bad in badLinks:  # Make sure it is correct kind of link
        if content[start:end].find(bad + ":") > -1:
            return False

    for tok in badContain:          # Make sure not in bad container
        numOpenClose = [0, 0]

        for openClose in range(2):  # check that all opened containers
            begin = 0               # are closed
            while True:
                pos = content[begin:start].find(tok[openClose])
                if pos == -1:
                    break
                begin += pos + len(tok[openClose])
                numOpenClose[openClose] += 1

        if numOpenClose[0] != numOpenClose[1]:
            return False

    return True


def getDistance(page, printMode=0):
    '''Finds the "distance" to the Philosophy page by following the first
       valid link. Also stores the next page in the chain.
    '''
    title = getTitle(page)
    #if ',' in title:
    #    title = re.sub(',', '_', title)
    if printMode:
        print(title)
    if title not in dists:
        dists[title] = ("Unknown", INF)  # Needed to catch loops
        next, dist = getDistance(fetchPage(getFirstLink(page)), printMode)
        if dist != INF:
            dists[title] = (next, dist + 1)
        else:
            print("Loop found. No path to Philosophy.")
            dists[title] = (next, INF)
    return (title, dists[title][1])


def fail():
    '''Called if no valid link is found.'''
    print("No valid links. No path to Philosophy.")
    return ("NULL", INF)


def loadDists():
    '''Loads the csv file into a dictionary.'''
    dists = {"Philosophy": ("NULL", 0)}
    with open("wikiDist.csv") as file:
        file.readline()
        for line in file:
            title, next, dist = line.strip().split("\",\"")
            dists[title[1:]] = (next, int(dist[:-1]))
    return dists


def writeDists():
    '''Writes the dictionary back to the csv file.'''
    with open("wikiDist.csv", 'w') as file:
        file.write("Title,Next,Dist\n")
        for title, info in dists.items():
            file.write("\"{}\",\"{}\",\"{}\"\n".format(title, info[0], info[1]))


dists = loadDists()
for i in range(5):
    print("Starting new random")
    getDistance(fetchPage(), 1)
    print()
writeDists()
