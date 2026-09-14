import os
from dotenv import load_dotenv


class ConfigManager:
    def __init__(self, env_path=".env"):
        load_dotenv(env_path)
        self._validate()

    def _validate(self):
        required = ["DB_HOST", "DB_USER", "DB_NAME", "LLM_API_KEY", "LLM_PROVIDER"]
        missing = [key for key in required if not os.getenv(key)]
        if missing:
            raise ValueError(f"Config tidak lengkap, missing: {', '.join(missing)}")

    @property
    def db_host(self):
        return os.getenv("DB_HOST", "localhost")

    @property
    def db_user(self):
        return os.getenv("DB_USER", "root")

    @property
    def db_password(self):
        return os.getenv("DB_PASSWORD", "")

    @property
    def db_name(self):
        return os.getenv("DB_NAME", "cli_assistant")

    @property
    def llm_api_key(self):
        return os.getenv("LLM_API_KEY")

    @property
    def llm_provider(self):
        return os.getenv("LLM_PROVIDER", "openai")
