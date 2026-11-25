# BRD — Business Requirements Document
## Platform Digital Operasional Kacang Dua Kelinci

| Item | Nilai |
|---|---|
| Versi | 0.1 (Draft) |
| Tanggal | 24 Nov 2026 |
| Status | Menunggu review stakeholder |
| Acuan | [PRD.md](PRD.md), [SRS.md](SRS.md), [DECISIONS.md](DECISIONS.md) |

---

## 1. Ringkasan Eksekutif & Konteks Bisnis
PT Dua Kelinci mengoperasikan rantai pasok dan distribusi produk FMCG (kacang, wafer, biskuit, dan makanan ringan) di seluruh wilayah Indonesia. Saat ini, konsolidasi data kinerja penjualan, ketersediaan stok cabang/gudang, dan realisasi budget masih mengandalkan rekap manual dari sistem ERP QAD dan file Excel spreadsheet. Proses operasional harian seperti persetujuan dokumen, pencatatan mutasi gudang, kehadiran tim sales lapangan, serta pengawasan mesin pengolahan dan pengemasan di pabrik masih terfragmentasi.

Inisiatif ini bertujuan membangun platform digital terintegrasi on-premise yang mengotomatisasi aliran informasi operasional dan menyajikan analitik bisnis berbasis peran (Brand Manager, Head of Sales, Head of Region) serta insight harian melalui Microsoft Teams.

## 2. Permasalahan Bisnis Saat Ini (*As-Is*) vs Target Solusi (*To-Be*)

| Aspek | Kondisi Saat Ini (*As-Is*) | Target Kondisi (*To-Be*) |
|---|---|---|
| **Pelaporan Eksekutif & Manajerial** | Laporan penjualan dan stok disusun manual tiap akhir pekan/bulan menggunakan Excel. Data sering terlambat 24–72 jam dan terjadi perbedaan angka antar-divisi. | Ringkasan harian (07.00 WIB) dan mingguan (Senin 07.00 WIB) otomatis via Microsoft Teams Adaptive Cards. Angka terpusat dan konsisten. |
| **Visibilitas Kinerja** | Brand Manager dan Head of Region tidak memiliki dasbor real-time untuk memantau pencapaian target per SKU/outlet secara langsung. | Dashboard Live berbasis web mandiri dengan Row-Level Security (RLS) sesuai kewenangan peran masing-masing. |
| **Operasional Internal** | Dokumen memo, PO, dan persetujuan internal masih memakai kertas fisik atau file PDF terpisah tanpa validasi digital terstandar. | Modul e-Signature internal dengan autentikasi SSO Microsoft Entra ID, stempel SHA-256, dan jejak audit (*audit trail*). |
| **Aktivitas Lapangan & Gudang** | Rute salesman belum terverifikasi secara geolokasi; kontrol stok gudang rentan selisih sebelum stock opname fisik. | PWA Rute Sales dengan geofencing GPS; WMS Ringan dengan scan barcode dan alur First Expired, First Out (FEFO). |
| **Pengawasan Mesin Pabrik** | Pencatatan downtime mesin dan suhu ruang produksi dilakukan di lembar cek fisik manual. | Telemetri sensor IoT via MQTT, deteksi anomali < 2 menit, peringatan otomatis ke tim maintenance pabrik. |

## 3. Pemangku Kepentingan (*Stakeholders*)

| Peran Pemangku Kepentingan | Tanggung Jawab / Kepentingan Utama |
|---|---|
| **Direksi & Manajemen Eksekutif** | Pemantauan kesehatan bisnis nasional, kepatuhan anggaran, efisiensi belanja modal/operasional. |
| **Brand Manager** | Pertumbuhan penjualan per brand/SKU, margin, efektivitas promosi/diskon, pengawasan stok pergerakan lambat (*slow-moving*). |
| **Head of Sales** | Pencapaian target penjualan nasional, pemerataan distribusi per tipe outlet, produktivitas salesman. |
| **Head of Region / Branch Manager** | Kinerja operasional cabang, pencapaian target regional, mitigasi kehabisan stok (*stockout*) di depo/gudang cabang. |
| **Kepala Gudang & Logistik** | Ketepatan mutasi stok, penerapan FEFO, percepatan proses penerimaan (*goods receipt*) dan pengeluaran barang. |
| **HRD & People Operations** | Tertib kehadiran karyawan, akurasi data absensi lapangan/pabrik, simplifikasi alur cuti. |
| **Manajer Pabrik & Maintenance** | Utilisasi mesin (OEE), kepatuhan suhu/kelembapan ruang produksi, penurunan angka breakdown tak terencana. |
| **Tim IT & ERP QAD** | Kestabilan server on-premise, keandalan antarmuka QAD API, tata kelola keamanan dan perlindungan data pribadi. |

