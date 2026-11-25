import datetime
import random
import uuid
from typing import Dict, Any, List, Optional
from app.db.connection import get_db

def init_enhanced_wms_tables():
    conn = get_db()
    cur = conn.cursor()

    # 1. Tabel Pergerakan Transaksi Inventory (Inbound, Outbound, Transfer, Adjustment)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS wms_inventory_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_no TEXT UNIQUE NOT NULL,
        transaction_type TEXT NOT NULL, -- INBOUND, OUTBOUND, TRANSFER, ADJUSTMENT
        warehouse_id TEXT NOT NULL,
        destination_warehouse_id TEXT,
        sku_id TEXT NOT NULL,
        sku_name TEXT NOT NULL,
        brand TEXT NOT NULL,
        batch_no TEXT NOT NULL,
        expiry_date TEXT NOT NULL,
        barcode_scanned TEXT,
        qty_carton INTEGER NOT NULL,
        reference_doc_no TEXT, -- PO / SJ / DO / Faktur
        operator_email TEXT NOT NULL,
        created_at TEXT NOT NULL,
        qad_sync_status TEXT DEFAULT 'PENDING', -- PENDING, SYNCED, FAILED
        qad_sync_time TEXT,
        qad_voucher_no TEXT
    );
    """)

    # 2. Tabel Sesi Stock Opname
    cur.execute("""
    CREATE TABLE IF NOT EXISTS wms_stock_opname_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_no TEXT UNIQUE NOT NULL,
        warehouse_id TEXT NOT NULL,
        scheduled_date TEXT NOT NULL,
        status TEXT DEFAULT 'OPEN', -- OPEN, IN_PROGRESS, COMPLETED, CANCELLED
        notes TEXT,
        created_by TEXT NOT NULL,
        created_at TEXT NOT NULL,
        completed_at TEXT
    );
    """)

    # 3. Tabel Detail Item Opname
    cur.execute("""
    CREATE TABLE IF NOT EXISTS wms_stock_opname_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        sku_id TEXT NOT NULL,
        sku_name TEXT NOT NULL,
        brand TEXT NOT NULL,
        batch_no TEXT NOT NULL,
        system_qty_carton INTEGER NOT NULL,
        physical_qty_carton INTEGER DEFAULT 0,
        variance_carton INTEGER DEFAULT 0,
        scanned_barcode TEXT,
        counted_by TEXT,
        verified_at TEXT,
        FOREIGN KEY(session_id) REFERENCES wms_stock_opname_sessions(id)
    );
    """)

    # Seed data transaksi demo jika kosong
    cur.execute("SELECT COUNT(*) as cnt FROM wms_inventory_transactions")
    if cur.fetchone()["cnt"] == 0:
        demo_txs = [
            ("WMS-IN-202610-001", "INBOUND", "WH-HO-PATI", None, "SKU-KCG-001", "Kacang Garing 200g", "Dua Kelinci", "BATCH-DK-20261015-A", "2027-10-15", "8992741001234", 500, "PO-PABRIK-0891", "dedi.kurniawan@duakelinci.id", "2026-10-25 10:00:00 WIB", "SYNCED", "2026-10-25 10:15:00 WIB", "QAD-IN-7781"),
            ("WMS-OUT-202610-002", "OUTBOUND", "WH-DC-BDG", None, "SKU-SKR-001", "Sukro Original 100g", "Sukro", "BATCH-SK-20260901-B", "2027-03-01", "8992741002345", 80, "DO-OUT-9912", "agus.wh.bdg@duakelinci.id", "2026-10-28 14:30:00 WIB", "SYNCED", "2026-10-28 14:45:00 WIB", "QAD-OUT-8812"),
            ("WMS-TRF-202610-003", "TRANSFER", "WH-HO-PATI", "WH-DC-JKT", "SKU-DKA-001", "Deka Crepes Choco 80g", "Deka", "BATCH-DKA-20261010-C", "2027-04-10", "8992741003456", 200, "SJ-TRF-0012", "dedi.kurniawan@duakelinci.id", "2026-10-30 08:00:00 WIB", "PENDING", None, None),
        ]
        cur.executemany("""
            INSERT INTO wms_inventory_transactions (
                transaction_no, transaction_type, warehouse_id, destination_warehouse_id,
                sku_id, sku_name, brand, batch_no, expiry_date, barcode_scanned,
                qty_carton, reference_doc_no, operator_email, created_at,
                qad_sync_status, qad_sync_time, qad_voucher_no
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, demo_txs)

    # Seed sesi opname demo jika kosong
    cur.execute("SELECT COUNT(*) as cnt FROM wms_stock_opname_sessions")
    if cur.fetchone()["cnt"] == 0:
        cur.execute("""
            INSERT INTO wms_stock_opname_sessions (
                session_no, warehouse_id, scheduled_date, status, notes, created_by, created_at
            ) VALUES ('OPN-202610-01', 'WH-DC-BDG', '2026-10-31', 'IN_PROGRESS', 'Stock Opname Siklus Akhir Bulan Oktober 2026', 'agus.wh.bdg@duakelinci.id', '2026-10-31 07:00:00 WIB')
        """)
        cur.execute("SELECT id FROM wms_stock_opname_sessions WHERE session_no = 'OPN-202610-01'")
        session_id = cur.fetchone()["id"]
        demo_opname_items = [
            (session_id, "SKU-KCG-001", "Kacang Garing 200g", "Dua Kelinci", "BATCH-DK-20261015-A", 150, 150, 0, "8992741001234", "surya.picker@duakelinci.id", "2026-10-31 08:15:00 WIB"),
            (session_id, "SKU-SKR-001", "Sukro Original 100g", "Sukro", "BATCH-SK-20260901-B", 200, 198, -2, "8992741002345", "surya.picker@duakelinci.id", "2026-10-31 08:30:00 WIB"),
            (session_id, "SKU-DKA-001", "Deka Crepes Choco 80g", "Deka", "BATCH-DKA-20261010-C", 120, 122, 2, "8992741003456", "surya.picker@duakelinci.id", "2026-10-31 08:45:00 WIB"),
        ]
        cur.executemany("""
            INSERT INTO wms_stock_opname_items (
                session_id, sku_id, sku_name, brand, batch_no, system_qty_carton,
                physical_qty_carton, variance_carton, scanned_barcode, counted_by, verified_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, demo_opname_items)

    conn.commit()
    conn.close()

init_enhanced_wms_tables()

# --- WMS INBOUND & OUTBOUND ---
def record_inbound_goods(payload: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_db()
    cur = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB")
    tx_no = f"WMS-IN-{datetime.datetime.now().strftime('%Y%m')}-{random.randint(100, 999)}"

    wh_id = payload.get("warehouse_id", "WH-HO-PATI")
    sku_id = payload.get("sku_id", "SKU-KCG-001")
    sku_name = payload.get("sku_name", "Kacang Garing 200g")
    brand = payload.get("brand", "Dua Kelinci")
    batch_no = payload.get("batch_no", f"BATCH-DK-{datetime.datetime.now().strftime('%Y%m%d')}-A")
    expiry_date = payload.get("expiry_date", "2027-10-31")
    qty = int(payload.get("qty_carton", 100))
    barcode = payload.get("barcode_scanned", "8992741001234")
    po_no = payload.get("reference_doc_no", f"PO-{datetime.datetime.now().strftime('%Y%m')}-001")
    operator = payload.get("operator_email", "dedi.kurniawan@duakelinci.id")

    cur.execute("""
        INSERT INTO wms_inventory_transactions (
            transaction_no, transaction_type, warehouse_id, sku_id, sku_name,
            brand, batch_no, expiry_date, barcode_scanned, qty_carton,
            reference_doc_no, operator_email, created_at, qad_sync_status
        ) VALUES (?, 'INBOUND', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING')
    """, (tx_no, wh_id, sku_id, sku_name, brand, batch_no, expiry_date, barcode, qty, po_no, operator, now_str))

    # Perbarui stok di fact_stock jika ada
    cur.execute("""
        UPDATE fact_stock
        SET qty_on_hand_carton = qty_on_hand_carton + ?
        WHERE date = '2026-10-31' AND warehouse_id = ? AND sku = ?;
    """, (qty, wh_id, sku_name))

    conn.commit()
    conn.close()
    return {"success": True, "transaction_no": tx_no, "status": "INBOUND_RECORDED", "qad_sync_status": "PENDING"}

def record_outbound_goods(payload: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_db()
    cur = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB")
    tx_no = f"WMS-OUT-{datetime.datetime.now().strftime('%Y%m')}-{random.randint(100, 999)}"

    wh_id = payload.get("warehouse_id", "WH-DC-BDG")
    sku_id = payload.get("sku_id", "SKU-SKR-001")
    sku_name = payload.get("sku_name", "Sukro Original 100g")
    brand = payload.get("brand", "Sukro")
    batch_no = payload.get("batch_no", "BATCH-SK-20260901-B")
    expiry_date = payload.get("expiry_date", "2027-03-01")
    qty = int(payload.get("qty_carton", 50))
    do_no = payload.get("reference_doc_no", f"DO-{datetime.datetime.now().strftime('%Y%m')}-001")
    operator = payload.get("operator_email", "agus.wh.bdg@duakelinci.id")

    cur.execute("""
        INSERT INTO wms_inventory_transactions (
            transaction_no, transaction_type, warehouse_id, sku_id, sku_name,
            brand, batch_no, expiry_date, barcode_scanned, qty_carton,
            reference_doc_no, operator_email, created_at, qad_sync_status
        ) VALUES (?, 'OUTBOUND', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING')
    """, (tx_no, wh_id, sku_id, sku_name, brand, batch_no, expiry_date, payload.get("barcode_scanned", ""), qty, do_no, operator, now_str))

    # Kurangi stok
    cur.execute("""
        UPDATE fact_stock
        SET qty_on_hand_carton = MAX(0, qty_on_hand_carton - ?)
        WHERE date = '2026-10-31' AND warehouse_id = ? AND sku = ?;
    """, (qty, wh_id, sku_name))

    conn.commit()
    conn.close()
    return {"success": True, "transaction_no": tx_no, "status": "OUTBOUND_RECORDED", "qad_sync_status": "PENDING"}

def list_inventory_transactions(wh_id: Optional[str] = None, tx_type: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_db()
    cur = conn.cursor()
    query = "SELECT * FROM wms_inventory_transactions WHERE 1=1"
    params = []
    if wh_id and wh_id != "ALL":
        query += " AND warehouse_id = ?"
        params.append(wh_id)
    if tx_type and tx_type != "ALL":
        query += " AND transaction_type = ?"
        params.append(tx_type)
    query += " ORDER BY id DESC LIMIT 100"
    cur.execute(query, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

# --- STOCK OPNAME ---
def list_opname_sessions(wh_id: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_db()
    cur = conn.cursor()
    if wh_id and wh_id != "ALL":
        cur.execute("SELECT * FROM wms_stock_opname_sessions WHERE warehouse_id = ? ORDER BY id DESC", (wh_id,))
    else:
        cur.execute("SELECT * FROM wms_stock_opname_sessions ORDER BY id DESC")
    sessions = [dict(r) for r in cur.fetchall()]

    for s in sessions:
        cur.execute("SELECT * FROM wms_stock_opname_items WHERE session_id = ?", (s["id"],))
        s["items"] = [dict(r) for r in cur.fetchall()]

    conn.close()
    return sessions

def create_opname_session(payload: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_db()
    cur = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB")
    session_no = f"OPN-{datetime.datetime.now().strftime('%Y%m')}-{random.randint(10, 99)}"
    wh_id = payload.get("warehouse_id", "WH-DC-BDG")
    notes = payload.get("notes", "Siklus Opname Fisik")
    created_by = payload.get("created_by", "agus.wh.bdg@duakelinci.id")

    cur.execute("""
        INSERT INTO wms_stock_opname_sessions (session_no, warehouse_id, scheduled_date, status, notes, created_by, created_at)
        VALUES (?, ?, ?, 'IN_PROGRESS', ?, ?, ?)
    """, (session_no, wh_id, datetime.date.today().isoformat(), notes, created_by, now_str))
    cur.execute("SELECT id FROM wms_stock_opname_sessions WHERE session_no = ?", (session_no,))
    session_id = cur.fetchone()["id"]

    # Ambil snapshot stok gudang untuk opname
    cur.execute("""
        SELECT sku, brand, batch_no, qty_on_hand_carton
        FROM fact_stock
        WHERE date = '2026-10-31' AND warehouse_id = ?
        LIMIT 10
    """, (wh_id,))
    stocks = cur.fetchall()

    for s in stocks:
        cur.execute("""
            INSERT INTO wms_stock_opname_items (
                session_id, sku_id, sku_name, brand, batch_no, system_qty_carton, physical_qty_carton, variance_carton
            ) VALUES (?, 'SKU-GEN', ?, ?, ?, ?, ?, 0)
        """, (session_id, s["sku"], s["brand"], s["batch_no"], s["qty_on_hand_carton"], s["qty_on_hand_carton"]))

    conn.commit()
    conn.close()
    return {"success": True, "session_no": session_no, "session_id": session_id}

def update_opname_item_count(item_id: int, physical_qty: int, barcode: Optional[str], counter_email: str) -> Dict[str, Any]:
    conn = get_db()
    cur = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB")

    cur.execute("SELECT system_qty_carton FROM wms_stock_opname_items WHERE id = ?", (item_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return {"success": False, "message": "Item opname tidak ditemukan"}

    sys_qty = row["system_qty_carton"]
    variance = physical_qty - sys_qty

    cur.execute("""
        UPDATE wms_stock_opname_items
        SET physical_qty_carton = ?,
            variance_carton = ?,
            scanned_barcode = COALESCE(?, scanned_barcode),
            counted_by = ?,
            verified_at = ?
        WHERE id = ?
    """, (physical_qty, variance, barcode, counter_email, now_str, item_id))

    conn.commit()
    conn.close()
    return {"success": True, "variance_carton": variance, "verified_at": now_str}

# --- BARCODE LOOKUP ---
def lookup_barcode(barcode: str) -> Dict[str, Any]:
    """
    Simulasi pemindaian barcode EAN-13 / GS1-128
    """
    catalog = {
        "8992741001234": {"sku_id": "SKU-KCG-001", "sku_name": "Kacang Garing 200g", "brand": "Dua Kelinci", "category": "Kacang Kulit", "pack_size": "24 pack/ctn", "shelf_life_days": 365},
        "8992741002345": {"sku_id": "SKU-SKR-001", "sku_name": "Sukro Original 100g", "brand": "Sukro", "category": "Kacang Salut", "pack_size": "30 pack/ctn", "shelf_life_days": 300},
        "8992741003456": {"sku_id": "SKU-DKA-001", "sku_name": "Deka Crepes Choco 80g", "brand": "Deka", "category": "Wafer Roll", "pack_size": "24 box/ctn", "shelf_life_days": 365},
        "8992741004567": {"sku_id": "SKU-SKR-002", "sku_name": "Sukro Pedas 100g", "brand": "Sukro", "category": "Kacang Salut", "pack_size": "30 pack/ctn", "shelf_life_days": 300},
        "8992741005678": {"sku_id": "SKU-TIC-001", "sku_name": "TicTac Sapi Panggang 90g", "brand": "TicTac", "category": "Pillows", "pack_size": "40 pack/ctn", "shelf_life_days": 270}
    }
    match = catalog.get(barcode.strip())
    if match:
        return {"success": True, "barcode": barcode, "found": True, "product": match}
    return {
        "success": True,
        "barcode": barcode,
        "found": True,
        "product": {
            "sku_id": f"SKU-{barcode[-4:]}",
            "sku_name": f"Produk Scan Barcode {barcode[-4:]}",
            "brand": "Dua Kelinci",
            "category": "Snack",
            "pack_size": "24 pcs/ctn",
            "shelf_life_days": 365
        }
    }

# --- ERP QAD SINKRONISASI WORKER ---
def sync_pending_to_qad() -> Dict[str, Any]:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM wms_inventory_transactions WHERE qad_sync_status = 'PENDING'")
    pending = cur.fetchall()

    synced_count = 0
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB")

    for p in pending:
        voucher_no = f"QAD-VCR-{random.randint(10000, 99999)}"
        cur.execute("""
            UPDATE wms_inventory_transactions
            SET qad_sync_status = 'SYNCED',
                qad_sync_time = ?,
                qad_voucher_no = ?
            WHERE id = ?
        """, (now_str, voucher_no, p["id"]))
        synced_count += 1

    conn.commit()
    conn.close()
    return {
        "success": True,
        "synced_records": synced_count,
        "timestamp": now_str,
        "erp_target": "QAD Adaptive ERP 2026 On-Premise"
    }
