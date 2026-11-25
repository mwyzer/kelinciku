# ACCEPTANCE CRITERIA — Platform Digital Operasional Kacang

| Item | Nilai |
|---|---|
| Versi | 0.1 (Draft) |
| Tanggal | 24 Nov 2026 |
| Status | Menunggu review stakeholder |
| Acuan | [USER-STORIES.md](USER-STORIES.md), [SRS.md](SRS.md), [DECISIONS.md](DECISIONS.md) |

---

## 1. Definisi Selesai Global (*Definition of Done / DoD*)
Setiap fitur atau modul dalam platform ini dianggap selesai dan siap rilis ke lingkungan staging/produksi apabila memenuhi kriteria berikut:
1. Kode sumber telah lolos linting otomatis dan pemeriksaan format tanpa error.
2. Unit test dan integration test untuk modul terkait lulus 100% dengan cakupan baris logika bisnis/kalkulasi ≥ 80%.
3. Skema database dikelola melalui skrip migrasi Alembic yang bersifat *backward-compatible*.
4. Endpoint API menyediakan dokumentasi OpenAPI/Swagger dan merespons format error standar RFC 7807.
5. Log terstruktur format JSON dicatat untuk setiap event penting dan tidak mengandung data rahasia/token.
6. Kriteria penerimaan spesifik (Given / When / Then) pada dokumen ini terverifikasi melalui automated test atau pengujian manual bertanda tangan tim QA/analis.

---

## 2. Kriteria Penerimaan per Modul & Fase

### 2.1 Ingesti Data & Kualitas Pipeline (Fase 0)

#### AC-DATA-01: Validasi Aritmetika Faktur Penjualan
- **Given:** File data penjualan (CSV atau payload API) berisi kolom `qty_carton`, `price_per_carton_idr`, `gross_sales_idr`, `discount_idr`, dan `net_sales_idr`.
- **When:** Sistem ETL memproses setiap baris transaksi.
- **Then:** Baris dinyatakan valid jika `abs((qty_carton * price_per_carton_idr) - gross_sales_idr) <= 1` dan `abs((gross_sales_idr - discount_idr) - net_sales_idr) <= 1`.
- **And:** Baris yang memenuhi syarat langsung dimuat ke tabel `dwh.fact_sales`.

#### AC-DATA-02: Penanganan Transaksi Retur Barang
- **Given:** Terdapat baris transaksi dengan nomor faktur berawalan `RTR` (seperti `RTR900001` pada data riil) dengan `qty_carton < 0` dan `net_sales_idr < 0`.
- **When:** Sistem memvalidasi transaksi tersebut.
- **Then:** Sistem tidak mengkarantina transaksi, melainkan menandainya sebagai `transaction_type = 'RETURN'` dan mencatatnya sebagai pengurang total penjualan bersih di data warehouse.

#### AC-DATA-03: Penanganan Nilai Salesman Kosong
- **Given:** Baris transaksi memiliki kolom `salesman` bernilai string kosong `""`.
- **When:** Pipeline ETL memproses baris tersebut.
- **Then:** Sistem mengganti nilai kosong menjadi `'UNASSIGNED'`, tetap menyimpan transaksi ke data warehouse, dan mencatat peringatan kualitas data pada ringkasan eksekusi batch.

#### AC-DATA-04: Normalisasi Nama Wilayah dan Huruf Besar/Kecil
- **Given:** Data input mencantumkan nama region seperti `'Jabar'`, `'JAWA BARAT'`, `'JABODETABEK'`, atau `'JAWA TIMUR'`.
- **When:** Tahap transformasi data dijalankan.
- **Then:** Sistem melakukan pembersihan spasi dan pemetaan melalui tabel `dwh.dim_region_alias` sehingga menghasilkan nama resmi kanonik (`'Jawa Barat'`, `'Jabodetabek'`, `'Jawa Timur'`).

#### AC-DATA-05: Penanganan Duplikasi Idempoten
- **Given:** File input mengandung 2 atau lebih baris dengan pasangan `(invoice_no, sku)` yang identik.
- **When:** Ingesti dijalankan berulang atau terdapat data duplikat dalam satu batch.
- **Then:** Sistem menerapkan operasi *upsert* berbasis kunci unik `(entity_code, invoice_no, sku)`, sehingga tidak terjadi penggandaan nilai pada tabel agregat.

#### AC-DATA-06: Isolasi Baris Cacat ke Karantina & Peringatan Otomatis
- **Given:** Terdapat baris data yang memiliki tanggal tidak valid, SKU tidak terdaftar di master, atau selisih nominal > 1 Rupiah.
- **When:** Validasi dijalankan.
- **Then:** Baris cacat dipindahkan ke `staging.quarantine` disertai alasan penolakan dan nomor baris sumber.
- **And:** Jika jumlah baris cacat dalam satu batch > 10%, proses ingest dibatalkan dan sistem mengirimkan alert prioritas tinggi ke kanal Teams IT.

---

### 2.2 Dashboard Live Web Mandiri & RLS (Fase 1)

#### AC-DASH-01: Isolasi Hak Akses Data Regional (Row-Level Security)
- **Given:** Pengguna dengan peran `head_region` untuk wilayah `'Jawa Barat'` login ke sistem melalui SSO.
- **When:** Pengguna membuka halaman ringkasan penjualan atau stok cabang.
- **Then:** Sistem hanya menampilkan data transaksi yang memiliki `region = 'Jawa Barat'`.
- **And:** Upaya memanipulasi parameter query API untuk membaca data wilayah lain menghasilkan respons HTTP 403 Forbidden.

