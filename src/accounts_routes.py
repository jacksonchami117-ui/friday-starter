from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required, UserMixin
from .db import get_user_by_email, verify_user, create_user

bp = Blueprint("accounts", __name__, url_prefix="/accounts")

class User(UserMixin): pass

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].lower()
        pwd = request.form["password"]
        if verify_user(email, pwd):
            row = get_user_by_email(email)
            u = User(); u.id = str(row["id"]); u.email = email
            login_user(u)
            return redirect("/campaigns/")
    return render_template("accounts_login.html")

@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        create_user(request.form["email"], request.form["password"])
        return redirect(url_for("accounts.login"))
    return render_template("accounts_register.html")

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("accounts.login"))
from __future__ import annotations
import os, re
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user, login_required
from src import db
from src.user import User

bp = Blueprint("accounts", __name__)

class AccountError(Exception):
    pass

@bp.route("/login", methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    
    if request.method == "POST":
        email = request.form.get("email","").strip()
        password = request.form.get("password","")
        remember = bool(request.form.get("remember"))
        
        if not email or not password:
            flash("Email and password required", "error")
        elif db.verify_user(email, password):
            user = User(email)
            login_user(user, remember=remember)
            next_url = request.args.get("next")
            if next_url:
                return redirect(next_url)
            return redirect(url_for("index"))
        else:
            flash("Invalid credentials", "error")
    
    return render_template("accounts/login.html")

@bp.route("/register", methods=["GET","POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    
    # Registration disabled by default
    if not os.environ.get("ENABLE_REGISTRATION"):
        flash("Registration is disabled", "error")
        return redirect(url_for("accounts.login"))
    
    if request.method == "POST":
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        confirm = request.form.get("confirm","")
        
        try:
            if not email or not password:
                raise AccountError("Email and password required")
            
            if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
                raise AccountError("Invalid email format")
                
            if len(password) < 8:
                raise AccountError("Password must be at least 8 characters")
                
            if password != confirm:
                raise AccountError("Passwords don't match")
            
            if db.get_user_by_email(email):
                raise AccountError("Email already registered")
            
            db.create_user(email, password)
            flash("Account created successfully", "success")
            return redirect(url_for("accounts.login"))
            
        except AccountError as e:
            flash(str(e), "error")
    
    return render_template("accounts/register.html")

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully", "info")
    return redirect(url_for("accounts.login"))
