import json
import urllib.request
import sys

def send_adaptive_card_to_teams(webhook_url: str, card_payload: dict) -> dict:
    """
    Mengirim kartu laporan Adaptive Card ke Microsoft Teams melalui Webhook.
    Format pembungkus Teams Webhook:
    {
       "type": "message",
       "attachments": [
           {
               "contentType": "application/vnd.microsoft.card.adaptive",
               "content": card_payload
           }
       ]
    }
    """
    teams_envelope = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": card_payload
            }
        ]
    }

    req_data = json.dumps(teams_envelope).encode('utf-8')
    req = urllib.request.Request(
        webhook_url,
        data=req_data,
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            status_code = response.status
            resp_text = response.read().decode('utf-8')
            return {
                "success": True,
                "status_code": status_code,
                "response": resp_text
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
        print(f"Mencoba mengirim ke Webhook: {test_url[:35]}...")
        sample_card = {
            "type": "AdaptiveCard",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "text": "PT DUA KELINCI - UJI KONEKSI TEAMS",
                    "weight": "Bolder",
                    "color": "Attention"
                },
                {
                    "type": "TextBlock",
                    "text": "Halo Muhammad Wyzer, ini adalah pesan uji koneksi Microsoft Teams dari Platform Operasional Dua Kelinci."
                }
            ]
        }
        res = send_adaptive_card_to_teams(test_url, sample_card)
        print("Hasil kirim:", res)
    else:
        print("Modul pengirim Webhook Teams siap digunakan.")
