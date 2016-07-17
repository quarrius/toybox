#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import uuid
import datetime

from peewee import *
from playhouse.fields import PasswordField
from playhouse.db_url import parse

if os.environ.get('TOYBOX_TESTING'):
    DB_OBJ = SqliteDatabase(None)
else:
    DB_OBJ = PostgresqlDatabase(None)

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

def db_config(db_uri):
    cfg = parse(db_uri)
    db_name = cfg['database']
    del cfg['database']
    return db_name, cfg
