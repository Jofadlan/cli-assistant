class ReminderManager:
    def __init__(self, db):
        self.db = db

    def create(self, user_id, task, due_date, priority="medium", is_recurring=False, recurrence_pattern=None):
        query = """INSERT INTO reminders (user_id, task, due_date, priority, is_recurring, recurrence_pattern)
                   VALUES (%s, %s, %s, %s, %s, %s)"""
        _, err = self.db.execute(query, (user_id, task, due_date, priority, is_recurring, recurrence_pattern))
        if err:
            return False, f"Gagal membuat reminder: {err}"
        return True, "Reminder berhasil dibuat"

    def read(self, user_id, status=None):
        if status == "pending":
            query = "SELECT * FROM reminders WHERE user_id = %s AND is_done = FALSE ORDER BY due_date ASC"
            return self.db.fetch(query, (user_id,))
        elif status == "done":
            query = "SELECT * FROM reminders WHERE user_id = %s AND is_done = TRUE ORDER BY due_date DESC"
            return self.db.fetch(query, (user_id,))
        query = "SELECT * FROM reminders WHERE user_id = %s ORDER BY is_done ASC, due_date ASC"
        return self.db.fetch(query, (user_id,))

    def update(self, reminder_id, field, value):
        allowed = ["task", "due_date", "priority", "is_done", "is_recurring", "recurrence_pattern"]
        if field not in allowed:
            return False, f"Field '{field}' tidak valid. Yang boleh: {', '.join(allowed)}"
        query = f"UPDATE reminders SET {field} = %s WHERE id = %s"
        _, err = self.db.execute(query, (value, reminder_id))
        if err:
            return False, f"Gagal update reminder: {err}"
        return True, "Reminder berhasil diupdate"

    def delete(self, reminder_id):
        query = "DELETE FROM reminders WHERE id = %s"
        _, err = self.db.execute(query, (reminder_id,))
        if err:
            return False, f"Gagal hapus reminder: {err}"
        return True, "Reminder berhasil dihapus"
