import urllib.request
import re
import sys

wikiURL = "https://en.wikipedia.org/wiki/{}"
badLinks = ["Book", "Help", "Wikipedia", "File", "Special"]
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


def getFirstLink(source, title, printMode=0):
    '''Finds the first "valid" link of the page.'''
    linkRe = re.compile(".*<a href=\"/wiki/(.+)\" title.*")

    contentStart = source.find("mw-content-text")  # find start of content
    content = source[contentStart:]

    aStart = content.find("<a href=\"/wiki/")      # find start of link
    aEnd = content[aStart:].find("</a>") + aStart  # find end of link

    isValid, failType = validLink(content, aStart, aEnd)
    while not isValid:                             # make sure it is valid
        aStart = content[aEnd:].find("<a href=\"/wiki/") + aEnd
        if aStart < aEnd:
            logMessage("No path error",
                       "No valid links found for {}.\n"
                       "\tManual check should be performed for "
                       "unclosed parentheses.".format(title),
                       printMode)
            return None
        aEnd = content[aStart:].find("</a>") + aStart

        isValid, failType = validLink(content, aStart, aEnd)

    link = content[aStart:aEnd]
    try:  # get the name of the next page
        return linkRe.match(link).group(1)
    except AttributeError:
        logMessage("No title error",
                   "Title could not be found in {}".format(link),
                   printMode)
        return None


def validLink(content, start, end):
    '''Checks that the link is valid.
       The link must not be in italics, parentheses, a table, or a div.
    '''
    for bad in badLinks:  # Make sure it is correct kind of link
        if content[start:end].find(bad + ":") > -1:
            return (False, bad)

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
            return (False, tok)

    return (True, None)


def getDistance(page, printMode=0):
    '''Finds the "distance" to the Philosophy page by following the first
       valid link. Also stores the next page in the chain.
    '''
    title = getTitle(page)
    if printMode:
        print(title)
    if title not in dists:
        dists[title] = ("Unknown", INF)  # Needed to catch loops

        firstLink = getFirstLink(page, title, printMode)
        if not firstLink:                # No links found
            dists[title] = ("NULL", INF)
        else:
            next, dist = getDistance(fetchPage(getFirstLink(page, title)),
                                     printMode)
            if dist != INF:
                dists[title] = (next, dist + 1)
            else:
                logMessage("No path error",
                           "Loop found from {} to {}".format(title, next),
                           printMode)
                dists[title] = (next, INF)
    return (title, dists[title][1])


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
            file.write("\"{}\",\"{}\",\"{}\"\n".format(
                title, info[0], info[1]))


def logMessage(messageType, message, printMessage=0):
    '''Writes a message to the log.'''
    with open("log.txt", 'a') as log:
        log.write("{}: {}\n".format(messageType, message))
    if printMessage:
        print("{}: {}".format(messageType, message))


if __name__ == "__main__":
    iters = 10
    if len(sys.argv) > 1:
        try:
            iters = int(sys.argv[1])
        except ValueError:
            sys.exit("run as: python wikiDist.py (<number of iterations>)")

    dists = loadDists()
    for i in range(iters):
        print("Starting from new random article...")
        getDistance(fetchPage(), 1)
        print()
    writeDists()
