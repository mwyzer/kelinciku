---
name: duakelinci-ops-platform
description: Prosedur standar, panduan operasional, arsitektur, dan perintah manajemen untuk Platform Terpadu PT Dua Kelinci (FastAPI Backend, Next.js Frontend, Docker Compose, e-Signature HOD, WMS FEFO, dan AI Agent).
---

# SKILL: PT Dua Kelinci Operational Platform

Keahlian ini mencakup standar pemeliharaan, arsitektur microservice, eksekusi Docker, pengujian berkala, serta integrasi modul analitik FMCG PT Dua Kelinci.

---

## 1. Arsitektur Komponen & Port

| Komponen | Teknologi | Port | Fungsi Utama |
| :--- | :--- | :--- | :--- |
| **Backend** | Python 3.12 / FastAPI | `8000` | Deterministic SQL, Numeric Gate, Forecasting Holt-Winters, e-Sign HOD, Telegram Dispatcher |
| **Frontend Modern** | Next.js 14 / TypeScript / Tailwind | `3000` | App Router, Visualisasi KPI, Stepper Otorisasi HOD, FEFO Allocator |
| **Frontend Ringan** | HTML5 / Tailwind CDN / ECharts | `8000/sales-brief` | Standalone sales brief & direct Telegram sharing |
| **Database** | SQLite WAL Mode (`kacang_dwh.db`) | Local Mount | Menyimpan 1.891 faktur, 10.309 stok batch, target budget, dan user RLS |

---

## 2. Cara Menjalankan Sistem

### Opsi A: Menggunakan Docker Compose (Direkomendasikan untuk Produksi / Server)
Pastikan Docker Desktop aktif di mesin Anda:
```bash
# 1. Build dan jalankan seluruh container secara terisolasi di background
docker compose up -d --build

# 2. Cek status container yang berjalan
docker compose ps

# 3. Pantau log real-time
docker compose logs -f

# 4. Hentikan container
docker compose down
```

### Opsi B: Menjalankan Secara Lokal (Development / Debugging)
#### 1. Backend (FastAPI):
```powershell
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Akses Swagger Docs: `http://127.0.0.1:8000/docs`

#### 2. Frontend (Next.js 14):
```powershell
cd frontend
npm install
npm run dev
```
Akses Aplikasi Web: `http://localhost:3000`

---

## 3. Matriks Otorisasi e-Signature Berdasarkan HOD

Alur tanda tangan berjenjang lintas departemen:
```
[Dokumen Pengajuan] 
   ➜ Step 1: Head of Sales (muhammad.wyzer@gmail.com)
   ➜ Step 2: Head of Marketing (maya.indah@duakelinci.id)
   ➜ Step 3: Head of Finance (rudi.hartono@duakelinci.id)
   ➜ STATUS: COMPLETED (Sertifikat Digital SHA-256 Terbit)
```

- **Persetujuan Cepat Lewat Email**: Sistem mengirimkan email HTML dengan tombol **TANDATANGANI** dan **TOLAK**. Aksi tersebut diverifikasi lewat endpoint `/api/v1/esign/email-action`.
- **Integrasi Audit Trail**: Setiap klik tercatat dengan Timestamp WIB, alamat IP, email, dan hash dokumen.

---

## 4. Prosedur Pengujian & Validasi

Jalankan test suite berkala sebelum rilis versi baru:
```powershell
# Jalankan verifikasi 4 modul inti (Agent, Forecasting, e-Sign, WMS)
python scripts/test_all_modules.py

# Uji kirim ringkasan email eksekutif harian
python scripts/send_daily_report.py muhammad.wyzer@gmail.com
```

---

## 5. Integrasi Telegram Bot (BotFather)
Kirim laporan penjualan harian via Bot Telegram:
- **Endpoint**: `POST /api/v1/telegram/send`
- **Payload**:
  ```json
  {
    "bot_token": "<TOKEN_DARI_BOTFATHER>",
    "chat_id": "@mwyzer",
    "text": "Ringkasan Eksekutif Penjualan..."
  }
  ```
- **Kanal Web Langsung**: `http://localhost:3000/sales-brief` atau `http://127.0.0.1:8000/sales-brief`.
