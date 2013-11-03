import functools
import math
import operator
import os
import re
import sublime
import sublime_plugin
import sys

try:
    from Default.indentation import line_and_normed_pt as normed_rowcol
except ImportError:
    # This is necessary due to load order of packages in Sublime Text 2
    sys.path.append(os.path.join(sublime.packages_path(), 'Default'))
    indentation = __import__('indentation')
    reload(indentation)
    del sys.path[-1]
    normed_rowcol = indentation.line_and_normed_pt

#----------------------------------------------------------------------

# riffle, as in riffle (perfect shuffle) a deck of cards
# produce an output list by alternately picking one item from each input list
# def riffle(*args):
#     return functools.reduce(operator.add, zip(*args))
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
    if x[0] == 'S' and len(x[1]) > 0: return (x[0],' ')
    return x

# expand separable chars with whitespace on either side
def trSep(x):
    if x[0] == 'C': return [('S', ''), x, ('S', '')];
    return [x];

# replace consecutive ws's with a single one
def reduceWS(l, x):
    if x[0] == 'S' and len(l) > 0 and l[-1][0] == 'S':
        return l[:-1] + [('S', ' ' * max(len(x[1]), len(l[-1][1])))]
    else:
        return l + [x]

# http://en.wikibooks.org/wiki/Algorithm_implementation/Strings/Levenshtein_distance#C.2B.2B
def edist(s1, s2):
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
def btedist(s, t, distfunc):
    (m,n) = len(s), len(t)
    d = [[0 for x in range(0, n+1)] for x in range(0, m+1)]
    b = [[0 for x in range(0, n+1)] for x in range(0, m+1)]
    for i in range(0, m+1): d[i][0] = i
    d[0] = range(0, n+1)
    for i in range(1, m+1):
        for j in range(1, n+1):
            (b[i][j], d[i][j]) = min(
                ( 0, d[i-1][j  ] + 1                        ),
                ( 1, d[i  ][j-1] + 1                        ),
                ( 2, d[i-1][j-1] + distfunc(s[i-1], t[j-1]) ),
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
        # if m1[0] == 'S' or m2[0] == 'S': return 0.1
        return 1
    if m1[0] == 'S' : return 0
    # if m1[0] == 'C': return 0
    # if m1[0] == 'O': return 0
    if m1[1] == m2[1] : return 0
    return 1

    # score = 0.0
    # if   m1 [     1 ]     == '' : score = len ( m2[1] )
    # elif m2 [     1 ]     == '' : score = len ( m1[1] )
    # else :  score = edist (  m1 [     1 ]     , m2[1] )
    # return score / (1.0 + score)

#----------------------------------------------------------------------

class AligneratorCommand(sublime_plugin.TextCommand):
    def __init__(self, *args, **kwargs):
        super(AligneratorCommand, self).__init__(*args, **kwargs)

        # capture 'words'
        separableChars = r"""\[\]\{\}\(\)\;\,\=\+"""
        quoteChars = r"""\'\""""

        # |(?P<O>[-\+/\*%&\|\^]=|=|&&|\|\||<<=?|>>=?|::)       # 'O'perators- mainly this is any non-breakable groups of otherwise separable chars

        matcher = r"""(?P<S>\s+)                               # 'S'pace, of the white variety
        |(?P<Q>(?P<qc>\'+|\"+)([^\\]|\\.)*?(?P=qc))            # 'Q'uoted items
        |(?P<N>[-+]?(\d+(\.\d*)?|\.\d+|0[xX][\dA-Fa-f]+)([eE][-+]?\d+)?) # 'N'ums: match ints & floats
        |(?P<O>[-\+/\*%&\|\^=]=|\[\]|\{\}|\(\)|\+\+|<<=|>>=)   # 'O'perators- mainly this is any non-breakable groups of otherwise separable chars
        |(?P<C>[""" + separableChars + r"""])                  # 'C'har: anything separable
        |(?P<W>[^\s""" + quoteChars + separableChars + r"""]+) # 'W'ord: groups of non-separable, non-whitespace chars
        """

        self.e = re.compile(matcher, re.VERBOSE)


    def run(self, edit):
        # read input lines
        view = self.view
        sel = view.sel()
        if len(sel) != 1:
            print('Alignerator: try selecting one (and only one) region')
            return
        oldText = view.substr(sel[0])
        lines = oldText.split('\n')

        allmatches = []
        for line in lines:
            # snag all matches
            lineiter = self.e.finditer(line)
            # expand all matches by name
            groups = [ match.groupdict() for match in lineiter ]
            # groups includes all non-matches- filter those out
            matches = [ [x for x in g.items() if x[1] != None][0] for g in groups ]
            if not matches or (len(matches) == 1 and matches[0][0] == 'S'):
                allmatches.append([])
                continue
            # add null ws between separable chars
            matches = [ m for mg in matches for m in trSep(mg) ]
            # now delete multiple whitespaces in a row
            matches = functools.reduce(reduceWS, [[matches[0]]] + matches[1:])
            allmatches.append(matches)

        # we'll align all lines to the longest matches list
        template = max( allmatches, key=lambda m:len(m) )

        chunks, justifies = [], []
        for matches in allmatches:
            if not matches:
                chunks.append([])
                justifies.append([])
                continue
            # align matches & template, stuff whitespace into all missing slots
            (d, bt) = btedist(matches, template, matchTypeDist)
            for i in range(len(bt)):
                if bt[i] == 1:
                    matches = matches[:i] + [('S','')] + matches[i:]
            # collapse all non-zero whitespace matches to single spaces
            (matchNames, chunk) = zip(*[ trSpace(m) for m in matches])
            # except restore the very first column if it was whitespace
            # we don't want the overall indentation to change
            if matchNames[0] == 'S':
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
        for (chunk, justify) in zip(chunks, justifies):
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
            newLines.append(fmt.format(*chunk))

        view.replace(edit, sel[0], '\n'.join(newLines))

                # 1 2 3 + 0 = 0;
                # 11 22 33 + 5 = 33333 ;
                # 111 222 333 + 555 = 3;
                # 111 222 333 + 555 + 6667 = 3 ;


def convert_to_mid_line_tabs(view, edit, tab_size, pt, length):
    spaces_end = pt + length
    spaces_start = spaces_end
    while view.substr(spaces_start-1) == ' ':
        spaces_start -= 1
    spaces_len = spaces_end - spaces_start
    normed_start = normed_rowcol(view, spaces_start)[1]
    normed_mod = normed_start % tab_size
    tabs_len = 0
    diff = 0
    if normed_mod != 0:
        diff = tab_size - normed_mod
        tabs_len += 1
    tabs_len += int(math.ceil(float(spaces_len - diff)
        / float(tab_size)))
    view.replace(edit, sublime.Region(spaces_start,
        spaces_end), '\t' * tabs_len)
    return tabs_len - spaces_len


class AligneratorOldCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        sel = view.sel()
        max_col = 0

        settings = view.settings()
        tab_size = int(settings.get('tab_size', 8))
        use_spaces = settings.get('translate_tabs_to_spaces')

        # This handles aligning single multi-line selections
        if len(sel) == 1:
            points = []
            line_nums = [view.rowcol(line.a)[0] for line in view.lines(sel[0])]
            # print(line_nums)

            trim_trailing_white_space = \
                settings.get('trim_trailing_white_space_on_save')

            if settings.get('align_indent'):
                # Align the left edges by first finding the left edge
                for row in line_nums:
                    pt = view.text_point(row, 0)

                    # Skip blank lines when the user times trailing whitespace
                    line = view.line(pt)
                    # print(line)
                    if trim_trailing_white_space and line.a == line.b:
                        continue

                    char = view.substr(pt)
                    while char == ' ' or char == '\t':
                        # Turn tabs into spaces when the preference is spaces
                        if use_spaces and char == '\t':
                            view.replace(edit, sublime.Region(pt, pt+1), ' ' *
                                tab_size)

                        # Turn spaces into tabs when tabs are the preference
                        if not use_spaces and char == ' ':
                            max_pt = pt + tab_size
                            end_pt = pt
                            while view.substr(end_pt) == ' ' and end_pt < \
                                    max_pt:
                                end_pt += 1
                            view.replace(edit, sublime.Region(pt, end_pt),
                                '\t')

                        pt += 1

                        # Rollback if the left edge wraps to the next line
                        if view.rowcol(pt)[0] != row:
                            pt -= 1
                            break

                        char = view.substr(pt)

                    points.append(pt)
                    max_col = max([max_col, view.rowcol(pt)[1]])

                # Adjust the left edges based on the maximum that was found
                adjustment = 0
                max_length = 0
                for pt in points:
                    pt += adjustment
                    length = max_col - view.rowcol(pt)[1]
                    max_length = max([max_length, length])
                    adjustment += length
                    view.insert(edit, pt, (' ' if use_spaces else '\t') *
                        length)

                perform_mid_line = max_length == 0

            else:
                perform_mid_line = True

            alignment_chars = settings.get('alignment_chars')
            if alignment_chars == None:
                alignment_chars = []
            alignment_prefix_chars = settings.get('alignment_prefix_chars')
            if alignment_prefix_chars == None:
                alignment_prefix_chars = []
            alignment_space_chars = settings.get('alignment_space_chars')
            if alignment_space_chars == None:
                alignment_space_chars = []

            alignment_pattern = '|'.join([re.escape(ch) for ch in
                alignment_chars])

            if perform_mid_line and alignment_chars:
                points = []
                max_col = 0
                for row in line_nums:
                    pt = view.text_point(row, 0)
                    matching_region = view.find(alignment_pattern, pt)
                    if not matching_region:
                        continue
                    matching_char_pt = matching_region.a

                    insert_pt = matching_char_pt
                    # If the equal sign is part of a multi-character
                    # operator, bring the first character forward also
                    if view.substr(insert_pt-1) in alignment_prefix_chars:
                        insert_pt -= 1

                    space_pt = insert_pt
                    while view.substr(space_pt-1) in [' ', '\t']:
                        space_pt -= 1
                        # Replace tabs with spaces for consistent indenting
                        if view.substr(space_pt) == '\t':
                            view.replace(edit, sublime.Region(space_pt,
                                space_pt+1), ' ' * tab_size)
                            matching_char_pt += tab_size - 1
                            insert_pt += tab_size - 1

                    if view.substr(matching_char_pt) in alignment_space_chars:
                        space_pt += 1

                    # If the next equal sign is not on this line, skip the line
                    if view.rowcol(matching_char_pt)[0] != row:
                        continue

                    points.append(insert_pt)
                    max_col = max([max_col, normed_rowcol(view, space_pt)[1]])

                # The adjustment takes care of correcting point positions
                # since spaces are being inserted, which changes the points
                adjustment = 0
                for pt in points:
                    pt += adjustment
                    length = max_col - normed_rowcol(view, pt)[1]
                    adjustment += length
                    if length >= 0:
                        view.insert(edit, pt, ' ' * length)
                    else:
                        view.erase(edit, sublime.Region(pt + length, pt))

                    if settings.get('mid_line_tabs') and not use_spaces:
                        adjustment += convert_to_mid_line_tabs(view, edit,
                            tab_size, pt, length)


        # This handles aligning multiple selections
        else:
            max_col = max([normed_rowcol(view, region.b)[1] for region in sel])

            for region in sel:
                length = max_col - normed_rowcol(view, region.b)[1]
                view.insert(edit, region.b, ' ' * length)
                if settings.get('mid_line_tabs') and not use_spaces:
                    convert_to_mid_line_tabs(view, edit, tab_size, region.b,
                        length)
