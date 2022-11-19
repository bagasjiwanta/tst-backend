import sqlite3
from flask import g
from enum import Enum

dbpath = "database/database.db"

# get database singleton instance
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(dbpath)
    return db


# query to database
def queryc(query, args=(), one=False, type="select"):
    cursor = get_db().execute(query, args)
    if type == "select":
        result = cursor.fetchall()
        cursor.close()
        return (result[0] if result else None) if one else result
    else:
        get_db().commit()
        cursor.close()
        if type == "insert":
            return cursor.lastrowid
        else :
            return cursor.rowcount
        