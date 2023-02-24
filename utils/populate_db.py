from app import app
import stops

def insert_stops():
    with app.app_context():
        stops.insert_all_stops()

if __name__ == "__main__":
    insert_stops()