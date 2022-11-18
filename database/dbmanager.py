import sqlite3
from flask import g

dbpath = "database/database.db"

# get database singleton instance
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(dbpath)
    return db

# query to database
def query(query, args=(), one=False, read=True):
    cursor = get_db().execute(query, args)
    if read:
        result = cursor.fetchall()
        cursor.close()
        return (result[0] if result else None) if one else result
    else:
        get_db().commit()
        cursor.close()
        return cursor.rowcount