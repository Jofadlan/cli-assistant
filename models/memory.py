class Memory:
    def __init__(self, id, user_id, category, fact, created_at=None, updated_at=None):
        self.id = id
        self.user_id = user_id
        self.category = category
        self.fact = fact
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "category": self.category,
            "fact": self.fact,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def __repr__(self):
        return f"Memory(id={self.id}, category='{self.category}', fact='{self.fact[:30]}...')"
