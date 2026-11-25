import csv
import sqlite3
import pathlib

ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent.parent.parent
DB_PATH = ROOT_DIR / "backend" / "data" / "kacang_dwh.db"

REGION_ALIASES = {
    "jabar": "Jawa Barat",
    "jawa barat": "Jawa Barat",
    "jabodetabek": "Jabodetabek",
    "jawa tengah": "Jawa Tengah",
    "jawa timur": "Jawa Timur",
    "kalimantan": "Kalimantan",
    "sumatera": "Sumatera",
}

def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS quarantine (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_file TEXT,
        row_number INTEGER,
        error_code TEXT,
        error_details TEXT,
        raw_data TEXT,
        created_at TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS fact_sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        invoice_no TEXT NOT NULL,
        entity_code TEXT NOT NULL,
        transaction_type TEXT NOT NULL,
        region TEXT NOT NULL,
        branch TEXT NOT NULL,
        outlet_id TEXT NOT NULL,
        outlet_name TEXT NOT NULL,
        outlet_type TEXT NOT NULL,
        salesman TEXT NOT NULL,
        brand TEXT NOT NULL,
        sku TEXT NOT NULL,
        qty_carton INTEGER NOT NULL,
        price_per_carton_idr REAL NOT NULL,
        gross_sales_idr REAL NOT NULL,
        discount_idr REAL NOT NULL,
        net_sales_idr REAL NOT NULL,
        UNIQUE (entity_code, invoice_no, sku)
    );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_sales_search ON fact_sales(region, branch, brand, date);")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS fact_stock (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        entity_code TEXT NOT NULL,
        region TEXT NOT NULL,
        branch TEXT NOT NULL,
        warehouse_id TEXT NOT NULL,
        warehouse_name TEXT NOT NULL,
        brand TEXT NOT NULL,
        sku TEXT NOT NULL,
        batch_no TEXT NOT NULL,
        expiry_date TEXT NOT NULL,
        qty_on_hand_carton INTEGER NOT NULL,
        qty_in_transit_carton INTEGER NOT NULL,
        qty_reserved_carton INTEGER NOT NULL,
        min_stock_carton INTEGER NOT NULL,
        cost_per_carton_idr REAL NOT NULL,
        stock_value_idr REAL NOT NULL,
        UNIQUE (entity_code, date, warehouse_id, sku, batch_no)
    );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_stock_search ON fact_stock(warehouse_id, sku, date);")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS fact_budget (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        period_month TEXT NOT NULL,
        entity_code TEXT NOT NULL,
        region TEXT NOT NULL,
        branch TEXT NOT NULL,
        brand TEXT NOT NULL,
        sku TEXT,
        budget_qty_carton INTEGER NOT NULL,
        budget_net_sales_idr REAL NOT NULL,
        UNIQUE (entity_code, period_month, branch, brand, sku)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_scope (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT NOT NULL,
        scope_type TEXT NOT NULL,
        scope_value TEXT NOT NULL
    );
    """)

    cur.execute("DELETE FROM user_scope;")
    users = [
        ("admin@duakelinci.id", "Budi Santoso", "admin", "NATIONAL", "ALL"),
        ("head.sales@duakelinci.id", "Rudi Hartono", "head_sales", "NATIONAL", "ALL"),
        ("bm.sukro@duakelinci.id", "Maya Indah", "brand_manager", "BRAND", "Sukro"),
        ("bm.dua_kelinci@duakelinci.id", "Andi Wijaya", "brand_manager", "BRAND", "Kacang Dua Kelinci"),
        ("hr.jabar@duakelinci.id", "Dedi Kurniawan", "head_region", "REGION", "Jawa Barat"),
        ("hr.jatim@duakelinci.id", "Siti Rahma", "head_region", "REGION", "Jawa Timur"),
        ("hr.jabodetabek@duakelinci.id", "Hendra Pratama", "head_region", "REGION", "Jabodetabek"),
    ]
    cur.executemany("INSERT INTO user_scope (email, full_name, role, scope_type, scope_value) VALUES (?, ?, ?, ?, ?);", users)

    conn.commit()
    conn.close()

def load_sales_csv():
    sales_file = ROOT_DIR / "csv" / "sales.csv"
    if not sales_file.exists():
        sales_file = ROOT_DIR / "sales.csv"
    if not sales_file.exists():
        print("sales.csv not found at", sales_file)
        return
    conn = get_connection()
    cur = conn.cursor()

    with open(sales_file, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        count = 0
        for i, row in enumerate(reader, start=2):
            raw_reg = row.get("region", "").strip()
            norm_reg = REGION_ALIASES.get(raw_reg.lower(), raw_reg)
            inv = row.get("invoice_no", "").strip()
            sku = row.get("sku", "").strip()
            salesman = row.get("salesman", "").strip() or "UNASSIGNED"
            try:
                qty = int(row.get("qty_carton", 0))
                price = float(row.get("price_per_carton_idr", 0))
                gross = float(row.get("gross_sales_idr", 0))
                discount = float(row.get("discount_idr", 0))
                net = float(row.get("net_sales_idr", 0))
            except ValueError as ve:
                cur.execute("""
                    INSERT INTO quarantine (source_file, row_number, error_code, error_details, raw_data, created_at)
                    VALUES (?, ?, ?, ?, ?, datetime('now'))
                """, ("sales.csv", i, "ERR_PARSE_NUMBER", str(ve), str(row)))
                continue

            tx_type = "RETURN" if inv.startswith("RTR") or qty < 0 else "SALE"

            cur.execute("""
                INSERT INTO fact_sales (
                    date, invoice_no, entity_code, transaction_type, region, branch,
                    outlet_id, outlet_name, outlet_type, salesman, brand, sku,
                    qty_carton, price_per_carton_idr, gross_sales_idr, discount_idr, net_sales_idr
                ) VALUES (?, ?, 'ID01', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(entity_code, invoice_no, sku) DO UPDATE SET
                    qty_carton = excluded.qty_carton,
                    net_sales_idr = excluded.net_sales_idr;
            """, (
                row.get("date", "").strip(), inv, tx_type, norm_reg, row.get("branch", "").strip(),
                row.get("outlet_id", "").strip(), row.get("outlet_name", "").strip(), row.get("outlet_type", "").strip(),
                salesman, row.get("brand", "").strip(), sku, qty, price, gross, discount, net
            ))
            count += 1
    conn.commit()
    conn.close()
    print("Loaded sales rows:", count)

def load_stock_csv():
    stock_file = ROOT_DIR / "csv" / "stock.csv"
    if not stock_file.exists():
        stock_file = ROOT_DIR / "stock.csv"
    if not stock_file.exists():
        print("stock.csv not found at", stock_file)
        return
    conn = get_connection()
    cur = conn.cursor()
    with open(stock_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        batch = []
        count = 0
        for r in reader:
            batch.append((
                r["date"], r["entity_code"], r["region"], r["branch"],
                r["warehouse_id"], r["warehouse_name"], r["brand"], r["sku"],
                r["batch_no"], r["expiry_date"], int(r["qty_on_hand_carton"]),
                int(r["qty_in_transit_carton"]), int(r["qty_reserved_carton"]),
                int(r["min_stock_carton"]), float(r["cost_per_carton_idr"]),
                float(r["stock_value_idr"])
            ))
            count += 1
            if len(batch) >= 1000:
                cur.executemany("""
                    INSERT INTO fact_stock (
                        date, entity_code, region, branch, warehouse_id, warehouse_name,
                        brand, sku, batch_no, expiry_date, qty_on_hand_carton,
                        qty_in_transit_carton, qty_reserved_carton, min_stock_carton,
                        cost_per_carton_idr, stock_value_idr
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(entity_code, date, warehouse_id, sku, batch_no) DO UPDATE SET
                        qty_on_hand_carton = excluded.qty_on_hand_carton,
                        stock_value_idr = excluded.stock_value_idr;
                """, batch)
                batch = []
        if batch:
            cur.executemany("""
                INSERT INTO fact_stock (
                    date, entity_code, region, branch, warehouse_id, warehouse_name,
                    brand, sku, batch_no, expiry_date, qty_on_hand_carton,
                    qty_in_transit_carton, qty_reserved_carton, min_stock_carton,
                    cost_per_carton_idr, stock_value_idr
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(entity_code, date, warehouse_id, sku, batch_no) DO UPDATE SET
                    qty_on_hand_carton = excluded.qty_on_hand_carton,
                    stock_value_idr = excluded.stock_value_idr;
            """, batch)
    conn.commit()
    conn.close()
    print("Loaded stock rows:", count)

def load_budget_csv():
    budget_file = ROOT_DIR / "csv" / "budget.csv"
    if not budget_file.exists():
        budget_file = ROOT_DIR / "budget.csv"
    if not budget_file.exists():
        print("budget.csv not found at", budget_file)
        return
    conn = get_connection()
    cur = conn.cursor()
    with open(budget_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        batch = []
        count = 0
        for r in reader:
            batch.append((
                r["period_month"], r["entity_code"], r["region"], r["branch"],
                r["brand"], r.get("sku", ""), int(r["budget_qty_carton"]),
                float(r["budget_net_sales_idr"])
            ))
            count += 1
        cur.executemany("""
            INSERT INTO fact_budget (
                period_month, entity_code, region, branch, brand, sku,
                budget_qty_carton, budget_net_sales_idr
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(entity_code, period_month, branch, brand, sku) DO UPDATE SET
                budget_net_sales_idr = excluded.budget_net_sales_idr;
        """, batch)
    conn.commit()
    conn.close()
    print("Loaded budget rows:", count)

def seed_all():
    init_db()
    load_sales_csv()
    load_stock_csv()
    load_budget_csv()

if __name__ == "__main__":
    seed_all()
