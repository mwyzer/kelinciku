# USER STORIES — Platform Digital Operasional Kacang Dua Kelinci

| Item | Nilai |
|---|---|
| Versi | 0.1 (Draft) |
| Tanggal | 24 Nov 2026 |
| Status | Menunggu review stakeholder |
| Acuan | [BRD.md](BRD.md), [PRD.md](PRD.md), [SRS.md](SRS.md) |

---

## 1. Daftar Epic

| ID Epic | Nama Epic | Deskripsi Ringkas |
|---|---|---|
| **EP-01** | Fondasi Data & Ingestion Pipeline | Ekstraksi, transformasi, validasi, dan isolasi data penjualan, stok, dan budget. |
| **EP-02** | Dashboard Live Web Mandiri | Portal visual interaktif berbasis peran dengan pengamanan Row-Level Security. |
| **EP-03** | AI Insight Agent & Microsoft Teams | Pengolahan KPI deterministik, narasi otomatis LLM on-premise, dan pengiriman Teams. |
| **EP-04** | Integrasi QAD API & Modul Gudang | Sinkronisasi data ERP langsung dan pengelolaan alur pergudangan FEFO. |
| **EP-05** | e-Signature Internal & Audit Dokumen | Pengunggahan, penandatanganan digital berbasis SSO, dan pencatatan audit trail. |
| **EP-06** | Modul HR (Cuti & Presensi) | Pengelolaan saldo cuti, approval atasan, serta presensi berbasis GPS dan foto. |
| **EP-07** | Modul Rute Sales Lapangan | Perencanaan kunjungan harian, validasi geofence outlet, dan operasional offline PWA. |
| **EP-08** | Monitoring IoT Pabrik | Penangkapan telemetri sensor mesin, alert batas toleransi, dan perhitungan OEE. |
| **EP-09** | Observability & Tata Kelola IT | Logging terpusat, pengawasan kesehatan layanan, dan penanganan insiden. |

---

## 2. Rincian User Stories

### EP-01: Fondasi Data & Ingestion Pipeline
- **US-01 (Import Data Penjualan CSV/QAD):** Sebagai Analis Data / Tim IT, saya ingin mengimpor data transaksi penjualan harian dari file CSV atau antarmuka API secara terjadwal, agar data warehouse selalu terisi dengan data transaksi terbaru. `[Prio: M | Fase: 0 | FR-DATA-01]`
- **US-02 (Validasi Aritmetika & Integritas):** Sebagai Administrator Data, saya ingin sistem memverifikasi bahwa `gross = qty * price` dan `net = gross - discount`, serta memastikan SKU terdaftar, agar laporan keuangan terbebas dari kesalahan entri data. `[Prio: M | Fase: 0 | FR-DATA-02]`
- **US-03 (Isolasi Baris Cacat ke Karantina):** Sebagai Analis Data, saya ingin baris transaksi yang tidak lolos validasi dipindahkan ke tabel karantina beserta catatan error-nya tanpa menghentikan pemrosesan baris valid lainnya, agar proses ETL tetap berjalan lancar dan perbaikan data dapat dilakukan terfokus. `[Prio: M | Fase: 0 | FR-DATA-02]`
- **US-04 (Normalisasi Alias Wilayah):** Sebagai Sistem Ingesti, saya ingin memetakan variasi penamaan wilayah (seperti `Jabar` dan `JAWA BARAT`) ke bentuk kanonik secara otomatis, agar laporan regional tidak terpecah menjadi beberapa kategori berbeda. `[Prio: M | Fase: 0 | FR-DATA-02]`
- **US-05 (Deduplikasi Transaksi Idempoten):** Sebagai Administrator Data, saya ingin proses pemuatan data bersifat idempoten berdasarkan kombinasi nomor invoice dan kode SKU, agar pengunggahan file ulang tidak menyebabkan duplikasi omzet. `[Prio: M | Fase: 0 | FR-DATA-03]`

