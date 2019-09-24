from __future__ import print_function

name = "csinsc"
version = "1.0.0"

'''
goto functionality
used (and tweaked) from: http://entrian.com/goto/download.html
'''

# checking_argv0 will only enable goto for the outer file that
# imports csinsc
# set this to False if you need goto for other files (will be
# slow)
checking_argv0 = True

import sys, token, tokenize

class MissingLabelError(Exception):
    """'goto' without matching 'label'."""
    pass

# Source filenames -> line numbers of plain gotos -> target label names.
_plainGotoCache = {}
# Source filenames -> line numbers of labels -> label names.
_labelCache = {}
# Source filenames -> label names -> line numbers of those labels.
_labelNameCache = {}

def _addToCaches(moduleFilename):
    """Finds the labels and gotos in a module and adds them to the caches."""

    # The token patterns that denote gotos and labels.
    plainGotoPattern = [(token.NAME, 'goto'), (token.OP, '.')]
    labelPattern = [(token.NAME, 'label'), (token.OP, '.')]

    # Initialise this module's cache entries.
    _plainGotoCache[moduleFilename] = {}
    _labelCache[moduleFilename] = {}
    _labelNameCache[moduleFilename] = {}

    # Tokenize the module; 'window' is the last two (type, string) pairs.
    window = [(None, ''), (None, '')]
    for tokenType, tokenString, (startRow, startCol), (endRow, endCol), line \
            in tokenize.generate_tokens(open(moduleFilename, 'r').readline):
        # Plain goto: "goto .x"
        if window == plainGotoPattern:
            _plainGotoCache[moduleFilename][startRow] = tokenString

        # Label: "label .x"  XXX Computed labels.
        elif window == labelPattern:
            _labelCache[moduleFilename][startRow] = tokenString
            _labelNameCache[moduleFilename][tokenString] = startRow

        # Move the token window back by one.
        window = [window[1], (tokenType, tokenString)]

    # print(_labelNameCache)


def _trace(frame, event, arg):
    try:
        # If this is the first time we've seen this source file, cache it.
        filename = frame.f_code.co_filename
        if checking_argv0:
          if filename != sys.argv[0]:
              return
        else:
          if filename[0] == "<":
              return

        if filename not in _plainGotoCache:
            _addToCaches(filename)

        # Is there a goto on this line?
        targetLabel = _plainGotoCache[filename].get(frame.f_lineno)

        # Jump to the label's line.
        if targetLabel:
            try:
                targetLine = _labelNameCache[filename][targetLabel]
            except KeyError:
                raise Exception(MissingLabelError, "Missing label: %s" % targetLabel)
            frame.f_lineno = targetLine

    except Exception as e:
        return None

    return _trace

# Install the trace function, including all preceding frames.
sys.settrace(_trace)
frame = sys._getframe().f_back
while frame:
    frame.f_trace = _trace
    frame = frame.f_back

# Define the so-called keywords for importing: 'goto', 'label' and 'comefrom'.
class _Label:
    """Allows arbitrary x.y attribute lookups."""

    def __getattr__(self, name):
        return None

goto = None
label = _Label()

# coding: utf-8
# Copyright (c) 2008-2011 Volvox Development Team
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Author: Konstantin Lepa <konstantin.lepa@gmail.com>

"""ANSII Color formatting for output in terminal."""


import os


__ALL__ = [ 'colored', 'cprint' ]

VERSION = (1, 1, 0)

ATTRIBUTES = dict(
        list(zip([
            'bold',
            'dark',
            '',
            'underline',
            'blink',
            '',
            'reverse',
            'concealed'
            ],
            list(range(1, 9))
            ))
        )
del ATTRIBUTES['']


HIGHLIGHTS = dict(
        list(zip([
            'on_grey',
            'on_red',
            'on_green',
            'on_yellow',
            'on_blue',
            'on_magenta',
            'on_cyan',
            'on_white'
            ],
            list(range(40, 48))
            ))
        )


COLORS = dict(
        list(zip([
            'grey',
            'red',
            'green',
            'yellow',
            'blue',
            'magenta',
            'cyan',
            'white',
            ],
            list(range(30, 38))
            ))
        )


RESET = '\033[0m'


def colored(text, color=None, on_color=None, attrs=None):
    """Colorize text.

    Available text colors:
        red, green, yellow, blue, magenta, cyan, white.

    Available text highlights:
        on_red, on_green, on_yellow, on_blue, on_magenta, on_cyan, on_white.

    Available attributes:
        bold, dark, underline, blink, reverse, concealed.

    Example:
        colored('Hello, World!', 'red', 'on_grey', ['blue', 'blink'])
        colored('Hello, World!', 'green')
    """
    if os.getenv('ANSI_COLORS_DISABLED') is None:
        fmt_str = '\033[%dm%s'
        if color is not None:
            text = fmt_str % (COLORS[color], text)

        if on_color is not None:
            text = fmt_str % (HIGHLIGHTS[on_color], text)

        if attrs is not None:
            for attr in attrs:
                text = fmt_str % (ATTRIBUTES[attr], text)

        text += RESET
    return text


def cprint(text, color=None, on_color=None, attrs=None, **kwargs):
    """Print colorize text.

    It accepts arguments of print function.
    """

    print((colored(text, color, on_color, attrs)), **kwargs)


