#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2014, Rui Carmo
Description: Bottle-specific utility functions
License: MIT (see LICENSE.md for details)
"""

import os
import sys
import logging
import json

log = logging.getLogger()

def inspect_routes(app):
    for route in app.routes:
        if 'mountpoint' in route.config:
            prefix = route.config['mountpoint']['prefix']
            subapp = route.config['mountpoint']['target']

            for prefixes, route in inspect_routes(subapp):
                yield [prefix] + prefixes, route
        else:
            yield [], route

def dump_routes(app):
    for prefixes, route in inspect_routes(app):
        abs_prefix = '/'.join(part for p in prefixes for part in p.split('/'))
        log.warn("Prefix:'%s' Route:'%s' [%s] %s" % (abs_prefix, route.rule, route.method, route.callback))
