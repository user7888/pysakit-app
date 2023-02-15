from db import db
from flask import session
from sqlalchemy import text

def get_stops():
    sql = text('SELECT S.id, S.hsl_id, S.name, S.owner, S.visible FROM stops S, users U WHERE S.owner=U.id AND S.visible ORDER BY s.id DESC')
    result = db.session.execute(sql)
    stop_list = result.fetchall()
    return stop_list

def delete(hsl_id):
    sql = text('UPDATE stops SET visible=FALSE WHERE hsl_id=:hsl_id')
    db.session.execute(sql, {"hsl_id": str(hsl_id)})
    db.session.commit()
    return


