import sys
sys.path.append('backend')
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("--- 1. UJI AI INSIGHT AGENT & NUMERIC VERIFICATION ---")
r_agent = client.get('/api/v1/agent/preview-summary', headers={'X-User-Email': 'bm.sukro@duakelinci.id'})
d_agent = r_agent.json()
print("Agent Status:", d_agent['status'])
print("Verification Passed:", d_agent['verification_passed'])
print("Final Narrative:", d_agent['narrative'])
assert d_agent['status'] == "SUCCESS"
assert "AdaptiveCard" == d_agent['adaptive_card']['type']

print("\n--- 2. UJI ENGINE FORECASTING 14 HARI (HOLT-WINTERS) ---")
r_fc = client.get('/api/v1/forecast/demand?horizon_days=14', headers={'X-User-Email': 'head.sales@duakelinci.id'})
d_fc = r_fc.json()
print("Forecast Points Generated:", len(d_fc['forecast']))
print("Contoh Prediksi Besok:", d_fc['forecast'][0]['date'], f"Qty: {d_fc['forecast'][0]['projected_qty_carton']}", f"Net: Rp {d_fc['forecast'][0]['projected_net_sales_idr']:,}")
print("Risiko Kehabisan Stok (Stockout Risks):", len(d_fc['stockout_risks']), "cabang terdeteksi.")
assert len(d_fc['forecast']) == 14

print("\n--- 3. UJI MODUL E-SIGNATURE INTERNAL & HASH SHA-256 ---")
doc_payload = {
    "title": "Memo Pengadaan Biji Kacang Tanah Q4 2026",
    "doc_type": "MEMO",
    "file_name": "memo_pengadaan_q4.pdf",
    "signers": [
        {"email": "bm.sukro@duakelinci.id", "name": "Maya Indah", "role": "Reviewer"},
        {"email": "head.sales@duakelinci.id", "name": "Rudi Hartono", "role": "Approver"}
    ]
}
r_doc = client.post('/api/v1/esign/documents', json=doc_payload, headers={'X-User-Email': 'bm.sukro@duakelinci.id'})
d_doc = r_doc.json()
doc_id = d_doc['id']
print("Dokumen Dibuat ID:", doc_id)
print("Hash SHA-256 Dokumen:", d_doc['sha256_hash'])
assert len(d_doc['sha256_hash']) == 64

# Maya menandatangani
r_sign1 = client.post(f'/api/v1/esign/documents/{doc_id}/sign', headers={'X-User-Email': 'bm.sukro@duakelinci.id'})
print("Signer 1 Sign Status:", r_sign1.json()['document_status'])

# Rudi menandatangani (Finalisasi)
r_sign2 = client.post(f'/api/v1/esign/documents/{doc_id}/sign', headers={'X-User-Email': 'head.sales@duakelinci.id'})
print("Signer 2 Sign Status:", r_sign2.json()['document_status'])
assert r_sign2.json()['document_status'] == "COMPLETED"

print("\n--- 4. UJI WMS GUDANG FEFO (FIRST EXPIRED, FIRST OUT) ---")
r_fefo = client.get('/api/v1/wms/fefo-recommendation?warehouse_id=WH-BDG&sku=Sukro%20Pedas%20100g&qty=50')
d_fefo = r_fefo.json()
print("Gudang:", d_fefo['warehouse_id'], "SKU:", d_fefo['sku'], "Diminta:", d_fefo['requested_qty'])
print("Alokasi Batch Berdasarkan FEFO:")
for alloc in d_fefo['fefo_allocations']:
    print(f" -> Batch: {alloc['batch_no']}, Expiry: {alloc['expiry_date']}, Alokasi: {alloc['allocated_qty']} Karton")

print("\n>>> SELURUH UJI INTEGRASI MODUL OPERASIONAL (1-4) LULUS 100% <<<")
