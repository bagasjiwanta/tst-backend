import sqlite3
from flask import g, abort
import os

dbpath = "database/database.db"

# get database singleton instance
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(dbpath)
    return db

# query to database
def query(
    query, 
    args = (), 
    one = False, 
    type = "select", 
    store = False, 
    store_id = None
    ):
    if store:
        db = get_store_db(store_id)
        cursor = db.execute(query, args)
    else:
        db = get_db()
        cursor = db.execute(query, args)

    if type == "select":
        result = cursor.fetchall()
        cursor.close()
        if store:
            db.close()
        return (result[0] if result else None) if one else result
    else:
        db.commit()
        cursor.close()
        if store:
            db.close()
        return cursor.lastrowid if type == "insert" else cursor.rowcount


def init_store_db(store_id: int):
    db_path = 'database/store/' + str(store_id) + '.db'
    schema = open('database/store/schema.sql', mode='r')
    db = sqlite3.connect(db_path)
    db.cursor().executescript(schema.read())
    schema.close()
    db.close()


def get_store_db(store_id: int):
    db_path = 'database/store/' + str(store_id) + '.db'
    db_exists = os.path.isfile(db_path)

    if not db_exists:
        init_store_db()
    
    store_db = sqlite3.connect(db_path)
    return store_db

