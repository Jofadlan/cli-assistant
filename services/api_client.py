import time
import requests


class APIClient:
    PROVIDERS = {
        "openai": {
            "url": "https://api.openai.com/v1/chat/completions",
            "model": "gpt-3.5-turbo",
        },
        "gemini": {
            "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent",
            "model": "gemini-3.6-flash",
        },
        "anthropic": {
            "url": "https://api.anthropic.com/v1/messages",
            "model": "claude-3-haiku-20240307",
        },
    }

    def __init__(self, api_key, provider="openai", max_retries=3):
        self.api_key = api_key
        self.provider = provider
        self.max_retries = max_retries
        self._config = self.PROVIDERS.get(provider)
        if not self._config:
            raise ValueError(f"Provider '{provider}' tidak didukung. Pilih: {', '.join(self.PROVIDERS.keys())}")

    def chat(self, messages, temperature=0.7):
        for attempt in range(self.max_retries):
            try:
                if self.provider == "openai":
                    return self._call_openai(messages, temperature)
                elif self.provider == "gemini":
                    return self._call_gemini(messages, temperature)
                elif self.provider == "anthropic":
                    return self._call_anthropic(messages, temperature)
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    wait = 2 ** attempt
                    print(f"[API] Retry {attempt + 1}/{self.max_retries} dalam {wait} detik...")
                    time.sleep(wait)
                else:
                    return None, f"API gagal setelah {self.max_retries} percobaan: {e}"
        return None, "Unknown error"

    def _call_openai(self, messages, temperature):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self._config["model"],
            "messages": messages,
            "temperature": temperature,
        }
        resp = requests.post(self._config["url"], json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"], None

    def _call_gemini(self, messages, temperature):
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})
        headers = {"Content-Type": "application/json"}
        payload = {"contents": contents, "generationConfig": {"temperature": temperature}}
        url = f"{self._config['url']}?key={self.api_key}"
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"], None

    def _call_anthropic(self, messages, temperature):
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        system_msg = ""
        user_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                user_messages.append(msg)
        payload = {
            "model": self._config["model"],
            "max_tokens": 1024,
            "messages": user_messages,
            "temperature": temperature,
        }
        if system_msg:
            payload["system"] = system_msg
        resp = requests.post(self._config["url"], json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data["content"][0]["text"], None
