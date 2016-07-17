#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import uuid
import datetime

from peewee import *
from playhouse.fields import PasswordField
from playhouse.db_url import connect

DB_OBJ = Proxy()

class ToyboxModel(Model):
    guid            = UUIDField(index=True, default=uuid.uuid4)

    created_at      = DateTimeField(default=datetime.datetime.utcnow)
    active          = BooleanField(default=True)

    class Meta:
        database = DB_OBJ

class User(ToyboxModel):
    user_name       = CharField(unique=True)
    # TODO: replace, probably won't work in lambda
    password        = PasswordField()
    email_addr      = CharField(unique=True)
    email_verified  = BooleanField(default=False)

class World(ToyboxModel):
    user            = ForeignKeyField(User, 'worlds')

    name            = CharField()
    api_key         = UUIDField(index=True, default=uuid.uuid4)
    map_token       = CharField(index=True, default=uuid.uuid4)

def db_init_proxy(db_uri):
    db_actual = connect(db_uri)
    DB_OBJ.initialize(db_actual)
    return db_actual
