# hotfuzz v3
#####hotfuzz is a 'fuzzy' search module that is lightweight and works very nicely in Python 2 and 3 projects
#####Based on Adam Cohen's fantastic fuzzywuzzy project, hotfuzz aims to work right out of the box with Flask and other Python web frameworks.
#####Ultimately, the goal of this project is to port this over to Flask exclusively for use alongside jQuery

#####hotfuzz is best suited for smaller dictionaries and lists (queries take about 1 second for lists of 5,000 items)
<br>

### Installation/Usage (tested on Python 2.7.10 and Python 3.4.3)
```extractOne(query, choices, score_cutoff)```
<br>
```extractBests(query, choices, score_cutoff, limit)```<br>

    query = what you want to search for
    choices = can be a dict or a list that you pass in
    score_cutoff = is a percentage ratio of match (70% or higher is good to use)
    limit = the number of results that you will get back
#####Any suggestions or ideas on how to improve this alpha build of hotfuzz are much appreciated!
#####tweet me [@supermansuri]
<br>
### Version
-   **v3** - Significant code refactoring, significant speed improvements, 
    significantly optimized Python 3+ comptability, forced unicode,
    removed unicode_literals import dependance
-   **v2** - Removed Levenshtein sequencematching and ext dependancies
-   **v1**: initial fork of fuzzywuzzy by Adam Cohen

###Bugs / Upcoming fixes
-   Publish unit tests
-   Speed-ups! (Query of List size of 5,000 takes approx 1 second)


###Attribution and Licensing

The MIT License (MIT)

Copyright (c) 2015 Kamil Mansuri, Adam Cohen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.


[@supermansuri]:http://twitter.com/supermansuri
