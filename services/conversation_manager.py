import uuid
from datetime import datetime


class ConversationManager:
    def __init__(self, db):
        self.db = db

    def create_message(self, user_id, conversation_id, role, message):
        query = """INSERT INTO conversations (user_id, conversation_id, role, message)
                   VALUES (%s, %s, %s, %s)"""
        _, err = self.db.execute(query, (user_id, conversation_id, role, message))
        return err is None

    def list_sessions(self, user_id):
        query = """SELECT conversation_id, MIN(created_at) as started_at, COUNT(*) as message_count
                   FROM conversations WHERE user_id = %s
                   GROUP BY conversation_id ORDER BY started_at DESC"""
        return self.db.fetch(query, (user_id,))

    def get_messages(self, user_id, conversation_id):
        query = """SELECT * FROM conversations
                   WHERE user_id = %s AND conversation_id = %s
                   ORDER BY created_at ASC"""
        return self.db.fetch(query, (user_id, conversation_id))

    def update_message(self, message_id, new_message):
        query = "UPDATE conversations SET message = %s WHERE id = %s"
        _, err = self.db.execute(query, (new_message, message_id))
        if err:
            return False, f"Gagal update pesan: {err}"
        return True, "Pesan berhasil diupdate"

    def delete_message(self, message_id):
        query = "DELETE FROM conversations WHERE id = %s"
        _, err = self.db.execute(query, (message_id,))
        if err:
            return False, f"Gagal hapus pesan: {err}"
        return True, "Pesan berhasil dihapus"

    def clear_session(self, user_id, conversation_id):
        query = "DELETE FROM conversations WHERE user_id = %s AND conversation_id = %s"
        _, err = self.db.execute(query, (user_id, conversation_id))
        if err:
            return False, f"Gagal hapus sesi: {err}"
        return True, "Sesi obrolan berhasil dihapus"

    def clear_all(self, user_id):
        query = "DELETE FROM conversations WHERE user_id = %s"
        _, err = self.db.execute(query, (user_id,))
        if err:
            return False, f"Gagal hapus riwayat: {err}"
        return True, "Semua riwayat chat berhasil dihapus"

    def new_session_id(self):
        return str(uuid.uuid4())
