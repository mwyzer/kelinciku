import sqlite3
import pathlib

def generate_postgres_sql():
    db_path = pathlib.Path("backend/data/kacang_dwh.db")
    if not db_path.exists():
        print(f"Error: {db_path} does not exist")
        return

    sqlite_conn = sqlite3.connect(str(db_path))
    sqlite_conn.row_factory = sqlite3.Row
    cur = sqlite_conn.cursor()

    out_file = pathlib.Path("docker/postgres/init-duakelinci.sql")
    out_file.parent.mkdir(parents=True, exist_ok=True)

    with open(out_file, "w", encoding="utf-8") as f:
        f.write("-- Inisialisasi Database PostgreSQL PT Dua Kelinci Ops\n")
        f.write('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";\n\n')

        ddl = """-- 1. quarantine
CREATE TABLE IF NOT EXISTS quarantine (
    id SERIAL PRIMARY KEY,
    source_file VARCHAR(255),
    row_number INTEGER,
    error_code VARCHAR(100),
    error_details TEXT,
    raw_data TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. user_scope
CREATE TABLE IF NOT EXISTS user_scope (
    id SERIAL PRIMARY KEY,
    email VARCHAR(150) UNIQUE NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    role VARCHAR(50) NOT NULL,
    scope_type VARCHAR(50) NOT NULL,
    scope_value VARCHAR(100) NOT NULL
);

-- 3. master_products
CREATE TABLE IF NOT EXISTS master_products (
    sku_id VARCHAR(100) PRIMARY KEY,
    sku_name VARCHAR(200) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL,
    carton_pack_qty INTEGER DEFAULT 24,
    price_het_idr DOUBLE PRECISION NOT NULL,
    price_wholesale_idr DOUBLE PRECISION NOT NULL,
    shelf_life_days INTEGER DEFAULT 365,
    status VARCHAR(50) DEFAULT 'ACTIVE'
);

-- 4. master_outlets
CREATE TABLE IF NOT EXISTS master_outlets (
    outlet_id VARCHAR(100) PRIMARY KEY,
    outlet_name VARCHAR(200) NOT NULL,
    outlet_type VARCHAR(100) NOT NULL,
    region VARCHAR(100) NOT NULL,
    branch VARCHAR(100) NOT NULL,
    payment_term_days INTEGER DEFAULT 14,
    status VARCHAR(50) DEFAULT 'ACTIVE'
);

-- 5. master_warehouses
CREATE TABLE IF NOT EXISTS master_warehouses (
    warehouse_id VARCHAR(100) PRIMARY KEY,
    warehouse_name VARCHAR(200) NOT NULL,
    region VARCHAR(100) NOT NULL,
    branch VARCHAR(100) NOT NULL,
    capacity_carton INTEGER DEFAULT 10000,
    status VARCHAR(50) DEFAULT 'ACTIVE'
);

-- 6. fact_sales
CREATE TABLE IF NOT EXISTS fact_sales (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    invoice_no VARCHAR(100) NOT NULL,
    entity_code VARCHAR(50) NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    region VARCHAR(100) NOT NULL,
    branch VARCHAR(100) NOT NULL,
    outlet_id VARCHAR(100) NOT NULL,
    outlet_name VARCHAR(200) NOT NULL,
    outlet_type VARCHAR(100) NOT NULL,
    salesman VARCHAR(100) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    sku VARCHAR(100) NOT NULL,
    qty_carton INTEGER NOT NULL,
    price_per_carton_idr DOUBLE PRECISION NOT NULL,
    gross_sales_idr DOUBLE PRECISION NOT NULL,
    discount_idr DOUBLE PRECISION NOT NULL,
    net_sales_idr DOUBLE PRECISION NOT NULL,
    CONSTRAINT uq_sales_item UNIQUE (entity_code, invoice_no, sku)
);

-- 7. fact_stock
CREATE TABLE IF NOT EXISTS fact_stock (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    entity_code VARCHAR(50) NOT NULL,
    region VARCHAR(100) NOT NULL,
    branch VARCHAR(100) NOT NULL,
    warehouse_id VARCHAR(100) NOT NULL,
    warehouse_name VARCHAR(200) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    sku VARCHAR(100) NOT NULL,
    batch_no VARCHAR(100) NOT NULL,
    expiry_date DATE NOT NULL,
    qty_on_hand_carton INTEGER NOT NULL,
    qty_in_transit_carton INTEGER NOT NULL,
    qty_reserved_carton INTEGER NOT NULL,
    min_stock_carton INTEGER NOT NULL,
    cost_per_carton_idr DOUBLE PRECISION NOT NULL,
    stock_value_idr DOUBLE PRECISION NOT NULL,
    CONSTRAINT uq_stock_batch UNIQUE (entity_code, date, warehouse_id, sku, batch_no)
);

-- 8. fact_budget
CREATE TABLE IF NOT EXISTS fact_budget (
    id SERIAL PRIMARY KEY,
    period_month VARCHAR(20) NOT NULL,
    entity_code VARCHAR(50) NOT NULL,
    region VARCHAR(100) NOT NULL,
    branch VARCHAR(100) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    sku VARCHAR(100),
    budget_qty_carton INTEGER NOT NULL,
    budget_net_sales_idr DOUBLE PRECISION NOT NULL,
    CONSTRAINT uq_budget_period UNIQUE (entity_code, period_month, branch, brand, sku)
);

-- 9. wms_movements
CREATE TABLE IF NOT EXISTS wms_movements (
    id SERIAL PRIMARY KEY,
    movement_type VARCHAR(50) NOT NULL,
    reference_no VARCHAR(100) NOT NULL,
    warehouse_id VARCHAR(100) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    sku VARCHAR(100) NOT NULL,
    batch_no VARCHAR(100) NOT NULL,
    expiry_date DATE NOT NULL,
    qty_carton INTEGER NOT NULL,
    operator_name VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 10. esign_documents
CREATE TABLE IF NOT EXISTS esign_documents (
    id VARCHAR(100) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    department VARCHAR(100) NOT NULL,
    doc_type VARCHAR(100) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    amount_idr DOUBLE PRECISION DEFAULT 0,
    sha256_hash VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    current_step INTEGER DEFAULT 1,
    total_steps INTEGER NOT NULL,
    created_by VARCHAR(150) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- 11. esign_signers
CREATE TABLE IF NOT EXISTS esign_signers (
    id SERIAL PRIMARY KEY,
    doc_id VARCHAR(100) NOT NULL REFERENCES esign_documents(id) ON DELETE CASCADE,
    signer_email VARCHAR(150) NOT NULL,
    signer_name VARCHAR(150) NOT NULL,
    department VARCHAR(100) NOT NULL,
    role_title VARCHAR(100) NOT NULL,
    step_order INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL,
    signed_at TIMESTAMP WITH TIME ZONE,
    ip_address VARCHAR(50),
    rejection_reason TEXT
);

-- 12. esign_audit_trail
CREATE TABLE IF NOT EXISTS esign_audit_trail (
    id SERIAL PRIMARY KEY,
    doc_id VARCHAR(100) NOT NULL,
    action VARCHAR(100) NOT NULL,
    actor_email VARCHAR(150) NOT NULL,
    actor_name VARCHAR(150) NOT NULL,
    department VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    details TEXT
);
"""
        f.write(ddl + "\n\n")

        def sql_val(v):
            if v is None:
                return "NULL"
            if isinstance(v, (int, float)):
                return str(v)
            s = str(v).replace("'", "''")
            return f"'{s}'"

        tables_to_dump = [
            "user_scope",
            "master_products",
            "master_outlets",
            "master_warehouses",
            "fact_sales",
            "fact_stock",
            "fact_budget",
            "esign_documents",
            "esign_signers",
            "esign_audit_trail"
        ]

        for tbl in tables_to_dump:
            cur.execute(f"SELECT * FROM {tbl}")
            rows = cur.fetchall()
            if not rows:
                continue
            cols = [d[0] for d in cur.description]
            col_list = ", ".join(cols)
            f.write(f"-- Seed data for {tbl} ({len(rows)} rows)\n")
            for r in rows:
                val_list = ", ".join([sql_val(r[c]) for c in cols])
                f.write(f"INSERT INTO {tbl} ({col_list}) VALUES ({val_list}) ON CONFLICT DO NOTHING;\n")
            f.write("\n")

    print(f"Postgres seed successfully created at: {out_file}")

if __name__ == "__main__":
    generate_postgres_sql()
