import sqlite3

class Database:
    def __init__(self, db_name="../resources/db/speed_typing.db"):
        """
        Initialize the Database class with the database name.
        """
        self.db_name = db_name

    def create_table(self):
        """
        Create the records table if it doesn't already exist.
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    wpm REAL NOT NULL,
                    accuracy REAL NOT NULL
                )
            """)
            conn.commit()

    def save_record(self, username, wpm, accuracy):
        """
        Save a player's record to the database.
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO records (username, wpm, accuracy)
                VALUES (?, ?, ?)
            """, (username, wpm, accuracy))
            conn.commit()

    def fetch_records(self):
        """
        Fetch all records from the database.
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username, wpm, accuracy FROM records")
            return cursor.fetchall()