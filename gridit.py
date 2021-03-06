#!/usr/bin/python

# TODO

# [ ] add support for sublime settings (elaborate...)
# okay, i was probably thinking be able to toggle some of the gridit behaviors,
# like scoring text within a column. sometimes its desirable, and sometimes its just wacky
#
# [ ] add support for column selections (perhaps generally multiple regions)
#
# [ ] user options
# [ ] read sublime language settings when aligning: keywords, operators, separables
# [X] allow comments to NOT be aligned
# [ ] allow comments to be aligned

# [ ] fix differing leading whitespace not aligning
# Bug: If the first column contains mixed numbers and strings, then repeated aligns
# will add more leading whitespace every time.

# i don't remember why i want tab sizes.
# wait, i think i do
# var lists in javascript - it would be nice to be able to align this properly:
# var a=1,
#     b=2;
# that would require knowing the tab size.
#
# [ ] read sublime tab stop size when aligning (am I replacing tabs with spaces?)
# [ ] can i make sublime replace tabs on my selection? (dont want to replace leading tabs though; because python)

# [ ] integrate sublime settings as command line flags & args to the module function
# [ ] user flag -tabsize
# [ ] what about emacs?  dev studio?  etc.?  xcode?

# [ ] only operate on lines matching the template to within say 50%
# [ ] maybe reset alignment when more than one line doesn't match the template
# [ ] maybe perform alignment on multiple templates simultaneously

# [ ] bugs
# [ ] fix html indentation - I saw the initial indentation break


#----------------------------------------------------------------------

"""
line up columny sections of text (code)
this script assumes that each line has the same number of 'columns'
and pads the whitespace between all the columns so everything lines up in a grid
available as a sublime plugin, or as a simple stdin/out filter
"""

import functools
import re

# tokenRE is generic regex to capture all tokens
# it is assumed that whitespace is allowed to appear between any pair of tokens
# so, we have to capture any sequences that can't be broken in this regex
# also, my rule is that tokens have a 1 character name
# groups to discard can be named with more than 1 character

separableChars = r'\[\]\{\}\(\)\;\,\=\+\:'
quoteChars     = r'\'\"'
comments       = r'//.*$|\#.*$|/\*.*?\*/'


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
                (0, d[i-1][j  ]+1),
                (1, d[i  ][j-1]+1),
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
    if m1[0] != m2[0]               : return 1
    if m1[0] == 'W' or m2[0] == 'W' : return 0
    if m1[1] == m2[1]               : return 0
    return 1


#----------------------------------------------------------------------

def gridit(lines):
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


# Attempt to provide sublime with a new command, but
# if sublime is not available, bail out silently to
# allow use of this file without any connection to sublime
try:
    import sublime
    import sublime_plugin

    class GriditCommand(sublime_plugin.TextCommand):
        def __init__(self, *args, **kwargs):
            super(GriditCommand, self).__init__(*args, **kwargs)

        def run(self, edit):
            # read input lines
            view = self.view
            sel = view.sel()

            if len(sel) != 1:
                print('Gridit: Sorry, I can only handle one region for now.')
                return

            reg = view.sel()[0]
            sel_start_line  = (view.classify(reg.a) & sublime.CLASS_LINE_START) != 0
            sel_start_empty = (view.classify(reg.a) & sublime.CLASS_EMPTY_LINE) != 0
            sel_end_line    = (view.classify(reg.b) & sublime.CLASS_LINE_END  ) != 0
            sel_end_empty   = (view.classify(reg.b) & sublime.CLASS_EMPTY_LINE) != 0

            if (not sel_start_line and not sel_start_empty) and (not sel_end_line and not sel_end_empty):
                view.run_command("expand_selection", {"to": "line"})
                # Fix the selection to what expand_selection should have been
                # to make sure repeated runs don't expand the lines of the selection every time
                reg = view.sel()[0]
                view.sel().clear()
                view.sel().add(sublime.Region(reg.a, reg.b-1))

            oldText = view.substr(sel[0])
            lines   = oldText.split('\n')

            newLines = gridit(lines)

            line_endings = self.view.settings().get('default_line_ending')
            lineEndChars = '\n'
            if   line_endings == 'windows': lineEndChars = '\r\n'
            elif line_endings == 'mac'    : lineEndChars = '\r'

            view.replace(edit, sel[0], lineEndChars.join(newLines))

# try:
#     import os
#     import sys
#     from Default.indentation import line_and_normed_pt as normed_rowcol
# except ImportError:
#     # This is necessary due to load order of packages in Sublime Text 2
#     sys.path.append(os.path.join(sublime.packages_path(), 'Default'))
#     indentation = __import__('indentation')
#     reload(indentation)
#     del sys.path[-1]
#     normed_rowcol = indentation.line_and_normed_pt

except ImportError:
    # quietly ignore it if sublime isn't available, it just means we're not in plugin mode
    pass


# If this file is executed directly,
# then process stdin using gridit() and paste to stdout
if __name__ == "__main__":
    import fileinput

    # read input lines
    lines = []
    try:
        for line in fileinput.input():
            lines.append(line.rstrip()) # chomp & eat right-side whitespace
    except KeyboardInterrupt:
        pass

    newLines = gridit(lines)

    for line in newLines:
        print(line)
