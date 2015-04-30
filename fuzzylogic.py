"""
fuzzylogic v2 - May 2015
Kamil Mansuri

fuzzylogic v2 is a fork of 'fuzzywuzzy' by Adam Cohen
The main difference is the forced usage of internal SequenceMatcher, and removal of all python-Levenshtein dependencies
Fork came about as Levenshtein speed not necessary for tiny queries (datasets should be small-ish)

As projects I work on grow more complex, this code will likely become reworked even more from the original code
I plan on integrating a new SequenceMatcher along with use of SQLAlchemy (or more likely 'peewee') to speed things up for larger datasets using PostreSQL or others


Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from __future__ import unicode_literals
import itertools
from difflib import SequenceMatcher
import re
import string
import sys


#left in the Python 3 checks, as eventually all code will support Python 3 exclusively
PY3 = sys.version_info[0] == 3


class StringProcessor(object):
    """
    This class defines method to process strings in the most
    efficient way. Ideally all the methods below use unicode strings
    for both input and output.
    """

    regex = re.compile(r"(?ui)\W")

    @classmethod
    def replace_non_letters_non_numbers_with_whitespace(cls, a_string):
        """
        This function replaces any sequence of non letters and non
        numbers with a single white space.
        """
        return cls.regex.sub(u" ", a_string)

    if PY3:
        strip = staticmethod(str.strip)
        to_lower_case = staticmethod(str.lower)
        to_upper_case = staticmethod(str.upper)
    else:
        strip = staticmethod(string.strip)
        to_lower_case = staticmethod(string.lower)
        to_upper_case = staticmethod(string.upper)




def validate_string(s):
    try:
        return len(s) > 0
    except TypeError:
        return False

bad_chars = str("").join([chr(i) for i in range(128, 256)])  # ascii dammit!
if PY3:
    translation_table = dict((ord(c), None) for c in bad_chars)


def asciionly(s):
    if PY3:
        return s.translate(translation_table)
    else:
        return s.translate(None, bad_chars)


def asciidammit(s):
    if type(s) is str:
        return asciionly(s)
    elif type(s) is unicode:
        return asciionly(s.encode('ascii', 'ignore'))
    else:
        return asciidammit(unicode(s))


def make_type_consistent(s1, s2):
    """If both objects aren't either both string or unicode instances force them to unicode"""
    if isinstance(s1, str) and isinstance(s2, str):
        return s1, s2

    elif isinstance(s1, unicode) and isinstance(s2, unicode):
        return s1, s2

    else:
        return unicode(s1), unicode(s2)


def full_process(s, force_ascii=False):
    """Process string by
        -- removing all but letters and numbers
        -- trim whitespace
        -- force to lower case
        if force_ascii == True, force convert to ascii"""

    if s is None:
        return ""

    if force_ascii:
        s = asciidammit(s)
    # Keep only Letters and Numbers (see Unicode docs).
    string_out = StringProcessor.replace_non_letters_non_numbers_with_whitespace(s)
    # Force into lowercase.
    string_out = StringProcessor.to_lower_case(string_out)
    # Remove leading and trailing whitespaces.
    string_out = StringProcessor.strip(string_out)
    return string_out


def intr(n):
    '''Returns a correctly rounded integer'''
    return int(round(n))


###########################
# Basic Scoring Functions #
###########################

def ratio(s1, s2):

    if s1 is None:
        raise TypeError("s1 is None")
    if s2 is None:
        raise TypeError("s2 is None")
    s1, s2 = make_type_consistent(s1, s2)

    if len(s1) == 0 or len(s2) == 0:
        return 0

    m = SequenceMatcher(None, s1, s2)
    return intr(100 * m.ratio())


# todo: skip duplicate indexes for a little more speed
def partial_ratio(s1, s2):
    """"Return the ratio of the most similar substring
    as a number between 0 and 100."""

    if s1 is None:
        raise TypeError("s1 is None")
    if s2 is None:
        raise TypeError("s2 is None")
    s1, s2 = make_type_consistent(s1, s2)
    if len(s1) == 0 or len(s2) == 0:
        return 0

    if len(s1) <= len(s2):
        shorter = s1
        longer = s2
    else:
        shorter = s2
        longer = s1

    m = SequenceMatcher(None, shorter, longer)
    blocks = m.get_matching_blocks()

    # each block represents a sequence of matching characters in a string
    # of the form (idx_1, idx_2, len)
    # the best partial match will block align with at least one of those blocks
    #   e.g. shorter = "abcd", longer = XXXbcdeEEE
    #   block = (1,3,3)
    #   best score === ratio("abcd", "Xbcd")
    scores = []
    for block in blocks:
        long_start = block[1] - block[0] if (block[1] - block[0]) > 0 else 0
        long_end = long_start + len(shorter)
        long_substr = longer[long_start:long_end]

        m2 = SequenceMatcher(None, shorter, long_substr)
        r = m2.ratio()
        if r > .995:
            return 100
        else:
            scores.append(r)

    return int(100 * max(scores))


