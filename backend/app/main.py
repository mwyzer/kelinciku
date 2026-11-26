from fastapi import FastAPI, Depends, Header, HTTPException, Query, Body, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse, HTMLResponse
import os
import pathlib
import datetime
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
import urllib.request
import json

from app.services import dwh_service
from app.services import agent_service
from app.services import forecast_service
from app.services import esign_service
from app.services import wms_service
from app.services import email_service
from app.services import telegram_service
from app.services import master_data_service
from app.services import ops_service
from app.services import sales_route_service
from app.services import iot_service

app = FastAPI(
    title="Kacang Dua Kelinci - Operational Platform API",
    version="0.2.1",
    description="API untuk Dashboard Live, AI Insight Agent, Forecasting, e-Signature, dan WMS Gudang"
)

_default_origins = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001"
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", _default_origins).split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-User-Email", "Authorization"],
)

def get_current_user(x_user_email: Optional[str] = Header(None, alias="X-User-Email")) -> Dict[str, Any]:
    """Identitas user dari header X-User-Email (simulasi SSO sampai SSO asli terpasang).

    Tidak ada lagi fallback ke akses NATIONAL: header wajib dan email harus terdaftar di user_scope.
    """
    email = (x_user_email or "").strip().lower()
    if not email:
        raise HTTPException(status_code=401, detail="Header X-User-Email wajib diisi.")
    user = dwh_service.get_user_scope(email)
    if not user:
        raise HTTPException(status_code=403, detail=f"User {email} tidak terdaftar di user_scope.")
    return user

# --- HEALTH & AUTH ---
frontend_path = pathlib.Path(__file__).resolve().parent.parent.parent / "frontend" / "public" / "index.html"
sales_brief_path = pathlib.Path(__file__).resolve().parent.parent.parent / "frontend" / "public" / "sales_brief.html"

@app.get("/")
def root():
    if frontend_path.exists():
        return FileResponse(frontend_path)
    return RedirectResponse(url="/docs")

@app.get("/sales-brief")
def get_sales_brief():
    if sales_brief_path.exists():
        return FileResponse(sales_brief_path)
    raise HTTPException(status_code=404, detail="File sales_brief.html tidak ditemukan")

@app.get("/api/v1/health")
def health_check():
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        conn = dwh_service.get_db()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.fetchone()
        conn.close()
        db_status = "pass"
    except Exception as e:
        db_status = f"fail: {e}"
    status = "pass" if db_status == "pass" else "fail"
    return {"status": status, "version": app.version, "timestamp": now, "checks": {"database": db_status}}

@app.get("/api/v1/auth/me")
def get_profile(user: Dict[str, Any] = Depends(get_current_user)):
    return user

# --- DASHBOARD & KPI ---
@app.get("/api/v1/dashboard/filters")
def get_filters(user: Dict[str, Any] = Depends(get_current_user)):
    return dwh_service.get_filter_options(user)

@app.get("/api/v1/dashboard/overview")
def get_overview(
    start_date: str = Query("2026-09-01"),
    end_date: str = Query("2026-10-31"),
    region: Optional[str] = Query(None),
    branch: Optional[str] = Query(None),
    brand: Optional[str] = Query(None),
    user: Dict[str, Any] = Depends(get_current_user)
):
    return dwh_service.get_kpi_overview(
        user=user,
        start_date=start_date,
        end_date=end_date,
        region=region,
        branch=branch,
        brand=brand
    )

@app.get("/api/v1/dashboard/charts/daily-trend")
def get_daily_trend(
    start_date: str = Query("2026-09-01"),
    end_date: str = Query("2026-10-31"),
    region: Optional[str] = Query(None),
    branch: Optional[str] = Query(None),
    brand: Optional[str] = Query(None),
    user: Dict[str, Any] = Depends(get_current_user)
):
    return dwh_service.get_daily_trends(
        user=user,
        start_date=start_date,
        end_date=end_date,
        region=region,
        branch=branch,
        brand=brand
    )

@app.get("/api/v1/dashboard/breakdown/{dimension}")
def get_breakdown(
    dimension: str,
    start_date: str = Query("2026-09-01"),
    end_date: str = Query("2026-10-31"),
    region: Optional[str] = Query(None),
    branch: Optional[str] = Query(None),
    brand: Optional[str] = Query(None),
    user: Dict[str, Any] = Depends(get_current_user)
):
    return dwh_service.get_performance_breakdown(
        user=user,
        dimension=dimension,
        start_date=start_date,
        end_date=end_date,
        region=region,
        branch=branch,
        brand=brand
    )

