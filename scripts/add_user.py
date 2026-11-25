import sqlite3

conn = sqlite3.connect('backend/data/kacang_dwh.db')
c = conn.cursor()
c.execute("""
    INSERT INTO user_scope (email, full_name, role, scope_type, scope_value)
    VALUES ('muhammad.wyzer@gmail.com', 'Muhammad Wyzer', 'head_sales', 'NATIONAL', 'ALL')
    ON CONFLICT(email) DO UPDATE SET
        full_name = excluded.full_name,
        role = excluded.role,
        scope_type = excluded.scope_type,
        scope_value = excluded.scope_value;
""")
conn.commit()
row = c.execute("SELECT * FROM user_scope WHERE email='muhammad.wyzer@gmail.com'").fetchone()
print("Pendaftaran akun berhasil:", row)
