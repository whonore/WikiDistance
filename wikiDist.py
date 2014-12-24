import urllib.request
import re
import sys

wikiURL = "https://en.wikipedia.org/wiki/{}"
badLinks = ["Book", "Help", "Wikipedia", "File"]
badToks = [("(", ")"),
           ("<table", "</table>"),
           ("<div", "</div>"),
           ("<i>", "</i>")]
INF = -1

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

    contentStart = source.find("mw-content-text") # find start of content
    content = source[contentStart:]

    aStart = content.find("<a href=\"/wiki/") # find start of link
    aEnd = content[aStart:].find("</a>") + aStart # find end of link
    while not validLink(content, aStart, aEnd): # make sure it is valid
        aStart = content[aEnd:].find("<a href=\"/wiki/") + aEnd
        if aStart < aEnd:
            return fail()
        aEnd = content[aStart:].find("</a>") + aStart

    try: # get the name of the next page
        return linkRe.match(content[aStart:aEnd]).group(1)
    except AttributeError:
        return fail()

def validLink(content, start, end):
    for bad in badLinks: # Make sure it is correct kind of link
        if content[start:end].find(bad + ":") > -1:
            return False

    for tok in badToks: # Make sure not in parens or table
        numOpenClose = [0, 0]

        for openClose in range(2): # check that all that are opened are closed
            begin = 0
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
    title = getTitle(page)
    if printMode:
        print(title)
    if title == "Philosophy":
        return 0
    if title not in dists:
        dists[title] = getDistance(fetchPage(getFirstLink(page)), printMode) + 1
        if dists[title] == 0:
            dists[title] = -1
            return fail()
    return dists[title]

def fail():
    print("No path to Philosophy")
    return INF

def loadDists():
    dists = {"Philosophy": 0}
    with open("wikiDist.csv") as file:
        file.readline()
        for line in file:
            t, d = line.split(", ")
            dists[t] = int(d)
    return dists

def writeDists():
    with open("wikiDist.csv", 'w') as file:
        file.write("Title, Dist\n")
        for t, d in dists.items():
            file.write("{}, {}\n".format(t, d))

dists = loadDists()
for i in range(1):
    print("Starting new random")
    print(getDistance(fetchPage(), 1), "\n")
writeDists()