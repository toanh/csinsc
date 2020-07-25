from __future__ import print_function

name = "csinsc"
version = "1.1.0.6"

# for complete the blanks exercises
__________ = None

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


######################### color constants #########################
#             abstracted for both termcolour and curses           #
###################################################################
class Colour:
    grey = '\033[30m'
    red = '\033[31m'
    green = '\033[32m'
    yellow = '\033[33m'
    blue = '\033[34m'
    magenta = '\033[35m'
    cyan = '\033[36m'
    white = '\033[37m'
    # TODO: fix black
    black = '\033[30m'
    reset = '\033[0m'


class Highlight:
    grey = '\033[40m'
    red = '\033[41m'
    green = '\033[42m'
    yellow = '\033[43m'
    blue = '\033[44m'
    magenta = '\033[45m'
    cyan = '\033[46m'
    # TODO: fix black
    black = '\033[40m'
    white = '\033[47m'


class Style:
    bold = '\033[1m'
    dark = '\033[2m'
    underline = '\033[4m'
    blink = '\033[5m'
    reverse = '\033[7m'
    concealed = '\033[8m'


############### color lookup for curses ###############
curses_lookup = {}

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

__ALL__ = ['colored', 'cprint']

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
        print(flush=True)

        for row in self.screen:
            print("".join(row))
        print(flush=True)


####################################################################
# Simple curses wrapper so console based text games can be easily  #
# written, tweaked, and analysed.                                  #
####################################################################
def simple_clear(lines=40):
    for _ in range(lines):
        print()


import termios, fcntl, sys, os

import locale
import copy
#import xterm

class Point:
  def __init__(self, x = 0, y = 0):
    self.x = x
    self.y = y

