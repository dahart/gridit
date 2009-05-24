#!/usr/bin/env python

import fileinput, math, re
from optparse import OptionParser

# capture 'words'

separableChars = "\[\]\{\}\(\)\;\,"
matcher = r"\s+|[" + separableChars + "]|[^\s" + separableChars + "]+|\b\d+\b"
# print matcher

e = re.compile(matcher)

# parser = OptionParser()
# parser.add_option("-b", "--buckets", dest="buckets",
#                   help="number of buckets", metavar="N", default=50)
# (options, args) = parser.parse_args()
# buckets = int(options.buckets)


# http://en.wikibooks.org/wiki/Algorithm_implementation/Strings/Levenshtein_distance#C.2B.2B
def levenshtein(s1, s2):
    d_curr = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        d_prev, d_curr = d_curr, [i]
        for j, c2 in enumerate(s2):
            d_curr.append(min(
              d_prev[j] + (c1 != c2),
              d_prev[j + 1] + 1,
              d_curr[j] + 1
            ))
    return d_curr[len(s2)]


# http://en.wikipedia.org/wiki/Levenshtein_distance
def LevenshteinDistanceWithBacktracking(s, t):
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
x                (2, d[i-1][j-1] + int(s[i-1] != t[j-1])),
                key=lambda x:x[1])
    (i, j) = (m, n)
    bt = [];
    while (i >= 1 and j >= 1):
        bt.append(b[i][j])
        if (b[i][j] == 0): i -= 1
        elif (b[i][j] == 1): j -= 1
        elif (b[i][j] == 2): i -= 1; j -= 1
    return (d[m][n], bt)


def TestLevALigner(lines):
    (d, bt) = LevenshteinDistanceWithBacktracking(lines[0], lines[1])
    bt.reverse()
    print "dist:", d
    print "bt:", bt
    print "zeros:", filter(lambda x:x==0, bt)
    print "ones:", filter(lambda x:x==1, bt)
    
    out0, out1 = lines[0], lines[1]
    
    for i in range(len(bt)):
        if (bt[i] == 1):
            out0 = out0[:i] + ' ' + out0[i:]
        if (bt[i] == 0):
            out1 = out1[:i] + ' ' + out1[i:]
                
    print "in0:", lines[0]
    print "out0:", out0
    print "out1:", out1
    print "in1:", lines[1]


# read input lines
lines = []
lists = []
lengths = []
try:
    for line in fileinput.input():
        # line = line.rstrip('\n') # chomp
        line = line.rstrip() # chomp & eat whitespace
        list = e.findall(line)
        lines.append(line)
        lists.append(list)
        lengths.append(len(line))

except KeyboardInterrupt:
    pass


# TestLevALigner(lines)

# for list in lists:
#     #print '|'.join(line)
#     print '|'.join(list)

def whichMax(list):
    return max(enumerate(list), key=lambda x:x[1])[0]

def whichMin(list):
    return min(enumerate(list), key=lambda x:x[1])[0]

alphaLineIdx = whichMax(lengths)
alphaLine = lines[alphaLineIdx]

# print "[", lengths[alphaLineIdx], "]",
# print "alphaLineIdx:", alphaLineIdx
# print alphaLine, "[alphaLine]"
# print len(lines[alphaLineIdx])

from itertools import izip

def flatten1(x, y):
    return [p for pair in izip(x, y) for p in pair]

def flatten6(x, y):
    return list(chain(*izip(x, y)))

# other attempts at flatten:
# [no work] map(lambda x:t=t+x[0]+x[1], zip(list, testspaces))
# [slow] t=reduce(lambda x,y:(x[0]+x[1]+y[0]+y[1],''), zip(list, testspaces))[0]
# t = ''.join(reduce(lambda x,y:x+y, zip(list, testspaces)))

import operator

# riffle, as in riffle a deck of cards 
# produce an output list by alternate picking between each input list
# meant for strings, operator.add concatenates
def riffle(*args):
    return reduce(operator.add, zip(*args))

# t = ''.join(lists[alphaLineIdx])
# print len(t)

def alignDist(s, t):
    return sum(map(lambda x:int(x[0]!=x[1]), zip(s, t)))

def TestMyAligner(lists):
    for listIndex, list in enumerate(lists):
        spaces = ['' for x in list]
        for iter in range(lengths[alphaLineIdx] - lengths[listIndex]):
            distances = [0 for x in spaces]
            for i in range(-1,len(spaces)):
                testspaces = spaces[:i] + [spaces[i] + ' '] + spaces[i+1:]
                t = ''.join(flatten1(list, testspaces))
    #             distances[i] = levenshtein(alphaLine, t)
                distances[i] = alignDist(alphaLine, t)
    #             print alphaLine
    #             print t, distances[i]
            i = whichMin(distances)
    #         print(distances), "[wm:", i, "]"
            spaces = spaces[:i] + [spaces[i] + ' '] + spaces[i+1:]
    #         t = ''.join(reduce(lambda x,y:x+y, zip(list, testspaces)))
    #         print t
        t = ''.join(flatten1(list, spaces))
    #     print t
        print t, "[", len(t), "]"
        print alphaLine

# TestMyAligner(lists)

# compute column widths
widths = [0 for x in lists[0]]
for list in lists:
    widths = map(max, zip(widths, map(len, list)))

maxCols = max(map(len, lists))
# print maxCols

import operator

for list in lists:
    while (len(list) < maxCols):
        list.append('')

    a = ['%'] * maxCols
    b = ['-'] * maxCols
    c = map(str, widths)
    d = ['s'] * maxCols

    fmt = ''.join(riffle(a,b,c,d))

#     fmt = reduce(operator.add, riffle(['s%-'] * maxCols, map(str, widths)))[1:] + 's'
#     print fmt

    print fmt % tuple(list)
