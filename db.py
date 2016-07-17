#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os

from peewee import SqliteDatabase, PostgresqlDatabase
from playhouse.db_url import parse

if os.environ.get('TOYBOX_TESTING'):
    DB_OBJ = SqliteDatabase(None)
else:
    DB_OBJ = PostgresqlDatabase(None)

def DB_INIT(db_uri):
    db_cfg = parse(db_uri)
    db_name = db_cfg['database']
    del db_cfg['database']

    DB_OBJ.init(db_name, **db_cfg)
    return DB_OBJ
