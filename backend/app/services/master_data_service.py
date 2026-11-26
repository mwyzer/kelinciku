import sqlite3
from typing import Dict, Any, List, Optional
from app.db.connection import get_db

def init_master_data_tables():
    conn = get_db()
    cur = conn.cursor()

    # 1. Master SKU / Produk
    cur.execute("""
    CREATE TABLE IF NOT EXISTS master_products (
        sku_id TEXT PRIMARY KEY,
        sku_name TEXT NOT NULL,
        brand TEXT NOT NULL,
        category TEXT NOT NULL,
        carton_pack_qty INTEGER DEFAULT 24,
        price_het_idr REAL NOT NULL,
        price_wholesale_idr REAL NOT NULL,
        shelf_life_days INTEGER DEFAULT 365,
        status TEXT DEFAULT 'ACTIVE'
    );
    """)

    # 2. Master Outlet
    cur.execute("""
    CREATE TABLE IF NOT EXISTS master_outlets (
        outlet_id TEXT PRIMARY KEY,
        outlet_name TEXT NOT NULL,
        outlet_type TEXT NOT NULL,
        region TEXT NOT NULL,
        branch TEXT NOT NULL,
        payment_term_days INTEGER DEFAULT 14,
        status TEXT DEFAULT 'ACTIVE'
    );
    """)

    # 3. Master Gudang / Depo
    cur.execute("""
    CREATE TABLE IF NOT EXISTS master_warehouses (
        warehouse_id TEXT PRIMARY KEY,
        warehouse_name TEXT NOT NULL,
        region TEXT NOT NULL,
        branch TEXT NOT NULL,
        capacity_carton INTEGER DEFAULT 10000,
        status TEXT DEFAULT 'ACTIVE'
    );
    """)

    # 4. Master Karyawan & Manajerial (Sales & Warehouse Focus)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS master_employees (
        employee_id TEXT PRIMARY KEY,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        department TEXT NOT NULL, -- SALES, WAREHOUSE, LOGISTICS, MANAGEMENT
        job_title TEXT NOT NULL,  -- Head of Sales, Sales Manager, Sales Supervisor, Field Salesman, Head of Warehouse, Warehouse Manager, Gudang Supervisor, Picker/Operator
        role_type TEXT NOT NULL,  -- MANAGER, SUPERVISOR, STAFF
        region TEXT NOT NULL,     -- Nasional, Jawa Barat, Jawa Tengah, Jawa Timur, Jabodetabek, Sumatera, Kalimantan
        branch TEXT NOT NULL,     -- Pusat, Bandung, Semarang, Surabaya, Jakarta Barat, etc.
        warehouse_id TEXT,        -- Nullable, linked to master_warehouses if Warehouse dept
        status TEXT DEFAULT 'ACTIVE'
    );
    """)

    conn.commit()

    # Seed Master Products jika kosong
    cur.execute("SELECT COUNT(*) FROM master_products;")
    if cur.fetchone()[0] == 0:
        cur.execute("SELECT DISTINCT sku, brand FROM fact_sales WHERE sku IS NOT NULL AND sku != '';")
        skus = cur.fetchall()
        for idx, row in enumerate(skus, 1):
            s_name = row["sku"]
            s_brand = row["brand"]
            cur.execute("""
                INSERT INTO master_products (sku_id, sku_name, brand, category, carton_pack_qty, price_het_idr, price_wholesale_idr)
                VALUES (?, ?, ?, 'Snack Kacang & Biskuit', 24, ?, ?);
            """, (f"SKU-{idx:03d}", s_name, s_brand, 185000.0, 166500.0))

    # Seed Master Outlets jika kosong
    cur.execute("SELECT COUNT(*) FROM master_outlets;")
    if cur.fetchone()[0] == 0:
        cur.execute("SELECT DISTINCT outlet_id, outlet_name, outlet_type, region, branch FROM fact_sales;")
        outlets = cur.fetchall()
        for row in outlets:
            cur.execute("""
                INSERT INTO master_outlets (outlet_id, outlet_name, outlet_type, region, branch, payment_term_days)
                VALUES (?, ?, ?, ?, ?, ?);
            """, (row["outlet_id"], row["outlet_name"], row["outlet_type"], row["region"], row["branch"], 21))

    # Seed Master Warehouses jika kosong
    cur.execute("SELECT COUNT(*) FROM master_warehouses;")
    if cur.fetchone()[0] == 0:
        cur.execute("SELECT DISTINCT warehouse_id, warehouse_name, region, branch FROM fact_stock;")
        whs = cur.fetchall()
        for row in whs:
            cur.execute("""
                INSERT INTO master_warehouses (warehouse_id, warehouse_name, region, branch, capacity_carton)
                VALUES (?, ?, ?, ?, 15000);
            """, (row["warehouse_id"], row["warehouse_name"], row["region"], row["branch"]))

    # Seed Master Karyawan jika kosong
    cur.execute("SELECT COUNT(*) FROM master_employees;")
    if cur.fetchone()[0] == 0:
        seed_employees = [
            # SALES DIVISION - MANAGERIAL & FIELD
            ("EMP-SLS-001", "Muhammad Wyzer", "muhammad.wyzer@gmail.com", "081234567890", "SALES", "Head of Sales", "MANAGER", "Nasional", "Pusat", None),
            ("EMP-SLS-002", "Rudi Hartono", "head.sales@duakelinci.id", "081298765432", "SALES", "Sales Director / GM", "MANAGER", "Nasional", "Pusat", None),
            ("EMP-SLS-003", "Dedi Kurniawan", "hr.jabar@duakelinci.id", "081311223344", "SALES", "Regional Sales Manager Jabar", "MANAGER", "Jawa Barat", "Bandung", None),
            ("EMP-SLS-004", "Siti Rahma", "hr.jatim@duakelinci.id", "081322334455", "SALES", "Regional Sales Manager Jatim", "MANAGER", "Jawa Timur", "Surabaya", None),
            ("EMP-SLS-005", "Hendra Pratama", "hr.jabodetabek@duakelinci.id", "081333445566", "SALES", "Regional Sales Manager Jabodetabek", "MANAGER", "Jabodetabek", "Jakarta Barat", None),
            ("EMP-SLS-006", "Gita Savitri", "gita.sales@duakelinci.id", "081344556677", "SALES", "Area Sales Supervisor", "SUPERVISOR", "Jawa Barat", "Bandung", None),
            ("EMP-SLS-007", "Hendra Gunawan", "hendra.sales@duakelinci.id", "081355667788", "SALES", "Field Salesman Senior", "STAFF", "Jawa Barat", "Bandung", None),
            ("EMP-SLS-008", "Fajar Nugraha", "fajar.sales@duakelinci.id", "081366778899", "SALES", "Field Salesman", "STAFF", "Jabodetabek", "Bekasi", None),
            ("EMP-SLS-009", "Putri Lestari", "putri.sales@duakelinci.id", "081377889900", "SALES", "Field Salesman", "STAFF", "Jawa Timur", "Surabaya", None),
            
            # WAREHOUSE & LOGISTICS DIVISION - MANAGERIAL & OPERATIONAL
            ("EMP-WMS-001", "Bambang Soeprapto", "bambang.warehouse@duakelinci.id", "081255443322", "WAREHOUSE", "Head of Warehouse & Logistics", "MANAGER", "Nasional", "Pusat", "WH-BDG"),
            ("EMP-WMS-002", "Agus Setiawan", "agus.wh.bdg@duakelinci.id", "081266554433", "WAREHOUSE", "Warehouse Manager Bandung", "MANAGER", "Jawa Barat", "Bandung", "WH-BDG"),
            ("EMP-WMS-003", "Tri Wahyuni", "tri.wh.sby@duakelinci.id", "081277665544", "WAREHOUSE", "Warehouse Manager Surabaya", "MANAGER", "Jawa Timur", "Surabaya", "WH-SBY"),
            ("EMP-WMS-004", "Joko Purwanto", "joko.wh.smg@duakelinci.id", "081288776655", "WAREHOUSE", "Warehouse Manager Semarang", "MANAGER", "Jawa Tengah", "Semarang", "WH-SMG"),
            ("EMP-WMS-005", "Ilham Syahputra", "ilham.spv.bdg@duakelinci.id", "081299887766", "WAREHOUSE", "Warehouse Supervisor", "SUPERVISOR", "Jawa Barat", "Bandung", "WH-BDG"),
            ("EMP-WMS-006", "Surya Saputra", "surya.picker@duakelinci.id", "081211009988", "WAREHOUSE", "FEFO Picking Lead Operator", "STAFF", "Jawa Barat", "Bandung", "WH-BDG"),
            ("EMP-WMS-007", "Rian Hidayat", "rian.checker@duakelinci.id", "081222110099", "WAREHOUSE", "Inbound/Outbound Inspector", "STAFF", "Jabodetabek", "Bekasi", "WH-BEK"),
        ]

        for emp in seed_employees:
            cur.execute("""
                INSERT INTO master_employees (
                    employee_id, full_name, email, phone, department, job_title, role_type, region, branch, warehouse_id, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE')
                ON CONFLICT(employee_id) DO NOTHING;
            """, emp)

        # Sinkronkan user_scope untuk login / persona switcher
        for emp in seed_employees:
            e_id, name, email, phone, dept, title, role_type, region, branch, wh_id = emp
            scope_type = "NATIONAL" if region == "Nasional" else "REGION"
            scope_val = "ALL" if region == "Nasional" else region
            cur.execute("""
                INSERT INTO user_scope (email, full_name, role, scope_type, scope_value)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(email) DO UPDATE SET
                    full_name=excluded.full_name,
                    role=excluded.role,
                    scope_type=excluded.scope_type,
                    scope_value=excluded.scope_value;
            """, (email, f"{name} ({title})", "head_sales" if dept == "SALES" else "warehouse_lead", scope_type, scope_val))

    conn.commit()
    conn.close()

init_master_data_tables()

# ================= READ / LIST =================

def list_products():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM master_products ORDER BY brand, sku_name ASC;")
    res = [dict(r) for r in cur.fetchall()]
    conn.close()
    return res

def list_outlets():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM master_outlets ORDER BY outlet_name ASC, outlet_id ASC;")
    res = [dict(r) for r in cur.fetchall()]
    conn.close()
    return res

def list_outlet_transactions():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT date, invoice_no, region, branch, outlet_id, outlet_name, outlet_type,
               salesman, brand, sku, qty_carton, price_per_carton_idr,
               gross_sales_idr, discount_idr, net_sales_idr
        FROM fact_sales
        ORDER BY date DESC, invoice_no ASC, sku ASC;
    """)
    res = [dict(r) for r in cur.fetchall()]
    conn.close()
    return res