if __name__ == '__main__':
    print('Current terminal type: %s' % os.getenv('TERM'))
    print('Test basic colors:')
    cprint('Grey color', 'grey')
    cprint('Red color', 'red')
    cprint('Green color', 'green')
    cprint('Yellow color', 'yellow')
    cprint('Blue color', 'blue')
    cprint('Magenta color', 'magenta')
    cprint('Cyan color', 'cyan')
    cprint('White color', 'white')
    print(('-' * 78))

    print('Test highlights:')
    cprint('On grey color', on_color='on_grey')
    cprint('On red color', on_color='on_red')
    cprint('On green color', on_color='on_green')
    cprint('On yellow color', on_color='on_yellow')
    cprint('On blue color', on_color='on_blue')
    cprint('On magenta color', on_color='on_magenta')
    cprint('On cyan color', on_color='on_cyan')
    cprint('On white color', color='grey', on_color='on_white')
    print('-' * 78)

    print('Test attributes:')
    cprint('Bold grey color', 'grey', attrs=['bold'])
    cprint('Dark red color', 'red', attrs=['dark'])
    cprint('Underline green color', 'green', attrs=['underline'])
    cprint('Blink yellow color', 'yellow', attrs=['blink'])
    cprint('Reversed blue color', 'blue', attrs=['reverse'])
    cprint('Concealed Magenta color', 'magenta', attrs=['concealed'])
    cprint('Bold underline reverse cyan color', 'cyan',
            attrs=['bold', 'underline', 'reverse'])
    cprint('Dark blink concealed white color', 'white',
            attrs=['dark', 'blink', 'concealed'])
    print(('-' * 78))

    print('Test mixing:')
    cprint('Underline red on grey color', 'red', 'on_grey',
            ['underline'])
    cprint('Reversed green on red color', 'green', 'on_red', ['reverse'])

from time import *

class SimpleScreen:
  def __init__(self):
    self.width = 10
    self.height = 5
    self.num_lines = 100
    
    self.screen = [[] * self.width] * self.height
    self.clear()

    self.fps = 60
    
  def clear(self):
    for row in range(self.height):
      self.screen[row] = [' '] * self.width

  def print_at(self, text, x, y):
    self.screen[y][x] = text
    
  def show(self):
    
    for _ in range(self.num_lines):
      print()
    print(flush = True)
    
    for row in self.screen:
      print("".join(row))
    print(flush = True)
    
####################################################################
# Simple curses wrapper so console based text games can be easily  #
# written, tweaked, and analysed.                                  #
####################################################################

from curses import *

class Screen(object):
  def __init__(self, width = 40, height = 25, fps = 60, refresh_on_clear = True):
    self.width = width
    self.height = height

    self.screen = [[] * self.width] * self.height

    self.keys = {}
    for key in range(512):
      self.keys[key] = False

    self.win = None

    self.fps = fps

    self.x = 0
    self.y = 0

    self.refresh_on_clear = refresh_on_clear

    self.clear()

  def __del__(self):
    if self.win is not None:
      self.teardown()

  def __enter__(self):
    self.setup()
    self.clear()
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    self.teardown()

  def setup(self):
    initscr()
    noecho()
    curs_set(0)
    self.win = newwin(self.height + 1, self.width + 1, 0, 0)
    self.win.keypad(1)
    self.win.nodelay(1)

  def teardown(self):
    self.win.keypad(0)
    echo()
    curs_set(1)
    endwin()

  def clear(self, clear_ch = " ", reset_cursor = True):
    if self.refresh_on_clear:
      self.refresh()
      
    for row in range(self.height):
      self.screen[row] = [clear_ch] * self.width

    if reset_cursor:
      self.x = 0
      self.y = 0


 
  def getch(self):
    return self.win.getch()

  def print(self, text, newline = True):
    x = int(self.x)
    y = int(self.y)

    for dx, ch in enumerate(text):
      if x + dx > self.width:
        # wrap to next line
        x = x + dx - self.width
        y = y + 1
      if y > self.height:
        # scroll everything up
        for row in range(1, self.height):
          for col in range(self.width):
            self.screen[y - 1][col] = self.screen[y][col]
      self.screen[y][x + dx] = ch    
      
    if newline:
      y += 1

    self.x = x
    self.y = y

    #if self.auto_refresh:
    #  self.refresh()

  def border(self):
    for x in range(1, self.width - 1):
      self.screen[0][x] = '-'
      self.screen[self.height - 1][x] = '-'
    for y in range(1, self.height - 1):
      self.screen[y][0] = '|'
      self.screen[y][self.width - 1] = '|'
    self.screen[0][0] = '.'
    self.screen[0][self.width - 1] = '.'
    self.screen[self.height - 1][0] = '\''
    self.screen[self.height - 1][self.width - 1] = '\''    

  def printAt(self, text, x, y):
    x = int(x)
    y = int(y)
    for dx, ch in enumerate(text):
      self.screen[y][x + dx] = ch

  def refresh(self):
    if self.win is None:
      self.setup()

    for y, row in enumerate(self.screen):
      line = str("".join(row))
      self.win.addstr(y, 0, line)

    for key in range(512):
      self.keys[key] = False

    self.win.timeout(int(1000.0 / self.fps))
    ch = self.win.getch()
    self.win.timeout(0)
    while ch != -1:
      self.keys[ch] = True
      ch = self.win.getch()

  def isKeyPressed(self, key):
    return self.keys[ord(key)]

  def setFPS(self, fps):
    self.fps = fps
    




