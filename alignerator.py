#!/usr/bin/python

import functools
import math
import operator
import os
import re
import sublime
import sublime_plugin
import sys

from . import gridit

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

class AligneratorCommand(sublime_plugin.TextCommand):
    def __init__(self, *args, **kwargs):
        super(AligneratorCommand, self).__init__(*args, **kwargs)

    def normalize_line_endings(self, string):
        string = string.replace('\r\n', '\n').replace('\r', '\n')
        line_endings = self.view.settings().get('default_line_ending')
        if line_endings == 'windows':
            string = string.replace('\n', '\r\n')
        elif line_endings == 'mac':
            string = string.replace('\n', '\r')
        return string

    def run(self, edit):
        # read input lines
        view = self.view
        sel = view.sel()
        if len(sel) != 1:
            print('Alignerator: try selecting one (and only one) region')
            return
        oldText = view.substr(sel[0])
        lines = oldText.split('\n')

        newLines = gridit.lineup(lines)

        view.replace(edit, sel[0], self.normalize_line_endings('\n'.join(newLines)))
