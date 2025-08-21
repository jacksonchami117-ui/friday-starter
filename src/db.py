import os
import sqlite3
import csv
import json
import logging
import pandas as pd
from datetime import datetime
from contextlib import contextmanager
from typing import Dict, List, Optional, Any

# Configuration
USE_DB = os.getenv("USE_DB", "0") == "1"
DB_PATH = os.path.join(os.getenv("DATA_DIR", "state"), "friday.db")

def _data_dir():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.getenv("DATA_DIR", os.path.join(base, "state"))

def _paths():
    d = _data_dir()
    return {
        "db": DB_PATH,
        "accepted": os.path.join(d, "accepted_leads.csv"),
        "rejected": os.path.join(d, "rejected_leads.csv"),
        "backup": os.path.join(d, "db_backup.csv"),
    }

class DatabaseManager:
    """Manages database operations with CSV fallback"""
    
    def __init__(self):
        self.use_db = USE_DB
        self.db_available = False
        self.paths = _paths()
        
        if self.use_db:
            self.db_available = self._init_database()
            
        if not self.db_available and self.use_db:
            logging.warning("Database initialization failed, falling back to CSV mode")
            self.use_db = False
    
    def _init_database(self) -> bool:
        """Initialize SQLite database with required tables"""
        try:
            os.makedirs(os.path.dirname(self.paths["db"]), exist_ok=True)
            
            with sqlite3.connect(self.paths["db"]) as conn:
                conn.execute("PRAGMA foreign_keys = ON")
                
                # Create tables
                self._create_tables(conn)
                
                # Migrate existing CSV data if tables are empty
                self._migrate_csv_data(conn)
                
            self.db_available = True
            logging.info("Database initialized successfully")
            return True
            
        except Exception as e:
            logging.error(f"Database initialization failed: {e}")
            return False
    
    def _create_tables(self, conn: sqlite3.Connection):
        """Create database tables"""
        
        # Leads table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                first_name TEXT,
                last_name TEXT,
                phone TEXT,
                website TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                rejection_reason TEXT,
                source TEXT,
                extra_data TEXT -- JSON for additional fields
            )
        """)
        
        # Jobs table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'queued',
                progress INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                lead_count INTEGER DEFAULT 0,
                config TEXT, -- JSON for job configuration
                error_message TEXT
            )
        """)
        
        # Videos table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_id INTEGER,
                job_id INTEGER,
                filename TEXT NOT NULL,
                type TEXT,
                status TEXT DEFAULT 'processing',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processing_time INTEGER, -- seconds
                file_size INTEGER, -- bytes
                metadata TEXT, -- JSON
                FOREIGN KEY (lead_id) REFERENCES leads(id),
                FOREIGN KEY (job_id) REFERENCES jobs(id)
            )
        """)
        
        # Analytics table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                metric_type TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                value REAL NOT NULL,
                extra_data TEXT, -- JSON for additional context
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, metric_type, metric_name)
            )
        """)
        
        # System settings table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes
        conn.execute("CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_analytics_date ON analytics(date)")
        
        conn.commit()
    
    def _migrate_csv_data(self, conn: sqlite3.Connection):
        """Migrate existing CSV data to database if tables are empty"""
        try:
            # Check if leads table is empty
            cursor = conn.execute("SELECT COUNT(*) FROM leads")
            if cursor.fetchone()[0] > 0:
                return  # Already has data
            
            # Migrate accepted leads
            if os.path.exists(self.paths["accepted"]):
                with open(self.paths["accepted"], 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        self._insert_lead_from_csv(conn, row, 'accepted')
            
            # Migrate rejected leads
            if os.path.exists(self.paths["rejected"]):
                with open(self.paths["rejected"], 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        self._insert_lead_from_csv(conn, row, 'rejected')
            
            conn.commit()
            logging.info("CSV data migrated to database successfully")
            
        except Exception as e:
            logging.error(f"CSV migration failed: {e}")
    
    def _insert_lead_from_csv(self, conn: sqlite3.Connection, row: Dict, status: str):
        """Insert a lead from CSV data"""
        try:
            # Extract standard fields
            email = row.get('email') or row.get('Email', '')
            first_name = row.get('first_name') or row.get('Name') or row.get('Full Name', '')
            phone = row.get('phone') or row.get('Phone', '')
            website = row.get('website') or row.get('Website', '')
            
            # Store extra fields as JSON
            extra_fields = {}
            for key, value in row.items():
                if key.lower() not in ['email', 'first_name', 'name', 'full name', 'phone', 'website', 'reason']:
                    extra_fields[key] = value
            
            rejection_reason = row.get('Reason') if status == 'rejected' else None
            
            conn.execute("""
                INSERT OR IGNORE INTO leads 
                (email, first_name, phone, website, status, rejection_reason, source, extra_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                email, first_name, phone, website, status, 
                rejection_reason, 'csv_migration', json.dumps(extra_fields)
            ))
            
        except Exception as e:
            logging.error(f"Error inserting lead from CSV: {e}")

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        if not self.use_db or not self.db_available:
            yield None
            return
            
        conn = None
        try:
            conn = sqlite3.connect(self.paths["db"])
            conn.row_factory = sqlite3.Row  # Enable column access by name
            yield conn
        except Exception as e:
            logging.error(f"Database connection error: {e}")
            if conn:
                conn.rollback()
            yield None
        finally:
            if conn:
                conn.close()

    def get_leads(self, status: Optional[str] = None, limit: Optional[int] = None) -> List[Dict]:
        """Get leads from database or CSV fallback"""
        if self.use_db and self.db_available:
            return self._get_leads_db(status, limit)
        else:
            return self._get_leads_csv(status, limit)
    
    def _get_leads_db(self, status: Optional[str] = None, limit: Optional[int] = None) -> List[Dict]:
        """Get leads from database"""
        try:
            with self.get_connection() as conn:
                if not conn:
                    return self._get_leads_csv(status, limit)
                
                query = "SELECT * FROM leads"
                params = []
                
                if status:
                    query += " WHERE status = ?"
                    params.append(status)
                
                query += " ORDER BY created_at DESC"
                
                if limit:
                    query += " LIMIT ?"
                    params.append(limit)
                
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                leads = []
                for row in rows:
                    lead = dict(row)
                    # Parse extra_data JSON
                    if lead.get('extra_data'):
                        try:
                            extra = json.loads(lead['extra_data'])
                            lead.update(extra)
                        except:
                            pass
                    leads.append(lead)
                
                return leads
                
        except Exception as e:
            logging.error(f"Error getting leads from database: {e}")
            return self._get_leads_csv(status, limit)
    
    def _get_leads_csv(self, status: Optional[str] = None, limit: Optional[int] = None) -> List[Dict]:
        """Get leads from CSV files (fallback)"""
        try:
            leads = []
            
            # Load accepted leads
            if not status or status == 'accepted':
                if os.path.exists(self.paths["accepted"]):
                    with open(self.paths["accepted"], 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            row['status'] = 'accepted'
                            leads.append(row)
            
            # Load rejected leads
            if not status or status == 'rejected':
                if os.path.exists(self.paths["rejected"]):
                    with open(self.paths["rejected"], 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            row['status'] = 'rejected'
                            leads.append(row)
            
            # Apply limit
            if limit:
                leads = leads[:limit]
            
            return leads
            
        except Exception as e:
            logging.error(f"Error getting leads from CSV: {e}")
            return []

    def add_lead(self, lead_data: Dict) -> bool:
        """Add a new lead to database or CSV"""
        if self.use_db and self.db_available:
            return self._add_lead_db(lead_data)
        else:
            return self._add_lead_csv(lead_data)
    
    def _add_lead_db(self, lead_data: Dict) -> bool:
        """Add lead to database"""
        try:
            with self.get_connection() as conn:
                if not conn:
                    return self._add_lead_csv(lead_data)
                
                # Extract standard fields
                email = lead_data.get('email', '')
                first_name = lead_data.get('first_name', '')
                phone = lead_data.get('phone', '')
                website = lead_data.get('website', '')
                status = lead_data.get('status', 'accepted')
                
                # Store extra fields
                extra_fields = {k: v for k, v in lead_data.items() 
                              if k not in ['email', 'first_name', 'phone', 'website', 'status']}
                
                conn.execute("""
                    INSERT OR REPLACE INTO leads 
                    (email, first_name, phone, website, status, source, extra_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    email, first_name, phone, website, status, 
                    'api', json.dumps(extra_fields)
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            logging.error(f"Error adding lead to database: {e}")
            return self._add_lead_csv(lead_data)
    
    def _add_lead_csv(self, lead_data: Dict) -> bool:
        """Add lead to CSV (fallback)"""
        try:
            status = lead_data.get('status', 'accepted')
            file_path = self.paths["accepted"] if status == 'accepted' else self.paths["rejected"]
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Check if file exists to determine if we need headers
            write_headers = not os.path.exists(file_path)
            
            with open(file_path, 'a', newline='', encoding='utf-8') as f:
                if write_headers:
                    writer = csv.DictWriter(f, fieldnames=lead_data.keys())
                    writer.writeheader()
                else:
                    writer = csv.DictWriter(f, fieldnames=lead_data.keys(), extrasaction='ignore')
                
                writer.writerow(lead_data)
            
            return True
            
        except Exception as e:
            logging.error(f"Error adding lead to CSV: {e}")
            return False

    def get_analytics_data(self, days: int = 30) -> Dict[str, Any]:
        """Get analytics data"""
        if self.use_db and self.db_available:
            return self._get_analytics_db(days)
        else:
            return self._get_analytics_fallback(days)
    
    def _get_analytics_db(self, days: int) -> Dict[str, Any]:
        """Get analytics from database"""
        try:
            with self.get_connection() as conn:
                if not conn:
                    return self._get_analytics_fallback(days)
                
                # Get lead processing stats
                cursor = conn.execute("""
                    SELECT DATE(created_at) as date, status, COUNT(*) as count
                    FROM leads 
                    WHERE created_at >= date('now', '-{} days')
                    GROUP BY DATE(created_at), status
                    ORDER BY date
                """.format(days))
                
                lead_stats = {}
                for row in cursor.fetchall():
                    date = row['date']
                    if date not in lead_stats:
                        lead_stats[date] = {'accepted': 0, 'rejected': 0}
                    lead_stats[date][row['status']] = row['count']
                
                # Get job stats
                cursor = conn.execute("""
                    SELECT type, status, COUNT(*) as count
                    FROM jobs
                    GROUP BY type, status
                """)
                
                job_stats = {}
                for row in cursor.fetchall():
                    if row['type'] not in job_stats:
                        job_stats[row['type']] = {}
                    job_stats[row['type']][row['status']] = row['count']
                
                return {
                    'lead_stats': lead_stats,
                    'job_stats': job_stats,
                    'source': 'database'
                }
                
        except Exception as e:
            logging.error(f"Error getting analytics from database: {e}")
            return self._get_analytics_fallback(days)
    
    def _get_analytics_fallback(self, days: int) -> Dict[str, Any]:
        """Get analytics from CSV files (fallback)"""
        try:
            leads = self.get_leads()
            
            # Basic stats
            accepted_count = len([l for l in leads if l.get('status') == 'accepted'])
            rejected_count = len([l for l in leads if l.get('status') == 'rejected'])
            
            return {
                'lead_stats': {
                    'total': len(leads),
                    'accepted': accepted_count,
                    'rejected': rejected_count
                },
                'job_stats': {},  # Not available in CSV mode
                'source': 'csv'
            }
            
        except Exception as e:
            logging.error(f"Error getting analytics fallback: {e}")
            return {'lead_stats': {}, 'job_stats': {}, 'source': 'error'}

    def backup_to_csv(self) -> bool:
        """Backup database to CSV"""
        if not self.use_db or not self.db_available:
            logging.info("Database not available, skipping backup")
            return True
        
        try:
            leads = self._get_leads_db()
            if leads:
                backup_path = self.paths["backup"]
                os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                
                # Write to CSV
                if leads:
                    fieldnames = set()
                    for lead in leads:
                        fieldnames.update(lead.keys())
                    
                    with open(backup_path, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=list(fieldnames))
                        writer.writeheader()
                        writer.writerows(leads)
                
                logging.info(f"Database backed up to {backup_path}")
            
            return True
            
        except Exception as e:
            logging.error(f"Database backup failed: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get database status information"""
        status = {
            'use_db_configured': USE_DB,
            'use_db_active': self.use_db,
            'db_available': self.db_available,
            'db_path': self.paths["db"],
        }
        
        if self.use_db and self.db_available:
            try:
                with self.get_connection() as conn:
                    if conn:
                        # Get table counts
                        cursor = conn.execute("SELECT COUNT(*) FROM leads")
                        status['leads_count'] = cursor.fetchone()[0]
                        
                        cursor = conn.execute("SELECT COUNT(*) FROM jobs")
                        status['jobs_count'] = cursor.fetchone()[0]
                        
                        cursor = conn.execute("SELECT COUNT(*) FROM videos")
                        status['videos_count'] = cursor.fetchone()[0]
                        
                        # Get database size
                        if os.path.exists(self.paths["db"]):
                            status['db_size_bytes'] = os.path.getsize(self.paths["db"])
            except Exception as e:
                status['error'] = str(e)
        
        return status

# Global database manager instance
db_manager = DatabaseManager()

def get_db_manager() -> DatabaseManager:
    """Get the global database manager instance"""
    return db_manager