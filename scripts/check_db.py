import sqlite3

conn = sqlite3.connect('backend/data/kacang_dwh.db')
c = conn.cursor()
print('sales count:', c.execute('SELECT COUNT(*) FROM fact_sales').fetchone()[0])
print('return count:', c.execute("SELECT COUNT(*) FROM fact_sales WHERE transaction_type='RETURN'").fetchone()[0])
print('unassigned salesman:', c.execute("SELECT COUNT(*) FROM fact_sales WHERE salesman='UNASSIGNED'").fetchone()[0])
print('stock count:', c.execute('SELECT COUNT(*) FROM fact_stock').fetchone()[0])
print('budget count:', c.execute('SELECT COUNT(*) FROM fact_budget').fetchone()[0])
print('user scope count:', c.execute('SELECT COUNT(*) FROM user_scope').fetchone()[0])
print('regions:', [r[0] for r in c.execute('SELECT DISTINCT region FROM fact_sales ORDER BY region').fetchall()])
