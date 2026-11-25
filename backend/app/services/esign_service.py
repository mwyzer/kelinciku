import hashlib
import uuid
import datetime
from typing import Dict, Any, List, Optional
from app.services.dwh_service import get_db

# Default Head of Departments PT Dua Kelinci
HOD_DIRECTORY = {
    "SALES": {"email": "muhammad.wyzer@gmail.com", "name": "Muhammad Wyzer", "title": "Head of Sales"},
    "MARKETING": {"email": "maya.indah@duakelinci.id", "name": "Maya Indah", "title": "Head of Marketing"},
    "FINANCE": {"email": "rudi.hartono@duakelinci.id", "name": "Rudi Hartono", "title": "Head of Finance"},
    "WAREHOUSE": {"email": "dedi.kurniawan@duakelinci.id", "name": "Dedi Kurniawan", "title": "Head of Warehouse"}
}

def init_enhanced_esign_tables():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS esign_documents (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        department TEXT NOT NULL,
        doc_type TEXT NOT NULL,
        file_name TEXT NOT NULL,
        amount_idr REAL DEFAULT 0,
        sha256_hash TEXT NOT NULL,
        status TEXT NOT NULL, -- IN_PROGRESS, COMPLETED, REJECTED
        current_step INTEGER DEFAULT 1,
        total_steps INTEGER NOT NULL,
        created_by TEXT NOT NULL,
        created_at TEXT NOT NULL,
        completed_at TEXT
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS esign_signers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doc_id TEXT NOT NULL,
        signer_email TEXT NOT NULL,
        signer_name TEXT NOT NULL,
        department TEXT NOT NULL,
        role_title TEXT NOT NULL,
        step_order INTEGER NOT NULL,
        status TEXT NOT NULL, -- PENDING, CURRENT, SIGNED, REJECTED
        signed_at TEXT,
        ip_address TEXT,
        rejection_reason TEXT,
        FOREIGN KEY(doc_id) REFERENCES esign_documents(id)
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS esign_audit_trail (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doc_id TEXT NOT NULL,
        action TEXT NOT NULL,
        actor_email TEXT NOT NULL,
        actor_name TEXT NOT NULL,
        department TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        details TEXT
    );
    """)
    conn.commit()
    conn.close()

init_enhanced_esign_tables()

def create_hod_document(
    title: str,
    department: str, # SALES, MARKETING, FINANCE, WAREHOUSE
    doc_type: str,
    file_name: str,
    amount_idr: float,
    created_by: str,
    created_by_name: str,
    target_departments: List[str] # Urutan persetujuan HOD (misal: ["SALES", "MARKETING", "FINANCE"])
) -> Dict[str, Any]:
    doc_id = str(uuid.uuid4())
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB")
    content_raw = f"{title}:{department}:{doc_type}:{amount_idr}:{now_str}".encode('utf-8')
    sha256_hash = hashlib.sha256(content_raw).hexdigest()

    conn = get_db()
    cur = conn.cursor()

    total_steps = len(target_departments)
    cur.execute("""
        INSERT INTO esign_documents (
            id, title, department, doc_type, file_name, amount_idr,
            sha256_hash, status, current_step, total_steps, created_by, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 'IN_PROGRESS', 1, ?, ?, ?);
    """, (doc_id, title, department, doc_type, file_name, amount_idr, sha256_hash, total_steps, created_by, now_str))

    for idx, dept in enumerate(target_departments, start=1):
        hod_info = HOD_DIRECTORY.get(dept, {"email": f"hod.{dept.lower()}@duakelinci.id", "name": f"Head of {dept.capitalize()}", "title": f"Head of {dept.capitalize()}"})
        init_status = "CURRENT" if idx == 1 else "PENDING"
        cur.execute("""
            INSERT INTO esign_signers (
                doc_id, signer_email, signer_name, department, role_title, step_order, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (doc_id, hod_info["email"], hod_info["name"], dept, hod_info["title"], idx, init_status))

    # Audit Trail Pembentukan Dokumen
    cur.execute("""
        INSERT INTO esign_audit_trail (doc_id, action, actor_email, actor_name, department, timestamp, details)
        VALUES (?, 'DOCUMENT_CREATED', ?, ?, ?, ?, ?);
    """, (doc_id, created_by, created_by_name, department, now_str, f"Pengajuan dokumen dibuat dengan {total_steps} tahapan persetujuan HOD."))

    conn.commit()
    conn.close()

    return {
        "id": doc_id,
        "title": title,
        "department": department,
        "sha256_hash": sha256_hash,
        "status": "IN_PROGRESS",
        "current_step": 1,
        "total_steps": total_steps
    }

def sign_hod_document(doc_id: str, actor_email: str, actor_name: str, ip_address: str = "127.0.0.1") -> Dict[str, Any]:
    conn = get_db()
    cur = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB")

    # Cari signer yang berhak menandatangani langkah saat ini
    cur.execute("""
        SELECT id, department, role_title, step_order
        FROM esign_signers
        WHERE doc_id = ? AND signer_email = ? AND status = 'CURRENT';
    """, (doc_id, actor_email))
    signer = cur.fetchone()

    if not signer:
        # Periksa apakah signer menandatangani di luar gilirannya
        cur.execute("SELECT status, step_order FROM esign_signers WHERE doc_id = ? AND signer_email = ?", (doc_id, actor_email))
        any_signer = cur.fetchone()
        conn.close()
        if any_signer:
            return {"success": False, "message": f"Belum giliran Anda menandatangani. Status langkah Anda: {any_signer['status']}"}
        return {"success": False, "message": "Anda tidak terdaftar sebagai penandatangan dokumen ini."}

    step_order = signer["step_order"]
    dept = signer["department"]

    # 1. Update status signer saat ini menjadi SIGNED
    cur.execute("""
        UPDATE esign_signers
        SET status = 'SIGNED', signed_at = ?, ip_address = ?
        WHERE id = ?;
    """, (now_str, ip_address, signer["id"]))

    # 2. Catat jejak audit
    cur.execute("""
        INSERT INTO esign_audit_trail (doc_id, action, actor_email, actor_name, department, timestamp, details)
        VALUES (?, 'HOD_APPROVED', ?, ?, ?, ?, ?);
    """, (doc_id, actor_email, actor_name, dept, now_str, f"Disetujui secara digital oleh {signer['role_title']} ({actor_email})."))

    # 3. Periksa langkah berikutnya
    cur.execute("SELECT total_steps FROM esign_documents WHERE id = ?", (doc_id,))
    total_steps = cur.fetchone()["total_steps"]

    if step_order < total_steps:
        next_step = step_order + 1
        cur.execute("UPDATE esign_documents SET current_step = ? WHERE id = ?", (next_step, doc_id))
        cur.execute("UPDATE esign_signers SET status = 'CURRENT' WHERE doc_id = ? AND step_order = ?", (doc_id, next_step))
        doc_status = "IN_PROGRESS"
    else:
        # Seluruh HOD selesai
        cur.execute("UPDATE esign_documents SET status = 'COMPLETED', completed_at = ? WHERE id = ?", (now_str, doc_id))
        cur.execute("""
            INSERT INTO esign_audit_trail (doc_id, action, actor_email, actor_name, department, timestamp, details)
            VALUES (?, 'WORKFLOW_COMPLETED', 'system', 'Sistem Otorisasi Terpadu', 'SYSTEM', ?, 'Seluruh persetujuan Head of Department telah lengkap.');
        """, (doc_id, now_str))
        doc_status = "COMPLETED"

    conn.commit()
    conn.close()

    return {
        "success": True,
        "doc_id": doc_id,
        "document_status": doc_status,
        "approved_step": step_order,
        "total_steps": total_steps,
        "message": "Tanda tangan digital HOD berhasil dibubuhkan."
    }

def reject_hod_document(doc_id: str, actor_email: str, actor_name: str, reason: str = "Pengajuan ditolak oleh Head of Department", ip_address: str = "127.0.0.1") -> Dict[str, Any]:
    conn = get_db()
    cur = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB")

    # Cari signer saat ini
    cur.execute("""
        SELECT id, department, role_title, step_order
        FROM esign_signers
        WHERE doc_id = ? AND signer_email = ? AND status = 'CURRENT';
    """, (doc_id, actor_email))
    signer = cur.fetchone()

    if not signer:
        conn.close()
        return {"success": False, "message": "Anda tidak memiliki wewenang aktif untuk menolak dokumen ini saat ini."}

    # Update signer status menjadi REJECTED
    cur.execute("""
        UPDATE esign_signers
        SET status = 'REJECTED', signed_at = ?, ip_address = ?, rejection_reason = ?
        WHERE id = ?;
    """, (now_str, ip_address, reason, signer["id"]))

    # Update dokumen menjadi REJECTED
    cur.execute("UPDATE esign_documents SET status = 'REJECTED', completed_at = ? WHERE id = ?", (now_str, doc_id))

    # Catat audit trail
    cur.execute("""
        INSERT INTO esign_audit_trail (doc_id, action, actor_email, actor_name, department, timestamp, details)
        VALUES (?, 'HOD_REJECTED', ?, ?, ?, ?, ?);
    """, (doc_id, actor_email, actor_name, signer["department"], now_str, f"Ditolak oleh {signer['role_title']} ({actor_email}). Alasan: {reason}"))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "doc_id": doc_id,
        "document_status": "REJECTED",
        "message": f"Dokumen telah berhasil ditolak oleh {signer['role_title']}."
    }

