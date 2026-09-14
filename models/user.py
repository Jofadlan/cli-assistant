class User:
    def __init__(self, id, username, created_at=None):
        self.id = id
        self.username = username
        self.created_at = created_at

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "created_at": self.created_at,
        }

    def __repr__(self):
        return f"User(id={self.id}, username='{self.username}')"
