import mysql.connector
from mysql.connector import Error


class Database:
    def __init__(self, host, user, password, database):
        self._config = {
            "host": host,
            "user": user,
            "password": password,
            "database": database,
        }
        self._connection = None

    def connect(self):
        try:
            self._connection = mysql.connector.connect(**self._config)
            return True
        except Error as e:
            print(f"[DB ERROR] Gagal koneksi: {e}")
            return False

    def disconnect(self):
        if self._connection and self._connection.is_connected():
            self._connection.close()

    def execute(self, query, params=None):
        try:
            cursor = self._connection.cursor()
            cursor.execute(query, params or ())
            self._connection.commit()
            cursor.close()
            return cursor.rowcount, None
        except Error as e:
            return None, str(e)

    def fetch(self, query, params=None):
        try:
            cursor = self._connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            return []

    def fetch_one(self, query, params=None):
        try:
            cursor = self._connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            return None

    @property
    def is_connected(self):
        return self._connection and self._connection.is_connected()
