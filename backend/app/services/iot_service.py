import datetime
import random
from typing import Dict, Any, List, Optional
from app.db.connection import get_db

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

    conn.commit()
    conn.close()

init_enhanced_iot_tables()

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

    cur.execute("SELECT * FROM iot_oee_records WHERE production_date = '2026-10-31'")
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

def ingest_sensor_telemetry_enhanced(payload: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_db()
    cur = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB")

    m_id = payload.get("machine_id", "MCH-PATI-01")
    dev_id = payload.get("device_id", "DEV-TEMP-01")
    temp = float(payload.get("temperature", 175.0))
    rh = float(payload.get("humidity", 48.0))
    speed = int(payload.get("output_counter", 120))
    vib = float(payload.get("vibration", 2.2))
    status = payload.get("machine_status", "RUNNING")

    cur.execute("""
        UPDATE iot_machines
        SET current_temp_celsius = ?,
            current_humidity_rh = ?,
            current_speed_ppm = ?,
            current_vibration_mms = ?,
            machine_status = ?,
            last_heartbeat = ?
        WHERE machine_id = ?
    """, (temp, rh, speed, vib, status, now_str, m_id))

    cur.execute("""
        INSERT INTO iot_telemetry_logs (
            machine_id, device_id, timestamp, temperature, humidity,
            output_counter, vibration, machine_status, quality_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'GOOD')
    """, (m_id, dev_id, now_str, temp, rh, speed, vib, status))

    # Threshold Check
    alert_created = None
    cur.execute("SELECT * FROM iot_machines WHERE machine_id = ?", (m_id,))
    m = cur.fetchone()
    if m:
        if temp > m["temperature_max"]:
            aid = f"ALT-{random.randint(10000, 99999)}"
            msg = f"OVERHEAT DETECTED: {m['machine_name']} suhu {temp}°C (Maks: {m['temperature_max']}°C)"
            cur.execute("""
                INSERT INTO iot_alerts (
                    alert_id, machine_id, device_id, alert_type, severity, metric_value,
                    threshold_value, alert_message, triggered_at
                ) VALUES (?, ?, ?, 'OVERHEAT', 'CRITICAL', ?, ?, ?, ?)
            """, (aid, m_id, dev_id, temp, m["temperature_max"], msg, now_str))
            alert_created = msg
        elif vib > m["vibration_threshold"]:
            aid = f"ALT-{random.randint(10000, 99999)}"
            msg = f"HIGH_VIBRATION: {m['machine_name']} getaran {vib} mm/s (Batas: {m['vibration_threshold']} mm/s)"
            cur.execute("""
                INSERT INTO iot_alerts (
                    alert_id, machine_id, device_id, alert_type, severity, metric_value,
                    threshold_value, alert_message, triggered_at
                ) VALUES (?, ?, ?, 'HIGH_VIBRATION', 'WARNING', ?, ?, ?, ?)
            """, (aid, m_id, dev_id, vib, m["vibration_threshold"], msg, now_str))
            alert_created = msg

    conn.commit()
    conn.close()
    return {"success": True, "machine_id": m_id, "timestamp": now_str, "alert_warning": alert_created}
