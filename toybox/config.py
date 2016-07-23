#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import os.path
import random
import logging
from codecs import open

import dns.resolver
import redis
import yaml


CONFIG_DOMAIN = 'config.quarri.local'

logger = logging.getLogger(__name__)

class ConfigFileWrapper(object):
    def __init__(self, config_file):
        with open(config_file, encoding='utf-8') as fd:
            self._config = yaml.safe_load(fd)

    def get(self, key):
        v =  self._config
        for key_part in key.split(':'):
            try:
                v = v[key_part]
            except KeyError:
                return None
        return v

def CFG_INIT():
    try:
        answers = dns.resolver.query(CONFIG_DOMAIN, 'SRV')
        config_host, config_port = random.choice([(a.target.to_text(), a.port) \
            for a in answers])
    except (IndexError, dns.resolver.NXDOMAIN) as resolver_err:
        # no domain found, probably running locally?
        logger.warn('Failed to retrieve config SRV record from <%s>: %s',
            CONFIG_DOMAIN, resolver_err)

        config_endpoint = os.environ.get('TOYBOX_CONFIG', None)
        if config_endpoint is None:
            logger.error('ENV[TOYBOX_CONFIG] not set, no config endpoint available')
            raise ValueError('No config endpoint available')
        else:
            if os.path.exists(config_endpoint):
                logger.debug('Using config file: %s', config_endpoint)
                return ConfigFileWrapper(config_endpoint)
            else:
                config_host, config_port = config_endpoint.split(':', 1)
                config_port = int(config_port)

    logger.debug('Using config endpoint: %s:%d', config_host, config_port)
    return redis.StrictRedis(host=config_host, port=config_port)

CFG = CFG_INIT()
