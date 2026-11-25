# Kamus Data Terpadu

Versi 0.2 · 24 Nov 2026 · Sumber acuan: `../sales.csv`

## 1. Profil Riil Data `sales.csv`
- **1.891 baris transaksi**, periode **1 September 2026 s.d. 31 Oktober 2026** (929 baris Sep 2026, 962 baris Okt 2026).
- **52 outlet**, **26 salesman aktif** (terdapat 5 baris dengan nama salesman kosong `""`).
- **6 region kanonik** dan **13 cabang distribusi**.
- **13 SKU** terdaftar di bawah **8 brand**: Kacang Dua Kelinci, Sukro, Tos Tos, Roni, Tic Tac, Pilus, Deka, Usagi.

> [!IMPORTANT]
> **Catatan Anomali & Aturan Normalisasi Data:**
> 1. Ditemukan variasi nama region: `'Jabar'`, `'JAWA BARAT'`, `'JABODETABEK'`, dan `'JAWA TIMUR'`. ETL wajib menormalisasi huruf besar/kecil dan spasi via tabel `dim_region_alias`.
> 2. Ditemukan 1 transaksi retur: faktur `RTR900001` dengan `qty_carton = -2` dan `net_sales_idr = -528000`. Transaksi ini sah bertipe `RETURN` dan mengurangi omzet.
> 3. Ditemukan 3 pasang baris duplikat identik `(invoice_no, sku)`. ETL wajib menerapkan operasi upsert idempoten.
> 4. Ditemukan 5 baris dengan kolom `salesman` kosong `""`. ETL memetakan nilai kosong menjadi `'UNASSIGNED'`.

## 2. `fact_sales` (Tabel Fakta Penjualan)

| Kolom | Tipe Data | Keterangan |
|---|---|---|
| date | DATE | Tanggal transaksi faktur (zona waktu WIB) |
| invoice_no | VARCHAR(20) | Nomor faktur / invoice QAD |
| entity_code | VARCHAR(10) | Kode entitas domestik (default: `ID01`) |
| transaction_type | VARCHAR(10) | Tipe transaksi: `SALE` atau `RETURN` |
| region | VARCHAR(50) | Wilayah pemasaran (nama kanonik) |
| branch | VARCHAR(50) | Cabang pemasaran |
| outlet_id | VARCHAR(20) | ID unik outlet |
| outlet_name | VARCHAR(100) | Nama toko / outlet |
| outlet_type | VARCHAR(30) | Tipe outlet: Grosir, Minimarket, Toko Kelontong, Warung |
| salesman | VARCHAR(50) | Nama tenaga penjual (jika kosong: `UNASSIGNED`) |
| brand | VARCHAR(50) | Merek produk |
| sku | VARCHAR(80) | Nama lengkap varian SKU |
| qty_carton | INT | Kuantitas karton (bernilai negatif untuk retur) |
| price_per_carton_idr | NUMERIC(18,2) | Harga jual per karton |
| gross_sales_idr | NUMERIC(18,2) | Penjualan kotor = qty × harga |
| discount_idr | NUMERIC(18,2) | Nilai potongan harga / diskon |
| net_sales_idr | NUMERIC(18,2) | Penjualan bersih = gross − discount |

Kunci unik penjamin integritas: `(entity_code, invoice_no, sku)`.

## 3. `fact_stock` (mengikuti pola `sales.csv`)

File dummy: [`../stock.csv`](../stock.csv) — snapshot harian Sep 2026, per branch × SKU (5.070 baris), dibuat oleh [`../scripts/generate_dummy.ps1`](../scripts/generate_dummy.ps1) dari `sales.csv`.

Format CSV/API: satu baris per tanggal × gudang × SKU.

```csv
date,entity_code,region,branch,warehouse_id,warehouse_name,brand,sku,batch_no,expiry_date,qty_on_hand_carton,qty_in_transit_carton,qty_reserved_carton,min_stock_carton,cost_per_carton_idr,stock_value_idr
2026-09-01,ID01,Jabodetabek,Jakarta Barat,WH-JKB,Gudang Jakarta Barat,Kacang Dua Kelinci,Kacang Kulit 70g,B2608A,2027-02-28,420,60,35,150,150000,63000000
2026-09-01,ID01,Jabodetabek,Tangerang,WH-TNG,Gudang Tangerang,Sukro,Sukro Pedas 100g,B2608C,2027-01-31,95,0,10,120,140000,13300000
2026-09-01,ID01,Jawa Timur,Surabaya,WH-SBY,Gudang Surabaya,Tos Tos,Tos Tos Tortilla BBQ 140g,B2607F,2026-12-31,210,40,0,100,200000,42000000
```

| Kolom | Tipe | Keterangan |
|---|---|---|
| date | DATE | Tanggal snapshot (akhir hari) |
| warehouse_id / warehouse_name | VARCHAR | Gudang |
| batch_no, expiry_date | VARCHAR, DATE | Untuk FEFO & alert kedaluwarsa |
| qty_on_hand_carton | INT | Stok fisik |
| qty_in_transit_carton | INT | Dalam perjalanan |
| qty_reserved_carton | INT | Sudah dialokasikan ke order |
| min_stock_carton | INT | Ambang stok minimum |
| cost_per_carton_idr | NUMERIC | HPP per karton |
| stock_value_idr | NUMERIC | = on_hand × cost |

Kunci unik: `(entity_code, date, warehouse_id, sku, batch_no)`.

**Turunan:**
- `available = on_hand − reserved`
- `days_of_cover = available ÷ rata-rata qty terjual per hari (28 hari terakhir)`
- Stok kritis: `available < min_stock` atau `days_of_cover < 7`.

## 4. `fact_budget`

File dummy: [`../budget.csv`](../budget.csv) — Sep–Des 2026, per region × branch × brand (416 baris), ≈ realisasi Sep ± 5–15% dengan kenaikan 3%/bulan.

```csv
period_month,entity_code,region,branch,brand,sku,budget_qty_carton,budget_net_sales_idr
2026-09,ID01,Jabodetabek,Jakarta Barat,Kacang Dua Kelinci,,1200,220000000
```
`sku` kosong = budget level brand. Kunci unik: `(entity_code, period_month, branch, brand, sku)`.

## 5. Dimensi & Master
| Tabel | Kolom utama |
|---|---|
| dim_entity | entity_code, plant_name, address (Indonesia saja, IDR, WIB) |
| dim_region_alias | alias, region_canonical |
| dim_product | sku_code, sku_name, brand, pack_size, cartons_per_pallet |
| dim_outlet | outlet_id, outlet_name, outlet_type, branch, lat, lng |
| dim_salesman | salesman_id, name, branch, supervisor_id |
| dim_warehouse | warehouse_id, name, branch, entity_code |
| user_scope | user_id, role, scope_type, scope_value |

## 6. Aturan Validasi ETL
1. `gross = qty × price` (toleransi selisih $\le 1$ Rupiah).
2. `net = gross − discount`, `discount ≥ 0`.
3. Untuk transaksi faktur reguler: wajib memiliki `qty > 0`.
4. Untuk transaksi retur (nomor faktur berawalan `'RTR'`): diizinkan `qty < 0` dan `net < 0`, ditandai sebagai `transaction_type = 'RETURN'`.
5. Kolom `salesman` yang kosong otomatis diisi `'UNASSIGNED'` dan dicatat dalam metrik kualitas data.
6. Region wajib dinormalisasi melalui kamus alias; SKU dan outlet dipetakan ke tabel master dimensi.
7. Baris yang melanggar aturan di atas dipindahkan ke `staging.quarantine` dan dilaporkan ke alert kanal Teams IT.
