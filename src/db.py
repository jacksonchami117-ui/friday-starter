from __future__ import annotations
import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Numeric, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib

# Create base class for models
Base = declarative_base()

# Database configuration
def get_database_url():
    """Get database URL from environment or default to SQLite"""
    return os.getenv('DATABASE_URL', 'sqlite:///state/db.sqlite')

# Create engine and session
engine = create_engine(get_database_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Database models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    company = Column(String(100), nullable=True)
    status = Column(String(20), default="new", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    orders = relationship("Order", back_populates="lead")
    render_jobs = relationship("RenderJob", back_populates="lead")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), default="pending", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    lead = relationship("Lead", back_populates="orders")

class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    manifest = Column(JSON, nullable=True)
    status = Column(String(20), default="draft", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    render_jobs = relationship("RenderJob", back_populates="campaign")

class RenderJob(Base):
    __tablename__ = "render_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    task_id = Column(String(255), nullable=True)
    status = Column(String(20), default="pending", nullable=False)
    video_path = Column(String(500), nullable=True)
    thumbnail_path = Column(String(500), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    campaign = relationship("Campaign", back_populates="render_jobs")
    lead = relationship("Lead", back_populates="render_jobs")

# Database functions
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def get_user_by_email(email):
    """Get user by email"""
    db = SessionLocal()
    try:
        return db.query(User).filter(User.email == email).first()
    finally:
        db.close()

def create_user(email, pwd):
    """Create new user"""
    db = SessionLocal()
    try:
        user = User(email=email, password_hash=generate_password_hash(pwd))
        db.add(user)
        db.commit()
        return user
    finally:
        db.close()

def verify_user(email, pwd):
    """Verify user credentials"""
    user = get_user_by_email(email)
    return bool(user and check_password_hash(user.password_hash, pwd))

def ensure_default_admin():
    """Ensure default admin user exists"""
    email = os.environ.get("DEFAULT_ADMIN", "admin@example.com")
    pwd = os.environ.get("DEFAULT_ADMIN_PASSWORD") or os.environ.get("ADMIN_PASSWORD") or "admin"
    
    if not get_user_by_email(email):
        create_user(email, pwd)

def email_token(email: str) -> str:
    """Generate email token"""
    return hashlib.sha1((email or "").lower().encode("utf-8")).hexdigest()[:16]

# Legacy SQLite functions for backward compatibility
def db_path():
    """Legacy function for SQLite path"""
    os.makedirs("state", exist_ok=True)
    return "state/db.sqlite"

def get_conn():
    """Legacy function for SQLite connection"""
    import sqlite3
    c = sqlite3.connect(db_path())
    c.row_factory = sqlite3.Row
    return c

def init():
    """Legacy initialization - now uses SQLAlchemy"""
    init_db()
    ensure_default_admin()
