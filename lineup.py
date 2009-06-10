#!/usr/bin/env python
#
# line up columny sections of text (code)
# this script assumes that each line has the same number of 'columns'
# and pads the whitespace between all the columns so everything lines up.
# takes stdin as input, prints to stdout
#
# at the bottom of this file are comments about how to 
# use this, in macro form, for:
# vs.net 2005
# emacs [todo]
#
# 

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


######################################################################
#
# VS.NET 2005 macro using lineup.py:
# (Modify paths to suit - e.g. search for depot/bin below)
#
# 
#     Function GetOutputWindow() As OutputWindow
#         Return DTE.Windows.Item(Constants.vsWindowKindOutput).Object()
#     End Function

#     Function GetActivePane() As OutputWindowPane
#         Return GetOutputWindow.ActivePane
#     End Function

#     Private Sub ErrToOutputWindow(ByVal err As String)
#         Dim OWp As OutputWindowPane = GetActivePane()
#         ' Write exception text to this new pane.
#         OWp.OutputString(err & vbNewLine)
#     End Sub


#     ' examples:
#     ' How to redirect standard input
#     ' http://msdn.microsoft.com/en-us/library/system.diagnostics.process.standardinput.aspx
#     ' HTML tidy
#     ' http://msdn.microsoft.com/en-us/library/aa289176(VS.71).aspx

#     Sub LineUpText()
#         Try
#             DTE.UndoContext.Open("LineUpText")

#             'From: http://www.ondotnet.com/pub/a/dotnet/2005/06/20/macrorefactor.html
#             'Get the selected text
#             Dim doc As Document = DTE.ActiveDocument
#             Dim sel As TextSelection = doc.Selection
#             Dim selectedText As String = sel.Text

#             '            Dim doc As Document = _
#             'applicationObject.Documents.Item(CustomIn)
#             Dim td As TextDocument = CType(DTE.ActiveDocument.Object("TextDocument"), TextDocument)

#             ''make sure we're working on complete lines only
#             'If Not td.StartPoint.AtStartOfLine Then
#             '    td.StartPoint.StartOfLine()
#             'End If
#             'If Not td.EndPoint.AtEndOfLine Then
#             '    td.EndPoint.EndOfLine()
#             'End If

#             Dim sp As TextPoint = td.StartPoint
#             Dim ep As TextPoint = td.EndPoint
#             Dim editStartPt As EditPoint = sp.CreateEditPoint()
#             Dim editEndPt As EditPoint = ep.CreateEditPoint()

#             ' Get content of the document.
#             Dim txtDoc As String = editStartPt.GetText(editEndPt)

#             ' Set up process info.
#             Dim psi As New System.Diagnostics.ProcessStartInfo
#             psi.FileName = "d:/depot/bin/python.bat"
#             psi.Arguments = Environ("UtilScripts") & "/lineup.py"
#             ErrToOutputWindow(psi.FileName & " " & psi.Arguments)
#             psi.CreateNoWindow = True
#             psi.UseShellExecute = False
#             psi.RedirectStandardInput = True
#             psi.RedirectStandardOutput = True
#             psi.RedirectStandardError = True

#             ' Create the process.
#             Dim p As New System.Diagnostics.Process

#             ' Associate process info with the process.
#             p.StartInfo = psi

#             ' Run the process.
#             Dim fStarted As Boolean = p.Start()
#             If Not fStarted Then _
#                 Throw New Exception("Unable to start " & psi.FileName & " process.")

#             ' Set up streams to interact with process's stdin/stdout.
#             Dim sw As System.IO.StreamWriter = p.StandardInput
#             Dim sr As System.IO.StreamReader = p.StandardOutput
#             Dim strFormattedDoc As String = Nothing

#             ' Write content of Active Selection to process's stdin.
#             sw.Write(selectedText)
#             sw.Close()

#             ' Read process's stdout and store in strFormattedDoc.
#             strFormattedDoc = sr.ReadToEnd()
#             sr.Close()

#             ' Handle no stdout text, instead display error text.
#             If strFormattedDoc = "" Then
#                 Dim srError As System.IO.StreamReader = p.StandardError
#                 Dim strError As String = srError.ReadToEnd()
#                 srError.Close()
#                 Throw New Exception(psi.FileName & " failed with error " _
#                     & "information: " & strError)
#             End If

#             Dim objSel As TextSelection = DTE.ActiveDocument.Selection
#             Dim objTP As VirtualPoint = objSel.TopPoint
#             Dim objBP As VirtualPoint = objSel.BottomPoint
#             Dim objTEP As EditPoint = objTP.CreateEditPoint
#             Dim objBEP As EditPoint = objBP.CreateEditPoint
#             objTEP.ReplaceText(objBEP, strFormattedDoc, CInt(vsEPReplaceTextOptions.vsEPReplaceTextTabsSpaces))

#         Catch ex As Exception
#             ErrToOutputWindow(ex.ToString())
#         Finally
#             DTE.UndoContext.Close()
#         End Try
#     End Sub
#
#######################################################################
#
# Emacs:
# (Modify paths to suit)
#
# ;; example: http://www.perl.com/pub/a/2005/03/31/lightning2.html
# (defun line-up-text ()
#   (interactive)
#   (shell-command-on-region (point)
#          (mark) "python ~/depot/scripts/bin/python/lineup/lineup.py" nil t))
# (global-set-key "\el"      'line-up-text  )
#
#######################################################################
