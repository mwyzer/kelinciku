import datetime
from typing import Dict, Any, List, Optional
from app.db.connection import get_db

def init_ops_tables():
    conn = get_db()
    cur = conn.cursor()
    # 1. Sales Visits & Geofence Check-In
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sales_visits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        salesman_email TEXT NOT NULL,
        salesman_name TEXT NOT NULL,
        outlet_id TEXT NOT NULL,
        outlet_name TEXT NOT NULL,
        outlet_address TEXT,
        latitude REAL,
        longitude REAL,
        distance_meter REAL,
        status TEXT NOT NULL, -- CHECKED_IN, COMPLETED, CANCELLED
        visit_purpose TEXT NOT NULL, -- ORDER_TAKING, MERCHANDISING, BILLING, PROSPECTING
        notes TEXT,
        order_amount_idr REAL DEFAULT 0,
        check_in_time TEXT NOT NULL,
        check_out_time TEXT
    );
    """)

    # 2. Stock Transfers antar gudang
    cur.execute("""
    CREATE TABLE IF NOT EXISTS stock_transfers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transfer_no TEXT UNIQUE NOT NULL,
        from_warehouse_id TEXT NOT NULL,
        to_warehouse_id TEXT NOT NULL,
        brand TEXT NOT NULL,
        sku TEXT NOT NULL,
        qty_carton INTEGER NOT NULL,
        requested_by TEXT NOT NULL,
        status TEXT NOT NULL, -- IN_TRANSIT, RECEIVED, CANCELLED
        driver_name TEXT,
        vehicle_no TEXT,
        departure_time TEXT NOT NULL,
        arrival_time TEXT,
        notes TEXT
    );
    """)

    # Seed demo sales visits if empty
    cur.execute("SELECT COUNT(*) as cnt FROM sales_visits")
    cnt = cur.fetchone()["cnt"]
    if cnt == 0:
        demo_visits = [
            ("budi.santoso@duakelinci.id", "Budi Santoso", "OUT-JKT-001", "Toko Sumber Rejeki Glodok", "Komp. Pertokoan Glodok Bl B/4, DKI Jakarta", -6.1432, 106.8156, 15.2, "COMPLETED", "ORDER_TAKING", "Toko repeat order Kacang Garing & Sukro 50 ctn.", 4250000, "2026-10-30 09:15:00 WIB", "2026-10-30 09:45:00 WIB"),
            ("budi.santoso@duakelinci.id", "Budi Santoso", "OUT-JKT-002", "Minimarket Barokah Melawai", "Jl Melawai Raya 12, Kebayoran Baru, Jakarta Selatan", -6.2435, 106.7981, 28.5, "COMPLETED", "MERCHANDISING", "Pemasangan display hanger baru untuk Deka Wafer.", 0, "2026-10-30 10:30:00 WIB", "2026-10-30 11:10:00 WIB"),
            ("eko.prasetyo@duakelinci.id", "Eko Prasetyo", "OUT-SBY-001", "Grosir Berkah Jaya Surabaya", "Jl. Pasar Besar No. 45, Surabaya", -7.2512, 112.7423, 8.4, "CHECKED_IN", "ORDER_TAKING", "Sedang menghitung sisa stok fisik toko bersama owner.", 0, "2026-10-31 08:30:00 WIB", None),
        ]
        cur.executemany("""
            INSERT INTO sales_visits (
                salesman_email, salesman_name, outlet_id, outlet_name, outlet_address,
                latitude, longitude, distance_meter, status, visit_purpose, notes,
                order_amount_idr, check_in_time, check_out_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, demo_visits)

    # Seed demo stock transfers if empty
    cur.execute("SELECT COUNT(*) as cnt FROM stock_transfers")
    cnt_tf = cur.fetchone()["cnt"]
    if cnt_tf == 0:
        demo_transfers = [
            ("TRF-202610-001", "WH-HO-PATI", "WH-DC-JKT", "Dua Kelinci", "Kacang Garing 200g", 300, "dedi.kurniawan@duakelinci.id", "RECEIVED", "Agus Setiawan", "B 9812 DKI", "2026-10-28 14:00:00 WIB", "2026-10-29 08:30:00 WIB", "Relokasi stok reguler dari Plant Pati ke DC Jakarta"),
            ("TRF-202610-002", "WH-HO-PATI", "WH-DC-SBY", "Sukro", "Sukro Original 100g", 250, "dedi.kurniawan@duakelinci.id", "IN_TRANSIT", "Bambang Supriadi", "L 8421 SBY", "2026-10-30 19:30:00 WIB", None, "Pasokan lonjakan permintaan event Jatim Fair"),
            ("TRF-202610-003", "WH-DC-BDG", "WH-DC-SMG", "Deka", "Deka Crepes Choco 80g", 150, "dedi.kurniawan@duakelinci.id", "IN_TRANSIT", "Danang Joko", "D 7611 BDG", "2026-10-31 06:15:00 WIB", None, "Pemerataan buffer stock area Jawa Tengah")
        ]
        cur.executemany("""
            INSERT INTO stock_transfers (
                transfer_no, from_warehouse_id, to_warehouse_id, brand, sku, qty_carton,
                requested_by, status, driver_name, vehicle_no, departure_time, arrival_time, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, demo_transfers)

    conn.commit()
    conn.close()

init_ops_tables()

# --- SALES VISITS METHODS ---
def list_sales_visits(salesman_email: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_db()
    cur = conn.cursor()
    if salesman_email and salesman_email != "ALL":
        cur.execute("SELECT * FROM sales_visits WHERE salesman_email = ? ORDER BY id DESC LIMIT 100", (salesman_email,))
    else:
        cur.execute("SELECT * FROM sales_visits ORDER BY id DESC LIMIT 100")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def create_sales_check_in(payload: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_db()
    cur = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB")

    cur.execute("""
        INSERT INTO sales_visits (
            salesman_email, salesman_name, outlet_id, outlet_name, outlet_address,
            latitude, longitude, distance_meter, status, visit_purpose, notes,
            order_amount_idr, check_in_time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'CHECKED_IN', ?, ?, ?, ?)
    """, (
        payload.get("salesman_email", "budi.santoso@duakelinci.id"),
        payload.get("salesman_name", "Budi Santoso"),
        payload.get("outlet_id", "OUT-JKT-001"),
        payload.get("outlet_name", "Toko Sumber Rejeki Glodok"),
        payload.get("outlet_address", "Jakarta"),
        float(payload.get("latitude", -6.1432)),
        float(payload.get("longitude", 106.8156)),
        float(payload.get("distance_meter", 12.5)),
        payload.get("visit_purpose", "ORDER_TAKING"),
        payload.get("notes", "Kunjungan rutin"),
        float(payload.get("order_amount_idr", 0)),
        now_str
    ))
    visit_id = cur.lastrowid
    conn.commit()
    conn.close()
    return {"success": True, "visit_id": visit_id, "status": "CHECKED_IN", "check_in_time": now_str}

def complete_sales_visit(visit_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_db()
    cur = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB")
    
    cur.execute("""
        UPDATE sales_visits
        SET status = 'COMPLETED',
            check_out_time = ?,
            notes = COALESCE(?, notes),
            order_amount_idr = COALESCE(?, order_amount_idr)
        WHERE id = ?
    """, (now_str, payload.get("notes"), payload.get("order_amount_idr"), visit_id))
    conn.commit()
    conn.close()
    return {"success": True, "visit_id": visit_id, "status": "COMPLETED", "check_out_time": now_str}

# --- STOCK TRANSFERS METHODS ---
def list_stock_transfers(status: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_db()
    cur = conn.cursor()
    if status and status != "ALL":
        cur.execute("SELECT * FROM stock_transfers WHERE status = ? ORDER BY id DESC LIMIT 100", (status,))
    else:
        cur.execute("SELECT * FROM stock_transfers ORDER BY id DESC LIMIT 100")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def create_stock_transfer(payload: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_db()
    cur = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB")
    import random
    transfer_no = f"TRF-{datetime.datetime.now().strftime('%Y%m')}-{random.randint(100, 999)}"

    from_wh = payload.get("from_warehouse_id", "WH-HO-PATI")
    to_wh = payload.get("to_warehouse_id", "WH-DC-JKT")
    sku = payload.get("sku", "Kacang Garing 200g")
    brand = payload.get("brand", "Dua Kelinci")
    qty = int(payload.get("qty_carton", 100))

    cur.execute("""
        INSERT INTO stock_transfers (
            transfer_no, from_warehouse_id, to_warehouse_id, brand, sku, qty_carton,
            requested_by, status, driver_name, vehicle_no, departure_time, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 'IN_TRANSIT', ?, ?, ?, ?)
    """, (
        transfer_no, from_wh, to_wh, brand, sku, qty,
        payload.get("requested_by", "dedi.kurniawan@duakelinci.id"),
        payload.get("driver_name", "Supir Logistik"),
        payload.get("vehicle_no", "B 1234 DK"),
        now_str,
        payload.get("notes", "Permintaan mutasi persediaan")
    ))
    conn.commit()
    conn.close()
    return {"success": True, "transfer_no": transfer_no, "status": "IN_TRANSIT", "departure_time": now_str}

def receive_stock_transfer(transfer_no: str) -> Dict[str, Any]:
    conn = get_db()
    cur = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB")
    
    cur.execute("SELECT * FROM stock_transfers WHERE transfer_no = ?", (transfer_no,))
    transfer = cur.fetchone()
    if not transfer:
        conn.close()
        return {"success": False, "message": "Surat Jalan Transfer tidak ditemukan."}

    cur.execute("""
        UPDATE stock_transfers
        SET status = 'RECEIVED',
            arrival_time = ?
        WHERE transfer_no = ?
    """, (now_str, transfer_no))

    # Mutasi stok di fact_stock (kurang di asal, tambah di tujuan jika record ada)
    cur.execute("""
        UPDATE fact_stock
        SET qty_on_hand_carton = qty_on_hand_carton - ?
        WHERE date = '2026-10-31' AND warehouse_id = ? AND sku = ?;
    """, (transfer["qty_carton"], transfer["from_warehouse_id"], transfer["sku"]))

    cur.execute("""
        UPDATE fact_stock
        SET qty_on_hand_carton = qty_on_hand_carton + ?
        WHERE date = '2026-10-31' AND warehouse_id = ? AND sku = ?;
    """, (transfer["qty_carton"], transfer["to_warehouse_id"], transfer["sku"]))

    conn.commit()
    conn.close()
    return {"success": True, "transfer_no": transfer_no, "status": "RECEIVED", "arrival_time": now_str}
