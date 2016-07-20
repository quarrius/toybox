#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import uuid
import datetime

from peewee import *
from playhouse.db_url import connect as db_connect
import boto3

from .config import CFG
from .db import DATABASE
from .cache import CACHE
from .xattr import XattrProxy_Redis_DynamoDB

dynamodb = boto3.resource('dynamodb')

DYNAMODB_TABLE_PREFIX   = 'quarrius-'

class ToyboxModel(Model):
    guid            = UUIDField(index=True, default=uuid.uuid4)

    created_at      = DateTimeField(default=datetime.datetime.utcnow)
    active          = BooleanField(default=True)

    class Meta:
        database = DATABASE

    class MetaXattr:
        cache = CACHE
        nosql_database = None

    def __init__(self, *args, **kwargs):
        super(ToyboxModel, self).__init__(*args, **kwargs)
        if self.__class__.MetaXattr.nosql_database is None:
            self.__class__.MetaXattr.nosql_database = \
                dynamodb.Table(DYNAMODB_TABLE_PREFIX + self._name_token)
        self.__xattr_proxy = XattrProxy_Redis_DynamoDB(self,
            self.__class__.MetaXattr.cache,
            self.__class__.MetaXattr.nosql_database,
        )

    @property
    def xattr(self):
        return self.__xattr_proxy

    @property
    def _name_token(self):
        return self.__class__.__name__.lower()


class User(ToyboxModel):
    username        = CharField(unique=True)
    password        = CharField()
    email_addr      = CharField(unique=True)

class World(ToyboxModel):
    user            = ForeignKeyField(User, 'worlds')

    name            = CharField()
    api_key         = UUIDField(index=True, default=uuid.uuid4)
    map_token       = CharField(index=True, default=uuid.uuid4)

class Dimension(ToyboxModel):
    world           = ForeignKeyField(World, 'dimensions')

    name            = CharField()
