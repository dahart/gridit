#!/usr/bin/env python

import fileinput, re, operator

# capture 'words'
separableChars = "\[\]\{\}\(\)\;\,"

matcher = r"""
(?P<ws>\s+)                                 # white space
|(?P<num>(?<=\s)\d+(?=\s))                  # match integers
|(?P<sep>[""" + separableChars + """])      # any separable char
|(?P<word>[^\s""" + separableChars + """]+) # groups of non-separable, non-whitespace chars
"""

e = re.compile(matcher, re.VERBOSE)

#----------------------------------------------------------------------

# riffle, as in riffle a deck of cards 
# produce an output list by alternate picking one item from each input list
# meant for strings-- operator.add concatenates
def riffle(*args):
    return reduce(operator.add, zip(*args))

# return the print format string for right-justify if we have a number
# or left-justify if we have anything else
def trJustify(x):
    if x == 'num': return ''
    return '-'

# collapse the text of whitespace pairs to a single space
def trSpace(x):
    if x[0] == 'ws': return (x[0],' ')
    return x

#----------------------------------------------------------------------

# read input lines
lists = []
justifies = []
try:
    for line in fileinput.input():
        line = line.rstrip() # chomp & eat right-side whitespace

        # snag all matches
        iter = e.finditer(line)
        # expand all matches by name
        groups = [match.groupdict() for match in iter]
        # groups includes all non-matches- filter those out
        matches = [ filter(lambda x:x[1] != None, g.iteritems())[0] for g in groups ]

        # collapse all whitespace matches to single spaces
        (matchNames, list) = zip(*map(trSpace, matches))
        # except restore the very first column if it was whitespace
        # we don't want the overall indentation to change
        if matchNames[0] == 'ws': list = (matches[0][1],) + list[1:]
        justify = map(trJustify, matchNames)

        # remember our text columns & justification
        lists.append(list)
        justifies.append(justify)
except KeyboardInterrupt:
    pass


# compute column widths
maxCols = max(map(len, lists))
widths = [0 for x in range(maxCols)]
justify = ['-' for x in widths]
for list in lists:
    # zero-pad the end of the result, so that widths doesn't get truncated 
    # because zip stops when the first list is empty
    newWidths = map(len, list) + [0] * (maxCols-len(list))
    widths = map(max, zip(widths, newWidths))


# now go back through all our lines and output with new formatting
for (list,justify) in zip(lists,justifies):
    n = len(list)

    a = ['%'] * n
    b = justify
    c = map(str, widths)
    d = ['s'] * n

    fmt = ''.join(riffle(a,b,c,d))

    print fmt % tuple(list)
