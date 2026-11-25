import json
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional

def get_latest_chat_id(bot_token: str) -> Dict[str, Any]:
    """
    Mengambil pesan masuk terakhir (getUpdates) dari bot
    untuk mendeteksi chat_id numerik pengirim yang baru saja menekan /start.
    """
    url = f"https://api.telegram.org/bot{bot_token.strip()}/getUpdates"
    req = urllib.request.Request(url, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res_body = response.read().decode("utf-8")
            data = json.loads(res_body)
            results = data.get("result", [])
            if not results:
                return {
                    "success": False,
                    "message": "Belum ada pesan yang masuk ke bot ini. Silakan buka bot Anda di Telegram dan ketik /start terlebih dahulu."
                }
            # Ambil update terakhir
            last_msg = results[-1].get("message") or results[-1].get("channel_post") or {}
            chat = last_msg.get("chat", {})
            return {
                "success": True,
                "chat_id": str(chat.get("id")),
                "username": chat.get("username", "N/A"),
                "first_name": chat.get("first_name", "N/A"),
                "type": chat.get("type", "private")
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

def send_telegram_message(
    bot_token: str,
    chat_id: str,
    text: str,
    parse_mode: str = "HTML",
    reply_markup: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Mengirim pesan langsung ke akun/grup Telegram via BotFather API.
    Dapat menyertakan tombol interaktif Inline Keyboard (Approve / Reject).
    """
    url = f"https://api.telegram.org/bot{bot_token.strip()}/sendMessage"
    payload: Dict[str, Any] = {
        "chat_id": chat_id.strip(),
        "text": text,
        "parse_mode": parse_mode
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res_body = response.read().decode("utf-8")
            return {
                "success": True,
                "status": "SENT_VIA_BOT",
                "response": json.loads(res_body)
            }
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        return {
            "success": False,
            "status": "HTTP_ERROR",
            "code": e.code,
            "error": err_msg
        }
    except Exception as e:
        return {
            "success": False,
            "status": "CONNECTION_ERROR",
            "error": str(e)
        }

def send_esign_telegram_request(
    bot_token: str,
    chat_id: str,
    doc: Dict[str, Any],
    recipient_name: str,
    recipient_email: str,
    base_url: str = "http://127.0.0.1:8000"
) -> Dict[str, Any]:
    """
    Mengirimkan dokumen permohonan e-Signature HOD langsung ke Telegram dengan tombol
    Inline Keyboard: 'Tandatangani (Setujui)' dan 'Tolak (Reject)'.
    """
    doc_id = doc["id"]
    title = doc.get("title", "Dokumen Otorisasi HOD")
    dept = doc.get("department", "SALES")
    amount = doc.get("amount_idr", 0)
    amount_str = f"Rp {amount:,.0f}" if amount else "Non-Finansial"
    step = doc.get("current_step", 1)
    total = doc.get("total_steps", 1)
    sha256 = doc.get("sha256_hash", "")[:24]

    text = (
        f"📝 <b>PERMOHONAN OTORISASI E-SIGNATURE (HOD)</b>\n"
        f"<b>PT Dua Kelinci</b>\n\n"
        f"Yth. <b>{recipient_name}</b>,\n"
        f"Dokumen berikut membutuhkan persetujuan digital resmi Anda (Tahap {step} dari {total}):\n\n"
        f"• <b>Judul:</b> {title}\n"
        f"• <b>Departemen:</b> {dept}\n"
        f"• <b>Estimasi Nilai:</b> {amount_str}\n"
        f"• <b>Hash SHA-256:</b> <code>{sha256}...</code>\n\n"
        f"Silakan klik salah satu tombol tindakan di bawah ini:"
    )

    approve_url = f"{base_url}/api/v1/esign/email-action?doc_id={doc_id}&email={recipient_email}&action=APPROVE"
    reject_url = f"{base_url}/api/v1/esign/email-action?doc_id={doc_id}&email={recipient_email}&action=REJECT"

    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "✅ TANDATANGANI (SETUJUI)", "url": approve_url},
                {"text": "❌ TOLAK (REJECT)", "url": reject_url}
            ],
            [
                {"text": "🌐 Buka Portal Operasional", "url": base_url}
            ]
        ]
    }

    return send_telegram_message(
        bot_token=bot_token,
        chat_id=chat_id,
        text=text,
        parse_mode="HTML",
        reply_markup=reply_markup
    )

