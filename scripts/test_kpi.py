import sys
sys.path.append('backend')
from app.services import dwh_service

admin = dwh_service.get_user_scope('admin@duakelinci.id')
bm_sukro = dwh_service.get_user_scope('bm.sukro@duakelinci.id')
hr_jabar = dwh_service.get_user_scope('hr.jabar@duakelinci.id')

kpi_admin = dwh_service.get_kpi_overview(admin)
kpi_sukro = dwh_service.get_kpi_overview(bm_sukro)
kpi_jabar = dwh_service.get_kpi_overview(hr_jabar)

print("Admin Net Sales (IDR):", f"{kpi_admin['net_sales_idr']:,.0f}", "Ach:", kpi_admin['achievement_pct'], "%")
print("BM Sukro Net Sales (IDR):", f"{kpi_sukro['net_sales_idr']:,.0f}", "Ach:", kpi_sukro['achievement_pct'], "%")
print("HR Jabar Net Sales (IDR):", f"{kpi_jabar['net_sales_idr']:,.0f}", "Ach:", kpi_jabar['achievement_pct'], "%")

assert kpi_admin['net_sales_idr'] > kpi_sukro['net_sales_idr']
assert kpi_admin['net_sales_idr'] > kpi_jabar['net_sales_idr']
print(">>> RLS VERIFICATION: SUCCESS! Net sales properly segmented by user scope.")
