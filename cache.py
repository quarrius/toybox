#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import logging

import redis

from .config import CFG

logger = logging.getLogger(__name__)

def CACHE_INIT(cache_endpoint=None):
    if cache_endpoint is None:
        cache_host, cache_port = CFG.mget([
            'config:toybox:CACHE_HOST', 'config:toybox:CACHE_PORT'])
    else:
        cache_host, cache_port = cache_endpoint.split(':', 1)
        cache_port = int(cache_port)
    logger.debug('Using cache endpoint: %s:%d', cache_host, cache_port)
    return redis.StrictRedis(host=cache_host, port=cache_port)

CACHE = CACHE_INIT()
