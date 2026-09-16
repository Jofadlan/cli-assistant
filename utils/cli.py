import getpass
import os
import re
from datetime import datetime

from utils.colors import C, colored, success, error, warning, info, dim


class CLIHandler:
    HELP_TEXT = f"""
{colored("╔══════════════════════════════════════════════════════════════╗", C.CYAN)}
{colored("║", C.CYAN)}{colored("                      📖 DAFTAR PERINTAH                     ", C.BOLD)}{colored("║", C.CYAN)}
{colored("╚══════════════════════════════════════════════════════════════╝", C.CYAN)}

{colored("  🔐  Autentikasi", C.BOLD + C.BRIGHT_YELLOW)}
  {colored("/login", C.BRIGHT_GREEN, bold=True)}                  Login (username & password)
  {colored("/register", C.BRIGHT_GREEN, bold=True)}               Register akun baru
  {colored("/logout", C.BRIGHT_GREEN, bold=True)}                 Logout dari sesi
  {colored("/exit", C.BRIGHT_GREEN, bold=True)}                   Keluar dari aplikasi

{colored("  💬  Obrolan", C.BOLD + C.BRIGHT_YELLOW)}
  {colored("/chat", C.BRIGHT_GREEN, bold=True)} <pesan>           Kirim pesan ke AI

{colored("  👤  Profil", C.BOLD + C.BRIGHT_YELLOW)}
  {colored("/profile", C.BRIGHT_GREEN, bold=True)}                Lihat profil
  {colored("/update-profile", C.BRIGHT_GREEN, bold=True)} <f> <v> Update field profil
  {colored("/change-password", C.BRIGHT_GREEN, bold=True)}       Ubah password
  {colored("/delete-account", C.BRIGHT_GREEN, bold=True)}        Hapus akun

{colored("  📜  Riwayat", C.BOLD + C.BRIGHT_YELLOW)}
  {colored("/sessions", C.BRIGHT_GREEN, bold=True)}               List semua sesi obrolan
  {colored("/history", C.BRIGHT_GREEN, bold=True)} <session_id>   Lihat pesan dalam sesi
  {colored("/edit-message", C.BRIGHT_GREEN, bold=True)} <id> <m>  Edit pesan
  {colored("/delete-message", C.BRIGHT_GREEN, bold=True)} <id>    Hapus pesan
  {colored("/clear-session", C.BRIGHT_GREEN, bold=True)} <id>     Hapus satu sesi
  {colored("/clear-history", C.BRIGHT_GREEN, bold=True)}          Hapus semua riwayat

{colored("  🧠  Memory", C.BOLD + C.BRIGHT_YELLOW)}
  {colored("/remember", C.BRIGHT_GREEN, bold=True)}               Simpan memory (interaktif)
  {colored("/remember", C.BRIGHT_GREEN, bold=True)} <fakta>       Simpan fakta langsung
  {colored("/remember", C.BRIGHT_GREEN, bold=True)} <kat> <fakta> Simpan fakta + kategori
  {colored("/list-memory", C.BRIGHT_GREEN, bold=True)}            Lihat semua memory
  {colored("/list-memory", C.BRIGHT_GREEN, bold=True)} <kategori> Lihat per kategori
  {colored("/update-memory", C.BRIGHT_GREEN, bold=True)} <id> <f> Update fakta
  {colored("/forget", C.BRIGHT_GREEN, bold=True)} <id>            Hapus fakta

{colored("  ⏰  Reminder", C.BOLD + C.BRIGHT_YELLOW)}
  {colored("/remind", C.BRIGHT_GREEN, bold=True)}                   Buat reminder (interaktif)
  {colored("/remind", C.BRIGHT_GREEN, bold=True)} <task> <date>      Buat reminder langsung
  {colored("/reminders", C.BRIGHT_GREEN, bold=True)}                   Lihat semua reminder
  {colored("/reminders --pending", C.BRIGHT_GREEN, bold=True)}         Belum selesai
  {colored("/reminders --done", C.BRIGHT_GREEN, bold=True)}            Sudah selesai
  {colored("/update-reminder", C.BRIGHT_GREEN, bold=True)} <id> done   Tandai selesai
  {colored("/delete-reminder", C.BRIGHT_GREEN, bold=True)} <id>        Hapus reminder

{colored("  🖥️  Layar", C.BOLD + C.BRIGHT_YELLOW)}
  {colored("/clear", C.BRIGHT_GREEN, bold=True)}                  Bersihkan layar terminal

{colored("  ❓  Bantuan", C.BOLD + C.BRIGHT_YELLOW)}
  {colored("/help", C.BRIGHT_GREEN, bold=True)}                   Tampilkan semua perintah
  {colored("/help", C.BRIGHT_GREEN, bold=True)} <command>         Detail cara pakai + contoh
"""

    MEMORY_CATEGORIES = ["preferensi", "fakta_pribadi", "pekerjaan", "lainnya"]

    # Detail per-perintah untuk /help <command>
    HELP_DETAILS = {
        "/login": {
            "desc": "Masuk ke akun kamu",
            "usage": ["/login"],
            "examples": ["/login"],
            "notes": [
                "Username & password diminta setelah perintah dijalankan",
                "Password disembunyikan saat diketik",
                "Setelah login, sesi chat baru otomatis dimulai",
            ],
        },
        "/register": {
            "desc": "Daftar akun baru",
            "usage": ["/register"],
            "examples": ["/register"],
            "notes": [
                "Password diminta 2x untuk konfirmasi",
                "Setelah berhasil, lanjutkan dengan /login",
            ],
        },
        "/logout": {
            "desc": "Keluar dari sesi login",
            "usage": ["/logout"],
            "notes": [
                "Memory, reminder, dan riwayat tetap tersimpan (tidak ikut terhapus)",
            ],
        },
        "/exit": {
            "desc": "Keluar dari aplikasi",
            "usage": ["/exit"],
            "notes": [
                "Sama dengan menekan Ctrl+D",
                "Semua data sudah tersimpan otomatis di database",
            ],
        },
        "/clear": {
            "desc": "Bersihkan layar terminal",
            "usage": ["/clear"],
            "examples": ["/clear"],
            "notes": [
                "Hanya membersihkan tampilan, tidak ada data yang terhapus",
                "Beda dengan /clear-history yang menghapus riwayat chat",
            ],
        },
        "/chat": {
            "desc": "Kirim pesan ke AI",
            "usage": ["/chat <pesan>"],
            "examples": [
                "/chat halo, perkenalkan diri kamu",
                "/chat catat bahwa saya alergi seafood",
                "/chat ingatkan saya rapat besok jam 9",
            ],
            "notes": [
                "AI bisa otomatis menyimpan/mengubah memory atau membuat reminder dari percakapan",
                "Hasil aksi AI (memory/reminder) ditampilkan di bawah jawaban",
                "Percakapan tersimpan per sesi, lihat lewat /sessions dan /history",
            ],
        },
        "/help": {
            "desc": "Tampilkan bantuan perintah",
            "usage": ["/help", "/help <command>"],
            "examples": ["/help", "/help remember", "/help remind"],
            "notes": [
                "Tanpa argumen: daftar semua perintah",
                "Dengan nama perintah: cara pakai lengkap + contoh",
                "Bisa ditulis dengan atau tanpa '/': /help remember = /help /remember",
            ],
        },
        "/profile": {
            "desc": "Lihat profil akun",
            "usage": ["/profile"],
            "notes": ["Menampilkan ID, username, dan tanggal bergabung"],
        },
        "/update-profile": {
            "desc": "Ubah data profil",
            "usage": ["/update-profile <field> <value>"],
            "examples": ["/update-profile username budi_aja"],
            "notes": [
                "Field yang tersedia: username",
                "Username harus unik (belum dipakai user lain)",
            ],
        },
        "/change-password": {
            "desc": "Ubah password akun",
            "usage": ["/change-password"],
            "notes": [
                "Password lama diminta untuk verifikasi",
                "Password baru diminta 2x untuk konfirmasi",
            ],
        },
        "/delete-account": {
            "desc": "Hapus akun permanen",
            "usage": ["/delete-account"],
            "notes": [
                "Menghapus akun + semua memory, reminder, dan riwayat obrolan",
                "Tidak bisa dibatalkan — diminta ketik YES untuk konfirmasi",
            ],
        },
        "/sessions": {
            "desc": "Lihat semua sesi obrolan",
            "usage": ["/sessions"],
            "notes": ["Gunakan Session ID untuk /history dan /clear-session"],
        },
        "/history": {
            "desc": "Lihat isi percakapan satu sesi",
            "usage": ["/history <session_id>"],
            "examples": ["/history 550e8400-e29b-41d4-a716-446655440000"],
            "notes": [
                "Ambil session_id dari /sessions",
                "ID harus ditulis lengkap (UUID 36 karakter)",
            ],
        },
        "/edit-message": {
            "desc": "Edit isi pesan",
            "usage": ["/edit-message <id> <pesan_baru>"],
            "examples": ["/edit-message 12 halo, yang benar Bandung"],
            "notes": ["<id> adalah ID pesan di database", "Perubahan bersifat permanen"],
        },
        "/delete-message": {
            "desc": "Hapus satu pesan",
            "usage": ["/delete-message <id>"],
            "examples": ["/delete-message 12"],
            "notes": ["Penghapusan bersifat permanen"],
        },
        "/clear-session": {
            "desc": "Hapus satu sesi obrolan",
            "usage": ["/clear-session <session_id>"],
            "examples": ["/clear-session 550e8400-e29b-41d4-a716-446655440000"],
            "notes": [
                "Semua pesan dalam sesi itu terhapus",
                "Diminta ketik YES untuk konfirmasi",
            ],
        },
        "/clear-history": {
            "desc": "Hapus semua riwayat obrolan",
            "usage": ["/clear-history"],
            "notes": [
                "Menghapus seluruh riwayat chat di semua sesi",
                "Diminta ketik YES untuk konfirmasi — tidak bisa dibatalkan",
            ],
        },
        "/remember": {
            "desc": "Simpan fakta ke memory AI",
            "usage": [
                "/remember",
                "/remember <fakta>",
                "/remember <kategori> <fakta>",
            ],
            "examples": [
                "/remember",
                "/remember saya suka kopi pahit",
                "/remember preferensi saya suka kopi pahit",
                "/remember pekerjaan saya backend developer di startup X",
            ],
            "notes": [
                "Tanpa argumen: mode interaktif (fakta & kategori ditanya satu-satu)",
                "Kategori: preferensi, fakta_pribadi, pekerjaan, lainnya",
                "Tanpa kategori otomatis jadi 'lainnya'",
                "AI juga bisa menyimpan memory otomatis dari /chat",
            ],
        },
        "/list-memory": {
            "desc": "Lihat daftar memory",
            "usage": ["/list-memory", "/list-memory <kategori>"],
            "examples": ["/list-memory", "/list-memory preferensi"],
            "notes": [
                "Tanpa kategori: tampilkan semua memory",
                "Gunakan ID yang tampil untuk /update-memory dan /forget",
            ],
        },
        "/update-memory": {
            "desc": "Ubah isi memory",
            "usage": ["/update-memory <id> <fakta_baru>"],
            "examples": ["/update-memory 3 saya sekarang suka teh"],
            "notes": [
                "Ambil <id> dari /list-memory",
                "Hanya isinya yang berubah, kategori tetap",
            ],
        },
        "/forget": {
            "desc": "Hapus satu memory",
            "usage": ["/forget <id>"],
            "examples": ["/forget 3"],
            "notes": [
                "Ambil <id> dari /list-memory",
                "Penghapusan bersifat permanen",
            ],
        },
        "/remind": {
            "desc": "Buat reminder",
            "usage": ["/remind", "/remind <task> <tanggal>"],
            "examples": [
                "/remind",
                "/remind rapat tim 2026-09-20",
                "/remind bayar listrik 20/09/2026",
                "/remind standup harian 2026-09-21 09:00",
            ],
            "notes": [
                "Tanpa argumen: mode interaktif (tugas, tanggal, prioritas, berulang ditanya satu-satu)",
                "Format tanggal: YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY — dengan atau tanpa jam",
                "Tanpa jam → dianggap sampai akhir hari itu (23:59)",
                "Prioritas default: medium (pilihan: high, medium, low)",
                "Bisa berulang: daily, weekly, atau monthly — otomatis dijadwalkan ulang setelah dinotifikasi",
                "Saat jatuh tempo, notifikasi muncul otomatis di terminal (tanpa perlu /reminders)",
            ],
        },
        "/reminders": {
            "desc": "Lihat daftar reminder",
            "usage": ["/reminders", "/reminders --pending", "/reminders --done"],
            "examples": ["/reminders", "/reminders --pending"],
            "notes": [
                "--pending: hanya yang belum selesai",
                "--done: hanya yang sudah selesai",
                "Gunakan ID untuk /update-reminder dan /delete-reminder",
                "Reminder yang lewat tenggat juga muncul otomatis sebagai notifikasi di terminal",
            ],
        },
        "/update-reminder": {
            "desc": "Ubah atau tandai reminder",
            "usage": [
                "/update-reminder <id> done",
                "/update-reminder <id> undo",
                "/update-reminder <id> <field> <value>",
            ],
            "examples": [
                "/update-reminder 5 done",
                "/update-reminder 5 undo",
                "/update-reminder 5 task belanja mingguan",
                "/update-reminder 5 priority high",
                "/update-reminder 5 due_date 2026-09-25 10:00",
            ],
            "notes": [
                "Shortcut: done = tandai selesai, undo = batalkan selesai",
                "Field valid: task, due_date, priority, is_done, is_recurring, recurrence_pattern",
                "Nilai boolean: true/1/yes atau false/0/no",
            ],
        },
        "/delete-reminder": {
            "desc": "Hapus reminder",
            "usage": ["/delete-reminder <id>"],
            "examples": ["/delete-reminder 5"],
            "notes": [
                "Diminta ketik YES untuk konfirmasi",
                "Penghapusan bersifat permanen",
            ],
        },
    }

    def __init__(self, auth, user_manager, memory_manager, reminder_manager, conversation_manager, chat_session):
        self.auth = auth
        self.user_manager = user_manager
        self.memory_manager = memory_manager
        self.reminder_manager = reminder_manager
        self.conversation_manager = conversation_manager
        self.chat_session = chat_session
        self.scheduler = None  # di-set dari main.py
        self._commands = {
            "/login": self._login,
            "/register": self._register,
            "/logout": self._logout,
            "/exit": self._exit,
            "/chat": self._chat,
            "/help": self._help,
            "/clear": self._clear,
            "/profile": self._profile,
            "/update-profile": self._update_profile,
            "/change-password": self._change_password,
            "/delete-account": self._delete_account,
            "/sessions": self._sessions,
            "/history": self._history,
            "/edit-message": self._edit_message,
            "/delete-message": self._delete_message,
            "/clear-session": self._clear_session,
            "/clear-history": self._clear_history,
            "/remember": self._remember,
            "/list-memory": self._list_memory,
            "/update-memory": self._update_memory,
            "/forget": self._forget,
            "/remind": self._remind,
            "/reminders": self._reminders,
            "/update-reminder": self._update_reminder,
            "/delete-reminder": self._delete_reminder,
        }

    def _prompt(self):
        if self.auth.is_logged_in:
            username = self.auth.current_user.username
            return f"{colored(username, C.GREEN)} {colored('❯', C.CYAN)} "
        return f"{colored('❯', C.CYAN)} "

    def handle(self, user_input):
        parts = user_input.strip().split(maxsplit=1)
        if not parts:
            return True

        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        if command in self._commands:
            return self._commands[command](args)
        else:
            print(error(f"Command tidak dikenal: '{command}'"))
            print(dim("   Ketik /help untuk daftar perintah, atau /help <command> untuk detail."))
            return True

    def _confirm(self, prompt="Yakin? Ketik "):
        answer = input(f"{prompt}{colored('YES', C.RED, bold=True)} untuk lanjut: ")
        return answer.strip() == "YES"

    # ─── Auth ───────────────────────────────────────────────────────

    def _login(self, args):
        username = input(f"  {colored('Username', C.CYAN)}: ")
        password = getpass.getpass(f"  {colored('Password', C.CYAN)}: ")
        success_flag, msg = self.auth.login(username, password)
        if success_flag:
            print(success(f"Selamat datang, {colored(username, C.BOLD)}!"))
            self.chat_session.start_new_session()
            if self.scheduler:
                self.scheduler.start(self.auth.current_user.id)
                pending = self.reminder_manager.read(self.auth.current_user.id, "pending")
                overdue = [r for r in pending if r.get("due_date") and str(r["due_date"]) < datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
                if overdue:
                    print(warning(f"Kamu punya {len(overdue)} reminder yang sudah lewat tenggat — cek /reminders"))
        else:
            print(error(msg))
        return True

    def _register(self, args):
        username = input(f"  {colored('Username baru', C.CYAN)}: ")
        password = getpass.getpass(f"  {colored('Password baru', C.CYAN)}: ")
        confirm = getpass.getpass(f"  {colored('Konfirmasi password', C.CYAN)}: ")
        if password != confirm:
            print(error("Password tidak cocok"))
            return True
        success_flag, msg = self.auth.register(username, password)
        if success_flag:
            print(success("Registrasi berhasil! Silakan login."))
        else:
            print(error(msg))
        return True

    def _logout(self, args):
        if not self.auth.is_logged_in:
            print(warning("Belum login"))
            return True
        success_flag, msg = self.auth.logout()
        if self.scheduler:
            self.scheduler.stop()
        print(success("Berhasil logout. Sampai jumpa!"))
        return True

    def _exit(self, args):
        return False

    def _clear(self, args):
        os.system("cls" if os.name == "nt" else "clear")
        return True

    # ─── Chat ───────────────────────────────────────────────────────

    def _chat(self, args):
        if not self.auth.is_logged_in:
            print(error("Login dulu pakai /login"))
            return True
        if not args:
            print(error("Pesan tidak boleh kosong. Contoh: /chat halo"))
            return True

        spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        print(f"  {colored(spinner_chars[0], C.CYAN)} Menunggu respon AI...", end="\r", flush=True)

        import time
        spinner_running = [True]
        def spin():
            i = 0
            while spinner_running[0]:
                print(f"  {colored(spinner_chars[i % len(spinner_chars)], C.CYAN)} Menunggu respon AI...", end="\r", flush=True)
                time.sleep(0.1)
                i += 1

        import threading
        t = threading.Thread(target=spin, daemon=True)
        t.start()

        response, error_msg, action_results = self.chat_session.send_message(
            self.auth.current_user.id, args
        )
        spinner_running[0] = False
        time.sleep(0.15)
        print("  " + " " * 40, end="\r", flush=True)

        if error_msg:
            print(error(f"Error: {error_msg}"))
        else:
            # Show AI response
            if response:
                print()
                print(f"  {colored('🤖 AI', C.BRIGHT_BLUE, bold=True)}")
                for line in response.split("\n"):
                    print(f"  {line}")
                print()

            # Show action results
            if action_results:
                action_labels = {
                    "memory_create": "Memory ditambahkan",
                    "memory_update": "Memory diupdate",
                    "memory_delete": "Memory dihapus",
                    "reminder_create": "Reminder dibuat",
                    "reminder_update": "Reminder diupdate",
                    "reminder_delete": "Reminder dihapus",
                }
                for ok, action_type, msg in action_results:
                    label = action_labels.get(action_type, action_type)
                    if ok:
                        print(success(f"{label}: {msg}"))
                    else:
                        print(error(f"{label}: {msg}"))
                print()
        return True

    # ─── Help ───────────────────────────────────────────────────────

    def _help(self, args):
        if args:
            cmd = args.strip().lower()
            if not cmd.startswith("/"):
                cmd = "/" + cmd
            if cmd in self.HELP_DETAILS:
                self._print_command_help(cmd)
            else:
                print(error(f"Perintah '{cmd}' tidak dikenal"))
                print(dim("   Ketik /help untuk melihat daftar semua perintah."))
        else:
            print(self.HELP_TEXT)
        return True

    def _print_command_help(self, cmd):
        d = self.HELP_DETAILS[cmd]
        print()
        print(f"  {colored(cmd, C.BRIGHT_GREEN, bold=True)} {colored('— ' + d['desc'], C.BOLD)}")
        print(f"  {'─' * 60}")
        print()
        print(f"  {colored('Penggunaan:', C.CYAN, bold=True)}")
        for u in d["usage"]:
            print(f"    {colored(u, C.WHITE)}")
        if d.get("examples"):
            print()
            print(f"  {colored('Contoh:', C.CYAN, bold=True)}")
            for e in d["examples"]:
                print(f"    {colored(e, C.BRIGHT_YELLOW)}")
        if d.get("notes"):
            print()
            print(f"  {colored('Catatan:', C.CYAN, bold=True)}")
            for n in d["notes"]:
                print(f"    {colored('•', C.GRAY)} {colored(n, C.GRAY)}")
        print()

    # ─── Profile ────────────────────────────────────────────────────

    def _profile(self, args):
        if not self.auth.is_logged_in:
            print(error("Login dulu pakai /login"))
            return True
        profile = self.user_manager.get_profile(self.auth.current_user.id)
        if profile:
            print()
            print(f"  {colored('👤 Profil', C.BRIGHT_BLUE, bold=True)}")
            print(f"  {'─' * 30}")
            print(f"  {colored('ID', C.GRAY)}       : {profile['id']}")
            print(f"  {colored('Username', C.GRAY)} : {colored(profile['username'], C.BOLD)}")
            print(f"  {colored('Joined', C.GRAY)}   : {profile['created_at']}")
            print()
        return True

    def _update_profile(self, args):
        if not self.auth.is_logged_in:
            print(error("Login dulu pakai /login"))
            return True
        parts = args.split(maxsplit=1)
        if len(parts) < 2:
            print(error("Format: /update-profile <field> <value>"))
            print(dim("   Contoh: /update-profile username budi_aja"))
            return True
        field, value = parts
        success_flag, msg = self.user_manager.update_profile(self.auth.current_user.id, field, value)
        if success_flag:
            print(success(msg))
            if field == "username":
                self.auth.current_user.username = value
        else:
            print(error(msg))
        return True

    def _change_password(self, args):
        if not self.auth.is_logged_in:
            print(error("Login dulu pakai /login"))
            return True
        old_pw = getpass.getpass(f"  {colored('Password lama', C.CYAN)}: ")
        new_pw = getpass.getpass(f"  {colored('Password baru', C.CYAN)}: ")
        confirm = getpass.getpass(f"  {colored('Konfirmasi password baru', C.CYAN)}: ")
        if new_pw != confirm:
            print(error("Password baru tidak cocok"))
            return True
        success_flag, msg = self.user_manager.change_password(self.auth.current_user.id, old_pw, new_pw)
        if success_flag:
            print(success(msg))
        else:
            print(error(msg))
        return True

    def _delete_account(self, args):
        if not self.auth.is_logged_in:
            print(error("Login dulu pakai /login"))
            return True
        print(warning("Akun yang dihapus tidak bisa dikembalikan!"))
        if self._confirm("Ketik "):
            success_flag, msg = self.user_manager.delete_account(self.auth.current_user.id)
            print(success(msg))
            self.auth.logout()
        else:
            print(dim("  Dibatalkan"))
        return True

    # ─── History ────────────────────────────────────────────────────

    def _sessions(self, args):
        if not self.auth.is_logged_in:
            print(error("Login dulu pakai /login"))
            return True
        sessions = self.conversation_manager.list_sessions(self.auth.current_user.id)
        if not sessions:
            print(warning("Belum ada sesi obrolan"))
            return True

        print()
        print(f"  {colored('📜 Sesi Obrolan', C.BRIGHT_BLUE, bold=True)}")
        print(f"  {'─' * 75}")
        print(f"  {colored('Session ID', C.GRAY):<42} {colored('Dimulai', C.GRAY):<20} {colored('Pesan', C.GRAY):<10}")
        print(f"  {'─' * 75}")
        for s in sessions:
            sid = str(s['conversation_id'])
            if len(sid) > 38:
                sid = sid[:35] + "..."
            print(f"  {sid:<42} {str(s['started_at']):<20} {s['message_count']:<10}")
        print()
        return True

    def _history(self, args):
        if not self.auth.is_logged_in:
            print(error("Login dulu pakai /login"))
            return True
        if not args:
            print(error("Format: /history <session_id>"))
            print(dim("   Ambil session_id dari /sessions"))
            return True
        messages = self.conversation_manager.get_messages(self.auth.current_user.id, args.strip())
        if not messages:
            print(warning("Sesi tidak ditemukan atau kosong"))
            return True
        print()
        for msg in messages:
            if msg["role"] == "user":
                prefix = colored("  You", C.GREEN, bold=True)
            else:
                prefix = colored("  AI", C.BRIGHT_BLUE, bold=True)
            print(f"{prefix}: {msg['message']}")
        print()
        return True

    def _edit_message(self, args):
        if not self.auth.is_logged_in:
            print(error("Login dulu pakai /login"))
            return True
        parts = args.split(maxsplit=1)
        if len(parts) < 2:
            print(error("Format: /edit-message <id> <pesan_baru>"))
            return True
        msg_id, new_msg = int(parts[0]), parts[1]
        success_flag, msg = self.conversation_manager.update_message(msg_id, new_msg)
        if success_flag:
            print(success(msg))
        else:
            print(error(msg))
        return True

    def _delete_message(self, args):
        if not self.auth.is_logged_in:
            print(error("Login dulu pakai /login"))
            return True
        if not args:
            print(error("Format: /delete-message <id>"))
            return True
        success_flag, msg = self.conversation_manager.delete_message(int(args.strip()))
        if success_flag:
            print(success(msg))
        else:
            print(error(msg))
        return True

    def _clear_session(self, args):
        if not self.auth.is_logged_in:
            print(error("Login dulu pakai /login"))
            return True
        if not args:
            print(error("Format: /clear-session <session_id>"))
            return True
        if self._confirm():
            success_flag, msg = self.conversation_manager.clear_session(self.auth.current_user.id, args.strip())
            if success_flag:
                print(success(msg))
            else:
                print(error(msg))
        else:
            print(dim("  Dibatalkan"))
        return True

    def _clear_history(self, args):
        if not self.auth.is_logged_in:
            print(error("Login dulu pakai /login"))
            return True
        print(warning("Semua riwayat obrolan akan dihapus!"))
        if self._confirm("Ketik "):
            success_flag, msg = self.conversation_manager.clear_all(self.auth.current_user.id)
            if success_flag:
                print(success(msg))
            else:
                print(error(msg))
        else:
            print(dim("  Dibatalkan"))
        return True

    # ─── Memory ─────────────────────────────────────────────────────

    def _remember(self, args):
        if not self.auth.is_logged_in:
            print(error("Login dulu pakai /login"))
            return True

        interactive = not args
        fact = ""
        category = None

        if args:
            # One-liner: /remember <fakta> atau /remember <kategori> <fakta>
            fact = args
            first_word = args.split()[0].lower()
            if first_word in self.MEMORY_CATEGORIES:
                rest = args.split(maxsplit=1)[1] if len(args.split()) > 1 else ""
                if not rest:
                    print(error("Format: /remember <kategori> <fakta>"))
                    print(dim("   Contoh: /remember preferensi saya suka kopi"))
                    return True
                fact = rest
                category = first_word
        else:
            # Mode interaktif (seperti /remind)
            print()
            print(f"  {colored('🧠 Simpan Memory Baru', C.BRIGHT_BLUE, bold=True)}")
            print(f"  {'─' * 40}")
            print()

            fact = input(f"  {colored('Fakta', C.CYAN)}: ").strip()
            if not fact:
                print(error("Fakta tidak boleh kosong"))
                return True

            print(f"  {dim('Kategori: ' + ', '.join(self.MEMORY_CATEGORIES))}")
            cat_input = input(
                f"  {colored('Kategori', C.CYAN)} {dim('(enter = deteksi otomatis)')}: "
            ).strip().lower()
            if cat_input and cat_input not in self.MEMORY_CATEGORIES:
                print(warning(f"Kategori '{cat_input}' tidak dikenal, pakai 'lainnya'"))
                category = "lainnya"
            elif cat_input:
                category = cat_input

            print()

        # Deteksi kategori otomatis kalau tidak ditentukan
        if category is None:
            first_word = fact.split()[0].lower() if fact.split() else ""
            category = first_word if first_word in self.MEMORY_CATEGORIES else "lainnya"

        if interactive:
            print(f"  {colored('Ringkasan:', C.GRAY)}")
            print(f"  Fakta     : {colored(fact, C.BOLD)}")
            print(f"  Kategori  : {colored(category, C.YELLOW)}")
            print()

        success_flag, msg = self.memory_manager.create(self.auth.current_user.id, fact, category)
        if success_flag:
            print(success("Memory berhasil disimpan!"))
            print(dim("   Lihat dengan /list-memory • hapus dengan /forget <id>"))
        else:
            print(error(msg))
        return True

    def _list_memory(self, args):
        if not self.auth.is_logged_in:
            print(error("Login dulu pakai /login"))
            return True
        category = args.strip() if args else None
        memories = self.memory_manager.read(self.auth.current_user.id, category)
        if not memories:
            print(warning("Belum ada memory"))
            return True

        print()
        print(f"  {colored('🧠 Memory', C.BRIGHT_BLUE, bold=True)}")
        if category:
            print(f"  {dim('Kategori:')} {colored(category, C.YELLOW)}")
        print(f"  {'─' * 75}")
        print(f"  {colored('ID', C.GRAY):<6} {colored('Kategori', C.GRAY):<15} {colored('Fakta', C.GRAY)}")
        print(f"  {'─' * 75}")
        for m in memories:
            fact_display = m["fact"]
            if len(fact_display) > 48:
                fact_display = fact_display[:45] + "..."
            cat_color = {
                "preferensi": C.BRIGHT_GREEN,
                "fakta_pribadi": C.BRIGHT_CYAN,
                "pekerjaan": C.BRIGHT_YELLOW,
                "lainnya": C.GRAY,
            }.get(m["category"], C.WHITE)
            print(f"  {str(m['id']):<6} {colored(m['category'], cat_color):<15} {fact_display}")
        print()
        return True

    def _update_memory(self, args):
        if not self.auth.is_logged_in:
            print(error("Login dulu pakai /login"))
            return True
        parts = args.split(maxsplit=1)
        if len(parts) < 2:
            print(error("Format: /update-memory <id> <fakta_baru>"))
            return True
        mem_id, new_fact = int(parts[0]), parts[1]
        success_flag, msg = self.memory_manager.update(mem_id, new_fact)
        if success_flag:
            print(success(msg))
        else:
            print(error(msg))
        return True

    def _forget(self, args):
        if not self.auth.is_logged_in:
            print(error("Login dulu pakai /login"))
            return True
        if not args:
            print(error("Format: /forget <id>"))
            return True
        success_flag, msg = self.memory_manager.delete(int(args.strip()))
        if success_flag:
            print(success(msg))
        else:
            print(error(msg))
        return True

    # ─── Reminders ──────────────────────────────────────────────────

    def _parse_date(self, date_str):
        """Try to parse date string into MySQL-compatible datetime format."""
        date_str = date_str.strip()
        formats = [
            ("%Y-%m-%d %H:%M", True),
            ("%Y-%m-%d", False),
            ("%d/%m/%Y %H:%M", True),
            ("%d/%m/%Y", False),
            ("%d-%m-%Y %H:%M", True),
            ("%d-%m-%Y", False),
        ]
        for fmt, has_time in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%Y-%m-%d %H:%M:%S" if has_time else "%Y-%m-%d 23:59:59")
            except ValueError:
                continue
        return None

    def _remind(self, args):
        if not self.auth.is_logged_in:
            print(error("Login dulu pakai /login"))
            return True

        task = ""
        due_date = None
        priority = "medium"
        is_recurring = False
        recurrence_pattern = None

        if args:
            # Try to parse inline: /remind <task> <date>
            parts = args.rsplit(maxsplit=1)
            task = parts[0]
            if len(parts) > 1:
                due_date = self._parse_date(parts[1])
                if not due_date:
                    print(error(f"Format tanggal tidak valid: '{parts[1]}'"))
                    print(dim("   Contoh: 2026-09-20, 20/09/2026, 2026-09-20 14:00"))
                    return True
        else:
            # Interactive mode
            print()
            print(f"  {colored('⏰ Buat Reminder Baru', C.BRIGHT_BLUE, bold=True)}")
            print(f"  {'─' * 40}")
            print()

            task = input(f"  {colored('Tugas', C.CYAN)}: ").strip()
            if not task:
                print(error("Tugas tidak boleh kosong"))
                return True

            date_input = input(
                f"  {colored('Tanggal', C.CYAN)} {dim('(contoh: 2026-09-20 atau 20/09/2026)')}: "
            ).strip()
            if not date_input:
                print(error("Tanggal tidak boleh kosong"))
                return True
            due_date = self._parse_date(date_input)
            if not due_date:
                print(error(f"Format tanggal tidak valid: '{date_input}'"))
                print(dim("   Contoh: 2026-09-20, 20/09/2026, 2026-09-20 14:00"))
                return True

            prio_input = input(
                f"  {colored('Prioritas', C.CYAN)} {dim('[high/medium/low] (default: medium)')}: "
            ).strip().lower()
            if prio_input and prio_input in ["high", "medium", "low"]:
                priority = prio_input
            elif prio_input:
                print(warning(f"Prioritas '{prio_input}' tidak dikenal, pakai 'medium'"))

            is_recurring = False
            recurrence_pattern = None
            rec_input = input(
                f"  {colored('Berulang?', C.CYAN)} {dim('[daily/weekly/monthly] (enter = tidak)')}: "
            ).strip().lower()
            if rec_input in ["daily", "weekly", "monthly"]:
                is_recurring = True
                recurrence_pattern = rec_input
            elif rec_input:
                print(warning(f"Pattern '{rec_input}' tidak dikenal, reminder dibuat non-berulang"))

            print()

        # Show confirmation
        print(f"  {colored('Ringkasan:', C.GRAY)}")
        print(f"  Tugas      : {colored(task, C.BOLD)}")
        print(f"  Tanggal    : {colored(due_date, C.YELLOW)}")
        prio_colors = {"high": C.BRIGHT_RED, "medium": C.BRIGHT_YELLOW, "low": C.GREEN}
        print(f"  Prioritas  : {colored(priority, prio_colors.get(priority, C.WHITE))}")
        print(f"  Berulang   : {colored(recurrence_pattern if is_recurring else '-', C.YELLOW)}")
        print()

        success_flag, msg = self.reminder_manager.create(
            self.auth.current_user.id, task, due_date, priority,
            is_recurring=is_recurring, recurrence_pattern=recurrence_pattern,
        )
        if success_flag:
            print(success(f"Reminder dibuat: {colored(task, C.BOLD)}"))
        else:
            print(error(msg))
        return True

    def _reminders(self, args):
        if not self.auth.is_logged_in:
            print(error("Login dulu pakai /login"))
            return True
        status = None
        if "--pending" in args:
            status = "pending"
        elif "--done" in args:
            status = "done"
        reminders = self.reminder_manager.read(self.auth.current_user.id, status)
        if not reminders:
            print(warning("Belum ada reminder"))
            return True

        # Status label
        if status == "pending":
            label = "⏰ Reminder Aktif"
        elif status == "done":
            label = "✅ Reminder Selesai"
        else:
            label = "⏰ Semua Reminder"

        print()
        print(f"  {colored(label, C.BRIGHT_BLUE, bold=True)}")
        print(f"  {'─' * 85}")

        # Priority colors
        p_colors = {"high": C.BRIGHT_RED, "medium": C.BRIGHT_YELLOW, "low": C.GREEN}
        s_colors = {"pending": C.BRIGHT_YELLOW, "done": C.BRIGHT_GREEN}

        for r in reminders:
            p_status = "done" if r["is_done"] else "pending"
            p_str = r["priority"]
            due = str(r["due_date"]) if r["due_date"] else "-"
            task_display = r["task"]
            if len(task_display) > 37:
                task_display = task_display[:34] + "..."

            id_str = str(r["id"])
            print(
                f"  {colored(id_str, C.GRAY):<6} "
                f"{colored(p_str, p_colors.get(p_str, C.WHITE)):<16} "
                f"{colored(p_status, s_colors.get(p_status, C.WHITE)):<14} "
                f"{due:<18} "
                f"{task_display}"
            )

        print(f"  {'─' * 85}")
        print(f"  {dim(f'Total: {len(reminders)} reminder')}")
        print()
        return True

    def _update_reminder(self, args):
        if not self.auth.is_logged_in:
            print(error("Login dulu pakai /login"))
            return True
        if not args:
            print(error("Format: /update-reminder <id> done  — tandai selesai"))
            return True
        parts = args.split(maxsplit=1)
        rem_id = int(parts[0])
        action = parts[1].strip().lower() if len(parts) > 1 else ""

        if action == "done":
            success_flag, msg = self.reminder_manager.update(rem_id, "is_done", True)
        elif action == "undo":
            success_flag, msg = self.reminder_manager.update(rem_id, "is_done", False)
        else:
            # Fallback: /update-reminder <id> <field> <value>
            field_val = action.split(maxsplit=1)
            if len(field_val) < 2:
                print(error("Format: /update-reminder <id> done | /update-reminder <id> <field> <value>"))
                print(dim("   Shortcut: done = tandai selesai, undo = batalkan selesai"))
                return True
            field, value = field_val
            if field == "is_done":
                value = value.lower() in ("true", "1", "yes")
            elif field == "is_recurring":
                value = value.lower() in ("true", "1", "yes")
            success_flag, msg = self.reminder_manager.update(rem_id, field, value)

        if success_flag:
            print(success(msg))
        else:
            print(error(msg))
        return True

    def _delete_reminder(self, args):
        if not self.auth.is_logged_in:
            print(error("Login dulu pakai /login"))
            return True
        if not args:
            print(error("Format: /delete-reminder <id>"))
            return True
        print(warning("Reminder yang dihapus tidak bisa dikembalikan!"))
        if self._confirm():
            success_flag, msg = self.reminder_manager.delete(int(args.strip()))
            if success_flag:
                print(success(msg))
            else:
                print(error(msg))
        else:
            print(dim("  Dibatalkan"))
        return True
