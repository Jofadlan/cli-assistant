import bcrypt
from models.user import User


class AuthManager:
    def __init__(self, db):
        self.db = db
        self._current_user = None

    @property
    def is_logged_in(self):
        return self._current_user is not None

    @property
    def current_user(self):
        return self._current_user

    def register(self, username, password):
        existing = self.db.fetch_one(
            "SELECT id FROM users WHERE username = %s", (username,)
        )
        if existing:
            return False, "Username sudah dipakai"

        password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        _, err = self.db.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, password_hash),
        )
        if err:
            return False, f"Gagal register: {err}"
        return True, "Register berhasil"

    def login(self, username, password):
        row = self.db.fetch_one(
            "SELECT id, username, password_hash FROM users WHERE username = %s",
            (username,),
        )
        if not row:
            return False, "Username tidak ditemukan"

        if not bcrypt.checkpw(password.encode("utf-8"), row["password_hash"].encode("utf-8")):
            return False, "Password salah"

        self._current_user = User(
            id=row["id"], username=row["username"]
        )
        return True, "Login berhasil"

    def logout(self):
        self._current_user = None
        return True, "Logout berhasil"
