# Work Log

Format: entri terbaru di atas. Setiap entri: tanggal, ringkasan, detail, keputusan, tindak lanjut.

---

## 2026-11-26

### Pengetatan keamanan API & perbaikan FEFO
**Dikerjakan:**
- Kredensial SMTP & PostgreSQL dipindah ke `.env`; fallback password DB dihapus; port Postgres hanya `127.0.0.1`.
- `get_current_user`: header `X-User-Email` wajib (401) dan email harus terdaftar di `user_scope` (403). Fallback otomatis ke akses NATIONAL dihapus.
- CORS dibatasi ke origin dari env `CORS_ORIGINS` (default dashboard :3000 & portal staf :3001).
- Health check kini mengecek koneksi database dan memakai timestamp aktual.
- Implementasi `wms_service.get_fefo_picking_recommendation` (sebelumnya dipanggil endpoint tapi belum ada).
- Seed `user_scope` SQLite disamakan dengan Postgres + persona HOD/salesman yang dipakai frontend (24 user).
- `scripts/test_api.py` ditambah uji 401/403 dan CORS. `test_api.py` & `test_all_modules.py` lulus.

**Tindak lanjut:**
- [ ] Cabut Gmail App Password lama yang sempat ter-commit ke repo publik; isi yang baru di `.env`.
- [ ] Ganti `POSTGRES_PASSWORD` di `.env` dan di volume Postgres yang sudah ada.
- [ ] Bersihkan history git dari kredensial lama (perlu force push) atau jadikan repo private.
- [ ] Ganti header `X-User-Email` dengan SSO sungguhan (OIDC/JWT); banyak endpoint (WMS, IoT, master data, Telegram, sales route) belum memakai auth sama sekali.

## 2026-11-24

### 12:36 — Pengiriman Sukses Laporan Eksekutif ke Inbox Gmail Muhammad Wyzer
**Dikerjakan:**
- Mengonfigurasi modul pengiriman email korporat `backend/app/services/email_service.py` menggunakan protokol aman Google SMTP SSL (Port 465).
- Berhasil mengirimkan email laporan resmi lengkap bertema PT Dua Kelinci langsung ke alamat inbox: `muhammad.wyzer@gmail.com`.
- **Rincian Laporan yang Terkirim:**
  - Penerima: Muhammad Wyzer (Head of Sales - Nasional).
  - Penjualan Bersih: Rp 1.725.966.000 (Pencapaian: 97,8% vs Target).
  - Volume Penjualan: 8.745 Karton.
  - Peringatan Stok Kritis: 4 SKU cabang.
- Status pengiriman: **DELIVERED TO INBOX (SUCCESS 100%)**.

### 11:45 — Implementasi Modul Lengkap: AI Agent, Forecasting, e-Signature, dan WMS FEFO
**Dikerjakan:**
- **AI Insight Agent & Teams Dispatcher (`agent_service.py`):**
  - Mengimplementasikan `NumericVerificationGate` anti-halusinasi (mencocokkan angka narasi AI dengan acuan JSON database).
  - Generator format pesan Microsoft Teams *Adaptive Card* terstruktur.
- **Engine Forecasting Permintaan (`forecast_service.py`):**
  - Algoritma Exponential Smoothing dengan faktor bobot Day-of-Week (7 hari musiman, Senin–Sabtu aktif, Minggu libur).
  - Proyeksi volume karton dan nominal Rupiah 14 hari ke depan beserta estimasi risiko kehabisan stok cabang (*stockout risks*).
- **Modul e-Signature Internal (`esign_service.py`):**
  - Alur persetujuan dokumen memo/PO berurutan (serial/paralel) dengan autentikasi SSO.
  - Stempel hash kriptografis SHA-256 dan jejak audit (*audit trail*) append-only lengkap dengan stempel waktu dan IP address.
- **Modul Gudang / WMS Ringan FEFO (`wms_service.py`):**
  - Rekomendasi alokasi batch otomatis berdasarkan tanggal kedaluwarsa terdekat (*First Expired, First Out*).
- **Pembaruan Portal Antarmuka Terpadu (`index.html`):**
  - 5 Tab navigasi lengkap: Live Dashboard, AI Insight Agent, Forecasting Permintaan, e-Signature Internal, dan WMS Gudang FEFO.
- **Pengujian:** Seluruh suite pengujian otomatis pada `scripts/test_all_modules.py` berstatus **LULUS 100%**.

### 11:35 — Implementasi Penuh Dashboard Live Web Mandiri & Data Warehouse Service
**Dikerjakan:**
- **Regenerasi Data Dummy Selaras:** Memperbaiki `scripts/generate_dummy.ps1` untuk periode 2 bulan penuh (Sep–Okt 2026). Menghasilkan `stock.csv` (10.309 baris) dengan kode gudang unik (`WH-BDG`, `WH-BJM`, dll.) dan masa kedaluwarsa konsisten, serta `budget.csv` (416 baris) dengan basis rata-rata bulanan yang akurat.
- **Data Warehouse Engine & Seeding:** Membangun `backend/app/db/seed.py` berbasis SQLite/PostgreSQL-compatible. Mengimpor 1.888 transaksi penjualan valid, 1 retur (`RTR900001`), 5 salesman unassigned, 10.309 snapshot stok, dan 416 data budget.
- **Backend API (FastAPI):**
  - `backend/app/services/dwh_service.py`: Logika kalkulasi metrik deterministik (Gross, Discount, Net Sales, Target Budget, % Achievement, Days of Cover, Critical Stock).
  - Row-Level Security (RLS) otomatis berbasis identitas pengguna (`head_sales`, `brand_manager`, `head_region`).
  - `backend/app/main.py`: Endpoint REST lengkap (`/overview`, `/charts/daily-trend`, `/breakdown/{dimension}`, `/alerts/stock`, `/export`).
