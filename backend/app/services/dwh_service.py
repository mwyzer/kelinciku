import sqlite3
import pathlib
from typing import Dict, Any, List, Optional

from app.db.connection import get_db, DB_PATH

def get_user_scope(email: str) -> Optional[Dict[str, Any]]:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM user_scope WHERE email = ?", (email,))
    row = cur.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def build_scope_filter(user: Optional[Dict[str, Any]], table_alias: str = "s") -> tuple[str, list]:
    conditions = []
    params = []
    if not user:
        return " 1=1 ", params

    scope_type = user.get("scope_type")
    scope_val = user.get("scope_value")

    if scope_type == "NATIONAL" or scope_val == "ALL":
        return " 1=1 ", params
    elif scope_type == "REGION":
        conditions.append(f"{table_alias}.region = ?")
        params.append(scope_val)
    elif scope_type == "BRANCH":
        conditions.append(f"{table_alias}.branch = ?")
        params.append(scope_val)
    elif scope_type == "BRAND":
        conditions.append(f"{table_alias}.brand = ?")
        params.append(scope_val)

    return " AND ".join(conditions) if conditions else " 1=1 ", params

def get_kpi_overview(
    user: Optional[Dict[str, Any]],
    start_date: str = "2026-09-01",
    end_date: str = "2026-10-31",
    region: Optional[str] = None,
    branch: Optional[str] = None,
    brand: Optional[str] = None
) -> Dict[str, Any]:
    conn = get_db()
    cur = conn.cursor()

    scope_sql, params = build_scope_filter(user, "s")
    where_clauses = [scope_sql, "s.date >= ?", "s.date <= ?"]
    params.extend([start_date, end_date])

    if region and region != "ALL":
        where_clauses.append("s.region = ?")
        params.append(region)
    if branch and branch != "ALL":
        where_clauses.append("s.branch = ?")
        params.append(branch)
    if brand and brand != "ALL":
        where_clauses.append("s.brand = ?")
        params.append(brand)

    where_str = " AND ".join(where_clauses)

    query_sales = f"""
    SELECT
        COALESCE(SUM(s.net_sales_idr), 0) as net_sales_idr,
        COALESCE(SUM(s.gross_sales_idr), 0) as gross_sales_idr,
        COALESCE(SUM(s.discount_idr), 0) as discount_idr,
        COALESCE(SUM(s.qty_carton), 0) as qty_carton,
        COUNT(DISTINCT s.invoice_no) as total_invoices,
        COUNT(DISTINCT s.outlet_id) as active_outlets
    FROM fact_sales s
    WHERE {where_str};
    """
    cur.execute(query_sales, params)
    sales_kpi = dict(cur.fetchone())

    # Budget Comparison
    budget_scope_sql, budget_params = build_scope_filter(user, "b")
    b_clauses = [budget_scope_sql]
    # Ambil bulan dari tanggal
    start_m = start_date[:7]
    end_m = end_date[:7]
    b_clauses.extend(["b.period_month >= ?", "b.period_month <= ?"])
    budget_params.extend([start_m, end_m])

    if region and region != "ALL":
        b_clauses.append("b.region = ?")
        budget_params.append(region)
    if branch and branch != "ALL":
        b_clauses.append("b.branch = ?")
        budget_params.append(branch)
    if brand and brand != "ALL":
        b_clauses.append("b.brand = ?")
        budget_params.append(brand)

    b_where_str = " AND ".join(b_clauses)
    query_budget = f"""
    SELECT
        COALESCE(SUM(b.budget_net_sales_idr), 0) as budget_net_sales_idr,
        COALESCE(SUM(b.budget_qty_carton), 0) as budget_qty_carton
    FROM fact_budget b
    WHERE {b_where_str};
    """
    cur.execute(query_budget, budget_params)
    budget_kpi = dict(cur.fetchone())

    net_sales = sales_kpi["net_sales_idr"]
    budget_sales = budget_kpi["budget_net_sales_idr"]
    ach_pct = round((net_sales / budget_sales * 100.0), 1) if budget_sales > 0 else 0.0
    discount_pct = round((sales_kpi["discount_idr"] / sales_kpi["gross_sales_idr"] * 100.0), 1) if sales_kpi["gross_sales_idr"] > 0 else 0.0

    # Critical stock count
    stock_scope_sql, stock_params = build_scope_filter(user, "st")
    st_clauses = [stock_scope_sql, "st.date = ?"]
    stock_params.append(end_date)
    if region and region != "ALL":
        st_clauses.append("st.region = ?")
        stock_params.append(region)
    if branch and branch != "ALL":
        st_clauses.append("st.branch = ?")
        stock_params.append(branch)
    if brand and brand != "ALL":
        st_clauses.append("st.brand = ?")
        stock_params.append(brand)

    st_where_str = " AND ".join(st_clauses)
    query_stock = f"""
    SELECT COUNT(*) as critical_stock_count
    FROM fact_stock st
    WHERE {st_where_str} AND st.qty_on_hand_carton < st.min_stock_carton;
    """
    cur.execute(query_stock, stock_params)
    crit_count = cur.fetchone()["critical_stock_count"]

    conn.close()

    return {
        "net_sales_idr": net_sales,
        "gross_sales_idr": sales_kpi["gross_sales_idr"],
        "discount_idr": sales_kpi["discount_idr"],
        "discount_pct": discount_pct,
        "qty_carton": sales_kpi["qty_carton"],
        "total_invoices": sales_kpi["total_invoices"],
        "active_outlets": sales_kpi["active_outlets"],
        "budget_net_sales_idr": budget_sales,
        "achievement_pct": ach_pct,
        "critical_stock_count": crit_count,
        "last_updated_wib": "2026-11-24 07:00 WIB"
    }

