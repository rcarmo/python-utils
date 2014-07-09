#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2012, Rui Carmo
Description: File utility functions
License: MIT (see LICENSE.md for details)
"""

import os
import sys
import logging
import zipfile

log = logging.getLogger()

def path_for(name, script=__file__):
    """Build absolute paths to resources based on app path"""

    if 'uwsgi' in sys.argv:
        return os.path.join(os.path.abspath(os.path.join(os.path.dirname(script),'..')),name)
    return os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]),name))


def locate(pattern, root=os.getcwd()):
    """Generator for iterating inside a file tree"""

    for path, dirs, files in os.walk(root):
        for filename in [os.path.abspath(os.path.join(path, filename)) for filename in files if fnmatch.fnmatch(filename, pattern)]:
            yield filename


def walk(top, topdown=True, onerror=None, followlinks=False, ziparchive=None, zipdepth=0):
    """Reimplementation of os.walk to traverse ZIP files as well"""

    try:
        if (os.path.splitext(top)[1]).lower() == '.zip':
            if ziparchive:
                # skip nested ZIPs.
                yield top, [], []
            else:
                ziparchive = zipfile.ZipFile(top)
            names = list(set(map(lambda x: [p+'/' for p in x.split('/') if p != ""][zipdepth],ziparchive.namelist())))
        else:
            names = os.listdir(top)
    except error, err:
        if onerror is not None:
            onerror(err)
        return

    dirs, nondirs = [], []
    if ziparchive:
        for name in names:
            if name == '__MACOSX/':
                continue
            if name[-1::] == '/':
                dirs.append(name)
            else:
                nondirs.append(name)
    else:        
        for name in names:
            if os.path.isdir(os.path.join(top, name)):
                dirs.append(name)
            else:
                nondirs.append(name)
    if topdown:
        yield top, dirs, nondirs
    for name in dirs:
        new_path = os.path.join(top, name)
        if ziparchive:
            for x in walk(new_path, topdown, onerror, followlinks):
                yield x
        else:
            if followlinks or not islink(new_path):
                for x in walk(new_path, topdown, onerror, followlinks):
                    yield x
    if not topdown:
        yield top, dirs, nondirs