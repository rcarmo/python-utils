#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2012, Rui Carmo
Description: Utility functions
License: MIT (see LICENSE.md for details)
"""

import os
import sys
import logging

log = logging.getLogger()

# export commonly-used submodule symbols
from utils.core import Struct, Singleton, get_config, tb
from utils.filekit import path_for, locate
from utils.timekit import time_since