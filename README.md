# CLI AI Assistant

Asisten AI berbasis terminal yang mendukung percakapan multi-turn dengan fitur memori, pengingat, dan riwayat percakapan persisten menggunakan MySQL.

## Fitur Utama

- **Autentikasi & Manajemen Pengguna** - Registrasi, login, logout, edit profil, ganti password, hapus akun
- **Chat AI** - Percakapan multi-turn dengan dukungan OpenAI, Google Gemini, dan Anthropic
- **Sistem Memori** - AI secara otomatis mengingat fakta tentang pengguna lintas sesi
- **Pengingat** - Pengingat harian/mingguan/bulanan dengan notifikasi latar belakang
- **Riwayat Percakapan** - Penyimpanan sesi percakapan penuh dengan CRUD pesan
- **Action Tags** - AI dapat secara otonom membuat/memperbarui/menghapus memori dan pengingat melalui tag aksi

## Tech Stack

| Komponen | Teknologi |
|---|---|
| Bahasa | Python 3.13+ |
| Database | MySQL |
| LLM | OpenAI / Gemini / Anthropic |
| Autentikasi | bcrypt |
| HTTP Client | requests |
| Konfigurasi | python-dotenv |

## Instalasi

### Prasyarat

- Python 3.13+
- MySQL server

### Langkah-langkah

```bash
# 1. Clone repository
git clone <repo-url>
cd cli-assistant

# 2. Buat dan aktifkan virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup database
mysql -u root -p < schema.sql

# 5. Konfigurasi environment variables
copy .env.example .env
```

### Konfigurasi `.env`

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=cli_assistant
LLM_API_KEY=your-api-key-here
LLM_PROVIDER=openai        # Pilihan: openai, gemini, anthropic
```

## Menjalankan

```bash
python main.py
```

## Perintah CLI

| Kategori | Perintah | Deskripsi |
|---|---|---|
| **Autentikasi** | `/register` | Daftar akun baru |
| | `/login` | Masuk ke akun |
| | `/logout` | Keluar dari akun |
| | `/exit` | Keluar dari aplikasi |
| **Chat** | `/chat <pesan>` | Kirim pesan ke AI |
| **Profil** | `/profile` | Lihat profil |
| | `/update-profile <field> <nilai>` | Perbarui profil |
| | `/change-password` | Ganti password |
| | `/delete-account` | Hapus akun |
| **Riwayat** | `/sessions` | Lihat semua sesi |
| | `/history <session_id>` | Lihat riwayat sesi |
| | `/edit-message <id> <pesan>` | Edit pesan |
| | `/delete-message <id>` | Hapus pesan |
| | `/clear-session <id>` | Hapus sesi |
| | `/clear-history` | Hapus semua riwayat |
| **Memori** | `/remember [kategori] <fakt>` | Simpan memori |
| | `/list-memory [kategori]` | Lihat semua memori |
| | `/update-memory <id> <fakt>` | Perbarui memori |
| | `/forget <id>` | Hapus memori |
| **Pengingat** | `/remind [tugas] [tanggal]` | Buat pengingat |
| | `/reminders [--pending\|--done]` | Lihat pengingat |
| | `/update-reminder <id> done\|undo\|field nilai` | Perbarui pengingat |
| | `/delete-reminder <id>` | Hapus pengingat |
| **Sistem** | `/clear` | Bersihkan layar |
| | `/help [perintah]` | Tampilkan bantuan |

## Struktur Database

```
users              - Data pengenda (username, password hash)
conversations      - Riwayat percakapan per sesi
memories           - Fakta tentang pengguna per kategori
reminders          - Pengingat dengan prioritas dan pola berulang
```