def get_daily_trends(
    user: Optional[Dict[str, Any]],
    start_date: str = "2026-09-01",
    end_date: str = "2026-10-31",
    region: Optional[str] = None,
    branch: Optional[str] = None,
    brand: Optional[str] = None
) -> List[Dict[str, Any]]:
    conn = get_db()
    cur = conn.cursor()

    scope_sql, params = build_scope_filter(user, "s")
    where_clauses = [scope_sql, "s.date >= ?", "s.date <= ?"]
    params.extend([start_date, end_date])

    if region and region != "ALL":
        where_clauses.append("s.region = ?")
        params.append(region)
    if branch and branch != "ALL":
        where_clauses.append("s.branch = ?")
        params.append(branch)
    if brand and brand != "ALL":
        where_clauses.append("s.brand = ?")
        params.append(brand)

    where_str = " AND ".join(where_clauses)
    query = f"""
    SELECT
        s.date,
        SUM(s.net_sales_idr) as net_sales_idr,
        SUM(s.qty_carton) as qty_carton
    FROM fact_sales s
    WHERE {where_str}
    GROUP BY s.date
    ORDER BY s.date ASC;
    """
    cur.execute(query, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def get_performance_breakdown(
    user: Optional[Dict[str, Any]],
    dimension: str = "brand",  # brand, sku, region, branch, outlet_type, salesman
    start_date: str = "2026-09-01",
    end_date: str = "2026-10-31",
    region: Optional[str] = None,
    branch: Optional[str] = None,
    brand: Optional[str] = None
) -> List[Dict[str, Any]]:
    conn = get_db()
    cur = conn.cursor()

    valid_dims = {"brand", "sku", "region", "branch", "outlet_type", "salesman"}
    if dimension not in valid_dims:
        dimension = "brand"

    scope_sql, params = build_scope_filter(user, "s")
    where_clauses = [scope_sql, "s.date >= ?", "s.date <= ?"]
    params.extend([start_date, end_date])

    if region and region != "ALL":
        where_clauses.append("s.region = ?")
        params.append(region)
    if branch and branch != "ALL":
        where_clauses.append("s.branch = ?")
        params.append(branch)
    if brand and brand != "ALL":
        where_clauses.append("s.brand = ?")
        params.append(brand)

    where_str = " AND ".join(where_clauses)
    query = f"""
    SELECT
        s.{dimension} as name,
        SUM(s.net_sales_idr) as net_sales_idr,
        SUM(s.qty_carton) as qty_carton,
        SUM(s.discount_idr) as discount_idr,
        COUNT(DISTINCT s.invoice_no) as invoices
    FROM fact_sales s
    WHERE {where_str}
    GROUP BY s.{dimension}
    ORDER BY net_sales_idr DESC;
    """
    cur.execute(query, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def get_stock_alerts(
    user: Optional[Dict[str, Any]],
    date: str = "2026-10-31",
    region: Optional[str] = None,
    branch: Optional[str] = None,
    brand: Optional[str] = None
) -> List[Dict[str, Any]]:
    conn = get_db()
    cur = conn.cursor()

    scope_sql, params = build_scope_filter(user, "st")
    where_clauses = [scope_sql, "st.date = ?"]
    params.append(date)

    if region and region != "ALL":
        where_clauses.append("st.region = ?")
        params.append(region)
    if branch and branch != "ALL":
        where_clauses.append("st.branch = ?")
        params.append(branch)
    if brand and brand != "ALL":
        where_clauses.append("st.brand = ?")
        params.append(brand)

    where_str = " AND ".join(where_clauses)
    query = f"""
    SELECT
        st.region,
        st.branch,
        st.warehouse_id,
        st.brand,
        st.sku,
        st.qty_on_hand_carton,
        st.min_stock_carton,
        (st.qty_on_hand_carton - st.min_stock_carton) as variance,
        st.expiry_date
    FROM fact_stock st
    WHERE {where_str} AND st.qty_on_hand_carton < st.min_stock_carton
    ORDER BY variance ASC;
    """
    cur.execute(query, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def get_filter_options(user: Optional[Dict[str, Any]]) -> Dict[str, List[str]]:
    conn = get_db()
    cur = conn.cursor()
    scope_sql, params = build_scope_filter(user, "s")

    cur.execute(f"SELECT DISTINCT s.region FROM fact_sales s WHERE {scope_sql} ORDER BY s.region", params)
    regions = [r[0] for r in cur.fetchall()]

    cur.execute(f"SELECT DISTINCT s.branch FROM fact_sales s WHERE {scope_sql} ORDER BY s.branch", params)
    branches = [r[0] for r in cur.fetchall()]

    cur.execute(f"SELECT DISTINCT s.brand FROM fact_sales s WHERE {scope_sql} ORDER BY s.brand", params)
    brands = [r[0] for r in cur.fetchall()]

    conn.close()
    return {
        "regions": ["ALL"] + regions,
        "branches": ["ALL"] + branches,
        "brands": ["ALL"] + brands
    }
