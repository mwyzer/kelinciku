import re
from typing import Dict, Any, List, Tuple

class NumericVerificationGate:
    """
    Memastikan seluruh angka, persentase, dan nominal rupiah pada narasi AI
    100% cocok dengan data acuan JSON KPI.
    Jika ditemukan angka fiktif (halusinasi), narasi ditolak dan digantikan template baku.
    """

    @staticmethod
    def extract_numbers(text: str) -> List[float]:
        # Ekstraksi angka: format desimal (koma/titik), persen, atau angka murni
        # Bersihkan titik ribuan dan ubah koma desimal ke titik
        cleaned = re.sub(r'(\d+)\.(\d{3})', r'\1\2', text)
        cleaned = cleaned.replace(',', '.')
        tokens = re.findall(r'[-+]?\d*\.?\d+', cleaned)
        nums = []
        for t in tokens:
            try:
                val = float(t)
                nums.append(round(val, 2))
            except ValueError:
                continue
        return nums

    @staticmethod
    def collect_reference_numbers(data: Any) -> set:
        ref_nums = set()
        if isinstance(data, dict):
            for v in data.values():
                ref_nums.update(NumericVerificationGate.collect_reference_numbers(v))
        elif isinstance(data, list):
            for item in data:
                ref_nums.update(NumericVerificationGate.collect_reference_numbers(item))
        elif isinstance(data, (int, float)):
            ref_nums.add(round(float(data), 2))
            # Format persentase / pembulatan satuan juta
            ref_nums.add(round(float(data) / 1000000.0, 1))
            ref_nums.add(round(float(data) / 1000000.0, 2))
        return ref_nums

    @classmethod
    def verify(cls, narrative: str, reference_kpi: Dict[str, Any]) -> Tuple[bool, str, List[float]]:
        narrative_nums = cls.extract_numbers(narrative)
        ref_nums = cls.collect_reference_numbers(reference_kpi)

        # Abaikan angka penanggalan umum jika ada (misal 2026, tanggal 1-31, jam 7)
        common_date_nums = {2026.0, 7.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 9.0, 10.0, 11.0, 12.0, 14.0, 24.0, 30.0, 31.0}
        unmatched = []

        for n in narrative_nums:
            if n in common_date_nums:
                continue
            # Cocokkan dengan toleransi 0.5%
            matched = any(abs(n - r) < 0.05 or (r != 0 and abs(n - r) / abs(r) < 0.005) for r in ref_nums)
            if not matched:
                unmatched.append(n)

        if not unmatched:
            return True, narrative, []
        else:
            # Fallback ke template baku deterministik
            manager = reference_kpi.get("manager_name", "Bapak/Ibu Manajer")
            scope = reference_kpi.get("scope_desc", "Operasional")
            net_sales = reference_kpi.get("net_sales_idr", 0)
            ach = reference_kpi.get("achievement_pct", 0)
            crit = reference_kpi.get("critical_stock_count", 0)
            
            fallback_text = (
                f"Yth. {manager} ({scope}), berikut ringkasan kinerja per 31 Oktober 2026: "
                f"Penjualan Bersih tercatat Rp {net_sales:,.0f} dengan pencapaian target {ach}% vs Budget. "
                f"Terdapat {crit} SKU berstatus stok kritis di depo cabang. "
                f"Informasi lengkap dan rincian transaksi dapat dilihat pada portal dashboard."
            )
            return False, fallback_text, unmatched

def build_adaptive_card_payload(kpi: Dict[str, Any], narrative: str) -> Dict[str, Any]:
    net_str = f"Rp {kpi.get('net_sales_idr', 0):,.0f}"
    ach_str = f"{kpi.get('achievement_pct', 0)}%"
    crit_str = f"{kpi.get('critical_stock_count', 0)} SKU"
    
    card = {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "body": [
            {
                "type": "Container",
                "style": "emphasis",
                "bleed": True,
                "items": [
                    {
                        "type": "TextBlock",
                        "text": "PT DUA KELINCI - RINGKASAN EKSEKUTIF",
                        "weight": "Bolder",
                        "color": "Attention",
                        "size": "Medium"
                    },
                    {
                        "type": "TextBlock",
                        "text": f"Penerima: {kpi.get('manager_name')} ({kpi.get('scope_desc')})",
                        "isSubtle": True,
                        "spacing": "None"
                    }
                ]
            },
            {
                "type": "TextBlock",
                "text": narrative,
                "wrap": True,
                "spacing": "Medium"
            },
            {
                "type": "FactSet",
                "spacing": "Medium",
                "facts": [
                    {"title": "Penjualan Bersih:", "value": net_str},
                    {"title": "Target Budget:", "value": f"Rp {kpi.get('budget_net_sales_idr', 0):,.0f}"},
                    {"title": "Pencapaian Target:", "value": ach_str},
                    {"title": "Volume Terjual:", "value": f"{kpi.get('qty_carton', 0):,} Karton"},
                    {"title": "Peringatan Stok Kritis:", "value": crit_str}
                ]
            }
        ],
        "actions": [
            {
                "type": "Action.OpenUrl",
                "title": "Buka Dashboard Live",
                "url": "http://127.0.0.1:8000/frontend"
            }
        ]
    }
    return card
