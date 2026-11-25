# API SPECIFICATION — Spesifikasi Antarmuka REST API
## Platform Digital Operasional Kacang Dua Kelinci

| Item | Nilai |
|---|---|
| Versi | 0.1 (Draft) |
| Tanggal | 24 Nov 2026 |
| Status | Menunggu review stakeholder |
| Acuan | [SRS.md](SRS.md), [FSD.md](FSD.md), [SPEC.md](SPEC.md) |

---

## 1. Konvensi Antarmuka Global
- **Base URL:** `/api/v1`
- **Format Pertukaran Data:** JSON (`Content-Type: application/json; charset=utf-8`).
- **Penamaan Properti:** `snake_case` (konsisten dengan skema database).
- **Autentikasi & Otorisasi:** Header HTTP `Authorization: Bearer <OIDC_JWT_TOKEN>` via SSO Microsoft Entra ID.
- **Standar Pelacakan Request:** Header wajib `X-Request-ID: <UUID>` diteruskan ke seluruh log tracing.
- **Idempotensi Permintaan Write:** Header opsional/wajib `Idempotency-Key: <UUID>` untuk operasi mutasi dan sinkronisasi offline.
- **Format Penanganan Error:** Sesuai RFC 7807 (*Problem Details for HTTP APIs*):
```json
{
  "type": "https://kacang.internal/errors/invalid-parameter",
  "title": "Parameter Tidak Valid",
  "status": 400,
  "detail": "Nilai 'discount_idr' tidak boleh bernilai negatif.",
  "instance": "/api/v1/etl/uploads/sales",
  "request_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"
}
```

---

## 2. Katalog Endpoint per Domain Layanan

### 2.1 Modul Sistem & Pemeriksaan Kesehatan
- **`GET /api/v1/health`**
  - **Deskripsi:** Liveness probe untuk Kubernetes / Docker monitor.
  - **Akses:** Publik (tanpa auth).
  - **Respons 200 OK:** `{"status": "pass", "version": "0.1.0"}`
- **`GET /api/v1/ready`**
  - **Deskripsi:** Readiness probe untuk menguji keterhubungan ke database PostgreSQL, Redis, MinIO, dan vLLM.
  - **Akses:** Publik.
  - **Respons 200 OK:**
    ```json
    {
      "status": "ready",
      "checks": {
        "postgres": "connected",
        "redis": "connected",
        "minio": "connected",
        "vllm": "connected"
      }
    }
    ```

### 2.2 Modul Ingesti & ETL Data
- **`POST /api/v1/etl/uploads/{dataset}`**
  - **Deskripsi:** Mengunggah file CSV/Excel (`sales`, `stock`, `budget`) untuk diproses pipeline ETL.
  - **Peran:** `admin`, `it_ops`.
  - **Parameter Path:** `dataset` (`sales` | `stock` | `budget`).
  - **Respons 202 Accepted:**
    ```json
    {
      "job_id": "c1f7b8a2-9e2b-4c5a-a3d8-e1a2b3c4d5e6",
      "status": "QUEUED",
      "dataset": "sales",
      "message": "File diterima dan antrean pemrosesan telah dibuat."
    }
    ```
- **`GET /api/v1/etl/runs/{job_id}`**
  - **Deskripsi:** Memeriksa status dan hasil eksekusi batch ingest.
  - **Respons 200 OK:**
    ```json
    {
      "job_id": "c1f7b8a2-9e2b-4c5a-a3d8-e1a2b3c4d5e6",
      "status": "SUCCESS",
      "total_rows": 1891,
      "valid_rows": 1888,
      "quarantined_rows": 3,
      "duration_seconds": 2.45
    }
    ```

### 2.3 Modul Dashboard Live & Analitik
- **`GET /api/v1/dashboard/overview`**
  - **Deskripsi:** Mengambil ringkasan kartu KPI utama sesuai otorisasi peran pengguna.
  - **Query Params:** `start_date=2026-09-01&end_date=2026-10-31&region=Jawa%20Barat`
  - **Respons 200 OK:**
    ```json
    {
      "net_sales_idr": 1845000000.0,
      "gross_sales_idr": 1950000000.0,
      "discount_total_idr": 105000000.0,
      "achievement_pct": 94.6,
      "growth_mom_pct": 3.5,
      "last_updated_wib": "2026-11-24 07:00:00"
    }
    ```
- **`GET /api/v1/dashboard/charts/daily-trend`**
  - **Deskripsi:** Mengambil deret waktu penjualan harian untuk komponen ECharts.
  - **Respons 200 OK:**
    ```json
    {
      "dates": ["2026-09-01", "2026-09-02", "2026-09-03"],
      "net_sales": [62400000, 58200000, 71500000],
      "carton_qty": [320, 298, 385]
    }
    ```

### 2.4 Modul AI Insight Agent & Microsoft Teams
- **`POST /api/v1/agent/summaries/dispatch`**
  - **Deskripsi:** Menjalankan komputasi KPI dan pengiriman pesan Adaptive Card Teams (dipicu otomatis oleh cron 07.00 WIB atau manual oleh admin).
  - **Peran:** `admin`, `it_ops`.
  - **Respons 200 OK:**
    ```json
    {
      "batch_id": "agt-20261124-01",
      "dispatched_count": 28,
      "fallback_template_count": 0,
      "failed_count": 0
    }
    ```
- **`GET /api/v1/agent/summaries/preview`**
  - **Deskripsi:** Menguji tampilan Adaptive Card dan narasi AI untuk pengguna saat ini tanpa mengirim ke Teams.
  - **Respons 200 OK:** Objek JSON Adaptive Card lengkap siap render di frontend.

### 2.5 Modul Operasional e-Signature
- **`POST /api/v1/esign/documents`**
  - **Deskripsi:** Mendaftarkan dokumen PDF baru dan menentukan daftar penandatangan.
  - **Payload:**
    ```json
    {
      "title": "Memo Internal Pengadaan Kemasan Sukro",
      "file_url": "minio://documents/2026/memo-089.pdf",
      "signers": [
        {"user_id": "usr-1", "order": 1, "role": "REVIEWER"},
        {"user_id": "usr-2", "order": 2, "role": "APPROVER"}
      ]
    }
    ```
- **`POST /api/v1/esign/documents/{id}/sign`**
  - **Deskripsi:** Membubuhkan tanda tangan digital pada dokumen.
  - **Header Wajib:** `Idempotency-Key`
  - **Respons 200 OK:** `{"status": "SIGNED", "signed_at_wib": "2026-11-24 14:30:15", "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"}`
