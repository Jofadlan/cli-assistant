class Reminder:
    def __init__(self, id, user_id, task, priority, due_date, is_done, is_recurring, recurrence_pattern, created_at=None, updated_at=None):
        self.id = id
        self.user_id = user_id
        self.task = task
        self.priority = priority
        self.due_date = due_date
        self.is_done = is_done
        self.is_recurring = is_recurring
        self.recurrence_pattern = recurrence_pattern
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "task": self.task,
            "priority": self.priority,
            "due_date": self.due_date,
            "is_done": self.is_done,
            "is_recurring": self.is_recurring,
            "recurrence_pattern": self.recurrence_pattern,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def __repr__(self):
        status = "done" if self.is_done else "pending"
        return f"Reminder(id={self.id}, task='{self.task[:30]}', priority='{self.priority}', status='{status}')"