def list_warehouses():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM master_warehouses ORDER BY region, branch ASC;")
    res = [dict(r) for r in cur.fetchall()]
    conn.close()
    return res

def list_employees(department: Optional[str] = None):
    conn = get_db()
    cur = conn.cursor()
    if department and department.upper() != "ALL":
        cur.execute("SELECT * FROM master_employees WHERE department = ? ORDER BY department, role_type DESC, full_name ASC;", (department.upper(),))
    else:
        cur.execute("SELECT * FROM master_employees ORDER BY department, role_type DESC, full_name ASC;")
    res = [dict(r) for r in cur.fetchall()]
    conn.close()
    return res

# ================= CREATE / ADD =================

def create_product(data: Dict[str, Any]) -> Dict[str, Any]:
    sku_id = data.get("sku_id", "").strip().upper()
    if not sku_id:
        raise ValueError("Kode SKU (sku_id) wajib diisi.")
    sku_name = data.get("sku_name", "").strip()
    if not sku_name:
        raise ValueError("Nama SKU Produk (sku_name) wajib diisi.")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO master_products (
            sku_id, sku_name, brand, category, carton_pack_qty, price_het_idr, price_wholesale_idr, shelf_life_days, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (sku_id) DO UPDATE SET
            sku_name = excluded.sku_name,
            brand = excluded.brand,
            category = excluded.category,
            carton_pack_qty = excluded.carton_pack_qty,
            price_het_idr = excluded.price_het_idr,
            price_wholesale_idr = excluded.price_wholesale_idr,
            shelf_life_days = excluded.shelf_life_days,
            status = excluded.status;
    """, (
        sku_id,
        sku_name,
        data.get("brand", "Dua Kelinci"),
        data.get("category", "Snack"),
        int(data.get("carton_pack_qty", 24)),
        float(data.get("price_het_idr", 0)),
        float(data.get("price_wholesale_idr", 0)),
        int(data.get("shelf_life_days", 365)),
        data.get("status", "ACTIVE")
    ))
    conn.commit()
    conn.close()
    return {"success": True, "sku_id": sku_id, "message": f"Produk SKU {sku_id} ({sku_name}) berhasil ditambahkan."}

def create_outlet(data: Dict[str, Any]) -> Dict[str, Any]:
    outlet_id = data.get("outlet_id", "").strip().upper()
    if not outlet_id:
        raise ValueError("Kode Outlet (outlet_id) wajib diisi.")
    outlet_name = data.get("outlet_name", "").strip()
    if not outlet_name:
        raise ValueError("Nama Outlet (outlet_name) wajib diisi.")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO master_outlets (
            outlet_id, outlet_name, outlet_type, region, branch, payment_term_days, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (outlet_id) DO UPDATE SET
            outlet_name = excluded.outlet_name,
            outlet_type = excluded.outlet_type,
            region = excluded.region,
            branch = excluded.branch,
            payment_term_days = excluded.payment_term_days,
            status = excluded.status;
    """, (
        outlet_id,
        outlet_name,
        data.get("outlet_type", "Grosir"),
        data.get("region", "Jawa Barat"),
        data.get("branch", "Bandung"),
        int(data.get("payment_term_days", 14)),
        data.get("status", "ACTIVE")
    ))
    conn.commit()
    conn.close()
    return {"success": True, "outlet_id": outlet_id, "message": f"Outlet {outlet_id} ({outlet_name}) berhasil ditambahkan."}

