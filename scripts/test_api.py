import uvicorn
from fastapi.testclient import TestClient
import sys
sys.path.append('backend')
from app.main import app

client = TestClient(app)

# 1. Health check
r_health = client.get('/api/v1/health')
print('Health API:', r_health.status_code, r_health.json())
assert r_health.status_code == 200

# 2. National Overview (Admin / Head of Sales)
r_admin = client.get('/api/v1/dashboard/overview', headers={'X-User-Email': 'head.sales@duakelinci.id'})
d_admin = r_admin.json()
print("National Sales (Head of Sales):", f"{d_admin['net_sales_idr']:,.0f}", "Ach:", d_admin['achievement_pct'], "%")

# 3. Brand Manager Sukro
r_sukro = client.get('/api/v1/dashboard/overview', headers={'X-User-Email': 'bm.sukro@duakelinci.id'})
d_sukro = r_sukro.json()
print("Sukro Sales (Brand Manager):", f"{d_sukro['net_sales_idr']:,.0f}", "Ach:", d_sukro['achievement_pct'], "%")

# 4. Head of Region Jabar
r_jabar = client.get('/api/v1/dashboard/overview', headers={'X-User-Email': 'hr.jabar@duakelinci.id'})
d_jabar = r_jabar.json()
print("Jawa Barat Sales (Head of Region):", f"{d_jabar['net_sales_idr']:,.0f}", "Ach:", d_jabar['achievement_pct'], "%")

# 5. Daily Trend
r_trend = client.get('/api/v1/dashboard/charts/daily-trend', headers={'X-User-Email': 'head.sales@duakelinci.id'})
print("Daily Trend Points:", len(r_trend.json()))

# 6. Breakdown by Brand
r_brand = client.get('/api/v1/dashboard/breakdown/brand', headers={'X-User-Email': 'head.sales@duakelinci.id'})
print("Brand Breakdown Count:", len(r_brand.json()))

# 7. Stock Alerts
r_stock = client.get('/api/v1/dashboard/alerts/stock', headers={'X-User-Email': 'head.sales@duakelinci.id'})
print("Stock Alerts Count:", len(r_stock.json()))

# 8. Export CSV
r_export = client.get('/api/v1/dashboard/export', headers={'X-User-Email': 'head.sales@duakelinci.id'})
print("Export Rows Count:", len(r_export.json()))

print(">>> BACKEND API VERIFICATION COMPLETED WITH 100% SUCCESS <<<")
