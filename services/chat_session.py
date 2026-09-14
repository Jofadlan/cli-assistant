import re


class ChatSession:
    # Action tag pattern: [ACTION:type:param1|param2|...][/ACTION]
    ACTION_PATTERN = re.compile(
        r"\[ACTION:(\w+):([^\]]*)\]\[/ACTION\]", re.IGNORECASE
    )

    def __init__(self, api_client, conversation_manager, memory_manager=None, reminder_manager=None):
        self.api_client = api_client
        self.conversation_manager = conversation_manager
        self.memory_manager = memory_manager
        self.reminder_manager = reminder_manager
        self._current_session_id = None

    @property
    def session_id(self):
        return self._current_session_id

    def start_new_session(self):
        self._current_session_id = self.conversation_manager.new_session_id()
        return self._current_session_id

    def _build_system_prompt(self, user_id):
        parts = [
            "Kamu adalah AI assistant yang membantu pengguna dalam Bahasa Indonesia. "
            "Kamu bisa mengingat fakta tentang pengguna dan membantu mengelola reminder mereka."
        ]

        # ── How to perform actions ──────────────────────────────────
        parts.append(
            "\n[KARMA KAMU BISA MELAKUKAN OPERASI MEMORY & REMINDER]"
            "\nKetika pengguna meminta kamu untuk menyimpan/mengingat sesuatu, menghapus fakta, "
            "membuat/mengupdate/menghapus reminder — kamu HARUS menyertakan action tag di akhir respons."
            "\n"
            "\nFormat action tag:"
            "\n  [ACTION:tipe:param1|param2|...][/ACTION]"
            "\n"
            "\nTipe yang tersedia:"
            "\n  memory_create  → [ACTION:memory_create:kategori|fakta][/ACTION]"
            "\n    kategori: preferensi, fakta_pribadi, pekerjaan, lainnya"
            "\n    contoh: [ACTION:memory_create:fakta_pribadi|Saya suka makan nasi goreng][/ACTION]"
            "\n"
            "\n  memory_update  → [ACTION:memory_update:id|fakta_baru][/ACTION]"
            "\n    contoh: [ACTION:memory_update:5|Saya sekarang vegetarian][/ACTION]"
            "\n"
            "\n  memory_delete  → [ACTION:memory_delete:id][/ACTION]"
            "\n    contoh: [ACTION:memory_delete:5][/ACTION]"
            "\n"
            "\n  reminder_create → [ACTION:reminder_create:tugas|tanggal|prioritas][/ACTION]"
            "\n    tanggal format: YYYY-MM-DD atau YYYY-MM-DD HH:MM"
            "\n    prioritas: high, medium, low"
            "\n    contoh: [ACTION:reminder_create:Beli obat|2026-09-20|high][/ACTION]"
            "\n"
            "\n  reminder_update → [ACTION:reminder_update:id|field|value][/ACTION]"
            "\n    field: task, due_date, priority, is_done"
            "\n    contoh: [ACTION:reminder_update:3|is_done|true][/ACTION]"
            "\n"
            "\n  reminder_delete → [ACTION:reminder_delete:id][/ACTION]"
            "\n    contoh: [ACTION:reminder_delete:3][/ACTION]"
            "\n"
            "\nPENTING:"
            "\n- Kamu BISA melakukan beberapa action sekaligus dalam satu respons."
            "\n- Tulis action tag di BARIS TERPISAH di akhir respons, BUKAN di tengah kalimat."
            "\n- Tetap beri penjelasan yang ramah dan jelas ke user tentang apa yang kamu lakukan."
            "\n- Jika user hanya bertanya (bukan meminta aksi), JANGAN sertakan action tag."
            "\n- Jika user meminta menghapus atau mengupdate sesuatu yang ada di context, "
            "gunakan ID yang sesuai dari context yang diberikan."
        )

        # Inject memories
        if self.memory_manager:
            memories = self.memory_manager.read(user_id)
            if memories:
                parts.append("\n[KONTEKS MEMORY PENGGUNA]")
                for m in memories:
                    parts.append(f"  - [id:{m['id']}] [{m['category']}] {m['fact']}")

        # Inject reminders
        if self.reminder_manager:
            pending = self.reminder_manager.read(user_id, "pending")
            done = self.reminder_manager.read(user_id, "done")
            parts.append("\n[KONTEKS REMINDER PENGGUNA]")
            if pending:
                parts.append("  Reminder aktif:")
                for r in pending:
                    due = str(r["due_date"]) if r["due_date"] else "tanpa tenggat"
                    parts.append(
                        f"    - [id:{r['id']}] {r['task']} "
                        f"(deadline: {due}, prioritas: {r['priority']})"
                    )
            if done:
                parts.append(f"  ({len(done)} reminder sudah selesai)")
            if not pending and not done:
                parts.append("  Belum ada reminder.")

        return "\n".join(parts)

    # ── Action execution ────────────────────────────────────────────

    def _execute_action(self, action_type, params_str, user_id):
        """Execute a single action tag. Returns (success: bool, message: str)."""
        params = [p.strip() for p in params_str.split("|")]

        try:
            # ── Memory ──────────────────────────────────────────────
            if action_type == "memory_create":
                if len(params) < 2:
                    return False, "Param kurang (kategori|fakta)"
                category, fact = params[0], params[1]
                valid_cats = ["preferensi", "fakta_pribadi", "pekerjaan", "lainnya"]
                if category not in valid_cats:
                    category = "lainnya"
                    fact = params[0] + "|" + params[1] if len(params) > 1 else params[0]
                ok, msg = self.memory_manager.create(user_id, fact, category)
                return ok, msg

            elif action_type == "memory_update":
                if len(params) < 2:
                    return False, "Param kurang (id|fakta_baru)"
                mem_id, new_fact = int(params[0]), params[1]
                ok, msg = self.memory_manager.update(mem_id, new_fact)
                return ok, msg

            elif action_type == "memory_delete":
                if len(params) < 1:
                    return False, "Param kurang (id)"
                mem_id = int(params[0])
                ok, msg = self.memory_manager.delete(mem_id)
                return ok, msg

            # ── Reminder ────────────────────────────────────────────
            elif action_type == "reminder_create":
                if len(params) < 3:
                    return False, "Param kurang (tugas|tanggal|prioritas)"
                task, due_date, priority = params[0], params[1], params[2]
                if priority not in ["high", "medium", "low"]:
                    priority = "medium"
                ok, msg = self.reminder_manager.create(user_id, task, due_date, priority)
                return ok, msg

            elif action_type == "reminder_update":
                if len(params) < 3:
                    return False, "Param kurang (id|field|value)"
                rem_id = int(params[0])
                field, value = params[1], params[2]
                if field == "is_done":
                    value = value.lower() in ("true", "1", "yes")
                elif field == "is_recurring":
                    value = value.lower() in ("true", "1", "yes")
                ok, msg = self.reminder_manager.update(rem_id, field, value)
                return ok, msg

            elif action_type == "reminder_delete":
                if len(params) < 1:
                    return False, "Param kurang (id)"
                rem_id = int(params[0])
                ok, msg = self.reminder_manager.delete(rem_id)
                return ok, msg

            else:
                return False, f"Tipe aksi '{action_type}' tidak dikenal"

        except (ValueError, IndexError) as e:
            return False, f"Error parse parameter: {e}"

    def _parse_and_execute_actions(self, response, user_id):
        """Parse action tags from AI response, execute them, return (clean_text, results)."""
        matches = list(self.ACTION_PATTERN.finditer(response))
        if not matches:
            return response, []

        results = []
        for match in matches:
            action_type = match.group(1)
            params_str = match.group(2)
            ok, msg = self._execute_action(action_type, params_str, user_id)
            results.append((ok, action_type, msg))

        # Strip action tags from response
        clean_text = self.ACTION_PATTERN.sub("", response).strip()
        return clean_text, results

    # ── Main send ───────────────────────────────────────────────────

    def send_message(self, user_id, message):
        if not self._current_session_id:
            self.start_new_session()

        self.conversation_manager.create_message(
            user_id, self._current_session_id, "user", message
        )

        history = self.conversation_manager.get_messages(user_id, self._current_session_id)

        # Build messages with system prompt + history
        system_prompt = self._build_system_prompt(user_id)
        api_messages = [{"role": "system", "content": system_prompt}]
        for msg in history:
            api_messages.append({"role": msg["role"], "content": msg["message"]})

        response, error = self.api_client.chat(api_messages)
        if error:
            return None, error, []

        # Parse and execute any action tags
        clean_response, action_results = self._parse_and_execute_actions(response, user_id)

        # Re-fetch context for next turn (memories/reminders may have changed)
        # The system prompt is rebuilt on each call so this is automatic.

        self.conversation_manager.create_message(
            user_id, self._current_session_id, "assistant", clean_response
        )
        return clean_response, None, action_results

    def get_history(self, user_id):
        if not self._current_session_id:
            return []
        return self.conversation_manager.get_messages(user_id, self._current_session_id)
