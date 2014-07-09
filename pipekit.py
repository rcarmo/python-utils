#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2012, Rui Carmo
Description: Pipeline patterns, mostly taken from itertools recipes
License: MIT (see LICENSE.md for details)
"""

import itertools
import collections

def chunk(chunk_size=32):
    """Group chunk_size elements into lists"""

    def chunker(gen):
        gen = iter(gen)
        chunk = []
        try:
            while True:
                for _ in xrange(chunk_size):
                    chunk.append(gen.next())
                yield chunk
                chunk = []
        except StopIteration:
            if chunk:
                yield chunk

    return chunker
 

def flatten(gen):
    """Flatten a sequence, but only one level deep."""

    return itertools.chain.from_iterable(gen)


 
def sink(iter, steps=None):
    """Sink data from an iterator, effecting any results from it being consumed."""
 
    if steps is None:
        # feed the entire iterator into a zero-length deque
        collections.deque(iter, maxlen=0)
    else:
        # advance to the empty slice starting at position 'steps'
        next(itertools.islice(iter, steps, steps), None)



def make_unique(seq, transform=None):
    """Remove duplicate items from a sequence"""
    
    if transform is None: 
        def transform(x): return x 
    seen = {} 
    for item in seq: 
        marker = transform(item) 
        if marker not in seen:
            seen[marker] = True
            yield item


def pipeline(source, functions):
    """Apply an array of functions to a source iterable"""

    return reduce(lambda x, y: y(x), functions, source)


if __name__=='__main__':

    def sum(iter):
        for i in iter:
            yield i + 1

    steps = [
        sum,
        chunk(8),
        chunk(4)
    ]
    p = pipeline(xrange(64), steps)
    for i in p:
        print i

