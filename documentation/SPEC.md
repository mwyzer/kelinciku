# SPEC — Master Technical & Delivery Specification
## Platform Digital Operasional Kacang Dua Kelinci

| Item | Nilai |
|---|---|
| Versi | 0.1 (Draft) |
| Tanggal | 24 Nov 2026 |
| Status | Menunggu review stakeholder |
| Acuan | [BRD.md](BRD.md), [SRS.md](SRS.md), [ARCHITECTURE.md](ARCHITECTURE.md), [DECISIONS.md](DECISIONS.md) |

---

## 1. Ringkasan Eksekusi Proyek
Dokumen ini merupakan spesifikasi induk teknis (*Master Specification*) yang mengikat seluruh pedoman rekayasa perangkat lunak, arsitektur, konvensi antarmuka, struktur kode, tata kelola data, dan jaminan kualitas untuk platform operasional internal PT Dua Kelinci.

## 2. Struktur Repositori Terpadu (*Monorepo Structure*)

Repositori proyek dikelola dengan struktur modul yang terisolasi dan mudah dipelihara:
```
Kacang/
├── backend/                       # Python 3.12 FastAPI Application
│   ├── app/
│   │   ├── api/v1/                # Endpoint router per domain
│   │   ├── core/                  # Konfigurasi, security, dependencies
│   │   ├── db/                    # Session factory, Base model, Alembic
│   │   ├── models/                # SQLAlchemy 2 models (staging, dwh, app)
│   │   ├── schemas/               # Pydantic v2 data contracts
│   │   ├── services/              # Logika bisnis, ETL engine, agent runner
│   │   └── workers/               # Celery task definitions
│   ├── tests/                     # Pytest suite (unit, integration, contracts)
│   ├── alembic/                   # Database migrations
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                      # Next.js 14+ (App Router) PWA
│   ├── src/
│   │   ├── app/                   # Route pages (dashboard, esign, wh, hr, route, iot)
│   │   ├── components/            # UI components, charts (ECharts), forms
│   │   ├── hooks/                 # Custom React hooks, auth, offline sync
│   │   ├── lib/                   # API client, utility functions
│   │   └── types/                 # TypeScript interfaces & types
│   ├── public/                    # Manifest PWA, service worker, static assets
│   ├── Dockerfile
│   └── package.json
├── infra/                         # On-Premise Deployment Configurations
│   ├── docker-compose/            # Lingkungan pengembangan lokal (dev)
│   │   └── docker-compose.yml     # PG 16, Timescale, MinIO, Redis, EMQX, vLLM
│   ├── k8s/                       # Manifest Kubernetes on-premise (RKE2/k3s)
│   │   ├── base/
│   │   └── overlays/production/
│   └── monitoring/                # Prometheus rules, Grafana dashboards, Alertmanager
├── scripts/                       # Utilitas, generator data dummy, seed data
│   └── generate_dummy.ps1
├── documentation/                 # Rangkaian dokumentasi resmi proyek (22 file)
└── sales.csv                      # Baseline data transaksi nyata (Sep-Okt 2026)
```

---

## 3. Matriks Ketertelusuran Sistem (*System Traceability Matrix*)

| ID Bisnis | ID Kebutuhan (SRS) | ID User Story | Komponen Teknis Terkait | File Pengujian Utama |
|---|---|---|---|---|
| **BR-01** | FR-DATA-01 s.d. 05 | US-01 s.d. 05 | `backend/services/etl/`, `dwh.fact_sales` | `tests/test_etl_pipeline.py` |
| **BR-02** | FR-AGT-01, FR-AGT-05 | US-12, US-14 | `backend/services/agent/`, Teams Card Sender | `tests/test_agent_dispatcher.py` |
| **BR-03** | FR-AGT-02 s.d. 04 | US-13 | `NumericVerificationGate`, vLLM Client | `tests/test_numeric_guardrail.py` |
| **BR-04** | FR-DASH-01 s.d. 07 | US-06 s.d. 11 | `frontend/src/app/dashboard/`, ECharts | `tests/test_dashboard_api.py` |
| **BR-05** | NFR-03, NFR-04, 12 | US-10 | SSO Entra ID, Network Isolation, Vault | `tests/test_security_rbac.py` |
| **BR-06** | FR-IOT-01 s.d. 04 | US-27 s.d. 29 | EMQX Broker, TimescaleDB, Alert Dispatcher | `tests/test_iot_telemetry.py` |
| **BR-07** | FR-SIGN-01 s.d. 04 | US-20 s.d. 22 | `backend/services/esign/`, MinIO S3 Client | `tests/test_esign_workflow.py` |

---

## 4. Standar Kode & Konvensi Rekayasa (*Engineering Conventions*)

1. **Python (Backend):**
   - Mengikuti standar PEP 8, diverifikasi menggunakan `ruff check` dan `ruff format`.
   - Wajib menggunakan Type Hints penuh (`typing`, Pydantic models).
   - Seluruh query database interaktif wajib dioptimasi dengan indexing dan menghindari masalah N+1 (*eager loading* via SQLAlchemy).
2. **TypeScript / JavaScript (Frontend):**
   - Format penulisan diverifikasi menggunakan ESLint dan Prettier.
   - Mode ketat TypeScript (`strict: true`) tanpa penggunaan tipe `any`.
   - Menggunakan Tailwind CSS untuk utilitas antarmuka yang seragam dan responsif mobile.
3. **Format Tanggal dan Mata Uang:**
   - Database menyimpan stempel waktu dalam format UTC (`TIMESTAMPTZ`).
   - Tampilan antarmuka dan laporan mengekspresikan waktu dalam zona **WIB (Asia/Jakarta)**.
   - Nilai finansial diformat ke format Rupiah standar Indonesia: `Rp 1.250.000,00`.

---

## 5. Strategi Deployment & Lingkungan Kerja

| Parameter | Pengembangan Lokal (*Dev*) | Staging On-Premise | Produksi On-Premise |
|---|---|---|---|
| **Orkestrator** | Docker Compose | Kubernetes k3s Single-Node | Kubernetes RKE2 Multi-Node HA |
| **Basis Data** | PostgreSQL 16 (Container) | PostgreSQL 16 Standalone On-Prem | PostgreSQL Primary + Read Replica |
| **Object Storage** | MinIO Container Lokal | MinIO Cluster On-Premise | MinIO Distributed HA (Erasure Code) |
| **Inferensi LLM** | Mock Server / vLLM Mini | vLLM Server GPU Staging | vLLM Server Dedicated Cluster GPU |
| **Koneksi Teams** | Teams Webhook Test Channel | Bot Framework Staging Tenant | Production Enterprise Teams App |
