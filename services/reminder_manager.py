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

    def get_by_id(self, reminder_id, user_id):
        query = "SELECT * FROM reminders WHERE id = %s AND user_id = %s"
        return self.db.fetch_one(query, (reminder_id, user_id))

    def get_due(self, user_id, now):
        query = """SELECT * FROM reminders
                   WHERE user_id = %s
                     AND is_done = FALSE
                     AND due_date IS NOT NULL
                     AND due_date <= %s
                     AND last_notified_at IS NULL
                   ORDER BY due_date ASC"""
        return self.db.fetch(query, (user_id, now))

    def mark_notified(self, reminder_id, now):
        query = "UPDATE reminders SET last_notified_at = %s WHERE id = %s"
        _, err = self.db.execute(query, (now, reminder_id))
        if err:
            return False, f"Gagal menandai notifikasi: {err}"
        return True, "OK"

    def _advance_recurring(self, due_date, pattern):
        from datetime import datetime, timedelta

        if isinstance(due_date, str):
            try:
                due_date = datetime.strptime(str(due_date)[:19], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return None
        pattern = (pattern or "daily").lower()
        if pattern == "daily":
            return due_date + timedelta(days=1)
        if pattern == "weekly":
            return due_date + timedelta(weeks=1)
        if pattern == "monthly":
            year, month = due_date.year, due_date.month + 1
            if month > 12:
                year, month = year + 1, 1
            day = min(due_date.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
            return due_date.replace(year=year, month=month, day=day)
        return None

    def reschedule_recurring(self, reminder):
        if not reminder.get("is_recurring"):
            return False, "Bukan reminder berulang"
        next_due = self._advance_recurring(reminder.get("due_date"), reminder.get("recurrence_pattern"))
        if not next_due:
            return False, "Pattern recurrence tidak dikenal"
        query = "UPDATE reminders SET due_date = %s, last_notified_at = NULL, is_done = FALSE WHERE id = %s"
        _, err = self.db.execute(query, (next_due.strftime("%Y-%m-%d %H:%M:%S"), reminder["id"]))
        if err:
            return False, f"Gagal menjadwalkan ulang: {err}"
        return True, f"Reminder berulang dijadwalkan ulang ke {next_due.strftime('%Y-%m-%d %H:%M')}"

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
