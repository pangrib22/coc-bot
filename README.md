# ⚔ Clash of Coins Bot

Bot otomatis untuk farming dan capture territory di Clash of Coins.

---

## 🚀 Cara Deploy ke Railway (Panduan Pemula)

### LANGKAH 1 — Buat akun GitHub (gratis)
1. Buka https://github.com
2. Klik **Sign up** → daftar pakai email
3. Verifikasi email kamu

---

### LANGKAH 2 — Upload kode ini ke GitHub
1. Login ke GitHub
2. Klik tombol **+** (pojok kanan atas) → **New repository**
3. Nama repo: `coc-bot`
4. Pilih **Public** → klik **Create repository**
5. Di halaman repo baru, klik **uploading an existing file**
6. Upload **semua file** dari folder ini (drag & drop semua)
7. Klik **Commit changes**

---

### LANGKAH 3 — Ambil Bearer Token dari game
1. Buka https://clashofcoins.com/play di Chrome
2. Tekan **F12** → klik tab **Network**
3. Di kolom filter ketik `api`
4. Klik salah satu request yang muncul (misalnya `user`)
5. Di panel kanan, klik tab **Headers**
6. Scroll ke bawah ke bagian **Request Headers**
7. Cari baris **Authorization** → copy semua teksnya (yang panjang)
8. Simpan dulu di notepad — ini adalah token kamu

---

### LANGKAH 4 — Deploy ke Railway
1. Buka https://railway.com → **Sign up with GitHub**
2. Klik **New Project** → **Deploy from GitHub repo**
3. Pilih repo `coc-bot` yang tadi dibuat
4. Tunggu build selesai (1-2 menit)
5. Klik tab **Variables** → tambahkan:

| Variable | Value |
|---|---|
| `BEARER_TOKEN` | Token yang kamu copy tadi (tanpa kata "Bearer") |
| `BOT_MODE` | `free` (atau `attack` kalau mau serang musuh) |
| `BOT_INTERVAL` | `30` |
| `MAX_TERRITORIES` | `50` |

6. Klik **Deploy** → bot mulai berjalan!

---

### LANGKAH 5 — Lihat Dashboard
1. Di Railway, klik tab **Settings** → **Networking**
2. Klik **Generate Domain**
3. Buka link yang muncul → kamu bisa lihat status bot real-time

---

## ⚙️ Konfigurasi

| Variable | Default | Keterangan |
|---|---|---|
| `BEARER_TOKEN` | **wajib** | Token dari DevTools game |
| `BOT_MODE` | `free` | `free` = claim gratis saja, `attack` = serang musuh juga |
| `BOT_INTERVAL` | `30` | Jeda antar aksi (detik). Jangan kurang dari 20! |
| `MAX_TERRITORIES` | `50` | Batas territory yang dikuasai |
| `LOG_LEVEL` | `INFO` | Level log: INFO / DEBUG |

---

## ⚠️ Penting

- **Token expired**: Token JWT biasanya expired dalam beberapa jam. Kalau bot berhenti, ambil token baru dari DevTools dan update di Railway Variables.
- **Jangan set interval terlalu cepat** — bisa kena rate limit / ban
- Gunakan dengan bijak sesuai Terms of Service game

---

## 📁 Struktur File

```
coc-bot/
├── bot/
│   ├── main.py       ← titik masuk program
│   ├── api.py        ← komunikasi dengan server game
│   ├── farmer.py     ← logika farming & attack
│   └── dashboard.py  ← tampilan web monitoring
├── Dockerfile        ← konfigurasi untuk Railway
├── railway.toml      ← konfigurasi Railway
├── requirements.txt  ← library Python yang dibutuhkan
└── .env.example      ← contoh variabel
```
