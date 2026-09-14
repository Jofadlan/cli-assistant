class MemoryManager:
    def __init__(self, db):
        self.db = db

    def create(self, user_id, fact, category="lainnya"):
        query = "INSERT INTO memories (user_id, fact, category) VALUES (%s, %s, %s)"
        _, err = self.db.execute(query, (user_id, fact, category))
        if err:
            return False, f"Gagal simpan memory: {err}"
        return True, "Memory berhasil disimpan"

    def read(self, user_id, category=None):
        if category:
            query = "SELECT * FROM memories WHERE user_id = %s AND category = %s ORDER BY created_at DESC"
            return self.db.fetch(query, (user_id, category))
        query = "SELECT * FROM memories WHERE user_id = %s ORDER BY created_at DESC"
        return self.db.fetch(query, (user_id,))

    def update(self, memory_id, new_fact):
        query = "UPDATE memories SET fact = %s WHERE id = %s"
        _, err = self.db.execute(query, (new_fact, memory_id))
        if err:
            return False, f"Gagal update memory: {err}"
        return True, "Memory berhasil diupdate"

    def delete(self, memory_id):
        query = "DELETE FROM memories WHERE id = %s"
        _, err = self.db.execute(query, (memory_id,))
        if err:
            return False, f"Gagal hapus memory: {err}"
        return True, "Memory berhasil dihapus"