##############################
# Advanced Scoring Functions #
##############################

def _process_and_sort(s, force_ascii):
    """Return a cleaned string with token sorted."""
    # pull tokens
    tokens = full_process(s, force_ascii=force_ascii).split()

    # sort tokens and join
    sorted_string = u" ".join(sorted(tokens))
    return sorted_string.strip()

# Sorted Token
#   find all alphanumeric tokens in the string
#   sort those tokens and take ratio of resulting joined strings
#   controls for unordered string elements
def _token_sort(s1, s2, partial=True, force_ascii=True):

    if s1 is None:
        raise TypeError("s1 is None")
    if s2 is None:
        raise TypeError("s2 is None")

    sorted1 = _process_and_sort(s1, force_ascii)
    sorted2 = _process_and_sort(s2, force_ascii)

    if partial:
        return partial_ratio(sorted1, sorted2)
    else:
        return ratio(sorted1, sorted2)

def token_sort_ratio(s1, s2, force_ascii=True):
    """Return a measure of the sequences' similarity between 0 and 100
    but sorting the token before comparing.
    """
    return _token_sort(s1, s2, partial=False, force_ascii=force_ascii)


def partial_token_sort_ratio(s1, s2, force_ascii=True):
    """Return the ratio of the most similar substring as a number between
    0 and 100 but sorting the token before comparing.
    """
    return _token_sort(s1, s2, partial=True, force_ascii=force_ascii)


def _token_set(s1, s2, partial=True, force_ascii=True):
    """Find all alphanumeric tokens in each string...
        - treat them as a set
        - construct two strings of the form:
            <sorted_intersection><sorted_remainder>
        - take ratios of those two strings
        - controls for unordered partial matches"""

    if s1 is None:
        raise TypeError("s1 is None")
    if s2 is None:
        raise TypeError("s2 is None")

    p1 = full_process(s1, force_ascii=force_ascii)
    p2 = full_process(s2, force_ascii=force_ascii)

    if not validate_string(p1):
        return 0
    if not validate_string(p2):
        return 0

    # pull tokens
    tokens1 = set(full_process(p1).split())
    tokens2 = set(full_process(p2).split())

    intersection = tokens1.intersection(tokens2)
    diff1to2 = tokens1.difference(tokens2)
    diff2to1 = tokens2.difference(tokens1)

    sorted_sect = " ".join(sorted(intersection))
    sorted_1to2 = " ".join(sorted(diff1to2))
    sorted_2to1 = " ".join(sorted(diff2to1))

    combined_1to2 = sorted_sect + " " + sorted_1to2
    combined_2to1 = sorted_sect + " " + sorted_2to1

    # strip
    sorted_sect = sorted_sect.strip()
    combined_1to2 = combined_1to2.strip()
    combined_2to1 = combined_2to1.strip()

    if partial:
        ratio_func = partial_ratio
    else:
        ratio_func = ratio

    pairwise = [
        ratio_func(sorted_sect, combined_1to2),
        ratio_func(sorted_sect, combined_2to1),
        ratio_func(combined_1to2, combined_2to1)
    ]
    return max(pairwise)


def token_set_ratio(s1, s2, force_ascii=True):
    return _token_set(s1, s2, partial=False, force_ascii=force_ascii)


def partial_token_set_ratio(s1, s2, force_ascii=True):
    return _token_set(s1, s2, partial=True, force_ascii=force_ascii)


# TODO: numerics

###################
# Combination API #
###################

# q is for quick
def QRatio(s1, s2, force_ascii=True):

    p1 = full_process(s1, force_ascii=force_ascii)
    p2 = full_process(s2, force_ascii=force_ascii)

    if not validate_string(p1):
        return 0
    if not validate_string(p2):
        return 0

    return ratio(p1, p2)


def UQRatio(s1, s2):
    return QRatio(s1, s2, force_ascii=False)


