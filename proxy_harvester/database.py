import sqlite3


class ProxyDatabase:
    """Database."""
    def __init__(self):
        self._connection: sqlite3.Connection | None = None

    def connect(self):
        try:
            self._connection = sqlite3.connect('sqlite_python.db')
            cursor = self._connection.cursor()
            print("Database created")  # TODO logging

            sqlite_select_query = "select sqlite_version();"
            cursor.execute(sqlite_select_query)
            print(f"Database version SQLite: {cursor.fetchall()}")  # TODO logging
            cursor.close()
        except sqlite3.Error as error:
            print("Error connecting to sqlite", error)  # TODO logging

    def close_connection(self):
        if self._connection:
            self._connection.close()
            print("Connection closed")  # TODO logging