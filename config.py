#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import random
import logging

import dns.resolver
import redis


CONFIG_DOMAIN = 'config.quarri.local'

logger = logging.getLogger(__name__)

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

        config_host, config_port = config_endpoint.split(':', 1)
        config_port = int(config_port)

    logger.debug('Using config endpoint: %s:%d', config_host, config_port)
    return redis.StrictRedis(host=config_host, port=config_port)

CFG = CFG_INIT()
