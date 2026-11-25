# Architecture Decision Records (ADR)

| ID | Tanggal | Keputusan | Status |
|---|---|---|---|
| ADR-001 | 2026-11-24 | Integrasi QAD via REST API | Diterima |
| ADR-002 | 2026-11-24 | Hosting on-premise | Diterima |
| ADR-003 | 2026-11-24 | Dashboard web dibangun sendiri | Diterima |
| ADR-004 | 2026-11-24 | e-Signature internal, PSrE ditunda | Diterima |
| ADR-005 | 2026-11-24 | ~~Desain multinasional sejak awal~~ | Digantikan ADR-008 |
| ADR-006 | 2026-11-24 | Format data stok mengikuti pola `sales.csv` | Diterima |
| ADR-007 | 2026-11-24 | LLM self-hosted di server GPU, angka dihitung SQL | Diterima |
| ADR-008 | 2026-11-24 | Cakupan Indonesia saja: IDR, WIB | Diterima |

---

### ADR-001 — Integrasi QAD via REST API
**Konteks:** QAD adalah system of record. **Keputusan:** Konektor membaca via API dengan sinkron inkremental, paginasi, retry, rate limit. **Konsekuensi:** Perlu dokumentasi endpoint & akun service dari tim QAD; tidak ada akses DB langsung.

### ADR-002 — Hosting on-premise
**Keputusan:** Seluruh layanan & data di data center perusahaan (Kubernetes). **Konsekuensi:** Tim perlu mengelola server, backup, patching; egress hanya ke Microsoft 365.

### ADR-003 — Dashboard web sendiri
**Keputusan:** Next.js + library chart (Apache ECharts). **Konsekuensi:** Fleksibel & tanpa lisensi BI per user, tetapi butuh effort pengembangan & RLS di backend.

### ADR-004 — e-Signature internal
**Keputusan:** Tanda tangan elektronik internal (SSO + hash SHA-256 + audit trail). **Konsekuensi:** Belum berkekuatan tanda tangan tersertifikasi; untuk dokumen legal eksternal tetap manual sampai integrasi PSrE.

### ADR-005 — Multinasional
**Keputusan:** `entity_code`, mata uang, zona waktu, bahasa di semua tabel & UI sejak fase 0. **Konsekuensi:** Skema sedikit lebih kompleks, menghindari migrasi besar nanti.

### ADR-006 — Format stok
**Keputusan:** Skema stok di [DATA-DICTIONARY.md](DATA-DICTIONARY.md) §3, berpola sama dengan `sales.csv`.

### ADR-007 — LLM self-hosted (diterima)
**Keputusan:** Server GPU on-premise dipakai bersama untuk LLM (vLLM, model open-weight) dan beban analitik IoT. LLM hanya menulis narasi dari JSON KPI. **Konsekuensi:** Perlu kuota GPU per workload (mis. Kubernetes GPU scheduling) agar LLM tidak mengganggu IoT.

### ADR-008 — Indonesia saja
**Konteks:** Operasi yang dicakup hanya di Indonesia. **Keputusan:** Satu negara, mata uang IDR, zona waktu jadwal WIB (Asia/Jakarta), UI Bahasa Indonesia. Kolom `entity_code` tetap dipertahankan (default `ID01`) agar bisa dipakai untuk pabrik/entitas berbeda. Tidak ada konversi kurs. **Menggantikan:** ADR-005.
