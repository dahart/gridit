#!/usr/bin/env python

import fileinput, re, operator

# capture 'words'
separableChars = "\[\]\{\}\(\)\;\,"

matcher = r"""
(?P<ws>\s+)                                 # white space
|(?P<quote>(?P<q>[\'\"]).*?(?P=q))          # quoted items
|(?P<num>[+-]?(?<=\b)((\d+(\.\d*)?)|\.\d+)([eE][+-]?[0-9]+|f)?(?=\b)) # match ints & floats - dunno if the word boundary look-around matches are still needed...
|(?P<sep>[""" + separableChars + """])      # any separable char
|(?P<word>[^\s""" + separableChars + """]+) # groups of non-separable, non-whitespace chars
"""

e = re.compile(matcher, re.VERBOSE)

#----------------------------------------------------------------------

# riffle, as in riffle a deck of cards 
# produce an output list by alternately picking one item from each input list
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
    if x[0] == 'ws' and len(x[1]) > 0: return (x[0],' ')
    return x

# expand separable chars with whitespace on either side
def trSep(x):
    if x[0] == 'sep': return [('ws', ''), x, ('ws', '')];
    return [x];

# replace consecutive ws's with a single one
def reduceWS(l, x):
    if x[0] == 'ws' and len(l) > 0 and l[-1][0] == 'ws':
        return l[:-1] + [('ws', ' ' * max(len(x[1]), len(l[-1][1])))]
    else:
        return l + [x]

#----------------------------------------------------------------------

# read input lines
lines = []
try:
    for line in fileinput.input():
        line = line.rstrip() # chomp & eat right-side whitespace
        lines.append(line)
except KeyboardInterrupt:
    pass



lists = []
justifies = []
for line in lines:
    # snag all matches
    iter = e.finditer(line)
    # expand all matches by name
    groups = [match.groupdict() for match in iter]
    # groups includes all non-matches- filter those out
    matches = [ filter(lambda x:x[1] != None, g.iteritems())[0] for g in groups ]

    if len(matches) == 0:
        lists.append([''])
        justifies.append([''])
    else:
        # add null ws between separable chars
        matches = reduce(operator.concat, map(trSep, matches));
        # now delete multiple whitespaces in a row - only propagate the largest WS
        # in order for reduce to return a list of tuples, I have to listify
        # the first element of the list of tuples, so that concatenate is operating
        # on a list, and not on the first tuple.  get it?!?!
        matches = reduce(reduceWS, [[matches[0]]] + matches[1:]);
        # collapse all non-zero whitespace matches to single spaces
        (matchNames, list) = zip(*map(trSpace, matches))

        # except restore the very first column if it was whitespace
        # we don't want the overall indentation to change
        if matchNames[0] == 'ws': 
            list = (matches[0][1],) + list[1:]
        justify = map(trJustify, matchNames)

        # remember our text columns & justification
        lists.append(list)
        justifies.append(justify)


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