def get_document_by_id(doc_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM esign_documents WHERE id = ?", (doc_id,))
    doc = cur.fetchone()
    if not doc:
        conn.close()
        return None
    d = dict(doc)
    cur.execute("SELECT signer_email, signer_name, department, role_title, step_order, status, signed_at, rejection_reason FROM esign_signers WHERE doc_id = ? ORDER BY step_order ASC", (d["id"],))
    d["signers"] = [dict(s) for s in cur.fetchall()]
    cur.execute("SELECT action, actor_name, department, timestamp, details FROM esign_audit_trail WHERE doc_id = ? ORDER BY id ASC", (d["id"],))
    d["audit_trail"] = [dict(a) for a in cur.fetchall()]
    conn.close()
    return d

def list_all_hod_documents() -> List[Dict[str, Any]]:

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM esign_documents ORDER BY created_at DESC;")
    docs = [dict(r) for r in cur.fetchall()]

    for d in docs:
        cur.execute("SELECT signer_email, signer_name, department, role_title, step_order, status, signed_at FROM esign_signers WHERE doc_id = ? ORDER BY step_order ASC", (d["id"],))
        d["signers"] = [dict(s) for s in cur.fetchall()]
        cur.execute("SELECT action, actor_name, department, timestamp, details FROM esign_audit_trail WHERE doc_id = ? ORDER BY id ASC", (d["id"],))
        d["audit_trail"] = [dict(a) for a in cur.fetchall()]

    conn.close()
    return docs

# Backward compatibility aliases
list_documents = list_all_hod_documents

def seed_demo_hod_documents():
    """Membuat contoh dokumen persetujuan lintas departemen untuk pengujian langsung."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM esign_documents")
    count = cur.fetchone()[0]
    conn.close()

    if count == 0:
        # Dokumen 1: Sales Promotion (Sales -> Marketing -> Finance)
        create_hod_document(
            title="Pengajuan Diskon Promo Khusus Sukro Modern Market Q4",
            department="SALES",
            doc_type="PROMO_REQUEST",
            file_name="promo_sukro_q4.pdf",
            amount_idr=125000000,
            created_by="muhammad.wyzer@gmail.com",
            created_by_name="Muhammad Wyzer",
            target_departments=["SALES", "MARKETING", "FINANCE"]
        )

        # Dokumen 2: Mutasi Gudang Inter-Depo (Warehouse -> Finance)
        create_hod_document(
            title="Berita Acara Mutasi Stok Darurat Gudang Bandung ke Surabaya",
            department="WAREHOUSE",
            doc_type="INTER_DEPO_TRANSFER",
            file_name="mutasi_stok_bdg_sby.pdf",
            amount_idr=84000000,
            created_by="dedi.kurniawan@duakelinci.id",
            created_by_name="Dedi Kurniawan",
            target_departments=["WAREHOUSE", "FINANCE"]
        )

def create_document(title: str, doc_type: str, file_name: str, created_by: str, signers: List[Dict[str, Any]]) -> Dict[str, Any]:
    # Support dynamic multi-signer or HOD workflow
    doc_id = str(uuid.uuid4())
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S WIB")
    content_raw = f"{title}:{doc_type}:{created_by}:{now_str}".encode('utf-8')
    sha256_hash = hashlib.sha256(content_raw).hexdigest()

    conn = get_db()
    cur = conn.cursor()

    total_steps = len(signers) if signers else 1
    cur.execute("""
        INSERT INTO esign_documents (
            id, title, department, doc_type, file_name, amount_idr,
            sha256_hash, status, current_step, total_steps, created_by, created_at
        ) VALUES (?, ?, 'GENERAL', ?, ?, 0.0, ?, 'IN_PROGRESS', 1, ?, ?, ?);
    """, (doc_id, title, doc_type, file_name, sha256_hash, total_steps, created_by, now_str))

    for idx, s in enumerate(signers, start=1):
        init_status = "CURRENT" if idx == 1 else "PENDING"
        role_t = s.get("role", s.get("title", f"Approver {idx}"))
        dept_t = s.get("department", "GENERAL")
        cur.execute("""
            INSERT INTO esign_signers (
                doc_id, signer_email, signer_name, department, role_title, step_order, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (doc_id, s.get("email"), s.get("name", s.get("email")), dept_t, role_t, idx, init_status))

    cur.execute("""
        INSERT INTO esign_audit_trail (doc_id, action, actor_email, actor_name, department, timestamp, details)
        VALUES (?, 'DOCUMENT_CREATED', ?, ?, 'GENERAL', ?, ?);
    """, (doc_id, created_by, created_by, now_str, f"Dokumen dibuat dengan {total_steps} penandatangan."))

    conn.commit()
    conn.close()

    return {
        "id": doc_id,
        "title": title,
        "sha256_hash": sha256_hash,
        "status": "IN_PROGRESS",
        "total_steps": total_steps
    }


def sign_document(doc_id: str, signer_email: str, signer_name: str, ip_address: str = "127.0.0.1") -> Dict[str, Any]:
    return sign_hod_document(doc_id, signer_email, signer_name, ip_address)


