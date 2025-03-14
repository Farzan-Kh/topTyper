from game import SpeedTypingApp
from db import Database

def main():
    # Initialize the database
    db = Database("resources/db/speed_typing.db")
    db.create_table()

    # Start the Textual app
    app = SpeedTypingApp(db)
    app.run()

if __name__ == "__main__":
    main()