class Screen(object):
    def __init__(self, width=40, height=25, colour=True, fps=60, auto_setup=True, refresh_on_clear=False):
        self.width = width
        self.height = height
        self.colourMode = colour

        self.screen = None

        self.keys = {}
        for key in range(512):
            self.keys[key] = False
        self.keys["vpad_up"] = False
        self.keys["vpad_down"] = False
        self.keys["vpad_left"] = False
        self.keys["vpad_right"] = False            

        self.win = None

        self.fps = fps

        self.x = 0
        self.y = 0
        self.mouse_state = ""

        self.mouse_x = -1
        self.mouse_y = -1

        self.refresh_on_clear = refresh_on_clear

        self.colours = {}
        self.colours[Colour.black] = [0, 0, 0]
        self.colours[Colour.grey] = [150, 150, 150]
        self.colours[Colour.red] = [255, 0, 0]
        self.colours[Colour.green] = [0, 255, 0]
        self.colours[Colour.yellow] = [255, 255, 0]
        self.colours[Colour.blue] = [0, 0, 255]
        self.colours[Colour.magenta] = [255, 0, 255]
        self.colours[Colour.cyan] = [0, 255, 255]
        self.colours[Colour.white] = [255, 255, 255]

        if auto_setup:
            self.setup()

        self.clear()
        locale.setlocale(locale.LC_ALL, '')      

    def __del__(self):
      self.teardown()

    def __enter__(self):
        self.setup()
        self.clear()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.teardown()

    def setup(self):      
      self.fd = sys.stdin.fileno()

      self.oldterm = termios.tcgetattr(self.fd)

      newattr = termios.tcgetattr(self.fd)
      newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
      termios.tcsetattr(self.fd, termios.TCSANOW, newattr)

      # hide cursor
      print("\033[?25l")

      print("\033[?1003h") # click detection
      print("\033[?1006h") # make it better
      print("\033[?7l") # don't  line wrap      

    def teardown(self):
      print(flush=True, end="")
      termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.oldterm)
      fcntl.fcntl(self.fd, fcntl.F_SETFL, self.oldflags)
      print("\033[?25h", end="") # show cursor
      print("\033[?1003l", end="") # disable click detection
      print("\033[?1006l", end="") # make it better
      print("\033[?7h", end="") # line wrap         

    def shutdown(self):
        self.teardown()

    def getMousePos(self):
      return Point(self.mouse_x, self.mouse_y)

    def clear(self, clear_ch=" ", clear_col=[255, 255, 255], clear_bg=[0, 0, 0], reset_cursor=True):
        # TODO: fix this so that black works
        #clear_col = 0
        if self.refresh_on_clear and self.screen is not None:
            self.refresh()

        self.screen = []
        for _ in range(self.height):
          row = []
          for __ in range(self.width):
            row.append(clear_ch)
          self.screen.append(row)

        self.colour_screen = []
        for _ in range(self.height):
          self.colour_screen.append([[clear_col[0],
                                      clear_col[1],
                                      clear_col[2],
                                      clear_bg[0],
                                      clear_bg[1],
                                      clear_bg[2]]] * self.width)

        if reset_cursor:
            self.x = 0
            self.y = 0

    def print(self, text, newline=True):
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

    
    def messageBox(self, message, title = ""):
      # make a copy of the Screen
      screen = copy.deepcopy(self.screen)

      msgWidth = self.width - 8

      lines = []

      paddingLen = (msgWidth - 2 - len(title)) / 2.0
      # left padding is rounded down, right padding is rounded accurately
      # to cater for odd lengthed text
      lines.append("╔" + "-" * int(paddingLen) + title + "-" * int(paddingLen + 0.5) + "╗")

      line = "|"
      words = message.split(" ")
      for word in words:
        # disregard the space at the end but adding the | also
        lineLen = len(line) + len(word)
        if lineLen >= msgWidth:
          lines.append(line[:-1] + (msgWidth - len(line)) * " " + "|")
          # new line
          line = "|"
        line += word + " "
      lines.append(line[:-1] + (msgWidth - len(line)) * " " + "|")

      endText = "Press [SPACE]"
      paddingLen = (msgWidth - 2 - len(endText)) / 2.0
      lines.append("╚" + "-" * int(paddingLen) + endText + "-" * int(paddingLen + 0.5) + "╝")

      if len(lines) > self.height - 4:
        raise Exception("Too much text for messageBox.")

      for y, line in enumerate(lines):
        self.printAt(line, 4, (self.height - len(lines))//2 + y)

      self.refresh()
      while not self.isKeyPressed(' '):
        self.refresh()

      self.screen = copy.deepcopy(screen)

    def border(self):
        for x in range(1, self.width - 2):
            self.screen[0][x] = '-'
            self.screen[self.height - 1][x] = '-'
        for y in range(1, self.height - 1):
            self.screen[y][0] = '|'
            self.screen[y][self.width - 2] = '|'
        self.screen[0][0] = '.'
        self.screen[0][self.width - 2] = '.'
        self.screen[self.height - 1][0] = '\''
        self.screen[self.height - 1][self.width - 2] = '\''

    def printAt(self, text, x, y, colour=None, bgcolour=None):
        if colour is None:
          colour = [255,255,255]
        elif type(colour) != list:
          colour = self.colours[colour]

        if bgcolour is None:
            bgcolour = [0,0,0]
        elif type(bgcolour) != list:
          bgcolour = self.colours[bgcolour]

        x = int(x)
        y = int(y)
        if y < 0 or y > self.height - 1:
          return
        for dx, ch in enumerate(text):            
            if (x + dx) < 0:
              continue
            elif (x + dx) > self.width - 1:
              return
            
            # transparency
            if ch == '.':
              continue

            self.screen[y][x + dx] = ch

            if self.colourMode:
                self.colour_screen[y][x + dx] = [colour[0],
                                                 colour[1],
                                                 colour[2],
                                                 bgcolour[0],
                                                 bgcolour[1],
                                                 bgcolour[2]]
                                    
    def getCharAt(self, x, y):
        return self.screen[int(y)][int(x)]

    # alias for refresh
    def reveal(self):
      return self.refresh()
        
    def refresh(self):
      print("\033[%d;%dH" % (0, 0))
      prevColourCode = ""
      for row in range(len(self.screen)):
        line = ""
        for col in range(len(self.screen[0])):
          colour = self.colour_screen[row][col]
          colourCode = "\033[38;2;%d;%d;%dm\033[48;2;%d;%d;%dm" % ( colour[0],
                                                                    colour[1],
                                                                    colour[2],
                                                                    colour[3],
                                                                    colour[4],
                                                                    colour[5] )
          
          if colourCode == prevColourCode:
            line += self.screen[row][col]# + " "  
          else:
            line += colourCode + self.screen[row][col]# + " "
          prevColourCode = colourCode
        print(line, flush=True) 

      # clearing the glitch on the right side of the screen
      # when a double replacement character � is glitched instead of an emoji
      print("\033[0m")
      for row in range(len(self.screen) + 1):
        print("\033[%d;%dH " % (row, len(self.screen[0]) + 1)) 

      # updating keys and mouse position
      for key in range(512):
          self.keys[key] = False   
      self.keys["vpad_up"] = False
      self.keys["vpad_down"] = False
      self.keys["vpad_left"] = False
      self.keys["vpad_right"] = False

      self.oldflags = fcntl.fcntl(self.fd, fcntl.F_GETFL)
      fcntl.fcntl(self.fd, fcntl.F_SETFL, self.oldflags | os.O_NONBLOCK)   

      try:
        try:
          c = sys.stdin.read(1)
          while len(c) > 0:
            if c == "\033":
              # escape character detected
              c = sys.stdin.read(1)      
              if c == "[":
                c = sys.stdin.read(1)      
                if c == "<":
                  # mouse state updated!
                  data = ""
                  c = sys.stdin.read(1)
                  while len(c) > 0:
                    data += c
                    c = sys.stdin.read(1)
                  coords = data.split(";")
                  self.mouse_x = int(coords[1]) - 1
                  m_char = coords[2].find('M')
                  if m_char == -1:
                    m_char = coords[2].find('m')
                  self.mouse_y = int(coords[2][:m_char]) - 1
                  
                  if self.mouse_x <= 4:
                    self.keys["vpad_left"] = True
                  elif self.mouse_x >= self.width - 4:
                    self.keys["vpad_right"] = True
                  if self.mouse_y <= 4:
                    self.keys["vpad_up"] = True
                  elif self.mouse_y >= self.height - 4:
                    self.keys["vpad_down"] = True    
              else:
                # escape key pressed, bail
                self.teardown()
                return False                  
            else:
              self.keys[ord(c)] = True
              # ESCAPE key pressed, finish
            c = sys.stdin.read(1)                   
        except IOError: 
          pass
      finally:
        fcntl.fcntl(self.fd, fcntl.F_SETFL, self.oldflags)

      if self.fps is not None:
          sleep(1 / self.fps)
      return True
                                 
    def isKeyPressed(self, key):
      if len(key) == 1:
        return self.keys[ord(key)]    
      else:
        return self.keys[key]

    def setFPS(self, fps):
        self.fps = fps
        
####################################################################
#                     Helper functions                             #
####################################################################        
from math import copysign
def getSign(value):
    return copysign(1, value)

class Sprite:
  def __init__(self, screen, text = "", x = 0, y = 0):
    self.screen = screen
    self.x = x
    self.y = y
    self.text = text
    self.width = len(text)

  def draw(self):
    self.screen.printAt(self.text, self.x, self.y)

  def contains(self, point, horiz_margin = 0, vert_margin = 0, top_margin = 1, bottom_margin = 2, left_margin = 0, right_margin = 0):
    if vert_margin > top_margin:
      top_margin = vert_margin
    if vert_margin > bottom_margin:
      bottom_margin = vert_margin

    if horiz_margin > left_margin:
      left_margin = horiz_margin
    if horiz_margin > right_margin:
      right_margin = horiz_margin    

    return point.x >= self.x - left_margin and \
            point.x <= self.x + len(self.text) + right_margin and \
            point.y >= self.y - top_margin and \
            point.y <= self.y + bottom_margin
'''
class TimeWeather:
  cities = ["melbourne", "sydney", "brisbane"]

  weather = { "melbourne": [],
              "sydney": [],
              "brisbane": [],}

  def getTemp(city):
    from requests import get
    from bs4 import BeautifulSoup    

    current_datetime = TimeWeather.getTime(city)
    city = city.lower()

    if len(TimeWeather.weather[city]) > 0:
      if (current_datetime - TimeWeather.weather[city][0]).total_seconds() < 60 * 5:
        #print("cached weather")
        return TimeWeather.weather[city][1]

    page = get(f"http://www.bom.gov.au/vic/observations/{city}.shtml")   
    soup = BeautifulSoup(page.content, 'html.parser')
    temp = soup.find('tr', class_="rowleftcolumn").find_all('td')[1].text
    TimeWeather.weather[city] = [current_datetime, temp]

    #print("fetched weather")
    return temp

  def getTime(city):
    from datetime import datetime
    import pytz

    if city.lower() in TimeWeather.cities:
      tz = pytz.timezone('Australia/' + city.lower()) 
      return datetime.now(tz)
    else:
      raise "Unknown city"  
'''