def create_warehouse(data: Dict[str, Any]) -> Dict[str, Any]:
    warehouse_id = data.get("warehouse_id", "").strip().upper()
    if not warehouse_id:
        raise ValueError("Kode Gudang (warehouse_id) wajib diisi.")
    warehouse_name = data.get("warehouse_name", "").strip()
    if not warehouse_name:
        raise ValueError("Nama Gudang (warehouse_name) wajib diisi.")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO master_warehouses (
            warehouse_id, warehouse_name, region, branch, capacity_carton, status
        ) VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT (warehouse_id) DO UPDATE SET
            warehouse_name = excluded.warehouse_name,
            region = excluded.region,
            branch = excluded.branch,
            capacity_carton = excluded.capacity_carton,
            status = excluded.status;
    """, (
        warehouse_id,
        warehouse_name,
        data.get("region", "Jawa Barat"),
        data.get("branch", "Bandung"),
        int(data.get("capacity_carton", 10000)),
        data.get("status", "ACTIVE")
    ))
    conn.commit()
    conn.close()
    return {"success": True, "warehouse_id": warehouse_id, "message": f"Gudang {warehouse_id} ({warehouse_name}) berhasil ditambahkan."}

def create_employee(data: Dict[str, Any]) -> Dict[str, Any]:
    employee_id = data.get("employee_id", "").strip().upper()
    if not employee_id:
        raise ValueError("NIP / Kode Karyawan (employee_id) wajib diisi.")
    full_name = data.get("full_name", "").strip()
    if not full_name:
        raise ValueError("Nama Lengkap Karyawan (full_name) wajib diisi.")
    email = data.get("email", "").strip().lower()
    if not email:
        raise ValueError("Alamat Email (email) wajib diisi.")

    conn = get_db()
    cur = conn.cursor()
    department = data.get("department", "SALES").upper()
    job_title = data.get("job_title", "Field Salesman")
    role_type = data.get("role_type", "STAFF").upper()
    region = data.get("region", "Nasional")
    branch = data.get("branch", "Pusat")
    warehouse_id = data.get("warehouse_id") if department == "WAREHOUSE" else None
    phone = data.get("phone", "")
    status = data.get("status", "ACTIVE")

    cur.execute("""
        INSERT INTO master_employees (
            employee_id, full_name, email, phone, department, job_title, role_type, region, branch, warehouse_id, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (employee_id) DO UPDATE SET
            full_name = excluded.full_name,
            email = excluded.email,
            phone = excluded.phone,
            department = excluded.department,
            job_title = excluded.job_title,
            role_type = excluded.role_type,
            region = excluded.region,
            branch = excluded.branch,
            warehouse_id = excluded.warehouse_id,
            status = excluded.status;
    """, (
        employee_id, full_name, email, phone, department, job_title, role_type, region, branch, warehouse_id, status
    ))

    # Sinkronisasi ke user_scope
    scope_type = "NATIONAL" if region == "Nasional" else "REGION"
    scope_val = "ALL" if region == "Nasional" else region
    role = "head_sales" if department == "SALES" else "warehouse_lead"
    cur.execute("""
        INSERT INTO user_scope (email, full_name, role, scope_type, scope_value)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(email) DO UPDATE SET
            full_name=excluded.full_name,
            role=excluded.role,
            scope_type=excluded.scope_type,
            scope_value=excluded.scope_value;
    """, (email, f"{full_name} ({job_title})", role, scope_type, scope_val))

    conn.commit()
    conn.close()
    return {"success": True, "employee_id": employee_id, "message": f"Karyawan {employee_id} ({full_name}) berhasil ditambahkan."}

# ================= UPDATE / EDIT / DELETE =================

def update_outlet(outlet_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE master_outlets
        SET outlet_name = ?,
            outlet_type = ?,
            region = ?,
            branch = ?,
            payment_term_days = ?,
            status = ?
        WHERE outlet_id = ?;
    """, (
        data.get("outlet_name"),
        data.get("outlet_type"),
        data.get("region"),
        data.get("branch"),
        int(data.get("payment_term_days", 14)),
        data.get("status", "ACTIVE"),
        outlet_id
    ))
    conn.commit()
    conn.close()
    return {"success": True, "outlet_id": outlet_id, "message": f"Outlet {outlet_id} berhasil diperbarui."}

