#!/usr/bin/env python2
# -*- coding: utf-8 -*-

class ExtendedAttributeProxy(DictMixin):
    KEY_SEP         = ':'

    def __init__(self, parent, cache, db):
        self.__parent = parent
        self.__local_cache = {}
        self.__key_prefix = self._get_key_prefix(parent)

        self._cache = cache
        self._db = db

    def _get_key(self, key):
        cache_key = self.__key_prefix + key
        value = self.__local_cache.get(key, None)
        if value is None:
            # not in local object cache, check remote cache
            value = self._cache.get(cache_key)
        if value is None:
            # not in remote cache, check backend db
            resp = self._db.get_item(
                Key={'guid': self.__parent.guid},
                AttributesToGet=[
                    key,
                ],
            )
            value = resp['Item'][key]
        if value is not None:
            self._cache.set(cache_key, value)
            self.__local_cache[key] = value
        return value


    def _set_key(self, key, value):
        cache_key = self.__key_prefix + key
        self._db.put_item(
            Item={
                'guid': self.__parent.guid,
                key: value,
            }
        )
        self._cache.set(cache_key, value)
        self.__local_cache[key] = value
        return True

    def _get_key_prefix(self, parent):
        return (self.KEY_SEP.join([
            'data',
            parent.__class__.__name__,
            parent.guid,
            'xattr',
        ]) + self.KEY_SEP).encode('utf-8')