#### AC-DASH-02: Isolasi Hak Akses Brand Manager
- **Given:** Pengguna dengan peran `brand_manager` untuk brand `'Sukro'` mengakses dashboard.
- **When:** Halaman dasbor dimuat.
- **Then:** Ringkasan pendapatan, persentase pencapaian budget, dan pergerakan stok hanya menampilkan produk-produk yang terdaftar di bawah brand `'Sukro'`.

#### AC-DASH-03: Batas Kecepatan Pemuatan Halaman
- **Given:** Database data warehouse terisi riwayat data transaksi selama 3 bulan penuh.
- **When:** Pengguna membuka dasbor dengan filter gabungan (wilayah, cabang, rentang tanggal).
- **Then:** Data visual dan grafik ECharts harus tampil sempurna dalam waktu kurang dari 3,0 detik pada persentil ke-95 (p95).

#### AC-DASH-04: Indikator Waktu Pembaruan Terakhir
- **Given:** Halaman dashboard telah selesai memuat data.
- **When:** Pengguna mengamati bilah status atas.
- **Then:** Sistem menampilkan label stempel waktu pembaruan data terakhir dalam format WIB (misal: "Data diperbarui: 24 Nov 2026, 06:30 WIB").

---

### 2.3 AI Insight Agent & Integrasi Teams (Fase 1)

#### AC-AGT-01: Jadwal Eksekusi Harian dan Mingguan
- **Given:** Waktu server menunjukkan pukul 07.00 WIB pada hari kerja.
- **When:** Scheduler memicu service Insight Agent.
- **Then:** Sistem menghitung KPI masing-masing manajer berdasarkan `user_scope` dan mengirimkan Adaptive Card ke chat personal/channel Teams yang terdaftar sebelum pukul 07.15 WIB.

#### AC-AGT-02: Penolakan Halusinasi AI (Numeric Verification Gate)
- **Given:** Layanan vLLM menghasilkan draft narasi ringkasan dalam Bahasa Indonesia.
- **When:** Validator numerik membandingkan angka nominal dan persentase yang tertulis di teks narasi terhadap JSON KPI acuan database.
- **Then:** Jika ditemukan satu saja angka yang berbeda atau tidak tercantum di JSON KPI, sistem menolak teks narasi AI tersebut dan secara otomatis beralih (*fallback*) mengirimkan pesan berbasis template baku deterministik.

#### AC-AGT-03: Mekanisme Retry Pengiriman Pesan
- **Given:** Sambungan jaringan ke Microsoft Teams Graph API mengalami gangguan sementara (HTTP 500/503 atau timeout).
- **When:** Pengiriman pesan gagal pada percobaan pertama.
- **Then:** Sistem melakukan percobaan ulang sebanyak maksimal 3 kali dengan jeda eksponensial (misal: 10 detik, 30 detik, 60 detik) dan mencatat status akhir di `app.agent_dispatch_log`.

---

### 2.4 Modul Operasional Internal (Fase 2, 3, 4)

#### AC-SIGN-01: Integritas Hash dan Jejak Audit Dokumen (Fase 3)
- **Given:** Dokumen PDF telah ditandatangani oleh seluruh penandatangan yang ditentukan.
- **When:** Dokumen final dibuat oleh sistem.
- **Then:** Dokumen disematkan sertifikat penyelesaian yang memuat nilai hash SHA-256 asli, nama akun SSO penandatangan, stempel waktu WIB, dan IP address.
- **And:** Dokumen disimpan pada object storage MinIO dengan status read-only.

#### AC-WH-01: Rekomendasi Alokasi Barang FEFO (Fase 2)
- **Given:** Terdapat beberapa batch stok untuk satu SKU yang sama dengan tanggal kedaluwarsa berbeda di gudang cabang.
- **When:** Staf gudang membuat Delivery Order (DO) pengeluaran barang.
- **Then:** Sistem secara otomatis merekomendasikan batch yang memiliki tanggal kedaluwarsa paling awal (*First Expired, First Out*).

#### AC-HR-01: Presensi Berbasis Validasi Geofence (Fase 3)
- **Given:** Karyawan melakukan absensi check-in melalui aplikasi PWA.
- **When:** Koordinat GPS perangkat berada di luar radius 100 meter dari titik koordinat kantor cabang/pabrik terdaftar.
- **Then:** Sistem menolak proses check-in dan menampilkan pesan peringatan jarak lokasi kerja.

#### AC-ROUTE-01: Sinkronisasi Data Kunjungan Offline (Fase 3)
- **Given:** Salesman melakukan input catatan toko dan data pesanan saat perangkat tidak memiliki koneksi internet.
- **When:** Aplikasi PWA kembali mendeteksi sinyal internet aktif.
- **Then:** Antrean transaksi lokal (IndexedDB) disinkronkan otomatis ke server dengan header `Idempotency-Key` tanpa menimbulkan data dobel.

#### AC-IOT-01: Respons Cepat Deteksi Mesin Offline (Fase 4)
- **Given:** Mesin produksi di pabrik terputus komunikasinya atau broker MQTT menerima sinyal Last Will and Testament (LWT).
- **When:** Tidak ada data telemetri yang diterima selama lebih dari 120 detik berturut-turut.
- **Then:** Sistem menandai status mesin sebagai `OFFLINE` dan menerbitkan pesan alert prioritas tinggi ke kanal Teams tim pemeliharaan pabrik dalam waktu < 2 menit.