def delete_outlet(outlet_id: str) -> Dict[str, Any]:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM master_outlets WHERE outlet_id = ?;", (outlet_id,))
    conn.commit()
    conn.close()
    return {"success": True, "outlet_id": outlet_id, "message": f"Outlet {outlet_id} berhasil dihapus."}

def update_product(sku_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE master_products
        SET sku_name = ?,
            brand = ?,
            category = ?,
            carton_pack_qty = ?,
            price_het_idr = ?,
            price_wholesale_idr = ?,
            shelf_life_days = ?,
            status = ?
        WHERE sku_id = ?;
    """, (
        data.get("sku_name"),
        data.get("brand"),
        data.get("category"),
        int(data.get("carton_pack_qty", 24)),
        float(data.get("price_het_idr", 0)),
        float(data.get("price_wholesale_idr", 0)),
        int(data.get("shelf_life_days", 365)),
        data.get("status", "ACTIVE"),
        sku_id
    ))
    conn.commit()
    conn.close()
    return {"success": True, "sku_id": sku_id, "message": f"SKU {sku_id} berhasil diperbarui."}

def delete_product(sku_id: str) -> Dict[str, Any]:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM master_products WHERE sku_id = ?;", (sku_id,))
    conn.commit()
    conn.close()
    return {"success": True, "sku_id": sku_id, "message": f"SKU {sku_id} berhasil dihapus."}

def update_warehouse(warehouse_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE master_warehouses
        SET warehouse_name = ?,
            region = ?,
            branch = ?,
            capacity_carton = ?,
            status = ?
        WHERE warehouse_id = ?;
    """, (
        data.get("warehouse_name"),
        data.get("region"),
        data.get("branch"),
        int(data.get("capacity_carton", 10000)),
        data.get("status", "ACTIVE"),
        warehouse_id
    ))
    conn.commit()
    conn.close()
    return {"success": True, "warehouse_id": warehouse_id, "message": f"Gudang {warehouse_id} berhasil diperbarui."}