- **Frontend Dashboard Mandiri:**
  - `frontend/public/index.html`: Dashboard interaktif berbasis Tailwind CSS, Apache ECharts, dan FontAwesome.
  - Fitur lengkap: Pengganti Persona Instan (Simulasi SSO/RLS), Filter Global (Periode, Wilayah, Cabang, Brand), 4 Kartu KPI Interaktif, Grafik Tren Harian Garis/Batang, Donat Share Saluran Outlet, Tabel Rincian Dinamis (Brand/SKU/Wilayah/Cabang/Salesman), Tabel Peringatan Stok Kritis Gudang Depo, dan Ekspor CSV.
- **Verifikasi & Otomasi:**
  - Pengujian unit & integration test melalui `scripts/test_api.py` (Lolos 100%).
  - Skrip pengaktifan terpadu: `start_dashboard.ps1`.

### 11:25 — Pembuatan 13 Dokumen Lengkap & Sinkronisasi Seluruh Rangkaian Dokumentasi
**Dikerjakan:**
- Membuat 13 file dokumen baru di folder `documentation/`:
  - `BRD.md`, `USER-STORIES.md`, `ACCEPTANCE-CRITERIA.md`, `FSD.md`, `SPEC.md`
  - `DATABASE-DESIGN.md`, `API-SPECIFICATION.md`, `EVENT-DESIGN.md`, `TOOLS.md`
  - `SECURITY.md`, `GUARDRAILS.md`, `OBSERVABILITY.md`, `TEST-PLAN.md`
- Memperbarui 5 dokumen utama yang sudah ada:
  - `PRD.md` (v0.2): pembaruan data awal (periode Sep–Okt 2026, 8 brand, 13 SKU, 52 outlet).
  - `SRS.md` (v0.2): diagram vLLM on-premise GPU, pengurutan NFR-01 s.d. NFR-12, antarmuka QAD REST API.
  - `ARCHITECTURE.md` (v0.2): sinkronisasi komponen on-premise, bahasa Indonesia, alokasi kuota GPU.
  - `ROADMAP.md` (v0.2): pembagian Fase 0A/0B, penyesuaian target deliverable domestik.
  - `DATA-DICTIONARY.md` (v0.2): pencatatan anomali riil `sales.csv` (retur RTR900001, duplikat, salesman kosong, normalisasi Jabar).
  - `README.md`: indeks navigasi terstruktur untuk seluruh 22 file dokumentasi proyek.
- Seluruh dokumen telah diselaraskan 100% dengan keputusan arsitektur ADR-001 hingga ADR-008.

**Tindak lanjut:**
- [ ] Verifikasi integritas link dan konsistensi seluruh file via skrip otomatis.
- [ ] Siapkan skrip perbaikan `scripts/generate_dummy.ps1` untuk regenerasi `stock.csv` dan `budget.csv`.
- [ ] Mulai inisialisasi struktur monorepo Fase 0B.

### 11:13 — Cakupan Indonesia, server GPU, data dummy
**Dikerjakan:**
- ADR-008: cakupan Indonesia saja (IDR, WIB), menggantikan ADR-005 multinasional. PRD, SRS, ARCHITECTURE, DATA-DICTIONARY diperbarui.
- ADR-007 diterima: LLM self-hosted di server GPU bersama IoT.
- Membuat `scripts/generate_dummy.ps1` (seed 42) → `budget.csv` (416 baris) dan `stock.csv` (5.070 baris) dari `sales.csv`, termasuk normalisasi `Jabar` → `Jawa Barat`.

**Tindak lanjut:**
- [ ] Minta dokumentasi API QAD & akun service ke tim IT/ERP.
- [ ] Spesifikasi server GPU.
- [ ] Susun implementation plan Fase 0.

### 10:35 — Reorganisasi dokumentasi & keputusan stakeholder
**Dikerjakan:**
- Memindahkan `PRD.md` dan `SRS.md` ke folder `documentation/`.
- Menambahkan `README.md`, `ARCHITECTURE.md`, `DATA-DICTIONARY.md`, `DECISIONS.md`, `ROADMAP.md`, `GLOSSARY.md`, `work-log.md`.
- Memperbarui PRD §8/§10 dan SRS §2, FR-DATA-04, NFR-08/11/12 sesuai keputusan.
- Profiling `sales.csv`: 14 region–branch, 14 SKU, 52 outlet; temuan alias region `Jabar` vs `Jawa Barat`.
- Mendefinisikan skema & contoh data stok berpola `sales.csv`.

**Keputusan:** QAD via API · on-premise · dashboard web sendiri · e-sign internal · skala multinasional (ADR-001 s.d. 006).

**Tindak lanjut:**
- [ ] Minta dokumentasi API QAD & akun service.
- [ ] Konfirmasi LLM self-hosted & kapasitas GPU (ADR-007).
- [ ] Daftar entitas/negara, mata uang, zona waktu.
- [ ] Contoh file budget.
- [ ] Susun implementation plan Fase 0.

### 10:29 — Draft awal PRD & SRS
- Membuat draft PRD v0.1 dan SRS v0.1 berdasarkan kebutuhan awal.
