#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import uuid
import datetime

from peewee import *

from .db import DB_OBJ
from .xattr import ExtendedAttributeProxy

class ToyboxModel(Model):
    guid            = UUIDField(index=True, default=uuid.uuid4)

    created_at      = DateTimeField(default=datetime.datetime.utcnow)
    active          = BooleanField(default=True)

    class Meta:
        database = DB_OBJ

    class MetaXattr:
        cache = None
        nosql_database = None

    @classmethod
    def init_xattr(cls, cache, nosql_db):
        cls.MetaXattr.cache = cache
        cls.MetaXattr.nosql_database = nosql_db

    def __init__(self, *args, **kwargs):
        super(ToyboxModel, self).__init__(*args, **kwargs)
        self.__xattr_proxy = ExtendedAttributeProxy(self,
            self.__class__.MetaXattr.cache,
            self.__class__.MetaXattr.nosql_database,
        )

    @property
    def xattr(self):
        return self.__xattr_proxy



class User(ToyboxModel):
    username        = CharField(unique=True)
    password        = CharField()
    email_addr      = CharField(unique=True)

class World(ToyboxModel):
    user            = ForeignKeyField(User, 'worlds')

    name            = CharField()
    api_key         = UUIDField(index=True, default=uuid.uuid4)
    map_token       = CharField(index=True, default=uuid.uuid4)
