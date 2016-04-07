#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Decorator functions

Created by: Rui Carmo
"""

from bottle import request, response, route, abort
import time, binascii, hashlib, email.utils, functools, json, cProfile, collections
from datetime import datetime
import logging
from core import tb

# Allow importing even when Redis bindings aren't present
try:
    from redis import StrictRedis as Redis
except ImportError:
    pass

log = logging.getLogger()

gmt_format_string = "%a, %d %b %Y %H:%M:%S GMT"


class CustomEncoder(json.JSONEncoder):
    """Custom encoder that serializes datetimes into JS-compliant times"""

    def default(self, obj):
        if isinstance(obj, datetime):
            epoch = datetime.utcfromtimestamp(0)
            delta = obj - epoch
            return int(delta.total_seconds()) * 1000
        return json.JSONEncoder.default(self, obj)


def cache_redis(r, prefix='url', ttl=3600):
    """Cache route results in Redis"""

    def decorator(callback):
        @functools.wraps(callback)
        def wrapper(*args, **kwargs):
            try:
                item = json.loads(r.get('%s:%s' % (prefix,request.urlparts.path)))
                body = item['body']
                for h in item['headers']:
                    response.set_header(str(h), item['headers'][h])
                response.set_header('X-Source', 'Redis')
            except Exception as e:
                log.debug("Redis cache miss for %s" % request.urlparts.path)
                body = callback(*args, **kwargs)
                item = {
                    'body': body,
                    'headers': dict(response.headers),
                    'mtime': int(time.time())
                }
                k = '%s:%s' % (prefix, request.urlparts.path)
                r.set(k, json.dumps(item))
                r.expire(k, ttl)
            return body
        return wrapper
    return decorator


def cache_results(timeout=0):
    """Cache route results for a given period of time"""

    def decorator(callback):
        _cache = {}
        _times = {}

        @functools.wraps(callback)
        def wrapper(*args, **kwargs):

            def expire(when):
                for t in [k for k in _times.keys()]:
                    if (when - t) > timeout:
                        del(_cache[_times[t]])
                        del(_times[t])

            now = time.time()
            try:
                item = _cache[request.urlparts]
                if 'If-Modified-Since'  in request.headers:
                    try:
                        since = time.mktime(email.utils.parsedate(request.headers['If-Modified-Since']))
                    except:
                        since = now
                    if item['mtime'] >= since:
                        expire(now)
                        abort(304,'Not modified')
                for h in item['headers']:
                    response.set_header(str(h), item['headers'][h])
                body = item['body']
                response.set_header('X-Source', 'Worker Cache')
            except KeyError:
                body = callback(*args, **kwargs)
                item = {
                    'body': body,
                    'headers': response.headers,
                    'mtime': int(now)
                }
                _cache[request.urlparts] = item
                _times[now] = request.urlparts

            expire(now)
            return body
        return wrapper
    return decorator


def cache_control(seconds = 0):
    """Insert HTTP caching headers"""

    def decorator(callback):
        @functools.wraps(callback)
        def wrapper(*args, **kwargs):
            expires = int(time.time() + seconds)
            expires = time.strftime(gmt_format_string, time.gmtime(expires))
            response.set_header('Expires', expires)
            if seconds:
                pragma = 'public'
            else:
                pragma = 'no-cache, must-revalidate'
            response.set_header('Cache-Control', "%s, max-age=%s" % (pragma, seconds))
            response.set_header('Pragma', pragma)
            return callback(*args, **kwargs)
        return wrapper
    return decorator


def profile(filename=None):
    """Profiling decorator for functions taking one or more arguments"""

    def decorator(callback):
        @functools.wraps(callback)
        def wrapper(*args, **kwargs):
            import cProfile
            import logging
            log.info('Profiling %s' % (callback.__name__))
            try:
                profiler = cProfile.Profile()
                res = profiler.runcall(callback, *args, **kwargs)
                profiler.dump_stats(filename or '%s_fn.profile' % (callback.__name__))
            except IOError:
                log.exception(_("Could not open profile '%(filename)s'") % {"filename": filename})
            return res
        return wrapper
    return decorator


def timed(callback):
    """Decorator for timing route processing"""

    @functools.wraps(callback)
    def wrapper(*args, **kwargs):
        start = time.time()
        body = callback(*args, **kwargs)
        end = time.time()
        response.set_header('X-Processing-Time', str(end - start))
        return body
    return wrapper


def jsonp(callback):
    """Decorator for JSONP handling"""

    @functools.wraps(callback)
    def wrapper(*args, **kwargs):
        body = callback(*args, **kwargs)
        try:
            body = json.dumps(body, cls=CustomEncoder)
            # Set content type only if serialization successful
            response.content_type = 'application/json'
        except Exception, e:
            return body

        callback_function = request.query.get('callback')
        if callback_function:
            body = ''.join([callback_function, '(', body, ')'])
            response.content_type = 'text/javascript'

        response.set_header('Last-Modified', time.strftime(gmt_format_string, time.gmtime()))
        response.set_header('ETag', binascii.b2a_base64(hashlib.sha1(body).digest()).strip())
        response.set_header('Content-Length', len(body))
        return body
    return wrapper


def memoize(f):
    """Memoization decorator for functions taking one or more arguments"""

    class memodict(dict):
        def __init__(self, f):
            self.f = f

        def __call__(self, *args):
            return self[args]

        def __missing__(self, key):
            res = self[key] = self.f(*key)
            return res

        def __repr__(self):
            return self.f.__doc__
        
        def __get__(self, obj, objtype):
            return functools.partial(self.__call__, obj)
    return memodict(f)


def lru_cache(limit=100):
    """Least-recently-used cache decorator"""

    def inner_function(callback):
        cache = collections.OrderedDict()

        @functools.wraps(callback)
        def wrapper(*args, **kwargs):
            key = args
            if kwargs:
                key += tuple(sorted(kwargs.items()))
            try:
                result = cache.pop(key)
            except KeyError:
                result = callback(*args, **kwargs)
                if len(cache) >= limit:
                    cache.popitem(0)
            cache[key] = result # refresh position
            return result
        return wrapper
    return inner_function
