import sqlite3
import threading

class Database:
    def __init__(self, db_name='appointments.db'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.lock = threading.Lock()
        self._create_tables()

    def _create_tables(self):
        with self.lock:
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                    user_id INTEGER PRIMARY KEY,
                                    name TEXT,
                                    email TEXT,
                                    phone_number TEXT,
                                    age INTEGER,
                                    appointment_status TEXT)''')
            
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS bookings (
                                    booking_id INTEGER PRIMARY KEY,
                                    user_id INTEGER,
                                    date TEXT,
                                    time TEXT,
                                    status TEXT,
                                    FOREIGN KEY (user_id) REFERENCES users (user_id))''')
            self.conn.commit()

    def execute(self, query, params=None):
        with self.lock:
            if params:
                return self.cursor.execute(query, params)
            return self.cursor.execute(query)

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()