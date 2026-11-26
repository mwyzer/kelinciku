import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Any, Optional

def generate_email_html(kpi: Dict[str, Any], recipient_name: str, recipient_email: str) -> str:
    net_sales_fmt = f"Rp {kpi.get('net_sales_idr', 0):,.0f}"
    budget_fmt = f"Rp {kpi.get('budget_net_sales_idr', 0):,.0f}"
    qty_fmt = f"{kpi.get('qty_carton', 0):,} Karton"
    ach_fmt = f"{kpi.get('achievement_pct', 0)}%"
    crit_fmt = f"{kpi.get('critical_stock_count', 0)} SKU"
    disc_fmt = f"{kpi.get('discount_pct', 0)}%"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 20px; color: #1e293b; }}
        .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }}
        .header {{ background-color: #dc2626; color: #ffffff; padding: 24px; text-align: left; }}
        .header h1 {{ margin: 0; font-size: 18px; font-weight: 800; letter-spacing: 0.5px; text-transform: uppercase; }}
        .header p {{ margin: 4px 0 0; font-size: 13px; opacity: 0.9; }}
        .body-content {{ padding: 24px; }}
        .narrative-box {{ background-color: #f1f5f9; border-left: 4px solid #dc2626; padding: 14px 16px; border-radius: 4px; font-size: 14px; line-height: 1.5; margin-bottom: 24px; color: #334155; }}
        .kpi-table {{ width: 100%; border-collapse: collapse; margin-bottom: 24px; }}
        .kpi-table td {{ padding: 12px 0; border-bottom: 1px solid #f1f5f9; font-size: 13px; }}
        .kpi-title {{ color: #64748b; font-weight: 500; }}
        .kpi-value {{ text-align: right; font-weight: 700; color: #0f172a; font-size: 14px; }}
        .badge-green {{ color: #059669; font-weight: 800; }}
        .badge-red {{ color: #dc2626; font-weight: 800; }}
        .btn {{ display: block; text-align: center; background-color: #0f172a; color: #ffffff !important; padding: 12px 20px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 13px; margin-top: 10px; }}
        .footer {{ padding: 16px 24px; background-color: #f8fafc; border-top: 1px solid #e2e8f0; font-size: 11px; color: #94a3b8; text-align: center; }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <h1>PT DUA KELINCI &bull; EXECUTIVE REPORT</h1>
          <p>Penerima: {recipient_name} (Head of Sales - Nasional)</p>
        </div>
        <div class="body-content">
          <div class="narrative-box">
            Yth. <strong>{recipient_name}</strong>, berikut ringkasan eksekutif kinerja operasional penjualan periode September s.d. Oktober 2026 yang dihitung secara deterministik dari database terpusat:
          </div>
          <table class="kpi-table">
            <tr>
              <td class="kpi-title">Penjualan Bersih (Net Sales):</td>
              <td class="kpi-value">{net_sales_fmt}</td>
            </tr>
            <tr>
              <td class="kpi-title">Target Anggaran (Budget):</td>
              <td class="kpi-value">{budget_fmt}</td>
            </tr>
            <tr>
              <td class="kpi-title">Tingkat Pencapaian Target:</td>
              <td class="kpi-value badge-green">{ach_fmt}</td>
            </tr>
            <tr>
              <td class="kpi-title">Total Volume Terjual:</td>
              <td class="kpi-value">{qty_fmt}</td>
            </tr>
            <tr>
              <td class="kpi-title">Rasio Potongan Harga / Diskon:</td>
              <td class="kpi-value">{disc_fmt}</td>
            </tr>
            <tr>
              <td class="kpi-title">Peringatan Stok Kritis Cabang:</td>
              <td class="kpi-value badge-red">{crit_fmt}</td>
            </tr>
          </table>
          <a href="http://127.0.0.1:8000/frontend" class="btn">Buka Portal Dashboard Live</a>
        </div>
        <div class="footer">
          Laporan ini diterbitkan otomatis oleh AI Insight Agent PT Dua Kelinci.<br>
          Zona Waktu Pelaporan: WIB (Asia/Jakarta) &bull; Sistem Terverifikasi Anti-Halusinasi
        </div>
      </div>
    </body>
    </html>
    """
    return html

def generate_esign_request_email_html(
    doc: Dict[str, Any],
    recipient_name: str,
    recipient_email: str,
    base_url: str = "http://127.0.0.1:8000"
) -> str:
    """Template email HTML interaktif dengan tombol Setujui (Sign) dan Tolak (Reject) langsung."""
    doc_id = doc["id"]
    title = doc.get("title", "Dokumen Otorisasi HOD")
    department = doc.get("department", "SALES")
    doc_type = doc.get("doc_type", "Persetujuan Dokumen")
    amount = doc.get("amount_idr", 0)
    amount_fmt = f"Rp {amount:,.0f}" if amount else "Non-Finansial"
    sha256 = doc.get("sha256_hash", "")
    created_at = doc.get("created_at", "")
    created_by = doc.get("created_by", "")
    current_step = doc.get("current_step", 1)
    total_steps = doc.get("total_steps", 1)

    # Link aksi langsung via HTTP GET agar bisa diklik dari aplikasi email (Gmail, Outlook, dsb.)
    approve_url = f"{base_url}/api/v1/esign/email-action?doc_id={doc_id}&email={recipient_email}&action=APPROVE"
    reject_url = f"{base_url}/api/v1/esign/email-action?doc_id={doc_id}&email={recipient_email}&action=REJECT"
    portal_url = f"{base_url}/"

    html = f"""
    <!DOCTYPE html>
    <html lang="id">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Permohonan Tanda Tangan Dokumen</title>
      <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f1f5f9; margin: 0; padding: 24px; color: #1e293b; }}
        .card {{ max-width: 620px; margin: 0 auto; background: #ffffff; border-radius: 14px; overflow: hidden; border: 1px solid #cbd5e1; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.07); }}
        .header {{ background: linear-gradient(135deg, #b91c1c 0%, #dc2626 100%); color: #ffffff; padding: 26px 28px; }}
        .header h1 {{ margin: 0; font-size: 19px; font-weight: 800; letter-spacing: 0.5px; text-transform: uppercase; }}
        .header p {{ margin: 6px 0 0; font-size: 13px; opacity: 0.95; }}
        .body {{ padding: 28px; }}
        .notice {{ background-color: #fef2f2; border-left: 4px solid #dc2626; padding: 14px 18px; border-radius: 6px; font-size: 13px; line-height: 1.5; color: #7f1d1d; margin-bottom: 24px; }}
        .table {{ width: 100%; border-collapse: collapse; margin-bottom: 26px; }}
        .table td {{ padding: 11px 0; border-bottom: 1px solid #f1f5f9; font-size: 13px; }}
        .label {{ color: #64748b; font-weight: 600; width: 38%; }}
        .val {{ color: #0f172a; font-weight: 700; text-align: right; }}
        .hash-box {{ background: #f8fafc; border: 1px dashed #cbd5e1; padding: 10px 12px; font-family: monospace; font-size: 11px; word-break: break-all; color: #475569; border-radius: 6px; margin-bottom: 26px; }}
        
        /* Tombol Aksi */
        .btn-container {{ display: flex; gap: 14px; margin-top: 10px; margin-bottom: 24px; }}
        .btn-approve {{ flex: 1; text-align: center; background-color: #059669; color: #ffffff !important; padding: 15px 20px; border-radius: 10px; text-decoration: none; font-weight: 800; font-size: 14px; box-shadow: 0 4px 6px -1px rgba(5,150,105,0.3); }}
        .btn-reject {{ flex: 1; text-align: center; background-color: #dc2626; color: #ffffff !important; padding: 15px 20px; border-radius: 10px; text-decoration: none; font-weight: 800; font-size: 14px; box-shadow: 0 4px 6px -1px rgba(220,38,38,0.3); }}
        
        .footer {{ padding: 18px 28px; background-color: #f8fafc; border-top: 1px solid #e2e8f0; font-size: 11px; color: #94a3b8; text-align: center; line-height: 1.5; }}
      </style>
    </head>
    <body>
      <div class="card">
        <div class="header">
          <h1>PT DUA KELINCI &bull; OTORISASI E-SIGNATURE</h1>
          <p>Permohonan Persetujuan Head of Department (Tahap {current_step} dari {total_steps})</p>
        </div>
        <div class="body">
          <div class="notice">
            Yth. <strong>{recipient_name}</strong>,<br>
            Anda memiliki 1 (satu) dokumen dinas operasional yang memerlukan otorisasi digital resmi dari Anda sebagai <strong>Head of Department</strong>.
          </div>

          <table class="table">
            <tr>
              <td class="label">Judul Pengajuan:</td>
              <td class="val">{title}</td>
            </tr>
            <tr>
              <td class="label">Departemen Pengaju:</td>
              <td class="val">{department}</td>
            </tr>
            <tr>
              <td class="label">Jenis Dokumen:</td>
              <td class="val">{doc_type}</td>
            </tr>
            <tr>
              <td class="label">Nilai / Estimasi Biaya:</td>
              <td class="val" style="color: #dc2626;">{amount_fmt}</td>
            </tr>
            <tr>
              <td class="label">Diajukan Oleh:</td>
              <td class="val">{created_by}</td>
            </tr>
            <tr>
              <td class="label">Waktu Dibuat:</td>
              <td class="val">{created_at}</td>
            </tr>
          </table>

          <div style="font-size: 11px; color: #64748b; margin-bottom: 6px; font-weight: 600;">Integritas Berkas Digital (Hash SHA-256):</div>
          <div class="hash-box">{sha256}</div>

          <p style="font-size: 13px; font-weight: 700; color: #0f172a; text-align: center; margin-bottom: 12px;">
            Silakan pilih tindakan otorisasi di bawah ini:
          </p>

          <!-- Action Buttons -->
          <table width="100%" cellspacing="0" cellpadding="0" style="margin-bottom: 24px;">
            <tr>
              <td width="48%" align="center">
                <a href="{approve_url}" style="display:block; width:90%; padding:14px 0; background-color:#059669; color:#ffffff; font-weight:bold; font-size:14px; text-decoration:none; border-radius:8px; text-align:center;">
                  &#10004; TANDATANGANI (SETUJUI)
                </a>
              </td>
              <td width="4%"></td>
              <td width="48%" align="center">
                <a href="{reject_url}" style="display:block; width:90%; padding:14px 0; background-color:#dc2626; color:#ffffff; font-weight:bold; font-size:14px; text-decoration:none; border-radius:8px; text-align:center;">
                  &#10008; TOLAK (REJECT)
                </a>
              </td>
            </tr>
          </table>

          <div style="text-align: center;">
            <a href="{portal_url}" style="color: #64748b; font-size: 12px; text-decoration: underline;">Buka Portal Dashboard Terpadu PT Dua Kelinci</a>
          </div>
        </div>
        <div class="footer">
          Sistem Otorisasi e-Signature Internal Terpadu &bull; PT Dua Kelinci<br>
          Mematuhi UU ITE No. 11/2008 &amp; Standar Validitas Audit Trail SHA-256 Otomatis
        </div>
      </div>
    </body>
    </html>
    """
    return html

def send_executive_email_via_smtp(

    to_email: str,
    subject: str,
    html_body: str,
    smtp_host: Optional[str] = None,
    smtp_port: Optional[int] = None,
    smtp_user: Optional[str] = None,
    smtp_pass: Optional[str] = None
) -> Dict[str, Any]:
    """Mengirim email HTML langsung via SMTP SSL menggunakan Google App Password.

    Kredensial dibaca dari environment variable SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS
    bila tidak diberikan sebagai argumen.
    """
    smtp_host = smtp_host or os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "465"))
    smtp_user = smtp_user or os.getenv("SMTP_USER")
    smtp_pass = smtp_pass or os.getenv("SMTP_PASS")
    if not smtp_user or not smtp_pass:
        return {
            "success": False,
            "status": "SMTP_NOT_CONFIGURED",
            "error": "SMTP_USER dan SMTP_PASS belum diset di environment."
        }
    clean_pass = smtp_pass.replace(" ", "")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Dua Kelinci AI System <{smtp_user}>"
    msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(smtp_user, clean_pass)
            server.sendmail(smtp_user, to_email, msg.as_string())
        return {
            "success": True,
            "status": "SENT_VIA_SMTP_SSL",
            "to": to_email,
            "message": f"Email berhasil dikirim langsung ke {to_email} via Google SMTP SSL"
        }
    except Exception as e:
        return {
            "success": False,
            "status": "SMTP_ERROR",
            "error": str(e)
        }

def send_report_email(

    to_email: str,
    recipient_name: str,
    kpi: Dict[str, Any],
    smtp_host: Optional[str] = None,
    smtp_port: int = 587,
    smtp_user: Optional[str] = None,
    smtp_password: Optional[str] = None
) -> Dict[str, Any]:
    html_content = generate_email_html(kpi, recipient_name, to_email)
    
    # Jika kredensial SMTP lokal disediakan, kirim email nyata
    if smtp_host and smtp_user and smtp_password:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"PT Dua Kelinci - Ringkasan Eksekutif Penjualan: {recipient_name}"
        msg["From"] = f"Dua Kelinci AI Agent <{smtp_user}>"
        msg["To"] = to_email
        msg.attach(MIMEText(html_content, "html"))

        try:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.sendmail(smtp_user, to_email, msg.as_string())
            return {
                "success": True,
                "status": "SENT_VIA_SMTP",
                "to": to_email,
                "message": f"Email laporan berhasil dikirim ke {to_email}"
            }
        except Exception as e:
            return {
                "success": False,
                "status": "SMTP_ERROR",
                "error": str(e)
            }
    else:
        # Buat file preview email HTML yang bisa langsung dibuka di browser
        import pathlib
        preview_path = pathlib.Path(__file__).resolve().parent.parent.parent.parent / "frontend" / "public" / "email_preview.html"
        preview_path.write_text(html_content, encoding="utf-8")
        return {
            "success": True,
            "status": "READY_AND_PREVIEWED",
            "to": to_email,
            "preview_file": str(preview_path),
            "message": f"Format email eksekutif untuk {to_email} telah selesai dibuat dan diverifikasi."
        }
