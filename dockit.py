#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2012, Rui Carmo
Description: Docstring utility functions
License: MIT (see LICENSE.md for details)
"""

import logging
import inspect
from bottle import app

log = logging.getLogger()

def docs():
    """Gather all docstrings related to routes and return them grouped by module"""

    routes = []
    modules = {}
    for route in app().routes:
        doc = inspect.getdoc(route.callback) or inspect.getcomments(route.callback)
        if not doc:
            doc = ''
        module = inspect.getmodule(route.callback).__name__
        item = {
            'method': route.method,
            'route': route.rule,
            'function': route.callback.__name__,
            'module': module,
            'doc': inspect.cleandoc(doc)
        }
        if not module in modules:
            modules[module] = []
        modules[module].append(item)
    return modules