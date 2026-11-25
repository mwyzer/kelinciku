# Arsitektur Sistem

Versi 0.2 · 24 Nov 2026 · Acuan: [SRS.md](SRS.md), [DECISIONS.md](DECISIONS.md)

## 1. Konteks Sistem On-Premise

```mermaid
flowchart LR
  subgraph DC["Data Center On-Premise"]
    API["Backend API (FastAPI)"]
    WEB["Web/PWA (Next.js)"]
    ETL["Worker ETL & Scheduler"]
    AGT["Insight Agent"]
    LLM["LLM self-hosted (vLLM GPU)"]
    PG[("PostgreSQL - DWH & OLTP")]
    TS[("TimescaleDB - IoT")]
    S3[("MinIO - Object Storage")]
    MQ["EMQX MQTT"]
    OBS["Prometheus, Grafana, Loki"]
  end
  QAD["QAD ERP API"] --> ETL
  XLS["Excel budget/stok"] --> ETL
  ETL --> PG
  SENS["Sensor pabrik"] --> MQ --> TS
  WEB --> API --> PG
  API --> TS
  API --> S3
  AGT --> PG
  AGT --> LLM
  AGT -->|proxy keluar| M365["Microsoft Teams / Entra ID"]
  WEB -->|OIDC| M365
```

## 2. Komponen & Tanggung Jawab

| Komponen | Tanggung Jawab Teknis |
|---|---|
| Web/PWA | Dashboard analitik, e-Signature, Gudang, HR, Rute Sales, IoT view (Bahasa Indonesia). |
| Backend API | Layanan REST FastAPI, RBAC, Row-Level Security, audit trail, validasi bisnis. |
| Worker ETL | Sinkronisasi data QAD API & Excel, pembersihan data, karantina baris cacat. |
| Scheduler | Penjadwalan Celery Beat untuk ringkasan harian/mingguan (07.00 WIB) dan ingest. |
| Insight Agent | Komputasi SQL deterministik, pembuatan narasi via vLLM, verifikasi numerik, Adaptive Card. |
| PostgreSQL | Skema `staging`, `dwh` (star schema), `app` (operasional internal). |
| TimescaleDB | Penyimpanan deret waktu sensor IoT pabrik, agregasi continuous 1m & 1h. |
| MinIO | Object storage penyimpanan dokumen PDF e-sign bertanda tangan dan foto absensi. |

## 3. Cakupan Domestik & Tata Kelola Waktu (ADR-008)
- Beroperasi khusus untuk wilayah Indonesia: mata uang tunggal IDR, tanpa konversi kurs.
- Waktu data disimpan dalam UTC di basis data dan ditampilkan dalam zona **WIB (Asia/Jakarta)**.
- Nilai `entity_code` (default `ID01`) dipertahankan untuk identifikasi pabrik dan entitas internal.
- Alokasi Server GPU: kapasitas VRAM dialokasikan terpisah (vLLM dibatasi 60%, 40% untuk analitik IoT).

## 4. Keamanan & Ketersediaan Tinggi (HA)
- Autentikasi terpusat via Microsoft Entra ID (OIDC PKCE); hak akses data dibatasi oleh PostgreSQL RLS.
- Klaster Kubernetes on-premise HA (RKE2) dengan cadangan data harian PostgreSQL dan WAL archiving (RPO ≤ 24 jam, RTO ≤ 4 jam).
- Referensi dokumen teknis terkait:
  - [DATABASE-DESIGN.md](DATABASE-DESIGN.md)
  - [API-SPECIFICATION.md](API-SPECIFICATION.md)
  - [EVENT-DESIGN.md](EVENT-DESIGN.md)
  - [SECURITY.md](SECURITY.md)
  - [OBSERVABILITY.md](OBSERVABILITY.md)
  - [GUARDRAILS.md](GUARDRAILS.md)


---

## 5. Data Flow Diagram (DFD) Operasional

