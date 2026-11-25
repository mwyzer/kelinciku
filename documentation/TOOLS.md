# TOOLS — Perkakas & Registri Tool Agent AI
## Platform Digital Operasional Kacang Dua Kelinci

| Item | Nilai |
|---|---|
| Versi | 0.1 (Draft) |
| Tanggal | 24 Nov 2026 |
| Status | Menunggu review stakeholder |
| Acuan | [SRS.md](SRS.md), [SPEC.md](SPEC.md), [GUARDRAILS.md](GUARDRAILS.md) |

---

## 1. Registri Tool Agent AI (Runtime Agent Tool Registry)

Layanan AI Insight Agent dan fitur interaktif Q&A beroperasi menggunakan fungsi-fungsi perkakas (*agent tools*) yang ketat, bersifat hanya-baca (*read-only*), dan dibatasi oleh hak akses pengguna (*user scope*):

### 1.1 `get_kpi_summary(scope_type, scope_value, start_date, end_date)`
- **Deskripsi:** Menghitung total net sales, target budget, persentase pencapaian, dan pertumbuhan periode sebelumnya secara deterministik melalui query database SQL.
- **Skema Parameter:**
  ```json
  {
    "type": "object",
    "properties": {
      "scope_type": {"type": "string", "enum": ["NATIONAL", "REGION", "BRAND"]},
      "scope_value": {"type": "string"},
      "start_date": {"type": "string", "format": "date"},
      "end_date": {"type": "string", "format": "date"}
    },
    "required": ["scope_type", "scope_value", "start_date", "end_date"]
  }
  ```
- **Pembatasan:** Hanya mengembalikan ringkasan teragregasi, tidak pernah membocorkan data pribadi atau transaksi individual.

### 1.2 `get_critical_stock_alerts(branch, min_days_of_cover)`
- **Deskripsi:** Mengambil daftar SKU di cabang/gudang yang memiliki ketersediaan di bawah batas hari persediaan minimum.
- **Parameter:** `branch` (opsional jika pengguna memiliki scope regional), `min_days_of_cover` (default: 7 hari).

### 1.3 `validate_narrative_numbers(narrative_text, reference_kpi_json)`
- **Deskripsi:** Memindai seluruh angka, nominal Rupiah, dan nilai persentase pada teks narasi AI untuk memastikan 100% kecocokan dengan data acuan.
- **Output:** `{"is_valid": true|false, "unmatched_tokens": []}`.

### 1.4 `render_and_send_teams_card(recipient_channel_or_upn, card_payload)`
- **Deskripsi:** Mengirimkan kartu interaktif Microsoft Teams Adaptive Card melalui antarmuka Graph API / Webhook dengan retry otomatis 3 kali.

---

## 2. Toolchain Pengembangan, Infrastruktur & Operasional

| Kategori | Nama Perangkat | Versi / Rilis | Peran dalam Proyek |
|---|---|---|---|
| **Bahasa & Runtime** | Python | 3.12+ | Backend REST API, engine ETL, dan pemrosesan data. |
| **Framework Backend** | FastAPI | 0.111+ | Kerangka web API asynchronous performa tinggi. |
| **ORM & Migrasi** | SQLAlchemy & Alembic | 2.0+ | Pemodelan objek data dan migrasi skema database terkontrol. |
| **Layanan Asinkron** | Celery & Redis | 5.4+ / 7.2+ | Broker antrean tugas latar belakang dan scheduler berkala. |
| **Frontend & UI** | Next.js & Tailwind CSS | 14+ (App Router) | Portal web dashboard live dan aplikasi internal PWA. |
| **Visualisasi Data** | Apache ECharts | 5.5+ | Komponen grafik interaktif performa tinggi (line, bar, pie). |
| **Basis Data Utama** | PostgreSQL | 16 | Penyimpanan data warehouse (star schema) dan data transaksional. |
| **Deret Waktu (IoT)** | TimescaleDB | Ekstensi PG 16 | Hypertable untuk telemetri sensor pabrik dan analisis OEE. |
| **Penyimpanan Objek** | MinIO | Standalone / Cluster | Object storage S3-compatible on-premise untuk file PDF & foto. |
| **Message Broker IoT** | EMQX | 5.x | Broker MQTT skala industri untuk koneksi ribuan sensor pabrik. |
| **Mesin Inferensi AI** | vLLM | 0.5+ | Server inferensi model bahasa terbuka (open-weight) di GPU lokal. |
| **Observability** | Prometheus, Grafana, Loki | Versi Terbaru | Monitoring metrik sistem, visualisasi log, dan alert insiden. |
| **Kontainer & Orkestrasi** | Docker & Kubernetes (RKE2) | 24+ / 1.28+ | Standardisasi deployment dev (compose) hingga production HA. |
