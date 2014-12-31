WikiDistance
============

A program to calculate the "distance" from Wikipedia pages to the Philosophy page.

Starting from a random Wikipedia article it finds the first "valid" link on the
page and follows it until one of the following occurs: <br>

- The Philosophy article is reached
- The article has no valid links
- The article eventually loops back to itself
    
A valid link is the first link to another Wikipedia article in the main body of
the article that is not in italics, parentheses, a table or a div.

A list of the article titles, the next article they point to and their distance
to Philosophy are stored in a csv file. This file is loaded every time the
program runs to avoid recalculating distances for articles that have already
been visited.

Run the code with: <br>
<code>python wikiDist.py (<# of iterations>)</code> <br>
Number of iterations is 10 by default