### 5.1 DFD Level 0 (Context Diagram)

```mermaid
flowchart TD
    E1["👤 Salesman / Field Staff"]
    E2["👔 Head of Department (HOD)"]
    E3["⚙️ System Administrator"]
    E4["🤖 Telegram Bot API"]
    E5["📧 Google SMTP Server"]

    SYS(["🏢 Platform Digital Operasional PT Dua Kelinci<br/>(FastAPI Backend & Next.js 14)"])

    E1 -->|"1. Input Order Penjualan & Klaim Retur"| SYS
    SYS -->|"2. Status Alokasi Stok FEFO & Plafon Kredit"| E1

    E3 -->|"3. Unggah File Master CSV (Outlet, SKU, Gudang)"| SYS
    SYS -->|"4. Log Hasil Ingest & Validasi Data"| E3

    SYS -->|"5. Push Approval Request (Payload e-Sign)"| E4
    SYS -->|"6. Kirim HTML Request Email dengan Token"| E5

    E4 -->|"7. Callback Tindakan HOD (Approve / Reject)"| SYS
    E5 -->|"8. Direct HTTP Click Approval / Rejection"| SYS

    SYS -->|"9. Ringkasan Eksekutif & Status Audit Dokumen"| E2
    E2 -->|"10. Keputusan Otorisasi / Tanda Tangan Digital"| SYS
```

### 5.2 DFD Level 1 (Dekomposisi Proses Inti)

```mermaid
flowchart TD
    Admin["Petugas Master Data / Admin"]
    HOD["Head of Department (HOD)"]
    Sales["Tim Sales & Distributor"]
    Telegram["Telegram Bot Gateway"]
    Gmail["Google SMTP Service"]

    D1[("D1: master_products")]
    D2[("D2: master_outlets")]
    D3[("D3: master_warehouses")]
    D4[("D4: fact_sales")]
    D5[("D5: fact_stock (Batches)")]
    D6[("D6: esign_documents & audit_trail")]

    P1["1.0 Ingest & Validasi Data Penjualan"]
    P2["2.0 Master Data Management & Import CSV"]
    P3["3.0 Alokasi Stok Gudang Berbasis FEFO"]
    P4["4.0 Orkestrasi e-Signature & Hashing SHA-256"]
    P5["5.0 Dispatcher Notifikasi Dual-Channel"]
    P6["6.0 Callback Handler Otorisasi Dokumen"]

    Admin -->|"Unggah CSV (Products, Outlets, WH)"| P2
    P2 -->|"Upsert Record Baru / Update Limit"| D1
    P2 -->|"Upsert Limit Kredit & TOP"| D2
    P2 -->|"Upsert Kapasitas Depo"| D3

    Sales -->|"Data Faktur & Transaksi"| P1
    D1 -.->|"Validasi SKU"| P1
    D2 -.->|"Cek Plafon Kredit Outlet"| P1
    P1 -->|"Simpan Transaksi Bersih"| D4

    Sales -->|"Permintaan Order Pengiriman"| P3
    D4 -.->|"Qty Pesanan"| P3
    D5 <-->|"Pencocokan Batch Terdekat (FEFO)"| P3
    P3 -->|"Output Alokasi Pengambilan Gudang"| Sales

    Sales -->|"Submit Dokumen Otorisasi (Diskon/PO)"| P4
    P4 -->|"Simpan Draft & Kunci Hash SHA-256"| D6
    P4 -->|"Trigger Approval Event"| P5

    P5 -->|"Kirim Pesan + Tombol Aksi"| Telegram
    P5 -->|"Kirim Email Interaktif"| Gmail

    Telegram -->|"Aksi HOD (Approve / Reject)"| P6
    Gmail -->|"Klik Link Otorisasi HTTP GET"| P6

    P6 -->|"Update Status & Catat Audit Trail"| D6
    D6 -.->|"Status Terkini Dokumen"| HOD
```