## 4. Kebutuhan Bisnis Tingkat Tinggi (*High-Level Requirements*)

- **BR-01 (Single Source of Truth):** Seluruh metrik penjualan, stok, dan budget harus bersumber dari satu data warehouse terpusat yang disinkronkan dari QAD ERP API dan data perencanaan.
- **BR-02 (Proaktif & Personalisasi):** Manajer tidak perlu mencari data secara manual; sistem harus mengirimkan insight yang dipersonalisasi sesuai lingkup otoritasnya langsung ke Microsoft Teams.
- **BR-03 (Akurasi Tanpa Halusinasi):** Seluruh angka finansial dan volume karton wajib dihitung secara deterministik oleh sistem data. Model AI dilarang melakukan aproksimasi atau manipulasi angka.
- **BR-04 (Kemudahan Akses Tanpa Lisensi Tambahan):** Dashboard dibangun sebagai portal web mandiri tanpa ketergantungan lisensi per-pengguna dari platform BI pihak ketiga.
- **BR-05 (Kedaulatan & Keamanan Data):** Seluruh infrastruktur komputasi, basis data, dan model bahasa (LLM) ditempatkan on-premise di data center perusahaan, dengan akses keluar dibatasi ketat ke Microsoft 365.
- **BR-06 (Kecepatan Deteksi Operasional):** Peringatan gangguan stok kritis atau downtime mesin pabrik harus terkirim kepada penanggung jawab terkait dalam waktu kurang dari 2 menit.
- **BR-07 (Efisiensi Dokumen & Kepatuhan):** Proses tanda tangan memo internal dan PO wajib terekam dalam audit trail digital yang memenuhi standar tata kelola internal PT Dua Kelinci.

## 5. Ruang Lingkup Proyek & Batasan (*Scope & Boundaries*)

### 5.1 Dalam Lingkup (*In-Scope*)
1. Ingesti data penjualan, stok, dan budget dari QAD REST API dan file spreadsheet pendukung.
2. AI Insight Agent terjadwal harian/mingguan ke Microsoft Teams berbasis vLLM lokal.
3. Dashboard live web mandiri (Next.js) untuk Brand Manager, Head of Sales, dan Head of Region.
4. Modul operasional internal bertahap: e-Signature internal, Gudang (WMS ringan), HR (Cuti & Absensi), Rute Sales (PWA GPS), dan IoT Pabrik.
5. Manajemen observability, log, metrik, alert kegagalan, dan dokumentasi operasional lengkap.

### 5.2 Di Luar Lingkup (*Out-of-Scope*)
1. Penggantian modul inti finansial dan manufaktur QAD ERP.
2. Integrasi sertifikasi tanda tangan pihak ketiga berbayar (PSrE berlisensi Kominfo) untuk fase awal (ditunda sesuai [DECISIONS.md](DECISIONS.md) ADR-004).
3. Penggajian penuh (*full payroll processing*) dan perhitungan PPh 21 pada modul HR.
4. Operasional di luar batas teritorial Indonesia (fokus mata uang IDR dan zona waktu WIB sesuai ADR-008).

## 6. Metrik Keberhasilan Bisnis (*Business Success Metrics*)

| Indikator Kinerja Bisnis | Target Kuantitatif | Metode Pengukuran |
|---|---|---|
| Kecepatan Ketersediaan Laporan | Turun ≥ 80% (dari 24 jam menjadi instan/harian pukul 07.00 WIB) | Waktu penyelesaian batch ETL dan pengiriman Teams |
| Konsistensi Data Penjualan | Deviasi angka dashboard vs rekonsiliasi QAD ≤ 0,5% | Audit rekonsiliasi mingguan tim finansial & IT |
| Adopsi Pengguna Manajerial | ≥ 80% manajer aktif mengakses dashboard minimal 3x/minggu | Telemetri log autentikasi pengguna |
| Ketepatan Kirim AI Insight | ≥ 95% pesan ringkasan terkirim sukses sebelum 07.15 WIB | Log dispatch agent dan webhook delivery rate |
| Efisiensi Siklus Persetujuan Internal | Waktu approval dokumen turun dari rata-rata 3 hari menjadi < 4 jam | Timestamp pelacakan status e-Signature |
| Respons Gangguan Mesin | Notifikasi downtime/anomali suhu diterima supervisor < 2 menit | Log event IoT broker ke dispatcher alert |
