#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import collections
import json
import logging

class XattrDictMixin(collections.MutableMapping):
    def __getitem__(self, key):
        if self._is_mkey(key):
            return self._get_mkey(key)
        return self._get_key(key)

    def __setitem__(self, key, value):
        if self._is_mkey(key):
            return self._set_mkey(key, value)
        return self._set_key(key, value)

    def __delitem__(self, key):
        return self._del_key(key)

    # these 3 methods only look at the local cache because
    # retrieving attributes/keys from remote cache and dynamodb
    # would be expensive
    def __len__(self):
        return len(self._local_cache)

    def __iter__(self):
        return self._local_cache.iterkeys()

    def __contains__(self, key):
        return key in self._local_cache

    def update(self, other):
        return self._set_mkey(other.keys(), other.values())

    def _is_mkey(self, key):
        return isinstance(key, (tuple, list))

class XattrProxyMixin(object):
    KEY_PATH_SEP            = ':'
    DEFAULT_CACHE_LENGTH    = 1 * 3600
    DEFAULT_ID_FIELD        = 'guid'

    def __init__(self, parent, cache_backend, db_backend,
            id_field=DEFAULT_ID_FIELD, cache_time=DEFAULT_CACHE_LENGTH):
        self._id_field = id_field
        self._cache_ttl = cache_time
        self._parent_obj_guid = str(getattr(parent, self._id_field))
        self._key_prefix = self._get_key_prefix(parent)

        self._cache = cache_backend
        self._db = db_backend
        self._local_cache = {}
        self._log = logging.getLogger('{}:{}:{}'.format(
            __name__, parent._name_token, self._parent_obj_guid))

    def _get_key_prefix(self, parent):
        return (self.KEY_PATH_SEP.join([
            'data',
            parent._name_token,
            self._parent_obj_guid,
            'xattr',
        ]) + self.KEY_PATH_SEP).encode('utf-8')

    def _get_key(self, key):
        raise NotImplementedError()

    def _get_mkey(self, keys):
        return {key: self._get_key(key) for key in keys}

    def _set_key(self, key, value):
        raise NotImplementedError()

    def _set_mkey(self, keys, values):
        for key, value in zip(keys, values):
            self._set_key(key, value)

    def _del_key(self, key):
        raise NotImplementedError()

    def _del_mkey(self, keys):
        for key in keys:
            self._del_key(key)

class XattrProxy_Testing(XattrProxyMixin, XattrDictMixin):
    def _get_key(self, key):
        return self._local_cache[key]

    def _set_key(self, key, value):
        self._local_cache[key] = value

    def _del_key(self, key):
        del self._local_cache[key]

class XattrProxy_Redis_DynamoDB(XattrProxyMixin, XattrDictMixin):
    def _get_key(self, key):
        cache_key = self._key_prefix + key
        try:
            return self._local_cache[key]
        except KeyError as local_err:
            value = self._cache.get(cache_key)
            if value is not None:
                value = self._unpack_value(value)
                self._local_cache[key] = value
                return value
            else:
                # If we have to go all the way back to dynamodb, might as well
                # grab all the attributes at once and cache them
                resp = self._db.get_item(
                    Key={self._id_field: self._parent_obj_guid},
                )
                try:
                    item = resp['Item']
                    del item[self._id_field]
                except KeyError as db_err:
                    raise local_err
                value = item[key]
                self._cache.mset({self._key_prefix + k: self._pack_value(v) \
                    for k, v in item.iteritems()})
                # mset can't do ttl, have to do it in a seperate step
                with self._cache.pipeline() as cache_pipe:
                    for item_key in item:
                        cache_pipe.expire(item_key, self._cache_ttl)
                    cache_pipe.execute()
                self._local_cache.update(item)
                return value

    def _get_mkey(self, keys):
        values = {k: None for k in keys}
        for k in values:
            try:
                values[k] = self._local_cache[k]
            except KeyError:
                continue
        if not any(v is None for v in values.itervalues()):
            # successfully pulled all values from local cache
            return values
        remaining_keys = [k for k in values if values[k] is None]
        cache_values = [
            self._unpack_value(v) if v is not None else None \
            for v in self._cache.mget([self._key_prefix + k for k in remaining_keys])
        ]
        values.update(dict(zip(remaining_keys, cache_values)))
        if not any(v is None for v in values.itervalues()):
            # successfully pulled all values from remote cache
            return values

        # If we have to go all the way back to dynamodb, might as well
        # grab all the attributes at once and cache them
        resp = self._db.get_item(
            Key={self._id_field: self._parent_obj_guid},
        )
        try:
            values = resp['Item']
            del values[self._id_field]
        except KeyError as db_err:
            # no values set at all for this obj id
            return {}
        self._cache.mset({self._key_prefix + k: self._pack_value(v) \
            for k, v in values.iteritems()})
        # mset can't do ttl, have to do it in a seperate step
        with self._cache.pipeline() as cache_pipe:
            for k in values:
                cache_pipe.expire(k, self._cache_ttl)
            cache_pipe.execute()
        self._local_cache.update(values)
        return values


    def _set_key(self, key, value):
        return self._set_mkey([key], [value])

    def _set_mkey(self, keys, values):
        items = dict(zip(keys, values))
        result = self._db.update_item(
            Key={self._id_field: self._parent_obj_guid},
            UpdateExpression='SET ' + ', '.join(
                '{} = :value{}'.format(k, i) \
                    for i, k in enumerate(keys)
            ),
            ExpressionAttributeValues={
                ':value{}'.format(i): v \
                    for i, v in enumerate(values)
            },
        )
        self._cache.mset({self._key_prefix + k: self._pack_value(v) \
            for k, v in items.iteritems()})
        # mset can't do ttl, have to do it in a seperate step
        with self._cache.pipeline() as cache_pipe:
            for k in keys:
                cache_pipe.expire(k, self._cache_ttl)
            cache_pipe.execute()
        self._local_cache.update(items)
        return True

    def _del_key(self, key):
        return self._del_mkey([key])

    def _del_mkey(self, keys):
        result = self._db.update_item(
            Key={self._id_field: self._parent_obj_guid},
            UpdateExpression='REMOVE ' + ', '.join(
                '{}'.format(k) \
                    for k in keys
            ),
        )
        self._cache.delete([self._key_prefix + k for k in keys])
        for k in keys:
            try:
                del self._local_cache[k]
            except KeyError:
                continue

    def _pack_value(self, value):
        return json.dumps(value)

    def _unpack_value(self, value):
        return json.loads(value)