@app.get("/api/v1/dashboard/alerts/stock")
def get_stock_alerts(
    date: str = Query("2026-10-31"),
    region: Optional[str] = Query(None),
    branch: Optional[str] = Query(None),
    brand: Optional[str] = Query(None),
    user: Dict[str, Any] = Depends(get_current_user)
):
    return dwh_service.get_stock_alerts(
        user=user,
        date=date,
        region=region,
        branch=branch,
        brand=brand
    )

@app.get("/api/v1/dashboard/export")
def export_sales(
    start_date: str = Query("2026-09-01"),
    end_date: str = Query("2026-10-31"),
    region: Optional[str] = Query(None),
    branch: Optional[str] = Query(None),
    brand: Optional[str] = Query(None),
    user: Dict[str, Any] = Depends(get_current_user)
):
    conn = dwh_service.get_db()
    cur = conn.cursor()
    scope_sql, params = dwh_service.build_scope_filter(user, "s")
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
    cur.execute(f"""
        SELECT date, invoice_no, transaction_type, region, branch, outlet_name,
               outlet_type, salesman, brand, sku, qty_carton, price_per_carton_idr,
               gross_sales_idr, discount_idr, net_sales_idr
        FROM fact_sales s
        WHERE {where_str}
        ORDER BY date DESC LIMIT 500;
    """, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

@app.post("/api/v1/dashboard/import-sales-csv")
def import_sales_csv_endpoint(payload: Dict[str, Any] = Body(...)):
    """
    Import file sales.csv atau data transaksi penjualan baru langsung ke fact_sales DWH.
    """
    import csv
    import io
    csv_content = payload.get("csv_content", "").strip()
    if not csv_content:
        raise HTTPException(status_code=400, detail="Isi file CSV tidak boleh kosong.")
    
    f = io.StringIO(csv_content)
    reader = csv.DictReader(f)
    conn = dwh_service.get_db()
    cur = conn.cursor()
    imported_count = 0
    
    for r in reader:
        try:
            date = r.get("date") or r.get("Tanggal") or "2026-10-31"
            inv_no = r.get("invoice_no") or r.get("No Faktur") or f"INV-IMP-{imported_count+1:05d}"
            entity = r.get("entity_code") or r.get("Entitas") or "DK-HO"
            t_type = r.get("transaction_type") or r.get("Tipe") or "SALES_ORDER"
            reg = r.get("region") or r.get("Wilayah") or "Jawa Barat"
            branch = r.get("branch") or r.get("Cabang") or "Bandung"
            o_id = r.get("outlet_id") or r.get("Kode Outlet") or "OUT-DEFAULT"
            o_name = r.get("outlet_name") or r.get("Nama Outlet") or "Outlet Umum"
            o_type = r.get("outlet_type") or r.get("Tipe Outlet") or "Toko Kelontong"
            salesman = r.get("salesman") or r.get("Salesman") or "Budi Santoso"
            brand = r.get("brand") or r.get("Brand") or "Kacang Dua Kelinci"
            sku = r.get("sku") or r.get("SKU") or "Kacang Garing 200g"
            qty = int(float(r.get("qty_carton") or r.get("Qty") or 1))
            price = float(r.get("price_per_carton_idr") or r.get("Harga") or 120000)
            gross = float(r.get("gross_sales_idr") or r.get("Gross") or (qty * price))
            disc = float(r.get("discount_idr") or r.get("Diskon") or 0)
            net = float(r.get("net_sales_idr") or r.get("Net") or (gross - disc))

            cur.execute("""
                INSERT INTO fact_sales (
                    date, invoice_no, entity_code, transaction_type, region, branch,
                    outlet_id, outlet_name, outlet_type, salesman, brand, sku,
                    qty_carton, price_per_carton_idr, gross_sales_idr, discount_idr, net_sales_idr
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(entity_code, invoice_no, sku) DO UPDATE SET
                    qty_carton = excluded.qty_carton,
                    gross_sales_idr = excluded.gross_sales_idr,
                    discount_idr = excluded.discount_idr,
                    net_sales_idr = excluded.net_sales_idr;
            """, (date, inv_no, entity, t_type, reg, branch, o_id, o_name, o_type, salesman, brand, sku, qty, price, gross, disc, net))
            imported_count += 1
        except Exception as ex:
            continue

    conn.commit()
    conn.close()
    return {
        "success": True,
        "imported_rows": imported_count,
        "message": f"Berhasil mengimpor {imported_count} baris transaksi penjualan ke fact_sales DWH."
    }

# --- AI INSIGHT AGENT & TEAMS DISPATCH ---
@app.get("/api/v1/agent/preview-summary")
def preview_agent_summary(user: Dict[str, Any] = Depends(get_current_user)):
    kpi = dwh_service.get_kpi_overview(user=user, start_date="2026-09-01", end_date="2026-10-31")
    kpi["manager_name"] = user["full_name"]
    kpi["scope_desc"] = f"{user['role'].upper()} - {user['scope_value']}"

    draft_narrative = (
        f"Halo {user['full_name']}, kinerja penjualan periode September-Oktober 2026 mencapai "
        f"Rp {kpi['net_sales_idr']:,.0f} dengan target achievement {kpi['achievement_pct']}%. "
        f"Saat ini teridentifikasi {kpi['critical_stock_count']} SKU berada di bawah stok aman."
    )

    is_valid, final_narrative, unmatched = agent_service.NumericVerificationGate.verify(draft_narrative, kpi)
    card_payload = agent_service.build_adaptive_card_payload(kpi, final_narrative)

    return {
        "status": "SUCCESS",
        "verification_passed": is_valid,
        "unmatched_numbers": unmatched,
        "narrative": final_narrative,
        "adaptive_card": card_payload
    }

@app.post("/api/v1/agent/send-teams")
def send_teams_report(
    webhook_url: Optional[str] = Body(None, embed=True),
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Mengirimkan Adaptive Card ke Microsoft Teams Webhook atau mencatat antrean dispatch.
    Jika webhook_url diberikan, HTTP POST dikirimkan ke Teams.
    """
    summary = preview_agent_summary(user)
    card = summary["adaptive_card"]

    dispatch_result = {
        "recipient_name": user["full_name"],
        "recipient_email": user["email"],
        "delivery_channel": "Microsoft Teams",
        "timestamp_wib": "2026-11-24 11:55:00 WIB",
        "status": "DISPATCHED"
    }

    if webhook_url and webhook_url.startswith("http"):
        try:
            req = urllib.request.Request(
                webhook_url,
                data=json.dumps(card).encode('utf-8'),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                dispatch_result["http_status"] = resp.status
                dispatch_result["status"] = "DELIVERED_TO_WEBHOOK"
        except Exception as ex:
            dispatch_result["status"] = "WEBHOOK_FAILED"
            dispatch_result["error"] = str(ex)
    else:
        # Simulasi pengiriman terintegrasi ke inbox user
        dispatch_result["status"] = "QUEUED_FOR_DELIVERY"
        dispatch_result["note"] = f"Pesan telah diantrekan untuk akun Teams {user['email']}. Menunggu konfigurasi Microsoft Teams Webhook URL resmi."

    return {
        "success": True,
        "dispatch_details": dispatch_result,
        "card_payload": card
    }

# --- FORECASTING ENGINE ---
@app.get("/api/v1/forecast/demand")
def get_demand_forecast(
    horizon_days: int = Query(14),
    region: Optional[str] = Query("ALL"),
    brand: Optional[str] = Query("ALL"),
    user: Dict[str, Any] = Depends(get_current_user)
):
    eff_region = user["scope_value"] if user["scope_type"] == "REGION" else (region or "ALL")
    eff_brand = user["scope_value"] if user["scope_type"] == "BRAND" else (brand or "ALL")
    return forecast_service.forecast_sales_and_stock(horizon_days, eff_region, eff_brand)

# --- E-SIGNATURE INTERNAL & HOD WORKFLOW ---
@app.get("/api/v1/esign/documents")
def list_esign_docs():
    return esign_service.list_all_hod_documents()

@app.post("/api/v1/esign/hod-documents")
def create_hod_doc(payload: Dict[str, Any] = Body(...), user: Dict[str, Any] = Depends(get_current_user)):
    return esign_service.create_hod_document(
        title=payload.get("title", "Dokumen Persetujuan HOD"),
        department=payload.get("department", "SALES"),
        doc_type=payload.get("doc_type", "MEMO"),
        file_name=payload.get("file_name", "memo.pdf"),
        amount_idr=float(payload.get("amount_idr", 0)),
        created_by=user["email"],
        created_by_name=user.get("full_name", user["email"]),
        target_departments=payload.get("target_departments", ["SALES", "MARKETING", "FINANCE"])
    )

@app.post("/api/v1/esign/seed-demo")
def seed_esign_demo():
    esign_service.seed_demo_hod_documents()
    return {"message": "Demo HOD documents seeded"}

@app.post("/api/v1/esign/documents")
def create_esign_doc(payload: Dict[str, Any] = Body(...), user: Dict[str, Any] = Depends(get_current_user)):
    return esign_service.create_document(
        title=payload.get("title", "Dokumen Baru"),
        doc_type=payload.get("doc_type", "MEMO"),
        file_name=payload.get("file_name", "memo.pdf"),
        created_by=user["email"],
        signers=payload.get("signers", [{"email": user["email"], "name": user["full_name"]}])
    )

@app.post("/api/v1/esign/documents/{doc_id}/sign")
def sign_doc(doc_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    return esign_service.sign_document(
        doc_id=doc_id,
        signer_email=user["email"],
        signer_name=user["full_name"],
        ip_address="127.0.0.1"
    )

# --- EMAIL INTERACTIVE SIGN / REJECT ENDPOINTS ---
@app.get("/api/v1/esign/email-action", response_class=HTMLResponse)
def handle_email_action(
    doc_id: str = Query(...),
    email: str = Query(...),
    action: str = Query(...) # APPROVE atau REJECT
):
    doc = esign_service.get_document_by_id(doc_id)
    if not doc:
        return HTMLResponse(content="<h2>Dokumen tidak ditemukan atau telah dihapus.</h2>", status_code=404)

    user_info = esign_service.HOD_DIRECTORY.get(
        doc.get("department", "SALES"),
        {"name": "Head of Department", "email": email, "title": "Head of Department"}
    )
    actor_name = user_info["name"]

    if action == "APPROVE":
        res = esign_service.sign_hod_document(doc_id=doc_id, actor_email=email, actor_name=actor_name, ip_address="Email-Client-Action")
        is_success = res.get("success", False)
        status_msg = res.get("message", "Tanda tangan digital berhasil dibubuhkan.")
        theme_color = "#059669" if is_success else "#dc2626"
        icon = "&#10004;" if is_success else "&#10008;"
        title_badge = "DOKUMEN BERHASIL DITANDATANGANI" if is_success else "GAGAL MENANDATANGANI"
    else:
        res = esign_service.reject_hod_document(doc_id=doc_id, actor_email=email, actor_name=actor_name, reason="Ditolak langsung via tombol email", ip_address="Email-Client-Action")
        is_success = res.get("success", False)
        status_msg = res.get("message", "Dokumen telah resmi ditolak.")
        theme_color = "#dc2626"
        icon = "&#10008;"
        title_badge = "DOKUMEN TELAH DITOLAK (REJECTED)"

    html_resp = f"""
    <!DOCTYPE html>
    <html lang="id">
    <head>
      <meta charset="utf-8">
      <title>Konfirmasi Tindakan e-Signature</title>
      <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8fafc; padding: 40px 20px; text-align: center; color: #1e293b; }}
        .card {{ max-width: 520px; margin: 0 auto; background: #fff; padding: 36px 30px; border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 10px 20px -5px rgba(0,0,0,0.06); }}
        .icon-circle {{ width: 68px; height: 68px; border-radius: 50%; background: {theme_color}18; color: {theme_color}; display: flex; align-items: center; justify-content: center; font-size: 32px; font-weight: bold; margin: 0 auto 20px; }}
        h1 {{ font-size: 19px; margin-bottom: 8px; color: {theme_color}; }}
        p {{ font-size: 14px; color: #64748b; line-height: 1.5; }}
        .doc-box {{ background: #f8fafc; border: 1px solid #e2e8f0; padding: 14px; border-radius: 8px; font-size: 13px; text-align: left; margin: 20px 0; }}
        .btn {{ display: inline-block; background: #0f172a; color: #ffffff !important; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-size: 13px; font-weight: 600; margin-top: 10px; }}
      </style>
    </head>
    <body>
      <div class="card">
        <div class="icon-circle">{icon}</div>
        <h1>{title_badge}</h1>
        <p>{status_msg}</p>

        <div class="doc-box">
          <div><strong>Judul:</strong> {doc.get('title')}</div>
          <div><strong>Departemen:</strong> {doc.get('department')}</div>
          <div><strong>Hash SHA-256:</strong> <span style="font-family:monospace; font-size:11px;">{doc.get('sha256_hash')[:24]}...</span></div>
          <div><strong>Status Akhir:</strong> <strong>{res.get('document_status', doc.get('status'))}</strong></div>
        </div>

        <a href="/" class="btn">Kembali ke Portal Operasional</a>
      </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_resp)

@app.post("/api/v1/esign/send-approval-email")
def send_approval_email(payload: Dict[str, Any] = Body(...)):
    doc_id = payload.get("doc_id")
    target_email = payload.get("email", "muhammad.wyzer@gmail.com")
    doc = esign_service.get_document_by_id(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Dokumen tidak ditemukan")

    user_info = esign_service.HOD_DIRECTORY.get("SALES", {"name": "Muhammad Wyzer"})
    html_content = email_service.generate_esign_request_email_html(
        doc=doc,
        recipient_name=user_info.get("name", "Head of Department"),
        recipient_email=target_email,
        base_url="http://127.0.0.1:8000"
    )

    subject = f"PT Dua Kelinci - Permohonan Otorisasi e-Signature: {doc.get('title')}"
    res = email_service.send_executive_email_via_smtp(
        to_email=target_email,
        subject=subject,
        html_body=html_content
    )
    return res

@app.post("/api/v1/esign/send-telegram-request")
def send_esign_telegram(payload: Dict[str, Any] = Body(...)):
    doc_id = payload.get("doc_id")
    bot_token = payload.get("bot_token")
    chat_id = payload.get("chat_id", "6190060235")
    user_email = payload.get("email", "muhammad.wyzer@gmail.com")

    if not doc_id or not bot_token or not chat_id:
        raise HTTPException(status_code=400, detail="doc_id, bot_token, dan chat_id wajib diisi.")

    doc = esign_service.get_document_by_id(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Dokumen tidak ditemukan")

    user_info = esign_service.HOD_DIRECTORY.get("SALES", {"name": "Muhammad Wyzer"})
    res = telegram_service.send_esign_telegram_request(
        bot_token=bot_token,
        chat_id=chat_id,
        doc=doc,
        recipient_name=user_info.get("name", "Head of Department"),
        recipient_email=user_email,
        base_url="http://127.0.0.1:8000"
    )
    return res


# --- TELEGRAM BOT INTEGRATION ---
@app.post("/api/v1/telegram/send")
def send_telegram_bot_message(payload: Dict[str, Any] = Body(...)):
    bot_token = payload.get("bot_token")
    chat_id = payload.get("chat_id")
    text = payload.get("text")

    if not bot_token or not chat_id or not text:
        raise HTTPException(status_code=400, detail="bot_token, chat_id, dan text wajib diisi.")

    res = telegram_service.send_telegram_message(
        bot_token=bot_token,
        chat_id=chat_id,
        text=text
    )
    return res

@app.get("/api/v1/telegram/detect-chat-id")
def detect_telegram_chat_id(bot_token: str = Query(...)):
    return telegram_service.get_latest_chat_id(bot_token)





# --- WMS GUDANG ENHANCED (INBOUND, OUTBOUND, OPNAME, BARCODE, SINKRON QAD) ---
@app.get("/api/v1/wms/fefo-recommendation")
def get_fefo_recommendation(
    warehouse_id: str = Query("WH-BDG"),
    sku: str = Query("Sukro Pedas 100g"),
    qty: int = Query(50)
):
    return wms_service.get_fefo_picking_recommendation(warehouse_id, sku, qty)

@app.get("/api/v1/wms/transactions")
def get_wms_transactions(warehouse_id: Optional[str] = Query(None), transaction_type: Optional[str] = Query(None)):
    return wms_service.list_inventory_transactions(warehouse_id, transaction_type)

@app.post("/api/v1/wms/inbound")
def post_wms_inbound(payload: Dict[str, Any] = Body(...)):
    return wms_service.record_inbound_goods(payload)

@app.post("/api/v1/wms/outbound")
def post_wms_outbound(payload: Dict[str, Any] = Body(...)):
    return wms_service.record_outbound_goods(payload)

@app.get("/api/v1/wms/barcode-lookup")
def get_barcode_lookup(barcode: str = Query(...)):
    return wms_service.lookup_barcode(barcode)

@app.get("/api/v1/wms/opname/sessions")
def get_opname_sessions(warehouse_id: Optional[str] = Query(None)):
    return wms_service.list_opname_sessions(warehouse_id)

@app.post("/api/v1/wms/opname/sessions")
def post_opname_session(payload: Dict[str, Any] = Body(...)):
    return wms_service.create_opname_session(payload)

@app.post("/api/v1/wms/opname/submit-count")
def post_opname_count(payload: Dict[str, Any] = Body(...)):
    item_id = int(payload.get("item_id", 0))
    physical_qty = int(payload.get("physical_qty_carton", 0))
    barcode = payload.get("barcode")
    counter_email = payload.get("counter_email", "surya.picker@duakelinci.id")
    return wms_service.update_opname_item_count(item_id, physical_qty, barcode, counter_email)

@app.post("/api/v1/wms/qad/trigger-sync")
def post_trigger_qad_sync():
    return wms_service.sync_pending_to_qad()

# --- RUTE SALES LAPANGAN & GEOFENCING (CALL PLAN, CHECK-IN GPS, TO) ---
@app.get("/api/v1/sales-route/daily-plan")
def get_sales_daily_plan(salesman_email: str = Query("budi.santoso@duakelinci.id"), plan_date: Optional[str] = Query(None)):
    return sales_route_service.get_daily_call_plan(salesman_email, plan_date)

@app.post("/api/v1/sales-route/check-in")
def post_sales_route_check_in(payload: Dict[str, Any] = Body(...)):
    return sales_route_service.process_sales_check_in(payload)

@app.post("/api/v1/sales-route/check-out")
def post_sales_route_check_out(payload: Dict[str, Any] = Body(...)):
    visit_id = int(payload.get("visit_id", 0))
    return sales_route_service.process_sales_check_out(visit_id, payload)

# --- IOT PABRIK SHOP FLOOR MONITORING (SENSOR, DASHBOARD, ALERT, OEE) ---
@app.get("/api/v1/iot/live-status")
def get_iot_live_status():
    return iot_service.get_live_shopfloor_status()

@app.get("/api/v1/iot/devices/health")
def get_iot_devices_health():
    return iot_service.get_iot_devices_health()

@app.post("/api/v1/iot/telemetry/ingest")
def post_iot_telemetry(payload: Dict[str, Any] = Body(...)):
    try:
        return iot_service.ingest_sensor_telemetry_enhanced(payload)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except iot_service.IoTNotFound as le:
        raise HTTPException(status_code=404, detail=str(le))

@app.get("/api/v1/iot/telemetry/history")
def get_iot_telemetry_history(machine_id: Optional[str] = None, limit: int = Query(500, ge=1, le=5000)):
    return iot_service.get_telemetry_history(machine_id, limit)

@app.get("/api/v1/iot/machines")
def get_iot_machines(production_line: Optional[str] = None):
    return iot_service.list_machines(production_line)

@app.get("/api/v1/iot/machines/{machine_id}")
def get_iot_machine_detail(machine_id: str):
    try:
        return iot_service.get_machine_detail(machine_id)
    except iot_service.IoTNotFound as le:
        raise HTTPException(status_code=404, detail=str(le))

@app.get("/api/v1/iot/devices")
def get_iot_devices():
    return iot_service.get_iot_devices_health()

@app.get("/api/v1/iot/alerts")
def get_iot_alerts(status: Optional[str] = None, machine_id: Optional[str] = None,
                   alert_type: Optional[str] = None, limit: int = Query(200, ge=1, le=2000)):
    return iot_service.list_alerts(status, machine_id, alert_type, limit)

@app.get("/api/v1/iot/alerts/active")
def get_iot_alerts_active():
    return iot_service.list_alerts("ACTIVE")

@app.post("/api/v1/iot/health-check")
def post_iot_health_check():
    return iot_service.run_health_check()

@app.post("/api/v1/iot/oee/calculate")
def post_iot_oee_calculate(payload: Dict[str, Any] = Body(...)):
    try:
        shift = iot_service.current_shift()
        return iot_service.calculate_oee(
            payload["machine_id"],
            payload.get("production_date") or shift["production_date"],
            int(payload.get("shift_no") or shift["shift_no"]),
        )
    except KeyError:
        raise HTTPException(status_code=400, detail="machine_id wajib diisi.")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except iot_service.IoTNotFound as le:
        raise HTTPException(status_code=404, detail=str(le))

@app.get("/api/v1/iot/oee-summary")
def get_iot_oee_summary(date_from: Optional[str] = None, date_to: Optional[str] = None):
    return iot_service.get_oee_summary(date_from, date_to)

@app.get("/api/v1/iot/oee-report")
def get_iot_oee_report(date_from: Optional[str] = None, date_to: Optional[str] = None,
                       machine_id: Optional[str] = None, shift_id: Optional[int] = None,
                       production_line: Optional[str] = None):
    return iot_service.get_oee_report(date_from, date_to, machine_id, shift_id, production_line)

@app.get("/api/v1/iot/production-summary")
def get_iot_production_summary(production_date: Optional[str] = None):
    return iot_service.get_production_summary(production_date)

@app.get("/api/v1/iot/production-report")
def get_iot_production_report(date_from: Optional[str] = None, date_to: Optional[str] = None,
                              machine_id: Optional[str] = None):
    return iot_service.get_production_report(date_from, date_to, machine_id)

@app.get("/api/v1/iot/downtime-report")
def get_iot_downtime_report(date_from: Optional[str] = None, date_to: Optional[str] = None,
                            machine_id: Optional[str] = None):
    return iot_service.get_downtime_report(date_from, date_to, machine_id)

def _iot_background_loop():
    """Health check (DEVICE_OFFLINE, UNSCHEDULED_DOWNTIME) + hitung ulang OEE shift berjalan, tiap 60 detik."""
    import time
    interval = int(os.getenv("IOT_MONITOR_INTERVAL_SECONDS", "60"))
    while True:
        time.sleep(interval)
        try:
            iot_service.run_health_check()
            iot_service.recalculate_current_shift_oee()
        except Exception as ex:
            print(f"[IoT] background loop error: {ex}")

@app.on_event("startup")
def _start_iot_monitor():
    if os.getenv("IOT_MONITOR_ENABLED", "true").lower() in ("1", "true", "yes"):
        import threading
        threading.Thread(target=_iot_background_loop, daemon=True, name="iot-monitor").start()

@app.patch("/api/v1/iot/alerts/{alert_id}/acknowledge")
def patch_acknowledge_alert(alert_id: str, payload: Dict[str, Any] = Body(...)):
    ack_by = payload.get("acknowledged_by", "teknisi.shift@duakelinci.id")
    return iot_service.acknowledge_iot_alert(alert_id, ack_by)

@app.patch("/api/v1/iot/alerts/{alert_id}/resolve")
def patch_resolve_alert(alert_id: str, payload: Dict[str, Any] = Body(...)):
    resolved_by = payload.get("resolved_by", "bambang.teknisi@duakelinci.id")
    notes = payload.get("resolution_notes", "Perbaikan sensor dan pendinginan mesin telah selesai.")
    return iot_service.resolve_iot_alert_enhanced(alert_id, resolved_by, notes)

@app.post("/api/v1/iot/alerts/{alert_id}/resolve")
def post_resolve_iot_alert(alert_id: str):
    return iot_service.resolve_iot_alert_enhanced(alert_id, "teknisi.shift@duakelinci.id", "Selesai ditangani")



# --- MASTER DATA MANAGEMENT (MDM) ---
@app.get("/api/v1/master/products")
def get_master_products():
    return master_data_service.list_products()

@app.post("/api/v1/master/products")
def create_product_endpoint(payload: Dict[str, Any] = Body(...)):
    try:
        return master_data_service.create_product(payload)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@app.put("/api/v1/master/products/{sku_id}")
def update_product_endpoint(sku_id: str, payload: Dict[str, Any] = Body(...)):
    return master_data_service.update_product(sku_id, payload)

@app.delete("/api/v1/master/products/{sku_id}")
def delete_product_endpoint(sku_id: str):
    return master_data_service.delete_product(sku_id)

@app.get("/api/v1/master/outlets")
def get_master_outlets():
    return master_data_service.list_outlets()

@app.get("/api/v1/master/outlets/transactions")
def get_master_outlet_transactions():
    return master_data_service.list_outlet_transactions()

@app.post("/api/v1/master/outlets")
def create_outlet_endpoint(payload: Dict[str, Any] = Body(...)):
    try:
        return master_data_service.create_outlet(payload)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@app.put("/api/v1/master/outlets/{outlet_id}")
def update_outlet_endpoint(outlet_id: str, payload: Dict[str, Any] = Body(...)):
    return master_data_service.update_outlet(outlet_id, payload)

@app.delete("/api/v1/master/outlets/{outlet_id}")
def delete_outlet_endpoint(outlet_id: str):
    return master_data_service.delete_outlet(outlet_id)

@app.get("/api/v1/master/warehouses")
def get_master_warehouses():
    return master_data_service.list_warehouses()

@app.post("/api/v1/master/warehouses")
def create_warehouse_endpoint(payload: Dict[str, Any] = Body(...)):
    try:
        return master_data_service.create_warehouse(payload)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@app.put("/api/v1/master/warehouses/{warehouse_id}")
def update_warehouse_endpoint(warehouse_id: str, payload: Dict[str, Any] = Body(...)):
    return master_data_service.update_warehouse(warehouse_id, payload)

@app.delete("/api/v1/master/warehouses/{warehouse_id}")
def delete_warehouse_endpoint(warehouse_id: str):
    return master_data_service.delete_warehouse(warehouse_id)

# --- MASTER KARYAWAN (SALES & WAREHOUSE) ---
@app.get("/api/v1/master/employees")
def get_master_employees(department: Optional[str] = Query(None)):
    return master_data_service.list_employees(department)

@app.post("/api/v1/master/employees")
def create_employee_endpoint(payload: Dict[str, Any] = Body(...)):
    try:
        return master_data_service.create_employee(payload)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@app.put("/api/v1/master/employees/{employee_id}")
def update_employee_endpoint(employee_id: str, payload: Dict[str, Any] = Body(...)):
    return master_data_service.update_employee(employee_id, payload)

@app.delete("/api/v1/master/employees/{employee_id}")
def delete_employee_endpoint(employee_id: str):
    return master_data_service.delete_employee(employee_id)

@app.post("/api/v1/master/import-csv")
def import_csv_endpoint(payload: Dict[str, Any] = Body(...)):
    entity_type = payload.get("entity_type", "outlets")
    csv_content = payload.get("csv_content", "")
    if not csv_content:
        raise HTTPException(status_code=400, detail="Isi file CSV tidak boleh kosong.")
    return master_data_service.import_master_csv(entity_type, csv_content)

# --- OPERATIONAL: FIELD SALES VISITS & GEOFENCING ---
@app.get("/api/v1/ops/visits")
def get_sales_visits(salesman_email: Optional[str] = Query(None)):
    return ops_service.list_sales_visits(salesman_email)

@app.post("/api/v1/ops/visits/check-in")
def check_in_sales_visit(payload: Dict[str, Any] = Body(...)):
    return ops_service.create_sales_check_in(payload)

@app.post("/api/v1/ops/visits/{visit_id}/complete")
def complete_sales_visit_endpoint(visit_id: int, payload: Dict[str, Any] = Body(...)):
    return ops_service.complete_sales_visit(visit_id, payload)

# --- OPERATIONAL: WAREHOUSE STOCK TRANSFERS ---
@app.get("/api/v1/ops/transfers")
def get_stock_transfers(status: Optional[str] = Query(None)):
    return ops_service.list_stock_transfers(status)

@app.post("/api/v1/ops/transfers")
def create_stock_transfer_endpoint(payload: Dict[str, Any] = Body(...)):
    return ops_service.create_stock_transfer(payload)

@app.post("/api/v1/ops/transfers/{transfer_no}/receive")
def receive_stock_transfer_endpoint(transfer_no: str):
    return ops_service.receive_stock_transfer(transfer_no)