### EP-02: Dashboard Live Web Mandiri
- **US-06 (Dasbor Kinerja Brand Manager):** Sebagai Brand Manager, saya ingin melihat rincian penjualan, pencapaian target budget, margin kotor, dan sebaran tipe outlet khusus untuk brand yang saya kelola, agar saya dapat mengevaluasi efektivitas produk di pasar. `[Prio: M | Fase: 1 | FR-DASH-01]`
- **US-07 (Dasbor Konsolidasi Head of Sales):** Sebagai Head of Sales, saya ingin melihat peringkat performa regional, cabang, dan tenaga penjual di seluruh Indonesia beserta tingkat diskon rata-rata, agar saya dapat mengambil tindakan perbaikan pada wilayah yang tertinggal target. `[Prio: M | Fase: 1 | FR-DASH-02]`
- **US-08 (Dasbor Operasional Head of Region):** Sebagai Head of Region, saya ingin memantau pencapaian cabang-cabang di wilayah otoritas saya, ketersediaan stok depo, dan status kunjungan sales, agar distribusi produk di wilayah saya tetap optimal. `[Prio: M | Fase: 1 | FR-DASH-03]`
- **US-09 (Filter Global & Penelusuran Detail):** Sebagai Pengguna Dashboard, saya ingin memfilter tampilan berdasarkan rentang tanggal, wilayah, cabang, brand, dan outlet, serta melakukan drill-down hingga level transaksi, agar saya dapat menganalisis anomali performa secara mendalam. `[Prio: M | Fase: 1 | FR-DASH-04]`
- **US-10 (Row-Level Security Sesuai Akun):** Sebagai Administrator Keamanan, saya ingin membatasi hak akses data dashboard secara otomatis berdasarkan identitas SSO pengguna, agar data cabang atau brand lain tidak bocor ke pihak yang tidak berwenang. `[Prio: M | Fase: 1 | FR-DASH-05]`
- **US-11 (Ekspor Ringkasan Data):** Sebagai Manajer Bisnis, saya ingin mengunduh tabel visual yang sedang saya analisis ke format Excel/CSV, agar saya dapat menyusun materi presentasi rapat evaluasi. `[Prio: S | Fase: 1 | FR-DASH-06]`

### EP-03: AI Insight Agent & Microsoft Teams
- **US-12 (Penerimaan Ringkasan Harian Teams):** Sebagai Manajer Regional/Brand, saya ingin menerima kartu ringkasan interaktif di Microsoft Teams setiap pukul 07.00 WIB, agar saya mengetahui pencapaian hari sebelumnya sebelum memulai jam kerja. `[Prio: M | Fase: 1 | FR-AGT-01]`
- **US-13 (Kalkulasi Metrik Deterministik Tanpa Halusinasi):** Sebagai Direktur Bisnis, saya ingin seluruh metrik persentase pencapaian dan nilai rupiah dihitung langsung oleh query database dan diverifikasi validator otomatis, agar narasi yang ditulis AI tidak mengandung angka fiktif. `[Prio: M | Fase: 1 | FR-AGT-02, FR-AGT-04]`
- **US-14 (Notifikasi Peringatan Stok Kritis):** Sebagai Kepala Depo Cabang, saya ingin menerima notifikasi otomatis ketika stok SKU tertentu berada di bawah batas minimum atau days of cover < 7 hari, agar proses permintaan suplai dapat segera dilakukan. `[Prio: M | Fase: 1 | FR-AGT-02]`
- **US-15 (Tanya-Jawab Data Alami):** Sebagai Eksekutif, saya ingin mengajukan pertanyaan bahasa alami sederhana di channel Teams terkait data penjualan dan mendapatkan jawaban terverifikasi, agar saya tidak perlu selalu membuka dashboard laptop saat bepergian. `[Prio: C | Fase: 2 | FR-AGT-07]`

### EP-04: Integrasi QAD API & Modul Gudang
- **US-16 (Sinkronisasi Inkremental QAD REST API):** Sebagai Sistem Integrator, saya ingin menarik data pesanan dan faktur dari API QAD berdasarkan penanda waktu terakhir modifikasi, agar beban pada sistem ERP QAD tetap terkontrol dan efisien. `[Prio: M | Fase: 2 | FR-DATA-04]`
- **US-17 (Penerimaan Barang dengan Barcode):** Sebagai Operator Gudang, saya ingin memindai barcode surat jalan dan mencatat nomor batch serta masa kedaluwarsa produk saat penerimaan, agar data stok fisik tercatat akurat di sistem. `[Prio: M | Fase: 2 | FR-WH-01]`
- **US-18 (Pengeluaran Barang Berdasarkan FEFO):** Sebagai Staf Pengiriman Gudang, saya ingin sistem merekomendasikan alokasi batch barang yang memiliki tanggal kedaluwarsa terdekat untuk dikeluarkan terlebih dahulu, agar risiko retur produk akibat rusak/kedaluwarsa diminimalkan. `[Prio: M | Fase: 2 | FR-WH-02]`
- **US-19 (Rekonsiliasi Stock Opname):** Sebagai Supervisor Gudang, saya ingin mencatat hasil penghitungan fisik periodik dan membuat pengajuan penyesuaian selisih stok ke atasan, agar transparansi persediaan tetap terjaga. `[Prio: M | Fase: 2 | FR-WH-03]`

