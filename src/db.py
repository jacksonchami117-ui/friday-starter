from __future__ import annotations
import os, sqlite3, contextlib, hashlib
from typing import Optional, Tuple
from werkzeug.security import generate_password_hash, check_password_hash

def db_path():
    os.makedirs("state", exist_ok=True)
    return "state/db.sqlite"

def get_conn():
    c = sqlite3.connect(db_path())
    c.row_factory = sqlite3.Row
    return c

def init():
    with contextlib.closing(get_conn()) as c:
        c.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,email TEXT UNIQUE,password_hash TEXT)")
        c.commit()

def get_user_by_email(email):
    with contextlib.closing(get_conn()) as c:
        return c.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()

def create_user(email, pwd):
    with contextlib.closing(get_conn()) as c:
        c.execute("INSERT INTO users(email,password_hash) VALUES(?,?)",(email, generate_password_hash(pwd)))
        c.commit()

def verify_user(email, pwd):
    row = get_user_by_email(email)
    return bool(row and check_password_hash(row["password_hash"], pwd))

def ensure_default_admin():
    email = os.environ.get("DEFAULT_ADMIN","admin@example.com")
    pwd = os.environ.get("DEFAULT_ADMIN_PASSWORD") or os.environ.get("ADMIN_PASSWORD") or "admin"
    if not get_user_by_email(email):
        create_user(email, pwd)

def email_token(email: str) -> str:
    return hashlib.sha1((email or "").lower().encode("utf-8")).hexdigest()[:16]
