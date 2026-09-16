class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Foreground
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    GRAY = "\033[90m"

    # Bright foreground
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"

    # Background
    BG_BLUE = "\033[44m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_RED = "\033[41m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"


def colored(text: str, color: str, bold: bool = False) -> str:
    prefix = C.BOLD if bold else ""
    return f"{prefix}{color}{text}{C.RESET}"


def success(text: str) -> str:
    return colored(f"  ✓ {text}", C.GREEN)


def error(text: str) -> str:
    return colored(f"  ✗ {text}", C.RED)


def warning(text: str) -> str:
    return colored(f"  ⚠ {text}", C.YELLOW)


def info(text: str) -> str:
    return colored(f"  ℹ {text}", C.CYAN)


def dim(text: str) -> str:
    return colored(text, C.GRAY)
