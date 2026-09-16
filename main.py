import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import ConfigManager
from services.database import Database
from services.auth import AuthManager
from services.user_manager import UserManager
from services.memory_manager import MemoryManager
from services.reminder_manager import ReminderManager
from services.conversation_manager import ConversationManager
from services.api_client import APIClient
from services.chat_session import ChatSession
from services.reminder_scheduler import ReminderScheduler
from utils.cli import CLIHandler
from utils.colors import C, colored


def print_banner():
    print()
    print(colored("  ╔══════════════════════════════════════════╗", C.CYAN))
    print(colored("  ║", C.CYAN) + colored("          🤖 CLI AI Assistant             ", C.BOLD) + colored("║", C.CYAN))
    print(colored("  ╠══════════════════════════════════════════╣", C.CYAN))
    print(colored("  ║", C.CYAN) + colored("  Chat pintar · Memory · Reminders        ", C.DIM) + colored("║", C.CYAN))
    print(colored("  ╚══════════════════════════════════════════╝", C.CYAN))
    print()


def main():
    print_banner()

    try:
        config = ConfigManager()
    except ValueError as e:
        print(colored(f"  ✗ Config error: {e}", C.RED))
        print(colored("  Pastikan file .env sudah diisi dengan benar", C.DIM))
        return

    db = Database(
        host=config.db_host,
        user=config.db_user,
        password=config.db_password,
        database=config.db_name,
    )

    if not db.connect():
        print(colored("  ✗ Gagal koneksi ke MySQL. Pastikan MySQL server jalan.", C.RED))
        return

    print(colored("  ✓ Terhubung ke MySQL", C.GREEN))

    auth = AuthManager(db)
    user_manager = UserManager(db)
    memory_manager = MemoryManager(db)
    reminder_manager = ReminderManager(db)
    conversation_manager = ConversationManager(db)

    try:
        api_client = APIClient(config.llm_api_key, config.llm_provider)
    except ValueError as e:
        print(colored(f"  ✗ API error: {e}", C.RED))
        return

    chat_session = ChatSession(
        api_client,
        conversation_manager,
        memory_manager=memory_manager,
        reminder_manager=reminder_manager,
    )

    cli = CLIHandler(
        auth=auth,
        user_manager=user_manager,
        memory_manager=memory_manager,
        reminder_manager=reminder_manager,
        conversation_manager=conversation_manager,
        chat_session=chat_session,
    )

    # Scheduler notifikasi reminder
    scheduler = ReminderScheduler(reminder_manager, prompt_fn=cli._prompt)
    cli.scheduler = scheduler

    print(colored("  Ketik /help untuk melihat semua perintah", C.GRAY))
    print()

    try:
        running = True
        while running:
            try:
                user_input = input(cli._prompt()).strip()
                if user_input:
                    running = cli.handle(user_input)
            except KeyboardInterrupt:
                print(colored("\n  Gunakan /exit untuk keluar", C.YELLOW))
            except EOFError:
                break
    finally:
        scheduler.stop()
        auth.logout()
        db.disconnect()
        print()
        print(colored("  Sampai jumpa! 👋", C.CYAN, bold=True))
        print()


if __name__ == "__main__":
    main()
