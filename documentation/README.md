# Dokumentasi Resmi Platform Digital Operasional Kacang Dua Kelinci

Indeks lengkap seluruh spesifikasi rekayasa perangkat lunak, arsitektur, kebijakan keamanan, dan rencana eksekusi proyek (Total: 22 dokumen).

---

### 1. Kebutuhan Bisnis, Produk & Pengguna
- [BRD.md](BRD.md) — Business Requirements Document: latar belakang bisnis, masalah, target KPI dampak.
- [PRD.md](PRD.md) — Product Requirements Document: lingkup modul, persona manajerial, asumsi, dan metrik keberhasilan.
- [USER-STORIES.md](USER-STORIES.md) — Daftar Epic dan rincian User Stories (`US-01` s.d. `US-31`).
- [ROADMAP.md](ROADMAP.md) — Rencana tahapan proyek (Fase 0A, 0B, hingga Fase 4).

### 2. Spesifikasi Fungsional & Rekayasa Sistem
- [SPEC.md](SPEC.md) — Master Technical & Delivery Specification: struktur monorepo, traceability matrix, standar kode.
- [SRS.md](SRS.md) — Software Requirements Specification: kebutuhan fungsional (`FR-*`) dan non-fungsional (`NFR-*`).
- [FSD.md](FSD.md) — Functional Specification Document: wireframe konseptual, logika perhitungan KPI, state machine.
- [ARCHITECTURE.md](ARCHITECTURE.md) — Arsitektur sistem on-premise, batas layanan, dan ketersediaan tinggi.

### 3. Model Data, Antarmuka & Event
- [DATABASE-DESIGN.md](DATABASE-DESIGN.md) — Desain skema multi-schema PostgreSQL 16, TimescaleDB, ERD, dan RLS.
- [DATA-DICTIONARY.md](DATA-DICTIONARY.md) — Kamus data tabel fakta, dimensi, serta anomali riil `sales.csv`.
- [API-SPECIFICATION.md](API-SPECIFICATION.md) — Kontrak antarmuka REST API (/api/v1) dan format payload.
- [EVENT-DESIGN.md](EVENT-DESIGN.md) — Arsitektur event Celery/Redis, topik MQTT EMQX, dan jadwal cron WIB.

### 4. AI, Keamanan & Batas Sistem (Guardrails)
- [GUARDRAILS.md](GUARDRAILS.md) — Kebijakan Zero-Math AI, gerbang verifikasi numerik, dan pembatasan alokasi GPU.
- [SECURITY.md](SECURITY.md) — Model ancaman STRIDE, matriks RBAC 10 peran, isolasi jaringan on-premise, kepatuhan UU PDP.
- [TOOLS.md](TOOLS.md) — Registri perkakas Agent AI dan toolchain pengembangan/infrastruktur on-premise.

### 5. Observability & Penjaminan Kualitas
- [OBSERVABILITY.md](OBSERVABILITY.md) — Log JSON terstruktur, metrik Prometheus, Grafana, alert insiden Teams, runbook.
- [TEST-PLAN.md](TEST-PLAN.md) — Strategi piramida pengujian, kasus uji kunci, kriteria masuk/keluar rilis.
- [ACCEPTANCE-CRITERIA.md](ACCEPTANCE-CRITERIA.md) — Kriteria penerimaan terukur berbasis Given/When/Then per fase.

### 6. Keputusan Arsitektur, Referensi & Catatan Kerja
- [DECISIONS.md](DECISIONS.md) — Catatan keputusan arsitektur (ADR-001 s.d. ADR-008).
- [GLOSSARY.md](GLOSSARY.md) — Glosarium istilah bisnis FMCG dan teknis operasional.
- [work-log.md](work-log.md) — Catatan log perkembangan pengerjaan harian.
