#!/usr/bin/python

import functools
import math
import operator
import os
import re
import sublime
import sublime_plugin
import sys

from . import lineup

# **    [ ] add support for sublime settings
# ***   [ ] user options
# ***   [ ] read sublime language settings when aligning: keywords, operators, separables
# ***   [X] allow comments to NOT be aligned
# ***   [ ] allow comments to be aligned
# ***   [ ] read sublime tab stop size when aligning (am I replacing tabs with spaces?)
# ****  [ ] can i make sublime replace tabs on my selection?
# ****  [ ] integrate sublime settings as command line flags & args to the module function
# ***** [ ] user flag -tabsize
# **    [ ] what about emacs?  dev studio?  etc.?  xcode?

# *     [ ] possible features
# **    [ ] only operate on lines matching the template to within say 50%
# **    [ ] maybe reset alignment when more than one line doesn't match the template
# **    [ ] maybe perform alignment on multiple templates simultaneously

# *     [ ] bugs
# **    [ ] fix html indentation - I saw the initial indentation break


# try:
#     from Default.indentation import line_and_normed_pt as normed_rowcol
# except ImportError:
#     # This is necessary due to load order of packages in Sublime Text 2
#     sys.path.append(os.path.join(sublime.packages_path(), 'Default'))
#     indentation = __import__('indentation')
#     reload(indentation)
#     del sys.path[-1]
#     normed_rowcol = indentation.line_and_normed_pt


#----------------------------------------------------------------------

class GriditCommand(sublime_plugin.TextCommand):
    def __init__(self, *args, **kwargs):
        super(GriditCommand, self).__init__(*args, **kwargs)

    def run(self, edit):
        # read input lines
        view = self.view
        sel = view.sel()
        if len(sel) != 1:
            print('Alignerator: try selecting one (and only one) region')
            return
        oldText = view.substr(sel[0])
        lines = oldText.split('\n')

        newLines = lineup.lineup(lines)

        line_endings = self.view.settings().get('default_line_ending')
        lineEndChars = '\n'
        if   line_endings == 'windows': lineEndChars = '\r\n'
        elif line_endings == 'mac'    : lineEndChars = '\r'

        view.replace(edit, sel[0], lineEndChars.join(newLines))
