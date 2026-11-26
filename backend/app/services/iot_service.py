import datetime
import os
import random
import uuid
from typing import Dict, Any, List, Optional
from app.db.connection import get_db

class IoTNotFound(Exception):
    """Mesin / resource IoT tidak ditemukan (dipetakan ke HTTP 404)."""

def init_enhanced_iot_tables():
    conn = get_db()
    cur = conn.cursor()

    # 1. Master Mesin (PRD 11.3.A)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS iot_machines (
        machine_id TEXT PRIMARY KEY,
        machine_name TEXT NOT NULL,
        production_line TEXT NOT NULL,
        product_type TEXT NOT NULL,
        ideal_speed_ppm INTEGER NOT NULL,
        temperature_min REAL NOT NULL,
        temperature_max REAL NOT NULL,
        humidity_min REAL NOT NULL,
        humidity_max REAL NOT NULL,
        vibration_threshold REAL NOT NULL,
        machine_status TEXT DEFAULT 'RUNNING',
        is_active BOOLEAN DEFAULT TRUE,
        current_temp_celsius REAL,
        current_humidity_rh REAL,
        current_speed_ppm INTEGER,
        current_vibration_mms REAL,
        last_heartbeat TEXT
    );
    """)

    # Alter table if already exists from earlier run
    try:
        cur.execute("ALTER TABLE iot_machines ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE")
        cur.execute("ALTER TABLE iot_machines ADD COLUMN IF NOT EXISTS current_vibration_mms REAL DEFAULT 2.0")
        cur.execute("ALTER TABLE iot_machines ADD COLUMN IF NOT EXISTS product_type TEXT DEFAULT 'Snack'")
        cur.execute("ALTER TABLE iot_machines ADD COLUMN IF NOT EXISTS vibration_threshold REAL DEFAULT 4.5")
    except Exception:
        pass

    # 2. Master Perangkat Sensor (PRD 11.3.B)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS iot_devices (
        device_id TEXT PRIMARY KEY,
        machine_id TEXT NOT NULL,
        device_type TEXT NOT NULL, -- SENSOR, CONTROLLER, GATEWAY
        sensor_type TEXT NOT NULL, -- TEMPERATURE, HUMIDITY, COUNTER, VIBRATION, PLC_DI
        protocol TEXT NOT NULL, -- MODBUS_RTU, MODBUS_TCP, MQTT
        installation_location TEXT NOT NULL,
        unit TEXT NOT NULL,
        last_seen_at TEXT,
        connection_status TEXT DEFAULT 'ONLINE', -- ONLINE, OFFLINE
        FOREIGN KEY(machine_id) REFERENCES iot_machines(machine_id)
    );
    """)

    # 3. Telemetri Sensor Timeseries (PRD 11.3.C)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS iot_telemetry_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        machine_id TEXT NOT NULL,
        device_id TEXT,
        timestamp TEXT NOT NULL,
        temperature REAL NOT NULL,
        humidity REAL NOT NULL,
        output_counter INTEGER NOT NULL,
        vibration REAL NOT NULL,
        machine_status TEXT NOT NULL,
        quality_status TEXT DEFAULT 'GOOD',
        FOREIGN KEY(machine_id) REFERENCES iot_machines(machine_id)
    );
    """)

    # 4. Machine Events (PRD 11.3.D)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS iot_machine_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id TEXT UNIQUE NOT NULL,
        machine_id TEXT NOT NULL,
        event_type TEXT NOT NULL, -- STATUS_CHANGE, DOWNTIME, MAINTENANCE
        start_time TEXT NOT NULL,
        end_time TEXT,
        duration_seconds INTEGER DEFAULT 0,
        downtime_category TEXT, -- PLANNED, UNPLANNED, ELECTRICAL, MECHANICAL
        downtime_reason TEXT,
        operator_id TEXT,
        FOREIGN KEY(machine_id) REFERENCES iot_machines(machine_id)
    );
    """)

    # 5. Production Schedule (PRD 11.3.F)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS iot_production_schedules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        production_date TEXT NOT NULL,
        shift_no INTEGER NOT NULL, -- 1, 2, 3
        machine_id TEXT NOT NULL,
        planned_start TEXT NOT NULL,
        planned_end TEXT NOT NULL,
        planned_production_minutes INTEGER NOT NULL,
        planned_downtime_minutes INTEGER NOT NULL,
        target_output_carton INTEGER NOT NULL
    );
    """)

    # 6. Event Alert (PRD 11.3.G)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS iot_alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alert_id TEXT UNIQUE NOT NULL,
        machine_id TEXT NOT NULL,
        device_id TEXT,
        alert_type TEXT NOT NULL, -- OVERHEAT, UNDERHEAT, HIGH_VIBRATION, UNSCHEDULED_DOWNTIME, SENSOR_FAILURE, DEVICE_OFFLINE
        severity TEXT NOT NULL, -- WARNING, CRITICAL
        metric_value REAL NOT NULL,
        threshold_value REAL NOT NULL,
        alert_message TEXT NOT NULL,
        triggered_at TEXT NOT NULL,
        acknowledged_at TEXT,
        acknowledged_by TEXT,
        resolved_at TEXT,
        resolved_by TEXT,
        resolution_notes TEXT,
        is_notified_telegram BOOLEAN DEFAULT TRUE,
        FOREIGN KEY(machine_id) REFERENCES iot_machines(machine_id)
    );
    """)

    # 7. OEE Records Terinci (PRD 11.3.H)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS iot_oee_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        machine_id TEXT NOT NULL,
        production_line TEXT NOT NULL,
        shift_id INTEGER NOT NULL,
        production_date TEXT NOT NULL,
        planned_production_time_min INTEGER NOT NULL,
        operating_time_min INTEGER NOT NULL,
        downtime_minutes INTEGER NOT NULL,
        total_count INTEGER NOT NULL,
        good_count INTEGER NOT NULL,
        reject_count INTEGER NOT NULL,
        availability_percentage REAL NOT NULL,
        performance_percentage REAL NOT NULL,
        quality_percentage REAL NOT NULL,
        oee_percentage REAL NOT NULL
    );
    """)

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB")

    # Seed master machines jika kosong
    cur.execute("SELECT COUNT(*) as cnt FROM iot_machines")
    if cur.fetchone()["cnt"] == 0:
        demo_machines = [
            ("MCH-PATI-01", "Roaster Oven Kacang Garing A", "Line 1 - Kacang Garing", "Kacang Garing 200g", 120, 160.0, 185.0, 40.0, 60.0, 4.5, "RUNNING", True, 174.5, 48.2, 118, 2.1, now_str),
            ("MCH-PATI-02", "Deep Fryer Continuous Sukro B", "Line 2 - Sukro", "Sukro Original 100g", 150, 165.0, 190.0, 40.0, 55.0, 5.0, "RUNNING", True, 178.2, 51.0, 145, 2.8, now_str),
            ("MCH-PATI-03", "Wafer Baking Oven Deka C", "Line 3 - Deka", "Deka Crepes Choco 80g", 90, 150.0, 180.0, 45.0, 65.0, 4.0, "BREAKDOWN", True, 188.4, 62.5, 0, 5.8, now_str),
            ("MCH-PATI-04", "Pillow Extruder TicTac D", "Line 4 - TicTac", "TicTac Sapi Panggang 90g", 140, 140.0, 175.0, 40.0, 60.0, 4.5, "IDLE", True, 155.0, 45.0, 0, 1.2, now_str),
        ]
        cur.executemany("""
            INSERT INTO iot_machines (
                machine_id, machine_name, production_line, product_type, ideal_speed_ppm,
                temperature_min, temperature_max, humidity_min, humidity_max, vibration_threshold,
                machine_status, is_active, current_temp_celsius, current_humidity_rh,
                current_speed_ppm, current_vibration_mms, last_heartbeat
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, demo_machines)

    # Seed master sensor devices jika kosong
    cur.execute("SELECT COUNT(*) as cnt FROM iot_devices")
    if cur.fetchone()["cnt"] == 0:
        demo_devices = [
            ("DEV-TEMP-01", "MCH-PATI-01", "SENSOR", "TEMPERATURE", "MODBUS_RTU", "Chamber Roasting Zone 2", "°C", now_str, "ONLINE"),
            ("DEV-VIB-01", "MCH-PATI-01", "SENSOR", "VIBRATION", "MODBUS_RTU", "Main Gearbox Bearing", "mm/s", now_str, "ONLINE"),
            ("DEV-HUM-01", "MCH-PATI-01", "SENSOR", "HUMIDITY", "MODBUS_TCP", "Packaging Room Zone 1", "% RH", now_str, "ONLINE"),
            ("DEV-CNT-01", "MCH-PATI-01", "SENSOR", "COUNTER", "PLC_DI", "Outfeed Conveyor Line 1", "Pcs", now_str, "ONLINE"),
            ("DEV-TEMP-03", "MCH-PATI-03", "SENSOR", "TEMPERATURE", "MODBUS_RTU", "Wafer Oven Zone 3", "°C", now_str, "ONLINE"),
            ("DEV-GW-01", "MCH-PATI-01", "GATEWAY", "PLC_DI", "MQTT", "Main Panel Pati DC 1", "Health", now_str, "ONLINE"),
        ]
        cur.executemany("""
            INSERT INTO iot_devices (
                device_id, machine_id, device_type, sensor_type, protocol,
                installation_location, unit, last_seen_at, connection_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, demo_devices)

    # Seed alerts jika kosong
    cur.execute("SELECT COUNT(*) as cnt FROM iot_alerts")
    if cur.fetchone()["cnt"] == 0:
        demo_alerts = [
            ("ALT-202611-001", "MCH-PATI-03", "DEV-TEMP-03", "OVERHEAT", "CRITICAL", 188.4, 180.0, "Suhu Wafer Oven melebihi batas aman 180°C. Risiko gosong pada adonan wafer.", now_str, None, None, None, None, None, True),
            ("ALT-202611-002", "MCH-PATI-03", "DEV-TEMP-03", "HIGH_VIBRATION", "WARNING", 5.8, 4.0, "Getaran motor penggerak conveyor oven melebihi 4.0 mm/s.", now_str, now_str, "bambang.teknisi@duakelinci.id", None, None, "Sedang dilakukan inspeksi bearing motor.", True),
        ]
        cur.executemany("""
            INSERT INTO iot_alerts (
                alert_id, machine_id, device_id, alert_type, severity, metric_value, threshold_value,
                alert_message, triggered_at, acknowledged_at, acknowledged_by, resolved_at, resolved_by,
                resolution_notes, is_notified_telegram
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, demo_alerts)

    # Seed OEE records jika kosong
    cur.execute("SELECT COUNT(*) as cnt FROM iot_oee_records")
    if cur.fetchone()["cnt"] == 0:
        demo_oee = [
            ("MCH-PATI-01", "Line 1 - Kacang Garing", 1, "2026-10-31", 480, 455, 25, 53600, 52900, 700, 94.8, 98.0, 98.7, 91.7),
            ("MCH-PATI-02", "Line 2 - Sukro", 1, "2026-10-31", 480, 440, 40, 63800, 62900, 900, 91.7, 96.7, 98.6, 87.4),
            ("MCH-PATI-03", "Line 3 - Deka", 1, "2026-10-31", 480, 310, 170, 24800, 23300, 1500, 64.6, 88.9, 94.0, 54.0),
            ("MCH-PATI-04", "Line 4 - TicTac", 1, "2026-10-31", 480, 420, 60, 56700, 55800, 900, 87.5, 96.4, 98.4, 83.0),
        ]
        cur.executemany("""
            INSERT INTO iot_oee_records (
                machine_id, production_line, shift_id, production_date,
                planned_production_time_min, operating_time_min, downtime_minutes,
                total_count, good_count, reject_count,
                availability_percentage, performance_percentage, quality_percentage, oee_percentage
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, demo_oee)

    # 8. Production Counters (PRD 11.3 - iot_production_counters)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS iot_production_counters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        machine_id TEXT NOT NULL,
        shift_id INTEGER NOT NULL,
        product_id TEXT,
        total_count INTEGER NOT NULL DEFAULT 0,
        good_count INTEGER NOT NULL DEFAULT 0,
        reject_count INTEGER NOT NULL DEFAULT 0,
        recorded_at TEXT NOT NULL,
        FOREIGN KEY(machine_id) REFERENCES iot_machines(machine_id)
    );
    """)

    # Seed jadwal produksi demo (3 shift x 4 mesin) jika kosong
    cur.execute("SELECT COUNT(*) as cnt FROM iot_production_schedules")
    if cur.fetchone()["cnt"] == 0:
        rows = []
        for m_id in ("MCH-PATI-01", "MCH-PATI-02", "MCH-PATI-03", "MCH-PATI-04"):
            for shift_no, (s, e) in SHIFT_WINDOWS.items():
                rows.append(("2026-10-31", shift_no, m_id, s, e, 480, 30, 0))
        cur.executemany("""
            INSERT INTO iot_production_schedules (
                production_date, shift_no, machine_id, planned_start, planned_end,
                planned_production_minutes, planned_downtime_minutes, target_output_carton
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, rows)

    conn.commit()
    conn.close()

# --- KONSTANTA & HELPER ---

WIB = datetime.timezone(datetime.timedelta(hours=7))
TS_FMT = "%Y-%m-%d %H:%M:%S WIB"
# Shift kerja: 1 = 07:00-15:00, 2 = 15:00-23:00, 3 = 23:00-07:00
SHIFT_WINDOWS = {1: ("07:00", "15:00"), 2: ("15:00", "23:00"), 3: ("23:00", "07:00")}
DEVICE_OFFLINE_SECONDS = 300          # PRD: perangkat dianggap offline setelah 5 menit tanpa data
UNSCHEDULED_DOWNTIME_SECONDS = 300    # PRD: Unplanned Downtime > 5 menit
DOWN_STATUSES = ("BREAKDOWN", "IDLE")

def _now() -> datetime.datetime:
    return datetime.datetime.now(WIB)

def _now_str() -> str:
    return _now().strftime(TS_FMT)

def _parse_ts(value: Optional[str]) -> Optional[datetime.datetime]:
    if not value:
        return None
    try:
        return datetime.datetime.strptime(str(value).replace(" WIB", "").strip(), "%Y-%m-%d %H:%M:%S").replace(tzinfo=WIB)
    except ValueError:
        return None

def current_shift(ts: Optional[datetime.datetime] = None) -> Dict[str, Any]:
    """Mengembalikan nomor shift & tanggal produksi (shift 3 setelah tengah malam milik tanggal sebelumnya)."""
    ts = ts or _now()
    h = ts.hour
    if 7 <= h < 15:
        return {"shift_no": 1, "production_date": ts.strftime("%Y-%m-%d")}
    if 15 <= h < 23:
        return {"shift_no": 2, "production_date": ts.strftime("%Y-%m-%d")}
    prod_date = ts if h >= 23 else ts - datetime.timedelta(days=1)
    return {"shift_no": 3, "production_date": prod_date.strftime("%Y-%m-%d")}

def _send_alert_telegram(machine_name: str, alert_type: str, severity: str, message: str, ts: str) -> bool:
    """Dispatch alert ke Telegram teknisi/supervisor. Butuh env IOT_TELEGRAM_BOT_TOKEN & IOT_TELEGRAM_CHAT_ID."""
    token = os.getenv("IOT_TELEGRAM_BOT_TOKEN", "").strip()
    chat_ids = [c.strip() for c in os.getenv("IOT_TELEGRAM_CHAT_ID", "").split(",") if c.strip()]
    if not token or not chat_ids:
        return False
    from app.services import telegram_service
    icon = "🔴" if severity == "CRITICAL" else "🟠"
    text = (f"{icon} <b>ALERT IoT Pabrik — {alert_type}</b>\n"
            f"Mesin: {machine_name}\nSeverity: {severity}\nWaktu: {ts}\n\n{message}")
    sent = False
    for chat_id in chat_ids:
        try:
            res = telegram_service.send_telegram_message(token, chat_id, text)
            sent = sent or bool(res.get("success", res.get("ok", False)))
        except Exception as ex:
            print(f"[IoT] Gagal kirim Telegram ke {chat_id}: {ex}")
    return sent

def _raise_alert(cur, machine: Dict[str, Any], device_id: Optional[str], alert_type: str, severity: str,
                 metric_value: float, threshold_value: float, message: str) -> Optional[Dict[str, Any]]:
    """Membuat alert baru kecuali sudah ada alert sejenis yang belum resolved untuk mesin yang sama (anti-spam)."""
    cur.execute("""
        SELECT alert_id FROM iot_alerts
        WHERE machine_id = ? AND alert_type = ? AND resolved_at IS NULL
        LIMIT 1
    """, (machine["machine_id"], alert_type))
    if cur.fetchone():
        return None
    now_str = _now_str()
    alert_id = f"ALT-{_now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"
    notified = _send_alert_telegram(machine["machine_name"], alert_type, severity, message, now_str)
    cur.execute("""
        INSERT INTO iot_alerts (
            alert_id, machine_id, device_id, alert_type, severity, metric_value,
            threshold_value, alert_message, triggered_at, is_notified_telegram
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (alert_id, machine["machine_id"], device_id, alert_type, severity,
          float(metric_value), float(threshold_value), message, now_str, notified))
    return {"alert_id": alert_id, "alert_type": alert_type, "severity": severity,
            "message": message, "telegram_sent": notified}

def _to_float(v) -> Optional[float]:
    try:
        return None if v is None or v == "" else float(v)
    except (TypeError, ValueError):
        return None

def _exec_safe(conn, sql: str) -> bool:
    """Jalankan satu DDL/DML; kalau gagal (mis. kolom sudah ada) rollback agar transaksi Postgres tidak macet."""
    cur = conn.cursor()
    try:
        cur.execute(sql)
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False

def migrate_legacy_iot_schema():
    """
    Database lama (init-duakelinci.sql versi awal) memakai nama kolom non-PRD
    (min_temp_celsius, status, message, oee_pct, temperature_celsius, ...).
    Tambahkan kolom PRD, isi dari kolom lama, dan lepas NOT NULL kolom lama.
    Kolom lama tidak dihapus supaya data historis tetap aman.
    """
    conn = get_db()
    new_columns = {
        "iot_machines": [
            ("temperature_min", "REAL", "min_temp_celsius"),
            ("temperature_max", "REAL", "max_temp_celsius"),
            ("humidity_min", "REAL", "40.0"),
            ("humidity_max", "REAL", "max_humidity_rh"),
            ("machine_status", "TEXT", "status"),
        ],
        "iot_alerts": [
            ("alert_id", "TEXT", "'ALT-LEGACY-' || id"),
            ("device_id", "TEXT", None),
            ("alert_message", "TEXT", "message"),
            ("acknowledged_at", "TEXT", None),
            ("acknowledged_by", "TEXT", None),
            ("resolved_by", "TEXT", None),
            ("resolution_notes", "TEXT", None),
        ],
        "iot_oee_records": [
            ("production_line", "TEXT", "(SELECT m.production_line FROM iot_machines m WHERE m.machine_id = iot_oee_records.machine_id)"),
            ("shift_id", "INTEGER", "shift_no"),
            ("planned_production_time_min", "INTEGER", "480"),
            ("downtime_minutes", "INTEGER", "total_downtime_minutes"),
            ("operating_time_min", "INTEGER", "480 - COALESCE(total_downtime_minutes, 0)"),
            ("total_count", "INTEGER", "total_output_carton"),
            ("good_count", "INTEGER", "total_output_carton"),
            ("reject_count", "INTEGER", "0"),
            ("availability_percentage", "REAL", "availability_pct"),
            ("performance_percentage", "REAL", "performance_pct"),
            ("quality_percentage", "REAL", "quality_pct"),
            ("oee_percentage", "REAL", "oee_pct"),
        ],
        "iot_telemetry_logs": [
            ("device_id", "TEXT", None),
            ("temperature", "REAL", "temperature_celsius"),
            ("humidity", "REAL", "humidity_rh"),
            ("vibration", "REAL", "0"),
            ("machine_status", "TEXT", "machine_state"),
            ("quality_status", "TEXT", "'GOOD'"),
        ],
    }
    legacy_columns = {
        "iot_machines": ["min_temp_celsius", "max_temp_celsius", "max_humidity_rh", "status"],
        "iot_alerts": ["message"],
        "iot_oee_records": ["shift_no", "machine_name", "availability_pct", "performance_pct",
                            "quality_pct", "oee_pct", "total_output_carton", "total_downtime_minutes"],
        "iot_telemetry_logs": ["temperature_celsius", "humidity_rh", "machine_state"],
    }
    for table, cols in new_columns.items():
        for col, typ, backfill in cols:
            _exec_safe(conn, f"ALTER TABLE {table} ADD COLUMN {col} {typ}")
            if backfill:
                # Diabaikan otomatis kalau kolom sumber tidak ada (skema baru)
                _exec_safe(conn, f"UPDATE {table} SET {col} = {backfill} WHERE {col} IS NULL")
    for table, cols in legacy_columns.items():
        for col in cols:
            _exec_safe(conn, f"ALTER TABLE {table} ALTER COLUMN {col} DROP NOT NULL")
    _exec_safe(conn, "CREATE UNIQUE INDEX IF NOT EXISTS ux_iot_alerts_alert_id ON iot_alerts(alert_id)")
    conn.close()

init_enhanced_iot_tables()
migrate_legacy_iot_schema()

# --- SERVICES & API LOGIC ---

def get_live_shopfloor_status() -> Dict[str, Any]:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM iot_machines WHERE is_active IS TRUE ORDER BY machine_id ASC")
    machines = [dict(r) for r in cur.fetchall()]

    cur.execute("SELECT * FROM iot_alerts WHERE resolved_at IS NULL ORDER BY id DESC")
    active_alerts = [dict(r) for r in cur.fetchall()]

    cur.execute("SELECT * FROM iot_devices ORDER BY device_id ASC")
    devices = [dict(r) for r in cur.fetchall()]

    cur.execute("""
        SELECT * FROM iot_oee_records
        WHERE production_date = (SELECT MAX(production_date) FROM iot_oee_records)
    """)
    oee_list = [dict(r) for r in cur.fetchall()]

    avg_oee = round(sum(o.get("oee_percentage", o.get("oee_pct", 80.0)) for o in oee_list) / max(len(oee_list), 1), 1) if oee_list else 79.0
    total_good_output = sum(o.get("good_count", o.get("total_output_carton", 1000)) for o in oee_list)
    total_reject = sum(o.get("reject_count", 50) for o in oee_list)

    conn.close()
    return {
        "timestamp_wib": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB"),
        "plant_location": "Plant Utama Pati - Jawa Tengah",
        "average_oee_pct": avg_oee,
        "total_output_units": total_good_output,
        "total_reject_units": total_reject,
        "active_alerts_count": len(active_alerts),
        "online_devices_count": sum(1 for d in devices if d["connection_status"] == "ONLINE"),
        "total_devices_count": len(devices),
        "machines": machines,
        "devices": devices,
        "active_alerts": active_alerts,
        "oee_records": oee_list
    }

def get_iot_devices_health() -> List[Dict[str, Any]]:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT d.*, m.machine_name, m.production_line
        FROM iot_devices d
        JOIN iot_machines m ON d.machine_id = m.machine_id
        ORDER BY d.device_id ASC
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def acknowledge_iot_alert(alert_id_str: str, ack_by: str) -> Dict[str, Any]:
    conn = get_db()
    cur = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB")

    cur.execute("""
        UPDATE iot_alerts
        SET acknowledged_at = ?,
            acknowledged_by = ?
        WHERE alert_id = ? OR id = ?
    """, (now_str, ack_by, alert_id_str, int(alert_id_str) if alert_id_str.isdigit() else 0))

    conn.commit()
    conn.close()
    return {"success": True, "alert_id": alert_id_str, "status": "ACKNOWLEDGED", "acknowledged_at": now_str}

def resolve_iot_alert_enhanced(alert_id_str: str, resolved_by: str, notes: str) -> Dict[str, Any]:
    conn = get_db()
    cur = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB")

    cur.execute("""
        UPDATE iot_alerts
        SET resolved_at = ?,
            resolved_by = ?,
            resolution_notes = ?
        WHERE alert_id = ? OR id = ?
    """, (now_str, resolved_by, notes, alert_id_str, int(alert_id_str) if alert_id_str.isdigit() else 0))

    conn.commit()
    conn.close()
    return {"success": True, "alert_id": alert_id_str, "status": "RESOLVED", "resolved_at": now_str}

# --- INGEST TELEMETRI + DETEKSI ANOMALI (PRD Modul E.F) ---

def ingest_sensor_telemetry_enhanced(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Menerima telemetri dari IoT Gateway (REST, atau bridge MQTT -> REST).
    Field: machine_id (wajib), device_id, temperature, humidity, output_counter, vibration,
    machine_status, good_count, reject_count, product_id, downtime_reason, operator_id.
    """
    m_id = str(payload.get("machine_id") or "").strip()
    if not m_id:
        raise ValueError("machine_id wajib diisi.")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM iot_machines WHERE machine_id = ?", (m_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise IoTNotFound(f"Mesin {m_id} tidak terdaftar di master iot_machines.")
    machine = dict(row)

    now_str = _now_str()
    dev_id = payload.get("device_id")
    temp = _to_float(payload.get("temperature"))
    rh = _to_float(payload.get("humidity"))
    vib = _to_float(payload.get("vibration"))
    counter = _to_float(payload.get("output_counter"))
    status = str(payload.get("machine_status") or machine.get("machine_status") or "RUNNING").upper()
    if status not in ("RUNNING", "IDLE", "BREAKDOWN", "MAINTENANCE"):
        status = "RUNNING"

    alerts: List[Dict[str, Any]] = []

    # 1. SENSOR_FAILURE: nilai kosong / di luar rentang fisik sensor
    invalid = []
    if temp is None or not (-20 <= temp <= 400):
        invalid.append(f"temperature={payload.get('temperature')}")
    if rh is None or not (0 <= rh <= 100):
        invalid.append(f"humidity={payload.get('humidity')}")
    if vib is None or not (0 <= vib <= 100):
        invalid.append(f"vibration={payload.get('vibration')}")
    if invalid:
        a = _raise_alert(cur, machine, dev_id, "SENSOR_FAILURE", "WARNING", 0, 0,
                         f"SENSOR_FAILURE: {machine['machine_name']} mengirim nilai tidak valid ({', '.join(invalid)}).")
        if a: alerts.append(a)

    # 2. Ambang suhu & getaran (hanya dicek saat mesin berjalan)
    if status == "RUNNING":
        if temp is not None and -20 <= temp <= 400:
            if temp > machine["temperature_max"]:
                a = _raise_alert(cur, machine, dev_id, "OVERHEAT", "CRITICAL", temp, machine["temperature_max"],
                                 f"OVERHEAT: {machine['machine_name']} suhu {temp}°C (Maks: {machine['temperature_max']}°C)")
                if a: alerts.append(a)
            elif temp < machine["temperature_min"]:
                a = _raise_alert(cur, machine, dev_id, "UNDERHEAT", "WARNING", temp, machine["temperature_min"],
                                 f"UNDERHEAT: {machine['machine_name']} suhu {temp}°C (Min: {machine['temperature_min']}°C)")
                if a: alerts.append(a)
        if vib is not None and 0 <= vib <= 100 and vib > machine["vibration_threshold"]:
            a = _raise_alert(cur, machine, dev_id, "HIGH_VIBRATION", "WARNING", vib, machine["vibration_threshold"],
                             f"HIGH_VIBRATION: {machine['machine_name']} getaran {vib} mm/s (Batas: {machine['vibration_threshold']} mm/s)")
            if a: alerts.append(a)

    # 3. Machine events: catat perubahan status (downtime dibuka/ditutup)
    prev_status = (machine.get("machine_status") or "RUNNING").upper()
    if status != prev_status:
        cur.execute("""
            SELECT event_id, start_time FROM iot_machine_events
            WHERE machine_id = ? AND end_time IS NULL ORDER BY id DESC LIMIT 1
        """, (m_id,))
        open_ev = cur.fetchone()
        if open_ev:
            started = _parse_ts(open_ev["start_time"]) or _now()
            dur = max(int((_now() - started).total_seconds()), 0)
            cur.execute("UPDATE iot_machine_events SET end_time = ?, duration_seconds = ? WHERE event_id = ?",
                        (now_str, dur, open_ev["event_id"]))
        if status != "RUNNING":
            category = "PLANNED" if status == "MAINTENANCE" else "UNPLANNED"
            event_type = "MAINTENANCE" if status == "MAINTENANCE" else "DOWNTIME"
            cur.execute("""
                INSERT INTO iot_machine_events (
                    event_id, machine_id, event_type, start_time, downtime_category, downtime_reason, operator_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (f"EVT-{uuid.uuid4().hex[:10].upper()}", m_id, event_type, now_str, category,
                  payload.get("downtime_reason") or f"Status berubah {prev_status} -> {status}",
                  payload.get("operator_id")))

    # 4. Update snapshot mesin
    cur.execute("""
        UPDATE iot_machines
        SET current_temp_celsius = COALESCE(?, current_temp_celsius),
            current_humidity_rh = COALESCE(?, current_humidity_rh),
            current_speed_ppm = COALESCE(?, current_speed_ppm),
            current_vibration_mms = COALESCE(?, current_vibration_mms),
            machine_status = ?,
            last_heartbeat = ?
        WHERE machine_id = ?
    """, (temp, rh, int(counter) if counter is not None else None, vib, status, now_str, m_id))

    # 5. Log telemetri
    cur.execute("""
        INSERT INTO iot_telemetry_logs (
            machine_id, device_id, timestamp, temperature, humidity,
            output_counter, vibration, machine_status, quality_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (m_id, dev_id, now_str, temp if temp is not None else 0, rh if rh is not None else 0,
          int(counter or 0), vib if vib is not None else 0, status,
          "REJECT" if int(payload.get("reject_count") or 0) > 0 else "GOOD"))

    # 6. Production counter (opsional)
    good = payload.get("good_count")
    reject = payload.get("reject_count")
    if good is not None or reject is not None:
        g, r = int(good or 0), int(reject or 0)
        cur.execute("""
            INSERT INTO iot_production_counters (
                machine_id, shift_id, product_id, total_count, good_count, reject_count, recorded_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (m_id, current_shift()["shift_no"], payload.get("product_id") or machine.get("product_type"),
              g + r, g, r, now_str))

    # 7. Heartbeat perangkat
    if dev_id:
        cur.execute("UPDATE iot_devices SET last_seen_at = ?, connection_status = 'ONLINE' WHERE device_id = ?",
                    (now_str, dev_id))
    cur.execute("UPDATE iot_devices SET last_seen_at = ?, connection_status = 'ONLINE' WHERE machine_id = ? AND device_type = 'GATEWAY'",
                (now_str, m_id))

    conn.commit()
    conn.close()
    return {
        "success": True,
        "machine_id": m_id,
        "machine_status": status,
        "timestamp": now_str,
        "alerts_triggered": alerts,
        "alert_warning": alerts[0]["message"] if alerts else None,
    }

def run_health_check() -> Dict[str, Any]:
    """
    Pemeriksaan berkala: DEVICE_OFFLINE (tidak ada data > 5 menit) dan
    UNSCHEDULED_DOWNTIME (downtime tak terencana > 5 menit). Dipanggil oleh background loop.
    """
    conn = get_db()
    cur = conn.cursor()
    now = _now()
    created: List[Dict[str, Any]] = []

    cur.execute("SELECT * FROM iot_machines")
    machines = {r["machine_id"]: dict(r) for r in cur.fetchall()}

    cur.execute("SELECT * FROM iot_devices")
    for d in [dict(r) for r in cur.fetchall()]:
        last = _parse_ts(d.get("last_seen_at"))
        stale = last is None or (now - last).total_seconds() > DEVICE_OFFLINE_SECONDS
        if stale and d.get("connection_status") != "OFFLINE":
            cur.execute("UPDATE iot_devices SET connection_status = 'OFFLINE' WHERE device_id = ?", (d["device_id"],))
            m = machines.get(d["machine_id"])
            if m:
                a = _raise_alert(cur, m, d["device_id"], "DEVICE_OFFLINE", "CRITICAL",
                                 round((now - last).total_seconds() / 60, 1) if last else 0, DEVICE_OFFLINE_SECONDS / 60,
                                 f"DEVICE_OFFLINE: {d['device_id']} ({d['sensor_type']}) di {m['machine_name']} tidak mengirim data sejak {d.get('last_seen_at') or '-'}.")
                if a: created.append(a)

    cur.execute("SELECT * FROM iot_machine_events WHERE end_time IS NULL AND downtime_category = 'UNPLANNED'")
    for ev in [dict(r) for r in cur.fetchall()]:
        started = _parse_ts(ev["start_time"])
        if not started:
            continue
        secs = (now - started).total_seconds()
        m = machines.get(ev["machine_id"])
        if m and secs > UNSCHEDULED_DOWNTIME_SECONDS:
            a = _raise_alert(cur, m, None, "UNSCHEDULED_DOWNTIME", "CRITICAL", round(secs / 60, 1),
                             UNSCHEDULED_DOWNTIME_SECONDS / 60,
                             f"UNSCHEDULED_DOWNTIME: {m['machine_name']} berhenti ({m.get('machine_status')}) selama {round(secs / 60, 1)} menit di luar jadwal.")
            if a: created.append(a)

    conn.commit()
    conn.close()
    return {"checked_at": now.strftime(TS_FMT), "alerts_created": created}

# --- KALKULASI OEE (PRD Modul E.G) ---

def _shift_bounds(production_date: str, shift_no: int):
    start_s, end_s = SHIFT_WINDOWS[shift_no]
    day = datetime.datetime.strptime(production_date, "%Y-%m-%d").replace(tzinfo=WIB)
    start = day.replace(hour=int(start_s[:2]), minute=int(start_s[3:]))
    end = day.replace(hour=int(end_s[:2]), minute=int(end_s[3:]))
    if end <= start:
        end += datetime.timedelta(days=1)
    return start, end

def calculate_oee(machine_id: str, production_date: str, shift_no: int, save: bool = True) -> Dict[str, Any]:
    """
    OEE = Availability x Performance x Quality
    - Availability = Operating Time / Planned Production Time
    - Performance  = (Ideal Cycle Time x Total Count) / Operating Time  (ideal cycle time = 1 / ideal_speed_ppm)
    - Quality      = Good Count / Total Count
    """
    if shift_no not in SHIFT_WINDOWS:
        raise ValueError("shift_no harus 1, 2, atau 3.")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM iot_machines WHERE machine_id = ?", (machine_id,))
    m = cur.fetchone()
    if not m:
        conn.close()
        raise IoTNotFound(f"Mesin {machine_id} tidak ditemukan.")
    m = dict(m)

    cur.execute("""
        SELECT * FROM iot_production_schedules
        WHERE machine_id = ? AND production_date = ? AND shift_no = ?
        ORDER BY id DESC LIMIT 1
    """, (machine_id, production_date, shift_no))
    sched = cur.fetchone()
    planned_downtime = int(sched["planned_downtime_minutes"]) if sched else 0
    planned_time = max((int(sched["planned_production_minutes"]) if sched else 480) - planned_downtime, 1)

    start, end = _shift_bounds(production_date, shift_no)
    now = _now()
    window_end = min(end, now)
    # Shift yang sedang berjalan: planned time diprorata sesuai waktu yang sudah lewat
    if start < now < end:
        elapsed_ratio = (now - start).total_seconds() / (end - start).total_seconds()
        planned_time = max(int(round(planned_time * elapsed_ratio)), 1)

    cur.execute("SELECT * FROM iot_machine_events WHERE machine_id = ? AND downtime_category = 'UNPLANNED'", (machine_id,))
    downtime_sec = 0.0
    for ev in cur.fetchall():
        s = _parse_ts(ev["start_time"])
        e = _parse_ts(ev["end_time"]) or now
        if not s:
            continue
        overlap = (min(e, window_end) - max(s, start)).total_seconds()
        if overlap > 0:
            downtime_sec += overlap
    downtime_min = int(round(downtime_sec / 60))
    operating_time = max(planned_time - downtime_min, 0)

    cur.execute("SELECT * FROM iot_production_counters WHERE machine_id = ?", (machine_id,))
    total = good = reject = 0
    for c in cur.fetchall():
        ts = _parse_ts(c["recorded_at"])
        if ts and start <= ts < end:
            total += int(c["total_count"]); good += int(c["good_count"]); reject += int(c["reject_count"])

    ideal_ppm = max(float(m["ideal_speed_ppm"] or 1), 1)
    availability = operating_time / planned_time
    performance = min((total / ideal_ppm) / operating_time, 1.0) if operating_time else 0
    quality = good / total if total else 0
    oee = availability * performance * quality

    record = {
        "machine_id": machine_id,
        "production_line": m["production_line"],
        "shift_id": shift_no,
        "production_date": production_date,
        "planned_production_time_min": planned_time,
        "operating_time_min": operating_time,
        "downtime_minutes": downtime_min,
        "total_count": total,
        "good_count": good,
        "reject_count": reject,
        "availability_percentage": round(availability * 100, 1),
        "performance_percentage": round(performance * 100, 1),
        "quality_percentage": round(quality * 100, 1),
        "oee_percentage": round(oee * 100, 1),
    }

    if save:
        cur.execute("DELETE FROM iot_oee_records WHERE machine_id = ? AND production_date = ? AND shift_id = ?",
                    (machine_id, production_date, shift_no))
        cols = list(record.keys())
        cur.execute(f"INSERT INTO iot_oee_records ({', '.join(cols)}) VALUES ({', '.join('?' for _ in cols)})",
                    tuple(record[c] for c in cols))
        conn.commit()
    conn.close()
    return record

def recalculate_current_shift_oee() -> List[Dict[str, Any]]:
    """Hitung ulang OEE shift berjalan untuk semua mesin yang punya data counter."""
    sh = current_shift()
    ids = [r["machine_id"] for r in _query("SELECT DISTINCT machine_id FROM iot_production_counters")]
    out = []
    for mid in ids:
        try:
            out.append(calculate_oee(mid, sh["production_date"], sh["shift_no"]))
        except Exception as ex:
            print(f"[IoT] OEE gagal untuk {mid}: {ex}")
    return out

# --- QUERY & LAPORAN (PRD 11.3.C API Endpoints) ---

def _where(filters: Dict[str, Any]):
    clauses, params = [], []
    for col, val in filters.items():
        if val is None or val == "" or str(val).upper() == "ALL":
            continue
        if col.endswith("__gte"):
            clauses.append(f"{col[:-5]} >= ?")
        elif col.endswith("__lte"):
            clauses.append(f"{col[:-5]} <= ?")
        else:
            clauses.append(f"{col} = ?")
        params.append(val)
    return (" WHERE " + " AND ".join(clauses)) if clauses else "", params

def _query(sql: str, params=()) -> List[Dict[str, Any]]:
    conn = get_db()
    cur = conn.cursor()
    cur.execute(sql, tuple(params))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def list_machines(production_line: Optional[str] = None) -> List[Dict[str, Any]]:
    where, params = _where({"production_line": production_line})
    return _query(f"SELECT * FROM iot_machines{where} ORDER BY machine_id ASC", params)

def get_machine_detail(machine_id: str) -> Dict[str, Any]:
    rows = _query("SELECT * FROM iot_machines WHERE machine_id = ?", (machine_id,))
    if not rows:
        raise IoTNotFound(f"Mesin {machine_id} tidak ditemukan.")
    return {
        **rows[0],
        "devices": _query("SELECT * FROM iot_devices WHERE machine_id = ? ORDER BY device_id", (machine_id,)),
        "active_alerts": _query("SELECT * FROM iot_alerts WHERE machine_id = ? AND resolved_at IS NULL ORDER BY id DESC", (machine_id,)),
        "recent_events": _query("SELECT * FROM iot_machine_events WHERE machine_id = ? ORDER BY id DESC LIMIT 20", (machine_id,)),
        "recent_telemetry": _query("SELECT * FROM iot_telemetry_logs WHERE machine_id = ? ORDER BY id DESC LIMIT 60", (machine_id,)),
        "oee_history": _query("SELECT * FROM iot_oee_records WHERE machine_id = ? ORDER BY production_date DESC, shift_id DESC LIMIT 30", (machine_id,)),
    }

def list_alerts(status: Optional[str] = None, machine_id: Optional[str] = None,
                alert_type: Optional[str] = None, limit: int = 200) -> List[Dict[str, Any]]:
    where, params = _where({"machine_id": machine_id, "alert_type": alert_type})
    extra = {
        "ACTIVE": "resolved_at IS NULL",
        "OPEN": "acknowledged_at IS NULL AND resolved_at IS NULL",
        "ACKNOWLEDGED": "acknowledged_at IS NOT NULL AND resolved_at IS NULL",
        "RESOLVED": "resolved_at IS NOT NULL",
    }.get((status or "").upper())
    if extra:
        where = (where + " AND " + extra) if where else (" WHERE " + extra)
    return _query(f"SELECT * FROM iot_alerts{where} ORDER BY id DESC LIMIT {int(limit)}", params)

def get_telemetry_history(machine_id: Optional[str] = None, limit: int = 500) -> List[Dict[str, Any]]:
    where, params = _where({"machine_id": machine_id})
    rows = _query(f"SELECT * FROM iot_telemetry_logs{where} ORDER BY id DESC LIMIT {min(int(limit), 5000)}", params)
    return list(reversed(rows))

def get_oee_report(date_from: Optional[str] = None, date_to: Optional[str] = None,
                   machine_id: Optional[str] = None, shift_id: Optional[int] = None,
                   production_line: Optional[str] = None) -> List[Dict[str, Any]]:
    where, params = _where({
        "production_date__gte": date_from, "production_date__lte": date_to,
        "machine_id": machine_id, "shift_id": shift_id, "production_line": production_line,
    })
    return _query(f"SELECT * FROM iot_oee_records{where} ORDER BY production_date DESC, production_line, shift_id", params)

def _agg_oee(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    planned = sum(r["planned_production_time_min"] for r in items)
    operating = sum(r["operating_time_min"] for r in items)
    total = sum(r["total_count"] for r in items)
    good = sum(r["good_count"] for r in items)
    perf = (sum(r["performance_percentage"] * r["operating_time_min"] for r in items) / operating) if operating else 0
    avail = operating / planned * 100 if planned else 0
    qual = good / total * 100 if total else 0
    return {
        "availability_percentage": round(avail, 1),
        "performance_percentage": round(perf, 1),
        "quality_percentage": round(qual, 1),
        "oee_percentage": round(avail * perf * qual / 10000, 1),
        "total_count": total,
        "good_count": good,
        "reject_count": sum(r["reject_count"] for r in items),
        "downtime_minutes": sum(r["downtime_minutes"] for r in items),
    }

def get_oee_summary(date_from: Optional[str] = None, date_to: Optional[str] = None) -> Dict[str, Any]:
    rows = get_oee_report(date_from, date_to)
    by_line: Dict[str, List[Dict[str, Any]]] = {}
    for r in rows:
        by_line.setdefault(r["production_line"], []).append(r)
    return {
        "date_from": date_from,
        "date_to": date_to,
        "plant": _agg_oee(rows) if rows else None,
        "by_line": [{"production_line": k, **_agg_oee(v)} for k, v in sorted(by_line.items())],
        "records_count": len(rows),
    }

def get_production_summary(production_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """Target vs aktual output per mesin per shift."""
    production_date = production_date or current_shift()["production_date"]
    scheds = _query("""
        SELECT s.*, m.machine_name, m.production_line, m.ideal_speed_ppm
        FROM iot_production_schedules s JOIN iot_machines m ON s.machine_id = m.machine_id
        WHERE s.production_date = ? ORDER BY s.machine_id, s.shift_no
    """, (production_date,))
    oee = {(r["machine_id"], r["shift_id"]): r for r in get_oee_report(production_date, production_date)}
    out = []
    for s in scheds:
        rec = oee.get((s["machine_id"], s["shift_no"]))
        target = s["target_output_carton"] or int(s["ideal_speed_ppm"] * (s["planned_production_minutes"] - s["planned_downtime_minutes"]))
        actual = rec["good_count"] if rec else 0
        out.append({
            "production_date": production_date,
            "shift_no": s["shift_no"],
            "machine_id": s["machine_id"],
            "machine_name": s["machine_name"],
            "production_line": s["production_line"],
            "target_output": target,
            "actual_good_output": actual,
            "reject_output": rec["reject_count"] if rec else 0,
            "achievement_percentage": round(actual / target * 100, 1) if target else 0,
            "oee_percentage": rec["oee_percentage"] if rec else None,
        })
    return out

def get_production_report(date_from: Optional[str] = None, date_to: Optional[str] = None,
                          machine_id: Optional[str] = None) -> List[Dict[str, Any]]:
    keys = ("production_date", "shift_id", "machine_id", "production_line",
            "total_count", "good_count", "reject_count", "quality_percentage")
    return [{k: r[k] for k in keys} for r in get_oee_report(date_from, date_to, machine_id)]

def get_downtime_report(date_from: Optional[str] = None, date_to: Optional[str] = None,
                        machine_id: Optional[str] = None) -> Dict[str, Any]:
    where, params = _where({"e.machine_id": machine_id})
    events = _query(f"""
        SELECT e.*, m.machine_name, m.production_line
        FROM iot_machine_events e JOIN iot_machines m ON e.machine_id = m.machine_id
        {where} ORDER BY e.id DESC
    """, params)
    now = _now()
    out = []
    for e in events:
        day = str(e["start_time"])[:10]
        if (date_from and day < date_from) or (date_to and day > date_to):
            continue
        e["is_ongoing"] = e["end_time"] is None
        if e["is_ongoing"]:
            s = _parse_ts(e["start_time"])
            e["duration_seconds"] = int((now - s).total_seconds()) if s else 0
        e["duration_minutes"] = round((e["duration_seconds"] or 0) / 60, 1)
        out.append(e)
    by_reason: Dict[str, float] = {}
    by_machine: Dict[str, float] = {}
    for e in out:
        reason = e.get("downtime_reason") or "Tidak diketahui"
        by_reason[reason] = by_reason.get(reason, 0) + e["duration_minutes"]
        by_machine[e["machine_id"]] = by_machine.get(e["machine_id"], 0) + e["duration_minutes"]
    return {
        "events": out,
        "total_downtime_minutes": round(sum(e["duration_minutes"] for e in out), 1),
        "by_reason": [{"reason": k, "minutes": round(v, 1)} for k, v in sorted(by_reason.items(), key=lambda x: -x[1])],
        "by_machine": [{"machine_id": k, "minutes": round(v, 1)} for k, v in sorted(by_machine.items(), key=lambda x: -x[1])],
    }