# w is for weighted
def WRatio(s1, s2, force_ascii=True):
    """Return a measure of the sequences' similarity between 0 and 100,
    using different algorithms.
    """

    p1 = full_process(s1, force_ascii=force_ascii)
    p2 = full_process(s2, force_ascii=force_ascii)

    if not validate_string(p1):
        return 0
    if not validate_string(p2):
        return 0

    # should we look at partials?
    try_partial = True
    unbase_scale = .95
    partial_scale = .90

    base = ratio(p1, p2)
    len_ratio = float(max(len(p1), len(p2))) / min(len(p1), len(p2))

    # if strings are similar length, don't use partials
    if len_ratio < 1.5:
        try_partial = False

    # if one string is much much shorter than the other
    if len_ratio > 8:
        partial_scale = .6

    if try_partial:
        partial = partial_ratio(p1, p2) * partial_scale
        ptsor = partial_token_sort_ratio(p1, p2, force_ascii=force_ascii) \
            * unbase_scale * partial_scale
        ptser = partial_token_set_ratio(p1, p2, force_ascii=force_ascii) \
            * unbase_scale * partial_scale

        return int(max(base, partial, ptsor, ptser))
    else:
        tsor = token_sort_ratio(p1, p2, force_ascii=force_ascii) * unbase_scale
        tser = token_set_ratio(p1, p2, force_ascii=force_ascii) * unbase_scale

        return int(max(base, tsor, tser))


def UWRatio(s1, s2):
    """Return a measure of the sequences' similarity between 0 and 100,
    using different algorithms. Same as WRatio but preserving unicode.
    """
    return WRatio(s1, s2, force_ascii=False)





def extract(query, choices, processor=None, scorer=None, limit=5):
    """Find best matches in a list or dictionary of choices, return a
    list of tuples containing the match and its score. If a dictionery
    is used, also returns the key for each match.

    Arguments:
        query       -- an object representing the thing we want to find
        choices     -- a list or dictionary of objects we are attempting
                       to extract values from. The dictionary should
                       consist of {key: str} pairs.
        scorer      -- f(OBJ, QUERY) --> INT. We will return the objects
                       with the highest score by default, we use
                       score.WRatio() and both OBJ and QUERY should be
                       strings
        processor   -- f(OBJ_A) --> OBJ_B, where the output is an input
                       to scorer for example, "processor = lambda x:
                       x[0]" would return the first element in a
                       collection x (of, say, strings) this would then
                       be used in the scoring collection by default, we
                       use full_process()

    """
    if choices is None:
        return []

    # Catch generators without lengths
    try:
        if len(choices) == 0:
            return []
    except TypeError:
        pass

    # default, turn whatever the choice is into a workable string
    if not processor:
        processor = full_process

    # default: wratio
    if not scorer:
        scorer = WRatio

    sl = list()

    if isinstance(choices, dict):
        for key, choice in choices.items():
            processed = processor(choice)
            score = scorer(query, processed)
            tuple = (choice, score, key)
            sl.append(tuple)

    else:
        for choice in choices:
            processed = processor(choice)
            score = scorer(query, processed)
            tuple = (choice, score)
            sl.append(tuple)

    sl.sort(key=lambda i: i[1], reverse=True)
    return sl[:limit]


def extractBests(query, choices, processor=None, scorer=None, score_cutoff=0, limit=5):
    """Find best matches above a score in a list of choices, return a
    list of tuples containing the match and its score.

    Convenience method which returns the choices with best scores, see
    extract() for full arguments list

    Optional parameter: score_cutoff.
        If the choice has a score of less than or equal to score_cutoff
        it will not be included on result list

    """
    best_list = extract(query, choices, processor, scorer, limit)
    return list(itertools.takewhile(lambda x: x[1] >= score_cutoff, best_list))


def extractOne(query, choices, processor=None, scorer=None, score_cutoff=0):
    """Find the best match above a score in a list of choices, return a
    tuple containing the match and its score if it's above the threshold
    or None.

    Convenience method which returns the single best choice, see
    extract() for full arguments list

    Optional parameter: score_cutoff.
        If the best choice has a score of less than or equal to
        score_cutoff we will return none (intuition: not a good enough
        match)

    """
    best_list = extract(query, choices, processor, scorer, limit=1)
    if len(best_list) > 0 and best_list[0][1] >= score_cutoff:
        return best_list[0]
    return None
