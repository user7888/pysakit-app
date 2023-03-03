from app import app
from db import db
from sqlalchemy import text
import stops

def clear_database ():
    tables = ['stops', 'routes', 'stops_and_users', 'routes_and_stops']
    for table in tables:
        sql = f'TRUNCATE TABLE {table}'
        db.session.execute(text(sql))
    db.session.commit()

def insert_stops():
    with app.app_context():
        stops.insert_all_stops()
