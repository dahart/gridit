#!/usr/bin/python

"""
line up columny sections of text (code)
this script assumes that each line has the same number of 'columns'
and pads the whitespace between all the columns so everything lines up in a grid
takes stdin as input, prints to stdout
"""

import functools
import re


# tokenRE is generic regex to capture all tokens
# it is assumed that whitespace is allowed to appear between any pair of tokens
# so, we have to capture any sequences that can't be broken in this regex
# also, my rule is that tokens have a 1 character name
# groups to discard can be named with more than 1 character

separableChars = r'\[\]\{\}\(\)\;\,\=\+'
quoteChars     = r'\'\"'
comments       = r'//.*$|\#.*$|/\*.*\*/'

tokenRE = r"""(?P<W>\s+)                               # 'W'hite space
|(?P<Q>(?P<qc>\'+|\"+)([^\\]|\\.)*?(?P=qc))            # 'Q'uoted items
|(?P<C>(""" + comments + r"""))                        # 'C'omments
|(?P<N>[-+]?(\d+(\.\d*)?|\.\d+|0[xX][\dA-Fa-f]+)([eE][-+]?\d+)?) # 'N'ums: match ints & floats
|(?P<O>[-\+/\*%&\|\^=\!]=|\[\]|\{\}|\(\)|\+\+|>>=|<<=) # 'O'perators- we only need to identify non-breakable groups of separable chars
|(?P<S>[""" + separableChars + r"""])                  # 'S'eparable characters
|(?P<G>[^\s""" + quoteChars + separableChars + r"""]+) # 'G'roups of non-separable, non-whitespace chars
"""

exp = re.compile(tokenRE, re.VERBOSE)

#----------------------------------------------------------------------

# riffle, as in riffle (perfect shuffle) a deck of cards
# produce an output list by alternately picking one item from each input list
def riffle(*args):
    return [ y for x in zip(*args) for y in x ]

# return the print format string for right-justify if we have a number
# or left-justify if we have anything else
def trJustify(x):
    if x == 'N': return '>'
    # if x == 'O': return '>'
    return '<'

# collapse the text of whitespace pairs to a single space
def trSpace(x):
    if x[0] == 'W' and len(x[1]) > 0: return (x[0],' ')
    return x

# expand separable chars with whitespace on either side
def trSep(x):
    if x[0] == 'S': return [('W', ''), x, ('W', '')];
    return [x];

# replace consecutive ws's with a single one
def reduceWS(l, x):
    if x[0] == 'W' and len(l) > 0 and l[-1][0] == 'W':
        return l[:-1] + [('W', ' ' * max(len(x[1]), len(l[-1][1])))]
    else:
        return l + [x]

# http://en.wikipedia.org/wiki/Levenshtein_distance
def btedist(s, t, distfunc):
    (m,n) = len(s), len(t)
    d = [[0 for x in range(0, n+1)] for x in range(0, m+1)]
    b = [[0 for x in range(0, n+1)] for x in range(0, m+1)]
    for i in range(0, m+1): d[i][0] = i
    d[0] = range(0, n+1)
    for i in range(1, m+1):
        for j in range(1, n+1):
            (b[i][j], d[i][j]) = min(
                (0, d[i-1][j]+1),
                (1, d[i][j-1]+1),
                (2, d[i-1][j-1] + distfunc(s[i-1], t[j-1])),
                key=lambda x:x[1])
    (i, j) = (m, n)
    bt = [];
    while (i >= 1 and j >= 1):
        bt.append(b[i][j])
        if   (b[i][j] == 0): i -= 1
        elif (b[i][j] == 1):         j -= 1
        elif (b[i][j] == 2): i -= 1; j -= 1
    bt.reverse()
    return (d[m][n], bt)


def matchTypeDist(m1, m2):
    if m1[0] != m2[0] :
        return 1
    if m1[0] == 'W' or m2[0] == 'W': return 0
    if m1[1] == m2[1] : return 0
    return 1


#----------------------------------------------------------------------

def lineup(lines):
    allmatches = []
    for line in lines:
        # snag all matches
        lineiter = exp.finditer(line)

        # expand all matches by name
        groups = [ match.groupdict() for match in lineiter ]

        # groups includes all non-matches- filter those out
        # strip out sub-groups, e.g. 'qc', by ensuring the group name is 1 character
        matches = [ [x for x in g.items() if x[1] and len(x[0]) == 1][0] for g in groups ]
        if not matches or (len(matches) == 1 and matches[0][0] == 'W'):
            allmatches.append([])
            continue

        # add null ws between separable chars
        matches = [ m for mg in matches for m in trSep(mg) ]

        # now delete multiple whitespaces in a row
        matches = functools.reduce(reduceWS, [[matches[0]]] + matches[1:])
        allmatches.append(matches)

    # we'll align all lines to the longest matches list
    template = max( allmatches, key=lambda m:len(m) )
    if template and template[0][0] != 'W': template = [('W', '')] + template

    chunks, justifies = [], []
    for matches in allmatches:
        if not matches:
            chunks.append([])
            justifies.append([])
            continue

        # enforce the first column not changing by separating it from the rest
        if matches[0][0] != 'W': matches = [('W','')] + matches
        matchesHead  , matchesTail  = matches  [:2], matches  [2:]
        templateHead , templateTail = template [:2], template [2:]

        # align matches & template, stuff whitespace into all missing slots
        (d, bt) = btedist(matchesTail, templateTail, matchTypeDist)
        for i in range(len(bt)):
            if bt[i] == 1:
                matchesTail = matchesTail [:i] + [('W' ,'')] + matchesTail [i:]
        matches = matchesHead + matchesTail

        # collapse all non-zero whitespace matches to single spaces
        (matchNames, chunk) = zip(*[ trSpace(m) for m in matches])

        # except restore the very first column if it was whitespace
        # we don't want the overall indentation to change
        if matchNames[0] == 'W':
            chunk = (matches[0][1],) + chunk[1:]
        justify = [ trJustify(name) for name in matchNames ]

        # remember our text columns & justification
        chunks.append(chunk)
        justifies.append(justify)

    # compute column widths
    maxCols = max([len(l) for l in chunks])
    widths = [0 for x in range(maxCols)]
    for chunk in chunks:
        # zero-pad the end of the result, so that widths doesn't get truncated
        # because zip stops when the first list is empty
        newWidths = [ len(t) for t in chunk ] + [0] * (maxCols-len(chunk))
        widths = [ max(w) for w in zip(widths, newWidths) ]

    # now go back through all our lines and output with new formatting
    newLines = []
    for (chunk,justify) in zip(chunks,justifies):
        if not chunk:
            newLines.append('')
            continue
        n = len(chunk)
        a = ['{:'] * n
        b = justify
        c = [ str(w) if w > 0 else '' for w in widths ]
        d = ['s'] * n
        e = ['}'] * n
        fmt = ''.join(riffle(a,b,c,d,e))
        newLines.append(fmt.format(*chunk).rstrip())

    return newLines



if __name__ == "__main__":
    import fileinput

    # read input lines
    lines = []
    try:
        for line in fileinput.input():
            lines.append(line.rstrip()) # chomp & eat right-side whitespace
    except KeyboardInterrupt:
        pass

    newLines = lineup(lines)

    for line in newLines:
        print(line)
