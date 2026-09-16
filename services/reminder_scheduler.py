import threading
import time
from datetime import datetime

from utils.colors import C, colored


# Prioritas → interval cek ulang (detik) setelah notifikasi pertama
_REMIND_AGAIN_AFTER = {"high": 60, "medium": 300, "low": 900}


class ReminderScheduler:
    def __init__(self, reminder_manager, check_interval=20, prompt_fn=None):
        self.reminder_manager = reminder_manager
        self.check_interval = check_interval
        self.prompt_fn = prompt_fn  
        self._thread = None
        self._stop_event = threading.Event()
        self._user_id = None
        self._notified = {}  

    # ── Lifecycle ───────────────────────────────────────────────────

    def start(self, user_id):
        self.stop()
        self._user_id = user_id
        self._notified = {}
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True, name="reminder-scheduler")
        self._thread.start()

    def stop(self):
        """Hentikan thread scheduler (dipanggil saat logout/exit)."""
        if self._thread and self._thread.is_alive():
            self._stop_event.set()
            self._thread = None
        self._user_id = None
        self._notified = {}

    @property
    def is_running(self):
        return self._thread is not None and self._thread.is_alive()

    # ── Loop utama ──────────────────────────────────────────────────

    def _run(self):
        while not self._stop_event.wait(self.check_interval):
            try:
                self.check_once()
            except Exception:
                # Scheduler tidak boleh mati karena error sewaktu-waktu
                pass

    def check_once(self):
        if not self._user_id:
            return

        now = datetime.now()
        now_str = now.strftime("%Y-%m-%d %H:%M:%S")

        due = self.reminder_manager.get_due(self._user_id, now_str)
        for r in due:
            self._notify(r)
            self.reminder_manager.mark_notified(r["id"], now_str)
            self._notified[r["id"]] = time.monotonic()
            if r.get("is_recurring"):
                self.reminder_manager.reschedule_recurring(r)

        now_mono = time.monotonic()
        for rem_id, last in list(self._notified.items()):
            row = self.reminder_manager.get_by_id(rem_id, self._user_id)
            if not row or row.get("is_done"):
                self._notified.pop(rem_id, None)
                continue
            if row.get("is_recurring"):
                self._notified.pop(rem_id, None)
                continue
            priority = row.get("priority", "medium")
            if now_mono - last < _REMIND_AGAIN_AFTER.get(priority, 300):
                continue
            self._notify(row, repeat=True)
            self._notified[rem_id] = now_mono

    # ── Notifikasi ──────────────────────────────────────────────────

    def _notify(self, reminder, repeat=False):
        task = reminder.get("task", "")
        due = reminder.get("due_date")
        priority = reminder.get("priority", "medium")
        is_high = priority == "high"

        print()
        print(
            f"  {colored('🔔 REMINDER', C.BRIGHT_RED if is_high else C.BRIGHT_YELLOW, bold=True)}"
            f"{colored(' [pengingat ulang]', C.GRAY) if repeat else ''}"
        )
        print(f"  {'─' * 45}")
        print(f"  {colored('Tugas', C.GRAY)}    : {colored(task, C.BOLD)}")
        if due:
            print(f"  {colored('Jatuh tempo', C.GRAY)}: {colored(str(due), C.YELLOW)}")
        print(f"  {colored('Prioritas', C.GRAY)} : {colored(priority, C.BRIGHT_RED if is_high else C.BRIGHT_YELLOW)}")
        print(f"  {'─' * 45}")
        print()
        if self.prompt_fn:
            print(self.prompt_fn(), end="", flush=True)

    def set_user(self, user_id):
        if user_id is None:
            self.stop()
        else:
            self.start(user_id)
