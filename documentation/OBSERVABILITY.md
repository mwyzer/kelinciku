# OBSERVABILITY — Monitoring, Metrik, Log & Alerting
## Platform Digital Operasional Kacang Dua Kelinci

| Item | Nilai |
|---|---|
| Versi | 0.1 (Draft) |
| Tanggal | 24 Nov 2026 |
| Status | Menunggu review stakeholder |
| Acuan | [SRS.md](SRS.md), [ARCHITECTURE.md](ARCHITECTURE.md), [SPEC.md](SPEC.md) |

---

## 1. Arsitektur Tiga Pilar Observability On-Premise

```mermaid
flowchart LR
  subgraph Sources ["Sumber Telemetri"]
    FASTAPI[FastAPI Backend API]
    CELERY[Celery Workers]
    EMQX[EMQX IoT Broker]
    PG[(PostgreSQL & TimescaleDB)]
    VLLM[vLLM GPU Engine]
  end

  subgraph Aggregators ["Pengumpul & Penyimpan"]
    PROM[Prometheus (Metrik)]
    LOKI[Grafana Loki (Log Terstruktur)]
  end

  subgraph Presentation_Alerts ["Visualisasi & Notifikasi"]
    GRAF[Grafana Dashboards]
    ALERT[Alertmanager]
    TEAMS[Channel MS Teams: IT Alerts]
  end

  FASTAPI & CELERY & PG & VLLM -->|Metrics Scrape| PROM
  FASTAPI & CELERY & EMQX -->|JSON Logs| LOKI
  PROM --> GRAF
  LOKI --> GRAF
  PROM --> ALERT --> TEAMS
```

---

## 2. Standar Log Terstruktur Format JSON

Seluruh komponen aplikasi wajib menghasilkan log dalam format baris JSON tunggal:
```json
{
  "timestamp": "2026-11-24T00:00:15.123Z",
  "level": "INFO",
  "service": "kacang-backend-etl",
  "environment": "production",
  "request_id": "c1f7b8a2-9e2b-4c5a-a3d8-e1a2b3c4d5e6",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "user_id": "usr-8f2a1b9c",
  "entity_code": "ID01",
  "event": "etl_batch_completed",
  "details": {
    "dataset": "sales",
    "total_rows": 1891,
    "valid_rows": 1888,
    "quarantined_rows": 3,
    "duration_ms": 2450
  }
}
```

---

## 3. Katalog Metrik Kunci (*Golden Signals & Domain Metrics*)

| Nama Metrik | Tipe | Sumber | Deskripsi & Batas Waspada |
|---|---|---|---|
| `http_request_duration_seconds` | Histogram | FastAPI | Durasi latensi endpoint API (p95 wajib < 3.0 detik). |
| `http_requests_total` | Counter | FastAPI | Jumlah total request HTTP dikelompokkan berdasarkan status code. |
| `etl_rows_processed_total` | Counter | Worker ETL | Akumulasi baris data yang berhasil diproses ke DWH. |
| `etl_rows_quarantined_total` | Counter | Worker ETL | Jumlah baris yang gagal dan dipindahkan ke karantina. |
| `agent_dispatch_success_total` | Counter | Agent Worker | Total pesan ringkasan yang sukses dikirim ke Microsoft Teams. |
| `agent_hallucination_fallback_total`| Counter | Gate AI | Jumlah narasi AI yang digantikan template baku karena salah angka. |
| `iot_active_machines_count` | Gauge | IoT Monitor | Jumlah mesin pabrik berstatus aktif mengirimkan data telemetri. |
| `iot_machines_offline_count` | Gauge | IoT Monitor | Jumlah mesin yang tidak mengirim sinyal > 120 detik (Alert jika > 0). |
| `gpu_vram_usage_bytes` | Gauge | vLLM / Node | Pemakaian memori GPU pada server on-premise (Waspada jika > 85%). |

---

## 4. Aturan Peringatan Insiden (*Alerting Rules*)

| Severity | Kondisi Pemicu Alert | Target Waktu Notifikasi | Kanal Notifikasi |
|---|---|---|---|
| **P1 - Critical** | Layanan database PostgreSQL mati atau disk penyimpanan data > 90%. | < 1 Menit | Teams IT Alerts & SMS Pager |
| **P1 - Critical** | Mesin pabrik utama offline > 2 menit selama jam shift produksi. | < 2 Menit | Teams Pabrik Maintenance |
| **P2 - High** | Job ETL harian gagal atau tingkat error validasi batch > 10%. | < 5 Menit | Teams IT Alerts |
| **P2 - High** | Persentase error API HTTP 5xx > 2% selama rentang waktu 5 menit. | < 5 Menit | Teams IT Alerts |
| **P3 - Warning** | Terdeteksi stok SKU tertentu di cabang berada di bawah level minimum. | Sesuai jadwal harian | Teams Cabang Terkait |
| **P3 - Warning** | AI Insight Agent menggunakan template fallback > 5 kali berturut-turut. | < 15 Menit | Teams IT Developer |

---

## 5. Prosedur Tanggap Darurat (*Incident Runbook Ringkas*)

### Kasus: Job Ingesti Data Penjualan Gagal (P2)
1. Periksa log error pada Grafana Loki dengan query: `{service="kacang-backend-etl", level="ERROR"}`.
2. Jika penyebabnya adalah file format salah atau korup, hubungi tim pengunggah data dan arahkan perbaikan baris yang ada di tabel `staging.quarantine`.
3. Jika masalah disebabkan oleh database timeout, periksa status koneksi PostgreSQL pool dan jalankan ulang task Celery terkait melalui endpoint `/api/v1/etl/runs/{job_id}/retry`.
