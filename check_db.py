from app import app
from models import db, User, Bill
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'visData.db')

def init_db():
    with app.app_context():
        db.create_all()
    print(f"Database initialized at {DB_PATH}")
    
def show_tables():
    with app.app_context():
        users = User.query.all()
        bills = Bill.query.all()
        print("Users:")
        for user in users:
            print(user)
        print("\nBills:")
        for bill in bills:
            print(bill)
            
if __name__ == '__main__':
    # init_db()
    show_tables()