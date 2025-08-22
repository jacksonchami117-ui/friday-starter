from __future__ import annotations
import os
from typing import Optional
from flask_login import UserMixin
from src import db

class User(UserMixin):
    def __init__(self, email: str):
        self.email = email.lower().strip()
        self.is_admin = self.email == (os.environ.get("DEFAULT_ADMIN","admin@example.com").lower())
    
    def get_id(self) -> str:
        return self.email
    
    @property
    def is_authenticated(self) -> bool:
        return bool(self.email and db.get_user_by_email(self.email))
    
    @property
    def is_active(self) -> bool:
        return True
    
    @property
    def is_anonymous(self) -> bool:
        return False
    
    @classmethod
    def get(cls, email: str) -> Optional['User']:
        if email and db.get_user_by_email(email):
            return cls(email)
        return None
