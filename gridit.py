import sublime, sublime_plugin
import os, sys, subprocess

class GriditCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # read input lines

        view = self.view
        sel = view.sel()
        if len(sel) != 1:
            return

        oldText = view.substr(sel[0])

        command = ['python']
        lineup = os.path.expanduser('~/depot/scripts/bin/python/lineup/lineup.py')
        args = [lineup]

        proc = subprocess.Popen(command + args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        proc.stdin.write(bytes(oldText,'utf-8'))
        proc.stdin.close()
        newText = proc.stdout.read()
        proc.wait()

        view.replace(edit, sel[0], newText.decode('utf-8'))
