#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import random
import logging

import dns.resolver
import redis


CONFIG_DOMAIN = 'config.quarri.local'
CONFIG_DEFAULT_PORT = 6379

logger = logging.getLogger(__name__)

def CFG_INIT(config_domain=CONFIG_DOMAIN):
    config_service = ('localhost', CONFIG_DEFAULT_PORT)
    try:
        answers = dns.resolver.query(CONFIG_DOMAIN, 'SRV')
        config_service = random.choice([(a.target.to_text(), a.port) for a in answers])
    except (IndexError, dns.resolver.NXDOMAIN) as err:
        # no domain found, probably running locally?
        logger.warn('Failed to retrieve config SRV record: %s', err)
        logger.exception(err)

        env_config_service = os.environ.get('QUARRIUS_CONFIG_SERVICE', None)
        if env_config_service is not None:
            logger.debug('Loading config service from env var: %s', env_config_service)
            config_service = env_config_service.split(':', 1)
            # convert the port number to an int
            config_service[1] = int(config_service[1])

    config_host, config_port = config_service
    logger.debug('Using config service: %s:%d', config_host, config_port)
    return redis.StrictRedis(host=config_host, port=config_port)