### EP-05: e-Signature Internal & Audit Dokumen
- **US-20 (Pengunggahan & Penentuan Alur Tanda Tangan):** Sebagai Staf Administrasi, saya ingin mengunggah dokumen memo/PO berformat PDF dan menentukan daftar pihak penandatangan secara berurutan atau bersamaan, agar proses birokrasi persetujuan terdokumentasi rapi. `[Prio: M | Fase: 3 | FR-SIGN-01]`
- **US-21 (Penandatanganan Dokumen via SSO):** Sebagai Manajer Penandatangan, saya ingin membubuhkan persetujuan dan tanda tangan digital setelah melakukan verifikasi login SSO Entra ID, agar dokumen memiliki legalitas internal yang valid. `[Prio: M | Fase: 3 | FR-SIGN-02]`
- **US-22 (Verifikasi Keaslian Hash Dokumen):** Sebagai Auditor Internal, saya ingin memverifikasi kode hash SHA-256 dan riwayat jejak audit (waktu, nama, alamat IP) pada dokumen final, agar saya dapat memastikan dokumen tidak mengalami manipulasi pasca-persetujuan. `[Prio: M | Fase: 3 | FR-SIGN-03]`

### EP-06: Modul HR (Cuti & Presensi)
- **US-23 (Pengajuan & Persetujuan Cuti Online):** Sebagai Karyawan, saya ingin mengajukan permohonan cuti tahunan dan melihat sisa saldo cuti saya secara transparan, serta atasan saya dapat menyetujuinya langsung lewat antarmuka web/Teams, agar proses izin kerja berjalan cepat. `[Prio: M | Fase: 3 | FR-HR-01, FR-HR-02]`
- **US-24 (Presensi Masuk/Pulang dengan Geofence & Foto):** Sebagai Karyawan Lapangan/Pabrik, saya ingin melakukan check-in dan check-out menggunakan kamera smartphone dan validasi radius koordinat lokasi kerja, agar catatan kehadiran saya terekam akurat tanpa kecurangan. `[Prio: M | Fase: 3 | FR-HR-03]`

### EP-07: Modul Rute Sales Lapangan
- **US-25 (Daftar Kunjungan Rute Harian):** Sebagai Tenaga Penjual (Salesman), saya ingin melihat daftar outlet yang wajib saya kunjungi hari ini lengkap dengan titik peta dan riwayat pesanan sebelumnya, agar jadwal kerja harian saya terstruktur. `[Prio: M | Fase: 3 | FR-ROUTE-01]`
- **US-26 (Check-In Outlet & Pencatatan Order Offline):** Sebagai Salesman, saya ingin melakukan check-in GPS di lokasi toko dan mencatat pesanan barang meskipun koneksi internet di lokasi sedang terputus, agar pekerjaan di lapangan tidak terhambat sinyal. `[Prio: M | Fase: 3 | FR-ROUTE-02, FR-ROUTE-05]`

### EP-08: Monitoring IoT Pabrik
- **US-27 (Telemetri Kondisi Mesin Real-Time):** Sebagai Supervisor Pabrik, saya ingin melihat grafik suhu ruang sangrai, kelembapan, dan jumlah output kemasan secara real-time dari lini produksi, agar parameter kualitas produk selalu berada dalam standar. `[Prio: M | Fase: 4 | FR-IOT-01, FR-IOT-02]`
- **US-28 (Peringatan Mesin Macet / Anomali Suhu):** Sebagai Teknisi Pemeliharaan, saya ingin menerima notifikasi instan di Teams apabila ada mesin pengemas yang berhenti beroperasi > 2 menit atau sensor suhu mendeteksi lonjakan berlebih, agar perbaikan segera dilakukan. `[Prio: M | Fase: 4 | FR-IOT-03]`
- **US-29 (Perhitungan Nilai OEE per Shift):** Sebagai Manajer Operasional Pabrik, saya ingin melihat laporan Overall Equipment Effectiveness (Availability, Performance, Quality) setiap pergantian shift kerja, agar efisiensi lini manufaktur dapat diukur objektif. `[Prio: S | Fase: 4 | FR-IOT-04]`

### EP-09: Observability & Tata Kelola IT
- **US-30 (Peringatan Kegagalan Job Terjadwal):** Sebagai Tim IT Operasional, saya ingin menerima notifikasi otomatis di kanal Teams IT jika job ETL, sinkronisasi QAD, atau pengiriman insight mengalami kegagalan dalam waktu < 5 menit, agar tim dapat segera melakukan investigasi dan pemulihan data. `[Prio: M | Fase: 0 | FR-OPS-02]`
- **US-31 (Audit Log Perubahan Sensitif):** Sebagai Compliance Officer, saya ingin seluruh aksi persetujuan e-signature, penyesuaian stok opname, dan pengubahan hak akses pengguna dicatat dalam audit log yang tidak dapat diubah (append-only), agar memenuhi standar tata kelola kepatuhan internal. `[Prio: M | Fase: 0 | FR-OPS-04]`