def delete_warehouse(warehouse_id: str) -> Dict[str, Any]:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM master_warehouses WHERE warehouse_id = ?;", (warehouse_id,))
    conn.commit()
    conn.close()
    return {"success": True, "warehouse_id": warehouse_id, "message": f"Gudang {warehouse_id} berhasil dihapus."}

def update_employee(employee_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM master_employees WHERE employee_id = ?;", (employee_id,))
    existing = cur.fetchone()
    if not existing:
        conn.close()
        return {"success": False, "employee_id": employee_id, "message": f"Karyawan {employee_id} tidak ditemukan."}

    full_name = data.get("full_name") if data.get("full_name") is not None else existing["full_name"]
    email = data.get("email") if data.get("email") is not None else existing["email"]
    phone = data.get("phone") if data.get("phone") is not None else existing["phone"]
    department = data.get("department") if data.get("department") is not None else existing["department"]
    job_title = data.get("job_title") if data.get("job_title") is not None else existing["job_title"]
    role_type = data.get("role_type") if data.get("role_type") is not None else existing["role_type"]
    region = data.get("region") if data.get("region") is not None else existing["region"]
    branch = data.get("branch") if data.get("branch") is not None else existing["branch"]
    warehouse_id = data.get("warehouse_id") if "warehouse_id" in data else existing["warehouse_id"]
    status = data.get("status") if data.get("status") is not None else existing["status"]

    cur.execute("""
        UPDATE master_employees
        SET full_name = ?,
            email = ?,
            phone = ?,
            department = ?,
            job_title = ?,
            role_type = ?,
            region = ?,
            branch = ?,
            warehouse_id = ?,
            status = ?
        WHERE employee_id = ?;
    """, (
        full_name,
        email,
        phone,
        department,
        job_title,
        role_type,
        region,
        branch,
        warehouse_id,
        status,
        employee_id
    ))
    # Sinkronisasi ke user_scope
    scope_type = "NATIONAL" if region == "Nasional" else "REGION"
    scope_val = "ALL" if region == "Nasional" else region
    role = "head_sales" if department == "SALES" else "warehouse_lead"
    cur.execute("""
        UPDATE user_scope
        SET full_name = ?,
            role = ?,
            scope_type = ?,
            scope_value = ?
        WHERE email = ?;
    """, (f"{full_name} ({job_title})", role, scope_type, scope_val, email))

    conn.commit()
    conn.close()
    return {"success": True, "employee_id": employee_id, "message": f"Karyawan {employee_id} ({full_name}) berhasil diperbarui."}

def delete_employee(employee_id: str) -> Dict[str, Any]:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM master_employees WHERE employee_id = ?;", (employee_id,))
    conn.commit()
    conn.close()
    return {"success": True, "employee_id": employee_id, "message": f"Karyawan {employee_id} berhasil dihapus."}

# ================= IMPORT CSV =================

def import_master_csv(entity_type: str, csv_content: str) -> Dict[str, Any]:
    """
    Import master data (products, outlets, warehouses, employees) dari teks/file CSV.
    Mendukung upsert baris demi baris.
    """
    import csv
    import io

    f = io.StringIO(csv_content.strip())
    reader = csv.DictReader(f)
    conn = get_db()
    cur = conn.cursor()
    imported_count = 0

    if entity_type == "outlets":
        for r in reader:
            o_id = r.get("outlet_id") or r.get("Kode Outlet") or f"OUT-{imported_count+1:04d}"
            name = r.get("outlet_name") or r.get("Nama Outlet") or "Outlet Tanpa Nama"
            o_type = r.get("outlet_type") or r.get("Tipe") or "Toko Kelontong"
            region = r.get("region") or r.get("Wilayah") or "Nasional"
            branch = r.get("branch") or r.get("Cabang") or "Pusat"
            terms = int(r.get("payment_term_days") or r.get("TOP") or 14)

            cur.execute("""
                INSERT INTO master_outlets (outlet_id, outlet_name, outlet_type, region, branch, payment_term_days)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(outlet_id) DO UPDATE SET
                    outlet_name=excluded.outlet_name,
                    outlet_type=excluded.outlet_type,
                    region=excluded.region,
                    branch=excluded.branch,
                    payment_term_days=excluded.payment_term_days;
            """, (o_id, name, o_type, region, branch, terms))
            imported_count += 1

    elif entity_type == "products":
        for r in reader:
            s_id = r.get("sku_id") or r.get("Kode SKU") or f"SKU-{imported_count+1:03d}"
            name = r.get("sku_name") or r.get("Nama SKU") or "SKU Baru"
            brand = r.get("brand") or r.get("Brand") or "Kacang Dua Kelinci"
            cat = r.get("category") or r.get("Kategori") or "Snack"
            pack = int(r.get("carton_pack_qty") or r.get("Isi Karton") or 24)
            het = float(r.get("price_het_idr") or r.get("HET") or 120000)
            ws = float(r.get("price_wholesale_idr") or r.get("Harga Grosir") or (het * 0.9))

            cur.execute("""
                INSERT INTO master_products (sku_id, sku_name, brand, category, carton_pack_qty, price_het_idr, price_wholesale_idr)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(sku_id) DO UPDATE SET
                    sku_name=excluded.sku_name,
                    brand=excluded.brand,
                    category=excluded.category,
                    carton_pack_qty=excluded.carton_pack_qty,
                    price_het_idr=excluded.price_het_idr,
                    price_wholesale_idr=excluded.price_wholesale_idr;
            """, (s_id, name, brand, cat, pack, het, ws))
            imported_count += 1

    elif entity_type == "warehouses":
        for r in reader:
            w_id = r.get("warehouse_id") or r.get("Kode Gudang") or f"WH-{imported_count+1:03d}"
            name = r.get("warehouse_name") or r.get("Nama Gudang") or "Gudang Cabang"
            region = r.get("region") or r.get("Wilayah") or "Nasional"
            branch = r.get("branch") or r.get("Cabang") or "Pusat"
            cap = int(r.get("capacity_carton") or r.get("Kapasitas") or 10000)

            cur.execute("""
                INSERT INTO master_warehouses (warehouse_id, warehouse_name, region, branch, capacity_carton)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(warehouse_id) DO UPDATE SET
                    warehouse_name=excluded.warehouse_name,
                    region=excluded.region,
                    branch=excluded.branch,
                    capacity_carton=excluded.capacity_carton;
            """, (w_id, name, region, branch, cap))
            imported_count += 1

    elif entity_type == "employees":
        for r in reader:
            e_id = r.get("employee_id") or r.get("NIP") or f"EMP-{imported_count+1:03d}"
            name = r.get("full_name") or r.get("Nama") or "Karyawan Baru"
            email = r.get("email") or f"{name.lower().replace(' ', '.')}@duakelinci.id"
            phone = r.get("phone") or r.get("No Telp") or "081200000000"
            dept = (r.get("department") or r.get("Departemen") or "SALES").upper()
            title = r.get("job_title") or r.get("Jabatan") or "Staff"
            role_type = (r.get("role_type") or r.get("Role") or "STAFF").upper()
            region = r.get("region") or r.get("Wilayah") or "Nasional"
            branch = r.get("branch") or r.get("Cabang") or "Pusat"
            wh_id = r.get("warehouse_id") or r.get("Kode Gudang") or None

            cur.execute("""
                INSERT INTO master_employees (
                    employee_id, full_name, email, phone, department, job_title, role_type, region, branch, warehouse_id, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE')
                ON CONFLICT(employee_id) DO UPDATE SET
                    full_name=excluded.full_name,
                    email=excluded.email,
                    phone=excluded.phone,
                    department=excluded.department,
                    job_title=excluded.job_title,
                    role_type=excluded.role_type,
                    region=excluded.region,
                    branch=excluded.branch,
                    warehouse_id=excluded.warehouse_id;
            """, (e_id, name, email, phone, dept, title, role_type, region, branch, wh_id))
            imported_count += 1

    conn.commit()
    conn.close()

    return {
        "success": True,
        "entity_type": entity_type,
        "imported_rows": imported_count,
        "message": f"Berhasil mengimpor {imported_count} baris data ke Master {entity_type.capitalize()}."
    }
