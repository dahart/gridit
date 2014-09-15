gridit
======

A sublime text plugin to line up ALL the things!

## What

Gridit tries to align everything in your selection, not just the start of the line, or assignment operators.

### Before:

```
(0,d[i-1][j]+1),
(12, d[i][j-1]+1),
(2,d[i][j-1]+1),
(300,d[i][j-1]+2,5),
```

### After:

```
(  0, d[i-1][j  ]+1  ),
( 12, d[i  ][j-1]+1  ),
(  2, d[i  ][j-1]+1  ),
(300, d[i  ][j-1]+2,5),
```

## How

If using sublime, install the plugin directly via Package Control (https://sublime.wbond.net/)

For any other editor, you can still line up all your things. Download gridit, then setup your own command to copy a selection, pipe to gridit, then replace the selection with the result. If your editor can't do that, I feel bad for you. There are notes on how to do this with Emacs and MS Visual Studio. Notes for any other editors will be gladly accepted.


## Why

- Feed your inner perfectionist / OCD.

- Drastically improve readability of repetetive lines. Gridit makes some typos stick out like a sore thumb.

- Allows, supports, provides more reasons to use column selection for fast editing.

- Helps when refactoring repetetive blocks, using column selection. Especially when adding, removing or rearranging arguments.

- Gridit left-aligns text to match up prefixes, and right-aligns numbers to match up position, e.g. ones column.


## Caveats

Gridit was nurtured with the languages that I use most, namely C/C++, python, javascript, bash and a few others. It might not work well with your favorite language. Show me what doesn't work and we can try to fix it.

I want gridit to be magical and always format code beautifully, but sometimes, occasionally, gridit doesn't do what you expect. Keep undo, and wbond's Alignment plugin, handy - these can cover some cases that gridit doesn't deal with. And, of course, send me examples that gridit can't handle, along with what it should look like, and we'll see if we can't make good things happen.
