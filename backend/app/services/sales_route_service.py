import datetime
import math
import random
from typing import Dict, Any, List, Optional
from app.db.connection import get_db

def init_sales_route_tables():
    conn = get_db()
    cur = conn.cursor()

    # 1. Tabel Rencana Kunjungan Harian (Call Plan Schedule)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sales_call_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plan_date TEXT NOT NULL,
        salesman_email TEXT NOT NULL,
        salesman_name TEXT NOT NULL,
        outlet_id TEXT NOT NULL,
        outlet_name TEXT NOT NULL,
        outlet_address TEXT,
        target_lat REAL NOT NULL,
        target_lng REAL NOT NULL,
        sequence_order INTEGER NOT NULL,
        is_mandatory BOOLEAN DEFAULT TRUE,
        status TEXT DEFAULT 'PLANNED', -- PLANNED, CHECKED_IN, VISITED, SKIPPED
        skip_reason TEXT
    );
    """)

    # 2. Tabel Log Kunjungan & GPS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sales_visit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        call_plan_id INTEGER,
        salesman_email TEXT NOT NULL,
        salesman_name TEXT NOT NULL,
        outlet_id TEXT NOT NULL,
        outlet_name TEXT NOT NULL,
        check_in_lat REAL NOT NULL,
        check_in_lng REAL NOT NULL,
        geofence_distance_meters REAL NOT NULL,
        is_geofence_valid BOOLEAN NOT NULL,
        check_in_time TEXT NOT NULL,
        check_out_time TEXT,
        duration_minutes INTEGER DEFAULT 0,
        visit_purpose TEXT NOT NULL, -- ORDER_TAKING, MERCHANDISING, BILLING, PROSPECTING
        order_created BOOLEAN DEFAULT FALSE,
        order_amount_idr REAL DEFAULT 0,
        order_carton_qty INTEGER DEFAULT 0,
        notes TEXT,
        photo_evidence_url TEXT,
        created_at TEXT NOT NULL
    );
    """)

    # Seed data call plan jika kosong
    cur.execute("SELECT COUNT(*) as cnt FROM sales_call_plans")
    if cur.fetchone()["cnt"] == 0:
        demo_call_plans = [
            ("2026-10-31", "budi.santoso@duakelinci.id", "Budi Santoso", "OUT-JKT-001", "Toko Sumber Rejeki Glodok", "Komp. Pertokoan Glodok Bl B/4, DKI Jakarta", -6.1432, 106.8156, 1, True, "VISITED", None),
            ("2026-10-31", "budi.santoso@duakelinci.id", "Budi Santoso", "OUT-JKT-002", "Minimarket Barokah Melawai", "Jl Melawai Raya 12, Kebayoran Baru, Jakarta Selatan", -6.2435, 106.7981, 2, True, "VISITED", None),
            ("2026-10-31", "budi.santoso@duakelinci.id", "Budi Santoso", "OUT-JKT-003", "Toko Manisan & Snack Pasar Baru", "Jl Pasar Baru No. 88, Sawah Besar, Jakarta Pusat", -6.1620, 106.8320, 3, True, "CHECKED_IN", None),
            ("2026-10-31", "budi.santoso@duakelinci.id", "Budi Santoso", "OUT-JKT-004", "Grosir Berkah Cempaka Putih", "Jl. Cempaka Putih Tengah 22, Jakarta Pusat", -6.1780, 106.8650, 4, True, "PLANNED", None),
            ("2026-10-31", "budi.santoso@duakelinci.id", "Budi Santoso", "OUT-JKT-005", "Toko Kelontong Sahabat Kelapa Gading", "Jl Boulevard Barat Raya LC 6, Jakarta Utara", -6.1520, 106.9020, 5, False, "PLANNED", None),
            ("2026-10-31", "eko.prasetyo@duakelinci.id", "Eko Prasetyo", "OUT-SBY-001", "Grosir Berkah Jaya Surabaya", "Jl. Pasar Besar No. 45, Surabaya", -7.2512, 112.7423, 1, True, "VISITED", None),
            ("2026-10-31", "eko.prasetyo@duakelinci.id", "Eko Prasetyo", "OUT-SBY-002", "Toko Snack Nusantara Darmo", "Jl Raya Darmo 102, Surabaya", -7.2890, 112.7380, 2, True, "PLANNED", None),
        ]
        cur.executemany("""
            INSERT INTO sales_call_plans (
                plan_date, salesman_email, salesman_name, outlet_id, outlet_name,
                outlet_address, target_lat, target_lng, sequence_order, is_mandatory, status, skip_reason
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, demo_call_plans)

    conn.commit()
    conn.close()

init_sales_route_tables()

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 1)

def get_daily_call_plan(salesman_email: str, plan_date: Optional[str] = None) -> Dict[str, Any]:
    conn = get_db()
    cur = conn.cursor()
    target_date = plan_date or "2026-10-31"

    cur.execute("""
        SELECT * FROM sales_call_plans
        WHERE (salesman_email = ? OR ? = 'ALL' OR ? = 'muhammad.wyzer@gmail.com') AND plan_date = ?
        ORDER BY sequence_order ASC
    """, (salesman_email, salesman_email, salesman_email, target_date))
    plans = [dict(r) for r in cur.fetchall()]

    if not plans:
        # Fallback to all plans on target date
        cur.execute("SELECT * FROM sales_call_plans WHERE plan_date = ? ORDER BY sequence_order ASC", (target_date,))
        plans = [dict(r) for r in cur.fetchall()]

    total_calls = len(plans)
    visited_calls = sum(1 for p in plans if p["status"] == "VISITED")
    active_checkin = next((p for p in plans if p["status"] == "CHECKED_IN"), None)

    cur.execute("""
        SELECT COUNT(*) as effective_calls, COALESCE(SUM(order_amount_idr), 0) as total_to_amount, COALESCE(SUM(order_carton_qty), 0) as total_to_cartons
        FROM sales_visit_logs
        WHERE (salesman_email = ? OR ? = 'ALL' OR ? = 'muhammad.wyzer@gmail.com') AND created_at LIKE ? AND order_created IS TRUE
    """, (salesman_email, salesman_email, salesman_email, f"{target_date}%"))
    metrics = dict(cur.fetchone())

    strike_rate = round((metrics["effective_calls"] / max(visited_calls, 1)) * 100.0, 1) if visited_calls > 0 else 0.0

    conn.close()
    return {
        "plan_date": target_date,
        "salesman_email": salesman_email,
        "total_targets": total_calls,
        "visited_count": visited_calls,
        "effective_calls": metrics["effective_calls"],
        "strike_rate_pct": strike_rate,
        "total_to_amount_idr": metrics["total_to_amount"],
        "total_to_cartons": metrics["total_to_cartons"],
        "active_checkin": active_checkin,
        "route_stops": plans
    }

def process_sales_check_in(payload: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_db()
    cur = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB")

    plan_id = payload.get("call_plan_id")
    salesman = payload.get("salesman_email", "budi.santoso@duakelinci.id")
    salesman_name = payload.get("salesman_name", "Budi Santoso")
    outlet_id = payload.get("outlet_id", "OUT-JKT-001")
    outlet_name = payload.get("outlet_name", "Toko Sumber Rejeki Glodok")
    user_lat = float(payload.get("latitude", -6.1432))
    user_lng = float(payload.get("longitude", 106.8156))

    cur.execute("SELECT target_lat, target_lng FROM sales_call_plans WHERE id = ?", (plan_id,))
    target = cur.fetchone()
    if target:
        dist_meter = calculate_haversine_distance(user_lat, user_lng, target["target_lat"], target["target_lng"])
    else:
        dist_meter = float(payload.get("distance_meter", 15.0))

    is_valid = dist_meter <= 50.0

    cur.execute("""
        INSERT INTO sales_visit_logs (
            call_plan_id, salesman_email, salesman_name, outlet_id, outlet_name,
            check_in_lat, check_in_lng, geofence_distance_meters, is_geofence_valid,
            check_in_time, visit_purpose, notes, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        plan_id, salesman, salesman_name, outlet_id, outlet_name,
        user_lat, user_lng, dist_meter, 1 if is_valid else 0,
        now_str, payload.get("visit_purpose", "ORDER_TAKING"),
        payload.get("notes", "Kunjungan outlet rutin"), now_str
    ))
    cur.execute("SELECT id FROM sales_visit_logs WHERE salesman_email = ? AND created_at = ?", (salesman, now_str))
    res_row = cur.fetchone()
    visit_id = res_row["id"] if res_row else random.randint(100, 999)

    if plan_id:
        cur.execute("UPDATE sales_call_plans SET status = 'CHECKED_IN' WHERE id = ?", (plan_id,))

    conn.commit()
    conn.close()
    return {
        "success": True,
        "visit_id": visit_id,
        "is_geofence_valid": is_valid,
        "distance_meters": dist_meter,
        "status": "CHECKED_IN",
        "check_in_time": now_str
    }

def process_sales_check_out(visit_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_db()
    cur = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB")

    order_amount = float(payload.get("order_amount_idr", 0))
    order_qty = int(payload.get("order_carton_qty", 0))
    order_created = order_amount > 0 or order_qty > 0
    duration = int(payload.get("duration_minutes", 25))

    cur.execute("""
        UPDATE sales_visit_logs
        SET check_out_time = ?,
            duration_minutes = ?,
            order_created = ?,
            order_amount_idr = ?,
            order_carton_qty = ?,
            notes = COALESCE(?, notes),
            photo_evidence_url = ?
        WHERE id = ?
    """, (now_str, duration, 1 if order_created else 0, order_amount, order_qty, payload.get("notes"), payload.get("photo_evidence_url"), visit_id))

    cur.execute("SELECT call_plan_id FROM sales_visit_logs WHERE id = ?", (visit_id,))
    v = cur.fetchone()
    if v and v["call_plan_id"]:
        cur.execute("UPDATE sales_call_plans SET status = 'VISITED' WHERE id = ?", (v["call_plan_id"],))

    conn.commit()
    conn.close()
    return {"success": True, "visit_id": visit_id, "status": "VISITED", "check_out_time": now_str}
