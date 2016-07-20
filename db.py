#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os

from peewee import SqliteDatabase, PostgresqlDatabase
from playhouse.db_url import connect

from .config import CFG

def DATABASE_INIT(db_uri=None):
    if db_uri is None:
        db_uri = CFG.get('config:toybox:DATABASE_URI')
    return connect(db_uri)

DATABASE = DATABASE_INIT()
