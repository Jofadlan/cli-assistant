class Conversation:
    def __init__(self, id, user_id, conversation_id, role, message, created_at=None, updated_at=None):
        self.id = id
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.role = role
        self.message = message
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "conversation_id": self.conversation_id,
            "role": self.role,
            "message": self.message,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def __repr__(self):
        return f"Conversation(id={self.id}, role='{self.role}', msg='{self.message[:30]}...')"
