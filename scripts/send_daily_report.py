import os
import sys
import datetime
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.services.dwh_service import get_user_scope, get_kpi_overview
from app.services.email_service import generate_email_html, send_executive_email_via_smtp

def run_daily_email_report(recipient_email: str = "muhammad.wyzer@gmail.com"):
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Memulai pengiriman laporan email harian ke: {recipient_email}")
    
    # Ambil profil user & wewenang RLS
    user = get_user_scope(recipient_email)
    if not user:
        user = {
            "email": recipient_email,
            "full_name": "Muhammad Wyzer",
            "role": "head_sales",
            "scope_type": "NATIONAL",
            "scope_value": "ALL"
        }
    
    # Ambil KPI snapshot terkini
    kpi = get_kpi_overview(user=user, start_date="2026-09-01", end_date="2026-10-31")
    
    # Generate HTML profesional
    html_content = generate_email_html(
        kpi=kpi,
        recipient_name=user.get("full_name", "Head of Department"),
        recipient_email=recipient_email
    )
    
    subject = f"PT Dua Kelinci - Ringkasan Eksekutif Operasional Harian ({datetime.datetime.now().strftime('%d %B %Y')})"
    
    # Kirim via SMTP SSL
    result = send_executive_email_via_smtp(
        to_email=recipient_email,
        subject=subject,
        html_body=html_content
    )
    
    print("Hasil Pengiriman:", result)
    return result

if __name__ == "__main__":
    email_target = sys.argv[1] if len(sys.argv) > 1 else "muhammad.wyzer@gmail.com"
    run_daily_email_report(email_target)
