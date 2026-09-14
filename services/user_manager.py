import bcrypt


class UserManager:
    def __init__(self, db):
        self.db = db

    def get_profile(self, user_id):
        return self.db.fetch_one(
            "SELECT id, username, created_at FROM users WHERE id = %s",
            (user_id,),
        )

    def update_profile(self, user_id, field, value):
        allowed = ["username"]
        if field not in allowed:
            return False, f"Field '{field}' tidak valid. Yang boleh: {', '.join(allowed)}"

        if field == "username":
            existing = self.db.fetch_one(
                "SELECT id FROM users WHERE username = %s AND id != %s",
                (value, user_id),
            )
            if existing:
                return False, "Username sudah dipakai user lain"

        query = f"UPDATE users SET {field} = %s WHERE id = %s"
        _, err = self.db.execute(query, (value, user_id))
        if err:
            return False, f"Gagal update profile: {err}"
        return True, "Profile berhasil diupdate"

    def change_password(self, user_id, old_password, new_password):
        row = self.db.fetch_one(
            "SELECT password_hash FROM users WHERE id = %s", (user_id,)
        )
        if not row:
            return False, "User tidak ditemukan"

        if not bcrypt.checkpw(
            old_password.encode("utf-8"), row["password_hash"].encode("utf-8")
        ):
            return False, "Password lama salah"

        new_hash = bcrypt.hashpw(
            new_password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        _, err = self.db.execute(
            "UPDATE users SET password_hash = %s WHERE id = %s",
            (new_hash, user_id),
        )
        if err:
            return False, f"Gagal ubah password: {err}"
        return True, "Password berhasil diubah"

    def delete_account(self, user_id):
        self.db.execute("DELETE FROM reminders WHERE user_id = %s", (user_id,))
        self.db.execute("DELETE FROM memories WHERE user_id = %s", (user_id,))
        self.db.execute("DELETE FROM conversations WHERE user_id = %s", (user_id,))
        _, err = self.db.execute("DELETE FROM users WHERE id = %s", (user_id,))
        if err:
            return False, f"Gagal hapus akun: {err}"
        return True, "Akun berhasil dihapus"
