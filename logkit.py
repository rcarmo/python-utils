#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2012, Rui Carmo
Description: Utility functions
License: MIT (see LICENSE.md for details)
"""

import json
import logging
import os

log = logging.getLogger()

from collections import deque

from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import TerminalFormatter, Terminal256Formatter, NullFormatter


class InMemoryHandler(logging.Handler):
    """In memory logging handler with a circular buffer"""

    def __init__(self, limit=8192):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Our custom argument
        self.limit = limit
        self.flush()

    def emit(self, record):
        self.records.append(self.format(record))

    def flush(self):
        self.records = deque([], self.limit)

    def dump(self):
        return self.records
        

class ColorFormatter(logging.Formatter) :
    """Console logging formatter with coloring"""
    _colors  = {
      "DEBUG"   : "\033[22;32m", # green
      "INFO"    : "\033[01;34m", # violet
      "WARNING" : "\033[22;35m", # magenta
      "ERROR"   : "\033[22;31m", # red
      "CRITICAL": "\033[01;31m"  # bold red
    };

    def format(self, record):
        if 'color' in os.environ.get('TERM', ''):
            if(self._colors.has_key(record.levelname)):
                record.levelname = "%s%s\033[0;0m" % (self._colors[record.levelname],  record.levelname)
            record.msg = "\033[37m\033[1m%s\033[0;0m" % record.msg
        return logging.Formatter.format(self, record)  


class PygmentsHandler(logging.StreamHandler):
    """Console logging handler with syntax highlighting"""

    def __init__(self, stream=None, syntax="guess", encoding='utf-8', style='default'):
        # run the regular Handler __init__
        logging.StreamHandler.__init__(self,stream)
        self.pformatter = (Terminal256Formatter(encoding=encoding, style=style)
             if '256color' in os.environ.get('TERM', '')
             else TerminalFormatter(encoding=encoding,style=style))
        if not stream.isatty():
            self.pformatter = NullFormatter
        if syntax == "guess":
            self.lexer = guess_lexer
        else:
            self.lexer = get_lexer_by_name(syntax)

    def emit(self, record):
        if self.pformatter == NullFormatter:
            return
        msg = self.format(record)
        # Note that the guessing also applies to any log formatting
        if self.lexer == guess_lexer:
            lexer = guess_lexer(msg)
            self.stream.write(highlight(msg,lexer,self.pformatter))
            return
        self.stream.write(highlight(msg,self.lexer,self.pformatter))


def json_ansi(item, stream, sort_keys=True, indent=0, separators=(',', ':'), encoding='utf-8', style='default'):
    """Helper function to pretty-print JSON via Pygments"""

    formatter = (Terminal256Formatter(encoding=encoding,style=style)
        if '256color' in os.environ.get('TERM', '')
        else TerminalFormatter(encoding=encoding,style=style))
    if not stream.isatty():
        formatter = NullFormatter
    lexer = get_lexer_by_name('json')
    stream.write(highlight(json.dumps(item,sort_keys, indent, separators),lexer,formatter))
